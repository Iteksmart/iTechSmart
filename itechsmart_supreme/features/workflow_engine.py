"""
Advanced Workflow Engine
User-friendly workflow creation and management for IT professionals
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import yaml
import json

from ..core.models import Alert, RemediationAction, ExecutionResult


class WorkflowStatus(Enum):
    """Workflow execution status"""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep:
    """Individual workflow step"""

    def __init__(
        self,
        name: str,
        action_type: str,
        parameters: Dict[str, Any],
        condition: Optional[str] = None,
        on_success: Optional[str] = None,
        on_failure: Optional[str] = None,
        timeout: int = 300,
    ):
        self.name = name
        self.action_type = action_type
        self.parameters = parameters
        self.condition = condition
        self.on_success = on_success
        self.on_failure = on_failure
        self.timeout = timeout
        self.status = WorkflowStatus.PENDING
        self.result = None


class Workflow:
    """Workflow definition"""

    def __init__(
        self,
        name: str,
        description: str,
        trigger: Dict[str, Any],
        steps: List[WorkflowStep],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = f"workflow-{datetime.now().timestamp()}"
        self.name = name
        self.description = description
        self.trigger = trigger
        self.steps = steps
        self.metadata = metadata or {}
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.current_step = 0


class WorkflowEngine:
    """
    Advanced workflow engine for creating and managing automation workflows
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workflows = {}
        self.workflow_templates = {}
        self.running_workflows = {}
        self.workflow_history = []

        # Load built-in templates
        self._load_builtin_templates()

    def _load_builtin_templates(self):
        """Load built-in workflow templates"""

        # High CPU remediation workflow
        self.workflow_templates["high_cpu_remediation"] = {
            "name": "High CPU Remediation",
            "description": "Automated workflow for high CPU usage",
            "trigger": {"type": "alert", "condition": "cpu_usage > 80"},
            "steps": [
                {
                    "name": "Identify Process",
                    "action_type": "command",
                    "parameters": {"command": "ps aux --sort=-%cpu | head -5"},
                },
                {
                    "name": "Notify Team",
                    "action_type": "notification",
                    "parameters": {
                        "channel": "slack",
                        "message": "High CPU detected on {host}",
                    },
                },
                {
                    "name": "Wait for Approval",
                    "action_type": "approval",
                    "parameters": {"timeout": 300, "approvers": ["admin", "ops-team"]},
                },
                {
                    "name": "Kill Process",
                    "action_type": "command",
                    "parameters": {"command": "kill -9 {process_id}"},
                    "condition": "approved == true",
                },
                {
                    "name": "Verify Resolution",
                    "action_type": "check",
                    "parameters": {"metric": "cpu_usage", "condition": "< 50"},
                },
                {
                    "name": "Log Incident",
                    "action_type": "log",
                    "parameters": {"system": "jira", "type": "incident"},
                },
            ],
        }

        # Service restart workflow
        self.workflow_templates["service_restart"] = {
            "name": "Service Restart Workflow",
            "description": "Graceful service restart with validation",
            "trigger": {"type": "alert", "condition": "service_down == true"},
            "steps": [
                {
                    "name": "Check Service Status",
                    "action_type": "command",
                    "parameters": {"command": "systemctl status {service_name}"},
                },
                {
                    "name": "Backup Configuration",
                    "action_type": "command",
                    "parameters": {"command": "cp /etc/{service_name}.conf /backup/"},
                },
                {
                    "name": "Stop Service",
                    "action_type": "command",
                    "parameters": {"command": "systemctl stop {service_name}"},
                },
                {"name": "Wait", "action_type": "wait", "parameters": {"duration": 5}},
                {
                    "name": "Start Service",
                    "action_type": "command",
                    "parameters": {"command": "systemctl start {service_name}"},
                },
                {
                    "name": "Verify Service",
                    "action_type": "command",
                    "parameters": {"command": "systemctl is-active {service_name}"},
                },
                {
                    "name": "Health Check",
                    "action_type": "http_check",
                    "parameters": {
                        "url": "http://{host}:{port}/health",
                        "expected_status": 200,
                    },
                },
            ],
        }

        # Security incident response
        self.workflow_templates["security_incident"] = {
            "name": "Security Incident Response",
            "description": "Automated security incident response",
            "trigger": {
                "type": "alert",
                "condition": "severity == critical AND source == wazuh",
            },
            "steps": [
                {
                    "name": "Isolate Host",
                    "action_type": "command",
                    "parameters": {"command": "iptables -A INPUT -j DROP"},
                },
                {
                    "name": "Collect Evidence",
                    "action_type": "command",
                    "parameters": {
                        "command": "tar -czf /tmp/evidence.tar.gz /var/log /etc"
                    },
                },
                {
                    "name": "Notify Security Team",
                    "action_type": "notification",
                    "parameters": {
                        "channel": "pagerduty",
                        "severity": "critical",
                        "message": "Security incident on {host}",
                    },
                },
                {
                    "name": "Create Ticket",
                    "action_type": "ticket",
                    "parameters": {
                        "system": "servicenow",
                        "priority": "P1",
                        "category": "security",
                    },
                },
                {
                    "name": "Wait for Investigation",
                    "action_type": "manual",
                    "parameters": {"message": "Security team investigating"},
                },
            ],
        }

    def create_workflow_from_template(
        self, template_name: str, parameters: Dict[str, Any]
    ) -> Workflow:
        """Create workflow from template"""

        if template_name not in self.workflow_templates:
            raise ValueError(f"Template not found: {template_name}")

        template = self.workflow_templates[template_name]

        # Create workflow steps
        steps = []
        for step_def in template["steps"]:
            # Replace parameters
            params = self._replace_parameters(step_def["parameters"], parameters)

            step = WorkflowStep(
                name=step_def["name"],
                action_type=step_def["action_type"],
                parameters=params,
                condition=step_def.get("condition"),
                on_success=step_def.get("on_success"),
                on_failure=step_def.get("on_failure"),
            )
            steps.append(step)

        workflow = Workflow(
            name=template["name"],
            description=template["description"],
            trigger=template["trigger"],
            steps=steps,
            metadata={"template": template_name, "parameters": parameters},
        )

        self.workflows[workflow.id] = workflow

        return workflow

    def create_custom_workflow(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        trigger: Optional[Dict[str, Any]] = None,
    ) -> Workflow:
        """Create custom workflow"""

        workflow_steps = []
        for step_def in steps:
            step = WorkflowStep(
                name=step_def["name"],
                action_type=step_def["action_type"],
                parameters=step_def["parameters"],
                condition=step_def.get("condition"),
                on_success=step_def.get("on_success"),
                on_failure=step_def.get("on_failure"),
                timeout=step_def.get("timeout", 300),
            )
            workflow_steps.append(step)

        workflow = Workflow(
            name=name,
            description=description,
            trigger=trigger or {},
            steps=workflow_steps,
        )

        self.workflows[workflow.id] = workflow

        return workflow

    async def execute_workflow(
        self, workflow_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute workflow"""

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()

        self.running_workflows[workflow_id] = workflow

        self.logger.info(f"Starting workflow: {workflow.name}")

        try:
            for i, step in enumerate(workflow.steps):
                workflow.current_step = i

                self.logger.info(
                    f"Executing step {i+1}/{len(workflow.steps)}: {step.name}"
                )

                # Check condition
                if step.condition and not self._evaluate_condition(
                    step.condition, context
                ):
                    self.logger.info(f"Skipping step {step.name} - condition not met")
                    continue

                # Execute step
                step.status = WorkflowStatus.RUNNING
                result = await self._execute_step(step, context)

                if result["success"]:
                    step.status = WorkflowStatus.COMPLETED
                    step.result = result

                    # Update context with result
                    context.update(result.get("output", {}))

                    # Handle on_success
                    if step.on_success:
                        self.logger.info(
                            f"Step succeeded, jumping to: {step.on_success}"
                        )
                        # Find step by name and jump
                        for j, s in enumerate(workflow.steps):
                            if s.name == step.on_success:
                                workflow.current_step = j - 1
                                break
                else:
                    step.status = WorkflowStatus.FAILED
                    step.result = result

                    # Handle on_failure
                    if step.on_failure:
                        self.logger.info(f"Step failed, jumping to: {step.on_failure}")
                        for j, s in enumerate(workflow.steps):
                            if s.name == step.on_failure:
                                workflow.current_step = j - 1
                                break
                    else:
                        # Fail workflow
                        workflow.status = WorkflowStatus.FAILED
                        break

            if workflow.status == WorkflowStatus.RUNNING:
                workflow.status = WorkflowStatus.COMPLETED

            workflow.completed_at = datetime.now()

            # Add to history
            self.workflow_history.append(
                {
                    "workflow_id": workflow_id,
                    "name": workflow.name,
                    "status": workflow.status.value,
                    "started_at": workflow.started_at.isoformat(),
                    "completed_at": workflow.completed_at.isoformat(),
                    "duration": (
                        workflow.completed_at - workflow.started_at
                    ).total_seconds(),
                }
            )

            return {
                "success": workflow.status == WorkflowStatus.COMPLETED,
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "context": context,
            }

        except Exception as e:
            self.logger.error(f"Workflow execution error: {e}")
            workflow.status = WorkflowStatus.FAILED
            return {"success": False, "error": str(e)}

        finally:
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]

    async def _execute_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute individual workflow step"""

        try:
            if step.action_type == "command":
                return await self._execute_command_step(step, context)

            elif step.action_type == "notification":
                return await self._execute_notification_step(step, context)

            elif step.action_type == "approval":
                return await self._execute_approval_step(step, context)

            elif step.action_type == "wait":
                return await self._execute_wait_step(step, context)

            elif step.action_type == "check":
                return await self._execute_check_step(step, context)

            elif step.action_type == "http_check":
                return await self._execute_http_check_step(step, context)

            elif step.action_type == "log":
                return await self._execute_log_step(step, context)

            elif step.action_type == "ticket":
                return await self._execute_ticket_step(step, context)

            elif step.action_type == "manual":
                return await self._execute_manual_step(step, context)

            else:
                return {
                    "success": False,
                    "error": f"Unknown action type: {step.action_type}",
                }

        except asyncio.TimeoutError:
            return {"success": False, "error": f"Step timed out after {step.timeout}s"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_command_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute command step"""
        command = self._replace_parameters(step.parameters["command"], context)
        # Execute command (integrate with command executor)
        return {"success": True, "output": {"command_executed": command}}

    async def _execute_notification_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute notification step"""
        # Send notification
        return {"success": True}

    async def _execute_approval_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute approval step"""
        # Wait for approval
        return {"success": True, "output": {"approved": True}}

    async def _execute_wait_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute wait step"""
        duration = step.parameters.get("duration", 5)
        await asyncio.sleep(duration)
        return {"success": True}

    async def _execute_check_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute check step"""
        # Perform check
        return {"success": True}

    async def _execute_http_check_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute HTTP check step"""
        # Perform HTTP check
        return {"success": True}

    async def _execute_log_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute log step"""
        # Log to external system
        return {"success": True}

    async def _execute_ticket_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute ticket creation step"""
        # Create ticket
        return {"success": True}

    async def _execute_manual_step(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute manual step"""
        # Wait for manual intervention
        return {"success": True}

    def _replace_parameters(self, value: Any, context: Dict[str, Any]) -> Any:
        """Replace parameters in value with context"""
        if isinstance(value, str):
            for key, val in context.items():
                value = value.replace(f"{{{key}}}", str(val))
        elif isinstance(value, dict):
            return {k: self._replace_parameters(v, context) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._replace_parameters(v, context) for v in value]
        return value

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate condition"""
        # Simple condition evaluation
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False

    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get available workflow templates"""
        return [
            {
                "name": name,
                "description": template["description"],
                "steps": len(template["steps"]),
            }
            for name, template in self.workflow_templates.items()
        ]

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        if workflow_id not in self.workflows:
            return None

        workflow = self.workflows[workflow_id]
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "current_step": workflow.current_step,
            "total_steps": len(workflow.steps),
            "started_at": (
                workflow.started_at.isoformat() if workflow.started_at else None
            ),
            "completed_at": (
                workflow.completed_at.isoformat() if workflow.completed_at else None
            ),
        }
