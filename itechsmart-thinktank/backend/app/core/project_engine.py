"""
Project Management Engine for iTechSmart Think-Tank
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import (
    Project,
    ProjectStatus,
    ProjectPriority,
    Task,
    TaskStatus,
    TeamMember,
    ProgressUpdate,
)


class ProjectEngine:
    """
    Project management engine for handling project lifecycle
    """

    def __init__(self):
        self.engine_id = "project-engine"
        self.version = "1.0.0"

    async def create_project(
        self,
        db: Session,
        name: str,
        description: str,
        creator_id: int,
        client_info: Optional[Dict] = None,
        requirements: Optional[List[str]] = None,
        tech_stack: Optional[Dict] = None,
    ) -> Project:
        """Create a new project"""

        project = Project(
            name=name,
            description=description,
            creator_id=creator_id,
            status=ProjectStatus.IDEATION,
            priority=ProjectPriority.MEDIUM,
            requirements=requirements or [],
            tech_stack=tech_stack or {},
            client_name=client_info.get("name") if client_info else None,
            client_organization=(
                client_info.get("organization") if client_info else None
            ),
            client_email=client_info.get("email") if client_info else None,
            start_date=datetime.utcnow(),
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    async def update_project_status(
        self, db: Session, project_id: int, new_status: ProjectStatus
    ) -> Project:
        """Update project status"""

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        old_status = project.status
        project.status = new_status
        project.updated_at = datetime.utcnow()

        # Set completion date if completed
        if new_status == ProjectStatus.COMPLETED:
            project.completed_date = datetime.utcnow()
            project.progress = 100.0

        db.commit()
        db.refresh(project)

        return project

    async def calculate_project_progress(self, db: Session, project_id: int) -> float:
        """Calculate project progress based on tasks"""

        # Get all tasks for the project
        tasks = db.query(Task).filter(Task.project_id == project_id).all()

        if not tasks:
            return 0.0

        # Calculate based on completed tasks
        completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.DONE)
        progress = (completed_tasks / len(tasks)) * 100

        # Update project progress
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.progress = progress
            db.commit()

        return progress

    async def add_team_member(
        self,
        db: Session,
        project_id: int,
        user_id: int,
        role: str,
        permissions: Optional[List[str]] = None,
    ) -> TeamMember:
        """Add a team member to a project"""

        # Check if already a member
        existing = (
            db.query(TeamMember)
            .filter(
                TeamMember.project_id == project_id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True,
            )
            .first()
        )

        if existing:
            raise ValueError("User is already a team member")

        team_member = TeamMember(
            project_id=project_id,
            user_id=user_id,
            role=role,
            permissions=permissions or [],
        )

        db.add(team_member)
        db.commit()
        db.refresh(team_member)

        return team_member

    async def create_task(
        self,
        db: Session,
        project_id: int,
        title: str,
        description: Optional[str] = None,
        assignee_id: Optional[int] = None,
        priority: ProjectPriority = ProjectPriority.MEDIUM,
        estimated_hours: Optional[float] = None,
        due_date: Optional[datetime] = None,
    ) -> Task:
        """Create a new task"""

        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            assignee_id=assignee_id,
            priority=priority,
            estimated_hours=estimated_hours,
            due_date=due_date,
            status=TaskStatus.TODO,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    async def update_task_status(
        self, db: Session, task_id: int, new_status: TaskStatus
    ) -> Task:
        """Update task status"""

        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = new_status
        task.updated_at = datetime.utcnow()

        # Set completion date if done
        if new_status == TaskStatus.DONE:
            task.completed_date = datetime.utcnow()

        db.commit()
        db.refresh(task)

        # Recalculate project progress
        await self.calculate_project_progress(db, task.project_id)

        return task

    async def add_progress_update(
        self,
        db: Session,
        project_id: int,
        title: str,
        description: str,
        is_milestone: bool = False,
        visible_to_client: bool = True,
        attachments: Optional[List[str]] = None,
    ) -> ProgressUpdate:
        """Add a progress update"""

        # Calculate current progress
        progress = await self.calculate_project_progress(db, project_id)

        # Count completed tasks
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        tasks_completed = sum(1 for task in tasks if task.status == TaskStatus.DONE)
        tasks_total = len(tasks)

        # Calculate hours spent
        hours_spent = sum(task.actual_hours or 0 for task in tasks)

        update = ProgressUpdate(
            project_id=project_id,
            title=title,
            description=description,
            progress_percentage=progress,
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            hours_spent=hours_spent,
            is_milestone=is_milestone,
            visible_to_client=visible_to_client,
            attachments=attachments or [],
        )

        db.add(update)
        db.commit()
        db.refresh(update)

        return update

    async def get_project_stats(self, db: Session, project_id: int) -> Dict[str, Any]:
        """Get comprehensive project statistics"""

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get tasks
        tasks = db.query(Task).filter(Task.project_id == project_id).all()

        # Calculate task statistics
        task_stats = {
            "total": len(tasks),
            "todo": sum(1 for t in tasks if t.status == TaskStatus.TODO),
            "in_progress": sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS),
            "review": sum(1 for t in tasks if t.status == TaskStatus.REVIEW),
            "done": sum(1 for t in tasks if t.status == TaskStatus.DONE),
            "blocked": sum(1 for t in tasks if t.status == TaskStatus.BLOCKED),
        }

        # Calculate time statistics
        estimated_hours = sum(t.estimated_hours or 0 for t in tasks)
        actual_hours = sum(t.actual_hours or 0 for t in tasks)

        # Get team size
        team_size = (
            db.query(TeamMember)
            .filter(TeamMember.project_id == project_id, TeamMember.is_active == True)
            .count()
        )

        # Calculate days since start
        days_active = 0
        if project.start_date:
            days_active = (datetime.utcnow() - project.start_date).days

        # Calculate days until due
        days_until_due = None
        if project.due_date:
            days_until_due = (project.due_date - datetime.utcnow()).days

        return {
            "project_id": project_id,
            "name": project.name,
            "status": project.status.value,
            "priority": project.priority.value,
            "progress": project.progress,
            "tasks": task_stats,
            "time": {
                "estimated_hours": estimated_hours,
                "actual_hours": actual_hours,
                "hours_remaining": max(0, estimated_hours - actual_hours),
                "efficiency": (
                    (estimated_hours / actual_hours * 100) if actual_hours > 0 else 0
                ),
            },
            "team": {
                "size": team_size,
                "hours_per_member": actual_hours / team_size if team_size > 0 else 0,
            },
            "timeline": {
                "days_active": days_active,
                "days_until_due": days_until_due,
                "start_date": (
                    project.start_date.isoformat() if project.start_date else None
                ),
                "due_date": project.due_date.isoformat() if project.due_date else None,
                "completed_date": (
                    project.completed_date.isoformat()
                    if project.completed_date
                    else None
                ),
            },
            "client": {
                "name": project.client_name,
                "organization": project.client_organization,
                "email": project.client_email,
            },
        }

    async def get_dashboard_stats(
        self, db: Session, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get dashboard statistics"""

        # Base query
        query = db.query(Project)

        # Filter by user if specified
        if user_id:
            query = query.join(TeamMember).filter(TeamMember.user_id == user_id)

        # Get all projects
        projects = query.all()

        # Calculate statistics
        total_projects = len(projects)
        active_projects = sum(
            1
            for p in projects
            if p.status not in [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]
        )
        completed_projects = sum(
            1 for p in projects if p.status == ProjectStatus.COMPLETED
        )

        # Status breakdown
        status_breakdown = {}
        for status in ProjectStatus:
            status_breakdown[status.value] = sum(
                1 for p in projects if p.status == status
            )

        # Priority breakdown
        priority_breakdown = {}
        for priority in ProjectPriority:
            priority_breakdown[priority.value] = sum(
                1 for p in projects if p.priority == priority
            )

        # Average progress
        avg_progress = (
            sum(p.progress for p in projects) / len(projects) if projects else 0
        )

        # Total hours
        total_estimated = sum(p.estimated_hours or 0 for p in projects)
        total_actual = sum(p.actual_hours or 0 for p in projects)

        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "average_progress": round(avg_progress, 2),
            "status_breakdown": status_breakdown,
            "priority_breakdown": priority_breakdown,
            "hours": {
                "estimated": total_estimated,
                "actual": total_actual,
                "efficiency": (
                    (total_estimated / total_actual * 100) if total_actual > 0 else 0
                ),
            },
        }
