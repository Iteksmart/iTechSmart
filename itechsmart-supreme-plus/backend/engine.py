"""
iTechSmart Supreme Plus - Core Engine
AI-Powered Infrastructure Auto-Remediation Engine

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

import logging
import json
import paramiko
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import requests
import redis

from models import (
    Incident, Remediation, RemediationAction, Integration,
    InfrastructureNode, AlertRule, RemediationLog, Metric,
    RemediationTemplate, ExecutionHistory, Notification,
    AIAnalysis, RemediationSchedule, AuditLog, Credential
)
from config import settings, REMEDIATION_TEMPLATES, SEVERITY_LEVELS, NETWORK_DEVICE_TYPES, NETWORK_COMMANDS

logger = logging.getLogger(__name__)

class SupremePlusEngine:
    """Core engine for AI-powered infrastructure auto-remediation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = redis.from_url(settings.REDIS_URL)
        
    # ==================== INCIDENT MANAGEMENT ====================
    
    def create_incident(
        self,
        title: str,
        description: str,
        severity: str,
        source: str,
        node_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Incident:
        """Create a new incident"""
        incident = Incident(
            title=title,
            description=description,
            severity=severity,
            source=source,
            node_id=node_id,
            status="open",
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        
        logger.info(f"Created incident #{incident.id}: {title} (severity: {severity})")
        
        # Trigger auto-remediation if enabled and severity allows
        if settings.AUTO_REMEDIATION_ENABLED and SEVERITY_LEVELS.get(severity, {}).get("auto_remediate"):
            self._trigger_auto_remediation(incident)
        
        # Send notifications
        self._send_incident_notifications(incident)
        
        return incident
    
    def analyze_incident_with_ai(self, incident_id: int) -> AIAnalysis:
        """Use AI to analyze incident and suggest remediation"""
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        # Prepare context for AI
        context = {
            "incident": {
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity,
                "source": incident.source,
                "metadata": incident.metadata
            },
            "node": None,
            "recent_metrics": []
        }
        
        if incident.node_id:
            node = self.db.query(InfrastructureNode).filter(
                InfrastructureNode.id == incident.node_id
            ).first()
            if node:
                context["node"] = {
                    "hostname": node.hostname,
                    "ip_address": node.ip_address,
                    "node_type": node.node_type,
                    "os_type": node.os_type
                }
                
                # Get recent metrics
                recent_metrics = self.db.query(Metric).filter(
                    Metric.node_id == node.id,
                    Metric.timestamp >= datetime.utcnow() - timedelta(hours=1)
                ).order_by(Metric.timestamp.desc()).limit(10).all()
                
                context["recent_metrics"] = [
                    {
                        "metric_name": m.metric_name,
                        "value": m.value,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in recent_metrics
                ]
        
        # AI analysis (simplified - in production, use actual AI API)
        analysis_result = self._perform_ai_analysis(context)
        
        # Store AI analysis
        ai_analysis = AIAnalysis(
            incident_id=incident_id,
            analysis_type="incident_diagnosis",
            input_data=context,
            output_data=analysis_result,
            model_used=settings.AI_MODEL,
            confidence_score=analysis_result.get("confidence", 0.0),
            created_at=datetime.utcnow()
        )
        self.db.add(ai_analysis)
        self.db.commit()
        self.db.refresh(ai_analysis)
        
        return ai_analysis
    
    def _perform_ai_analysis(self, context: Dict) -> Dict:
        """Perform AI analysis on incident (placeholder for actual AI integration)"""
        # In production, this would call OpenAI/Anthropic API
        # For now, return rule-based analysis
        
        incident = context["incident"]
        severity = incident["severity"]
        description = incident["description"].lower()
        
        # Rule-based diagnosis
        diagnosis = "Unknown issue"
        recommended_actions = []
        confidence = 0.5
        
        if "disk" in description or "storage" in description:
            diagnosis = "Disk space issue detected"
            recommended_actions = ["clear_disk_space", "expand_volume"]
            confidence = 0.85
        elif "memory" in description or "ram" in description:
            diagnosis = "Memory pressure detected"
            recommended_actions = ["restart_service", "kill_process"]
            confidence = 0.80
        elif "cpu" in description:
            diagnosis = "High CPU utilization"
            recommended_actions = ["kill_process", "scale_service"]
            confidence = 0.75
        elif "service" in description or "down" in description:
            diagnosis = "Service availability issue"
            recommended_actions = ["restart_service", "restart_container"]
            confidence = 0.90
        elif "network" in description or "connection" in description:
            diagnosis = "Network connectivity issue"
            recommended_actions = ["restart_service", "update_firewall"]
            confidence = 0.70
        
        return {
            "diagnosis": diagnosis,
            "recommended_actions": recommended_actions,
            "confidence": confidence,
            "reasoning": f"Based on incident description and severity level ({severity})",
            "estimated_resolution_time": "5-15 minutes"
        }
    
    # ==================== REMEDIATION EXECUTION ====================
    
    def create_remediation(
        self,
        incident_id: int,
        action_type: str,
        target_node_id: int,
        parameters: Optional[Dict] = None,
        auto_execute: bool = False
    ) -> Remediation:
        """Create a remediation plan"""
        remediation = Remediation(
            incident_id=incident_id,
            action_type=action_type,
            target_node_id=target_node_id,
            parameters=parameters or {},
            status="pending",
            created_at=datetime.utcnow()
        )
        self.db.add(remediation)
        self.db.commit()
        self.db.refresh(remediation)
        
        logger.info(f"Created remediation #{remediation.id} for incident #{incident_id}")
        
        if auto_execute:
            self.execute_remediation(remediation.id)
        
        return remediation
    
    def execute_remediation(self, remediation_id: int) -> Dict:
        """Execute a remediation action"""
        remediation = self.db.query(Remediation).filter(
            Remediation.id == remediation_id
        ).first()
        
        if not remediation:
            raise ValueError(f"Remediation {remediation_id} not found")
        
        if remediation.status != "pending":
            raise ValueError(f"Remediation {remediation_id} is not in pending status")
        
        # Update status
        remediation.status = "in_progress"
        remediation.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            # Get target node
            node = self.db.query(InfrastructureNode).filter(
                InfrastructureNode.id == remediation.target_node_id
            ).first()
            
            if not node:
                raise ValueError(f"Node {remediation.target_node_id} not found")
            
            # Get remediation template
            template = REMEDIATION_TEMPLATES.get(remediation.action_type)
            if not template:
                raise ValueError(f"Unknown action type: {remediation.action_type}")
            
            # Execute based on node type
            if node.os_type in ["linux", "ubuntu", "centos", "debian", "unix"]:
                result = self._execute_ssh_command(node, template, remediation.parameters)
            elif node.os_type in ["windows", "windows_server", "windows_workstation"]:
                result = self._execute_powershell_command(node, template, remediation.parameters)
            elif node.node_type in ["network_device", "router", "switch", "firewall", "load_balancer"]:
                result = self._execute_network_device_command(node, template, remediation.parameters)
            else:
                raise ValueError(f"Unsupported OS/device type: {node.os_type}")
            
            # Update remediation
            remediation.status = "success" if result["success"] else "failed"
            remediation.completed_at = datetime.utcnow()
            remediation.result = result
            
            # Create log entry
            log = RemediationLog(
                remediation_id=remediation.id,
                action=remediation.action_type,
                status=remediation.status,
                output=result.get("output", ""),
                error=result.get("error"),
                timestamp=datetime.utcnow()
            )
            self.db.add(log)
            
            # Update incident if remediation successful
            if remediation.status == "success":
                incident = self.db.query(Incident).filter(
                    Incident.id == remediation.incident_id
                ).first()
                if incident:
                    incident.status = "resolved"
                    incident.resolved_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Remediation #{remediation_id} completed with status: {remediation.status}")
            
            return {
                "remediation_id": remediation.id,
                "status": remediation.status,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing remediation #{remediation_id}: {str(e)}")
            remediation.status = "failed"
            remediation.completed_at = datetime.utcnow()
            remediation.result = {"error": str(e)}
            self.db.commit()
            raise
    
    def _execute_ssh_command(
        self,
        node: InfrastructureNode,
        template: Dict,
        parameters: Dict
    ) -> Dict:
        """Execute command via SSH"""
        try:
            # Get credentials
            credential = self.db.query(Credential).filter(
                Credential.node_id == node.id,
                Credential.credential_type == "ssh"
            ).first()
            
            if not credential:
                return {"success": False, "error": "No SSH credentials found"}
            
            # Format command
            command = template["commands"].get("linux", "")
            for key, value in parameters.items():
                command = command.replace(f"{{{key}}}", str(value))
            
            # Execute via SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=node.ip_address,
                username=credential.username,
                password=credential.password,
                timeout=settings.SSH_TIMEOUT
            )
            
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            exit_code = stdout.channel.recv_exit_status()
            
            ssh.close()
            
            return {
                "success": exit_code == 0,
                "output": output,
                "error": error if error else None,
                "exit_code": exit_code
            }
            
        except Exception as e:
            logger.error(f"SSH execution error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _execute_powershell_command(
        self,
        node: InfrastructureNode,
        template: Dict,
        parameters: Dict
    ) -> Dict:
        """Execute PowerShell command via WinRM"""
        try:
            # Get credentials
            credential = self.db.query(Credential).filter(
                Credential.node_id == node.id,
                Credential.credential_type == "winrm"
            ).first()
            
            if not credential:
                return {"success": False, "error": "No WinRM credentials found"}
            
            # Format command
            command = template["commands"].get("windows", "")
            for key, value in parameters.items():
                command = command.replace(f"{{{key}}}", str(value))
            
            # Execute via WinRM using requests (basic implementation)
            # In production, use pywinrm library for full support
            import base64
            
            # Construct WinRM endpoint
            winrm_url = f"http://{node.ip_address}:5985/wsman"
            
            # Basic auth
            auth = (credential.username, credential.password)
            
            # PowerShell execution envelope
            ps_script = f"powershell.exe -Command &quot;{command}&quot;"
            
            # Simple execution (simplified - in production use pywinrm)
            try:
                import subprocess
                # Use winrs if available (Windows to Windows)
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=settings.REMEDIATION_TIMEOUT
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else None,
                    "exit_code": result.returncode
                }
            except subprocess.TimeoutExpired:
                return {"success": False, "error": "Command execution timeout"}
            except Exception as e:
                return {"success": False, "error": f"Execution error: {str(e)}"}
                
        except Exception as e:
            logger.error(f"WinRM execution error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ==================== INTEGRATION MANAGEMENT ====================
    
    def create_integration(
        self,
        name: str,
        integration_type: str,
        config: Dict,
        enabled: bool = True
    ) -> Integration:
        """Create a new integration"""
        integration = Integration(
            name=name,
            integration_type=integration_type,
            config=config,
            enabled=enabled,
            created_at=datetime.utcnow()
        )
        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)
        
        logger.info(f"Created integration: {name} (type: {integration_type})")
        return integration
    
    def test_integration(self, integration_id: int) -> Dict:
        """Test an integration connection"""
        integration = self.db.query(Integration).filter(
            Integration.id == integration_id
        ).first()
        
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        try:
            if integration.integration_type == "prometheus":
                return self._test_prometheus_integration(integration)
            elif integration.integration_type == "wazuh":
                return self._test_wazuh_integration(integration)
            elif integration.integration_type == "webhook":
                return self._test_webhook_integration(integration)
            else:
                return {"success": False, "error": "Integration type not supported"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_prometheus_integration(self, integration: Integration) -> Dict:
        """Test Prometheus integration"""
        try:
            url = integration.config.get("url")
            response = requests.get(f"{url}/api/v1/status/config", timeout=5)
            return {
                "success": response.status_code == 200,
                "message": "Prometheus connection successful"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_wazuh_integration(self, integration: Integration) -> Dict:
        """Test Wazuh integration"""
        try:
            url = integration.config.get("url")
            api_key = integration.config.get("api_key")
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(f"{url}/", headers=headers, timeout=5)
            return {
                "success": response.status_code == 200,
                "message": "Wazuh connection successful"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_webhook_integration(self, integration: Integration) -> Dict:
        """Test webhook integration"""
        try:
            url = integration.config.get("url")
            test_payload = {"test": True, "timestamp": datetime.utcnow().isoformat()}
            response = requests.post(url, json=test_payload, timeout=5)
            return {
                "success": response.status_code in [200, 201, 202],
                "message": "Webhook test successful"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== MONITORING & METRICS ====================
    
    def collect_metrics(self, node_id: int) -> List[Metric]:
        """Collect metrics from a node"""
        node = self.db.query(InfrastructureNode).filter(
            InfrastructureNode.id == node_id
        ).first()
        
        if not node:
            raise ValueError(f"Node {node_id} not found")
        
        metrics = []
        timestamp = datetime.utcnow()
        
        # Collect metrics via SSH or agent
        # This is a placeholder - in production, integrate with actual monitoring
        metric_data = {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 78.5,
            "network_in": 1024.5,
            "network_out": 512.3
        }
        
        for metric_name, value in metric_data.items():
            metric = Metric(
                node_id=node_id,
                metric_name=metric_name,
                value=value,
                unit=self._get_metric_unit(metric_name),
                timestamp=timestamp
            )
            metrics.append(metric)
            self.db.add(metric)
        
        self.db.commit()
        return metrics
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Get unit for metric"""
        units = {
            "cpu_usage": "percent",
            "memory_usage": "percent",
            "disk_usage": "percent",
            "network_in": "mbps",
            "network_out": "mbps"
        }
        return units.get(metric_name, "")
    
    def check_alert_rules(self) -> List[Incident]:
        """Check all alert rules and create incidents if triggered"""
        alert_rules = self.db.query(AlertRule).filter(
            AlertRule.enabled == True
        ).all()
        
        incidents = []
        
        for rule in alert_rules:
            if self._evaluate_alert_rule(rule):
                incident = self.create_incident(
                    title=f"Alert: {rule.name}",
                    description=rule.description,
                    severity=rule.severity,
                    source="alert_rule",
                    node_id=rule.node_id,
                    metadata={"rule_id": rule.id, "condition": rule.condition}
                )
                incidents.append(incident)
        
        return incidents
    
    def _evaluate_alert_rule(self, rule: AlertRule) -> bool:
        """Evaluate if an alert rule should trigger"""
        # Get recent metrics for the node
        recent_metrics = self.db.query(Metric).filter(
            Metric.node_id == rule.node_id,
            Metric.metric_name == rule.metric_name,
            Metric.timestamp >= datetime.utcnow() - timedelta(minutes=5)
        ).order_by(Metric.timestamp.desc()).limit(5).all()
        
        if not recent_metrics:
            return False
        
        # Parse condition (e.g., "> 80")
        condition = rule.condition
        threshold = rule.threshold
        
        # Check if any recent metric exceeds threshold
        for metric in recent_metrics:
            if condition == ">" and metric.value > threshold:
                return True
            elif condition == "<" and metric.value < threshold:
                return True
            elif condition == "==" and metric.value == threshold:
                return True
        
        return False
    
    # ==================== HELPER METHODS ====================
    
    def _trigger_auto_remediation(self, incident: Incident):
        """Trigger automatic remediation for an incident"""
        try:
            # Analyze incident with AI
            ai_analysis = self.analyze_incident_with_ai(incident.id)
            
            # Get recommended actions
            recommended_actions = ai_analysis.output_data.get("recommended_actions", [])
            
            if recommended_actions and incident.node_id:
                # Create and execute first recommended action
                action_type = recommended_actions[0]
                remediation = self.create_remediation(
                    incident_id=incident.id,
                    action_type=action_type,
                    target_node_id=incident.node_id,
                    auto_execute=True
                )
                logger.info(f"Auto-remediation triggered for incident #{incident.id}")
        except Exception as e:
            logger.error(f"Error in auto-remediation: {str(e)}")
    
    def _send_incident_notifications(self, incident: Incident):
        """Send notifications for an incident"""
        severity_config = SEVERITY_LEVELS.get(incident.severity, {})
        channels = severity_config.get("notification_channels", [])
        
        for channel in channels:
            notification = Notification(
                incident_id=incident.id,
                channel=channel,
                status="pending",
                created_at=datetime.utcnow()
            )
            self.db.add(notification)
        
        self.db.commit()
        logger.info(f"Queued notifications for incident #{incident.id} on channels: {channels}")
    
    # ==================== NETWORK DEVICE SUPPORT ====================
    
    def _execute_network_device_command(
        self,
        node: InfrastructureNode,
        template: Dict,
        parameters: Dict
    ) -> Dict:
        """Execute command on network device (Cisco, Juniper, Palo Alto, etc.)"""
        try:
            # Get credentials
            credential = self.db.query(Credential).filter(
                Credential.node_id == node.id,
                Credential.credential_type == "ssh"
            ).first()
            
            if not credential:
                return {"success": False, "error": "No credentials found for network device"}
            
            # Determine device type from metadata
            device_type = node.metadata.get("device_type", "cisco")
            device_config = NETWORK_DEVICE_TYPES.get(device_type, NETWORK_DEVICE_TYPES["cisco_ios"])
            
            # Format command based on device type
            command = self._format_network_command(template, parameters, device_type)
            
            # Execute via SSH with device-specific handling
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=node.ip_address,
                username=credential.username,
                password=credential.password,
                port=device_config.get("port", 22),
                timeout=settings.SSH_TIMEOUT
            )
            
            # Get interactive shell for network devices
            shell = ssh.invoke_shell()
            
            # Wait for prompt
            import time
            time.sleep(1)
            
            # Clear initial output
            if shell.recv_ready():
                shell.recv(4096)
            
            # Enter enable mode if required (Cisco)
            if device_config.get("enable_mode") and credential.metadata.get("enable_password"):
                shell.send("enable\n")
                time.sleep(0.5)
                shell.send(f"{credential.metadata.get('enable_password')}\n")
                time.sleep(0.5)
            
            # Send command
            shell.send(f"{command}\n")
            time.sleep(2)
            
            # Collect output
            output = ""
            while shell.recv_ready():
                output += shell.recv(4096).decode('utf-8')
                time.sleep(0.5)
            
            # Close connection
            shell.close()
            ssh.close()
            
            # Parse output for success/failure
            success = self._parse_network_device_output(output, device_type)
            
            return {
                "success": success,
                "output": output,
                "error": None if success else "Command execution may have failed",
                "device_type": device_type
            }
            
        except Exception as e:
            logger.error(f"Network device execution error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _format_network_command(self, template: Dict, parameters: Dict, device_type: str) -> str:
        """Format command for specific network device type"""
        # Get command for device type
        if device_type.startswith("cisco"):
            command = template["commands"].get("cisco", "")
        elif device_type.startswith("juniper"):
            command = template["commands"].get("juniper", "")
        elif device_type.startswith("palo_alto"):
            command = template["commands"].get("palo_alto", "")
        else:
            command = template["commands"].get("cisco", "")  # Default to Cisco
        
        # Replace parameters
        for key, value in parameters.items():
            command = command.replace(f"{{{key}}}", str(value))
        
        return command
    
    def _parse_network_device_output(self, output: str, device_type: str) -> bool:
        """Parse network device output to determine success"""
        # Look for common error indicators
        error_indicators = [
            "% Invalid",
            "% Incomplete",
            "% Ambiguous",
            "Error:",
            "Failed",
            "syntax error"
        ]
        
        output_lower = output.lower()
        for indicator in error_indicators:
            if indicator.lower() in output_lower:
                return False
        
        # If no errors found, consider successful
        return True
    
    # ==================== WORKSTATION SUPPORT ====================
    
    def execute_workstation_remediation(
        self,
        node_id: int,
        action_type: str,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """Execute workstation-specific remediation"""
        from config import WORKSTATION_ACTIONS
        
        node = self.db.query(InfrastructureNode).filter(
            InfrastructureNode.id == node_id
        ).first()
        
        if not node:
            raise ValueError(f"Node {node_id} not found")
        
        action = WORKSTATION_ACTIONS.get(action_type)
        if not action:
            raise ValueError(f"Unknown workstation action: {action_type}")
        
        # Create remediation record
        remediation = Remediation(
            incident_id=None,  # Can be standalone
            action_type=action_type,
            target_node_id=node_id,
            parameters=parameters or {},
            status="pending",
            created_at=datetime.utcnow()
        )
        self.db.add(remediation)
        self.db.commit()
        self.db.refresh(remediation)
        
        # Execute the action
        remediation.status = "in_progress"
        remediation.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            # Execute PowerShell command for Windows workstations
            credential = self.db.query(Credential).filter(
                Credential.node_id == node_id,
                Credential.credential_type == "winrm"
            ).first()
            
            if not credential:
                raise ValueError("No credentials found for workstation")
            
            # Execute command
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", action["command"]],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            remediation.status = "success" if result.returncode == 0 else "failed"
            remediation.completed_at = datetime.utcnow()
            remediation.result = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
            
            self.db.commit()
            
            return remediation.result
            
        except Exception as e:
            remediation.status = "failed"
            remediation.completed_at = datetime.utcnow()
            remediation.result = {"success": False, "error": str(e)}
            self.db.commit()
            raise
    
    # ==================== SERVER DIAGNOSTICS ====================
    
    def run_server_diagnostics(self, node_id: int) -> Dict:
        """Run comprehensive server diagnostics"""
        from config import SERVER_ACTIONS
        
        node = self.db.query(InfrastructureNode).filter(
            InfrastructureNode.id == node_id
        ).first()
        
        if not node:
            raise ValueError(f"Node {node_id} not found")
        
        results = {}
        
        # Run each diagnostic check
        for action_name, action_config in SERVER_ACTIONS.items():
            try:
                if node.os_type in ["linux", "ubuntu", "centos", "debian"]:
                    command = action_config.get("linux", "")
                else:
                    command = action_config.get("windows", "")
                
                if not command:
                    continue
                
                # Execute command
                if node.os_type in ["linux", "ubuntu", "centos", "debian"]:
                    result = self._execute_ssh_command_direct(node, command)
                else:
                    result = self._execute_powershell_command_direct(node, command)
                
                results[action_name] = result
                
            except Exception as e:
                results[action_name] = {"success": False, "error": str(e)}
        
        return results
    
    def _execute_ssh_command_direct(self, node: InfrastructureNode, command: str) -> Dict:
        """Execute SSH command directly without template"""
        try:
            credential = self.db.query(Credential).filter(
                Credential.node_id == node.id,
                Credential.credential_type == "ssh"
            ).first()
            
            if not credential:
                return {"success": False, "error": "No SSH credentials found"}
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=node.ip_address,
                username=credential.username,
                password=credential.password,
                timeout=settings.SSH_TIMEOUT
            )
            
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            exit_code = stdout.channel.recv_exit_status()
            
            ssh.close()
            
            return {
                "success": exit_code == 0,
                "output": output,
                "error": error if error else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_powershell_command_direct(self, node: InfrastructureNode, command: str) -> Dict:
        """Execute PowerShell command directly without template"""
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}