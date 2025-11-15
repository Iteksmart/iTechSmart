"""
Event log collection from Windows and Linux systems
"""

import asyncio
import logging
from typing import List, Dict, Any, Callable
from datetime import datetime, timedelta
import paramiko
import winrm
import re

from ..core.models import Alert, AlertSource, SeverityLevel, HostCredentials, Platform


class EventLogCollector:
    """Collect and analyze event logs from remote systems"""
    
    def __init__(self, alert_callback: Callable):
        self.alert_callback = alert_callback
        self.running = False
        self.logger = logging.getLogger(__name__)
        self.monitored_hosts = []
    
    def add_host(self, credentials: HostCredentials):
        """Add a host to monitor"""
        self.monitored_hosts.append(credentials)
        self.logger.info(f"Added host for monitoring: {credentials.host}")
    
    async def start(self):
        """Start collecting event logs"""
        self.running = True
        self.logger.info("Starting event log collection...")
        
        tasks = []
        for host in self.monitored_hosts:
            if host.platform == Platform.WINDOWS:
                tasks.append(self.collect_windows_logs(host))
            elif host.platform == Platform.LINUX:
                tasks.append(self.collect_linux_logs(host))
        
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """Stop collecting logs"""
        self.running = False
        self.logger.info("Stopping event log collection...")
    
    async def collect_windows_logs(self, credentials: HostCredentials):
        """Collect Windows Event Logs"""
        while self.running:
            try:
                # PowerShell command to get recent critical/error events
                ps_command = """
                Get-EventLog -LogName System -EntryType Error,Warning -Newest 50 | 
                Select-Object TimeGenerated, EntryType, Source, EventID, Message | 
                ConvertTo-Json
                """
                
                session = winrm.Session(
                    f'http://{credentials.host}:5985/wsman',
                    auth=(credentials.username, credentials.password)
                )
                
                result = session.run_ps(ps_command)
                
                if result.status_code == 0:
                    import json
                    events = json.loads(result.std_out.decode())
                    
                    if not isinstance(events, list):
                        events = [events]
                    
                    for event in events:
                        await self.process_windows_event(event, credentials.host)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error collecting Windows logs from {credentials.host}: {e}")
                await asyncio.sleep(300)
    
    async def collect_linux_logs(self, credentials: HostCredentials):
        """Collect Linux system logs"""
        while self.running:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Connect
                if credentials.password:
                    ssh.connect(
                        credentials.host,
                        username=credentials.username,
                        password=credentials.password,
                        port=credentials.port
                    )
                elif credentials.private_key:
                    ssh.connect(
                        credentials.host,
                        username=credentials.username,
                        key_filename=credentials.private_key,
                        port=credentials.port
                    )
                
                # Get recent error logs
                commands = [
                    "journalctl -p err -n 50 --no-pager --output=json",  # systemd
                    "tail -n 50 /var/log/syslog | grep -i error",  # syslog
                ]
                
                for command in commands:
                    try:
                        stdin, stdout, stderr = ssh.exec_command(command)
                        output = stdout.read().decode()
                        
                        if 'journalctl' in command:
                            # Parse JSON output
                            for line in output.strip().split('\n'):
                                if line:
                                    try:
                                        import json
                                        event = json.loads(line)
                                        await self.process_linux_event(event, credentials.host)
                                    except:
                                        pass
                        else:
                            # Parse text output
                            for line in output.strip().split('\n'):
                                if line and 'error' in line.lower():
                                    await self.process_linux_log_line(line, credentials.host)
                    
                    except Exception as e:
                        self.logger.debug(f"Command failed (may be normal): {e}")
                
                ssh.close()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error collecting Linux logs from {credentials.host}: {e}")
                await asyncio.sleep(300)
    
    async def process_windows_event(self, event: Dict[str, Any], host: str):
        """Process a Windows event log entry"""
        entry_type = event.get('EntryType', 'Information')
        
        if entry_type in ['Error', 'Warning']:
            severity = SeverityLevel.HIGH if entry_type == 'Error' else SeverityLevel.MEDIUM
            
            # Check for specific critical events
            event_id = event.get('EventID', 0)
            message = event.get('Message', '')
            
            # Critical event IDs
            critical_events = {
                1001: 'System crash detected',
                6008: 'Unexpected system shutdown',
                7001: 'Service failed to start',
                7031: 'Service crashed',
                4625: 'Failed login attempt',
                4740: 'Account lockout'
            }
            
            if event_id in critical_events:
                alert = Alert(
                    source=AlertSource.SYSTEM,
                    severity=SeverityLevel.CRITICAL if event_id in [1001, 6008] else SeverityLevel.HIGH,
                    message=f"{critical_events[event_id]}: {message[:200]}",
                    host=host,
                    metrics={
                        'event_id': event_id,
                        'source': event.get('Source', 'Unknown'),
                        'entry_type': entry_type,
                        'metric_type': 'event_log'
                    },
                    raw_data=event,
                    tags=['windows', 'event_log', entry_type.lower()]
                )
                await self.alert_callback(alert)
    
    async def process_linux_event(self, event: Dict[str, Any], host: str):
        """Process a Linux systemd journal entry"""
        priority = event.get('PRIORITY', 6)  # 0-7, lower is more severe
        message = event.get('MESSAGE', '')
        
        if priority <= 3:  # Error or critical
            severity = SeverityLevel.CRITICAL if priority <= 2 else SeverityLevel.HIGH
            
            alert = Alert(
                source=AlertSource.SYSTEM,
                severity=severity,
                message=f"System error: {message[:200]}",
                host=host,
                metrics={
                    'priority': priority,
                    'unit': event.get('_SYSTEMD_UNIT', 'unknown'),
                    'metric_type': 'event_log'
                },
                raw_data=event,
                tags=['linux', 'systemd', 'error']
            )
            await self.alert_callback(alert)
    
    async def process_linux_log_line(self, line: str, host: str):
        """Process a Linux log line"""
        # Parse common log patterns
        if 'error' in line.lower() or 'fail' in line.lower():
            alert = Alert(
                source=AlertSource.SYSTEM,
                severity=SeverityLevel.MEDIUM,
                message=f"System log error: {line[:200]}",
                host=host,
                metrics={
                    'log_line': line,
                    'metric_type': 'event_log'
                },
                raw_data={'line': line},
                tags=['linux', 'syslog', 'error']
            )
            await self.alert_callback(alert)
    
    async def get_recent_logs(self, credentials: HostCredentials, log_type: str = 'all') -> List[str]:
        """Get recent logs from a host for diagnosis"""
        logs = []
        
        try:
            if credentials.platform == Platform.WINDOWS:
                logs = await self.get_windows_logs(credentials, log_type)
            elif credentials.platform == Platform.LINUX:
                logs = await self.get_linux_logs(credentials, log_type)
        
        except Exception as e:
            self.logger.error(f"Error getting logs from {credentials.host}: {e}")
        
        return logs
    
    async def get_windows_logs(self, credentials: HostCredentials, log_type: str) -> List[str]:
        """Get Windows logs"""
        ps_command = f"""
        Get-EventLog -LogName System -Newest 100 | 
        Select-Object TimeGenerated, EntryType, Source, Message | 
        Format-List
        """
        
        session = winrm.Session(
            f'http://{credentials.host}:5985/wsman',
            auth=(credentials.username, credentials.password)
        )
        
        result = session.run_ps(ps_command)
        
        if result.status_code == 0:
            return result.std_out.decode().split('\n')
        
        return []
    
    async def get_linux_logs(self, credentials: HostCredentials, log_type: str) -> List[str]:
        """Get Linux logs"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if credentials.password:
            ssh.connect(
                credentials.host,
                username=credentials.username,
                password=credentials.password,
                port=credentials.port
            )
        elif credentials.private_key:
            ssh.connect(
                credentials.host,
                username=credentials.username,
                key_filename=credentials.private_key,
                port=credentials.port
            )
        
        command = "journalctl -n 100 --no-pager"
        stdin, stdout, stderr = ssh.exec_command(command)
        logs = stdout.read().decode().split('\n')
        
        ssh.close()
        
        return logs