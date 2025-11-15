"""
iTechSmart Workflow - Automation Orchestrator API
Visual workflow builder and automation endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ..core.automation_orchestrator_engine import AutomationOrchestratorEngine
from ..models.automation_orchestrator import (
    NodeType, TriggerType, ActionType, WorkflowStatus
)

router = APIRouter(prefix="/automation", tags=["Automation Orchestrator"])
engine = AutomationOrchestratorEngine()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class WorkflowCreate(BaseModel):
    name: str
    description: str
    category: Optional[str] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[WorkflowStatus] = None


class NodeCreate(BaseModel):
    node_type: NodeType
    label: str
    position_x: float
    position_y: float
    config: Dict[str, Any] = {}


class EdgeCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    condition: Optional[str] = None


class WorkflowExecute(BaseModel):
    input_data: Dict[str, Any] = {}


class TriggerCreate(BaseModel):
    trigger_type: TriggerType
    name: str
    config: Dict[str, Any] = {}


class TemplateUse(BaseModel):
    name: str


# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

@router.get("/workflows")
async def get_workflows(
    status: Optional[WorkflowStatus] = Query(None),
    category: Optional[str] = Query(None)
):
    """Get workflows with filters"""
    workflows = engine.get_workflows(status=status, category=category)
    
    return {
        "total": len(workflows),
        "workflows": workflows
    }


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details"""
    if workflow_id not in engine.workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = engine.workflows[workflow_id]
    
    # Get nodes
    nodes = [
        {
            "node_id": n.node_id,
            "node_type": n.node_type.value,
            "label": n.label,
            "position_x": n.position_x,
            "position_y": n.position_y,
            "config": n.config
        }
        for n in engine.nodes.values()
        if n.workflow_id == workflow_id
    ]
    
    # Get edges
    edges = [
        {
            "edge_id": e.edge_id,
            "source_node_id": e.source_node_id,
            "target_node_id": e.target_node_id,
            "condition": e.condition
        }
        for e in engine.edges.values()
        if e.workflow_id == workflow_id
    ]
    
    # Get triggers
    triggers = [
        {
            "trigger_id": t.trigger_id,
            "trigger_type": t.trigger_type.value,
            "name": t.name,
            "is_enabled": t.is_enabled
        }
        for t in engine.triggers.values()
        if t.workflow_id == workflow_id
    ]
    
    return {
        "workflow_id": workflow.workflow_id,
        "name": workflow.name,
        "description": workflow.description,
        "status": workflow.status.value,
        "category": workflow.category,
        "version": workflow.version,
        "canvas_data": workflow.canvas_data,
        "nodes": nodes,
        "edges": edges,
        "triggers": triggers,
        "execution_count": workflow.execution_count,
        "success_count": workflow.success_count,
        "failure_count": workflow.failure_count,
        "created_at": workflow.created_at.isoformat(),
        "updated_at": workflow.updated_at.isoformat()
    }


@router.post("/workflows")
async def create_workflow(workflow: WorkflowCreate):
    """Create new workflow"""
    result = engine.create_workflow(
        name=workflow.name,
        description=workflow.description,
        user="api_user",  # Should come from auth
        category=workflow.category
    )
    
    return result


