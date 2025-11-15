"""
Workflow API Routes
Provides endpoints for workflow management and execution
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, Workflow, WorkflowExecution as DBWorkflowExecution
from app.integrations.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

# Initialize workflow engine
workflow_engine = WorkflowEngine()


# Request models
class CreateWorkflowRequest(BaseModel):
    name: str
    description: str
    nodes: List[Dict[str, Any]]
    variables: Optional[Dict[str, Any]] = None


class UpdateWorkflowRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    variables: Optional[Dict[str, Any]] = None


class ExecuteWorkflowRequest(BaseModel):
    input_context: Optional[Dict[str, Any]] = None


class CreateFromTemplateRequest(BaseModel):
    template_id: str
    name: str
    variables: Optional[Dict[str, Any]] = None


@router.post("/create")
async def create_workflow(
    request: CreateWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new workflow
    
    Args:
        request: Workflow creation request
        
    Returns:
        Created workflow
    """
    try:
        workflow = await workflow_engine.create_workflow(
            name=request.name,
            description=request.description,
            nodes=request.nodes,
            variables=request.variables
        )
        
        # Save to database
        db_workflow = Workflow(
            user_id=current_user.id,
            workflow_id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            definition=workflow.to_dict(),
            version=workflow.version
        )
        db.add(db_workflow)
        db.commit()
        
        return {
            "success": True,
            "workflow": workflow.to_dict(),
            "message": "Workflow created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workflows for current user"""
    try:
        db_workflows = db.query(Workflow)\
            .filter(Workflow.user_id == current_user.id)\
            .order_by(Workflow.created_at.desc())\
            .all()
        
        workflows = []
        for db_wf in db_workflows:
            wf = await workflow_engine.get_workflow(db_wf.workflow_id)
            if wf:
                workflows.append(wf.to_dict())
        
        return {
            "success": True,
            "workflows": workflows,
            "count": len(workflows),
            "message": "Workflows retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workflow by ID"""
    try:
        # Check ownership
        db_workflow = db.query(Workflow)\
            .filter(
                Workflow.workflow_id == workflow_id,
                Workflow.user_id == current_user.id
            )\
            .first()
        
        if not db_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = await workflow_engine.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "success": True,
            "workflow": workflow.to_dict(),
            "message": "Workflow retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{workflow_id}")
async def update_workflow(
    workflow_id: str,
    request: UpdateWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing workflow"""
    try:
        # Check ownership
        db_workflow = db.query(Workflow)\
            .filter(
                Workflow.workflow_id == workflow_id,
                Workflow.user_id == current_user.id
            )\
            .first()
        
        if not db_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = await workflow_engine.update_workflow(
            workflow_id=workflow_id,
            name=request.name,
            description=request.description,
            nodes=request.nodes,
            variables=request.variables
        )
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update database
        if request.name:
            db_workflow.name = request.name
        if request.description:
            db_workflow.description = request.description
        db_workflow.definition = workflow.to_dict()
        db_workflow.version = workflow.version
        
        db.commit()
        
        return {
            "success": True,
            "workflow": workflow.to_dict(),
            "message": "Workflow updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow"""
    try:
        # Check ownership
        db_workflow = db.query(Workflow)\
            .filter(
                Workflow.workflow_id == workflow_id,
                Workflow.user_id == current_user.id
            )\
            .first()
        
        if not db_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Delete from engine
        success = await workflow_engine.delete_workflow(workflow_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Delete from database
        db.delete(db_workflow)
        db.commit()
        
        return {
            "success": True,
            "message": "Workflow deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    request: ExecuteWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a workflow"""
    try:
        # Check ownership
        db_workflow = db.query(Workflow)\
            .filter(
                Workflow.workflow_id == workflow_id,
                Workflow.user_id == current_user.id
            )\
            .first()
        
        if not db_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Execute workflow
        execution = await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            input_context=request.input_context
        )
        
        # Save execution to database
        db_execution = DBWorkflowExecution(
            user_id=current_user.id,
            workflow_id=workflow_id,
            execution_id=execution.id,
            status=execution.status.value,
            context=execution.context,
            logs=execution.logs,
            error=execution.error
        )
        db.add(db_execution)
        db.commit()
        
        return {
            "success": True,
            "execution": execution.to_dict(),
            "message": "Workflow executed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/history")
async def get_execution_history(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get execution history for a workflow"""
    try:
        # Check ownership
        db_workflow = db.query(Workflow)\
            .filter(
                Workflow.workflow_id == workflow_id,
                Workflow.user_id == current_user.id
            )\
            .first()
        
        if not db_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get execution history
        executions = await workflow_engine.get_execution_history(
            workflow_id=workflow_id,
            limit=limit
        )
        
        return {
            "success": True,
            "executions": [e.to_dict() for e in executions],
            "count": len(executions),
            "message": "Execution history retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/list")
async def list_templates(
    current_user: User = Depends(get_current_user)
):
    """List all workflow templates"""
    try:
        templates = await workflow_engine.get_templates()
        
        return {
            "success": True,
            "templates": [t.to_dict() for t in templates],
            "count": len(templates),
            "message": "Templates retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/create-from")
async def create_from_template(
    request: CreateFromTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a workflow from a template"""
    try:
        workflow = await workflow_engine.create_from_template(
            template_id=request.template_id,
            name=request.name,
            variables=request.variables
        )
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Save to database
        db_workflow = Workflow(
            user_id=current_user.id,
            workflow_id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            definition=workflow.to_dict(),
            version=workflow.version
        )
        db.add(db_workflow)
        db.commit()
        
        return {
            "success": True,
            "workflow": workflow.to_dict(),
            "message": "Workflow created from template successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get execution details"""
    try:
        # Check ownership
        db_execution = db.query(DBWorkflowExecution)\
            .filter(
                DBWorkflowExecution.execution_id == execution_id,
                DBWorkflowExecution.user_id == current_user.id
            )\
            .first()
        
        if not db_execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        execution = await workflow_engine.get_execution(execution_id)
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "success": True,
            "execution": execution.to_dict(),
            "message": "Execution retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/share")
async def share_workflow(
    workflow_id: str,
    share_with_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share a workflow with another user"""
    try:
        # Check ownership
        db_workflow = db.query(Workflow)\
            .filter(
                Workflow.workflow_id == workflow_id,
                Workflow.user_id == current_user.id
            )\
            .first()
        
        if not db_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Check if target user exists
        target_user = db.query(User).filter(User.id == share_with_user_id).first()
        
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # Create a copy for the target user
        workflow = await workflow_engine.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Create new workflow for target user
        new_workflow = await workflow_engine.create_workflow(
            name=f"{workflow.name} (shared)",
            description=workflow.description,
            nodes=[node.to_dict() for node in workflow.nodes],
            variables=workflow.variables
        )
        
        # Save to database
        db_new_workflow = Workflow(
            user_id=share_with_user_id,
            workflow_id=new_workflow.id,
            name=new_workflow.name,
            description=new_workflow.description,
            definition=new_workflow.to_dict(),
            version=new_workflow.version
        )
        db.add(db_new_workflow)
        db.commit()
        
        return {
            "success": True,
            "message": f"Workflow shared with user {share_with_user_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))