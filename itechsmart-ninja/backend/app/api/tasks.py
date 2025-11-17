"""
Tasks API Routes
Handles task creation, execution, monitoring, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import asyncio

from app.core.database import get_db
from app.models.database import Task, TaskStep, User, Template
from app.api.auth import get_current_user
from app.agents.orchestrator import MultiAgentOrchestrator
from app.agents.researcher_agent import ResearcherAgent
from app.agents.coder_agent import CoderAgent
from app.agents.writer_agent import WriterAgent
from app.agents.analyst_agent import AnalystAgent
from app.agents.debugger_agent import DebuggerAgent
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: str
    task_type: str  # research, code, website, analysis, debug, documentation
    parameters: dict = {}
    template_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    task_type: str
    status: str
    progress: int
    result: Optional[dict]
    error: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]

    class Config:
        from_attributes = True


class TaskStepResponse(BaseModel):
    id: int
    task_id: int
    step_number: int
    agent_type: str
    description: str
    status: str
    result: Optional[dict]
    error: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]

    class Config:
        from_attributes = True


# Background task execution
async def execute_task_background(task_id: int, db_session):
    """Execute task in background"""
    try:
        # Get task from database
        task = db_session.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        # Update task status
        task.status = "running"
        task.started_at = datetime.utcnow()
        db_session.commit()

        logger.info(f"Starting task execution: {task.title} (ID: {task_id})")

        # Create orchestrator
        orchestrator = MultiAgentOrchestrator()

        # Execute task based on type
        result = None
        if task.task_type == "research":
            agent = ResearcherAgent()
            query = task.parameters.get("query", task.description)
            result = await agent.research(query)

        elif task.task_type == "code":
            agent = CoderAgent()
            language = task.parameters.get("language", "python")
            description = task.parameters.get("description", task.description)
            result = await agent.generate_code(description, language)

        elif task.task_type == "website":
            # Use orchestrator for complex website creation
            result = await orchestrator.execute_task(
                task_type="website",
                description=task.description,
                parameters=task.parameters,
            )

        elif task.task_type == "analysis":
            agent = AnalystAgent()
            data = task.parameters.get("data", [])
            analysis_type = task.parameters.get("analysis_type", "descriptive")
            result = await agent.analyze(data, analysis_type)

        elif task.task_type == "debug":
            agent = DebuggerAgent()
            error_message = task.parameters.get("error_message", "")
            code = task.parameters.get("code", "")
            result = await agent.debug(error_message, code)

        elif task.task_type == "documentation":
            agent = WriterAgent()
            doc_type = task.parameters.get("doc_type", "readme")
            content = task.parameters.get("content", {})
            result = await agent.write_documentation(doc_type, content)

        else:
            # Use orchestrator for complex tasks
            result = await orchestrator.execute_task(
                task_type=task.task_type,
                description=task.description,
                parameters=task.parameters,
            )

        # Update task with result
        task.status = "completed"
        task.progress = 100
        task.result = result
        task.completed_at = datetime.utcnow()
        db_session.commit()

        logger.info(f"Task completed successfully: {task.title} (ID: {task_id})")

    except Exception as e:
        logger.error(f"Task execution failed: {str(e)}")

        # Update task with error
        task = db_session.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            db_session.commit()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new task

    - **title**: Task title
    - **description**: Detailed task description
    - **task_type**: Type of task (research, code, website, analysis, debug, documentation)
    - **parameters**: Additional parameters for the task
    - **template_id**: Optional template to use
    """
    # Validate task type
    valid_types = [
        "research",
        "code",
        "website",
        "analysis",
        "debug",
        "documentation",
        "custom",
    ]
    if task_data.task_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task type. Must be one of: {', '.join(valid_types)}",
        )

    # If template_id provided, load template
    if task_data.template_id:
        template = (
            db.query(Template).filter(Template.id == task_data.template_id).first()
        )
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
            )
        # Merge template parameters with provided parameters
        task_data.parameters = {**template.parameters, **task_data.parameters}

    # Create task
    task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        parameters=task_data.parameters,
        status="pending",
        progress=0,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    logger.info(
        f"Task created: {task.title} (ID: {task.id}) by user {current_user.email}"
    )

    # Execute task in background
    background_tasks.add_task(execute_task_background, task.id, db)

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        status=task.status,
        progress=task.progress,
        result=task.result,
        error=task.error,
        created_at=task.created_at.isoformat(),
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List tasks for current user

    - **skip**: Number of tasks to skip (pagination)
    - **limit**: Maximum number of tasks to return
    - **status**: Filter by status (pending, running, completed, failed)
    - **task_type**: Filter by task type
    """
    query = db.query(Task).filter(Task.user_id == current_user.id)

    if status:
        query = query.filter(Task.status == status)

    if task_type:
        query = query.filter(Task.task_type == task_type)

    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    return [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            task_type=task.task_type,
            status=task.status,
            progress=task.progress,
            result=task.result,
            error=task.error,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
        )
        for task in tasks
    ]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get task details by ID"""
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        status=task.status,
        progress=task.progress,
        result=task.result,
        error=task.error,
        created_at=task.created_at.isoformat(),
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.get("/{task_id}/steps", response_model=List[TaskStepResponse])
async def get_task_steps(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all steps for a task"""
    # Verify task belongs to user
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    steps = (
        db.query(TaskStep)
        .filter(TaskStep.task_id == task_id)
        .order_by(TaskStep.step_number)
        .all()
    )

    return [
        TaskStepResponse(
            id=step.id,
            task_id=step.task_id,
            step_number=step.step_number,
            agent_type=step.agent_type,
            description=step.description,
            status=step.status,
            result=step.result,
            error=step.error,
            started_at=step.started_at.isoformat() if step.started_at else None,
            completed_at=step.completed_at.isoformat() if step.completed_at else None,
        )
        for step in steps
    ]


@router.post("/{task_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a running task"""
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if task.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be cancelled (not pending or running)",
        )

    task.status = "cancelled"
    task.completed_at = datetime.utcnow()
    db.commit()

    logger.info(f"Task cancelled: {task.title} (ID: {task_id})")

    return None


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a task"""
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    # Delete associated steps
    db.query(TaskStep).filter(TaskStep.task_id == task_id).delete()

    # Delete task
    db.delete(task)
    db.commit()

    logger.info(f"Task deleted: {task.title} (ID: {task_id})")

    return None


@router.get("/stats/summary")
async def get_task_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get task statistics for current user"""
    total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()

    completed_tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id, Task.status == "completed")
        .count()
    )

    failed_tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id, Task.status == "failed")
        .count()
    )

    running_tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id, Task.status == "running")
        .count()
    )

    pending_tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id, Task.status == "pending")
        .count()
    )

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "running_tasks": running_tasks,
        "pending_tasks": pending_tasks,
        "success_rate": round(
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2
        ),
    }