@router.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, updates: WorkflowUpdate):
    """Update workflow"""
    update_dict = updates.dict(exclude_unset=True)
    
    result = engine.update_workflow(
        workflow_id=workflow_id,
        updates=update_dict,
        user="api_user"
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/workflows/{workflow_id}/activate")
async def activate_workflow(workflow_id: str):
    """Activate workflow"""
    result = engine.activate_workflow(workflow_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete workflow"""
    if workflow_id not in engine.workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    del engine.workflows[workflow_id]
    
    return {"success": True, "workflow_id": workflow_id}


# ============================================================================
# NODE ENDPOINTS
# ============================================================================

@router.post("/workflows/{workflow_id}/nodes")
async def add_node(workflow_id: str, node: NodeCreate):
    """Add node to workflow"""
    result = engine.add_node(
        workflow_id=workflow_id,
        node_type=node.node_type,
        label=node.label,
        position_x=node.position_x,
        position_y=node.position_y,
        config=node.config
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.delete("/workflows/{workflow_id}/nodes/{node_id}")
async def remove_node(workflow_id: str, node_id: str):
    """Remove node from workflow"""
    result = engine.remove_node(workflow_id, node_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/workflows/{workflow_id}/edges")
async def connect_nodes(workflow_id: str, edge: EdgeCreate):
    """Connect two nodes"""
    result = engine.connect_nodes(
        workflow_id=workflow_id,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        condition=edge.condition
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# ============================================================================
# EXECUTION ENDPOINTS
# ============================================================================

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, execution: WorkflowExecute):
    """Execute workflow"""
    result = engine.execute_workflow(
        workflow_id=workflow_id,
        input_data=execution.input_data,
        triggered_by="manual",
        user="api_user"
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get execution status"""
    result = engine.get_execution_status(execution_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """Cancel running execution"""
    result = engine.cancel_execution(execution_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/workflows/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: str,
    limit: int = Query(50, le=500)
):
    """Get workflow execution history"""
    if workflow_id not in engine.workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    executions = [
        {
            "execution_id": e.execution_id,
            "status": e.status.value,
            "triggered_by": e.triggered_by,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            "duration_seconds": e.duration_seconds,
            "error_message": e.error_message
        }
        for e in engine.executions.values()
        if e.workflow_id == workflow_id
    ][:limit]
    
    return {
        "workflow_id": workflow_id,
        "total": len(executions),
        "executions": executions
    }


# ============================================================================
# TRIGGER ENDPOINTS
# ============================================================================

@router.post("/workflows/{workflow_id}/triggers")
async def add_trigger(workflow_id: str, trigger: TriggerCreate):
    """Add trigger to workflow"""
    result = engine.add_trigger(
        workflow_id=workflow_id,
        trigger_type=trigger.trigger_type,
        name=trigger.name,
        config=trigger.config
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/workflows/{workflow_id}/triggers")
async def get_workflow_triggers(workflow_id: str):
    """Get workflow triggers"""
    if workflow_id not in engine.workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    triggers = [
        {
            "trigger_id": t.trigger_id,
            "trigger_type": t.trigger_type.value,
            "name": t.name,
            "is_enabled": t.is_enabled,
            "config": t.config,
            "trigger_count": t.trigger_count,
            "last_triggered_at": t.last_triggered_at.isoformat() if t.last_triggered_at else None
        }
        for t in engine.triggers.values()
        if t.workflow_id == workflow_id
    ]
    
    return {
        "workflow_id": workflow_id,
        "total": len(triggers),
        "triggers": triggers
    }


# ============================================================================
# TEMPLATE ENDPOINTS
# ============================================================================

@router.get("/templates")
async def get_templates(category: Optional[str] = Query(None)):
    """Get workflow templates"""
    templates = engine.get_templates(category=category)
    
    return {
        "total": len(templates),
        "templates": templates
    }


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get template details"""
    if template_id not in engine.templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template = engine.templates[template_id]
    
    return {
        "template_id": template.template_id,
        "name": template.name,
        "description": template.description,
        "category": template.category,
        "workflow_data": template.workflow_data,
        "canvas_data": template.canvas_data,
        "use_count": template.use_count,
        "rating": template.rating
    }


@router.post("/templates/{template_id}/use")
async def create_from_template(template_id: str, data: TemplateUse):
    """Create workflow from template"""
    result = engine.create_from_template(
        template_id=template_id,
        name=data.name,
        user="api_user"
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# ============================================================================
# INTEGRATION ACTION ENDPOINTS
# ============================================================================

@router.get("/actions")
async def get_integration_actions(
    integration_name: Optional[str] = Query(None)
):
    """Get available integration actions"""
    actions = engine.get_integration_actions(integration_name=integration_name)
    
    return {
        "total": len(actions),
        "actions": actions
    }


@router.get("/actions/{action_id}")
async def get_action_details(action_id: str):
    """Get action details"""
    if action_id not in engine.integration_actions:
        raise HTTPException(status_code=404, detail="Action not found")
    
    action = engine.integration_actions[action_id]
    
    return {
        "action_id": action.action_id,
        "integration_name": action.integration_name,
        "action_name": action.action_name,
        "action_type": action.action_type.value,
        "description": action.description,
        "input_schema": action.input_schema,
        "output_schema": action.output_schema,
        "config_schema": action.config_schema,
        "requires_auth": action.requires_auth,
        "auth_type": action.auth_type
    }


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

@router.get("/metrics/dashboard")
async def get_dashboard_metrics():
    """Get dashboard metrics"""
    return engine.get_dashboard_metrics()


@router.get("/workflows/{workflow_id}/metrics")
async def get_workflow_metrics(
    workflow_id: str,
    days: int = Query(30, ge=1, le=365)
):
    """Get workflow performance metrics"""
    result = engine.get_workflow_metrics(workflow_id=workflow_id, days=days)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# ============================================================================
# NODE TYPES ENDPOINT
# ============================================================================

@router.get("/node-types")
async def get_node_types():
    """Get available node types"""
    return {
        "node_types": [
            {
                "value": nt.value,
                "label": nt.value.replace("_", " ").title(),
                "category": "trigger" if nt == NodeType.TRIGGER else "action"
            }
            for nt in NodeType
        ]
    }


@router.get("/trigger-types")
async def get_trigger_types():
    """Get available trigger types"""
    return {
        "trigger_types": [
            {
                "value": tt.value,
                "label": tt.value.replace("_", " ").title()
            }
            for tt in TriggerType
        ]
    }


@router.get("/action-types")
async def get_action_types():
    """Get available action types"""
    return {
        "action_types": [
            {
                "value": at.value,
                "label": at.value.replace("_", " ").title(),
                "category": "incident" if "incident" in at.value else
                           "deployment" if "deploy" in at.value else
                           "infrastructure" if at.value in ["restart_service", "execute_command"] else
                           "communication" if "send" in at.value else
                           "data"
            }
            for at in ActionType
        ]
    }