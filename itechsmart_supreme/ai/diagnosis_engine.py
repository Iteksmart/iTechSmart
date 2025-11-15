"""
AI-powered diagnosis engine with offline capability
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime

from ..core.models import Alert, Diagnosis, SeverityLevel, Platform


class AIDiagnosisEngine:
    """AI engine for diagnosing infrastructure issues"""
    
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = True):
        self.offline_mode = offline_mode
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.knowledge_base = self.load_knowledge_base()
        
        if not offline_mode and api_key:
            try:
                import openai
                openai.api_key = api_key
                self.openai = openai
                self.logger.info("AI engine initialized in online mode")
            except ImportError:
                self.logger.warning("OpenAI not available, falling back to offline mode")
                self.offline_mode = True
        else:
            self.logger.info("AI engine initialized in offline mode")
    
    def load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base for offline diagnosis"""
        return {
            'cpu_issues': {
                'patterns': [
                    {'pattern': r'backup.*\.sh', 'action': 'kill_process', 'risk': 'low'},
                    {'pattern': r'python.*runaway', 'action': 'kill_process', 'risk': 'low'},
                    {'pattern': r'java.*heap', 'action': 'restart_service', 'risk': 'medium'},
                ],
                'thresholds': {
                    'high': 80,
                    'critical': 95
                }
            },
            'memory_issues': {
                'patterns': [
                    {'pattern': r'java', 'action': 'increase_heap', 'risk': 'medium'},
                    {'pattern': r'cache', 'action': 'clear_cache', 'risk': 'low'},
                    {'pattern': r'leak', 'action': 'restart_service', 'risk': 'high'},
                ],
                'thresholds': {
                    'high': 85,
                    'critical': 95
                }
            },
            'disk_issues': {
                'patterns': [
                    {'pattern': r'log', 'action': 'rotate_logs', 'risk': 'low'},
                    {'pattern': r'tmp', 'action': 'clean_tmp', 'risk': 'low'},
                    {'pattern': r'cache', 'action': 'clear_cache', 'risk': 'low'},
                ],
                'thresholds': {
                    'high': 80,
                    'critical': 90
                }
            },
            'security_issues': {
                'brute_force': {
                    'action': 'block_ip',
                    'risk': 'low',
                    'threshold': 5
                },
                'rootkit': {
                    'action': 'quarantine_host',
                    'risk': 'critical',
                    'threshold': 1
                },
                'malware': {
                    'action': 'isolate_and_scan',
                    'risk': 'high',
                    'threshold': 1
                }
            }
        }
    
    async def diagnose_issue(self, alert: Alert, context: Optional[Dict[str, Any]] = None) -> Diagnosis:
        """Diagnose an infrastructure issue"""
        self.logger.info(f"Diagnosing alert: {alert.id} - {alert.message}")
        
        # Gather context if not provided
        if context is None:
            context = await self.gather_context(alert)
        
        # Use AI or offline diagnosis
        if self.offline_mode:
            diagnosis_result = await self.offline_diagnosis(alert, context)
        else:
            diagnosis_result = await self.ai_diagnosis(alert, context)
        
        diagnosis = Diagnosis(
            alert_id=alert.id,
            root_cause=diagnosis_result['root_cause'],
            confidence=diagnosis_result['confidence'],
            recommended_actions=diagnosis_result['actions'],
            context=context,
            ai_model='offline' if self.offline_mode else 'gpt-4'
        )
        
        self.logger.info(f"Diagnosis complete: {diagnosis.root_cause} (confidence: {diagnosis.confidence}%)")
        
        return diagnosis
    
    async def gather_context(self, alert: Alert) -> Dict[str, Any]:
        """Gather additional context for diagnosis"""
        context = {
            'alert_info': {
                'severity': alert.severity.value,
                'source': alert.source.value,
                'host': alert.host,
                'tags': alert.tags
            },
            'metrics': alert.metrics,
            'timestamp': alert.timestamp.isoformat()
        }
        
        return context
    
    async def offline_diagnosis(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based offline diagnosis"""
        
        # Determine issue type from alert
        if 'cpu' in alert.message.lower() or alert.metrics.get('metric_type') == 'cpu':
            return await self.diagnose_cpu_issue(alert, context)
        
        elif 'memory' in alert.message.lower() or alert.metrics.get('metric_type') == 'memory':
            return await self.diagnose_memory_issue(alert, context)
        
        elif 'disk' in alert.message.lower() or alert.metrics.get('metric_type') == 'disk':
            return await self.diagnose_disk_issue(alert, context)
        
        elif 'brute' in alert.message.lower() or 'brute_force' in alert.tags:
            return await self.diagnose_brute_force(alert, context)
        
        elif 'service' in alert.message.lower() or 'down' in alert.message.lower():
            return await self.diagnose_service_down(alert, context)
        
        elif alert.source.value == 'wazuh':
            return await self.diagnose_security_issue(alert, context)
        
        else:
            return {
                'root_cause': 'Unknown issue - requires manual investigation',
                'confidence': 20,
                'actions': [
                    {
                        'command': 'echo "Manual investigation required"',
                        'description': 'Gather more information',
                        'platform': 'linux',
                        'risk': 'none'
                    }
                ]
            }
    
    async def diagnose_cpu_issue(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose CPU-related issues"""
        cpu_usage = alert.metrics.get('cpu_usage', 0)
        
        actions = []
        
        # Get process list to identify culprit
        actions.append({
            'command': 'ps aux --sort=-%cpu | head -20',
            'description': 'Identify top CPU-consuming processes',
            'platform': 'linux',
            'risk': 'none'
        })
        
        # Common CPU issue patterns
        if cpu_usage > 90:
            # Critical CPU usage - likely runaway process
            actions.append({
                'command': "ps aux --sort=-%cpu | head -2 | tail -1 | awk '{print $2}' | xargs kill -9",
                'description': 'Kill top CPU-consuming process',
                'platform': 'linux',
                'risk': 'medium'
            })
            
            confidence = 75
            root_cause = f"Critical CPU usage ({cpu_usage:.1f}%) - likely runaway process"
        
        else:
            # High CPU usage - investigate first
            confidence = 60
            root_cause = f"High CPU usage ({cpu_usage:.1f}%) - investigation needed"
        
        return {
            'root_cause': root_cause,
            'confidence': confidence,
            'actions': actions
        }
    
    async def diagnose_memory_issue(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose memory-related issues"""
        memory_usage = alert.metrics.get('memory_usage', 0)
        
        actions = []
        
        # Get memory-hungry processes
        actions.append({
            'command': 'ps aux --sort=-%mem | head -20',
            'description': 'Identify top memory-consuming processes',
            'platform': 'linux',
            'risk': 'none'
        })
        
        # Check for memory leaks
        actions.append({
            'command': 'free -h && cat /proc/meminfo',
            'description': 'Check detailed memory information',
            'platform': 'linux',
            'risk': 'none'
        })
        
        if memory_usage > 95:
            # Critical - clear caches
            actions.append({
                'command': 'sync && echo 3 > /proc/sys/vm/drop_caches',
                'description': 'Clear system caches to free memory',
                'platform': 'linux',
                'risk': 'low'
            })
            
            confidence = 70
            root_cause = f"Critical memory usage ({memory_usage:.1f}%) - possible memory leak"
        
        else:
            confidence = 60
            root_cause = f"High memory usage ({memory_usage:.1f}%) - monitoring required"
        
        return {
            'root_cause': root_cause,
            'confidence': confidence,
            'actions': actions
        }
    
    async def diagnose_disk_issue(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose disk-related issues"""
        disk_usage = alert.metrics.get('disk_usage', 0)
        mountpoint = alert.metrics.get('mountpoint', '/')
        
        actions = []
        
        # Find large files/directories
        actions.append({
            'command': f'du -sh {mountpoint}/* 2>/dev/null | sort -rh | head -10',
            'description': f'Find largest directories on {mountpoint}',
            'platform': 'linux',
            'risk': 'none'
        })
        
        # Check for old log files
        actions.append({
            'command': f'find {mountpoint}/var/log -type f -name "*.log" -mtime +30 -exec ls -lh {{}} \\;',
            'description': 'Find old log files',
            'platform': 'linux',
            'risk': 'none'
        })
        
        if disk_usage > 90:
            # Critical - clean up
            actions.append({
                'command': 'journalctl --vacuum-time=7d',
                'description': 'Clean old systemd journal logs',
                'platform': 'linux',
                'risk': 'low'
            })
            
            actions.append({
                'command': 'find /tmp -type f -atime +7 -delete',
                'description': 'Clean old temporary files',
                'platform': 'linux',
                'risk': 'low'
            })
            
            confidence = 80
            root_cause = f"Critical disk usage on {mountpoint} ({disk_usage:.1f}%) - cleanup required"
        
        else:
            confidence = 65
            root_cause = f"High disk usage on {mountpoint} ({disk_usage:.1f}%) - monitoring required"
        
        return {
            'root_cause': root_cause,
            'confidence': confidence,
            'actions': actions
        }
    
    async def diagnose_brute_force(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose brute force attack"""
        source_ip = alert.metrics.get('source_ip', 'unknown')
        failure_count = alert.metrics.get('failure_count', 0)
        
        actions = []
        
        if source_ip != 'unknown':
            # Block the attacking IP
            actions.append({
                'command': f'iptables -A INPUT -s {source_ip} -j DROP',
                'description': f'Block IP address {source_ip}',
                'platform': 'linux',
                'risk': 'low'
            })
            
            # Also add to fail2ban if available
            actions.append({
                'command': f'fail2ban-client set sshd banip {source_ip}',
                'description': f'Add {source_ip} to fail2ban',
                'platform': 'linux',
                'risk': 'low'
            })
            
            confidence = 95
            root_cause = f"Brute force attack from {source_ip} ({failure_count} failed attempts)"
        
        else:
            confidence = 60
            root_cause = f"Possible brute force attack detected ({failure_count} failed attempts)"
        
        return {
            'root_cause': root_cause,
            'confidence': confidence,
            'actions': actions
        }
    
    async def diagnose_service_down(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose service down issues"""
        service_name = alert.metrics.get('service', 'unknown')
        
        actions = []
        
        # Check service status
        actions.append({
            'command': f'systemctl status {service_name}',
            'description': f'Check status of {service_name}',
            'platform': 'linux',
            'risk': 'none'
        })
        
        # Check service logs
        actions.append({
            'command': f'journalctl -u {service_name} -n 50 --no-pager',
            'description': f'Check recent logs for {service_name}',
            'platform': 'linux',
            'risk': 'none'
        })
        
        # Restart service
        actions.append({
            'command': f'systemctl restart {service_name}',
            'description': f'Restart {service_name} service',
            'platform': 'linux',
            'risk': 'medium'
        })
        
        # Verify service is running
        actions.append({
            'command': f'systemctl is-active {service_name}',
            'description': f'Verify {service_name} is running',
            'platform': 'linux',
            'risk': 'none'
        })
        
        return {
            'root_cause': f"Service {service_name} is down or unresponsive",
            'confidence': 85,
            'actions': actions
        }
    
    async def diagnose_security_issue(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose security-related issues"""
        
        if 'rootkit' in alert.tags:
            return {
                'root_cause': 'Rootkit detected - system compromise suspected',
                'confidence': 90,
                'actions': [
                    {
                        'command': 'systemctl isolate rescue.target',
                        'description': 'Isolate system to rescue mode',
                        'platform': 'linux',
                        'risk': 'critical'
                    }
                ]
            }
        
        elif 'file_integrity' in alert.tags:
            file_path = alert.metrics.get('file_path', 'unknown')
            return {
                'root_cause': f'Unauthorized file modification: {file_path}',
                'confidence': 85,
                'actions': [
                    {
                        'command': f'ls -la {file_path}',
                        'description': f'Check file details for {file_path}',
                        'platform': 'linux',
                        'risk': 'none'
                    },
                    {
                        'command': f'md5sum {file_path}',
                        'description': f'Get file hash for {file_path}',
                        'platform': 'linux',
                        'risk': 'none'
                    }
                ]
            }
        
        else:
            return {
                'root_cause': 'Security event detected - investigation required',
                'confidence': 60,
                'actions': [
                    {
                        'command': 'last -n 20',
                        'description': 'Check recent login history',
                        'platform': 'linux',
                        'risk': 'none'
                    }
                ]
            }
    
    async def ai_diagnosis(self, alert: Alert, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI (GPT-4) for diagnosis"""
        
        prompt = f"""
You are an expert IT infrastructure engineer. Analyze this alert and provide a diagnosis.

Alert Information:
- Message: {alert.message}
- Host: {alert.host}
- Severity: {alert.severity.value}
- Source: {alert.source.value}
- Metrics: {json.dumps(alert.metrics, indent=2)}

Context:
{json.dumps(context, indent=2)}

Provide a JSON response with:
1. root_cause: Brief description of the root cause
2. confidence: Confidence level (0-100)
3. actions: List of recommended remediation actions with:
   - command: The exact command to execute
   - description: What the command does
   - platform: linux, windows, or network
   - risk: none, low, medium, high, or critical

Focus on safe, effective remediation that can be automated.
"""
        
        try:
            response = self.openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        
        except Exception as e:
            self.logger.error(f"AI diagnosis failed: {e}")
            return await self.offline_diagnosis(alert, context)