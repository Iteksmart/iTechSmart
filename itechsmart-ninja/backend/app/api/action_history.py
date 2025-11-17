"""
Action History and Undo/Redo API Endpoints
Provides REST API for action tracking and rollback
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field

from ..services.action_history_service import (
    action_history_service,
    ActionType,
    ActionStatus,
)

router = APIRouter(prefix="/api/action-history", tags=["action-history"])


# Request Models
class RecordActionRequest(BaseModel):
    action_type: ActionType
    description: str
    parameters: dict
    before_state: Optional[dict] = None
    can_undo: bool = True
    undo_handler: Optional[str] = None
    redo_handler: Optional[str] = None
    parent_action_id: Optional[str] = None


class CompleteActionRequest(BaseModel):
    result: dict
    after_state: Optional[dict] = None


class CreateCheckpointRequest(BaseModel):
    name: str
    description: str
    state_snapshot: dict


# Response Models
class ActionResponse(BaseModel):
    success: bool
    action: Optional[dict] = None
    error: Optional[str] = None


class CheckpointResponse(BaseModel):
    success: bool
    checkpoint: Optional[dict] = None
    error: Optional[str] = None


# Helper function to get current user
def get_current_user_id(user_id: str = Query(...)) -> str:
    """Get current authenticated user ID"""
    return user_id


# Action Recording


@router.post("/record", response_model=ActionResponse)
async def record_action(
    workspace_id: str = Query(...),
    request: RecordActionRequest = None,
    user_id: str = Query(...),
):
    """
    Record new action

    Tracks AI action for undo/redo functionality
    Optionally captures before state for rollback
    """
    result = action_history_service.record_action(
        workspace_id=workspace_id,
        user_id=user_id,
        action_type=request.action_type,
        description=request.description,
        parameters=request.parameters,
        before_state=request.before_state,
        can_undo=request.can_undo,
        undo_handler=request.undo_handler,
        redo_handler=request.redo_handler,
        parent_action_id=request.parent_action_id,
    )

    return ActionResponse(**result)


@router.post("/actions/{action_id}/complete", response_model=ActionResponse)
async def complete_action(
    action_id: str, request: CompleteActionRequest, user_id: str = Query(...)
):
    """
    Mark action as completed

    Records action result and after state
    Adds action to undo stack if undoable
    """
    result = action_history_service.complete_action(
        action_id=action_id, result=request.result, after_state=request.after_state
    )

    return ActionResponse(**result)


@router.post("/actions/{action_id}/fail")
async def fail_action(
    action_id: str, error: str = Query(...), user_id: str = Query(...)
):
    """
    Mark action as failed

    Records error message for debugging
    """
    result = action_history_service.fail_action(action_id, error)
    return result


# Undo/Redo Operations


@router.post("/undo", response_model=ActionResponse)
async def undo_action(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    Undo last action

    Reverts the most recent undoable action
    Moves action to redo stack
    """
    result = action_history_service.undo_action(workspace_id)
    return ActionResponse(**result)


