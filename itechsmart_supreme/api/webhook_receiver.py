"""
Webhook receiver for GitHub, Prometheus, Wazuh, and custom integrations
"""

from flask import Flask, request, jsonify
import logging
from typing import Callable, Dict, Any
import asyncio
from datetime import datetime
import hmac
import hashlib

from ..core.models import Alert, AlertSource, SeverityLevel


class WebhookReceiver:
    """Receive and process webhooks from various sources"""
    
    def __init__(self, app: Flask, alert_callback: Callable):
        self.app = app
        self.alert_callback = alert_callback
        self.logger = logging.getLogger(__name__)
        self.webhook_secrets = {}
        
        # Register webhook endpoints
        self.register_routes()
    
    def register_routes(self):
        """Register webhook endpoints"""
        
        @self.app.route('/webhook/prometheus', methods=['POST'])
        def prometheus_webhook():
            return asyncio.run(self.handle_prometheus_webhook(request))
        
        @self.app.route('/webhook/wazuh', methods=['POST'])
        def wazuh_webhook():
            return asyncio.run(self.handle_wazuh_webhook(request))
        
        @self.app.route('/webhook/github', methods=['POST'])
        def github_webhook():
            return asyncio.run(self.handle_github_webhook(request))
        
        @self.app.route('/webhook/custom', methods=['POST'])
        def custom_webhook():
            return asyncio.run(self.handle_custom_webhook(request))
        
        @self.app.route('/webhook/health', methods=['GET'])
        def health_check():
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
    
    def set_webhook_secret(self, source: str, secret: str):
        """Set webhook secret for verification"""
        self.webhook_secrets[source] = secret
        self.logger.info(f"Webhook secret set for: {source}")
    
    def verify_signature(self, source: str, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        if source not in self.webhook_secrets:
            self.logger.warning(f"No secret configured for {source}")
            return True  # Allow if no secret configured
        
        secret = self.webhook_secrets[source].encode()
        expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    async def handle_prometheus_webhook(self, request) -> tuple:
        """Handle Prometheus Alertmanager webhook"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Process alerts
            alerts = data.get('alerts', [])
            
            for prom_alert in alerts:
                # Only process firing alerts
                if prom_alert.get('status') != 'firing':
                    continue
                
                labels = prom_alert.get('labels', {})
                annotations = prom_alert.get('annotations', {})
                
                # Determine severity
                severity_map = {
                    'critical': SeverityLevel.CRITICAL,
                    'warning': SeverityLevel.HIGH,
                    'info': SeverityLevel.MEDIUM
                }
                severity = severity_map.get(
                    labels.get('severity', 'warning').lower(),
                    SeverityLevel.MEDIUM
                )
                
                # Create alert
                alert = Alert(
                    source=AlertSource.PROMETHEUS,
                    severity=severity,
                    message=annotations.get('summary', labels.get('alertname', 'Unknown alert')),
                    host=labels.get('instance', 'unknown'),
                    metrics={
                        'alertname': labels.get('alertname'),
                        'job': labels.get('job'),
                        'severity': labels.get('severity'),
                        'metric_type': 'prometheus_alert'
                    },
                    raw_data=prom_alert,
                    tags=['prometheus', labels.get('alertname', '')]
                )
                
                # Trigger callback
                await self.alert_callback(alert)
            
            return jsonify({'status': 'success', 'processed': len(alerts)}), 200
        
        except Exception as e:
            self.logger.error(f"Error processing Prometheus webhook: {e}")
            return jsonify({'error': str(e)}), 500
    
    async def handle_wazuh_webhook(self, request) -> tuple:
        """Handle Wazuh webhook"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Wazuh alert structure
            rule = data.get('rule', {})
            agent = data.get('agent', {})
            
            # Determine severity
            rule_level = rule.get('level', 0)
            if rule_level >= 12:
                severity = SeverityLevel.CRITICAL
            elif rule_level >= 10:
                severity = SeverityLevel.HIGH
            elif rule_level >= 7:
                severity = SeverityLevel.MEDIUM
            else:
                severity = SeverityLevel.LOW
            
            # Create alert
            alert = Alert(
                source=AlertSource.WAZUH,
                severity=severity,
                message=rule.get('description', 'Security event detected'),
                host=agent.get('name', 'unknown'),
                metrics={
                    'rule_id': rule.get('id'),
                    'rule_level': rule_level,
                    'rule_groups': rule.get('groups', []),
                    'metric_type': 'security'
                },
                raw_data=data,
                tags=['wazuh', 'security'] + rule.get('groups', [])
            )
            
            # Trigger callback
            await self.alert_callback(alert)
            
            return jsonify({'status': 'success'}), 200
        
        except Exception as e:
            self.logger.error(f"Error processing Wazuh webhook: {e}")
            return jsonify({'error': str(e)}), 500
    
    async def handle_github_webhook(self, request) -> tuple:
        """Handle GitHub webhook"""
        try:
            # Verify signature
            signature = request.headers.get('X-Hub-Signature-256', '')
            if signature:
                signature = signature.replace('sha256=', '')
                if not self.verify_signature('github', request.data, signature):
                    return jsonify({'error': 'Invalid signature'}), 401
            
            data = request.get_json()
            event_type = request.headers.get('X-GitHub-Event')
            
            if not data or not event_type:
                return jsonify({'error': 'Invalid webhook data'}), 400
            
            # Process different GitHub events
            if event_type == 'push':
                await self.process_github_push(data)
            elif event_type == 'issues':
                await self.process_github_issue(data)
            elif event_type == 'workflow_run':
                await self.process_github_workflow(data)
            
            return jsonify({'status': 'success', 'event': event_type}), 200
        
        except Exception as e:
            self.logger.error(f"Error processing GitHub webhook: {e}")
            return jsonify({'error': str(e)}), 500
    
    async def process_github_push(self, data: Dict[str, Any]):
        """Process GitHub push event"""
        repository = data.get('repository', {}).get('full_name', 'unknown')
        pusher = data.get('pusher', {}).get('name', 'unknown')
        commits = data.get('commits', [])
        
        self.logger.info(f"GitHub push to {repository} by {pusher}: {len(commits)} commits")
        
        # Could trigger deployment or infrastructure updates
        # For now, just log
    
    async def process_github_issue(self, data: Dict[str, Any]):
        """Process GitHub issue event"""
        action = data.get('action')
        issue = data.get('issue', {})
        
        # If issue is labeled as 'infrastructure' or 'incident', create alert
        labels = [label.get('name') for label in issue.get('labels', [])]
        
        if 'infrastructure' in labels or 'incident' in labels:
            alert = Alert(
                source=AlertSource.GITHUB,
                severity=SeverityLevel.HIGH if 'incident' in labels else SeverityLevel.MEDIUM,
                message=f"GitHub issue: {issue.get('title', 'Unknown')}",
                host='github',
                metrics={
                    'issue_number': issue.get('number'),
                    'action': action,
                    'labels': labels,
                    'metric_type': 'github_issue'
                },
                raw_data=data,
                tags=['github', 'issue'] + labels
            )
            
            await self.alert_callback(alert)
    
    async def process_github_workflow(self, data: Dict[str, Any]):
        """Process GitHub workflow event"""
        workflow_run = data.get('workflow_run', {})
        conclusion = workflow_run.get('conclusion')
        
        # Alert on failed workflows
        if conclusion == 'failure':
            alert = Alert(
                source=AlertSource.GITHUB,
                severity=SeverityLevel.HIGH,
                message=f"GitHub workflow failed: {workflow_run.get('name', 'Unknown')}",
                host='github',
                metrics={
                    'workflow_name': workflow_run.get('name'),
                    'conclusion': conclusion,
                    'run_number': workflow_run.get('run_number'),
                    'metric_type': 'github_workflow'
                },
                raw_data=data,
                tags=['github', 'workflow', 'failure']
            )
            
            await self.alert_callback(alert)
    
    async def handle_custom_webhook(self, request) -> tuple:
        """Handle custom webhook format"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Expected format:
            # {
            #   "severity": "high|medium|low|critical",
            #   "message": "Alert message",
            #   "host": "hostname",
            #   "metrics": {...},
            #   "tags": [...]
            # }
            
            severity_map = {
                'critical': SeverityLevel.CRITICAL,
                'high': SeverityLevel.HIGH,
                'medium': SeverityLevel.MEDIUM,
                'low': SeverityLevel.LOW
            }
            
            alert = Alert(
                source=AlertSource.CUSTOM,
                severity=severity_map.get(
                    data.get('severity', 'medium').lower(),
                    SeverityLevel.MEDIUM
                ),
                message=data.get('message', 'Custom alert'),
                host=data.get('host', 'unknown'),
                metrics=data.get('metrics', {}),
                raw_data=data,
                tags=data.get('tags', ['custom'])
            )
            
            await self.alert_callback(alert)
            
            return jsonify({'status': 'success'}), 200
        
        except Exception as e:
            self.logger.error(f"Error processing custom webhook: {e}")
            return jsonify({'error': str(e)}), 500