"""
Workflow Engine Integration
Provides workflow creation, execution, and management capabilities
"""

from typing import Dict, Any, List, Optional, Callable
import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Workflow node types"""

    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    DELAY = "delay"
    ERROR_HANDLER = "error_handler"
    START = "start"
    END = "end"


class ActionType(Enum):
    """Action types"""

    CODE_EXECUTION = "code_execution"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    DATABASE_QUERY = "database_query"
    NOTIFICATION = "notification"
    AI_TASK = "ai_task"
    CUSTOM = "custom"


class WorkflowStatus(Enum):
    """Workflow execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class WorkflowNode:
    """Represents a node in the workflow"""

    id: str
    type: NodeType
    name: str
    config: Dict[str, Any]
    position: Dict[str, float]  # x, y coordinates
    next_nodes: List[str]  # IDs of next nodes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "config": self.config,
            "position": self.position,
            "next_nodes": self.next_nodes,
        }


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""

    id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    variables: Dict[str, Any]
    version: int
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": [node.to_dict() for node in self.nodes],
            "variables": self.variables,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""

    id: str
    workflow_id: str
    status: WorkflowStatus
    start_time: str
    end_time: Optional[str]
    current_node: Optional[str]
    context: Dict[str, Any]
    logs: List[Dict[str, Any]]
    error: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "current_node": self.current_node,
            "context": self.context,
            "logs": self.logs,
            "error": self.error,
        }


