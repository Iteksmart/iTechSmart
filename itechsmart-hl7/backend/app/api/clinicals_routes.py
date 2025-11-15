"""
Clinical API Routes
REST API endpoints for clinical features
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.clinicals.workflow_engine import (
    workflow_engine, WorkflowStepType, ClinicalWorkflow
)
from app.clinicals.drug_checker import drug_checker
from app.clinicals.ai_insights import ai_insights, InsightType
from app.clinicals.decision_support import decision_support, GuidelineCategory
from app.clinicals.care_coordination import (
    care_coordinator, TaskPriority, CareTeamRole
)

router = APIRouter(prefix="/api/clinicals", tags=["clinicals"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class WorkflowCreateRequest(BaseModel):
    template_id: str
    patient_id: str
    created_by: str


class WorkflowStepUpdateRequest(BaseModel):
    result: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class DrugCheckRequest(BaseModel):
    new_medication: str
    current_medications: List[str]
    allergies: List[str]
    is_pregnant: bool = False
    creatinine_clearance: Optional[float] = None


class AIInsightsRequest(BaseModel):
    patient_id: str
    vital_signs: Optional[Dict[str, float]] = None
    vital_signs_history: Optional[List[Dict[str, Any]]] = None
    lab_results: Optional[Dict[str, float]] = None
    symptoms: Optional[List[str]] = None
    age: Optional[int] = None
    comorbidities: Optional[List[str]] = None
    length_of_stay: Optional[int] = None
    previous_admissions: Optional[int] = None


class TaskCreateRequest(BaseModel):
    title: str
    description: str
    priority: TaskPriority
    assigned_to: str
    assigned_role: CareTeamRole
    due_hours: int
    patient_id: str
    created_by: str


class HandoffCreateRequest(BaseModel):
    patient_id: str
    from_provider: str
    to_provider: str
    handoff_type: str
    summary: str
    action_items: List[str]
    concerns: List[str]


class TeamMemberCreateRequest(BaseModel):
    name: str
    role: CareTeamRole
    specialty: Optional[str] = None
    contact: Optional[str] = None


# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

@router.get("/workflows/templates")
async def get_workflow_templates():
    """Get available workflow templates"""
    templates = []
    for template in workflow_engine.workflow_templates.values():
        templates.append({
            'workflow_id': template.workflow_id,
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'total_steps': len(template.steps)
        })
    return {'templates': templates}


@router.post("/workflows")
async def create_workflow(request: WorkflowCreateRequest):
    """Create a new workflow from template"""
    try:
        workflow = workflow_engine.create_workflow(
            request.template_id,
            request.patient_id,
            request.created_by
        )
        return {'workflow': workflow.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details"""
    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {'workflow': workflow.to_dict()}


@router.post("/workflows/{workflow_id}/steps/{step_id}/start")
async def start_workflow_step(
    workflow_id: str,
    step_id: str,
    assigned_to: Optional[str] = None
):
    """Start a workflow step"""
    success = workflow_engine.start_step(workflow_id, step_id, assigned_to)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot start step")
    return {'message': 'Step started successfully'}


@router.post("/workflows/{workflow_id}/steps/{step_id}/complete")
async def complete_workflow_step(
    workflow_id: str,
    step_id: str,
    request: WorkflowStepUpdateRequest
):
    """Complete a workflow step"""
    success = workflow_engine.complete_step(
        workflow_id,
        step_id,
        request.result,
        request.notes
    )
    if not success:
        raise HTTPException(status_code=400, detail="Cannot complete step")
    return {'message': 'Step completed successfully'}


@router.get("/workflows/patient/{patient_id}")
async def get_patient_workflows(patient_id: str):
    """Get all workflows for a patient"""
    workflows = workflow_engine.get_patient_workflows(patient_id)
    return {
        'workflows': [w.to_dict() for w in workflows],
        'total': len(workflows)
    }


@router.get("/workflows/overdue")
async def get_overdue_steps():
    """Get all overdue workflow steps"""
    overdue = workflow_engine.get_overdue_steps()
    return {
        'overdue_steps': overdue,
        'total': len(overdue)
    }


@router.get("/workflows/statistics")
async def get_workflow_statistics():
    """Get workflow statistics"""
    return workflow_engine.get_statistics()


# ============================================================================
# DRUG INTERACTION ENDPOINTS
# ============================================================================

