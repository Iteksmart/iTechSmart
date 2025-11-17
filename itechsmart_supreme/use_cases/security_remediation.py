"""
Security Incident Remediation Use Cases
Malware detection, brute force attacks, and security threats
"""

import asyncio
import logging
from typing import Dict, Any, List

from core.models import Alert, Diagnosis, SeverityLevel


class SecurityRemediation:
    """
    Security incident auto-remediation

    Scenarios:
    - Brute force attacks
    - Malware detection
    - Unauthorized access attempts
    - Port scanning
    - DDoS attacks
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.blocked_ips = set()

    async def diagnose_security_incident(self, alert: Alert) -> Diagnosis:
        """Diagnose security incidents"""

        self.logger.info("🔍 Diagnosing security incident...")

        message = alert.message.lower()

        if "brute force" in message or "failed login" in message:
            return await self._diagnose_brute_force(alert)
        elif "malware" in message or "virus" in message:
            return await self._diagnose_malware(alert)
        elif "rootkit" in message:
            return await self._diagnose_rootkit(alert)
        elif "port scan" in message:
            return await self._diagnose_port_scan(alert)
        else:
            return await self._diagnose_generic_security(alert)

    async def _diagnose_brute_force(self, alert: Alert) -> Diagnosis:
        """Diagnose brute force attack"""

        # Extract source IP from alert
        source_ip = self._extract_ip_from_alert(alert)

        return Diagnosis(
            id=alert.id,
            root_cause=f"Brute force attack detected from {source_ip}",
            confidence=95,
            affected_components=["ssh", "authentication"],
            recommendations=[
                {
                    "description": f"Block IP address {source_ip}",
                    "command": f"iptables -A INPUT -s {source_ip} -j DROP",
                    "risk": "low",
                    "impact": f"IP {source_ip} will be blocked",
                    "rollback": f"iptables -D INPUT -s {source_ip} -j DROP",
                    "requires_approval": False,
                },
                {
                    "description": "Save iptables rules",
                    "command": "iptables-save > /etc/iptables/rules.v4",
                    "risk": "low",
                    "impact": "Persist firewall rules",
                    "requires_approval": False,
                },
                {
                    "description": "Check failed login attempts",
                    "command": f'grep "Failed password" /var/log/auth.log | grep {source_ip} | tail -20',
                    "risk": "low",
                    "impact": "View attack details",
                    "requires_approval": False,
                },
            ],
        )

    async def _diagnose_malware(self, alert: Alert) -> Diagnosis:
        """Diagnose malware detection"""

        file_path = self._extract_file_path(alert)

        return Diagnosis(
            id=alert.id,
            root_cause=f"Malware detected: {file_path}",
            confidence=90,
            affected_components=["filesystem", "security"],
            recommendations=[
                {
                    "description": "Quarantine infected file",
                    "command": f'mv {file_path} /var/quarantine/{file_path.split("/")[-1]}.quarantine',
                    "risk": "medium",
                    "impact": "File will be moved to quarantine",
                    "rollback": f'mv /var/quarantine/{file_path.split("/")[-1]}.quarantine {file_path}',
                    "requires_approval": True,
                },
                {
                    "description": "Create quarantine directory",
                    "command": "mkdir -p /var/quarantine && chmod 700 /var/quarantine",
                    "risk": "low",
                    "impact": "Create secure quarantine directory",
                    "requires_approval": False,
                },
                {
                    "description": "Scan system for similar threats",
                    "command": "clamscan -r /home /var/www",
                    "risk": "low",
                    "impact": "Full system scan",
                    "requires_approval": False,
                },
            ],
        )

    async def _diagnose_rootkit(self, alert: Alert) -> Diagnosis:
        """Diagnose rootkit detection"""

        return Diagnosis(
            id=alert.id,
            root_cause="Rootkit detected on system",
            confidence=95,
            affected_components=["kernel", "system"],
            recommendations=[
                {
                    "description": "Isolate host from network",
                    "command": "iptables -P INPUT DROP && iptables -P OUTPUT DROP && iptables -P FORWARD DROP",
                    "risk": "high",
                    "impact": "Host will be isolated from network",
                    "rollback": "iptables -P INPUT ACCEPT && iptables -P OUTPUT ACCEPT && iptables -P FORWARD ACCEPT",
                    "requires_approval": True,
                },
                {
                    "description": "Create forensic snapshot",
                    "command": "dd if=/dev/sda of=/mnt/forensics/disk.img bs=4M",
                    "risk": "low",
                    "impact": "Create disk image for analysis",
                    "requires_approval": True,
                },
                {
                    "description": "Alert security team",
                    "command": 'echo "CRITICAL: Rootkit detected on $(hostname)" | mail -s "Security Alert" security@company.com',
                    "risk": "low",
                    "impact": "Send alert to security team",
                    "requires_approval": False,
                },
            ],
        )

    async def _diagnose_port_scan(self, alert: Alert) -> Diagnosis:
        """Diagnose port scanning activity"""

        source_ip = self._extract_ip_from_alert(alert)

        return Diagnosis(
            id=alert.id,
            root_cause=f"Port scan detected from {source_ip}",
            confidence=85,
            affected_components=["network", "firewall"],
            recommendations=[
                {
                    "description": f"Block scanning IP {source_ip}",
                    "command": f"iptables -A INPUT -s {source_ip} -j DROP",
                    "risk": "low",
                    "impact": f"IP {source_ip} will be blocked",
                    "rollback": f"iptables -D INPUT -s {source_ip} -j DROP",
                    "requires_approval": False,
                },
                {
                    "description": "Log scan details",
                    "command": f'echo "Port scan from {source_ip} at $(date)" >> /var/log/security/port_scans.log',
                    "risk": "low",
                    "impact": "Log incident for analysis",
                    "requires_approval": False,
                },
            ],
        )

    async def _diagnose_generic_security(self, alert: Alert) -> Diagnosis:
        """Diagnose generic security incidents"""

        return Diagnosis(
            id=alert.id,
            root_cause="Security incident detected",
            confidence=70,
            affected_components=["security"],
            recommendations=[
                {
                    "description": "Review security logs",
                    "command": "tail -100 /var/log/auth.log",
                    "risk": "low",
                    "impact": "View recent security events",
                    "requires_approval": False,
                },
                {
                    "description": "Check active connections",
                    "command": "netstat -tunap",
                    "risk": "low",
                    "impact": "View active network connections",
                    "requires_approval": False,
                },
            ],
        )

    def _extract_ip_from_alert(self, alert: Alert) -> str:
        """Extract IP address from alert message"""

        import re

        # Try to find IP in message
        ip_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        match = re.search(ip_pattern, alert.message)

        if match:
            return match.group(0)

        # Try to get from metrics
        if alert.metrics and "source_ip" in alert.metrics:
            return alert.metrics["source_ip"]

        return "unknown"

    def _extract_file_path(self, alert: Alert) -> str:
        """Extract file path from alert message"""

        # Simple extraction - in production, use more robust parsing
        if alert.metrics and "file_path" in alert.metrics:
            return alert.metrics["file_path"]

        return "/tmp/unknown_file"

    async def block_ip_address(
        self, ip_address: str, reason: str = "Security threat"
    ) -> Dict[str, Any]:
        """Block an IP address"""

        self.logger.info(f"🛡️ Blocking IP: {ip_address} - Reason: {reason}")

        commands = [
            f"iptables -A INPUT -s {ip_address} -j DROP",
            "iptables-save > /etc/iptables/rules.v4",
            f'echo "{ip_address} blocked at $(date): {reason}" >> /var/log/blocked_ips.log',
        ]

        self.blocked_ips.add(ip_address)

        return {
            "ip_address": ip_address,
            "reason": reason,
            "commands": commands,
            "status": "blocked",
            "timestamp": asyncio.get_event_loop().time(),
        }

    async def quarantine_file(self, file_path: str) -> Dict[str, Any]:
        """Quarantine a malicious file"""

        self.logger.info(f"🔒 Quarantining file: {file_path}")

        import os

        filename = os.path.basename(file_path)

        commands = [
            "mkdir -p /var/quarantine && chmod 700 /var/quarantine",
            f"mv {file_path} /var/quarantine/{filename}.quarantine",
            f'echo "Quarantined {file_path} at $(date)" >> /var/log/quarantine.log',
        ]

        return {
            "file_path": file_path,
            "quarantine_path": f"/var/quarantine/{filename}.quarantine",
            "commands": commands,
            "status": "quarantined",
        }

    async def isolate_host(self, host: str) -> Dict[str, Any]:
        """Isolate a compromised host from network"""

        self.logger.info(f"🚨 Isolating host: {host}")

        commands = [
            "iptables -P INPUT DROP",
            "iptables -P OUTPUT DROP",
            "iptables -P FORWARD DROP",
            "iptables -A INPUT -i lo -j ACCEPT",  # Allow localhost
            "iptables -A OUTPUT -o lo -j ACCEPT",
            f'echo "Host {host} isolated at $(date)" >> /var/log/isolation.log',
        ]

        return {
            "host": host,
            "commands": commands,
            "status": "isolated",
            "note": "Host is isolated from network. Manual intervention required.",
        }

    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IPs"""
        return list(self.blocked_ips)
