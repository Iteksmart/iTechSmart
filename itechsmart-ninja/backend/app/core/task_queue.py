"""
Asynchronous Task Queue System for iTechSmart Ninja
Enables background task execution with status tracking and result compilation
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Task priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class TaskResult:
    """Task execution result"""

    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }


@dataclass
class Task:
    """Represents an asynchronous task"""

    task_id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_task_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    timeout: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "result": self.result,
            "error": self.error,
            "progress": self.progress,
            "metadata": self.metadata,
            "parent_task_id": self.parent_task_id,
            "subtasks": self.subtasks,
            "dependencies": self.dependencies,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }


class TaskQueue:
    """
    Asynchronous task queue with priority support

    Features:
    - Priority-based task execution
    - Background workers
    - Task dependencies
    - Subtask support
    - Progress tracking
    - Result compilation
    - Retry mechanism
    - Timeout support
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks: Dict[str, Task] = {}
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.callbacks: Dict[str, List[Callable]] = {}

    async def start(self):
        """Start the task queue workers"""
        if self.is_running:
            return

        self.is_running = True
        self.workers = [
            asyncio.create_task(self._worker(i)) for i in range(self.max_workers)
        ]
        logger.info(f"Task queue started with {self.max_workers} workers")

    async def stop(self):
        """Stop the task queue workers"""
        self.is_running = False

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        logger.info("Task queue stopped")

    async def submit(
        self,
        func: Callable,
        *args,
        name: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        parent_task_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        max_retries: int = 3,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> str:
        """
        Submit a task to the queue

        Args:
            func: Function to execute
            *args: Positional arguments
            name: Task name
            priority: Task priority
            metadata: Additional metadata
            parent_task_id: Parent task ID for subtasks
            dependencies: List of task IDs this task depends on
            max_retries: Maximum retry attempts
            timeout: Task timeout in seconds
            **kwargs: Keyword arguments

        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())

        task = Task(
            task_id=task_id,
            name=name or func.__name__,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            metadata=metadata or {},
            parent_task_id=parent_task_id,
            dependencies=dependencies or [],
            max_retries=max_retries,
            timeout=timeout,
        )

        self.tasks[task_id] = task

        # If this is a subtask, add to parent's subtasks
        if parent_task_id and parent_task_id in self.tasks:
            self.tasks[parent_task_id].subtasks.append(task_id)

        # Queue the task
        await self.queue.put((priority.value, task_id))
        task.status = TaskStatus.QUEUED

        logger.info(f"Task submitted: {task_id} ({name})")
        return task_id

    async def submit_batch(
        self, tasks: List[Dict[str, Any]], parent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit multiple tasks as a batch

        Args:
            tasks: List of task definitions
            parent_name: Name for the parent batch task

        Returns:
            Batch information with task IDs
        """
        batch_id = str(uuid.uuid4())
        task_ids = []

        for task_def in tasks:
            task_id = await self.submit(
                func=task_def["func"],
                *task_def.get("args", ()),
                name=task_def.get("name"),
                priority=task_def.get("priority", TaskPriority.NORMAL),
                metadata={**task_def.get("metadata", {}), "batch_id": batch_id},
                parent_task_id=batch_id,
                **task_def.get("kwargs", {}),
            )
            task_ids.append(task_id)

        return {
            "batch_id": batch_id,
            "task_ids": task_ids,
            "total_tasks": len(task_ids),
            "name": parent_name or f"Batch {batch_id[:8]}",
        }

    async def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        if task_id in self.tasks:
            return self.tasks[task_id].to_dict()
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id].to_dict()
        return None

    async def get_result(
        self, task_id: str, wait: bool = False
    ) -> Optional[TaskResult]:
        """
        Get task result

        Args:
            task_id: Task ID
            wait: Wait for task to complete

        Returns:
            Task result or None
        """
        if wait:
            while task_id not in self.completed_tasks:
                if task_id not in self.tasks:
                    return None
                await asyncio.sleep(0.1)

        return self.completed_tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status in [TaskStatus.PENDING, TaskStatus.QUEUED]:
                task.status = TaskStatus.CANCELLED
                logger.info(f"Task cancelled: {task_id}")
                return True
        return False

    async def pause_task(self, task_id: str) -> bool:
        """Pause a task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.IN_PROGRESS:
                task.status = TaskStatus.PAUSED
                logger.info(f"Task paused: {task_id}")
                return True
        return False

    async def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PAUSED:
                task.status = TaskStatus.QUEUED
                await self.queue.put((task.priority.value, task_id))
                logger.info(f"Task resumed: {task_id}")
                return True
        return False

    def register_callback(self, task_id: str, callback: Callable):
        """Register a callback for task completion"""
        if task_id not in self.callbacks:
            self.callbacks[task_id] = []
        self.callbacks[task_id].append(callback)

    async def _worker(self, worker_id: int):
        """Worker coroutine"""
        logger.info(f"Worker {worker_id} started")

        while self.is_running:
            try:
                # Get task from queue with timeout
                try:
                    priority, task_id = await asyncio.wait_for(
                        self.queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                if task_id not in self.tasks:
                    continue

                task = self.tasks[task_id]

                # Check if task is cancelled
                if task.status == TaskStatus.CANCELLED:
                    continue

                # Check dependencies
                if not await self._check_dependencies(task):
                    # Re-queue if dependencies not met
                    await self.queue.put((priority, task_id))
                    await asyncio.sleep(0.5)
                    continue

                # Execute task
                await self._execute_task(task, worker_id)

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")

        logger.info(f"Worker {worker_id} stopped")

    async def _check_dependencies(self, task: Task) -> bool:
        """Check if task dependencies are met"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
            if self.completed_tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True

    async def _execute_task(self, task: Task, worker_id: int):
        """Execute a task"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.active_tasks[task.task_id] = task

        logger.info(f"Worker {worker_id} executing task: {task.task_id} ({task.name})")

        try:
            # Execute with timeout if specified
            if task.timeout:
                result = await asyncio.wait_for(
                    task.func(*task.args, **task.kwargs), timeout=task.timeout
                )
            else:
                result = await task.func(*task.args, **task.kwargs)

            # Task completed successfully
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            task.progress = 100.0

            # Create result
            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                started_at=task.started_at,
                completed_at=task.completed_at,
                execution_time=(task.completed_at - task.started_at).total_seconds(),
                metadata=task.metadata,
            )

            self.completed_tasks[task.task_id] = task_result

            # Execute callbacks
            await self._execute_callbacks(task.task_id, task_result)

            logger.info(f"Task completed: {task.task_id} ({task.name})")

        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = f"Task timeout after {task.timeout} seconds"
            await self._handle_task_failure(task)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            await self._handle_task_failure(task)

        finally:
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]

    async def _handle_task_failure(self, task: Task):
        """Handle task failure with retry logic"""
        logger.error(f"Task failed: {task.task_id} ({task.name}) - {task.error}")

        # Retry if possible
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.QUEUED
            await self.queue.put((task.priority.value, task.task_id))
            logger.info(
                f"Retrying task: {task.task_id} (attempt {task.retry_count}/{task.max_retries})"
            )
        else:
            # Max retries reached
            task.completed_at = datetime.utcnow()

            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=task.error,
                started_at=task.started_at,
                completed_at=task.completed_at,
                execution_time=(
                    (task.completed_at - task.started_at).total_seconds()
                    if task.started_at
                    else 0
                ),
                metadata=task.metadata,
            )

            self.completed_tasks[task.task_id] = task_result

            # Execute callbacks
            await self._execute_callbacks(task.task_id, task_result)

    async def _execute_callbacks(self, task_id: str, result: TaskResult):
        """Execute registered callbacks"""
        if task_id in self.callbacks:
            for callback in self.callbacks[task_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(result)
                    else:
                        callback(result)
                except Exception as e:
                    logger.error(f"Callback error for task {task_id}: {str(e)}")

    async def compile_results(
        self, task_ids: List[str], wait: bool = True
    ) -> Dict[str, Any]:
        """
        Compile results from multiple tasks

        Args:
            task_ids: List of task IDs
            wait: Wait for all tasks to complete

        Returns:
            Compiled results
        """
        if wait:
            # Wait for all tasks to complete
            while not all(tid in self.completed_tasks for tid in task_ids):
                await asyncio.sleep(0.1)

        results = []
        errors = []

        for task_id in task_ids:
            if task_id in self.completed_tasks:
                result = self.completed_tasks[task_id]
                if result.status == TaskStatus.COMPLETED:
                    results.append(result.result)
                else:
                    errors.append({"task_id": task_id, "error": result.error})

        return {
            "total_tasks": len(task_ids),
            "completed": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics"""
        total_tasks = len(self.tasks) + len(self.completed_tasks)
        completed = len(
            [
                t
                for t in self.completed_tasks.values()
                if t.status == TaskStatus.COMPLETED
            ]
        )
        failed = len(
            [t for t in self.completed_tasks.values() if t.status == TaskStatus.FAILED]
        )

        return {
            "total_tasks": total_tasks,
            "pending": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
            ),
            "queued": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.QUEUED]
            ),
            "in_progress": len(self.active_tasks),
            "completed": completed,
            "failed": failed,
            "cancelled": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.CANCELLED]
            ),
            "success_rate": completed / total_tasks if total_tasks > 0 else 0,
            "active_workers": len(self.workers),
            "max_workers": self.max_workers,
        }


# Global task queue instance
task_queue = TaskQueue(max_workers=5)
