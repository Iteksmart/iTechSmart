"""
Action History API Routes
Provides undo/redo capabilities for user actions
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..database import get_db
from ..models.database import ActionHistory, User
from ..integrations.action_history import action_history_manager, ActionType
from ..auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])
logger = logging.getLogger(__name__)


# Request/Response Models
from pydantic import BaseModel


class AddActionRequest(BaseModel):
    action_type: str
    description: str
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    undoable: bool = True


class UndoMultipleRequest(BaseModel):
    count: int


class SearchRequest(BaseModel):
    query: str
    limit: int = 50


class BookmarkRequest(BaseModel):
    action_id: str


@router.post("/actions")
async def add_action(
    request: AddActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new action to history
    
    Example:
    ```json
    {
        "action_type": "file_modification",
        "description": "Modified main.py",
        "previous_state": {"content": "old content"},
        "new_state": {"content": "new content"},
        "metadata": {"file_path": "/path/to/main.py"},
        "undoable": true
    }
    ```
    """
    try:
        # Validate action type
        try:
            action_type = ActionType(request.action_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action type. Supported: {[t.value for t in ActionType]}"
            )
            
        # Add to in-memory manager
        action_id = action_history_manager.add_action(
            action_type=action_type,
            description=request.description,
            previous_state=request.previous_state,
            new_state=request.new_state,
            metadata=request.metadata,
            undoable=request.undoable
        )
        
        # Save to database
        db_action = ActionHistory(
            user_id=current_user.id,
            action_id=action_id,
            action_type=request.action_type,
            description=request.description,
            previous_state=request.previous_state,
            new_state=request.new_state,
            metadata=request.metadata,
            undoable=request.undoable,
            undone=False,
            created_at=datetime.utcnow()
        )
        
        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        
        return {
            "success": True,
            "action_id": action_id,
            "message": f"Action '{request.description}' added to history"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions")
async def get_actions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    action_type: Optional[str] = None,
    include_undone: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Get action history"""
    try:
        # Convert action_type string to enum if provided
        action_type_enum = None
        if action_type:
            try:
                action_type_enum = ActionType(action_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action type: {action_type}"
                )
                
        # Get from in-memory manager
        actions = action_history_manager.get_history(
            limit=limit,
            offset=offset,
            action_type=action_type_enum,
            include_undone=include_undone
        )
        
        return {
            "success": True,
            "actions": actions,
            "total": len(action_history_manager.actions),
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions/{action_id}")
async def get_action(
    action_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific action by ID"""
    try:
        action = action_history_manager.get_action(action_id)
        
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
            
        return {
            "success": True,
            "action": action
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/undo")
async def undo_action(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Undo the last action"""
    try:
        result = await action_history_manager.undo()
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
            
        # Update database
        action_id = result["action"]["action_id"]
        db_action = db.query(ActionHistory).filter(
            ActionHistory.action_id == action_id,
            ActionHistory.user_id == current_user.id
        ).first()
        
        if db_action:
            db_action.undone = True
            db.commit()
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to undo action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redo")
async def redo_action(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Redo the last undone action"""
    try:
        result = await action_history_manager.redo()
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
            
        # Update database
        action_id = result["action"]["action_id"]
        db_action = db.query(ActionHistory).filter(
            ActionHistory.action_id == action_id,
            ActionHistory.user_id == current_user.id
        ).first()
        
        if db_action:
            db_action.undone = False
            db.commit()
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to redo action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/undo-batch")
async def undo_multiple(
    request: UndoMultipleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Undo multiple actions
    
    Example:
    ```json
    {
        "count": 5
    }
    ```
    """
    try:
        if request.count <= 0:
            raise HTTPException(status_code=400, detail="Count must be positive")
            
        result = await action_history_manager.undo_multiple(request.count)
        
        # Update database for all undone actions
        for action_data in result.get("actions", []):
            action_id = action_data["action_id"]
            db_action = db.query(ActionHistory).filter(
                ActionHistory.action_id == action_id,
                ActionHistory.user_id == current_user.id
            ).first()
            
            if db_action:
                db_action.undone = True
                
        db.commit()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to undo multiple actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redo-batch")
async def redo_multiple(
    request: UndoMultipleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Redo multiple actions
    
    Example:
    ```json
    {
        "count": 3
    }
    ```
    """
    try:
        if request.count <= 0:
            raise HTTPException(status_code=400, detail="Count must be positive")
            
        result = await action_history_manager.redo_multiple(request.count)
        
        # Update database for all redone actions
        for action_data in result.get("actions", []):
            action_id = action_data["action_id"]
            db_action = db.query(ActionHistory).filter(
                ActionHistory.action_id == action_id,
                ActionHistory.user_id == current_user.id
            ).first()
            
            if db_action:
                db_action.undone = False
                
        db.commit()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to redo multiple actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_history(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search action history
    
    Example:
    ```json
    {
        "query": "file modification",
        "limit": 50
    }
    ```
    """
    try:
        actions = action_history_manager.search_history(
            query=request.query,
            limit=request.limit
        )
        
        return {
            "success": True,
            "query": request.query,
            "results": actions,
            "count": len(actions)
        }
        
    except Exception as e:
        logger.error(f"Failed to search history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bookmark")
async def bookmark_action(
    request: BookmarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bookmark an action
    
    Example:
    ```json
    {
        "action_id": "action_abc123"
    }
    ```
    """
    try:
        result = action_history_manager.bookmark_action(request.action_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
            
        # Update database
        db_action = db.query(ActionHistory).filter(
            ActionHistory.action_id == request.action_id,
            ActionHistory.user_id == current_user.id
        ).first()
        
        if db_action:
            db_action.bookmarked = True
            db.commit()
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to bookmark action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bookmark/{action_id}")
async def unbookmark_action(
    action_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove bookmark from action"""
    try:
        result = action_history_manager.unbookmark_action(action_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
            
        # Update database
        db_action = db.query(ActionHistory).filter(
            ActionHistory.action_id == action_id,
            ActionHistory.user_id == current_user.id
        ).first()
        
        if db_action:
            db_action.bookmarked = False
            db.commit()
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unbookmark action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookmarks")
async def get_bookmarked_actions(
    current_user: User = Depends(get_current_user)
):
    """Get all bookmarked actions"""
    try:
        actions = action_history_manager.get_bookmarked_actions()
        
        return {
            "success": True,
            "bookmarks": actions,
            "count": len(actions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get bookmarked actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_history(
    keep_bookmarked: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear action history"""
    try:
        result = action_history_manager.clear_history(keep_bookmarked=keep_bookmarked)
        
        # Clear database
        if keep_bookmarked:
            db.query(ActionHistory).filter(
                ActionHistory.user_id == current_user.id,
                ActionHistory.bookmarked == False
            ).delete()
        else:
            db.query(ActionHistory).filter(
                ActionHistory.user_id == current_user.id
            ).delete()
            
        db.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(
    current_user: User = Depends(get_current_user)
):
    """Get action history statistics"""
    try:
        stats = action_history_manager.get_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_history(
    format: str = Query("json", regex="^(json|csv)$"),
    include_undone: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Export action history"""
    try:
        exported_data = action_history_manager.export_history(
            format=format,
            include_undone=include_undone
        )
        
        # Set appropriate content type
        media_type = "application/json" if format == "json" else "text/csv"
        filename = f"action_history.{format}"
        
        from fastapi.responses import Response
        return Response(
            content=exported_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to export history: {e}")
        raise HTTPException(status_code=500, detail=str(e))