"""
Task Scheduler Integration
Provides cron-like task scheduling using APScheduler
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
import logging
import asyncio
import uuid

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Task scheduler for automated execution
    """
    
    def __init__(self):
        self.scheduler = None
        self.scheduled_tasks: Dict[str, Any] = {}
        self.execution_callback: Optional[Callable] = None
        self._init_scheduler()
    
    def _init_scheduler(self):
        """Initialize APScheduler"""
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.jobstores.memory import MemoryJobStore
            from apscheduler.executors.asyncio import AsyncIOExecutor
            
            jobstores = {
                'default': MemoryJobStore()
            }
            executors = {
                'default': AsyncIOExecutor()
            }
            job_defaults = {
                'coalesce': False,
                'max_instances': 3,
                'misfire_grace_time': 60
            }
            
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
            
            self.scheduler.start()
            logger.info("Task scheduler initialized successfully")
            
        except Exception as e:
            logger.warning(f"APScheduler not available: {str(e)}")
            self.scheduler = None
    
    def set_execution_callback(self, callback: Callable):
        """Set callback function for task execution"""
        self.execution_callback = callback
    
    async def create_task(
        self,
        task_id: str,
        name: str,
        schedule: str,
        code: str,
        language: str = "python",
        timeout: int = 300,
        max_retries: int = 3,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Create scheduled task
        
        Args:
            task_id: Task ID
            name: Task name
            schedule: Cron expression or interval
            code: Code to execute
            language: Programming language
            timeout: Execution timeout
            max_retries: Maximum retry attempts
            enabled: Whether task is enabled
            
        Returns:
            Task details
        """
        try:
            # Validate and parse schedule
            schedule_type, schedule_params = self._parse_schedule(schedule)
            
            # Calculate next run
            next_run = self._calculate_next_run(schedule)
            
            task_info = {
                "id": task_id,
                "name": name,
                "schedule": schedule,
                "schedule_type": schedule_type,
                "schedule_params": schedule_params,
                "code": code,
                "language": language,
                "enabled": enabled,
                "timeout": timeout,
                "max_retries": max_retries,
                "retry_count": 0,
                "next_run": next_run.isoformat() if next_run else None,
                "last_run": None,
                "last_status": None,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.scheduled_tasks[task_id] = task_info
            
            # Add to APScheduler if enabled
            if enabled and self.scheduler:
                self._add_job_to_scheduler(task_id, task_info)
            
            logger.info(f"Created scheduled task {task_id}: {name}")
            return task_info
            
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise
    
    def _parse_schedule(self, schedule: str) -> tuple:
        """Parse schedule expression"""
        try:
            # Check if it's a cron expression (5 or 6 parts)
            parts = schedule.split()
            if len(parts) in [5, 6]:
                return ('cron', {
                    'minute': parts[0] if len(parts) >= 1 else '*',
                    'hour': parts[1] if len(parts) >= 2 else '*',
                    'day': parts[2] if len(parts) >= 3 else '*',
                    'month': parts[3] if len(parts) >= 4 else '*',
                    'day_of_week': parts[4] if len(parts) >= 5 else '*',
                    'second': parts[5] if len(parts) == 6 else '0'
                })
            
            # Check if it's an interval expression
            if schedule.startswith('every '):
                interval_str = schedule[6:].strip()
                
                if 'second' in interval_str:
                    seconds = int(interval_str.split()[0])
                    return ('interval', {'seconds': seconds})
                elif 'minute' in interval_str:
                    minutes = int(interval_str.split()[0])
                    return ('interval', {'minutes': minutes})
                elif 'hour' in interval_str:
                    hours = int(interval_str.split()[0])
                    return ('interval', {'hours': hours})
                elif 'day' in interval_str:
                    days = int(interval_str.split()[0])
                    return ('interval', {'days': days})
            
            # Check if it's a one-time execution
            if schedule.startswith('at '):
                time_str = schedule[3:].strip()
                run_time = datetime.fromisoformat(time_str)
                return ('date', {'run_date': run_time})
            
            raise ValueError(f"Invalid schedule format: {schedule}")
            
        except Exception as e:
            logger.error(f"Error parsing schedule: {str(e)}")
            raise
    
    def _calculate_next_run(self, schedule: str) -> Optional[datetime]:
        """Calculate next run time from schedule"""
        try:
            from croniter import croniter
            
            schedule_type, params = self._parse_schedule(schedule)
            
            if schedule_type == 'cron':
                # Reconstruct cron expression
                cron_expr = f"{params['minute']} {params['hour']} {params['day']} {params['month']} {params['day_of_week']}"
                cron = croniter(cron_expr, datetime.utcnow())
                return cron.get_next(datetime)
            
            elif schedule_type == 'interval':
                now = datetime.utcnow()
                if 'seconds' in params:
                    return now + timedelta(seconds=params['seconds'])
                elif 'minutes' in params:
                    return now + timedelta(minutes=params['minutes'])
                elif 'hours' in params:
                    return now + timedelta(hours=params['hours'])
                elif 'days' in params:
                    return now + timedelta(days=params['days'])
            
            elif schedule_type == 'date':
                return params['run_date']
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating next run: {str(e)}")
            return None
    
    def _add_job_to_scheduler(self, task_id: str, task_info: Dict[str, Any]):
        """Add job to APScheduler"""
        try:
            if not self.scheduler:
                return
            
            schedule_type = task_info['schedule_type']
            params = task_info['schedule_params']
            
            # Create job function
            async def job_func():
                await self._execute_task(task_id)
            
            if schedule_type == 'cron':
                self.scheduler.add_job(
                    job_func,
                    'cron',
                    id=task_id,
                    **params,
                    replace_existing=True
                )
            elif schedule_type == 'interval':
                self.scheduler.add_job(
                    job_func,
                    'interval',
                    id=task_id,
                    **params,
                    replace_existing=True
                )
            elif schedule_type == 'date':
                self.scheduler.add_job(
                    job_func,
                    'date',
                    id=task_id,
                    **params,
                    replace_existing=True
                )
            
            logger.info(f"Added job {task_id} to scheduler")
            
        except Exception as e:
            logger.error(f"Error adding job to scheduler: {str(e)}")
    
    async def _execute_task(self, task_id: str):
        """Execute scheduled task"""
        try:
            if task_id not in self.scheduled_tasks:
                logger.error(f"Task {task_id} not found")
                return
            
            task_info = self.scheduled_tasks[task_id]
            
            if not task_info['enabled']:
                logger.info(f"Task {task_id} is disabled, skipping execution")
                return
            
            logger.info(f"Executing task {task_id}: {task_info['name']}")
            
            # Update last run
            task_info['last_run'] = datetime.utcnow().isoformat()
            
            # Call execution callback if set
            if self.execution_callback:
                try:
                    result = await self.execution_callback(task_id, task_info)
                    task_info['last_status'] = 'success' if result.get('exit_code', 0) == 0 else 'failure'
                    task_info['retry_count'] = 0
                except Exception as e:
                    logger.error(f"Task execution failed: {str(e)}")
                    task_info['last_status'] = 'failure'
                    task_info['retry_count'] += 1
                    
                    # Retry if needed
                    if task_info['retry_count'] < task_info['max_retries']:
                        logger.info(f"Retrying task {task_id} (attempt {task_info['retry_count']})")
                        await asyncio.sleep(60)  # Wait 1 minute before retry
                        await self._execute_task(task_id)
            
            # Update next run
            task_info['next_run'] = self._calculate_next_run(task_info['schedule']).isoformat()
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
    
    async def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        schedule: Optional[str] = None,
        code: Optional[str] = None,
        enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update scheduled task"""
        try:
            if task_id not in self.scheduled_tasks:
                raise ValueError(f"Task {task_id} not found")
            
            task_info = self.scheduled_tasks[task_id]
            
            # Update fields
            if name is not None:
                task_info['name'] = name
            if code is not None:
                task_info['code'] = code
            if enabled is not None:
                task_info['enabled'] = enabled
            
            # Update schedule if changed
            if schedule is not None and schedule != task_info['schedule']:
                task_info['schedule'] = schedule
                schedule_type, schedule_params = self._parse_schedule(schedule)
                task_info['schedule_type'] = schedule_type
                task_info['schedule_params'] = schedule_params
                task_info['next_run'] = self._calculate_next_run(schedule).isoformat()
                
                # Update in scheduler
                if self.scheduler:
                    self.scheduler.remove_job(task_id)
                    if task_info['enabled']:
                        self._add_job_to_scheduler(task_id, task_info)
            
            logger.info(f"Updated task {task_id}")
            return task_info
            
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            raise
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete scheduled task"""
        try:
            if task_id not in self.scheduled_tasks:
                raise ValueError(f"Task {task_id} not found")
            
            # Remove from scheduler
            if self.scheduler:
                try:
                    self.scheduler.remove_job(task_id)
                except:
                    pass
            
            # Remove from memory
            del self.scheduled_tasks[task_id]
            
            logger.info(f"Deleted task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}")
            raise
    
    async def enable_task(self, task_id: str) -> bool:
        """Enable task"""
        try:
            if task_id not in self.scheduled_tasks:
                raise ValueError(f"Task {task_id} not found")
            
            task_info = self.scheduled_tasks[task_id]
            task_info['enabled'] = True
            
            # Add to scheduler
            if self.scheduler:
                self._add_job_to_scheduler(task_id, task_info)
            
            logger.info(f"Enabled task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling task: {str(e)}")
            raise
    
    async def disable_task(self, task_id: str) -> bool:
        """Disable task"""
        try:
            if task_id not in self.scheduled_tasks:
                raise ValueError(f"Task {task_id} not found")
            
            task_info = self.scheduled_tasks[task_id]
            task_info['enabled'] = False
            
            # Remove from scheduler
            if self.scheduler:
                try:
                    self.scheduler.remove_job(task_id)
                except:
                    pass
            
            logger.info(f"Disabled task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error disabling task: {str(e)}")
            raise
    
    async def run_task_now(self, task_id: str) -> Dict[str, Any]:
        """Execute task immediately"""
        try:
            if task_id not in self.scheduled_tasks:
                raise ValueError(f"Task {task_id} not found")
            
            # Execute task
            await self._execute_task(task_id)
            
            return {
                "execution_id": f"exec_{uuid.uuid4().hex[:12]}",
                "task_id": task_id,
                "status": "completed",
                "started_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running task: {str(e)}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task details"""
        return self.scheduled_tasks.get(task_id)
    
    async def list_tasks(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all tasks"""
        tasks = list(self.scheduled_tasks.values())
        
        if user_id is not None:
            tasks = [t for t in tasks if t.get('user_id') == user_id]
        
        return tasks
    
    async def get_next_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get next scheduled runs"""
        try:
            if not self.scheduler:
                return []
            
            jobs = self.scheduler.get_jobs()
            next_runs = []
            
            for job in jobs[:limit]:
                task_info = self.scheduled_tasks.get(job.id, {})
                next_runs.append({
                    'task_id': job.id,
                    'task_name': task_info.get('name', 'Unknown'),
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'schedule': task_info.get('schedule', '')
                })
            
            # Sort by next run time
            next_runs.sort(key=lambda x: x['next_run'] or '')
            
            return next_runs[:limit]
            
        except Exception as e:
            logger.error(f"Error getting next runs: {str(e)}")
            return []
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        try:
            return {
                'running': self.scheduler.running if self.scheduler else False,
                'total_tasks': len(self.scheduled_tasks),
                'enabled_tasks': sum(1 for t in self.scheduled_tasks.values() if t['enabled']),
                'disabled_tasks': sum(1 for t in self.scheduled_tasks.values() if not t['enabled']),
                'active_jobs': len(self.scheduler.get_jobs()) if self.scheduler else 0
            }
        except Exception as e:
            logger.error(f"Error getting scheduler status: {str(e)}")
            return {}
    
    def shutdown(self):
        """Shutdown scheduler"""
        try:
            if self.scheduler:
                self.scheduler.shutdown()
                logger.info("Scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")