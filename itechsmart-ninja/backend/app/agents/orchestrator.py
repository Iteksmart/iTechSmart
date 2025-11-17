"""
Multi-Agent Orchestrator - Coordinates all agents to complete complex tasks
"""

from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.coder_agent import CoderAgent
from app.agents.writer_agent import WriterAgent
from app.agents.analyst_agent import AnalystAgent
from app.agents.debugger_agent import DebuggerAgent

logger = logging.getLogger(__name__)


class TaskPlan:
    """Represents a task execution plan"""

    def __init__(self, task_id: str, description: str):
        self.task_id = task_id
        self.description = description
        self.steps: List[Dict[str, Any]] = []
        self.current_step = 0
        self.status = "pending"
        self.results: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def add_step(
        self,
        agent_name: str,
        action: str,
        description: str,
        dependencies: List[int] = None,
    ):
        """Add a step to the plan"""
        step = {
            "step_number": len(self.steps) + 1,
            "agent": agent_name,
            "action": action,
            "description": description,
            "dependencies": dependencies or [],
            "status": "pending",
            "result": None,
            "started_at": None,
            "completed_at": None,
        }
        self.steps.append(step)

    def get_next_step(self) -> Optional[Dict[str, Any]]:
        """Get next executable step"""
        for step in self.steps:
            if step["status"] == "pending":
                # Check if dependencies are met
                if self._dependencies_met(step):
                    return step
        return None

    def _dependencies_met(self, step: Dict[str, Any]) -> bool:
        """Check if step dependencies are met"""
        for dep_num in step["dependencies"]:
            dep_step = self.steps[dep_num - 1]
            if dep_step["status"] != "completed":
                return False
        return True

    def mark_step_started(self, step_number: int):
        """Mark step as started"""
        if 0 < step_number <= len(self.steps):
            self.steps[step_number - 1]["status"] = "running"
            self.steps[step_number - 1]["started_at"] = datetime.utcnow()

    def mark_step_completed(self, step_number: int, result: Any):
        """Mark step as completed"""
        if 0 < step_number <= len(self.steps):
            self.steps[step_number - 1]["status"] = "completed"
            self.steps[step_number - 1]["result"] = result
            self.steps[step_number - 1]["completed_at"] = datetime.utcnow()

    def mark_step_failed(self, step_number: int, error: str):
        """Mark step as failed"""
        if 0 < step_number <= len(self.steps):
            self.steps[step_number - 1]["status"] = "failed"
            self.steps[step_number - 1]["error"] = error
            self.steps[step_number - 1]["completed_at"] = datetime.utcnow()

    def get_progress(self) -> float:
        """Get execution progress (0-100)"""
        if not self.steps:
            return 0.0

        completed = sum(1 for step in self.steps if step["status"] == "completed")
        return (completed / len(self.steps)) * 100

    def is_complete(self) -> bool:
        """Check if all steps are completed"""
        return all(step["status"] == "completed" for step in self.steps)

    def has_failed(self) -> bool:
        """Check if any step has failed"""
        return any(step["status"] == "failed" for step in self.steps)


