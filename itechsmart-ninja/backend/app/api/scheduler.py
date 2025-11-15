"""
Task Scheduler API Routes
Provides endpoints for managing scheduled tasks
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, ScheduledTask, TaskExecution
from app.integrations.task_scheduler import TaskScheduler

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])

# Initialize task scheduler
task_scheduler = TaskScheduler()


# Set up execution callback
async def execute_task_callback(task_id: str, task_info: Dict[str, Any]) -> Dict[str, Any]:
    """Callback function to execute scheduled tasks"""
    try:
        # Here you would integrate with your code execution system
        # For now, we'll simulate execution
        import subprocess
        
        code = task_info['code']
        language = task_info['language']
        timeout = task_info['timeout']
        
        if language == 'python':
            result = subprocess.run(
                ['python', '-c', code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
        elif language == 'nodejs':
            result = subprocess.run(
                ['node', '-e', code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        return {
            'output': result.stdout,
            'error': result.stderr,
            'exit_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            'output': '',
            'error': 'Execution timeout',
            'exit_code': 124
        }
    except Exception as e:
        return {
            'output': '',
            'error': str(e),
            'exit_code': 1
        }


task_scheduler.set_execution_callback(execute_task_callback)


@router.post("/tasks/create")
async def create_task(
    name: str,
    schedule: str,
    code: str,
    language: str = "python",
    description: Optional[str] = None,
    timeout: int = 300,
    max_retries: int = 3,
    enabled: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create scheduled task
    
    Args:
        name: Task name
        schedule: Cron expression or interval (e.g., "0 2 * * *" or "every 5 minutes")
        code: Code to execute
        language: Programming language (python, nodejs)
        description: Task description
        timeout: Execution timeout in seconds
        max_retries: Maximum retry attempts
        enabled: Whether task is enabled
    """
    try:
        # Generate task ID
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        # Create task in scheduler
        task_info = await task_scheduler.create_task(
            task_id=task_id,
            name=name,
            schedule=schedule,
            code=code,
            language=language,
            timeout=timeout,
            max_retries=max_retries,
            enabled=enabled
        )
        
        # Save to database
        task_db = ScheduledTask(
            user_id=current_user.id,
            task_id=task_id,
            name=name,
            description=description or '',
            schedule=schedule,
            code=code,
            language=language,
            enabled=enabled,
            max_retries=max_retries,
            timeout=timeout,
            next_run=datetime.fromisoformat(task_info['next_run']) if task_info['next_run'] else None
        )
        db.add(task_db)
        db.commit()
        db.refresh(task_db)
        
        return {
            "success": True,
            "task": {
                "id": task_db.id,
                "task_id": task_id,
                "name": name,
                "schedule": schedule,
                "language": language,
                "enabled": enabled,
                "next_run": task_info['next_run'],
                "created_at": task_db.created_at.isoformat() if task_db.created_at else None
            },
            "message": "Task created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    enabled: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all scheduled tasks"""
    try:
        query = db.query(ScheduledTask).filter(
            ScheduledTask.user_id == current_user.id
        )
        
        if enabled is not None:
            query = query.filter(ScheduledTask.enabled == enabled)
        
        tasks = query.offset(skip).limit(limit).all()
        
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "task_id": task.task_id,
                "name": task.name,
                "description": task.description,
                "schedule": task.schedule,
                "language": task.language,
                "enabled": task.enabled,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "last_status": task.last_status,
                "created_at": task.created_at.isoformat() if task.created_at else None
            })
        
        return {
            "success": True,
            "tasks": task_list,
            "total": len(task_list),
            "message": "Tasks retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task details"""
    try:
        task = db.query(ScheduledTask).filter(
            ScheduledTask.task_id == task_id,
            ScheduledTask.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "success": True,
            "task": {
                "id": task.id,
                "task_id": task.task_id,
                "name": task.name,
                "description": task.description,
                "schedule": task.schedule,
                "code": task.code,
                "language": task.language,
                "enabled": task.enabled,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "last_status": task.last_status,
                "retry_count": task.retry_count,
                "max_retries": task.max_retries,
                "timeout": task.timeout,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            },
            "message": "Task retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    name: Optional[str] = None,
    schedule: Optional[str] = None,
    code: Optional[str] = None,
    description: Optional[str] = None,
    enabled: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update scheduled task"""
    try:
        task = db.query(ScheduledTask).filter(
            ScheduledTask.task_id == task_id,
            ScheduledTask.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update in scheduler
        await task_scheduler.update_task(
            task_id=task_id,
            name=name,
            schedule=schedule,
            code=code,
            enabled=enabled
        )
        
        # Update database
        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if schedule is not None:
            task.schedule = schedule
        if code is not None:
            task.code = code
        if enabled is not None:
            task.enabled = enabled
        
        db.commit()
        db.refresh(task)
        
        return {
            "success": True,
            "task": {
                "id": task.id,
                "task_id": task.task_id,
                "name": task.name,
                "schedule": task.schedule,
                "enabled": task.enabled
            },
            "message": "Task updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete scheduled task"""
    try:
        task = db.query(ScheduledTask).filter(
            ScheduledTask.task_id == task_id,
            ScheduledTask.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Delete from scheduler
        await task_scheduler.delete_task(task_id)
        
        # Delete from database
        db.delete(task)
        db.commit()
        
        return {
            "success": True,
            "message": "Task deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/enable")
async def enable_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable scheduled task"""
    try:
        task = db.query(ScheduledTask).filter(
            ScheduledTask.task_id == task_id,
            ScheduledTask.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Enable in scheduler
        await task_scheduler.enable_task(task_id)
        
        # Update database
        task.enabled = True
        db.commit()
        
        return {
            "success": True,
            "message": "Task enabled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/disable")
async def disable_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable scheduled task"""
    try:
        task = db.query(ScheduledTask).filter(
            ScheduledTask.task_id == task_id,
            ScheduledTask.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Disable in scheduler
        await task_scheduler.disable_task(task_id)
        
        # Update database
        task.enabled = False
        db.commit()
        
        return {
            "success": True,
            "message": "Task disabled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/run-now")
async def run_task_now(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute task immediately"""
    try:
        task = db.query(ScheduledTask).filter(
            ScheduledTask.task_id == task_id,
            ScheduledTask.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Execute task
        result = await task_scheduler.run_task_now(task_id)
        
        # Save execution to database
        execution = TaskExecution(
            task_id=task.id,
            execution_id=result['execution_id'],
            status='running',
            started_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        
        return {
            "success": True,
            "execution": result,
            "message": "Task executed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/history")
async def get_task_history(
    task_id: str,
    skip: int = 0,
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task execution history"""
    try:
        task = db.query(ScheduledTask).filter(
            ScheduledTask.task_id == task_id,
            ScheduledTask.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        executions = db.query(TaskExecution).filter(
            TaskExecution.task_id == task.id
        ).order_by(TaskExecution.started_at.desc()).offset(skip).limit(limit).all()
        
        history = []
        for execution in executions:
            history.append({
                "execution_id": execution.execution_id,
                "status": execution.status,
                "output": execution.output,
                "error": execution.error,
                "exit_code": execution.exit_code,
                "execution_time": execution.execution_time,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
            })
        
        return {
            "success": True,
            "history": history,
            "total": len(history),
            "message": "Task history retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/logs")
async def get_task_logs(
    task_id: str,
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent task execution logs"""
    try:
        task = db.query(ScheduledTask).filter(
            ScheduledTask.task_id == task_id,
            ScheduledTask.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        executions = db.query(TaskExecution).filter(
            TaskExecution.task_id == task.id
        ).order_by(TaskExecution.started_at.desc()).limit(limit).all()
        
        logs = []
        for execution in executions:
            log_entry = f"[{execution.started_at}] Status: {execution.status}"
            if execution.output:
                log_entry += f"\nOutput: {execution.output}"
            if execution.error:
                log_entry += f"\nError: {execution.error}"
            logs.append(log_entry)
        
        return {
            "success": True,
            "logs": "\n\n".join(logs),
            "message": "Task logs retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/next-runs")
async def get_next_runs(
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user)
):
    """Get next scheduled runs"""
    try:
        next_runs = await task_scheduler.get_next_runs(limit)
        
        return {
            "success": True,
            "next_runs": next_runs,
            "total": len(next_runs),
            "message": "Next runs retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_scheduler_status(
    current_user: User = Depends(get_current_user)
):
    """Get scheduler status"""
    try:
        status = await task_scheduler.get_scheduler_status()
        
        return {
            "success": True,
            "status": status,
            "message": "Scheduler status retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))