@router.post("/drug-check")
async def check_drug_interactions(request: DrugCheckRequest):
    """Comprehensive drug interaction check"""
    result = drug_checker.comprehensive_check(
        request.new_medication,
        request.current_medications,
        request.allergies,
        request.is_pregnant,
        request.creatinine_clearance
    )
    return result


@router.post("/drug-check/drug-drug")
async def check_drug_drug_interactions(medications: List[str]):
    """Check for drug-drug interactions"""
    interactions = drug_checker.check_drug_drug_interactions(medications)
    return {
        'interactions': [i.to_dict() for i in interactions],
        'total': len(interactions)
    }


@router.post("/drug-check/drug-allergy")
async def check_drug_allergy(medication: str, allergies: List[str]):
    """Check for drug-allergy interactions"""
    interactions = drug_checker.check_drug_allergy_interactions(medication, allergies)
    return {
        'interactions': [i.to_dict() for i in interactions],
        'total': len(interactions)
    }


@router.post("/drug-check/duplicate-therapy")
async def check_duplicate_therapy(medications: List[str]):
    """Check for duplicate therapy"""
    interactions = drug_checker.check_duplicate_therapy(medications)
    return {
        'interactions': [i.to_dict() for i in interactions],
        'total': len(interactions)
    }


# ============================================================================
# AI INSIGHTS ENDPOINTS
# ============================================================================

@router.post("/ai-insights/sepsis-risk")
async def predict_sepsis_risk(request: AIInsightsRequest):
    """Predict sepsis risk"""
    if not request.vital_signs or not request.lab_results:
        raise HTTPException(status_code=400, detail="Vital signs and lab results required")
    
    insight = ai_insights.predict_sepsis_risk(
        request.patient_id,
        request.vital_signs,
        request.lab_results
    )
    return {'insight': insight.to_dict()}


@router.post("/ai-insights/readmission-risk")
async def predict_readmission_risk(request: AIInsightsRequest):
    """Predict 30-day readmission risk"""
    if not all([request.age, request.comorbidities, request.length_of_stay, request.previous_admissions]):
        raise HTTPException(status_code=400, detail="Age, comorbidities, length of stay, and previous admissions required")
    
    insight = ai_insights.predict_readmission_risk(
        request.patient_id,
        request.age,
        request.comorbidities,
        request.length_of_stay,
        request.previous_admissions
    )
    return {'insight': insight.to_dict()}


@router.post("/ai-insights/deterioration")
async def detect_deterioration(request: AIInsightsRequest):
    """Detect patient deterioration"""
    if not request.vital_signs_history:
        raise HTTPException(status_code=400, detail="Vital signs history required")
    
    insight = ai_insights.detect_deterioration(
        request.patient_id,
        request.vital_signs_history
    )
    
    if not insight:
        return {'message': 'No deterioration detected'}
    
    return {'insight': insight.to_dict()}


@router.post("/ai-insights/diagnosis")
async def suggest_diagnosis(request: AIInsightsRequest):
    """Suggest possible diagnoses"""
    if not all([request.symptoms, request.vital_signs, request.lab_results]):
        raise HTTPException(status_code=400, detail="Symptoms, vital signs, and lab results required")
    
    insights = ai_insights.suggest_diagnosis(
        request.patient_id,
        request.symptoms,
        request.vital_signs,
        request.lab_results
    )
    return {
        'insights': [i.to_dict() for i in insights],
        'total': len(insights)
    }


@router.get("/ai-insights/statistics")
async def get_ai_statistics():
    """Get AI insights statistics"""
    return ai_insights.get_statistics()


# ============================================================================
# CLINICAL DECISION SUPPORT ENDPOINTS
# ============================================================================

@router.get("/decision-support/categories")
async def get_guideline_categories():
    """Get all guideline categories"""
    return {'categories': decision_support.get_all_categories()}


