"""
Wazuh security monitoring integration
"""

import asyncio
import logging
from typing import List, Dict, Any, Callable
from datetime import datetime
import aiohttp
import json

from ..core.models import Alert, AlertSource, SeverityLevel


class WazuhMonitor:
    """Monitor Wazuh security events and generate alerts"""
    
    def __init__(self, endpoints: List[Dict[str, str]], alert_callback: Callable):
        """
        Initialize Wazuh monitor
        
        Args:
            endpoints: List of dicts with 'url', 'username', 'password'
            alert_callback: Callback function for alerts
        """
        self.endpoints = endpoints
        self.alert_callback = alert_callback
        self.running = False
        self.logger = logging.getLogger(__name__)
        self.sessions = {}
        self.tokens = {}
    
    async def authenticate(self, endpoint: Dict[str, str]) -> str:
        """Authenticate with Wazuh API"""
        url = endpoint['url']
        
        try:
            async with aiohttp.ClientSession() as session:
                auth_url = f"{url}/security/user/authenticate"
                
                async with session.post(
                    auth_url,
                    auth=aiohttp.BasicAuth(endpoint['username'], endpoint['password']),
                    ssl=False
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        token = data['data']['token']
                        self.tokens[url] = token
                        self.logger.info(f"Authenticated with Wazuh at {url}")
                        return token
                    else:
                        self.logger.error(f"Failed to authenticate with Wazuh: {response.status}")
                        return None
        
        except Exception as e:
            self.logger.error(f"Wazuh authentication error: {e}")
            return None
    
    async def start(self):
        """Start monitoring Wazuh events"""
        self.running = True
        self.logger.info("Starting Wazuh monitoring...")
        
        # Authenticate with all endpoints
        for endpoint in self.endpoints:
            await self.authenticate(endpoint)
        
        tasks = [
            self.monitor_security_events(),
            self.monitor_file_integrity(),
            self.monitor_rootkit_detection(),
            self.monitor_vulnerability_detection(),
            self.monitor_authentication_failures(),
        ]
        
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        self.logger.info("Stopping Wazuh monitoring...")
    
    async def monitor_security_events(self):
        """Monitor general security events"""
        while self.running:
            try:
                for endpoint in self.endpoints:
                    url = endpoint['url']
                    token = self.tokens.get(url)
                    
                    if not token:
                        token = await self.authenticate(endpoint)
                        if not token:
                            continue
                    
                    try:
                        async with aiohttp.ClientSession() as session:
                            headers = {'Authorization': f'Bearer {token}'}
                            
                            # Get recent alerts
                            alerts_url = f"{url}/alerts"
                            params = {
                                'limit': 100,
                                'sort': '-timestamp',
                                'rule.level': '>=10'  # High severity
                            }
                            
                            async with session.get(
                                alerts_url,
                                headers=headers,
                                params=params,
                                ssl=False
                            ) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    alerts = data.get('data', {}).get('affected_items', [])
                                    
                                    for wazuh_alert in alerts:
                                        await self.process_wazuh_alert(wazuh_alert)
                                
                                elif response.status == 401:
                                    # Token expired, re-authenticate
                                    await self.authenticate(endpoint)
                    
                    except Exception as e:
                        self.logger.error(f"Error fetching Wazuh alerts: {e}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Security event monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def monitor_file_integrity(self):
        """Monitor file integrity monitoring (FIM) events"""
        while self.running:
            try:
                for endpoint in self.endpoints:
                    url = endpoint['url']
                    token = self.tokens.get(url)
                    
                    if not token:
                        continue
                    
                    try:
                        async with aiohttp.ClientSession() as session:
                            headers = {'Authorization': f'Bearer {token}'}
                            
                            # Get FIM events
                            alerts_url = f"{url}/alerts"
                            params = {
                                'limit': 50,
                                'rule.groups': 'syscheck',
                                'sort': '-timestamp'
                            }
                            
                            async with session.get(
                                alerts_url,
                                headers=headers,
                                params=params,
                                ssl=False
                            ) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    alerts = data.get('data', {}).get('affected_items', [])
                                    
                                    for wazuh_alert in alerts:
                                        if wazuh_alert.get('rule', {}).get('level', 0) >= 7:
                                            await self.process_fim_alert(wazuh_alert)
                    
                    except Exception as e:
                        self.logger.error(f"Error fetching FIM events: {e}")
                
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"FIM monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def monitor_rootkit_detection(self):
        """Monitor rootkit detection events"""
        while self.running:
            try:
                for endpoint in self.endpoints:
                    url = endpoint['url']
                    token = self.tokens.get(url)
                    
                    if not token:
                        continue
                    
                    try:
                        async with aiohttp.ClientSession() as session:
                            headers = {'Authorization': f'Bearer {token}'}
                            
                            # Get rootkit alerts
                            alerts_url = f"{url}/alerts"
                            params = {
                                'limit': 50,
                                'rule.groups': 'rootcheck',
                                'sort': '-timestamp'
                            }
                            
                            async with session.get(
                                alerts_url,
                                headers=headers,
                                params=params,
                                ssl=False
                            ) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    alerts = data.get('data', {}).get('affected_items', [])
                                    
                                    for wazuh_alert in alerts:
                                        alert = Alert(
                                            source=AlertSource.WAZUH,
                                            severity=SeverityLevel.CRITICAL,
                                            message=f"Rootkit detected: {wazuh_alert.get('rule', {}).get('description', 'Unknown')}",
                                            host=wazuh_alert.get('agent', {}).get('name', 'unknown'),
                                            metrics={
                                                'rule_id': wazuh_alert.get('rule', {}).get('id'),
                                                'rule_level': wazuh_alert.get('rule', {}).get('level'),
                                                'metric_type': 'security'
                                            },
                                            raw_data=wazuh_alert,
                                            tags=['rootkit', 'security', 'critical']
                                        )
                                        await self.alert_callback(alert)
                    
                    except Exception as e:
                        self.logger.error(f"Error fetching rootkit alerts: {e}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Rootkit monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def monitor_vulnerability_detection(self):
        """Monitor vulnerability detection events"""
        while self.running:
            try:
                for endpoint in self.endpoints:
                    url = endpoint['url']
                    token = self.tokens.get(url)
                    
                    if not token:
                        continue
                    
                    try:
                        async with aiohttp.ClientSession() as session:
                            headers = {'Authorization': f'Bearer {token}'}
                            
                            # Get vulnerability alerts
                            alerts_url = f"{url}/vulnerability"
                            
                            async with session.get(
                                alerts_url,
                                headers=headers,
                                ssl=False
                            ) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    vulnerabilities = data.get('data', {}).get('affected_items', [])
                                    
                                    for vuln in vulnerabilities:
                                        if vuln.get('severity') in ['High', 'Critical']:
                                            alert = Alert(
                                                source=AlertSource.WAZUH,
                                                severity=SeverityLevel.HIGH if vuln.get('severity') == 'High' else SeverityLevel.CRITICAL,
                                                message=f"Vulnerability detected: {vuln.get('cve', 'Unknown')}",
                                                host=vuln.get('agent_name', 'unknown'),
                                                metrics={
                                                    'cve': vuln.get('cve'),
                                                    'cvss': vuln.get('cvss', {}).get('cvss3', {}).get('base_score'),
                                                    'package': vuln.get('name'),
                                                    'metric_type': 'vulnerability'
                                                },
                                                raw_data=vuln,
                                                tags=['vulnerability', 'security', 'cve']
                                            )
                                            await self.alert_callback(alert)
                    
                    except Exception as e:
                        self.logger.error(f"Error fetching vulnerability data: {e}")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Vulnerability monitoring error: {e}")
                await asyncio.sleep(3600)
    
    async def monitor_authentication_failures(self):
        """Monitor authentication failure events (brute force detection)"""
        while self.running:
            try:
                for endpoint in self.endpoints:
                    url = endpoint['url']
                    token = self.tokens.get(url)
                    
                    if not token:
                        continue
                    
                    try:
                        async with aiohttp.ClientSession() as session:
                            headers = {'Authorization': f'Bearer {token}'}
                            
                            # Get authentication failure alerts
                            alerts_url = f"{url}/alerts"
                            params = {
                                'limit': 100,
                                'rule.groups': 'authentication_failed',
                                'sort': '-timestamp'
                            }
                            
                            async with session.get(
                                alerts_url,
                                headers=headers,
                                params=params,
                                ssl=False
                            ) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    alerts = data.get('data', {}).get('affected_items', [])
                                    
                                    # Group by source IP to detect brute force
                                    ip_failures = {}
                                    for wazuh_alert in alerts:
                                        src_ip = wazuh_alert.get('data', {}).get('srcip', 'unknown')
                                        if src_ip not in ip_failures:
                                            ip_failures[src_ip] = []
                                        ip_failures[src_ip].append(wazuh_alert)
                                    
                                    # Alert on multiple failures from same IP
                                    for src_ip, failures in ip_failures.items():
                                        if len(failures) >= 5:  # 5+ failures = brute force
                                            alert = Alert(
                                                source=AlertSource.WAZUH,
                                                severity=SeverityLevel.HIGH,
                                                message=f"Brute force attack detected from {src_ip}: {len(failures)} failed attempts",
                                                host=failures[0].get('agent', {}).get('name', 'unknown'),
                                                metrics={
                                                    'source_ip': src_ip,
                                                    'failure_count': len(failures),
                                                    'metric_type': 'security'
                                                },
                                                raw_data={'failures': failures},
                                                tags=['brute_force', 'authentication', 'security']
                                            )
                                            await self.alert_callback(alert)
                    
                    except Exception as e:
                        self.logger.error(f"Error fetching authentication failures: {e}")
                
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Authentication monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def process_wazuh_alert(self, wazuh_alert: Dict[str, Any]):
        """Process a Wazuh alert and convert to internal format"""
        rule = wazuh_alert.get('rule', {})
        rule_level = rule.get('level', 0)
        
        # Map Wazuh levels to severity
        if rule_level >= 12:
            severity = SeverityLevel.CRITICAL
        elif rule_level >= 10:
            severity = SeverityLevel.HIGH
        elif rule_level >= 7:
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        alert = Alert(
            source=AlertSource.WAZUH,
            severity=severity,
            message=rule.get('description', 'Security event detected'),
            host=wazuh_alert.get('agent', {}).get('name', 'unknown'),
            metrics={
                'rule_id': rule.get('id'),
                'rule_level': rule_level,
                'rule_groups': rule.get('groups', []),
                'metric_type': 'security'
            },
            raw_data=wazuh_alert,
            tags=['security'] + rule.get('groups', [])
        )
        
        await self.alert_callback(alert)
    
    async def process_fim_alert(self, wazuh_alert: Dict[str, Any]):
        """Process file integrity monitoring alert"""
        syscheck = wazuh_alert.get('syscheck', {})
        
        alert = Alert(
            source=AlertSource.WAZUH,
            severity=SeverityLevel.HIGH,
            message=f"File modified: {syscheck.get('path', 'unknown')}",
            host=wazuh_alert.get('agent', {}).get('name', 'unknown'),
            metrics={
                'file_path': syscheck.get('path'),
                'event': syscheck.get('event'),
                'md5_after': syscheck.get('md5_after'),
                'metric_type': 'file_integrity'
            },
            raw_data=wazuh_alert,
            tags=['file_integrity', 'security', 'fim']
        )
        
        await self.alert_callback(alert)