"""
Main orchestrator for iTechSmart Supreme
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from .models import (
    Alert,
    Diagnosis,
    RemediationAction,
    ExecutionResult,
    ActionStatus,
    SeverityLevel,
    HostCredentials,
    Platform,
)
from ..monitoring.prometheus_monitor import PrometheusMonitor
from ..monitoring.wazuh_monitor import WazuhMonitor
from ..monitoring.event_log_collector import EventLogCollector
from ..ai.diagnosis_engine import AIDiagnosisEngine
from ..execution.command_executor import SecureCommandExecutor
from ..security.credential_manager import CredentialManager


class iTechSmartSupreme:
    """Main orchestrator for autonomous infrastructure healing"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.credential_manager = CredentialManager(
            master_password=config.get("master_password", "change_me_in_production"),
            storage_path=config.get("credentials_path", "credentials.enc"),
        )

        self.ai_engine = AIDiagnosisEngine(
            api_key=config.get("openai_api_key"),
            offline_mode=config.get("offline_mode", True),
        )

        self.executor = SecureCommandExecutor()

        # Monitoring engines
        self.prometheus_monitor = PrometheusMonitor(
            endpoints=config.get("prometheus_endpoints", []),
            alert_callback=self.handle_alert,
        )

        self.wazuh_monitor = WazuhMonitor(
            endpoints=config.get("wazuh_endpoints", []),
            alert_callback=self.handle_alert,
        )

        self.event_log_collector = EventLogCollector(alert_callback=self.handle_alert)

        # State management
        self.active_alerts: Dict[str, Alert] = {}
        self.pending_actions: Dict[str, RemediationAction] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.diagnoses: Dict[str, Diagnosis] = {}

        # Configuration
        self.auto_remediation_enabled = config.get("auto_remediation", False)
        self.approval_required_for_high_risk = config.get(
            "require_approval_high_risk", True
        )

        # Statistics
        self.stats = {
            "total_alerts": 0,
            "resolved_alerts": 0,
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "start_time": datetime.now(),
        }

    async def start(self):
        """Start the iTechSmart Supreme platform"""
        self.logger.info("🚀 Starting iTechSmart Supreme...")

        # Load monitored hosts
        self.load_monitored_hosts()

        # Start monitoring tasks
        tasks = [
            self.prometheus_monitor.start(),
            self.wazuh_monitor.start(),
            self.event_log_collector.start(),
        ]

        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop the platform"""
        self.logger.info("Stopping iTechSmart Supreme...")

        await self.prometheus_monitor.stop()
        await self.wazuh_monitor.stop()
        await self.event_log_collector.stop()

    def load_monitored_hosts(self):
        """Load monitored hosts from credentials"""
        hosts = self.credential_manager.list_hosts()

        for host in hosts:
            credentials = self.credential_manager.get_credentials(host)
            if credentials:
                self.event_log_collector.add_host(credentials)

        self.logger.info(f"Loaded {len(hosts)} monitored hosts")

    async def handle_alert(self, alert: Alert):
        """Handle incoming alert"""
        self.logger.info(f"🚨 Alert received: {alert.message} on {alert.host}")

        # Update statistics
        self.stats["total_alerts"] += 1

        # Store alert
        self.active_alerts[alert.id] = alert

        # Get AI diagnosis
        try:
            diagnosis = await self.ai_engine.diagnose_issue(alert)
            self.diagnoses[alert.id] = diagnosis

            self.logger.info(
                f"🧠 AI Diagnosis: {diagnosis.root_cause} "
                f"(confidence: {diagnosis.confidence}%)"
            )

            # Generate and process remediation actions
            for action_data in diagnosis.recommended_actions:
                action = self.create_remediation_action(alert, action_data)
                await self.process_remediation_action(action)

        except Exception as e:
            self.logger.error(f"Error processing alert {alert.id}: {e}")

    def create_remediation_action(
        self, alert: Alert, action_data: Dict[str, Any]
    ) -> RemediationAction:
        """Create a remediation action from diagnosis"""

        # Determine platform
        platform_map = {
            "linux": Platform.LINUX,
            "windows": Platform.WINDOWS,
            "network": Platform.NETWORK,
        }
        platform = platform_map.get(
            action_data.get("platform", "linux").lower(), Platform.LINUX
        )

        # Determine risk level
        risk_map = {
            "none": SeverityLevel.LOW,
            "low": SeverityLevel.LOW,
            "medium": SeverityLevel.MEDIUM,
            "high": SeverityLevel.HIGH,
            "critical": SeverityLevel.CRITICAL,
        }
        risk_level = risk_map.get(
            action_data.get("risk", "medium").lower(), SeverityLevel.MEDIUM
        )

        # Determine if approval is required
        requires_approval = self.should_require_approval(action_data, risk_level)

        action = RemediationAction(
            alert_id=alert.id,
            command=action_data["command"],
            platform=platform,
            risk_level=risk_level,
            description=action_data["description"],
            estimated_impact=action_data.get("impact", "Unknown"),
            requires_approval=requires_approval,
        )

        self.stats["total_actions"] += 1

        return action

    def should_require_approval(
        self, action_data: Dict[str, Any], risk_level: SeverityLevel
    ) -> bool:
        """Determine if an action requires approval"""

        # Always require approval for high/critical risk
        if risk_level in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            return True

        # Require approval if auto-remediation is disabled
        if not self.auto_remediation_enabled:
            return True

        # Check against safe command whitelist
        safe_commands = [
            "systemctl restart",
            "service restart",
            "pkill -f",
            "docker restart",
            "journalctl --vacuum",
            "find /tmp -type f -atime +7 -delete",
        ]

        command = action_data["command"]
        for safe_cmd in safe_commands:
            if command.startswith(safe_cmd):
                return False

        return True

    async def process_remediation_action(self, action: RemediationAction):
        """Process a remediation action"""

        if action.requires_approval:
            # Add to pending actions for manual approval
            self.pending_actions[action.id] = action
            self.logger.info(f"⏳ Action requires approval: {action.description}")
        else:
            # Execute automatically
            await self.execute_action(action)

    async def execute_action(self, action: RemediationAction):
        """Execute a remediation action"""

        self.logger.info(f"⚡ Executing action: {action.description}")

        # Get alert to determine host
        alert = self.active_alerts.get(action.alert_id)
        if not alert:
            self.logger.error(f"Alert not found for action: {action.id}")
            return

        # Get credentials for the target host
        credentials = self.credential_manager.get_credentials(alert.host)
        if not credentials:
            self.logger.error(f"No credentials found for host: {alert.host}")
            return

        # Execute the command
        result = await self.executor.execute_remediation(action, credentials)

        # Update statistics
        if result.success:
            self.stats["successful_actions"] += 1
            self.logger.info(f"✅ Action completed successfully: {action.description}")

            # Mark alert as resolved if action was successful
            alert.resolved = True
            alert.resolution_time = datetime.now()
            self.stats["resolved_alerts"] += 1
        else:
            self.stats["failed_actions"] += 1
            self.logger.error(f"❌ Action failed: {result.error or 'Unknown error'}")

        # Store execution result
        self.execution_history.append(
            {
                "execution_id": result.execution_id,
                "action_id": action.id,
                "alert_id": action.alert_id,
                "timestamp": datetime.now().isoformat(),
                "success": result.success,
                "command": action.command,
                "host": alert.host,
                "stdout": result.stdout[:500] if result.stdout else "",
                "stderr": result.stderr[:500] if result.stderr else "",
                "exit_code": result.exit_code,
            }
        )

        return result

    def approve_action(self, action_id: str, approved_by: str) -> bool:
        """Approve a pending action"""

        if action_id not in self.pending_actions:
            self.logger.warning(f"Action not found: {action_id}")
            return False

        action = self.pending_actions[action_id]
        action.status = ActionStatus.APPROVED
        action.approved_by = approved_by
        action.approved_at = datetime.now()

        self.logger.info(f"✓ Action approved by {approved_by}: {action.description}")

        # Execute the action
        asyncio.create_task(self.execute_action(action))

        # Remove from pending
        del self.pending_actions[action_id]

        return True

    def reject_action(self, action_id: str, rejected_by: str, reason: str) -> bool:
        """Reject a pending action"""

        if action_id not in self.pending_actions:
            self.logger.warning(f"Action not found: {action_id}")
            return False

        action = self.pending_actions[action_id]
        action.status = ActionStatus.REJECTED

        self.logger.info(
            f"✗ Action rejected by {rejected_by}: {action.description} "
            f"(Reason: {reason})"
        )

        # Remove from pending
        del self.pending_actions[action_id]

        return True

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return [
            {
                "id": alert.id,
                "timestamp": alert.timestamp.isoformat(),
                "source": alert.source.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "host": alert.host,
                "resolved": alert.resolved,
                "tags": alert.tags,
            }
            for alert in self.active_alerts.values()
            if not alert.resolved
        ]

    def get_pending_actions(self) -> List[Dict[str, Any]]:
        """Get all pending actions"""
        return [
            {
                "id": action.id,
                "alert_id": action.alert_id,
                "description": action.description,
                "command": action.command,
                "platform": action.platform.value,
                "risk_level": action.risk_level.value,
                "created_at": action.created_at.isoformat(),
                "status": action.status.value,
            }
            for action in self.pending_actions.values()
        ]

    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history[-limit:]

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        uptime = datetime.now() - self.stats["start_time"]

        return {
            "status": "running",
            "uptime_seconds": uptime.total_seconds(),
            "statistics": {
                "total_alerts": self.stats["total_alerts"],
                "resolved_alerts": self.stats["resolved_alerts"],
                "active_alerts": len(
                    [a for a in self.active_alerts.values() if not a.resolved]
                ),
                "total_actions": self.stats["total_actions"],
                "successful_actions": self.stats["successful_actions"],
                "failed_actions": self.stats["failed_actions"],
                "pending_actions": len(self.pending_actions),
            },
            "configuration": {
                "auto_remediation": self.auto_remediation_enabled,
                "offline_mode": self.ai_engine.offline_mode,
                "kill_switch": self.executor.global_kill_switch,
            },
            "monitored_hosts": len(self.credential_manager.list_hosts()),
        }

    def enable_kill_switch(self):
        """Enable global kill switch"""
        self.executor.enable_kill_switch()

    def disable_kill_switch(self):
        """Disable global kill switch"""
        self.executor.disable_kill_switch()

    def add_host(self, host_data: Dict[str, Any]) -> bool:
        """Add a host to monitor"""
        try:
            platform_map = {
                "linux": Platform.LINUX,
                "windows": Platform.WINDOWS,
                "network": Platform.NETWORK,
            }

            credentials = self.credential_manager.add_credentials(
                host=host_data["host"],
                username=host_data["username"],
                password=host_data.get("password"),
                private_key=host_data.get("private_key"),
                port=host_data.get("port", 22),
                platform=platform_map.get(
                    host_data.get("platform", "linux").lower(), Platform.LINUX
                ),
                domain=host_data.get("domain"),
                use_sudo=host_data.get("use_sudo", False),
            )

            self.event_log_collector.add_host(credentials)

            return True

        except Exception as e:
            self.logger.error(f"Failed to add host: {e}")
            return False

    def remove_host(self, host: str) -> bool:
        """Remove a host from monitoring"""
        return self.credential_manager.remove_credentials(host)

    def get_monitored_hosts(self) -> List[str]:
        """Get list of monitored hosts"""
        return self.credential_manager.list_hosts()
