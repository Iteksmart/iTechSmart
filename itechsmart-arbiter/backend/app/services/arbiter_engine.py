import json
import time
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import asyncio
import uuid
import re
from dataclasses import dataclass

from app.core.config import settings
from app.core.database import get_database
from app.models.schemas import ActionResponse

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    LOW = "LOW"  # Auto-approve
    MEDIUM = "MEDIUM"  # Log and notify
    HIGH = "HIGH"  # Require Human Approval (HITL)
    CRITICAL = "CRITICAL"  # Auto-block


@dataclass
class ConstitutionRule:
    """Represents a single constitution rule"""

    forbidden_commands: List[str]
    restricted_hours: Dict[str, int]
    high_risk_keywords: List[str]
    approval_thresholds: Dict[str, int]
    environment_rules: Dict[str, List[str]]


class ArbiterEngine:
    """Core governance engine that evaluates AI actions"""

    def __init__(self):
        self.constitution = None
        self.emergency_stop_active = False
        self.db = None
        self._initialized = False

    async def initialize(self):
        """Initialize the Arbiter engine"""
        try:
            self.db = get_database()
            await self.load_constitution()
            self._initialized = True
            logger.info("🛡️ Arbiter Engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Arbiter Engine: {str(e)}")
            raise

    async def load_constitution(self):
        """Load constitution from database or use defaults"""
        try:
            # Try to load from database
            stored = await self.db.constitutions.find_one({"active": True})
            if stored:
                self.constitution = ConstitutionRule(**stored["rules"])
            else:
                # Use default constitution
                self.constitution = self._get_default_constitution()
                await self.save_constitution(self.constitution)
        except Exception as e:
            logger.warning(f"Failed to load constitution, using defaults: {str(e)}")
            self.constitution = self._get_default_constitution()

    def _get_default_constitution(self) -> ConstitutionRule:
        """Get default constitution rules"""
        return ConstitutionRule(
            forbidden_commands=[
                "rm -rf /",
                "drop table",
                "shutdown -h now",
                "format c:",
                "dd if=/dev/zero",
                ":(){ :|:& };:",
                "sudo rm -rf /",
                "chmod 777 /etc/shadow",
            ],
            restricted_hours={"start": 9, "end": 17},  # 9 AM to 5 PM
            high_risk_keywords=[
                "firewall",
                "iptables",
                "sudo",
                "chmod 777",
                "delete",
                "remove",
                "drop",
                "truncate",
                "reboot",
                "shutdown",
                "halt",
                "poweroff",
            ],
            approval_thresholds={
                "auto_approve": 20,
                "human_approval": 50,
                "blocked": 80,
            },
            environment_rules={
                "production": ["restart", "stop", "kill", "terminate"],
                "staging": ["drop", "delete", "truncate"],
                "development": [],  # Most actions allowed in dev
            },
        )

    async def save_constitution(self, constitution: ConstitutionRule):
        """Save constitution to database"""
        try:
            await self.db.constitutions.update_one(
                {"active": True},
                {
                    "$set": {
                        "rules": constitution.__dict__,
                        "updated_at": datetime.utcnow(),
                        "active": True,
                    }
                },
                upsert=True,
            )
        except Exception as e:
            logger.error(f"Failed to save constitution: {str(e)}")

    async def evaluate_request(
        self,
        agent_id: str,
        command: str,
        target_system: str,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate an action request against constitution rules

        Returns decision with risk score and required actions
        """
        if not self._initialized:
            raise RuntimeError("Arbiter engine not initialized")

        if self.emergency_stop_active:
            return {
                "status": "DENIED",
                "reason": "Emergency stop is active - all actions blocked",
                "risk_score": 100,
                "action_required": "None",
                "approval_id": None,
            }

        logger.info(f"🔍 Evaluating request from {agent_id} for {target_system}")

        # 1. IMMEDIATE BLOCK - Check forbidden commands
        for forbidden in self.constitution.forbidden_commands:
            if forbidden.lower() in command.lower():
                logger.warning(f"🚫 Forbidden command detected: {forbidden}")
                return {
                    "status": "DENIED",
                    "reason": f"Violates Constitution (Forbidden Command: {forbidden})",
                    "risk_score": 100,
                    "action_required": "None",
                    "approval_id": None,
                }

        # 2. CALCULATE RISK SCORE
        risk_score = await self._calculate_risk_score(command, target_system, context)

        # 3. DETERMINE RISK LEVEL
        risk_level = self._determine_risk_level(risk_score)

        # 4. BUSINESS LOGIC GATES
        if risk_level == RiskLevel.HIGH and self._is_business_hours():
            return {
                "status": "PAUSED",
                "reason": "High risk action during business hours",
                "risk_score": risk_score,
                "action_required": "Human Approval (HITL)",
                "approval_id": str(uuid.uuid4()),
            }

        # 5. ENVIRONMENT-SPECIFIC RULES
        env_violation = self._check_environment_rules(command, target_system)
        if env_violation:
            return {
                "status": "DENIED",
                "reason": f"Environment rule violation: {env_violation}",
                "risk_score": min(risk_score + 20, 100),
                "action_required": "None",
                "approval_id": None,
            }

        # 6. FINAL DECISION
        if risk_level == RiskLevel.CRITICAL:
            return {
                "status": "DENIED",
                "reason": "Risk score too high for autonomous execution",
                "risk_score": risk_score,
                "action_required": "Manual Intervention",
                "approval_id": None,
            }
        elif risk_level == RiskLevel.HIGH:
            return {
                "status": "PENDING_APPROVAL",
                "reason": "Risk exceeds autonomous threshold",
                "risk_score": risk_score,
                "action_required": "Slack/Teams Approval Sent",
                "approval_id": str(uuid.uuid4()),
            }
        elif risk_level == RiskLevel.MEDIUM:
            return {
                "status": "APPROVED",
                "reason": "Approved with monitoring",
                "risk_score": risk_score,
                "action_required": "Execute with Monitoring",
                "approval_id": None,
            }
        else:  # LOW
            return {
                "status": "APPROVED",
                "reason": "Within autonomous safety parameters",
                "risk_score": risk_score,
                "action_required": "Execute",
                "approval_id": None,
            }

    async def _calculate_risk_score(
        self, command: str, target_system: str, context: Dict[str, Any] = None
    ) -> int:
        """Calculate risk score (0-100) for the action"""
        score = 0
        command_lower = command.lower()
        target_lower = target_system.lower()

        # Base complexity check
        if len(command) > 100:
            score += 15

        # Keyword analysis
        for keyword in self.constitution.high_risk_keywords:
            if keyword in command_lower:
                score += 25
                logger.info(f"⚠️ Risk increased: Found high-risk keyword '{keyword}'")

        # Contextual Analysis
        if "prod" in target_lower or "production" in target_lower:
            score += 35
            logger.info("⚠️ Risk increased: Target is Production")

        if "db" in target_lower or "database" in target_lower:
            score += 20
            logger.info("⚠️ Risk increased: Target is Database")

        # Agent reputation (if available)
        if context and "agent_reputation" in context:
            reputation = context["agent_reputation"]
            if reputation < 0.5:  # Poor reputation
                score += 30
            elif reputation > 0.9:  # Excellent reputation
                score -= 10

        # Time-based risk
        if not self._is_business_hours():
            score += 15  # Higher risk outside business hours

        return min(score, 100)

    def _determine_risk_level(self, risk_score: int) -> RiskLevel:
        """Determine risk level based on score"""
        thresholds = self.constitution.approval_thresholds

        if risk_score >= thresholds["blocked"]:
            return RiskLevel.CRITICAL
        elif risk_score >= thresholds["human_approval"]:
            return RiskLevel.HIGH
        elif risk_score >= thresholds["auto_approve"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _is_business_hours(self) -> bool:
        """Check if current time is within restricted business hours"""
        current_hour = datetime.now().hour
        start = self.constitution.restricted_hours["start"]
        end = self.constitution.restricted_hours["end"]
        return start <= current_hour < end

    def _check_environment_rules(
        self, command: str, target_system: str
    ) -> Optional[str]:
        """Check environment-specific rules"""
        command_lower = command.lower()
        target_lower = target_system.lower()

        # Determine environment
        if "prod" in target_lower:
            env = "production"
        elif "stage" in target_lower:
            env = "staging"
        elif "dev" in target_lower:
            env = "development"
        else:
            return None  # Unknown environment, skip environment rules

        # Check restricted commands for this environment
        restricted_commands = self.constitution.environment_rules.get(env, [])

        for restricted in restricted_commands:
            if restricted in command_lower:
                return f"'{restricted}' not allowed in {env} environment"

        return None

    async def emergency_stop(self, reason: str, initiated_by: str) -> Dict[str, Any]:
        """Activate emergency stop - block all actions"""
        self.emergency_stop_active = True
        logger.critical(f"🚨 EMERGENCY STOP ACTIVATED by {initiated_by}: {reason}")

        # Log to database
        await self.db.audit_log.insert_one(
            {
                "type": "EMERGENCY_STOP",
                "initiated_by": initiated_by,
                "reason": reason,
                "timestamp": datetime.utcnow(),
                "active": True,
            }
        )

        return {
            "status": "EMERGENCY_STOP_ACTIVATED",
            "reason": reason,
            "initiated_by": initiated_by,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def log_decision(self, request: Dict[str, Any], result: Dict[str, Any]):
        """Log governance decision to audit trail"""
        try:
            await self.db.audit_log.insert_one(
                {
                    "type": "GOVERNANCE_DECISION",
                    "agent_id": request.get("agent_id"),
                    "command": request.get("command"),
                    "target_system": request.get("target_system"),
                    "decision": result,
                    "timestamp": datetime.utcnow(),
                    "risk_score": result.get("risk_score"),
                    "status": result.get("status"),
                }
            )
        except Exception as e:
            logger.error(f"Failed to log decision: {str(e)}")

    async def get_constitution(self) -> Dict[str, Any]:
        """Get current constitution"""
        if not self.constitution:
            await self.load_constitution()

        return {
            "constitution": self.constitution.__dict__,
            "emergency_stop_active": self.emergency_stop_active,
            "last_updated": datetime.utcnow().isoformat(),
        }

    async def update_constitution(
        self, policies: Dict[str, Any], updated_by: str
    ) -> Dict[str, Any]:
        """Update constitution policies"""
        try:
            # Validate policies
            self.constitution = ConstitutionRule(**policies)
            await self.save_constitution(self.constitution)

            # Log the change
            await self.db.audit_log.insert_one(
                {
                    "type": "CONSTITUTION_UPDATE",
                    "updated_by": updated_by,
                    "policies": policies,
                    "timestamp": datetime.utcnow(),
                }
            )

            return {
                "status": "CONSTITUTION_UPDATED",
                "updated_by": updated_by,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to update constitution: {str(e)}")
            raise

    async def get_metrics(self) -> Dict[str, Any]:
        """Get governance metrics"""
        try:
            # Get recent decisions
            since = datetime.utcnow() - timedelta(hours=24)
            recent_decisions = list(
                self.db.audit_log.find(
                    {"type": "GOVERNANCE_DECISION", "timestamp": {"$gte": since}}
                )
            )

            # Calculate metrics
            total = len(recent_decisions)
            approved = sum(
                1 for d in recent_decisions if d["decision"]["status"] == "APPROVED"
            )
            denied = sum(
                1 for d in recent_decisions if d["decision"]["status"] == "DENIED"
            )
            pending = sum(
                1
                for d in recent_decisions
                if d["decision"]["status"] == "PENDING_APPROVAL"
            )

            avg_risk = (
                sum(d.get("risk_score", 0) for d in recent_decisions) / total
                if total > 0
                else 0
            )

            return {
                "total_decisions_24h": total,
                "approved": approved,
                "denied": denied,
                "pending_approval": pending,
                "approval_rate": (approved / total * 100) if total > 0 else 0,
                "average_risk_score": round(avg_risk, 2),
                "emergency_stop_active": self.emergency_stop_active,
                "top_agents": await self._get_top_agents(recent_decisions),
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            return {"error": str(e)}

    async def _get_top_agents(self, decisions: List[Dict]) -> List[Dict]:
        """Get top agents by request count"""
        agent_counts = {}
        for decision in decisions:
            agent_id = decision.get("agent_id", "unknown")
            agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1

        # Sort and return top 5
        sorted_agents = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"agent_id": agent, "count": count} for agent, count in sorted_agents[:5]
        ]

    async def get_audit_log(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get audit log"""
        try:
            logs = list(
                self.db.audit_log.find({})
                .sort("timestamp", -1)
                .skip(offset)
                .limit(limit)
            )

            # Convert ObjectId to string
            for log in logs:
                log["_id"] = str(log["_id"])
                if "timestamp" in log:
                    log["timestamp"] = log["timestamp"].isoformat()

            return {
                "logs": logs,
                "total": await self.db.audit_log.count_documents({}),
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            logger.error(f"Failed to get audit log: {str(e)}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for the Arbiter engine"""
        return {
            "status": "healthy" if self._initialized else "uninitialized",
            "emergency_stop_active": self.emergency_stop_active,
            "constitution_loaded": self.constitution is not None,
            "database_connected": self.db is not None,
        }

    async def cleanup(self):
        """Cleanup resources"""
        self._initialized = False
        logger.info("🧹 Arbiter engine cleanup complete")
