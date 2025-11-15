"""
Workflow Automation Engine for iTechSmart Ninja
Provides workflow creation, execution, and management
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(str, Enum):
    """Workflow trigger types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"
    API = "api"


class ActionType(str, Enum):
    """Workflow action types"""
    HTTP_REQUEST = "http_request"
    RUN_CODE = "run_code"
    SEND_EMAIL = "send_email"
    SEND_NOTIFICATION = "send_notification"
    CREATE_FILE = "create_file"
    TRANSFORM_DATA = "transform_data"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    DELAY = "delay"
    AI_TASK = "ai_task"


class ConditionOperator(str, Enum):
    """Conditional operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


@dataclass
class WorkflowTrigger:
    """Workflow trigger configuration"""
    trigger_type: TriggerType
    config: Dict[str, Any]
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_type": self.trigger_type.value,
            "config": self.config,
            "enabled": self.enabled
        }


@dataclass
class WorkflowAction:
    """Workflow action configuration"""
    action_id: str
    action_type: ActionType
    name: str
    config: Dict[str, Any]
    next_action: Optional[str] = None
    on_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "name": self.name,
            "config": self.config,
            "next_action": self.next_action,
            "on_error": self.on_error
        }


@dataclass
class WorkflowCondition:
    """Conditional logic for workflows"""
    field: str
    operator: ConditionOperator
    value: Any
    
    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate condition against data"""
        field_value = data.get(self.field)
        
        if self.operator == ConditionOperator.EQUALS:
            return field_value == self.value
        elif self.operator == ConditionOperator.NOT_EQUALS:
            return field_value != self.value
        elif self.operator == ConditionOperator.GREATER_THAN:
            return field_value > self.value
        elif self.operator == ConditionOperator.LESS_THAN:
            return field_value < self.value
        elif self.operator == ConditionOperator.CONTAINS:
            return self.value in str(field_value)
        elif self.operator == ConditionOperator.NOT_CONTAINS:
            return self.value not in str(field_value)
        elif self.operator == ConditionOperator.IN:
            return field_value in self.value
        elif self.operator == ConditionOperator.NOT_IN:
            return field_value not in self.value
        
        return False


@dataclass
class Workflow:
    """Workflow definition"""
    workflow_id: str
    name: str
    description: str
    trigger: WorkflowTrigger
    actions: List[WorkflowAction]
    status: WorkflowStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "trigger": self.trigger.to_dict(),
            "actions": [action.to_dict() for action in self.actions],
            "status": self.status.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "tags": self.tags
        }


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime]
    trigger_data: Dict[str, Any]
    execution_log: List[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "trigger_data": self.trigger_data,
            "execution_log": self.execution_log,
            "result": self.result,
            "error_message": self.error_message
        }


