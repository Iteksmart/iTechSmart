"""
Auto-Remediation Engine - Self-Healing Infrastructure Core
This is the heart of iTechSmart Supreme's autonomous capabilities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid

from core.models import (
    Alert,
    Diagnosis,
    RemediationAction,
    ExecutionResult,
    AlertSource,
    SeverityLevel,
    ActionStatus,
    Platform,
    HostCredentials,
    ApprovalWorkflow,
)
from monitoring.prometheus_monitor import PrometheusMonitor
from monitoring.wazuh_monitor import WazuhMonitor
from ai.diagnosis_engine import AIDiagnosisEngine
from execution.command_executor import SecureCommandExecutor


class RemediationMode(Enum):
    """Remediation execution modes"""

    MANUAL = "manual"  # All actions require approval
    SEMI_AUTO = "semi_auto"  # High-risk requires approval
    FULL_AUTO = "full_auto"  # All actions auto-execute


class AutoRemediationEngine:
    """
    Self-healing infrastructure engine

    Features:
    - Real-time alert processing from Prometheus & Wazuh
    - AI-powered root cause analysis
    - Automated command generation
    - Safe execution with approval workflows
    - Rollback capability
    - Immutable audit logging
    """

    def __init__(
        self,
        prometheus_endpoints: List[str],
        wazuh_endpoints: List[Dict[str, str]],
        ai_api_key: Optional[str] = None,
        mode: RemediationMode = RemediationMode.SEMI_AUTO,
    ):
        self.logger = logging.getLogger(__name__)
        self.mode = mode
        self.running = False

        # Alert queue
        self.alert_queue = asyncio.Queue()
        self.active_remediations = {}
        self.remediation_history = []

        # Initialize components
        self.prometheus = PrometheusMonitor(
            endpoints=prometheus_endpoints, alert_callback=self.handle_alert
        )

        self.wazuh = WazuhMonitor(
            endpoints=wazuh_endpoints, alert_callback=self.handle_alert
        )

        self.diagnosis_engine = AIDiagnosisEngine(
            api_key=ai_api_key, offline_mode=ai_api_key is None
        )

        self.executor = SecureCommandExecutor()

        # Approval workflows
        self.pending_approvals = {}
        self.approval_callbacks = {}

        # Statistics
        self.stats = {
            "total_alerts": 0,
            "auto_remediated": 0,
            "manual_approvals": 0,
            "failed_remediations": 0,
            "avg_resolution_time": 0,
        }

        self.logger.info(f"Auto-remediation engine initialized in {mode.value} mode")

    async def start(self):
        """Start the self-healing engine"""
        self.running = True
        self.logger.info("🚀 Starting self-healing infrastructure engine...")

        # Start monitoring systems
        tasks = [
            self.prometheus.start(),
            self.wazuh.start(),
            self.process_alert_queue(),
            self.monitor_pending_approvals(),
        ]

        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop the engine"""
        self.running = False
        self.logger.info("Stopping self-healing engine...")

        await self.prometheus.stop()
        await self.wazuh.stop()

    async def handle_alert(self, alert: Alert):
        """Handle incoming alert from monitoring systems"""
        self.stats["total_alerts"] += 1

        self.logger.info(
            f"📢 Alert received: {alert.source.value} - "
            f"{alert.severity.value} - {alert.message}"
        )

        # Add to processing queue
        await self.alert_queue.put(alert)

    async def process_alert_queue(self):
        """Process alerts from the queue"""
        while self.running:
            try:
                # Get alert from queue
                alert = await asyncio.wait_for(self.alert_queue.get(), timeout=1.0)

                # Process alert
                await self.process_alert(alert)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing alert queue: {e}")
                await asyncio.sleep(1)

    async def process_alert(self, alert: Alert):
        """Process a single alert through the remediation pipeline"""
        remediation_id = str(uuid.uuid4())
        start_time = datetime.now()

        try:
            self.logger.info(
                f"🔍 Processing alert {alert.id} (Remediation: {remediation_id})"
            )

            # Step 1: AI Diagnosis
            self.logger.info("🧠 Running AI diagnosis...")
            diagnosis = await self.diagnosis_engine.diagnose_issue(alert)

            if not diagnosis.root_cause:
                self.logger.warning(f"Could not diagnose alert {alert.id}")
                return

            self.logger.info(
                f"✅ Diagnosis complete: {diagnosis.root_cause}\n"
                f"   Confidence: {diagnosis.confidence}%"
            )

            # Step 2: Generate remediation actions
            self.logger.info("⚙️  Generating remediation actions...")
            actions = await self.generate_remediation_actions(alert, diagnosis)

            if not actions:
                self.logger.warning(
                    f"No remediation actions generated for alert {alert.id}"
                )
                return

            self.logger.info(f"📋 Generated {len(actions)} remediation action(s)")

            # Step 3: Execute or request approval
            for action in actions:
                await self.execute_or_approve(action, remediation_id)

            # Calculate resolution time
            resolution_time = (datetime.now() - start_time).total_seconds()

            # Update statistics
            self.update_statistics(resolution_time, actions)

            # Log to history
            self.log_remediation(
                remediation_id, alert, diagnosis, actions, resolution_time
            )

        except Exception as e:
            self.logger.error(f"Error processing alert {alert.id}: {e}")
            self.stats["failed_remediations"] += 1

    async def generate_remediation_actions(
        self, alert: Alert, diagnosis: Diagnosis
    ) -> List[RemediationAction]:
        """Generate remediation actions based on diagnosis"""

        actions = []

        # Use diagnosis recommendations
        for recommendation in diagnosis.recommendations:
            action = RemediationAction(
                id=str(uuid.uuid4()),
                alert_id=alert.id,
                diagnosis_id=diagnosis.id,
                command=recommendation["command"],
                description=recommendation["description"],
                platform=self.detect_platform(alert),
                risk_level=self.assess_risk_level(recommendation),
                requires_approval=self.requires_approval(recommendation),
                estimated_impact=recommendation.get("impact", "Unknown"),
                rollback_command=recommendation.get("rollback"),
                created_at=datetime.now(),
            )

            actions.append(action)

        return actions

    async def execute_or_approve(self, action: RemediationAction, remediation_id: str):
        """Execute action or request approval based on mode and risk"""

        # Check if approval is required
        if self.should_request_approval(action):
            self.logger.info(
                f"⏸️  Action requires approval: {action.description}\n"
                f"   Command: {action.command}\n"
                f"   Risk: {action.risk_level.value}"
            )

            # Add to pending approvals
            action.status = ActionStatus.PENDING_APPROVAL
            self.pending_approvals[action.id] = {
                "action": action,
                "remediation_id": remediation_id,
                "requested_at": datetime.now(),
            }

            self.stats["manual_approvals"] += 1

            # Trigger approval notification
            await self.notify_approval_required(action)

        else:
            # Auto-execute
            self.logger.info(
                f"🤖 Auto-executing action: {action.description}\n"
                f"   Command: {action.command}"
            )

            await self.execute_action(action, remediation_id)

    async def execute_action(self, action: RemediationAction, remediation_id: str):
        """Execute a remediation action"""

        try:
            # Get credentials for target host
            credentials = await self.get_host_credentials(action.alert_id)

            if not credentials:
                self.logger.error(f"No credentials found for action {action.id}")
                action.status = ActionStatus.FAILED
                return

            # Execute command
            self.logger.info(f"⚡ Executing: {action.command}")
            result = await self.executor.execute_remediation(action, credentials)

            if result.success:
                self.logger.info(
                    f"✅ Action executed successfully\n"
                    f"   Output: {result.stdout[:200]}"
                )
                self.stats["auto_remediated"] += 1
            else:
                self.logger.error(
                    f"❌ Action failed\n" f"   Error: {result.stderr[:200]}"
                )
                self.stats["failed_remediations"] += 1

                # Attempt rollback if available
                if action.rollback_command:
                    await self.attempt_rollback(action, credentials)

        except Exception as e:
            self.logger.error(f"Error executing action {action.id}: {e}")
            action.status = ActionStatus.FAILED
            self.stats["failed_remediations"] += 1

    async def attempt_rollback(
        self, action: RemediationAction, credentials: HostCredentials
    ):
        """Attempt to rollback a failed action"""
        self.logger.warning(f"🔄 Attempting rollback for action {action.id}")

        try:
            rollback_action = RemediationAction(
                id=str(uuid.uuid4()),
                alert_id=action.alert_id,
                diagnosis_id=action.diagnosis_id,
                command=action.rollback_command,
                description=f"Rollback: {action.description}",
                platform=action.platform,
                risk_level=action.risk_level,
                requires_approval=False,
                created_at=datetime.now(),
            )

            result = await self.executor.execute_remediation(
                rollback_action, credentials
            )

            if result.success:
                self.logger.info("✅ Rollback successful")
            else:
                self.logger.error(f"❌ Rollback failed: {result.stderr}")

        except Exception as e:
            self.logger.error(f"Rollback error: {e}")

    async def approve_action(self, action_id: str, approved_by: str) -> bool:
        """Approve a pending action"""

        if action_id not in self.pending_approvals:
            self.logger.error(f"Action {action_id} not found in pending approvals")
            return False

        approval_data = self.pending_approvals[action_id]
        action = approval_data["action"]
        remediation_id = approval_data["remediation_id"]

        self.logger.info(f"✅ Action {action_id} approved by {approved_by}")

        action.status = ActionStatus.APPROVED
        action.approved_by = approved_by
        action.approved_at = datetime.now()

        # Remove from pending
        del self.pending_approvals[action_id]

        # Execute the action
        await self.execute_action(action, remediation_id)

        return True

    async def reject_action(
        self, action_id: str, rejected_by: str, reason: str
    ) -> bool:
        """Reject a pending action"""

        if action_id not in self.pending_approvals:
            return False

        approval_data = self.pending_approvals[action_id]
        action = approval_data["action"]

        self.logger.info(f"❌ Action {action_id} rejected by {rejected_by}: {reason}")

        action.status = ActionStatus.REJECTED
        action.approved_by = rejected_by
        action.rejection_reason = reason

        # Remove from pending
        del self.pending_approvals[action_id]

        return True

    async def monitor_pending_approvals(self):
        """Monitor and timeout old pending approvals"""
        while self.running:
            try:
                current_time = datetime.now()
                timeout_threshold = timedelta(hours=1)

                expired = []
                for action_id, data in self.pending_approvals.items():
                    if current_time - data["requested_at"] > timeout_threshold:
                        expired.append(action_id)

                for action_id in expired:
                    self.logger.warning(f"⏰ Action {action_id} approval timeout")
                    await self.reject_action(
                        action_id, "system", "Approval timeout (1 hour)"
                    )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error monitoring approvals: {e}")
                await asyncio.sleep(60)

    def should_request_approval(self, action: RemediationAction) -> bool:
        """Determine if action requires approval"""

        # Manual mode - all actions require approval
        if self.mode == RemediationMode.MANUAL:
            return True

        # Full auto mode - no approvals required
        if self.mode == RemediationMode.FULL_AUTO:
            return False

        # Semi-auto mode - high/critical risk requires approval
        if self.mode == RemediationMode.SEMI_AUTO:
            return action.risk_level in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]

        return action.requires_approval

    def detect_platform(self, alert: Alert) -> Platform:
        """Detect platform from alert"""
        # Simple detection based on alert data
        # In production, this would query a CMDB or asset inventory
        return Platform.LINUX  # Default

    def assess_risk_level(self, recommendation: Dict[str, Any]) -> SeverityLevel:
        """Assess risk level of a recommendation"""
        risk = recommendation.get("risk", "medium").lower()

        risk_map = {
            "low": SeverityLevel.LOW,
            "medium": SeverityLevel.MEDIUM,
            "high": SeverityLevel.HIGH,
            "critical": SeverityLevel.CRITICAL,
        }

        return risk_map.get(risk, SeverityLevel.MEDIUM)

    def requires_approval(self, recommendation: Dict[str, Any]) -> bool:
        """Check if recommendation requires approval"""
        return recommendation.get("requires_approval", False)

    async def get_host_credentials(self, alert_id: str) -> Optional[HostCredentials]:
        """Get credentials for target host"""
        # In production, this would fetch from a secure vault
        # For now, return a placeholder
        return HostCredentials(
            host="localhost",
            username="admin",
            password="",  # Use key-based auth
            platform=Platform.LINUX,
            port=22,
        )

    async def notify_approval_required(self, action: RemediationAction):
        """Notify administrators that approval is required"""
        # In production, this would send notifications via:
        # - Email
        # - Slack
        # - PagerDuty
        # - SMS
        # - Web dashboard
        self.logger.info(f"📧 Approval notification sent for action {action.id}")

    def update_statistics(
        self, resolution_time: float, actions: List[RemediationAction]
    ):
        """Update engine statistics"""
        # Update average resolution time
        total_time = self.stats["avg_resolution_time"] * (
            self.stats["total_alerts"] - 1
        )
        self.stats["avg_resolution_time"] = (total_time + resolution_time) / self.stats[
            "total_alerts"
        ]

    def log_remediation(
        self,
        remediation_id: str,
        alert: Alert,
        diagnosis: Diagnosis,
        actions: List[RemediationAction],
        resolution_time: float,
    ):
        """Log remediation to immutable audit trail"""

        log_entry = {
            "remediation_id": remediation_id,
            "timestamp": datetime.now().isoformat(),
            "alert": {
                "id": alert.id,
                "source": alert.source.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "host": alert.host,
            },
            "diagnosis": {
                "root_cause": diagnosis.root_cause,
                "confidence": diagnosis.confidence,
                "affected_components": diagnosis.affected_components,
            },
            "actions": [
                {
                    "id": action.id,
                    "command": action.command,
                    "status": action.status.value,
                    "risk_level": action.risk_level.value,
                    "approved_by": action.approved_by,
                }
                for action in actions
            ],
            "resolution_time": resolution_time,
            "mode": self.mode.value,
        }

        self.remediation_history.append(log_entry)

        # In production, write to immutable storage (e.g., blockchain, WORM storage)
        self.logger.info(f"📝 Remediation logged: {remediation_id}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            **self.stats,
            "pending_approvals": len(self.pending_approvals),
            "active_remediations": len(self.active_remediations),
            "mode": self.mode.value,
            "uptime": "N/A",  # Calculate from start time
        }

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get list of pending approvals"""
        return [
            {
                "action_id": action_id,
                "description": data["action"].description,
                "command": data["action"].command,
                "risk_level": data["action"].risk_level.value,
                "requested_at": data["requested_at"].isoformat(),
            }
            for action_id, data in self.pending_approvals.items()
        ]

    def get_remediation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get remediation history"""
        return self.remediation_history[-limit:]

    def enable_global_kill_switch(self):
        """Enable global kill switch - stops all executions"""
        self.executor.enable_kill_switch()
        self.logger.critical("🛑 GLOBAL KILL SWITCH ENABLED")

    def disable_global_kill_switch(self):
        """Disable global kill switch"""
        self.executor.disable_kill_switch()
        self.logger.info("✅ Global kill switch disabled")
