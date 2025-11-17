"""
System Remediation Use Cases
CPU, memory, disk, SSL certificates, database issues
"""

import asyncio
import logging
from typing import Dict, Any

from core.models import Alert, Diagnosis


class SystemRemediation:
    """
    System-level auto-remediation

    Scenarios:
    - High CPU usage
    - High memory usage
    - Disk space issues
    - SSL certificate expiration
    - Database deadlocks
    - Failed backup jobs
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def diagnose_high_cpu(self, alert: Alert) -> Diagnosis:
        """Diagnose high CPU usage"""

        self.logger.info("🔍 Diagnosing high CPU usage...")

        cpu_usage = alert.metrics.get("cpu_usage", 0)

        return Diagnosis(
            id=alert.id,
            root_cause=f"High CPU usage detected: {cpu_usage}%",
            confidence=90,
            affected_components=["cpu", "system"],
            recommendations=[
                {
                    "description": "Identify top CPU processes",
                    "command": "ps aux --sort=-%cpu | head -10",
                    "risk": "low",
                    "impact": "View top CPU consumers",
                    "requires_approval": False,
                },
                {
                    "description": "Check for runaway processes",
                    "command": "top -b -n 1 | head -20",
                    "risk": "low",
                    "impact": "View system processes",
                    "requires_approval": False,
                },
                {
                    "description": "Kill stuck backup script",
                    "command": 'pkill -f "backup.sh"',
                    "risk": "low",
                    "impact": "Terminate backup script",
                    "rollback": None,
                    "requires_approval": False,
                },
            ],
        )

    async def diagnose_high_memory(self, alert: Alert) -> Diagnosis:
        """Diagnose high memory usage"""

        self.logger.info("🔍 Diagnosing high memory usage...")

        memory_usage = alert.metrics.get("memory_usage", 0)

        return Diagnosis(
            id=alert.id,
            root_cause=f"High memory usage detected: {memory_usage}%",
            confidence=85,
            affected_components=["memory", "system"],
            recommendations=[
                {
                    "description": "Identify memory-hungry processes",
                    "command": "ps aux --sort=-%mem | head -10",
                    "risk": "low",
                    "impact": "View top memory consumers",
                    "requires_approval": False,
                },
                {
                    "description": "Clear page cache",
                    "command": "sync && echo 1 > /proc/sys/vm/drop_caches",
                    "risk": "low",
                    "impact": "Clear system cache",
                    "requires_approval": False,
                },
                {
                    "description": "Restart memory-intensive service",
                    "command": "systemctl restart application",
                    "risk": "medium",
                    "impact": "Service will be restarted",
                    "rollback": "systemctl stop application",
                    "requires_approval": True,
                },
            ],
        )

    async def diagnose_disk_full(self, alert: Alert) -> Diagnosis:
        """Diagnose disk space issues"""

        self.logger.info("🔍 Diagnosing disk space issue...")

        disk_usage = alert.metrics.get("disk_usage", 0)
        mountpoint = alert.metrics.get("mountpoint", "/")

        return Diagnosis(
            id=alert.id,
            root_cause=f"Disk space critical on {mountpoint}: {disk_usage}%",
            confidence=95,
            affected_components=["disk", "storage"],
            recommendations=[
                {
                    "description": "Find large files",
                    "command": f"du -h {mountpoint} | sort -rh | head -20",
                    "risk": "low",
                    "impact": "Identify large files",
                    "requires_approval": False,
                },
                {
                    "description": "Clean old log files",
                    "command": 'find /var/log -name "*.log" -mtime +30 -delete',
                    "risk": "low",
                    "impact": "Delete logs older than 30 days",
                    "requires_approval": False,
                },
                {
                    "description": "Clean package cache",
                    "command": "apt-get clean || yum clean all",
                    "risk": "low",
                    "impact": "Clear package manager cache",
                    "requires_approval": False,
                },
                {
                    "description": "Clean temp files",
                    "command": "find /tmp -type f -mtime +7 -delete",
                    "risk": "low",
                    "impact": "Delete old temp files",
                    "requires_approval": False,
                },
            ],
        )

    async def diagnose_ssl_expiration(self, alert: Alert) -> Diagnosis:
        """Diagnose SSL certificate expiration"""

        self.logger.info("🔍 Diagnosing SSL certificate expiration...")

        domain = alert.metrics.get("domain", "example.com")

        return Diagnosis(
            id=alert.id,
            root_cause=f"SSL certificate expired or expiring soon for {domain}",
            confidence=100,
            affected_components=["ssl", "web"],
            recommendations=[
                {
                    "description": "Renew Let's Encrypt certificate",
                    "command": f"certbot renew --cert-name {domain}",
                    "risk": "low",
                    "impact": "Certificate will be renewed",
                    "requires_approval": False,
                },
                {
                    "description": "Reload web server",
                    "command": "systemctl reload nginx || systemctl reload apache2",
                    "risk": "low",
                    "impact": "Web server will reload configuration",
                    "requires_approval": False,
                },
                {
                    "description": "Verify certificate",
                    "command": f"echo | openssl s_client -connect {domain}:443 2>/dev/null | openssl x509 -noout -dates",
                    "risk": "low",
                    "impact": "Check certificate validity",
                    "requires_approval": False,
                },
            ],
        )

    async def diagnose_database_deadlock(self, alert: Alert) -> Diagnosis:
        """Diagnose database deadlock"""

        self.logger.info("🔍 Diagnosing database deadlock...")

        return Diagnosis(
            id=alert.id,
            root_cause="Database deadlock detected",
            confidence=90,
            affected_components=["database", "mysql", "postgresql"],
            recommendations=[
                {
                    "description": "Show MySQL processlist",
                    "command": 'mysql -e "SHOW FULL PROCESSLIST;"',
                    "risk": "low",
                    "impact": "View active database queries",
                    "requires_approval": False,
                },
                {
                    "description": "Kill blocking query",
                    "command": 'mysql -e "KILL <process_id>;"',
                    "risk": "medium",
                    "impact": "Terminate blocking query",
                    "requires_approval": True,
                },
                {
                    "description": "Restart database service",
                    "command": "systemctl restart mysql || systemctl restart postgresql",
                    "risk": "high",
                    "impact": "Database will be restarted",
                    "rollback": "systemctl stop mysql || systemctl stop postgresql",
                    "requires_approval": True,
                },
            ],
        )

    async def diagnose_failed_backup(self, alert: Alert) -> Diagnosis:
        """Diagnose failed backup job"""

        self.logger.info("🔍 Diagnosing failed backup...")

        return Diagnosis(
            id=alert.id,
            root_cause="Backup job failed",
            confidence=85,
            affected_components=["backup", "storage"],
            recommendations=[
                {
                    "description": "Check backup logs",
                    "command": "tail -100 /var/log/backup.log",
                    "risk": "low",
                    "impact": "View backup logs",
                    "requires_approval": False,
                },
                {
                    "description": "Check disk space",
                    "command": "df -h /backup",
                    "risk": "low",
                    "impact": "Check backup destination space",
                    "requires_approval": False,
                },
                {
                    "description": "Retry backup job",
                    "command": "/usr/local/bin/backup.sh",
                    "risk": "low",
                    "impact": "Re-run backup script",
                    "requires_approval": False,
                },
                {
                    "description": "Clean old backups",
                    "command": 'find /backup -name "*.tar.gz" -mtime +30 -delete',
                    "risk": "medium",
                    "impact": "Delete backups older than 30 days",
                    "requires_approval": True,
                },
            ],
        )

    async def kill_runaway_process(self, process_name: str) -> Dict[str, Any]:
        """Kill a runaway process"""

        self.logger.info(f"⚡ Killing runaway process: {process_name}")

        commands = [
            f'pkill -f "{process_name}"',
            f"ps aux | grep {process_name}",
            f'echo "Killed {process_name} at $(date)" >> /var/log/killed_processes.log',
        ]

        return {"process": process_name, "commands": commands, "status": "killed"}

    async def clean_disk_space(self, mountpoint: str = "/") -> Dict[str, Any]:
        """Clean disk space"""

        self.logger.info(f"🧹 Cleaning disk space on {mountpoint}")

        commands = [
            'find /var/log -name "*.log" -mtime +30 -delete',
            "apt-get clean || yum clean all",
            "find /tmp -type f -mtime +7 -delete",
            "journalctl --vacuum-time=7d",
            f"df -h {mountpoint}",
        ]

        return {"mountpoint": mountpoint, "commands": commands, "status": "cleaned"}

    async def renew_ssl_certificate(self, domain: str) -> Dict[str, Any]:
        """Renew SSL certificate"""

        self.logger.info(f"🔐 Renewing SSL certificate for {domain}")

        commands = [
            f"certbot renew --cert-name {domain}",
            "systemctl reload nginx || systemctl reload apache2",
            f'echo "Certificate renewed for {domain} at $(date)" >> /var/log/ssl_renewals.log',
        ]

        return {"domain": domain, "commands": commands, "status": "renewed"}

    async def fix_database_deadlock(
        self, database_type: str = "mysql"
    ) -> Dict[str, Any]:
        """Fix database deadlock"""

        self.logger.info(f"🔧 Fixing {database_type} deadlock")

        if database_type == "mysql":
            commands = [
                'mysql -e "SHOW FULL PROCESSLIST;"',
                'mysql -e "SELECT * FROM information_schema.INNODB_LOCKS;"',
                "systemctl restart mysql",
            ]
        else:  # postgresql
            commands = [
                "psql -c \"SELECT * FROM pg_stat_activity WHERE state = 'active';\"",
                "systemctl restart postgresql",
            ]

        return {"database": database_type, "commands": commands, "status": "fixed"}

    async def retry_backup(
        self, backup_script: str = "/usr/local/bin/backup.sh"
    ) -> Dict[str, Any]:
        """Retry failed backup"""

        self.logger.info(f"🔄 Retrying backup: {backup_script}")

        commands = [
            f"bash {backup_script}",
            "ls -lh /backup | tail -5",
            f'echo "Backup retried at $(date)" >> /var/log/backup_retries.log',
        ]

        return {
            "backup_script": backup_script,
            "commands": commands,
            "status": "retried",
        }
