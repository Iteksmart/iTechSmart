"""
Advanced Debugging API Routes
Provides endpoints for enhanced debugging capabilities
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, DebugSession
from app.integrations.advanced_debugger import AdvancedDebugger

router = APIRouter(prefix="/api/debug", tags=["debugging"])

# Initialize debugger
debugger = AdvancedDebugger()


# Request models
class ErrorAnalysisRequest(BaseModel):
    error_message: str
    stack_trace: Optional[str] = None
    code: Optional[str] = None
    language: str = "python"


class BreakpointRequest(BaseModel):
    file_path: str
    line_number: int
    condition: Optional[str] = None


class VariableInspectionRequest(BaseModel):
    variable_name: str
    context: Dict[str, Any]


class CodeProfileRequest(BaseModel):
    code: str
    language: str = "python"


class MemoryLeakRequest(BaseModel):
    code: str
    language: str = "python"


@router.post("/analyze-error")
async def analyze_error(
    request: ErrorAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze error with AI
    
    Args:
        request: Error analysis request
        
    Returns:
        Error analysis with fix suggestions
    """
    try:
        result = await debugger.analyze_error(
            error_message=request.error_message,
            stack_trace=request.stack_trace,
            code=request.code,
            language=request.language
        )
        
        return {
            "success": True,
            "analysis": result,
            "message": "Error analyzed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-breakpoint")
async def set_breakpoint(
    request: BreakpointRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set smart breakpoint
    
    Args:
        request: Breakpoint request
        
    Returns:
        Created breakpoint
    """
    try:
        breakpoint = await debugger.set_breakpoint(
            file_path=request.file_path,
            line_number=request.line_number,
            condition=request.condition
        )
        
        # Save to database
        db_session = DebugSession(
            user_id=current_user.id,
            session_type="breakpoint",
            data={
                "breakpoint_id": breakpoint.id,
                "file_path": breakpoint.file_path,
                "line_number": breakpoint.line_number
            }
        )
        db.add(db_session)
        db.commit()
        
        return {
            "success": True,
            "breakpoint": breakpoint.to_dict(),
            "message": "Breakpoint set successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/breakpoints")
async def list_breakpoints(
    current_user: User = Depends(get_current_user)
):
    """List all breakpoints"""
    try:
        breakpoints = await debugger.list_breakpoints()
        
        return {
            "success": True,
            "breakpoints": [bp.to_dict() for bp in breakpoints],
            "count": len(breakpoints),
            "message": "Breakpoints retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/breakpoints/{breakpoint_id}")
async def remove_breakpoint(
    breakpoint_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a breakpoint"""
    try:
        success = await debugger.remove_breakpoint(breakpoint_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Breakpoint not found")
        
        return {
            "success": True,
            "message": "Breakpoint removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/breakpoints/{breakpoint_id}/toggle")
async def toggle_breakpoint(
    breakpoint_id: str,
    current_user: User = Depends(get_current_user)
):
    """Enable/disable a breakpoint"""
    try:
        success = await debugger.toggle_breakpoint(breakpoint_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Breakpoint not found")
        
        return {
            "success": True,
            "message": "Breakpoint toggled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inspect-variable")
async def inspect_variable(
    request: VariableInspectionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Inspect variable value and type
    
    Args:
        request: Variable inspection request
        
    Returns:
        Variable information
    """
    try:
        variable_info = await debugger.inspect_variable(
            variable_name=request.variable_name,
            context=request.context
        )
        
        return {
            "success": True,
            "variable": variable_info.to_dict(),
            "message": "Variable inspected successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile")
async def profile_code(
    request: CodeProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Profile code performance
    
    Args:
        request: Code profiling request
        
    Returns:
        Profiling results
    """
    try:
        profile_result = await debugger.profile_code(
            code=request.code,
            language=request.language
        )
        
        # Save to database
        db_session = DebugSession(
            user_id=current_user.id,
            session_type="profile",
            data={
                "execution_time": profile_result.execution_time,
                "memory_usage": profile_result.memory_usage,
                "cpu_usage": profile_result.cpu_usage
            }
        )
        db.add(db_session)
        db.commit()
        
        return {
            "success": True,
            "profile": profile_result.to_dict(),
            "message": "Code profiled successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/call-stack/{execution_id}")
async def get_call_stack(
    execution_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get call stack for execution"""
    try:
        call_stack = await debugger.get_call_stack(execution_id)
        
        return {
            "success": True,
            "call_stack": call_stack,
            "depth": len(call_stack),
            "message": "Call stack retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-memory-leaks")
async def detect_memory_leaks(
    request: MemoryLeakRequest,
    current_user: User = Depends(get_current_user)
):
    """Detect memory leaks in code"""
    try:
        leaks = await debugger.detect_memory_leaks(
            code=request.code,
            language=request.language
        )
        
        return {
            "success": True,
            "leaks": [leak.to_dict() for leak in leaks],
            "count": len(leaks),
            "severity_summary": {
                "critical": sum(1 for l in leaks if l.severity == "critical"),
                "high": sum(1 for l in leaks if l.severity == "high"),
                "medium": sum(1 for l in leaks if l.severity == "medium"),
                "low": sum(1 for l in leaks if l.severity == "low")
            },
            "message": "Memory leak detection completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coverage/{project_id}")
async def get_code_coverage(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get code coverage statistics"""
    try:
        coverage = await debugger.get_code_coverage(project_id)
        
        return {
            "success": True,
            "coverage": coverage,
            "message": "Coverage retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_debug_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """List recent debug sessions"""
    try:
        sessions = db.query(DebugSession)\
            .filter(DebugSession.user_id == current_user.id)\
            .order_by(DebugSession.created_at.desc())\
            .limit(limit)\
            .all()
        
        return {
            "success": True,
            "sessions": [
                {
                    "id": s.id,
                    "type": s.session_type,
                    "data": s.data,
                    "created_at": s.created_at.isoformat()
                }
                for s in sessions
            ],
            "count": len(sessions),
            "message": "Debug sessions retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))