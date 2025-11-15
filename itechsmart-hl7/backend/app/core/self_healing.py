"""
Self-Healing Engine for HL7 Integration
Autonomous detection, diagnosis, and remediation of HL7 issues
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """Incident severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentType(Enum):
    """Types of HL7 incidents"""
    MESSAGE_FAILURE = "message_failure"
    QUEUE_BACKLOG = "queue_backlog"
    CONNECTION_LOST = "connection_lost"
    SERVICE_DOWN = "service_down"
    PARSING_ERROR = "parsing_error"
    ROUTING_ERROR = "routing_error"
    TIMEOUT = "timeout"
    AUTHENTICATION_FAILURE = "authentication_failure"


class RemediationAction(Enum):
    """Available remediation actions"""
    RETRY_MESSAGE = "retry_message"
    RESTART_SERVICE = "restart_service"
    RECONNECT = "reconnect"
    CLEAR_QUEUE = "clear_queue"
    REROUTE_MESSAGE = "reroute_message"
    ALERT_TEAM = "alert_team"
    ESCALATE = "escalate"


class SelfHealingEngine:
    """
    Autonomous self-healing engine for HL7 integration issues
    """
    
    def __init__(self, ai_agent=None):
        self.ai_agent = ai_agent
        self.incident_history = []
        self.remediation_rules = self._initialize_rules()
        self.max_retry_attempts = 3
        self.retry_delay = 5  # seconds
        self.learning_enabled = True
        
    def _initialize_rules(self) -> Dict[IncidentType, List[Dict]]:
        """
        Initialize remediation rules for different incident types
        """
        return {
            IncidentType.MESSAGE_FAILURE: [
                {
                    'condition': lambda incident: incident.get('retry_count', 0) < 3,
                    'action': RemediationAction.RETRY_MESSAGE,
                    'priority': 1,
                    'description': 'Retry failed message up to 3 times'
                },
                {
                    'condition': lambda incident: incident.get('retry_count', 0) >= 3,
                    'action': RemediationAction.ALERT_TEAM,
                    'priority': 2,
                    'description': 'Alert team after 3 failed retries'
                }
            ],
            IncidentType.QUEUE_BACKLOG: [
                {
                    'condition': lambda incident: incident.get('queue_size', 0) > 1000,
                    'action': RemediationAction.CLEAR_QUEUE,
                    'priority': 1,
                    'description': 'Clear queue if backlog exceeds 1000 messages'
                },
                {
                    'condition': lambda incident: incident.get('queue_size', 0) > 500,
                    'action': RemediationAction.RESTART_SERVICE,
                    'priority': 2,
                    'description': 'Restart service if queue exceeds 500 messages'
                }
            ],
            IncidentType.CONNECTION_LOST: [
                {
                    'condition': lambda incident: True,
                    'action': RemediationAction.RECONNECT,
                    'priority': 1,
                    'description': 'Attempt to reconnect immediately'
                },
                {
                    'condition': lambda incident: incident.get('reconnect_attempts', 0) >= 3,
                    'action': RemediationAction.ALERT_TEAM,
                    'priority': 2,
                    'description': 'Alert team after 3 failed reconnection attempts'
                }
            ],
            IncidentType.SERVICE_DOWN: [
                {
                    'condition': lambda incident: True,
                    'action': RemediationAction.RESTART_SERVICE,
                    'priority': 1,
                    'description': 'Restart service immediately'
                },
                {
                    'condition': lambda incident: incident.get('restart_attempts', 0) >= 2,
                    'action': RemediationAction.ESCALATE,
                    'priority': 2,
                    'description': 'Escalate after 2 failed restart attempts'
                }
            ],
            IncidentType.PARSING_ERROR: [
                {
                    'condition': lambda incident: incident.get('error_type') == 'malformed_segment',
                    'action': RemediationAction.REROUTE_MESSAGE,
                    'priority': 1,
                    'description': 'Reroute malformed messages to error queue'
                },
                {
                    'condition': lambda incident: True,
                    'action': RemediationAction.ALERT_TEAM,
                    'priority': 2,
                    'description': 'Alert team for manual review'
                }
            ],
            IncidentType.ROUTING_ERROR: [
                {
                    'condition': lambda incident: True,
                    'action': RemediationAction.REROUTE_MESSAGE,
                    'priority': 1,
                    'description': 'Attempt alternative routing'
                }
            ],
            IncidentType.TIMEOUT: [
                {
                    'condition': lambda incident: incident.get('timeout_count', 0) < 3,
                    'action': RemediationAction.RETRY_MESSAGE,
                    'priority': 1,
                    'description': 'Retry with increased timeout'
                },
                {
                    'condition': lambda incident: incident.get('timeout_count', 0) >= 3,
                    'action': RemediationAction.ALERT_TEAM,
                    'priority': 2,
                    'description': 'Alert team after repeated timeouts'
                }
            ],
            IncidentType.AUTHENTICATION_FAILURE: [
                {
                    'condition': lambda incident: True,
                    'action': RemediationAction.RECONNECT,
                    'priority': 1,
                    'description': 'Reconnect with fresh credentials'
                },
                {
                    'condition': lambda incident: incident.get('auth_attempts', 0) >= 2,
                    'action': RemediationAction.ALERT_TEAM,
                    'priority': 2,
                    'description': 'Alert team - credentials may be invalid'
                }
            ]
        }
    
    async def detect_incident(self, monitoring_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect incidents from monitoring data
        
        Args:
            monitoring_data: Real-time monitoring metrics
            
        Returns:
            Incident details if detected, None otherwise
        """
        incidents = []
        
        # Check for message failures
        if monitoring_data.get('failed_messages', 0) > 0:
            incidents.append({
                'type': IncidentType.MESSAGE_FAILURE,
                'severity': IncidentSeverity.HIGH,
                'details': {
                    'failed_count': monitoring_data['failed_messages'],
                    'error_messages': monitoring_data.get('error_messages', [])
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for queue backlog
        queue_size = monitoring_data.get('queue_size', 0)
        if queue_size > 100:
            severity = IncidentSeverity.CRITICAL if queue_size > 1000 else IncidentSeverity.HIGH
            incidents.append({
                'type': IncidentType.QUEUE_BACKLOG,
                'severity': severity,
                'details': {
                    'queue_size': queue_size,
                    'threshold': 100
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for connection issues
        if not monitoring_data.get('connection_status', True):
            incidents.append({
                'type': IncidentType.CONNECTION_LOST,
                'severity': IncidentSeverity.CRITICAL,
                'details': {
                    'last_connected': monitoring_data.get('last_connected'),
                    'endpoint': monitoring_data.get('endpoint')
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for service health
        if not monitoring_data.get('service_healthy', True):
            incidents.append({
                'type': IncidentType.SERVICE_DOWN,
                'severity': IncidentSeverity.CRITICAL,
                'details': {
                    'service_name': monitoring_data.get('service_name'),
                    'last_heartbeat': monitoring_data.get('last_heartbeat')
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for parsing errors
        if monitoring_data.get('parsing_errors', 0) > 0:
            incidents.append({
                'type': IncidentType.PARSING_ERROR,
                'severity': IncidentSeverity.MEDIUM,
                'details': {
                    'error_count': monitoring_data['parsing_errors'],
                    'error_types': monitoring_data.get('error_types', [])
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for timeouts
        if monitoring_data.get('timeout_count', 0) > 0:
            incidents.append({
                'type': IncidentType.TIMEOUT,
                'severity': IncidentSeverity.MEDIUM,
                'details': {
                    'timeout_count': monitoring_data['timeout_count'],
                    'avg_response_time': monitoring_data.get('avg_response_time')
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return incidents[0] if incidents else None
    
    async def diagnose_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose incident using AI-powered root cause analysis
        
        Args:
            incident: Incident details
            
        Returns:
            Diagnosis with root cause and recommended actions
        """
        incident_type = incident['type']
        severity = incident['severity']
        details = incident['details']
        
        # AI-powered diagnosis
        if self.ai_agent:
            diagnosis_prompt = f"""
            Analyze this HL7 integration incident:
            
            Type: {incident_type.value}
            Severity: {severity.value}
            Details: {json.dumps(details, indent=2)}
            
            Provide:
            1. Root cause analysis
            2. Recommended remediation actions
            3. Prevention strategies
            """
            
            ai_diagnosis = await self.ai_agent.analyze(diagnosis_prompt)
        else:
            ai_diagnosis = self._rule_based_diagnosis(incident)
        
        diagnosis = {
            'incident_id': incident.get('id', datetime.utcnow().timestamp()),
            'incident_type': incident_type.value,
            'severity': severity.value,
            'root_cause': ai_diagnosis.get('root_cause', 'Unknown'),
            'recommended_actions': ai_diagnosis.get('actions', []),
            'prevention_strategies': ai_diagnosis.get('prevention', []),
            'confidence': ai_diagnosis.get('confidence', 0.8),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return diagnosis
    
    def _rule_based_diagnosis(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rule-based diagnosis when AI is not available
        """
        incident_type = incident['type']
        details = incident['details']
        
        diagnoses = {
            IncidentType.MESSAGE_FAILURE: {
                'root_cause': 'Message processing failure due to invalid format or system unavailability',
                'actions': ['Retry message', 'Validate message format', 'Check target system availability'],
                'prevention': ['Implement message validation', 'Add retry logic', 'Monitor system health']
            },
            IncidentType.QUEUE_BACKLOG: {
                'root_cause': 'Message processing slower than incoming rate or downstream system bottleneck',
                'actions': ['Scale processing capacity', 'Clear old messages', 'Restart service'],
                'prevention': ['Implement auto-scaling', 'Add queue monitoring', 'Optimize processing']
            },
            IncidentType.CONNECTION_LOST: {
                'root_cause': 'Network connectivity issue or target system unavailable',
                'actions': ['Reconnect', 'Check network', 'Verify target system status'],
                'prevention': ['Implement connection pooling', 'Add health checks', 'Use redundant connections']
            },
            IncidentType.SERVICE_DOWN: {
                'root_cause': 'Service crash or resource exhaustion',
                'actions': ['Restart service', 'Check logs', 'Verify resource availability'],
                'prevention': ['Implement health monitoring', 'Add resource limits', 'Use auto-restart']
            },
            IncidentType.PARSING_ERROR: {
                'root_cause': 'Malformed HL7 message or unsupported format',
                'actions': ['Validate message', 'Route to error queue', 'Alert team'],
                'prevention': ['Implement strict validation', 'Add format checking', 'Document standards']
            }
        }
        
        return diagnoses.get(incident_type, {
            'root_cause': 'Unknown',
            'actions': ['Alert team', 'Manual investigation required'],
            'prevention': ['Add monitoring', 'Document incident']
        })
    
    async def remediate_incident(self, incident: Dict[str, Any], diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically remediate incident based on diagnosis
        
        Args:
            incident: Incident details
            diagnosis: Diagnosis results
            
        Returns:
            Remediation results
        """
        incident_type = IncidentType(incident['type']) if isinstance(incident['type'], str) else incident['type']
        
        # Get applicable remediation rules
        rules = self.remediation_rules.get(incident_type, [])
        
        # Sort rules by priority
        rules = sorted(rules, key=lambda x: x['priority'])
        
        remediation_results = {
            'incident_id': incident.get('id'),
            'actions_taken': [],
            'success': False,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Execute remediation actions
        for rule in rules:
            if rule['condition'](incident.get('details', {})):
                action = rule['action']
                
                logger.info(f"Executing remediation action: {action.value}")
                
                try:
                    result = await self._execute_action(action, incident, diagnosis)
                    
                    remediation_results['actions_taken'].append({
                        'action': action.value,
                        'description': rule['description'],
                        'result': result,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                    if result.get('success'):
                        remediation_results['success'] = True
                        break  # Stop if remediation successful
                        
                except Exception as e:
                    logger.error(f"Error executing action {action.value}: {str(e)}")
                    remediation_results['actions_taken'].append({
                        'action': action.value,
                        'description': rule['description'],
                        'result': {'success': False, 'error': str(e)},
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        # Log remediation
        self._log_remediation(incident, diagnosis, remediation_results)
        
        return remediation_results
    
    async def _execute_action(self, action: RemediationAction, incident: Dict, diagnosis: Dict) -> Dict[str, Any]:
        """
        Execute specific remediation action
        """
        if action == RemediationAction.RETRY_MESSAGE:
            return await self._retry_message(incident)
        elif action == RemediationAction.RESTART_SERVICE:
            return await self._restart_service(incident)
        elif action == RemediationAction.RECONNECT:
            return await self._reconnect(incident)
        elif action == RemediationAction.CLEAR_QUEUE:
            return await self._clear_queue(incident)
        elif action == RemediationAction.REROUTE_MESSAGE:
            return await self._reroute_message(incident)
        elif action == RemediationAction.ALERT_TEAM:
            return await self._alert_team(incident, diagnosis)
        elif action == RemediationAction.ESCALATE:
            return await self._escalate(incident, diagnosis)
        else:
            return {'success': False, 'error': 'Unknown action'}
    
    async def _retry_message(self, incident: Dict) -> Dict[str, Any]:
        """Retry failed message"""
        logger.info("Retrying failed message...")
        
        # Simulate retry logic
        await asyncio.sleep(self.retry_delay)
        
        # In production, this would actually retry the message
        return {
            'success': True,
            'message': 'Message retry initiated',
            'retry_count': incident.get('details', {}).get('retry_count', 0) + 1
        }
    
    async def _restart_service(self, incident: Dict) -> Dict[str, Any]:
        """Restart service"""
        logger.info("Restarting service...")
        
        service_name = incident.get('details', {}).get('service_name', 'unknown')
        
        # In production, this would actually restart the service
        # Example: subprocess.run(['systemctl', 'restart', service_name])
        
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'message': f'Service {service_name} restarted successfully',
            'restart_time': datetime.utcnow().isoformat()
        }
    
    async def _reconnect(self, incident: Dict) -> Dict[str, Any]:
        """Reconnect to endpoint"""
        logger.info("Reconnecting to endpoint...")
        
        endpoint = incident.get('details', {}).get('endpoint', 'unknown')
        
        # In production, this would actually reconnect
        await asyncio.sleep(1)
        
        return {
            'success': True,
            'message': f'Reconnected to {endpoint}',
            'connection_time': datetime.utcnow().isoformat()
        }
    
    async def _clear_queue(self, incident: Dict) -> Dict[str, Any]:
        """Clear message queue"""
        logger.info("Clearing message queue...")
        
        queue_size = incident.get('details', {}).get('queue_size', 0)
        
        # In production, this would actually clear the queue
        # with proper archival and logging
        
        return {
            'success': True,
            'message': f'Cleared {queue_size} messages from queue',
            'archived': True
        }
    
    async def _reroute_message(self, incident: Dict) -> Dict[str, Any]:
        """Reroute message to alternative destination"""
        logger.info("Rerouting message...")
        
        # In production, this would route to error queue or alternative endpoint
        
        return {
            'success': True,
            'message': 'Message rerouted to error queue',
            'destination': 'error_queue'
        }
    
    async def _alert_team(self, incident: Dict, diagnosis: Dict) -> Dict[str, Any]:
        """Alert team about incident"""
        logger.info("Alerting team...")
        
        alert_message = f"""
        HL7 Incident Alert
        
        Type: {incident['type']}
        Severity: {incident['severity']}
        Root Cause: {diagnosis.get('root_cause', 'Unknown')}
        
        Details: {json.dumps(incident.get('details', {}), indent=2)}
        
        Recommended Actions:
        {chr(10).join(f"- {action}" for action in diagnosis.get('recommended_actions', []))}
        """
        
        # In production, send to PagerDuty, Slack, email, etc.
        
        return {
            'success': True,
            'message': 'Team alerted',
            'alert_sent_to': ['pagerduty', 'slack', 'email']
        }
    
    async def _escalate(self, incident: Dict, diagnosis: Dict) -> Dict[str, Any]:
        """Escalate incident to senior team"""
        logger.info("Escalating incident...")
        
        # In production, escalate to on-call manager
        
        return {
            'success': True,
            'message': 'Incident escalated to senior team',
            'escalated_to': 'on-call-manager'
        }
    
    def _log_remediation(self, incident: Dict, diagnosis: Dict, results: Dict):
        """Log remediation for audit trail"""
        log_entry = {
            'incident': incident,
            'diagnosis': diagnosis,
            'remediation': results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.incident_history.append(log_entry)
        
        # In production, store in database for compliance
        logger.info(f"Remediation logged: {json.dumps(log_entry, indent=2)}")
    
    async def autonomous_healing_loop(self, monitoring_service):
        """
        Continuous autonomous healing loop
        
        Args:
            monitoring_service: Service providing real-time monitoring data
        """
        logger.info("Starting autonomous healing loop...")
        
        while True:
            try:
                # Get monitoring data
                monitoring_data = await monitoring_service.get_current_metrics()
                
                # Detect incidents
                incident = await self.detect_incident(monitoring_data)
                
                if incident:
                    logger.warning(f"Incident detected: {incident['type'].value}")
                    
                    # Diagnose incident
                    diagnosis = await self.diagnose_incident(incident)
                    logger.info(f"Diagnosis: {diagnosis['root_cause']}")
                    
                    # Remediate incident
                    results = await self.remediate_incident(incident, diagnosis)
                    
                    if results['success']:
                        logger.info("Incident remediated successfully")
                    else:
                        logger.error("Remediation failed - manual intervention required")
                
                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in healing loop: {str(e)}")
                await asyncio.sleep(30)  # Wait longer on error


# Example usage
if __name__ == "__main__":
    async def main():
        # Create self-healing engine
        engine = SelfHealingEngine()
        
        # Simulate incident
        incident = {
            'type': IncidentType.MESSAGE_FAILURE,
            'severity': IncidentSeverity.HIGH,
            'details': {
                'failed_count': 5,
                'retry_count': 0,
                'error_messages': ['Connection timeout', 'Invalid response']
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Diagnose
        diagnosis = await engine.diagnose_incident(incident)
        print(f"Diagnosis: {json.dumps(diagnosis, indent=2)}")
        
        # Remediate
        results = await engine.remediate_incident(incident, diagnosis)
        print(f"Remediation: {json.dumps(results, indent=2)}")
    
    asyncio.run(main())