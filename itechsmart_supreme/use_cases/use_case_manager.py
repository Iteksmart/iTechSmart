"""
Use Case Manager - Orchestrates all pre-built remediation scenarios
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from use_cases.web_server_remediation import WebServerRemediation
from use_cases.security_remediation import SecurityRemediation
from use_cases.system_remediation import SystemRemediation
from core.models import Alert, Diagnosis


class UseCaseManager:
    """
    Manage and execute pre-built use cases
    
    Automatically detects the appropriate use case based on alert type
    and executes the corresponding remediation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize use case handlers
        self.web_server = WebServerRemediation()
        self.security = SecurityRemediation()
        self.system = SystemRemediation()
        
        # Statistics
        self.stats = {
            'web_server_fixes': 0,
            'security_incidents': 0,
            'system_fixes': 0,
            'total_remediations': 0
        }
    
    async def diagnose_and_remediate(self, alert: Alert) -> Diagnosis:
        """
        Automatically diagnose and provide remediation for an alert
        
        Args:
            alert: Alert to diagnose
        
        Returns:
            Diagnosis with remediation recommendations
        """
        
        self.logger.info(f"🎯 Processing use case for alert: {alert.message}")
        
        # Detect use case type
        use_case_type = self._detect_use_case_type(alert)
        
        self.logger.info(f"📋 Detected use case type: {use_case_type}")
        
        # Route to appropriate handler
        if use_case_type == 'web_server':
            diagnosis = await self.web_server.diagnose_web_server_issue(alert)
            self.stats['web_server_fixes'] += 1
        
        elif use_case_type == 'security':
            diagnosis = await self.security.diagnose_security_incident(alert)
            self.stats['security_incidents'] += 1
        
        elif use_case_type == 'high_cpu':
            diagnosis = await self.system.diagnose_high_cpu(alert)
            self.stats['system_fixes'] += 1
        
        elif use_case_type == 'high_memory':
            diagnosis = await self.system.diagnose_high_memory(alert)
            self.stats['system_fixes'] += 1
        
        elif use_case_type == 'disk_full':
            diagnosis = await self.system.diagnose_disk_full(alert)
            self.stats['system_fixes'] += 1
        
        elif use_case_type == 'ssl_expiration':
            diagnosis = await self.system.diagnose_ssl_expiration(alert)
            self.stats['system_fixes'] += 1
        
        elif use_case_type == 'database_deadlock':
            diagnosis = await self.system.diagnose_database_deadlock(alert)
            self.stats['system_fixes'] += 1
        
        elif use_case_type == 'failed_backup':
            diagnosis = await self.system.diagnose_failed_backup(alert)
            self.stats['system_fixes'] += 1
        
        else:
            # Generic diagnosis
            diagnosis = await self._generic_diagnosis(alert)
        
        self.stats['total_remediations'] += 1
        
        return diagnosis
    
    def _detect_use_case_type(self, alert: Alert) -> str:
        """Detect the type of use case based on alert"""
        
        message = alert.message.lower()
        metric_type = alert.metrics.get('metric_type', '').lower()
        
        # Web server issues
        if any(keyword in message for keyword in ['apache', 'nginx', 'httpd', 'web server', '502', '503']):
            return 'web_server'
        
        # Security incidents
        if any(keyword in message for keyword in ['brute force', 'malware', 'rootkit', 'attack', 'unauthorized']):
            return 'security'
        
        # CPU issues
        if 'cpu' in message or metric_type == 'cpu':
            return 'high_cpu'
        
        # Memory issues
        if 'memory' in message or metric_type == 'memory':
            return 'high_memory'
        
        # Disk issues
        if 'disk' in message or metric_type == 'disk':
            return 'disk_full'
        
        # SSL issues
        if 'ssl' in message or 'certificate' in message:
            return 'ssl_expiration'
        
        # Database issues
        if 'deadlock' in message or 'database' in message:
            return 'database_deadlock'
        
        # Backup issues
        if 'backup' in message:
            return 'failed_backup'
        
        return 'generic'
    
    async def _generic_diagnosis(self, alert: Alert) -> Diagnosis:
        """Generic diagnosis for unknown issues"""
        
        return Diagnosis(
            id=alert.id,
            root_cause="Issue detected - manual investigation recommended",
            confidence=50,
            affected_components=['unknown'],
            recommendations=[
                {
                    'description': 'Check system logs',
                    'command': 'journalctl -n 100',
                    'risk': 'low',
                    'impact': 'View recent system logs',
                    'requires_approval': False
                },
                {
                    'description': 'Check service status',
                    'command': 'systemctl status',
                    'risk': 'low',
                    'impact': 'View service statuses',
                    'requires_approval': False
                }
            ]
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get use case statistics"""
        return {
            **self.stats,
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        # In production, track actual success/failure
        return 95.0  # Placeholder
    
    async def execute_use_case(self, use_case_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific use case by name
        
        Args:
            use_case_name: Name of the use case
            **kwargs: Use case specific parameters
        
        Returns:
            Execution result
        """
        
        self.logger.info(f"⚡ Executing use case: {use_case_name}")
        
        use_cases = {
            'restart_apache': self.web_server.auto_restart_apache,
            'restart_nginx': self.web_server.auto_restart_nginx,
            'block_ip': self.security.block_ip_address,
            'quarantine_file': self.security.quarantine_file,
            'isolate_host': self.security.isolate_host,
            'kill_process': self.system.kill_runaway_process,
            'clean_disk': self.system.clean_disk_space,
            'renew_ssl': self.system.renew_ssl_certificate,
            'fix_deadlock': self.system.fix_database_deadlock,
            'retry_backup': self.system.retry_backup
        }
        
        if use_case_name not in use_cases:
            raise ValueError(f"Unknown use case: {use_case_name}")
        
        handler = use_cases[use_case_name]
        result = await handler(**kwargs)
        
        return result
    
    def list_available_use_cases(self) -> Dict[str, str]:
        """List all available use cases"""
        
        return {
            'web_server': {
                'restart_apache': 'Auto-restart Apache web server',
                'restart_nginx': 'Auto-restart Nginx web server'
            },
            'security': {
                'block_ip': 'Block malicious IP address',
                'quarantine_file': 'Quarantine malicious file',
                'isolate_host': 'Isolate compromised host'
            },
            'system': {
                'kill_process': 'Kill runaway process',
                'clean_disk': 'Clean disk space',
                'renew_ssl': 'Renew SSL certificate',
                'fix_deadlock': 'Fix database deadlock',
                'retry_backup': 'Retry failed backup'
            }
        }