"""
Care Coordination Tools
Team collaboration and care coordination features
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TaskPriority(str, Enum):
    """Task priority levels"""
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    """Task completion status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CareTeamRole(str, Enum):
    """Care team member roles"""
    ATTENDING_PHYSICIAN = "attending_physician"
    RESIDENT = "resident"
    NURSE = "nurse"
    PHARMACIST = "pharmacist"
    CASE_MANAGER = "case_manager"
    SOCIAL_WORKER = "social_worker"
    PHYSICAL_THERAPIST = "physical_therapist"
    RESPIRATORY_THERAPIST = "respiratory_therapist"
    DIETITIAN = "dietitian"
    CONSULTANT = "consultant"


class CareTask:
    """Care coordination task"""
    
    def __init__(
        self,
        task_id: str,
        title: str,
        description: str,
        priority: TaskPriority,
        assigned_to: str,
        assigned_role: CareTeamRole,
        due_date: datetime,
        patient_id: str,
        created_by: str
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.assigned_to = assigned_to
        self.assigned_role = assigned_role
        self.due_date = due_date
        self.patient_id = patient_id
        self.created_by = created_by
        self.created_at = datetime.utcnow()
        self.status = TaskStatus.PENDING
        self.completed_at: Optional[datetime] = None
        self.notes: List[str] = []
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        return datetime.utcnow() > self.due_date and self.status != TaskStatus.COMPLETED
    
    def complete(self, notes: str = None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if notes:
            self.notes.append(notes)
        logger.info(f"Task completed: {self.task_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'assigned_to': self.assigned_to,
            'assigned_role': self.assigned_role.value,
            'due_date': self.due_date.isoformat(),
            'patient_id': self.patient_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'is_overdue': self.is_overdue()
        }


class CareTeamMember:
    """Care team member"""
    
    def __init__(
        self,
        member_id: str,
        name: str,
        role: CareTeamRole,
        specialty: Optional[str] = None,
        contact: Optional[str] = None
    ):
        self.member_id = member_id
        self.name = name
        self.role = role
        self.specialty = specialty
        self.contact = contact
        self.active_patients: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'member_id': self.member_id,
            'name': self.name,
            'role': self.role.value,
            'specialty': self.specialty,
            'contact': self.contact,
            'active_patients': len(self.active_patients)
        }


class Handoff:
    """Patient handoff communication"""
    
    def __init__(
        self,
        handoff_id: str,
        patient_id: str,
        from_provider: str,
        to_provider: str,
        handoff_type: str,
        summary: str,
        action_items: List[str],
        concerns: List[str]
    ):
        self.handoff_id = handoff_id
        self.patient_id = patient_id
        self.from_provider = from_provider
        self.to_provider = to_provider
        self.handoff_type = handoff_type  # shift_change, transfer, discharge
        self.summary = summary
        self.action_items = action_items
        self.concerns = concerns
        self.created_at = datetime.utcnow()
        self.acknowledged = False
        self.acknowledged_at: Optional[datetime] = None
    
    def acknowledge(self):
        """Acknowledge receipt of handoff"""
        self.acknowledged = True
        self.acknowledged_at = datetime.utcnow()
        logger.info(f"Handoff acknowledged: {self.handoff_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'handoff_id': self.handoff_id,
            'patient_id': self.patient_id,
            'from_provider': self.from_provider,
            'to_provider': self.to_provider,
            'handoff_type': self.handoff_type,
            'summary': self.summary,
            'action_items': self.action_items,
            'concerns': self.concerns,
            'created_at': self.created_at.isoformat(),
            'acknowledged': self.acknowledged,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }


class CareCoordinator:
    """
    Care Coordination System
    Manages team collaboration and care coordination
    """
    
    def __init__(self):
        self.tasks: Dict[str, CareTask] = {}
        self.team_members: Dict[str, CareTeamMember] = {}
        self.handoffs: Dict[str, Handoff] = {}
        self.patient_teams: Dict[str, List[str]] = {}  # patient_id -> [member_ids]
    
    def create_task(
        self,
        title: str,
        description: str,
        priority: TaskPriority,
        assigned_to: str,
        assigned_role: CareTeamRole,
        due_hours: int,
        patient_id: str,
        created_by: str
    ) -> CareTask:
        """Create a new care task"""
        task_id = f"TASK_{datetime.utcnow().timestamp()}"
        due_date = datetime.utcnow() + timedelta(hours=due_hours)
        
        task = CareTask(
            task_id,
            title,
            description,
            priority,
            assigned_to,
            assigned_role,
            due_date,
            patient_id,
            created_by
        )
        
        self.tasks[task_id] = task
        logger.info(f"Created task: {task_id} for patient: {patient_id}")
        
        return task
    
    def get_task(self, task_id: str) -> Optional[CareTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_patient(self, patient_id: str) -> List[CareTask]:
        """Get all tasks for a patient"""
        return [
            task for task in self.tasks.values()
            if task.patient_id == patient_id
        ]
    
    def get_tasks_by_assignee(self, assignee: str) -> List[CareTask]:
        """Get all tasks assigned to a user"""
        return [
            task for task in self.tasks.values()
            if task.assigned_to == assignee and task.status != TaskStatus.COMPLETED
        ]
    
    def get_overdue_tasks(self) -> List[CareTask]:
        """Get all overdue tasks"""
        return [
            task for task in self.tasks.values()
            if task.is_overdue()
        ]
    
    def complete_task(self, task_id: str, notes: str = None) -> bool:
        """Complete a task"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.complete(notes)
        return True
    
    def add_team_member(
        self,
        name: str,
        role: CareTeamRole,
        specialty: Optional[str] = None,
        contact: Optional[str] = None
    ) -> CareTeamMember:
        """Add a care team member"""
        member_id = f"MEMBER_{datetime.utcnow().timestamp()}"
        
        member = CareTeamMember(
            member_id,
            name,
            role,
            specialty,
            contact
        )
        
        self.team_members[member_id] = member
        logger.info(f"Added team member: {name} ({role.value})")
        
        return member
    
    def assign_to_patient(self, patient_id: str, member_id: str) -> bool:
        """Assign team member to patient"""
        member = self.team_members.get(member_id)
        if not member:
            return False
        
        if patient_id not in self.patient_teams:
            self.patient_teams[patient_id] = []
        
        if member_id not in self.patient_teams[patient_id]:
            self.patient_teams[patient_id].append(member_id)
            member.active_patients.append(patient_id)
            logger.info(f"Assigned {member.name} to patient {patient_id}")
        
        return True
    
    def get_patient_team(self, patient_id: str) -> List[CareTeamMember]:
        """Get care team for a patient"""
        member_ids = self.patient_teams.get(patient_id, [])
        return [
            self.team_members[mid] for mid in member_ids
            if mid in self.team_members
        ]
    
    def create_handoff(
        self,
        patient_id: str,
        from_provider: str,
        to_provider: str,
        handoff_type: str,
        summary: str,
        action_items: List[str],
        concerns: List[str]
    ) -> Handoff:
        """Create a patient handoff"""
        handoff_id = f"HANDOFF_{datetime.utcnow().timestamp()}"
        
        handoff = Handoff(
            handoff_id,
            patient_id,
            from_provider,
            to_provider,
            handoff_type,
            summary,
            action_items,
            concerns
        )
        
        self.handoffs[handoff_id] = handoff
        logger.info(f"Created handoff: {handoff_id} for patient: {patient_id}")
        
        return handoff
    
    def acknowledge_handoff(self, handoff_id: str) -> bool:
        """Acknowledge receipt of handoff"""
        handoff = self.handoffs.get(handoff_id)
        if not handoff:
            return False
        
        handoff.acknowledge()
        return True
    
    def get_pending_handoffs(self, provider: str) -> List[Handoff]:
        """Get pending handoffs for a provider"""
        return [
            handoff for handoff in self.handoffs.values()
            if handoff.to_provider == provider and not handoff.acknowledged
        ]
    
    def generate_daily_task_list(
        self,
        patient_id: str,
        date: datetime = None
    ) -> List[Dict[str, Any]]:
        """Generate daily task list for a patient"""
        if date is None:
            date = datetime.utcnow()
        
        # Standard daily tasks
        daily_tasks = [
            {
                'title': 'Morning Assessment',
                'description': 'Complete morning vital signs and physical assessment',
                'priority': TaskPriority.HIGH,
                'role': CareTeamRole.NURSE,
                'due_hours': 4
            },
            {
                'title': 'Medication Reconciliation',
                'description': 'Review and reconcile all medications',
                'priority': TaskPriority.MEDIUM,
                'role': CareTeamRole.PHARMACIST,
                'due_hours': 8
            },
            {
                'title': 'Daily Progress Note',
                'description': 'Document daily progress note',
                'priority': TaskPriority.HIGH,
                'role': CareTeamRole.ATTENDING_PHYSICIAN,
                'due_hours': 12
            },
            {
                'title': 'Discharge Planning Review',
                'description': 'Review discharge planning needs',
                'priority': TaskPriority.MEDIUM,
                'role': CareTeamRole.CASE_MANAGER,
                'due_hours': 24
            }
        ]
        
        return daily_tasks
    
    def generate_handoff_report(
        self,
        patient_id: str,
        provider: str
    ) -> Dict[str, Any]:
        """Generate standardized handoff report (SBAR format)"""
        
        # Get patient tasks
        tasks = self.get_tasks_by_patient(patient_id)
        pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
        
        # Get care team
        team = self.get_patient_team(patient_id)
        
        report = {
            'patient_id': patient_id,
            'provider': provider,
            'generated_at': datetime.utcnow().isoformat(),
            'sbar': {
                'situation': {
                    'description': 'Current patient status and reason for admission',
                    'key_points': [
                        'Primary diagnosis',
                        'Current location',
                        'Code status'
                    ]
                },
                'background': {
                    'description': 'Relevant medical history and hospital course',
                    'key_points': [
                        'Past medical history',
                        'Medications',
                        'Allergies',
                        'Recent procedures'
                    ]
                },
                'assessment': {
                    'description': 'Current clinical assessment',
                    'key_points': [
                        'Vital signs trends',
                        'Laboratory results',
                        'Physical exam findings',
                        'Response to treatment'
                    ]
                },
                'recommendation': {
                    'description': 'Plan and action items',
                    'key_points': [
                        'Pending tasks',
                        'Anticipated issues',
                        'Follow-up needed'
                    ]
                }
            },
            'pending_tasks': [t.to_dict() for t in pending_tasks],
            'care_team': [m.to_dict() for m in team],
            'action_items': [
                'Review pending lab results',
                'Follow up on consults',
                'Reassess pain management',
                'Update family on progress'
            ]
        }
        
        return report
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get care coordination statistics"""
        total_tasks = len(self.tasks)
        pending_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        overdue_tasks = len(self.get_overdue_tasks())
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        
        pending_handoffs = sum(1 for h in self.handoffs.values() if not h.acknowledged)
        
        return {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'team_members': len(self.team_members),
            'total_handoffs': len(self.handoffs),
            'pending_handoffs': pending_handoffs
        }


# Global care coordinator instance
care_coordinator = CareCoordinator()