"""
Clinical Workflow Engine
Automated clinical pathways and workflow management
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepType(str, Enum):
    """Types of workflow steps"""
    ASSESSMENT = "assessment"
    ORDER = "order"
    MEDICATION = "medication"
    LAB_TEST = "lab_test"
    IMAGING = "imaging"
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    DISCHARGE = "discharge"
    NOTIFICATION = "notification"


class WorkflowStep:
    """Individual workflow step"""
    
    def __init__(
        self,
        step_id: str,
        step_type: WorkflowStepType,
        title: str,
        description: str,
        required: bool = True,
        dependencies: List[str] = None,
        auto_execute: bool = False,
        timeout_hours: int = 24
    ):
        self.step_id = step_id
        self.step_type = step_type
        self.title = title
        self.description = description
        self.required = required
        self.dependencies = dependencies or []
        self.auto_execute = auto_execute
        self.timeout_hours = timeout_hours
        self.status = WorkflowStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.assigned_to: Optional[str] = None
        self.result: Optional[Dict[str, Any]] = None
        self.notes: List[str] = []
    
    def can_execute(self, completed_steps: List[str]) -> bool:
        """Check if step can be executed based on dependencies"""
        return all(dep in completed_steps for dep in self.dependencies)
    
    def start(self, assigned_to: str = None):
        """Start step execution"""
        self.status = WorkflowStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        self.assigned_to = assigned_to
        logger.info(f"Started workflow step: {self.step_id}")
    
    def complete(self, result: Dict[str, Any] = None, notes: str = None):
        """Complete step execution"""
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.result = result
        if notes:
            self.notes.append(notes)
        logger.info(f"Completed workflow step: {self.step_id}")
    
    def fail(self, error: str):
        """Mark step as failed"""
        self.status = WorkflowStatus.FAILED
        self.notes.append(f"Failed: {error}")
        logger.error(f"Failed workflow step: {self.step_id} - {error}")
    
    def is_overdue(self) -> bool:
        """Check if step is overdue"""
        if self.started_at and self.status == WorkflowStatus.IN_PROGRESS:
            deadline = self.started_at + timedelta(hours=self.timeout_hours)
            return datetime.utcnow() > deadline
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'step_id': self.step_id,
            'step_type': self.step_type.value,
            'title': self.title,
            'description': self.description,
            'required': self.required,
            'dependencies': self.dependencies,
            'auto_execute': self.auto_execute,
            'timeout_hours': self.timeout_hours,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'assigned_to': self.assigned_to,
            'result': self.result,
            'notes': self.notes,
            'is_overdue': self.is_overdue()
        }


class ClinicalWorkflow:
    """Clinical workflow definition"""
    
    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str,
        category: str,
        steps: List[WorkflowStep]
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.category = category
        self.steps = {step.step_id: step for step in steps}
        self.status = WorkflowStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.patient_id: Optional[str] = None
        self.created_by: Optional[str] = None
    
    def get_next_steps(self) -> List[WorkflowStep]:
        """Get next executable steps"""
        completed_step_ids = [
            step_id for step_id, step in self.steps.items()
            if step.status == WorkflowStatus.COMPLETED
        ]
        
        next_steps = []
        for step in self.steps.values():
            if (step.status == WorkflowStatus.PENDING and 
                step.can_execute(completed_step_ids)):
                next_steps.append(step)
        
        return next_steps
    
    def get_progress(self) -> Dict[str, Any]:
        """Get workflow progress"""
        total_steps = len(self.steps)
        completed_steps = sum(
            1 for step in self.steps.values()
            if step.status == WorkflowStatus.COMPLETED
        )
        failed_steps = sum(
            1 for step in self.steps.values()
            if step.status == WorkflowStatus.FAILED
        )
        
        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'failed_steps': failed_steps,
            'progress_percentage': (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            'status': self.status.value
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'patient_id': self.patient_id,
            'created_by': self.created_by,
            'steps': [step.to_dict() for step in self.steps.values()],
            'progress': self.get_progress(),
            'next_steps': [step.to_dict() for step in self.get_next_steps()]
        }


class ClinicalWorkflowEngine:
    """
    Clinical Workflow Engine
    Manages automated clinical pathways and workflows
    """
    
    def __init__(self):
        self.workflows: Dict[str, ClinicalWorkflow] = {}
        self.workflow_templates: Dict[str, ClinicalWorkflow] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default workflow templates"""
        
        # Admission Workflow
        admission_steps = [
            WorkflowStep(
                "admission_001",
                WorkflowStepType.ASSESSMENT,
                "Initial Assessment",
                "Complete initial patient assessment and vital signs",
                required=True,
                timeout_hours=2
            ),
            WorkflowStep(
                "admission_002",
                WorkflowStepType.ORDER,
                "Admission Orders",
                "Enter admission orders and care plan",
                required=True,
                dependencies=["admission_001"],
                timeout_hours=4
            ),
            WorkflowStep(
                "admission_003",
                WorkflowStepType.LAB_TEST,
                "Admission Labs",
                "Order and collect admission laboratory tests",
                required=True,
                dependencies=["admission_002"],
                timeout_hours=6
            ),
            WorkflowStep(
                "admission_004",
                WorkflowStepType.MEDICATION,
                "Medication Reconciliation",
                "Complete medication reconciliation",
                required=True,
                dependencies=["admission_001"],
                timeout_hours=4
            ),
            WorkflowStep(
                "admission_005",
                WorkflowStepType.NOTIFICATION,
                "Notify Care Team",
                "Notify attending physician and care team",
                required=True,
                dependencies=["admission_002"],
                auto_execute=True,
                timeout_hours=1
            )
        ]
        
        self.workflow_templates["admission"] = ClinicalWorkflow(
            "template_admission",
            "Patient Admission",
            "Standard patient admission workflow",
            "admission",
            admission_steps
        )
        
        # Discharge Workflow
        discharge_steps = [
            WorkflowStep(
                "discharge_001",
                WorkflowStepType.ASSESSMENT,
                "Discharge Assessment",
                "Complete discharge readiness assessment",
                required=True,
                timeout_hours=4
            ),
            WorkflowStep(
                "discharge_002",
                WorkflowStepType.MEDICATION,
                "Discharge Medications",
                "Prepare discharge medication list and prescriptions",
                required=True,
                dependencies=["discharge_001"],
                timeout_hours=2
            ),
            WorkflowStep(
                "discharge_003",
                WorkflowStepType.FOLLOW_UP,
                "Follow-up Appointments",
                "Schedule follow-up appointments",
                required=True,
                dependencies=["discharge_001"],
                timeout_hours=2
            ),
            WorkflowStep(
                "discharge_004",
                WorkflowStepType.DISCHARGE,
                "Discharge Instructions",
                "Provide discharge instructions and education",
                required=True,
                dependencies=["discharge_002", "discharge_003"],
                timeout_hours=2
            ),
            WorkflowStep(
                "discharge_005",
                WorkflowStepType.NOTIFICATION,
                "Notify Primary Care",
                "Send discharge summary to primary care provider",
                required=True,
                dependencies=["discharge_004"],
                auto_execute=True,
                timeout_hours=24
            )
        ]
        
        self.workflow_templates["discharge"] = ClinicalWorkflow(
            "template_discharge",
            "Patient Discharge",
            "Standard patient discharge workflow",
            "discharge",
            discharge_steps
        )
        
        # Sepsis Protocol
        sepsis_steps = [
            WorkflowStep(
                "sepsis_001",
                WorkflowStepType.ASSESSMENT,
                "Sepsis Screening",
                "Complete sepsis screening (qSOFA, SIRS)",
                required=True,
                timeout_hours=1
            ),
            WorkflowStep(
                "sepsis_002",
                WorkflowStepType.LAB_TEST,
                "Sepsis Labs",
                "Order lactate, blood cultures, CBC, CMP",
                required=True,
                dependencies=["sepsis_001"],
                auto_execute=True,
                timeout_hours=1
            ),
            WorkflowStep(
                "sepsis_003",
                WorkflowStepType.MEDICATION,
                "Broad-Spectrum Antibiotics",
                "Administer broad-spectrum antibiotics within 1 hour",
                required=True,
                dependencies=["sepsis_002"],
                timeout_hours=1
            ),
            WorkflowStep(
                "sepsis_004",
                WorkflowStepType.ORDER,
                "Fluid Resuscitation",
                "Initiate fluid resuscitation (30 mL/kg crystalloid)",
                required=True,
                dependencies=["sepsis_001"],
                timeout_hours=3
            ),
            WorkflowStep(
                "sepsis_005",
                WorkflowStepType.CONSULTATION,
                "ICU Consultation",
                "Consult ICU if severe sepsis or septic shock",
                required=False,
                dependencies=["sepsis_003", "sepsis_004"],
                timeout_hours=2
            )
        ]
        
        self.workflow_templates["sepsis"] = ClinicalWorkflow(
            "template_sepsis",
            "Sepsis Protocol",
            "Time-critical sepsis management protocol",
            "emergency",
            sepsis_steps
        )
        
        logger.info(f"Loaded {len(self.workflow_templates)} workflow templates")
    
    def create_workflow(
        self,
        template_id: str,
        patient_id: str,
        created_by: str
    ) -> ClinicalWorkflow:
        """Create workflow from template"""
        if template_id not in self.workflow_templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self.workflow_templates[template_id]
        
        # Create new workflow instance
        workflow_id = f"{template_id}_{patient_id}_{datetime.utcnow().timestamp()}"
        
        # Deep copy steps
        new_steps = []
        for step in template.steps.values():
            new_step = WorkflowStep(
                step.step_id,
                step.step_type,
                step.title,
                step.description,
                step.required,
                step.dependencies.copy(),
                step.auto_execute,
                step.timeout_hours
            )
            new_steps.append(new_step)
        
        workflow = ClinicalWorkflow(
            workflow_id,
            template.name,
            template.description,
            template.category,
            new_steps
        )
        
        workflow.patient_id = patient_id
        workflow.created_by = created_by
        workflow.started_at = datetime.utcnow()
        workflow.status = WorkflowStatus.IN_PROGRESS
        
        self.workflows[workflow_id] = workflow
        
        logger.info(f"Created workflow: {workflow_id} for patient: {patient_id}")
        
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[ClinicalWorkflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def start_step(
        self,
        workflow_id: str,
        step_id: str,
        assigned_to: str = None
    ) -> bool:
        """Start workflow step"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        step = workflow.steps.get(step_id)
        if not step:
            return False
        
        # Check if step can be executed
        completed_step_ids = [
            sid for sid, s in workflow.steps.items()
            if s.status == WorkflowStatus.COMPLETED
        ]
        
        if not step.can_execute(completed_step_ids):
            logger.warning(f"Step {step_id} cannot be executed - dependencies not met")
            return False
        
        step.start(assigned_to)
        return True
    
    def complete_step(
        self,
        workflow_id: str,
        step_id: str,
        result: Dict[str, Any] = None,
        notes: str = None
    ) -> bool:
        """Complete workflow step"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        step = workflow.steps.get(step_id)
        if not step:
            return False
        
        step.complete(result, notes)
        
        # Check if workflow is complete
        all_required_complete = all(
            step.status == WorkflowStatus.COMPLETED
            for step in workflow.steps.values()
            if step.required
        )
        
        if all_required_complete:
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            logger.info(f"Workflow completed: {workflow_id}")
        
        return True
    
    def get_patient_workflows(self, patient_id: str) -> List[ClinicalWorkflow]:
        """Get all workflows for a patient"""
        return [
            workflow for workflow in self.workflows.values()
            if workflow.patient_id == patient_id
        ]
    
    def get_overdue_steps(self) -> List[Dict[str, Any]]:
        """Get all overdue workflow steps"""
        overdue = []
        for workflow in self.workflows.values():
            for step in workflow.steps.values():
                if step.is_overdue():
                    overdue.append({
                        'workflow_id': workflow.workflow_id,
                        'workflow_name': workflow.name,
                        'patient_id': workflow.patient_id,
                        'step': step.to_dict()
                    })
        return overdue
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        total_workflows = len(self.workflows)
        active_workflows = sum(
            1 for w in self.workflows.values()
            if w.status == WorkflowStatus.IN_PROGRESS
        )
        completed_workflows = sum(
            1 for w in self.workflows.values()
            if w.status == WorkflowStatus.COMPLETED
        )
        
        return {
            'total_workflows': total_workflows,
            'active_workflows': active_workflows,
            'completed_workflows': completed_workflows,
            'available_templates': len(self.workflow_templates),
            'overdue_steps': len(self.get_overdue_steps())
        }


# Global workflow engine instance
workflow_engine = ClinicalWorkflowEngine()