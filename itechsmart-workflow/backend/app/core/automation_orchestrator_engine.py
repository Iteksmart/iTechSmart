"""
iTechSmart Workflow - Automation Orchestrator Engine
Visual workflow builder with automation capabilities
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import json

from ..models.automation_orchestrator import (
    AutomationWorkflow, WorkflowNode, WorkflowEdge, WorkflowExecution,
    NodeExecution, WorkflowTrigger, WorkflowTemplate, IntegrationAction,
    WorkflowVariable, WorkflowSchedule, WorkflowWebhook, WorkflowLog,
    WorkflowMetrics, NodeType, TriggerType, ActionType, ExecutionStatus,
    WorkflowStatus
)


class AutomationOrchestratorEngine:
    """
    Automation orchestrator with visual workflow builder
    """
    
    def __init__(self):
        self.workflows: Dict[str, AutomationWorkflow] = {}
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: Dict[str, WorkflowEdge] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.node_executions: Dict[str, NodeExecution] = {}
        self.triggers: Dict[str, WorkflowTrigger] = {}
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.integration_actions: Dict[str, IntegrationAction] = {}
        self.variables: Dict[str, WorkflowVariable] = {}
        self.schedules: Dict[str, WorkflowSchedule] = {}
        self.webhooks: Dict[str, WorkflowWebhook] = {}
        self.logs: Dict[str, WorkflowLog] = {}
        self.metrics: Dict[str, WorkflowMetrics] = {}
        
        # Initialize templates and actions
        self._initialize_templates()
        self._initialize_integration_actions()
    
    # ========================================================================
    # INITIALIZATION
    # ========================================================================
    
    def _initialize_templates(self):
        """Initialize pre-built workflow templates"""
        templates = [
            {
                "name": "Incident Response Automation",
                "description": "Automatically respond to critical incidents",
                "category": "Incident Management",
                "workflow_data": {
                    "trigger": "incident_created",
                    "actions": ["notify_team", "create_ticket", "escalate"]
                }
            },
            {
                "name": "Deployment Pipeline",
                "description": "Automated CI/CD deployment workflow",
                "category": "DevOps",
                "workflow_data": {
                    "trigger": "git_push",
                    "actions": ["run_tests", "build", "deploy", "notify"]
                }
            },
            {
                "name": "Server Health Check",
                "description": "Monitor and restart unhealthy services",
                "category": "Infrastructure",
                "workflow_data": {
                    "trigger": "schedule",
                    "actions": ["check_health", "restart_if_needed", "alert"]
                }
            },
            {
                "name": "User Onboarding",
                "description": "Automate new user account setup",
                "category": "IT Operations",
                "workflow_data": {
                    "trigger": "user_created",
                    "actions": ["create_accounts", "assign_licenses", "send_welcome"]
                }
            },
            {
                "name": "Backup and Recovery",
                "description": "Automated backup workflow",
                "category": "Data Management",
                "workflow_data": {
                    "trigger": "schedule",
                    "actions": ["backup_database", "verify_backup", "notify"]
                }
            }
        ]
        
        for template_data in templates:
            template_id = f"tmpl_{uuid4().hex[:12]}"
            template = WorkflowTemplate(
                template_id=template_id,
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"]
            )
            template.workflow_data = template_data["workflow_data"]
            self.templates[template_id] = template
    
    def _initialize_integration_actions(self):
        """Initialize pre-configured integration actions"""
        actions = [
            # Incident Response
            {"name": "Create Incident", "type": ActionType.CREATE_INCIDENT, "integration": "iTechSmart"},
            {"name": "Update Incident", "type": ActionType.UPDATE_INCIDENT, "integration": "iTechSmart"},
            {"name": "Assign Incident", "type": ActionType.ASSIGN_INCIDENT, "integration": "iTechSmart"},
            {"name": "Escalate Incident", "type": ActionType.ESCALATE_INCIDENT, "integration": "iTechSmart"},
            {"name": "Resolve Incident", "type": ActionType.RESOLVE_INCIDENT, "integration": "iTechSmart"},
            
            # Deployment
            {"name": "Deploy Application", "type": ActionType.DEPLOY_APPLICATION, "integration": "Kubernetes"},
            {"name": "Rollback Deployment", "type": ActionType.ROLLBACK_DEPLOYMENT, "integration": "Kubernetes"},
            {"name": "Run Tests", "type": ActionType.RUN_TESTS, "integration": "Jenkins"},
            {"name": "Backup Database", "type": ActionType.BACKUP_DATABASE, "integration": "PostgreSQL"},
            
            # Infrastructure
            {"name": "Restart Service", "type": ActionType.RESTART_SERVICE, "integration": "SystemD"},
            {"name": "Execute Command", "type": ActionType.EXECUTE_COMMAND, "integration": "SSH"},
            {"name": "Run Script", "type": ActionType.RUN_SCRIPT, "integration": "Shell"},
            
            # Communication
            {"name": "Send Email", "type": ActionType.SEND_EMAIL, "integration": "SMTP"},
            {"name": "Send Slack Message", "type": ActionType.SEND_SLACK, "integration": "Slack"},
            {"name": "Send SMS", "type": ActionType.SEND_SMS, "integration": "Twilio"},
            {"name": "Create Ticket", "type": ActionType.CREATE_TICKET, "integration": "Jira"},
            
            # Data
            {"name": "Query Database", "type": ActionType.QUERY_DATABASE, "integration": "SQL"},
            {"name": "Call API", "type": ActionType.CALL_API, "integration": "HTTP"},
            {"name": "Transform Data", "type": ActionType.TRANSFORM_DATA, "integration": "JSONPath"}
        ]
        
        for action_data in actions:
            action_id = f"action_{uuid4().hex[:12]}"
            action = IntegrationAction(
                action_id=action_id,
                integration_name=action_data["integration"],
                action_name=action_data["name"],
                action_type=action_data["type"]
            )
            self.integration_actions[action_id] = action
    
    # ========================================================================
    # WORKFLOW MANAGEMENT
    # ========================================================================
    
    def create_workflow(
        self,
        name: str,
        description: str,
        user: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new workflow"""
        workflow_id = f"wf_{uuid4().hex[:12]}"
        workflow = AutomationWorkflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            created_by=user
        )
        workflow.category = category
        
        self.workflows[workflow_id] = workflow
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "name": name
        }
    
    def get_workflows(
        self,
        status: Optional[WorkflowStatus] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get workflows with filters"""
        workflows = list(self.workflows.values())
        
        if status:
            workflows = [w for w in workflows if w.status == status]
        if category:
            workflows = [w for w in workflows if w.category == category]
        
        return [
            {
                "workflow_id": w.workflow_id,
                "name": w.name,
                "description": w.description,
                "status": w.status.value,
                "category": w.category,
                "version": w.version,
                "execution_count": w.execution_count,
                "success_count": w.success_count,
                "failure_count": w.failure_count,
                "last_executed_at": w.last_executed_at.isoformat() if w.last_executed_at else None,
                "created_at": w.created_at.isoformat()
            }
            for w in workflows
        ]
    
    def update_workflow(
        self,
        workflow_id: str,
        updates: Dict[str, Any],
        user: str
    ) -> Dict[str, Any]:
        """Update workflow"""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        
        for key, value in updates.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        workflow.updated_at = datetime.utcnow()
        workflow.updated_by = user
        workflow.version += 1
        
        return {"success": True, "workflow_id": workflow_id, "version": workflow.version}
    
    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Activate workflow"""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.ACTIVE
        workflow.updated_at = datetime.utcnow()
        
        return {"success": True, "workflow_id": workflow_id, "status": "active"}
    
    # ========================================================================
    # NODE MANAGEMENT
    # ========================================================================
    
    def add_node(
        self,
        workflow_id: str,
        node_type: NodeType,
        label: str,
        position_x: float,
        position_y: float,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add node to workflow"""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        node_id = f"node_{uuid4().hex[:12]}"
        node = WorkflowNode(
            node_id=node_id,
            workflow_id=workflow_id,
            node_type=node_type,
            label=label
        )
        node.position_x = position_x
        node.position_y = position_y
        node.config = config
        
        self.nodes[node_id] = node
        
        # Update workflow canvas data
        workflow = self.workflows[workflow_id]
        workflow.canvas_data["nodes"].append({
            "id": node_id,
            "type": node_type.value,
            "position": {"x": position_x, "y": position_y},
            "data": {"label": label, "config": config}
        })
        workflow.updated_at = datetime.utcnow()
        
        return {"success": True, "node_id": node_id}
    
    def connect_nodes(
        self,
        workflow_id: str,
        source_node_id: str,
        target_node_id: str,
        condition: Optional[str] = None
    ) -> Dict[str, Any]:
        """Connect two nodes"""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            return {"success": False, "error": "Node not found"}
        
        edge_id = f"edge_{uuid4().hex[:12]}"
        edge = WorkflowEdge(
            edge_id=edge_id,
            workflow_id=workflow_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id
        )
        edge.condition = condition
        
        self.edges[edge_id] = edge
        
        # Update node connections
        source_node = self.nodes[source_node_id]
        target_node = self.nodes[target_node_id]
        source_node.output_connections.append(target_node_id)
        target_node.input_connections.append(source_node_id)
        
        # Update workflow canvas data
        workflow = self.workflows[workflow_id]
        workflow.canvas_data["edges"].append({
            "id": edge_id,
            "source": source_node_id,
            "target": target_node_id,
            "label": condition
        })
        workflow.updated_at = datetime.utcnow()
        
        return {"success": True, "edge_id": edge_id}
    
    def remove_node(self, workflow_id: str, node_id: str) -> Dict[str, Any]:
        """Remove node from workflow"""
        if node_id not in self.nodes:
            return {"success": False, "error": "Node not found"}
        
        # Remove connected edges
        edges_to_remove = [
            e for e in self.edges.values()
            if e.source_node_id == node_id or e.target_node_id == node_id
        ]
        for edge in edges_to_remove:
            del self.edges[edge.edge_id]
        
        # Remove node
        del self.nodes[node_id]
        
        # Update workflow canvas data
        workflow = self.workflows[workflow_id]
        workflow.canvas_data["nodes"] = [
            n for n in workflow.canvas_data["nodes"] if n["id"] != node_id
        ]
        workflow.canvas_data["edges"] = [
            e for e in workflow.canvas_data["edges"]
            if e["source"] != node_id and e["target"] != node_id
        ]
        workflow.updated_at = datetime.utcnow()
        
        return {"success": True, "node_id": node_id}
    
    # ========================================================================
    # WORKFLOW EXECUTION
    # ========================================================================
    
    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        triggered_by: str = "manual",
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute workflow"""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.ACTIVE:
            return {"success": False, "error": "Workflow is not active"}
        
        execution_id = f"exec_{uuid4().hex[:12]}"
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            triggered_by=triggered_by
        )
        execution.triggered_by_user = user
        execution.input_data = input_data
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        
        self.executions[execution_id] = execution
        
        # Update workflow stats
        workflow.execution_count += 1
        workflow.last_executed_at = datetime.utcnow()
        
        # Start execution (simplified - in production would be async)
        self._run_workflow_execution(execution_id)
        
        return {
            "success": True,
            "execution_id": execution_id,
            "status": execution.status.value
        }
    
    def _run_workflow_execution(self, execution_id: str):
        """Run workflow execution (simplified)"""
        execution = self.executions[execution_id]
        workflow = self.workflows[execution.workflow_id]
        
        # Get workflow nodes
        workflow_nodes = [
            n for n in self.nodes.values()
            if n.workflow_id == workflow.workflow_id
        ]
        
        # Find start node (trigger node)
        start_nodes = [n for n in workflow_nodes if n.node_type == NodeType.TRIGGER]
        
        if not start_nodes:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = "No trigger node found"
            execution.completed_at = datetime.utcnow()
            return
        
        # Execute nodes in order (simplified - should handle parallel, conditions, etc.)
        current_node = start_nodes[0]
        execution.current_node_id = current_node.node_id
        
        try:
            # Execute each node
            for node in workflow_nodes:
                node_exec_id = f"node_exec_{uuid4().hex[:12]}"
                node_execution = NodeExecution(
                    node_execution_id=node_exec_id,
                    execution_id=execution_id,
                    node_id=node.node_id,
                    node_type=node.node_type
                )
                node_execution.status = ExecutionStatus.RUNNING
                node_execution.started_at = datetime.utcnow()
                
                # Simulate node execution
                node_execution.status = ExecutionStatus.COMPLETED
                node_execution.completed_at = datetime.utcnow()
                node_execution.duration_seconds = 1.0
                
                self.node_executions[node_exec_id] = node_execution
                execution.completed_nodes.append(node.node_id)
            
            # Complete execution
            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()
            
            # Update workflow stats
            workflow.success_count += 1
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            workflow.failure_count += 1
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get execution status"""
        if execution_id not in self.executions:
            return {"success": False, "error": "Execution not found"}
        
        execution = self.executions[execution_id]
        
        # Get node executions
        node_executions = [
            {
                "node_id": ne.node_id,
                "status": ne.status.value,
                "duration": ne.duration_seconds
            }
            for ne in self.node_executions.values()
            if ne.execution_id == execution_id
        ]
        
        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "duration_seconds": execution.duration_seconds,
            "current_node_id": execution.current_node_id,
            "completed_nodes": execution.completed_nodes,
            "failed_nodes": execution.failed_nodes,
            "node_executions": node_executions,
            "error_message": execution.error_message
        }
    
    def cancel_execution(self, execution_id: str) -> Dict[str, Any]:
        """Cancel running execution"""
        if execution_id not in self.executions:
            return {"success": False, "error": "Execution not found"}
        
        execution = self.executions[execution_id]
        
        if execution.status != ExecutionStatus.RUNNING:
            return {"success": False, "error": "Execution is not running"}
        
        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        
        return {"success": True, "execution_id": execution_id}
    
    # ========================================================================
    # TRIGGER MANAGEMENT
    # ========================================================================
    
    def add_trigger(
        self,
        workflow_id: str,
        trigger_type: TriggerType,
        name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add trigger to workflow"""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        trigger_id = f"trigger_{uuid4().hex[:12]}"
        trigger = WorkflowTrigger(
            trigger_id=trigger_id,
            workflow_id=workflow_id,
            trigger_type=trigger_type,
            name=name
        )
        trigger.config = config
        
        # Set trigger-specific config
        if trigger_type == TriggerType.SCHEDULE:
            trigger.schedule_cron = config.get("cron")
        elif trigger_type == TriggerType.WEBHOOK:
            trigger.webhook_url = f"/webhooks/{trigger_id}"
            trigger.webhook_secret = uuid4().hex
        elif trigger_type == TriggerType.EVENT:
            trigger.event_type = config.get("event_type")
            trigger.event_source = config.get("event_source")
        
        self.triggers[trigger_id] = trigger
        
        return {
            "success": True,
            "trigger_id": trigger_id,
            "webhook_url": trigger.webhook_url if trigger_type == TriggerType.WEBHOOK else None
        }
    
    # ========================================================================
    # TEMPLATE MANAGEMENT
    # ========================================================================
    
    def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get workflow templates"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return [
            {
                "template_id": t.template_id,
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "use_count": t.use_count,
                "rating": t.rating
            }
            for t in templates
        ]
    
    def create_from_template(
        self,
        template_id: str,
        name: str,
        user: str
    ) -> Dict[str, Any]:
        """Create workflow from template"""
        if template_id not in self.templates:
            return {"success": False, "error": "Template not found"}
        
        template = self.templates[template_id]
        
        # Create workflow
        result = self.create_workflow(
            name=name,
            description=template.description,
            user=user,
            category=template.category
        )
        
        if result["success"]:
            workflow_id = result["workflow_id"]
            workflow = self.workflows[workflow_id]
            workflow.canvas_data = template.canvas_data.copy()
            
            template.use_count += 1
        
        return result
    
    # ========================================================================
    # INTEGRATION ACTIONS
    # ========================================================================
    
    def get_integration_actions(
        self,
        integration_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get available integration actions"""
        actions = list(self.integration_actions.values())
        
        if integration_name:
            actions = [a for a in actions if a.integration_name == integration_name]
        
        return [
            {
                "action_id": a.action_id,
                "integration_name": a.integration_name,
                "action_name": a.action_name,
                "action_type": a.action_type.value,
                "description": a.description,
                "requires_auth": a.requires_auth
            }
            for a in actions
        ]
    
    # ========================================================================
    # METRICS & ANALYTICS
    # ========================================================================
    
    def get_workflow_metrics(
        self,
        workflow_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get workflow performance metrics"""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        
        # Get executions for period
        period_start = datetime.utcnow() - timedelta(days=days)
        executions = [
            e for e in self.executions.values()
            if e.workflow_id == workflow_id and e.created_at >= period_start
        ]
        
        total = len(executions)
        successful = len([e for e in executions if e.status == ExecutionStatus.COMPLETED])
        failed = len([e for e in executions if e.status == ExecutionStatus.FAILED])
        
        # Calculate average duration
        completed_executions = [e for e in executions if e.duration_seconds]
        avg_duration = None
        if completed_executions:
            avg_duration = sum(e.duration_seconds for e in completed_executions) / len(completed_executions)
        
        return {
            "workflow_id": workflow_id,
            "period_days": days,
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "average_duration_seconds": avg_duration
        }
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get overall dashboard metrics"""
        total_workflows = len(self.workflows)
        active_workflows = len([w for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE])
        total_executions = len(self.executions)
        running_executions = len([e for e in self.executions.values() if e.status == ExecutionStatus.RUNNING])
        
        return {
            "total_workflows": total_workflows,
            "active_workflows": active_workflows,
            "total_executions": total_executions,
            "running_executions": running_executions,
            "templates_available": len(self.templates),
            "integration_actions": len(self.integration_actions)
        }