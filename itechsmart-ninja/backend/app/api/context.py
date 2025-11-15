"""
Context Memory API Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.core.context_memory import context_manager, ContextType, MemoryPriority

router = APIRouter(prefix="/api/v1/context", tags=["Context Memory"])


class ContextAddRequest(BaseModel):
    """Add context request"""
    session_id: str
    content: Any
    context_type: str = "conversation"
    priority: str = "normal"
    metadata: Dict[str, Any] = {}
    tags: List[str] = []


class ContextSearchRequest(BaseModel):
    """Search context request"""
    session_id: str
    query: str
    context_type: Optional[str] = None
    limit: int = 10


@router.post("/add")
async def add_context(request: ContextAddRequest) -> Dict[str, Any]:
    """
    Add entry to context memory
    
    Example:
    ```json
    {
        "session_id": "user-123",
        "content": "User asked about Python decorators",
        "context_type": "conversation",
        "tags": ["python", "decorators"]
    }
    ```
    """
    try:
        # Get session
        memory = context_manager.get_session(request.session_id)
        
        # Map types
        context_type = ContextType(request.context_type)
        priority = MemoryPriority[request.priority.upper()]
        
        # Add to memory
        entry_id = memory.add(
            content=request.content,
            context_type=context_type,
            priority=priority,
            metadata=request.metadata,
            tags=request.tags
        )
        
        return {
            "success": True,
            "entry_id": entry_id,
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/recent")
async def get_recent(
    session_id: str,
    limit: int = 10,
    context_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recent context entries
    
    Args:
        session_id: Session ID
        limit: Maximum entries to return
        context_type: Filter by context type
    """
    try:
        memory = context_manager.get_session(session_id)
        
        ct = ContextType(context_type) if context_type else None
        entries = memory.get_recent(limit=limit, context_type=ct)
        
        return {
            "success": True,
            "session_id": session_id,
            "entries": [e.to_dict() for e in entries],
            "count": len(entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/conversation")
async def get_conversation_history(
    session_id: str,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """Get conversation history for session"""
    try:
        memory = context_manager.get_session(session_id)
        entries = memory.get_conversation_history(limit=limit)
        
        return {
            "success": True,
            "session_id": session_id,
            "conversation": [e.to_dict() for e in entries],
            "count": len(entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/tasks")
async def get_task_history(
    session_id: str,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """Get task history for session"""
    try:
        memory = context_manager.get_session(session_id)
        entries = memory.get_task_history(limit=limit)
        
        return {
            "success": True,
            "session_id": session_id,
            "tasks": [e.to_dict() for e in entries],
            "count": len(entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_context(request: ContextSearchRequest) -> Dict[str, Any]:
    """
    Search context memory
    
    Example:
    ```json
    {
        "session_id": "user-123",
        "query": "Python decorators",
        "context_type": "conversation",
        "limit": 10
    }
    ```
    """
    try:
        memory = context_manager.get_session(request.session_id)
        
        ct = ContextType(request.context_type) if request.context_type else None
        results = memory.search(
            query=request.query,
            context_type=ct,
            limit=request.limit
        )
        
        return {
            "success": True,
            "session_id": request.session_id,
            "query": request.query,
            "results": [e.to_dict() for e in results],
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/window")
async def get_context_window(
    session_id: str,
    max_tokens: int = 8000,
    context_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get context window within token limit
    
    Useful for preparing context for AI models with token limits
    """
    try:
        memory = context_manager.get_session(session_id)
        
        ct = ContextType(context_type) if context_type else None
        window = memory.get_context_window(
            max_tokens=max_tokens,
            context_type=ct
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "max_tokens": max_tokens,
            "entries": [e.to_dict() for e in window],
            "count": len(window)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/summary")
async def get_summary(session_id: str) -> Dict[str, Any]:
    """Get context memory summary"""
    try:
        memory = context_manager.get_session(session_id)
        summary = memory.summarize_context()
        
        return {
            "success": True,
            **summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}/clear")
async def clear_context(
    session_id: str,
    context_type: Optional[str] = None
) -> Dict[str, Any]:
    """Clear context memory"""
    try:
        memory = context_manager.get_session(session_id)
        
        ct = ContextType(context_type) if context_type else None
        memory.clear(context_type=ct)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Context cleared successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/export")
async def export_context(session_id: str) -> Dict[str, Any]:
    """Export context memory"""
    try:
        memory = context_manager.get_session(session_id)
        data = memory.export()
        
        return {
            "success": True,
            **data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/import")
async def import_context(session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Import context memory"""
    try:
        memory = context_manager.get_session(session_id)
        memory.import_data(data)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Context imported successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions() -> Dict[str, Any]:
    """List all active sessions"""
    sessions = context_manager.get_all_sessions()
    
    return {
        "success": True,
        "sessions": sessions,
        "count": len(sessions)
    }


@router.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """Get overall context memory statistics"""
    stats = context_manager.get_statistics()
    
    return {
        "success": True,
        **stats
    }