@router.get("/decision-support/guidelines/{category}")
async def get_guidelines(category: str):
    """Get guidelines for a category"""
    try:
        cat = GuidelineCategory(category)
        recommendations = decision_support.get_recommendations(cat)
        return {
            'category': category,
            'recommendations': [r.to_dict() for r in recommendations],
            'total': len(recommendations)
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Category not found")


@router.get("/decision-support/search")
async def search_guidelines(query: str):
    """Search guidelines by keyword"""
    results = decision_support.search_guidelines(query)
    return {
        'query': query,
        'results': [r.to_dict() for r in results],
        'total': len(results)
    }


@router.get("/decision-support/statistics")
async def get_decision_support_statistics():
    """Get decision support statistics"""
    return decision_support.get_statistics()


# ============================================================================
# CARE COORDINATION ENDPOINTS
# ============================================================================

@router.post("/care-coordination/tasks")
async def create_task(request: TaskCreateRequest):
    """Create a new care task"""
    task = care_coordinator.create_task(
        request.title,
        request.description,
        request.priority,
        request.assigned_to,
        request.assigned_role,
        request.due_hours,
        request.patient_id,
        request.created_by
    )
    return {'task': task.to_dict()}


@router.get("/care-coordination/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task details"""
    task = care_coordinator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {'task': task.to_dict()}


@router.post("/care-coordination/tasks/{task_id}/complete")
async def complete_task(task_id: str, notes: Optional[str] = None):
    """Complete a task"""
    success = care_coordinator.complete_task(task_id, notes)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {'message': 'Task completed successfully'}


@router.get("/care-coordination/tasks/patient/{patient_id}")
async def get_patient_tasks(patient_id: str):
    """Get all tasks for a patient"""
    tasks = care_coordinator.get_tasks_by_patient(patient_id)
    return {
        'tasks': [t.to_dict() for t in tasks],
        'total': len(tasks)
    }


@router.get("/care-coordination/tasks/assignee/{assignee}")
async def get_assignee_tasks(assignee: str):
    """Get all tasks assigned to a user"""
    tasks = care_coordinator.get_tasks_by_assignee(assignee)
    return {
        'tasks': [t.to_dict() for t in tasks],
        'total': len(tasks)
    }


@router.get("/care-coordination/tasks/overdue")
async def get_overdue_tasks():
    """Get all overdue tasks"""
    tasks = care_coordinator.get_overdue_tasks()
    return {
        'tasks': [t.to_dict() for t in tasks],
        'total': len(tasks)
    }


@router.post("/care-coordination/team-members")
async def add_team_member(request: TeamMemberCreateRequest):
    """Add a care team member"""
    member = care_coordinator.add_team_member(
        request.name,
        request.role,
        request.specialty,
        request.contact
    )
    return {'member': member.to_dict()}


@router.post("/care-coordination/team-members/{member_id}/assign/{patient_id}")
async def assign_to_patient(member_id: str, patient_id: str):
    """Assign team member to patient"""
    success = care_coordinator.assign_to_patient(patient_id, member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team member not found")
    return {'message': 'Team member assigned successfully'}


@router.get("/care-coordination/team/patient/{patient_id}")
async def get_patient_team(patient_id: str):
    """Get care team for a patient"""
    team = care_coordinator.get_patient_team(patient_id)
    return {
        'team': [m.to_dict() for m in team],
        'total': len(team)
    }


@router.post("/care-coordination/handoffs")
async def create_handoff(request: HandoffCreateRequest):
    """Create a patient handoff"""
    handoff = care_coordinator.create_handoff(
        request.patient_id,
        request.from_provider,
        request.to_provider,
        request.handoff_type,
        request.summary,
        request.action_items,
        request.concerns
    )
    return {'handoff': handoff.to_dict()}


@router.post("/care-coordination/handoffs/{handoff_id}/acknowledge")
async def acknowledge_handoff(handoff_id: str):
    """Acknowledge receipt of handoff"""
    success = care_coordinator.acknowledge_handoff(handoff_id)
    if not success:
        raise HTTPException(status_code=404, detail="Handoff not found")
    return {'message': 'Handoff acknowledged successfully'}


@router.get("/care-coordination/handoffs/pending/{provider}")
async def get_pending_handoffs(provider: str):
    """Get pending handoffs for a provider"""
    handoffs = care_coordinator.get_pending_handoffs(provider)
    return {
        'handoffs': [h.to_dict() for h in handoffs],
        'total': len(handoffs)
    }


@router.get("/care-coordination/handoffs/report/{patient_id}")
async def generate_handoff_report(patient_id: str, provider: str):
    """Generate standardized handoff report"""
    report = care_coordinator.generate_handoff_report(patient_id, provider)
    return report


@router.get("/care-coordination/statistics")
async def get_care_coordination_statistics():
    """Get care coordination statistics"""
    return care_coordinator.get_statistics()