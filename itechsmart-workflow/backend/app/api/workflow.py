"""
iTechSmart Workflow - API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ..core.workflow_engine import workflow_engine, NodeType, WorkflowStatus


router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


# Request/Response Models
class NodeConfig(BaseModel):
    id: str
    type: str
    name: str
    config: Dict[str, Any] = {}
    position: Dict[str, int] = {"x": 0, "y": 0}


class EdgeConfig(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None


class TriggerConfig(BaseModel):
    type: str  # schedule, webhook, event, manual
    config: Dict[str, Any]


class CreateWorkflowRequest(BaseModel):
    name: str
    description: str
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]
    triggers: Optional[List[TriggerConfig]] = None


class UpdateWorkflowRequest(BaseModel):
    nodes: Optional[List[NodeConfig]] = None
    edges: Optional[List[EdgeConfig]] = None
    triggers: Optional[List[TriggerConfig]] = None


class ExecuteWorkflowRequest(BaseModel):
    input_data: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    version: int


class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    input_data: Dict[str, Any]
    context: Dict[str, Any]
    current_node: Optional[str]
    completed_nodes: List[Dict[str, Any]]
    failed_nodes: List[Dict[str, Any]]
    started_at: str
    completed_at: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]


# Workflow Management Endpoints
@router.post("/", response_model=Dict[str, str])
async def create_workflow(request: CreateWorkflowRequest):
    """Create a new workflow"""
    try:
        workflow_id = workflow_engine.create_workflow(
            name=request.name,
            description=request.description,
            nodes=[node.dict() for node in request.nodes],
            edges=[edge.dict() for edge in request.edges],
            triggers=[trigger.dict() for trigger in request.triggers] if request.triggers else None
        )
        
        return {
            "workflow_id": workflow_id,
            "message": "Workflow created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """Get workflow details"""
    workflow = workflow_engine.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return WorkflowResponse(**workflow)


@router.put("/{workflow_id}")
async def update_workflow(workflow_id: str, request: UpdateWorkflowRequest):
    """Update workflow definition"""
    try:
        success = workflow_engine.update_workflow(
            workflow_id=workflow_id,
            nodes=[node.dict() for node in request.nodes] if request.nodes else None,
            edges=[edge.dict() for edge in request.edges] if request.edges else None,
            triggers=[trigger.dict() for trigger in request.triggers] if request.triggers else None
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {"message": "Workflow updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/activate")
async def activate_workflow(workflow_id: str):
    """Activate a workflow"""
    success = workflow_engine.activate_workflow(workflow_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {"message": "Workflow activated successfully"}


@router.post("/{workflow_id}/deactivate")
async def deactivate_workflow(workflow_id: str):
    """Deactivate a workflow"""
    success = workflow_engine.deactivate_workflow(workflow_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {"message": "Workflow deactivated successfully"}


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow"""
    if workflow_id in workflow_engine.workflows:
        del workflow_engine.workflows[workflow_id]
        return {"message": "Workflow deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Workflow not found")


# Workflow Execution Endpoints
@router.post("/{workflow_id}/execute", response_model=Dict[str, str])
async def execute_workflow(
    workflow_id: str,
    request: ExecuteWorkflowRequest,
    background_tasks: BackgroundTasks
):
    """Execute a workflow"""
    try:
        execution_id = await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            input_data=request.input_data,
            context=request.context
        )
        
        return {
            "execution_id": execution_id,
            "message": "Workflow execution started"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{workflow_id}/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(workflow_id: str, execution_id: str):
    """Get execution status"""
    execution = workflow_engine.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution["workflow_id"] != workflow_id:
        raise HTTPException(status_code=400, detail="Execution does not belong to this workflow")
    
    return ExecutionResponse(**execution)


@router.post("/{workflow_id}/executions/{execution_id}/cancel")
async def cancel_execution(workflow_id: str, execution_id: str):
    """Cancel a running execution"""
    success = workflow_engine.cancel_execution(execution_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Execution not found or cannot be cancelled")
    
    return {"message": "Execution cancelled successfully"}


@router.get("/{workflow_id}/executions", response_model=List[ExecutionResponse])
async def list_executions(
    workflow_id: str,
    status: Optional[str] = None,
    limit: int = 100
):
    """List workflow executions"""
    executions = workflow_engine.get_workflow_executions(
        workflow_id=workflow_id,
        status=status,
        limit=limit
    )
    
    return [ExecutionResponse(**execution) for execution in executions]


@router.get("/{workflow_id}/statistics")
async def get_workflow_statistics(workflow_id: str):
    """Get workflow execution statistics"""
    workflow = workflow_engine.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    stats = workflow_engine.get_workflow_statistics(workflow_id)
    
    return stats


# Workflow Templates
@router.get("/templates/list")
async def list_workflow_templates():
    """List available workflow templates"""
    templates = [
        {
            "id": "approval_workflow",
            "name": "Approval Workflow",
            "description": "Simple approval workflow with email notifications",
            "category": "approval",
            "nodes": [
                {"id": "start", "type": "start", "name": "Start"},
                {"id": "approval", "type": "approval", "name": "Approval Required"},
                {"id": "email", "type": "email", "name": "Send Notification"},
                {"id": "end", "type": "end", "name": "End"}
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": "approval"},
                {"id": "e2", "source": "approval", "target": "email"},
                {"id": "e3", "source": "email", "target": "end"}
            ]
        },
        {
            "id": "data_processing",
            "name": "Data Processing Workflow",
            "description": "Process data with validation and transformation",
            "category": "data",
            "nodes": [
                {"id": "start", "type": "start", "name": "Start"},
                {"id": "validate", "type": "script", "name": "Validate Data"},
                {"id": "transform", "type": "script", "name": "Transform Data"},
                {"id": "save", "type": "api_call", "name": "Save to Database"},
                {"id": "end", "type": "end", "name": "End"}
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": "validate"},
                {"id": "e2", "source": "validate", "target": "transform"},
                {"id": "e3", "source": "transform", "target": "save"},
                {"id": "e4", "source": "save", "target": "end"}
            ]
        },
        {
            "id": "notification_workflow",
            "name": "Multi-Channel Notification",
            "description": "Send notifications via email, SMS, and webhook",
            "category": "notification",
            "nodes": [
                {"id": "start", "type": "start", "name": "Start"},
                {"id": "parallel", "type": "parallel", "name": "Send in Parallel"},
                {"id": "email", "type": "email", "name": "Send Email"},
                {"id": "webhook", "type": "webhook", "name": "Send Webhook"},
                {"id": "end", "type": "end", "name": "End"}
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": "parallel"},
                {"id": "e2", "source": "parallel", "target": "email"},
                {"id": "e3", "source": "parallel", "target": "webhook"},
                {"id": "e4", "source": "email", "target": "end"},
                {"id": "e5", "source": "webhook", "target": "end"}
            ]
        }
    ]
    
    return templates


@router.post("/templates/{template_id}/create")
async def create_from_template(template_id: str, name: str, description: str):
    """Create a workflow from a template"""
    # Get template (simplified - would fetch from database in production)
    templates = await list_workflow_templates()
    template = next((t for t in templates if t["id"] == template_id), None)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    workflow_id = workflow_engine.create_workflow(
        name=name,
        description=description,
        nodes=template["nodes"],
        edges=template["edges"]
    )
    
    return {
        "workflow_id": workflow_id,
        "message": "Workflow created from template successfully"
    }


# Health Check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iTechSmart Workflow",
        "timestamp": datetime.utcnow().isoformat(),
        "workflows_count": len(workflow_engine.workflows),
        "executions_count": len(workflow_engine.executions)
    }