class MultiAgentOrchestrator:
    """Orchestrates multiple agents to complete complex tasks"""

    def __init__(self, ai_provider: str = "openai"):
        self.ai_provider = ai_provider

        # Initialize all agents
        self.agents: Dict[str, BaseAgent] = {
            "researcher": ResearcherAgent(ai_provider),
            "coder": CoderAgent(ai_provider),
            "writer": WriterAgent(ai_provider),
            "analyst": AnalystAgent(ai_provider),
            "debugger": DebuggerAgent(ai_provider),
        }

        # Task tracking
        self.active_tasks: Dict[str, TaskPlan] = {}
        self.completed_tasks: List[TaskPlan] = []

        logger.info(
            f"MultiAgentOrchestrator initialized with {len(self.agents)} agents"
        )

    async def execute_task(
        self, task: Dict[str, Any], progress_callback=None
    ) -> Dict[str, Any]:
        """Execute a complex task using multiple agents"""
        try:
            task_id = task.get("id", f"task_{datetime.utcnow().timestamp()}")
            description = task.get("description", "")

            logger.info(f"Orchestrator executing task: {task_id}")

            # Create execution plan
            plan = await self.create_plan(task)
            self.active_tasks[task_id] = plan

            # Execute plan
            plan.status = "running"
            plan.started_at = datetime.utcnow()

            result = await self._execute_plan(plan, progress_callback)

            # Mark as completed
            plan.status = "completed" if not plan.has_failed() else "failed"
            plan.completed_at = datetime.utcnow()

            # Move to completed tasks
            self.completed_tasks.append(plan)
            del self.active_tasks[task_id]

            return result

        except Exception as e:
            logger.error(f"Orchestrator execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "orchestrator": "MultiAgentOrchestrator",
            }

    async def create_plan(self, task: Dict[str, Any]) -> TaskPlan:
        """Create execution plan for a task"""
        task_id = task.get("id", f"task_{datetime.utcnow().timestamp()}")
        description = task.get("description", "")
        task_type = task.get("type", "general")

        plan = TaskPlan(task_id, description)

        # Determine which agents are needed based on task type
        if task_type == "research":
            plan = await self._plan_research_task(task, plan)
        elif task_type == "code":
            plan = await self._plan_coding_task(task, plan)
        elif task_type == "website":
            plan = await self._plan_website_task(task, plan)
        elif task_type == "analysis":
            plan = await self._plan_analysis_task(task, plan)
        elif task_type == "debug":
            plan = await self._plan_debug_task(task, plan)
        elif task_type == "documentation":
            plan = await self._plan_documentation_task(task, plan)
        else:
            plan = await self._plan_general_task(task, plan)

        logger.info(f"Created plan with {len(plan.steps)} steps for task {task_id}")
        return plan

    async def _plan_research_task(
        self, task: Dict[str, Any], plan: TaskPlan
    ) -> TaskPlan:
        """Plan a research task"""
        query = task.get("query", task.get("description", ""))

        plan.add_step("researcher", "search", f"Search for information about: {query}")
        plan.add_step(
            "researcher", "analyze", "Analyze and synthesize findings", dependencies=[1]
        )
        plan.add_step("writer", "report", "Generate research report", dependencies=[2])

        return plan

    async def _plan_coding_task(self, task: Dict[str, Any], plan: TaskPlan) -> TaskPlan:
        """Plan a coding task"""
        requirements = task.get("requirements", task.get("description", ""))
        language = task.get("language", "python")

        plan.add_step("researcher", "search", f"Research best practices for {language}")
        plan.add_step(
            "coder", "generate", f"Generate code: {requirements}", dependencies=[1]
        )
        plan.add_step("coder", "review", "Review generated code", dependencies=[2])
        plan.add_step("coder", "test", "Generate tests", dependencies=[3])
        plan.add_step("writer", "document", "Generate documentation", dependencies=[3])

        return plan

    async def _plan_website_task(
        self, task: Dict[str, Any], plan: TaskPlan
    ) -> TaskPlan:
        """Plan a website building task"""
        requirements = task.get("requirements", task.get("description", ""))

        plan.add_step(
            "researcher", "search", "Research design trends and best practices"
        )
        plan.add_step("coder", "generate", "Generate HTML structure", dependencies=[1])
        plan.add_step("coder", "generate", "Generate CSS styling", dependencies=[2])
        plan.add_step(
            "coder", "generate", "Generate JavaScript functionality", dependencies=[3]
        )
        plan.add_step("coder", "review", "Review complete website", dependencies=[4])
        plan.add_step("writer", "document", "Generate README", dependencies=[5])

        return plan

    async def _plan_analysis_task(
        self, task: Dict[str, Any], plan: TaskPlan
    ) -> TaskPlan:
        """Plan a data analysis task"""
        data = task.get("data", {})
        analysis_type = task.get("analysis_type", "descriptive")

        plan.add_step("analyst", "clean", "Clean and prepare data")
        plan.add_step(
            "analyst", "analyze", f"Perform {analysis_type} analysis", dependencies=[1]
        )
        plan.add_step("analyst", "visualize", "Create visualizations", dependencies=[2])
        plan.add_step("writer", "report", "Generate analysis report", dependencies=[3])

        return plan

    async def _plan_debug_task(self, task: Dict[str, Any], plan: TaskPlan) -> TaskPlan:
        """Plan a debugging task"""
        error = task.get("error", {})
        code = task.get("code", "")

        plan.add_step("debugger", "analyze", "Analyze error")
        plan.add_step("debugger", "root_cause", "Identify root cause", dependencies=[1])
        plan.add_step("debugger", "fix", "Generate fix", dependencies=[2])
        plan.add_step("coder", "test", "Test the fix", dependencies=[3])
        plan.add_step("writer", "document", "Document the fix", dependencies=[4])

        return plan

    async def _plan_documentation_task(
        self, task: Dict[str, Any], plan: TaskPlan
    ) -> TaskPlan:
        """Plan a documentation task"""
        doc_type = task.get("doc_type", "readme")

        if task.get("code"):
            plan.add_step("coder", "review", "Review code structure")
            plan.add_step(
                "writer", "document", f"Generate {doc_type}", dependencies=[1]
            )
        else:
            plan.add_step("researcher", "search", "Research topic")
            plan.add_step(
                "writer", "document", f"Generate {doc_type}", dependencies=[1]
            )

        return plan

    async def _plan_general_task(
        self, task: Dict[str, Any], plan: TaskPlan
    ) -> TaskPlan:
        """Plan a general task"""
        description = task.get("description", "")

        # Analyze task to determine required agents
        required_agents = self._analyze_task_requirements(description)

        step_num = 1
        for agent_name, action in required_agents:
            deps = [step_num - 1] if step_num > 1 else []
            plan.add_step(
                agent_name, action, f"{action} for: {description}", dependencies=deps
            )
            step_num += 1

        return plan

    def _analyze_task_requirements(self, description: str) -> List[tuple]:
        """Analyze task to determine required agents"""
        description_lower = description.lower()
        agents = []

        # Check for research needs
        if any(
            word in description_lower
            for word in ["research", "find", "search", "information"]
        ):
            agents.append(("researcher", "search"))

        # Check for coding needs
        if any(
            word in description_lower
            for word in ["code", "program", "develop", "build", "create"]
        ):
            agents.append(("coder", "generate"))

        # Check for analysis needs
        if any(
            word in description_lower
            for word in ["analyze", "data", "statistics", "metrics"]
        ):
            agents.append(("analyst", "analyze"))

        # Check for writing needs
        if any(
            word in description_lower
            for word in ["write", "document", "report", "article"]
        ):
            agents.append(("writer", "document"))

        # Check for debugging needs
        if any(word in description_lower for word in ["debug", "fix", "error", "bug"]):
            agents.append(("debugger", "analyze"))

        # Default to researcher if no specific needs identified
        if not agents:
            agents.append(("researcher", "search"))
            agents.append(("writer", "document"))

        return agents

    async def _execute_plan(
        self, plan: TaskPlan, progress_callback=None
    ) -> Dict[str, Any]:
        """Execute a task plan"""
        results = []

        while not plan.is_complete() and not plan.has_failed():
            # Get next executable step
            next_step = plan.get_next_step()

            if not next_step:
                # No more executable steps (might be waiting for dependencies)
                if not plan.is_complete():
                    logger.error(
                        "No executable steps but plan not complete - deadlock detected"
                    )
                    break
                break

            # Execute step
            step_result = await self._execute_step(next_step, plan)
            results.append(step_result)

            # Update progress
            if progress_callback:
                await progress_callback(
                    {
                        "task_id": plan.task_id,
                        "progress": plan.get_progress(),
                        "current_step": next_step["step_number"],
                        "total_steps": len(plan.steps),
                        "step_result": step_result,
                    }
                )

        # Compile final result
        final_result = {
            "success": plan.is_complete() and not plan.has_failed(),
            "task_id": plan.task_id,
            "description": plan.description,
            "steps_completed": sum(1 for s in plan.steps if s["status"] == "completed"),
            "total_steps": len(plan.steps),
            "results": results,
            "execution_time": (
                (plan.completed_at - plan.started_at).total_seconds()
                if plan.completed_at
                else None
            ),
            "orchestrator": "MultiAgentOrchestrator",
        }

        return final_result

    async def _execute_step(
        self, step: Dict[str, Any], plan: TaskPlan
    ) -> Dict[str, Any]:
        """Execute a single step"""
        step_number = step["step_number"]
        agent_name = step["agent"]
        action = step["action"]

        logger.info(f"Executing step {step_number}: {agent_name}.{action}")

        # Mark step as started
        plan.mark_step_started(step_number)

        try:
            # Get agent
            agent = self.agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent not found: {agent_name}")

            # Prepare task for agent
            agent_task = {
                "type": action,
                "description": step["description"],
                "context": self._gather_context(step, plan),
            }

            # Execute agent task
            result = await agent.execute(agent_task)

            # Mark step as completed
            plan.mark_step_completed(step_number, result)

            return {
                "step": step_number,
                "agent": agent_name,
                "action": action,
                "success": result.get("success", True),
                "result": result,
            }

        except Exception as e:
            logger.error(f"Step {step_number} failed: {str(e)}")
            plan.mark_step_failed(step_number, str(e))

            return {
                "step": step_number,
                "agent": agent_name,
                "action": action,
                "success": False,
                "error": str(e),
            }

    def _gather_context(self, step: Dict[str, Any], plan: TaskPlan) -> Dict[str, Any]:
        """Gather context from previous steps"""
        context = {}

        # Get results from dependency steps
        for dep_num in step["dependencies"]:
            if 0 < dep_num <= len(plan.steps):
                dep_step = plan.steps[dep_num - 1]
                if dep_step["result"]:
                    context[f"step_{dep_num}"] = dep_step["result"]

        return context

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_name: agent.get_status() for agent_name, agent in self.agents.items()
        }

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active tasks"""
        return [
            {
                "task_id": plan.task_id,
                "description": plan.description,
                "progress": plan.get_progress(),
                "status": plan.status,
                "steps": len(plan.steps),
                "started_at": plan.started_at.isoformat() if plan.started_at else None,
            }
            for plan in self.active_tasks.values()
        ]

    def get_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a task"""
        plan = self.active_tasks.get(task_id)

        if not plan:
            # Check completed tasks
            for completed_plan in self.completed_tasks:
                if completed_plan.task_id == task_id:
                    plan = completed_plan
                    break

        if not plan:
            return None

        return {
            "task_id": plan.task_id,
            "description": plan.description,
            "status": plan.status,
            "progress": plan.get_progress(),
            "steps": [
                {
                    "step_number": s["step_number"],
                    "agent": s["agent"],
                    "action": s["action"],
                    "description": s["description"],
                    "status": s["status"],
                    "started_at": (
                        s["started_at"].isoformat() if s.get("started_at") else None
                    ),
                    "completed_at": (
                        s["completed_at"].isoformat() if s.get("completed_at") else None
                    ),
                }
                for s in plan.steps
            ],
            "created_at": plan.created_at.isoformat(),
            "started_at": plan.started_at.isoformat() if plan.started_at else None,
            "completed_at": (
                plan.completed_at.isoformat() if plan.completed_at else None
            ),
        }