@router.post("/redo", response_model=ActionResponse)
async def redo_action(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    Redo last undone action

    Re-applies the most recently undone action
    Moves action back to undo stack
    """
    result = action_history_service.redo_action(workspace_id)
    return ActionResponse(**result)


@router.post("/undo-multiple")
async def undo_multiple(
    workspace_id: str = Query(...),
    count: int = Query(..., ge=1, le=50),
    user_id: str = Query(...),
):
    """
    Undo multiple actions

    Reverts specified number of recent actions
    Stops on first error
    """
    result = action_history_service.undo_multiple(workspace_id, count)
    return result


@router.post("/redo-multiple")
async def redo_multiple(
    workspace_id: str = Query(...),
    count: int = Query(..., ge=1, le=50),
    user_id: str = Query(...),
):
    """
    Redo multiple actions

    Re-applies specified number of undone actions
    Stops on first error
    """
    result = action_history_service.redo_multiple(workspace_id, count)
    return result


# History Queries


@router.get("/history")
async def get_action_history(
    workspace_id: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
    action_type: Optional[ActionType] = None,
    user_id: str = Query(...),
):
    """
    Get action history

    Returns chronological list of actions
    Optionally filter by action type
    """
    actions = action_history_service.get_action_history(
        workspace_id=workspace_id, limit=limit, action_type=action_type
    )

    return {"success": True, "actions": actions, "count": len(actions)}


@router.get("/undo-stack")
async def get_undo_stack(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    Get undo stack

    Returns list of actions that can be undone
    """
    actions = action_history_service.get_undo_stack(workspace_id)

    return {
        "success": True,
        "actions": actions,
        "count": len(actions),
        "can_undo": len(actions) > 0,
    }


@router.get("/redo-stack")
async def get_redo_stack(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    Get redo stack

    Returns list of actions that can be redone
    """
    actions = action_history_service.get_redo_stack(workspace_id)

    return {
        "success": True,
        "actions": actions,
        "count": len(actions),
        "can_redo": len(actions) > 0,
    }


@router.get("/actions/{action_id}")
async def get_action(action_id: str, user_id: str = Query(...)):
    """
    Get action details

    Returns complete action information including snapshots
    """
    action = action_history_service.actions.get(action_id)

    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    return {"success": True, "action": action.to_dict()}


# Checkpoint Management


@router.post("/checkpoints", response_model=CheckpointResponse)
async def create_checkpoint(
    workspace_id: str = Query(...),
    request: CreateCheckpointRequest = None,
    user_id: str = Query(...),
):
    """
    Create checkpoint

    Saves current system state for rollback
    Useful before major operations
    """
    result = action_history_service.create_checkpoint(
        workspace_id=workspace_id,
        name=request.name,
        description=request.description,
        state_snapshot=request.state_snapshot,
    )

    return CheckpointResponse(**result)


@router.post("/checkpoints/{checkpoint_id}/rollback")
async def rollback_to_checkpoint(checkpoint_id: str, user_id: str = Query(...)):
    """
    Rollback to checkpoint

    Undoes all actions after checkpoint
    Restores system to checkpoint state
    """
    result = action_history_service.rollback_to_checkpoint(checkpoint_id)
    return result


@router.get("/checkpoints")
async def list_checkpoints(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    List checkpoints

    Returns all checkpoints for workspace
    """
    checkpoint_ids = action_history_service.workspace_checkpoints.get(workspace_id, [])

    checkpoints = []
    for checkpoint_id in checkpoint_ids:
        checkpoint = action_history_service.checkpoints.get(checkpoint_id)
        if checkpoint:
            checkpoints.append(checkpoint.to_dict())

    return {"success": True, "checkpoints": checkpoints, "count": len(checkpoints)}


@router.get("/checkpoints/{checkpoint_id}")
async def get_checkpoint(checkpoint_id: str, user_id: str = Query(...)):
    """
    Get checkpoint details

    Returns complete checkpoint information
    """
    checkpoint = action_history_service.checkpoints.get(checkpoint_id)

    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    return {"success": True, "checkpoint": checkpoint.to_dict()}


# Statistics


@router.get("/stats")
async def get_stats(workspace_id: str = Query(...), user_id: str = Query(...)):
    """
    Get action history statistics

    Returns metrics about actions and undo/redo usage
    """
    all_actions = list(action_history_service.workspace_actions.get(workspace_id, []))
    undo_stack = action_history_service.undo_stacks.get(workspace_id, [])
    redo_stack = action_history_service.redo_stacks.get(workspace_id, [])
    checkpoints = action_history_service.workspace_checkpoints.get(workspace_id, [])

    # Count by action type
    action_type_counts = {}
    for action_id in all_actions:
        action = action_history_service.actions.get(action_id)
        if action:
            action_type = action.action_type.value
            action_type_counts[action_type] = action_type_counts.get(action_type, 0) + 1

    # Count by status
    status_counts = {}
    for action_id in all_actions:
        action = action_history_service.actions.get(action_id)
        if action:
            status = action.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "success": True,
        "stats": {
            "total_actions": len(all_actions),
            "undoable_actions": len(undo_stack),
            "redoable_actions": len(redo_stack),
            "checkpoints": len(checkpoints),
            "action_types": action_type_counts,
            "action_status": status_counts,
            "can_undo": len(undo_stack) > 0,
            "can_redo": len(redo_stack) > 0,
        },
    }


# Action Types


@router.get("/action-types")
async def list_action_types():
    """
    List available action types

    Returns all action types that can be tracked
    """
    action_types = [
        {"value": at.value, "label": at.value.replace("_", " ").title()}
        for at in ActionType
    ]

    return {"success": True, "action_types": action_types}
