"""
Workflow Automation API Endpoints for iTechSmart Ninja
Provides REST API for workflow creation and execution
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..core.workflow_engine import (
    WorkflowEngine,
    Workflow,
    WorkflowExecution,
    WorkflowTrigger,
    WorkflowAction,
    WorkflowStatus,
    TriggerType,
    ActionType,
    get_workflow_engine
)

router = APIRouter(prefix="/workflow-automation", tags=["workflow-automation"])


# Request/Response Models
class WorkflowTriggerRequest(BaseModel):
    """Request for workflow trigger"""
    trigger_type: str = Field(..., description="Trigger type")
    config: Dict[str, Any] = Field(..., description="Trigger configuration")
    enabled: bool = Field(default=True, description="Enable trigger")


class WorkflowActionRequest(BaseModel):
    """Request for workflow action"""
    action_id: str = Field(..., description="Action ID")
    action_type: str = Field(..., description="Action type")
    name: str = Field(..., description="Action name")
    config: Dict[str, Any] = Field(..., description="Action configuration")
    next_action: Optional[str] = Field(default=None, description="Next action ID")
    on_error: Optional[str] = Field(default=None, description="Error handler action ID")


class CreateWorkflowRequest(BaseModel):
    """Request to create a workflow"""
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    trigger: WorkflowTriggerRequest = Field(..., description="Workflow trigger")
    actions: List[WorkflowActionRequest] = Field(..., description="Workflow actions")
    created_by: str = Field(..., description="User ID")
    tags: Optional[List[str]] = Field(default=None, description="Tags")


class ExecuteWorkflowRequest(BaseModel):
    """Request to execute a workflow"""
    trigger_data: Optional[Dict[str, Any]] = Field(default=None, description="Trigger data")


class WorkflowResponse(BaseModel):
    """Response with workflow information"""
    workflow_id: str
    name: str
    description: str
    trigger: Dict[str, Any]
    actions: List[Dict[str, Any]]
    status: str
    created_by: str
    created_at: str
    updated_at: str
    version: int
    tags: List[str]


class WorkflowExecutionResponse(BaseModel):
    """Response with workflow execution information"""
    execution_id: str
    workflow_id: str
    status: str
    started_at: str
    completed_at: Optional[str]
    trigger_data: Dict[str, Any]
    execution_log: List[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]


class WorkflowListResponse(BaseModel):
    """Response with list of workflows"""
    workflows: List[WorkflowResponse]
    total: int


class ExecutionListResponse(BaseModel):
    """Response with list of executions"""
    executions: List[WorkflowExecutionResponse]
    total: int


# API Endpoints
@router.post("/create", response_model=WorkflowResponse)
async def create_workflow(
    request: CreateWorkflowRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Create a new workflow
    
    **Trigger Types:** manual, scheduled, event, webhook, api
    **Action Types:** http_request, run_code, send_email, send_notification, create_file, 
                     transform_data, conditional, loop, delay, ai_task
    """
    try:
        trigger = WorkflowTrigger(
            trigger_type=TriggerType(request.trigger.trigger_type),
            config=request.trigger.config,
            enabled=request.trigger.enabled
        )
        
        actions = [
            WorkflowAction(
                action_id=action.action_id,
                action_type=ActionType(action.action_type),
                name=action.name,
                config=action.config,
                next_action=action.next_action,
                on_error=action.on_error
            )
            for action in request.actions
        ]
        
        workflow = await engine.create_workflow(
            name=request.name,
            description=request.description,
            trigger=trigger,
            actions=actions,
            created_by=request.created_by,
            tags=request.tags
        )
        
        return WorkflowResponse(**workflow.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")


@router.post("/{workflow_id}/activate", response_model=WorkflowResponse)
async def activate_workflow(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Activate a workflow"""
    try:
        workflow = await engine.activate_workflow(workflow_id)
        return WorkflowResponse(**workflow.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate workflow: {str(e)}")


@router.post("/{workflow_id}/pause", response_model=WorkflowResponse)
async def pause_workflow(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Pause a workflow"""
    try:
        workflow = await engine.pause_workflow(workflow_id)
        return WorkflowResponse(**workflow.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause workflow: {str(e)}")


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    request: ExecuteWorkflowRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Execute a workflow"""
    try:
        execution = await engine.execute_workflow(
            workflow_id=workflow_id,
            trigger_data=request.trigger_data
        )
        return WorkflowExecutionResponse(**execution.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute workflow: {str(e)}")


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Get workflow information"""
    workflow = await engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    return WorkflowResponse(**workflow.to_dict())


@router.get("/list/all", response_model=WorkflowListResponse)
async def list_workflows(
    created_by: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[str] = None,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """List all workflows with optional filtering"""
    try:
        status_enum = WorkflowStatus(status) if status else None
        tag_list = tags.split(",") if tags else None
        
        workflows = await engine.list_workflows(
            created_by=created_by,
            status=status_enum,
            tags=tag_list
        )
        
        return WorkflowListResponse(
            workflows=[WorkflowResponse(**w.to_dict()) for w in workflows],
            total=len(workflows)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_execution(
    execution_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Get workflow execution information"""
    execution = await engine.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    return WorkflowExecutionResponse(**execution.to_dict())


@router.get("/executions/list/all", response_model=ExecutionListResponse)
async def list_executions(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """List workflow executions with optional filtering"""
    try:
        status_enum = WorkflowStatus(status) if status else None
        executions = await engine.list_executions(workflow_id=workflow_id, status=status_enum)
        
        return ExecutionListResponse(
            executions=[WorkflowExecutionResponse(**e.to_dict()) for e in executions],
            total=len(executions)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list executions: {str(e)}")


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Delete a workflow"""
    try:
        success = await engine.delete_workflow(workflow_id)
        if success:
            return {"message": f"Workflow {workflow_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")


@router.get("/health")
async def health_check(engine: WorkflowEngine = Depends(get_workflow_engine)):
    """Check workflow service health"""
    try:
        workflows = await engine.list_workflows()
        executions = await engine.list_executions()
        
        status_counts = {}
        for workflow in workflows:
            status = workflow.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "status": "healthy",
            "total_workflows": len(workflows),
            "total_executions": len(executions),
            "workflow_status_breakdown": status_counts,
            "supported_trigger_types": [t.value for t in TriggerType],
            "supported_action_types": [a.value for a in ActionType]
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}