class WorkflowEngine:
    """Manages workflow creation and execution"""
    
    def __init__(self):
        """Initialize workflow engine"""
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.action_handlers: Dict[ActionType, Callable] = {}
        self._register_default_handlers()
        logger.info("WorkflowEngine initialized successfully")
    
    def _register_default_handlers(self):
        """Register default action handlers"""
        self.action_handlers[ActionType.HTTP_REQUEST] = self._handle_http_request
        self.action_handlers[ActionType.RUN_CODE] = self._handle_run_code
        self.action_handlers[ActionType.SEND_EMAIL] = self._handle_send_email
        self.action_handlers[ActionType.SEND_NOTIFICATION] = self._handle_send_notification
        self.action_handlers[ActionType.CREATE_FILE] = self._handle_create_file
        self.action_handlers[ActionType.TRANSFORM_DATA] = self._handle_transform_data
        self.action_handlers[ActionType.CONDITIONAL] = self._handle_conditional
        self.action_handlers[ActionType.LOOP] = self._handle_loop
        self.action_handlers[ActionType.DELAY] = self._handle_delay
        self.action_handlers[ActionType.AI_TASK] = self._handle_ai_task
    
    async def create_workflow(
        self,
        name: str,
        description: str,
        trigger: WorkflowTrigger,
        actions: List[WorkflowAction],
        created_by: str,
        tags: Optional[List[str]] = None
    ) -> Workflow:
        """
        Create a new workflow
        
        Args:
            name: Workflow name
            description: Workflow description
            trigger: Workflow trigger configuration
            actions: List of workflow actions
            created_by: User ID
            tags: Optional tags
            
        Returns:
            Workflow object
        """
        workflow_id = str(uuid.uuid4())
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            trigger=trigger,
            actions=actions,
            status=WorkflowStatus.DRAFT,
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=tags or []
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Workflow {workflow_id} created: {name}")
        
        return workflow
    
    async def activate_workflow(self, workflow_id: str) -> Workflow:
        """Activate a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.status = WorkflowStatus.ACTIVE
        workflow.updated_at = datetime.now()
        
        logger.info(f"Workflow {workflow_id} activated")
        return workflow
    
    async def pause_workflow(self, workflow_id: str) -> Workflow:
        """Pause a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.status = WorkflowStatus.PAUSED
        workflow.updated_at = datetime.now()
        
        logger.info(f"Workflow {workflow_id} paused")
        return workflow
    
    async def execute_workflow(
        self,
        workflow_id: str,
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """
        Execute a workflow
        
        Args:
            workflow_id: Workflow ID
            trigger_data: Optional trigger data
            
        Returns:
            WorkflowExecution object
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if workflow.status not in [WorkflowStatus.ACTIVE, WorkflowStatus.DRAFT]:
            raise ValueError(f"Workflow {workflow_id} is not active (status: {workflow.status})")
        
        execution_id = str(uuid.uuid4())
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.ACTIVE,
            started_at=datetime.now(),
            completed_at=None,
            trigger_data=trigger_data or {},
            execution_log=[],
            result=None,
            error_message=None
        )
        
        self.executions[execution_id] = execution
        
        try:
            # Execute workflow actions
            context = {"trigger_data": trigger_data or {}}
            
            # Start with first action
            current_action_id = workflow.actions[0].action_id if workflow.actions else None
            
            while current_action_id:
                action = next((a for a in workflow.actions if a.action_id == current_action_id), None)
                if not action:
                    break
                
                # Log action start
                execution.execution_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "status": "started"
                })
                
                try:
                    # Execute action
                    handler = self.action_handlers.get(action.action_type)
                    if handler:
                        result = await handler(action, context)
                        context[action.action_id] = result
                        
                        # Log action success
                        execution.execution_log.append({
                            "timestamp": datetime.now().isoformat(),
                            "action_id": action.action_id,
                            "action_type": action.action_type.value,
                            "status": "completed",
                            "result": result
                        })
                        
                        # Move to next action
                        current_action_id = action.next_action
                    else:
                        raise ValueError(f"No handler for action type: {action.action_type}")
                
                except Exception as e:
                    logger.error(f"Error executing action {action.action_id}: {e}")
                    
                    # Log action error
                    execution.execution_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "action_id": action.action_id,
                        "action_type": action.action_type.value,
                        "status": "failed",
                        "error": str(e)
                    })
                    
                    # Handle error
                    if action.on_error:
                        current_action_id = action.on_error
                    else:
                        raise
            
            # Workflow completed successfully
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.result = context
            
            logger.info(f"Workflow execution {execution_id} completed successfully")
        
        except Exception as e:
            logger.error(f"Workflow execution {execution_id} failed: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.now()
            execution.error_message = str(e)
        
        return execution
    
    # Action Handlers
    async def _handle_http_request(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTTP request action"""
        import aiohttp
        
        config = action.config
        method = config.get("method", "GET")
        url = config.get("url")
        headers = config.get("headers", {})
        body = config.get("body")
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=body) as response:
                return {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "body": await response.text()
                }
    
    async def _handle_run_code(self, action: WorkflowAction, context: Dict[str, Any]) -> Any:
        """Handle run code action"""
        config = action.config
        code = config.get("code")
        language = config.get("language", "python")
        
        # This would integrate with the sandbox service
        return {"output": f"Code executed: {code[:50]}..."}
    
    async def _handle_send_email(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send email action"""
        config = action.config
        to = config.get("to")
        subject = config.get("subject")
        body = config.get("body")
        
        # This would integrate with email service
        logger.info(f"Email sent to {to}: {subject}")
        return {"sent": True, "to": to}
    
    async def _handle_send_notification(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send notification action"""
        config = action.config
        message = config.get("message")
        channel = config.get("channel", "default")
        
        logger.info(f"Notification sent to {channel}: {message}")
        return {"sent": True, "channel": channel}
    
    async def _handle_create_file(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create file action"""
        config = action.config
        filename = config.get("filename")
        content = config.get("content")
        
        # This would integrate with file service
        logger.info(f"File created: {filename}")
        return {"created": True, "filename": filename}
    
    async def _handle_transform_data(self, action: WorkflowAction, context: Dict[str, Any]) -> Any:
        """Handle transform data action"""
        config = action.config
        source = config.get("source")
        transformation = config.get("transformation")
        
        # Get source data from context
        data = context.get(source, {})
        
        # Apply transformation (simplified)
        if transformation == "to_json":
            return json.dumps(data)
        elif transformation == "to_uppercase":
            return str(data).upper()
        
        return data
    
    async def _handle_conditional(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conditional action"""
        config = action.config
        condition = WorkflowCondition(
            field=config.get("field"),
            operator=ConditionOperator(config.get("operator")),
            value=config.get("value")
        )
        
        result = condition.evaluate(context)
        
        return {"condition_met": result}
    
    async def _handle_loop(self, action: WorkflowAction, context: Dict[str, Any]) -> List[Any]:
        """Handle loop action"""
        config = action.config
        items = config.get("items", [])
        
        results = []
        for item in items:
            # Process each item
            results.append({"processed": item})
        
        return results
    
    async def _handle_delay(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delay action"""
        config = action.config
        seconds = config.get("seconds", 1)
        
        await asyncio.sleep(seconds)
        
        return {"delayed": seconds}
    
    async def _handle_ai_task(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI task action"""
        config = action.config
        task_type = config.get("task_type")
        input_data = config.get("input")
        
        # This would integrate with AI services
        logger.info(f"AI task executed: {task_type}")
        return {"result": f"AI task {task_type} completed"}
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    async def list_workflows(
        self,
        created_by: Optional[str] = None,
        status: Optional[WorkflowStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[Workflow]:
        """List workflows with optional filtering"""
        workflows = list(self.workflows.values())
        
        if created_by:
            workflows = [w for w in workflows if w.created_by == created_by]
        
        if status:
            workflows = [w for w in workflows if w.status == status]
        
        if tags:
            workflows = [w for w in workflows if any(tag in w.tags for tag in tags)]
        
        return workflows
    
    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution by ID"""
        return self.executions.get(execution_id)
    
    async def list_executions(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[WorkflowStatus] = None
    ) -> List[WorkflowExecution]:
        """List workflow executions with optional filtering"""
        executions = list(self.executions.values())
        
        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        return executions
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            logger.info(f"Workflow {workflow_id} deleted")
            return True
        return False


# Global workflow engine instance
_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine() -> WorkflowEngine:
    """Get or create global workflow engine instance"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine