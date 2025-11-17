"""
Web Server Auto-Restart Use Case
Automatically restart Apache/Nginx when service is down
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from core.models import Alert, Diagnosis, RemediationAction, Platform, SeverityLevel


class WebServerRemediation:
    """
    Auto-restart web servers (Apache/Nginx)

    Scenarios:
    - Service down
    - High error rate
    - Configuration syntax errors
    - Port conflicts
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def diagnose_web_server_issue(self, alert: Alert) -> Diagnosis:
        """Diagnose web server issues"""

        self.logger.info("🔍 Diagnosing web server issue...")

        # Check if Apache or Nginx
        service_name = self._detect_web_server(alert)

        if not service_name:
            return Diagnosis(
                id=alert.id,
                root_cause="Unknown web server",
                confidence=0,
                recommendations=[],
            )

        # Common issues
        if "connection refused" in alert.message.lower():
            return self._diagnose_service_down(alert, service_name)
        elif "502" in alert.message or "503" in alert.message:
            return self._diagnose_backend_issue(alert, service_name)
        elif "syntax" in alert.message.lower():
            return self._diagnose_config_error(alert, service_name)
        else:
            return self._diagnose_generic_issue(alert, service_name)

    def _detect_web_server(self, alert: Alert) -> Optional[str]:
        """Detect which web server is running"""

        message = alert.message.lower()

        if "apache" in message or "httpd" in message:
            return "apache2"
        elif "nginx" in message:
            return "nginx"

        return None

    def _diagnose_service_down(self, alert: Alert, service_name: str) -> Diagnosis:
        """Diagnose service down scenario"""

        return Diagnosis(
            id=alert.id,
            root_cause=f"{service_name} service is not running",
            confidence=95,
            affected_components=[service_name],
            recommendations=[
                {
                    "description": f"Restart {service_name} service",
                    "command": f"systemctl restart {service_name}",
                    "risk": "low",
                    "impact": "Service will be restarted",
                    "rollback": f"systemctl stop {service_name}",
                    "requires_approval": False,
                },
                {
                    "description": "Verify service status",
                    "command": f"systemctl status {service_name}",
                    "risk": "low",
                    "impact": "Check service status",
                    "requires_approval": False,
                },
                {
                    "description": "Check service logs",
                    "command": f"journalctl -u {service_name} -n 50",
                    "risk": "low",
                    "impact": "View recent logs",
                    "requires_approval": False,
                },
            ],
        )

    def _diagnose_backend_issue(self, alert: Alert, service_name: str) -> Diagnosis:
        """Diagnose backend/upstream issues"""

        return Diagnosis(
            id=alert.id,
            root_cause=f"{service_name} backend/upstream service unavailable",
            confidence=85,
            affected_components=[service_name, "backend"],
            recommendations=[
                {
                    "description": "Reload configuration",
                    "command": f"systemctl reload {service_name}",
                    "risk": "low",
                    "impact": "Reload configuration without downtime",
                    "rollback": None,
                    "requires_approval": False,
                },
                {
                    "description": "Test configuration",
                    "command": (
                        f"{service_name} -t"
                        if service_name == "nginx"
                        else "apachectl configtest"
                    ),
                    "risk": "low",
                    "impact": "Verify configuration syntax",
                    "requires_approval": False,
                },
            ],
        )

    def _diagnose_config_error(self, alert: Alert, service_name: str) -> Diagnosis:
        """Diagnose configuration syntax errors"""

        return Diagnosis(
            id=alert.id,
            root_cause=f"{service_name} configuration syntax error",
            confidence=90,
            affected_components=[service_name],
            recommendations=[
                {
                    "description": "Test configuration syntax",
                    "command": (
                        f"{service_name} -t"
                        if service_name == "nginx"
                        else "apachectl configtest"
                    ),
                    "risk": "low",
                    "impact": "Check configuration syntax",
                    "requires_approval": False,
                },
                {
                    "description": "Restore backup configuration",
                    "command": f"cp /etc/{service_name}/{service_name}.conf.backup /etc/{service_name}/{service_name}.conf",
                    "risk": "medium",
                    "impact": "Restore previous working configuration",
                    "rollback": None,
                    "requires_approval": True,
                },
            ],
        )

    def _diagnose_generic_issue(self, alert: Alert, service_name: str) -> Diagnosis:
        """Diagnose generic web server issues"""

        return Diagnosis(
            id=alert.id,
            root_cause=f"{service_name} experiencing issues",
            confidence=70,
            affected_components=[service_name],
            recommendations=[
                {
                    "description": f"Restart {service_name} service",
                    "command": f"systemctl restart {service_name}",
                    "risk": "low",
                    "impact": "Service will be restarted",
                    "rollback": f"systemctl stop {service_name}",
                    "requires_approval": False,
                }
            ],
        )

    async def auto_restart_apache(self, host: str) -> Dict[str, Any]:
        """Auto-restart Apache web server"""

        self.logger.info(f"🔄 Auto-restarting Apache on {host}")

        commands = [
            "systemctl restart apache2",
            "systemctl status apache2",
            "apachectl configtest",
        ]

        return {
            "service": "apache2",
            "host": host,
            "commands": commands,
            "status": "success",
        }

    async def auto_restart_nginx(self, host: str) -> Dict[str, Any]:
        """Auto-restart Nginx web server"""

        self.logger.info(f"🔄 Auto-restarting Nginx on {host}")

        commands = [
            "nginx -t",  # Test config first
            "systemctl restart nginx",
            "systemctl status nginx",
        ]

        return {
            "service": "nginx",
            "host": host,
            "commands": commands,
            "status": "success",
        }