class WorkflowEngine:
    """Main workflow engine for creating and executing workflows"""

    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self.templates: Dict[str, WorkflowDefinition] = {}

        # Initialize built-in templates
        self._initialize_templates()

        # Register default action handlers
        self._register_default_handlers()

    def _initialize_templates(self):
        """Initialize built-in workflow templates"""

        # Template 1: Data Processing Pipeline
        self.templates["data_processing"] = self._create_data_processing_template()

        # Template 2: API Integration
        self.templates["api_integration"] = self._create_api_integration_template()

        # Template 3: File Processing
        self.templates["file_processing"] = self._create_file_processing_template()

        # Template 4: Notification Workflow
        self.templates["notification"] = self._create_notification_template()

        # Template 5: Error Recovery
        self.templates["error_recovery"] = self._create_error_recovery_template()

    def _create_data_processing_template(self) -> WorkflowDefinition:
        """Create data processing workflow template"""
        nodes = [
            WorkflowNode(
                id="start",
                type=NodeType.START,
                name="Start",
                config={},
                position={"x": 100, "y": 100},
                next_nodes=["load_data"],
            ),
            WorkflowNode(
                id="load_data",
                type=NodeType.ACTION,
                name="Load Data",
                config={
                    "action_type": ActionType.FILE_OPERATION.value,
                    "operation": "read",
                    "file_path": "data.csv",
                },
                position={"x": 300, "y": 100},
                next_nodes=["process_data"],
            ),
            WorkflowNode(
                id="process_data",
                type=NodeType.ACTION,
                name="Process Data",
                config={
                    "action_type": ActionType.CODE_EXECUTION.value,
                    "code": "# Process data here",
                },
                position={"x": 500, "y": 100},
                next_nodes=["save_results"],
            ),
            WorkflowNode(
                id="save_results",
                type=NodeType.ACTION,
                name="Save Results",
                config={
                    "action_type": ActionType.FILE_OPERATION.value,
                    "operation": "write",
                    "file_path": "results.csv",
                },
                position={"x": 700, "y": 100},
                next_nodes=["end"],
            ),
            WorkflowNode(
                id="end",
                type=NodeType.END,
                name="End",
                config={},
                position={"x": 900, "y": 100},
                next_nodes=[],
            ),
        ]

        return WorkflowDefinition(
            id="template_data_processing",
            name="Data Processing Pipeline",
            description="Load, process, and save data",
            nodes=nodes,
            variables={},
            version=1,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def _create_api_integration_template(self) -> WorkflowDefinition:
        """Create API integration workflow template"""
        nodes = [
            WorkflowNode(
                id="start",
                type=NodeType.START,
                name="Start",
                config={},
                position={"x": 100, "y": 100},
                next_nodes=["api_call"],
            ),
            WorkflowNode(
                id="api_call",
                type=NodeType.ACTION,
                name="API Call",
                config={
                    "action_type": ActionType.API_CALL.value,
                    "method": "GET",
                    "url": "https://api.example.com/data",
                },
                position={"x": 300, "y": 100},
                next_nodes=["check_response"],
            ),
            WorkflowNode(
                id="check_response",
                type=NodeType.CONDITION,
                name="Check Response",
                config={"condition": "response.status == 200"},
                position={"x": 500, "y": 100},
                next_nodes=["process_success", "handle_error"],
            ),
            WorkflowNode(
                id="process_success",
                type=NodeType.ACTION,
                name="Process Success",
                config={
                    "action_type": ActionType.CODE_EXECUTION.value,
                    "code": "# Process successful response",
                },
                position={"x": 700, "y": 50},
                next_nodes=["end"],
            ),
            WorkflowNode(
                id="handle_error",
                type=NodeType.ACTION,
                name="Handle Error",
                config={
                    "action_type": ActionType.NOTIFICATION.value,
                    "message": "API call failed",
                },
                position={"x": 700, "y": 150},
                next_nodes=["end"],
            ),
            WorkflowNode(
                id="end",
                type=NodeType.END,
                name="End",
                config={},
                position={"x": 900, "y": 100},
                next_nodes=[],
            ),
        ]

        return WorkflowDefinition(
            id="template_api_integration",
            name="API Integration",
            description="Call API and handle response",
            nodes=nodes,
            variables={},
            version=1,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def _create_file_processing_template(self) -> WorkflowDefinition:
        """Create file processing workflow template"""
        nodes = [
            WorkflowNode(
                id="start",
                type=NodeType.START,
                name="Start",
                config={},
                position={"x": 100, "y": 100},
                next_nodes=["list_files"],
            ),
            WorkflowNode(
                id="list_files",
                type=NodeType.ACTION,
                name="List Files",
                config={
                    "action_type": ActionType.FILE_OPERATION.value,
                    "operation": "list",
                    "directory": ".",
                },
                position={"x": 300, "y": 100},
                next_nodes=["process_loop"],
            ),
            WorkflowNode(
                id="process_loop",
                type=NodeType.LOOP,
                name="Process Each File",
                config={"iterator": "files", "variable": "file"},
                position={"x": 500, "y": 100},
                next_nodes=["process_file"],
            ),
            WorkflowNode(
                id="process_file",
                type=NodeType.ACTION,
                name="Process File",
                config={
                    "action_type": ActionType.CODE_EXECUTION.value,
                    "code": "# Process file",
                },
                position={"x": 700, "y": 100},
                next_nodes=["end"],
            ),
            WorkflowNode(
                id="end",
                type=NodeType.END,
                name="End",
                config={},
                position={"x": 900, "y": 100},
                next_nodes=[],
            ),
        ]

        return WorkflowDefinition(
            id="template_file_processing",
            name="File Processing",
            description="Process multiple files in a directory",
            nodes=nodes,
            variables={},
            version=1,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def _create_notification_template(self) -> WorkflowDefinition:
        """Create notification workflow template"""
        nodes = [
            WorkflowNode(
                id="start",
                type=NodeType.START,
                name="Start",
                config={},
                position={"x": 100, "y": 100},
                next_nodes=["check_condition"],
            ),
            WorkflowNode(
                id="check_condition",
                type=NodeType.CONDITION,
                name="Check Condition",
                config={"condition": "value > threshold"},
                position={"x": 300, "y": 100},
                next_nodes=["send_notification", "end"],
            ),
            WorkflowNode(
                id="send_notification",
                type=NodeType.ACTION,
                name="Send Notification",
                config={
                    "action_type": ActionType.NOTIFICATION.value,
                    "channel": "email",
                    "message": "Alert: Threshold exceeded",
                },
                position={"x": 500, "y": 100},
                next_nodes=["end"],
            ),
            WorkflowNode(
                id="end",
                type=NodeType.END,
                name="End",
                config={},
                position={"x": 700, "y": 100},
                next_nodes=[],
            ),
        ]

        return WorkflowDefinition(
            id="template_notification",
            name="Conditional Notification",
            description="Send notification based on condition",
            nodes=nodes,
            variables={},
            version=1,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def _create_error_recovery_template(self) -> WorkflowDefinition:
        """Create error recovery workflow template"""
        nodes = [
            WorkflowNode(
                id="start",
                type=NodeType.START,
                name="Start",
                config={},
                position={"x": 100, "y": 100},
                next_nodes=["try_action"],
            ),
            WorkflowNode(
                id="try_action",
                type=NodeType.ERROR_HANDLER,
                name="Try Action",
                config={"max_retries": 3, "retry_delay": 5},
                position={"x": 300, "y": 100},
                next_nodes=["main_action", "error_action"],
            ),
            WorkflowNode(
                id="main_action",
                type=NodeType.ACTION,
                name="Main Action",
                config={
                    "action_type": ActionType.CODE_EXECUTION.value,
                    "code": "# Main action code",
                },
                position={"x": 500, "y": 50},
                next_nodes=["end"],
            ),
            WorkflowNode(
                id="error_action",
                type=NodeType.ACTION,
                name="Error Handler",
                config={
                    "action_type": ActionType.NOTIFICATION.value,
                    "message": "Action failed after retries",
                },
                position={"x": 500, "y": 150},
                next_nodes=["end"],
            ),
            WorkflowNode(
                id="end",
                type=NodeType.END,
                name="End",
                config={},
                position={"x": 700, "y": 100},
                next_nodes=[],
            ),
        ]

        return WorkflowDefinition(
            id="template_error_recovery",
            name="Error Recovery",
            description="Handle errors with retry logic",
            nodes=nodes,
            variables={},
            version=1,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def _register_default_handlers(self):
        """Register default action handlers"""
        self.action_handlers[ActionType.CODE_EXECUTION.value] = (
            self._handle_code_execution
        )
        self.action_handlers[ActionType.API_CALL.value] = self._handle_api_call
        self.action_handlers[ActionType.FILE_OPERATION.value] = (
            self._handle_file_operation
        )
        self.action_handlers[ActionType.NOTIFICATION.value] = self._handle_notification

    async def _handle_code_execution(
        self, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        """Handle code execution action"""
        code = config.get("code", "")
        # In production, execute in sandboxed environment
        exec_globals = {"context": context}
        exec(code, exec_globals)
        return exec_globals.get("result")

    async def _handle_api_call(
        self, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        """Handle API call action"""
        # Placeholder for API call
        return {"status": 200, "data": {}}

    async def _handle_file_operation(
        self, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        """Handle file operation action"""
        operation = config.get("operation")
        file_path = config.get("file_path")

        if operation == "read":
            # Read file
            return {"content": "file content"}
        elif operation == "write":
            # Write file
            return {"success": True}
        elif operation == "list":
            # List files
            return {"files": []}

        return None

    async def _handle_notification(
        self, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        """Handle notification action"""
        message = config.get("message", "")
        channel = config.get("channel", "default")
        logger.info(f"Notification [{channel}]: {message}")
        return {"sent": True}

    async def create_workflow(
        self,
        name: str,
        description: str,
        nodes: List[Dict[str, Any]],
        variables: Optional[Dict[str, Any]] = None,
    ) -> WorkflowDefinition:
        """
        Create a new workflow

        Args:
            name: Workflow name
            description: Workflow description
            nodes: List of workflow nodes
            variables: Initial variables

        Returns:
            Created workflow definition
        """
        workflow_id = str(uuid.uuid4())

        # Convert node dicts to WorkflowNode objects
        workflow_nodes = []
        for node_data in nodes:
            node = WorkflowNode(
                id=node_data.get("id", str(uuid.uuid4())),
                type=NodeType(node_data["type"]),
                name=node_data["name"],
                config=node_data.get("config", {}),
                position=node_data.get("position", {"x": 0, "y": 0}),
                next_nodes=node_data.get("next_nodes", []),
            )
            workflow_nodes.append(node)

        workflow = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            nodes=workflow_nodes,
            variables=variables or {},
            version=1,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        self.workflows[workflow_id] = workflow

        logger.info(f"Created workflow: {workflow_id}")

        return workflow

    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)

    async def list_workflows(self) -> List[WorkflowDefinition]:
        """List all workflows"""
        return list(self.workflows.values())

    async def update_workflow(
        self,
        workflow_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        nodes: Optional[List[Dict[str, Any]]] = None,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Optional[WorkflowDefinition]:
        """Update an existing workflow"""
        workflow = self.workflows.get(workflow_id)

        if not workflow:
            return None

        if name:
            workflow.name = name
        if description:
            workflow.description = description
        if nodes:
            workflow.nodes = [
                WorkflowNode(
                    id=n.get("id", str(uuid.uuid4())),
                    type=NodeType(n["type"]),
                    name=n["name"],
                    config=n.get("config", {}),
                    position=n.get("position", {"x": 0, "y": 0}),
                    next_nodes=n.get("next_nodes", []),
                )
                for n in nodes
            ]
        if variables is not None:
            workflow.variables = variables

        workflow.version += 1
        workflow.updated_at = datetime.now().isoformat()

        logger.info(f"Updated workflow: {workflow_id}")

        return workflow

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            logger.info(f"Deleted workflow: {workflow_id}")
            return True
        return False

    async def execute_workflow(
        self, workflow_id: str, input_context: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """
        Execute a workflow

        Args:
            workflow_id: Workflow ID to execute
            input_context: Initial context/variables

        Returns:
            Workflow execution instance
        """
        workflow = self.workflows.get(workflow_id)

        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        execution_id = str(uuid.uuid4())

        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now().isoformat(),
            end_time=None,
            current_node=None,
            context=input_context or {},
            logs=[],
            error=None,
        )

        self.executions[execution_id] = execution

        try:
            # Find start node
            start_node = next(
                (n for n in workflow.nodes if n.type == NodeType.START), None
            )

            if not start_node:
                raise ValueError("No start node found in workflow")

            # Execute workflow
            await self._execute_node(workflow, start_node, execution)

            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.now().isoformat()

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.end_time = datetime.now().isoformat()
            logger.error(f"Workflow execution failed: {str(e)}")

        return execution

    async def _execute_node(
        self,
        workflow: WorkflowDefinition,
        node: WorkflowNode,
        execution: WorkflowExecution,
    ):
        """Execute a single workflow node"""
        execution.current_node = node.id

        # Log node execution
        execution.logs.append(
            {
                "timestamp": datetime.now().isoformat(),
                "node_id": node.id,
                "node_name": node.name,
                "status": "started",
            }
        )

        try:
            if node.type == NodeType.START:
                # Start node - just continue to next
                pass

            elif node.type == NodeType.END:
                # End node - workflow complete
                return

            elif node.type == NodeType.ACTION:
                # Execute action
                action_type = node.config.get("action_type")
                handler = self.action_handlers.get(action_type)

                if handler:
                    result = await handler(node.config, execution.context)
                    execution.context[f"{node.id}_result"] = result

            elif node.type == NodeType.CONDITION:
                # Evaluate condition
                condition = node.config.get("condition", "True")
                result = eval(condition, {"context": execution.context})
                execution.context[f"{node.id}_result"] = result

            elif node.type == NodeType.DELAY:
                # Delay execution
                delay = node.config.get("delay", 1)
                await asyncio.sleep(delay)

            # Log success
            execution.logs.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "node_id": node.id,
                    "node_name": node.name,
                    "status": "completed",
                }
            )

            # Execute next nodes
            for next_node_id in node.next_nodes:
                next_node = next(
                    (n for n in workflow.nodes if n.id == next_node_id), None
                )
                if next_node:
                    await self._execute_node(workflow, next_node, execution)

        except Exception as e:
            execution.logs.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "node_id": node.id,
                    "node_name": node.name,
                    "status": "failed",
                    "error": str(e),
                }
            )
            raise

    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution by ID"""
        return self.executions.get(execution_id)

    async def get_execution_history(
        self, workflow_id: str, limit: int = 50
    ) -> List[WorkflowExecution]:
        """Get execution history for a workflow"""
        executions = [
            e for e in self.executions.values() if e.workflow_id == workflow_id
        ]

        # Sort by start time (most recent first)
        executions.sort(key=lambda x: x.start_time, reverse=True)

        return executions[:limit]

    async def get_templates(self) -> List[WorkflowDefinition]:
        """Get all workflow templates"""
        return list(self.templates.values())

    async def create_from_template(
        self, template_id: str, name: str, variables: Optional[Dict[str, Any]] = None
    ) -> Optional[WorkflowDefinition]:
        """Create a workflow from a template"""
        template = self.templates.get(template_id)

        if not template:
            return None

        # Create new workflow from template
        workflow = await self.create_workflow(
            name=name,
            description=template.description,
            nodes=[node.to_dict() for node in template.nodes],
            variables=variables or template.variables,
        )

        return workflow

    def register_action_handler(self, action_type: str, handler: Callable):
        """Register a custom action handler"""
        self.action_handlers[action_type] = handler
        logger.info(f"Registered action handler: {action_type}")
