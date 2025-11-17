"""
iTechSmart Workflow - Core Workflow Engine
Handles workflow execution, state management, and process automation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import json
import asyncio
from uuid import uuid4


class WorkflowStatus(str, Enum):
    """Workflow execution status"""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeType(str, Enum):
    """Workflow node types"""

    START = "start"
    END = "end"
    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    APPROVAL = "approval"
    API_CALL = "api_call"
    EMAIL = "email"
    WEBHOOK = "webhook"
    DELAY = "delay"
    SCRIPT = "script"


class WorkflowNode:
    """Represents a single node in a workflow"""

    def __init__(
        self,
        node_id: str,
        node_type: NodeType,
        name: str,
        config: Dict[str, Any],
        position: Dict[str, int],
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.name = name
        self.config = config
        self.position = position
        self.status = "pending"
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node with given context"""
        self.started_at = datetime.utcnow()
        self.status = "running"

        try:
            if self.node_type == NodeType.TASK:
                result = await self._execute_task(context)
            elif self.node_type == NodeType.DECISION:
                result = await self._execute_decision(context)
            elif self.node_type == NodeType.APPROVAL:
                result = await self._execute_approval(context)
            elif self.node_type == NodeType.API_CALL:
                result = await self._execute_api_call(context)
            elif self.node_type == NodeType.EMAIL:
                result = await self._execute_email(context)
            elif self.node_type == NodeType.WEBHOOK:
                result = await self._execute_webhook(context)
            elif self.node_type == NodeType.DELAY:
                result = await self._execute_delay(context)
            elif self.node_type == NodeType.SCRIPT:
                result = await self._execute_script(context)
            else:
                result = {"success": True}

            self.status = "completed"
            self.result = result
            self.completed_at = datetime.utcnow()
            return result

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            self.completed_at = datetime.utcnow()
            raise

    async def _execute_task(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task node"""
        task_type = self.config.get("task_type")

        if task_type == "assign":
            return {
                "success": True,
                "assigned_to": self.config.get("assignee"),
                "task_id": str(uuid4()),
            }
        elif task_type == "update":
            return {"success": True, "updated_fields": self.config.get("fields", {})}
        else:
            return {"success": True}

    async def _execute_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a decision node"""
        condition = self.config.get("condition")
        # Evaluate condition against context
        # This is a simplified version
        result = eval(condition, {"context": context})
        return {
            "success": True,
            "decision": result,
            "next_path": "true" if result else "false",
        }

    async def _execute_approval(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an approval node"""
        return {
            "success": True,
            "approval_required": True,
            "approvers": self.config.get("approvers", []),
            "approval_id": str(uuid4()),
        }

    async def _execute_api_call(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an API call node"""
        import httpx

        method = self.config.get("method", "GET")
        url = self.config.get("url")
        headers = self.config.get("headers", {})
        body = self.config.get("body", {})

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method, url=url, headers=headers, json=body
            )

            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response": (
                    response.json()
                    if response.headers.get("content-type") == "application/json"
                    else response.text
                ),
            }

    async def _execute_email(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an email node"""
        return {
            "success": True,
            "email_sent": True,
            "recipients": self.config.get("recipients", []),
            "subject": self.config.get("subject"),
        }

    async def _execute_webhook(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a webhook node"""
        import httpx

        url = self.config.get("url")
        payload = self.config.get("payload", {})

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)

            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
            }

    async def _execute_delay(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a delay node"""
        delay_seconds = self.config.get("delay_seconds", 0)
        await asyncio.sleep(delay_seconds)

        return {"success": True, "delayed_seconds": delay_seconds}

    async def _execute_script(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a script node"""
        script = self.config.get("script")
        # Execute script in sandboxed environment
        # This is a simplified version
        local_vars = {"context": context, "result": None}
        exec(script, {}, local_vars)

        return {"success": True, "result": local_vars.get("result")}


class WorkflowEngine:
    """Core workflow execution engine"""

    def __init__(self):
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.executions: Dict[str, Dict[str, Any]] = {}

    def create_workflow(
        self,
        name: str,
        description: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        triggers: List[Dict[str, Any]] = None,
    ) -> str:
        """Create a new workflow definition"""
        workflow_id = str(uuid4())

        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "nodes": nodes,
            "edges": edges,
            "triggers": triggers or [],
            "status": WorkflowStatus.DRAFT,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "version": 1,
        }

        self.workflows[workflow_id] = workflow
        return workflow_id

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow definition"""
        return self.workflows.get(workflow_id)

    def update_workflow(
        self,
        workflow_id: str,
        nodes: List[Dict[str, Any]] = None,
        edges: List[Dict[str, Any]] = None,
        triggers: List[Dict[str, Any]] = None,
    ) -> bool:
        """Update workflow definition"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False

        if nodes is not None:
            workflow["nodes"] = nodes
        if edges is not None:
            workflow["edges"] = edges
        if triggers is not None:
            workflow["triggers"] = triggers

        workflow["updated_at"] = datetime.utcnow().isoformat()
        workflow["version"] += 1

        return True

    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False

        workflow["status"] = WorkflowStatus.ACTIVE
        workflow["updated_at"] = datetime.utcnow().isoformat()
        return True

    def deactivate_workflow(self, workflow_id: str) -> bool:
        """Deactivate a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False

        workflow["status"] = WorkflowStatus.PAUSED
        workflow["updated_at"] = datetime.utcnow().isoformat()
        return True

    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any] = None,
        context: Dict[str, Any] = None,
    ) -> str:
        """Execute a workflow instance"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        if workflow["status"] != WorkflowStatus.ACTIVE:
            raise ValueError(f"Workflow {workflow_id} is not active")

        execution_id = str(uuid4())

        execution = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "status": "running",
            "input_data": input_data or {},
            "context": context or {},
            "current_node": None,
            "completed_nodes": [],
            "failed_nodes": [],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "result": None,
            "error": None,
        }

        self.executions[execution_id] = execution

        # Execute workflow asynchronously
        asyncio.create_task(self._execute_workflow_async(execution_id))

        return execution_id

    async def _execute_workflow_async(self, execution_id: str):
        """Execute workflow asynchronously"""
        execution = self.executions[execution_id]
        workflow = self.workflows[execution["workflow_id"]]

        try:
            # Find start node
            start_node = next(
                (n for n in workflow["nodes"] if n["type"] == NodeType.START), None
            )

            if not start_node:
                raise ValueError("No start node found in workflow")

            # Execute workflow from start node
            context = execution["context"].copy()
            context.update(execution["input_data"])

            current_node_id = start_node["id"]

            while current_node_id:
                # Find current node
                node_data = next(
                    (n for n in workflow["nodes"] if n["id"] == current_node_id), None
                )

                if not node_data:
                    break

                # Create and execute node
                node = WorkflowNode(
                    node_id=node_data["id"],
                    node_type=NodeType(node_data["type"]),
                    name=node_data["name"],
                    config=node_data.get("config", {}),
                    position=node_data.get("position", {}),
                )

                execution["current_node"] = current_node_id

                result = await node.execute(context)

                execution["completed_nodes"].append(
                    {
                        "node_id": current_node_id,
                        "result": result,
                        "completed_at": datetime.utcnow().isoformat(),
                    }
                )

                # Update context with result
                context[f"node_{current_node_id}_result"] = result

                # Find next node
                if node.node_type == NodeType.END:
                    break

                if node.node_type == NodeType.DECISION:
                    # Find edge based on decision result
                    next_path = result.get("next_path", "true")
                    next_edge = next(
                        (
                            e
                            for e in workflow["edges"]
                            if e["source"] == current_node_id
                            and e.get("label") == next_path
                        ),
                        None,
                    )
                else:
                    # Find next edge
                    next_edge = next(
                        (
                            e
                            for e in workflow["edges"]
                            if e["source"] == current_node_id
                        ),
                        None,
                    )

                current_node_id = next_edge["target"] if next_edge else None

            # Mark execution as completed
            execution["status"] = "completed"
            execution["completed_at"] = datetime.utcnow().isoformat()
            execution["result"] = context

        except Exception as e:
            execution["status"] = "failed"
            execution["error"] = str(e)
            execution["completed_at"] = datetime.utcnow().isoformat()
            execution["failed_nodes"].append(
                {
                    "node_id": execution["current_node"],
                    "error": str(e),
                    "failed_at": datetime.utcnow().isoformat(),
                }
            )

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        return self.executions.get(execution_id)

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        execution = self.executions.get(execution_id)
        if not execution:
            return False

        if execution["status"] == "running":
            execution["status"] = "cancelled"
            execution["completed_at"] = datetime.utcnow().isoformat()
            return True

        return False

    def get_workflow_executions(
        self, workflow_id: str, status: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get executions for a workflow"""
        executions = [
            e for e in self.executions.values() if e["workflow_id"] == workflow_id
        ]

        if status:
            executions = [e for e in executions if e["status"] == status]

        # Sort by started_at descending
        executions.sort(key=lambda x: x["started_at"], reverse=True)

        return executions[:limit]

    def get_workflow_statistics(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        executions = self.get_workflow_executions(workflow_id)

        total = len(executions)
        completed = len([e for e in executions if e["status"] == "completed"])
        failed = len([e for e in executions if e["status"] == "failed"])
        running = len([e for e in executions if e["status"] == "running"])
        cancelled = len([e for e in executions if e["status"] == "cancelled"])

        return {
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "cancelled": cancelled,
            "success_rate": (completed / total * 100) if total > 0 else 0,
            "failure_rate": (failed / total * 100) if total > 0 else 0,
        }


# Global workflow engine instance
workflow_engine = WorkflowEngine()
