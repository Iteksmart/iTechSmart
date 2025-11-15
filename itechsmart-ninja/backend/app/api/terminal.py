"""
Terminal API Endpoints for iTechSmart Ninja
Provides REST API for terminal session management and command execution
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..core.terminal import (
    TerminalManager,
    TerminalSession,
    TerminalConfig,
    TerminalStatus,
    CommandExecution,
    CommandStatus,
    get_terminal_manager
)

router = APIRouter(prefix="/terminal", tags=["terminal"])


# Request/Response Models
class CreateSessionRequest(BaseModel):
    """Request to create a terminal session"""
    user_id: str = Field(..., description="User ID")
    shell: str = Field(default="/bin/bash", description="Shell to use")
    working_directory: str = Field(default="/workspace", description="Working directory")
    environment: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    timeout: int = Field(default=300, ge=10, le=3600, description="Command timeout in seconds")
    enable_history: bool = Field(default=True, description="Enable command history")


class ExecuteCommandRequest(BaseModel):
    """Request to execute a command"""
    command: str = Field(..., description="Command to execute")
    stream_output: bool = Field(default=False, description="Enable real-time output streaming")


class SessionResponse(BaseModel):
    """Response with session information"""
    session_id: str
    user_id: str
    status: str
    config: Dict[str, Any]
    created_at: str
    last_activity: str
    command_count: int
    current_directory: str
    environment: Dict[str, str]


class CommandResponse(BaseModel):
    """Response with command execution results"""
    command_id: str
    session_id: str
    command: str
    status: str
    started_at: str
    completed_at: Optional[str]
    exit_code: Optional[int]
    stdout: str
    stderr: str
    execution_time: Optional[float]


class SessionListResponse(BaseModel):
    """Response with list of sessions"""
    sessions: List[SessionResponse]
    total: int


class CommandHistoryResponse(BaseModel):
    """Response with command history"""
    commands: List[CommandResponse]
    total: int


# API Endpoints
@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    manager: TerminalManager = Depends(get_terminal_manager)
):
    """
    Create a new terminal session
    
    **Parameters:**
    - **user_id**: User ID
    - **shell**: Shell to use (default: /bin/bash)
    - **working_directory**: Initial working directory (default: /workspace)
    - **environment**: Environment variables
    - **timeout**: Command timeout in seconds (default: 300)
    - **enable_history**: Enable command history (default: true)
    
    **Returns:**
    - Terminal session information
    """
    try:
        config = TerminalConfig(
            shell=request.shell,
            working_directory=request.working_directory,
            environment=request.environment or {},
            timeout=request.timeout,
            enable_history=request.enable_history
        )
        
        session = await manager.create_session(
            user_id=request.user_id,
            config=config
        )
        
        return SessionResponse(**session.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.post("/sessions/{session_id}/execute", response_model=CommandResponse)
async def execute_command(
    session_id: str,
    request: ExecuteCommandRequest,
    manager: TerminalManager = Depends(get_terminal_manager)
):
    """
    Execute a command in a terminal session
    
    **Parameters:**
    - **session_id**: Session ID
    - **command**: Command to execute
    - **stream_output**: Enable real-time output streaming
    
    **Returns:**
    - Command execution results including stdout, stderr, and exit code
    """
    try:
        execution = await manager.execute_command(
            session_id=session_id,
            command=request.command,
            stream_output=request.stream_output
        )
        
        return CommandResponse(**execution.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    manager: TerminalManager = Depends(get_terminal_manager)
):
    """
    Get information about a terminal session
    
    **Parameters:**
    - **session_id**: Session ID
    
    **Returns:**
    - Terminal session information
    """
    session = await manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    return SessionResponse(**session.to_dict())


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    manager: TerminalManager = Depends(get_terminal_manager)
):
    """
    List all terminal sessions with optional filtering
    
    **Parameters:**
    - **user_id**: Filter by user ID
    - **status**: Filter by status (active, idle, busy, closed, error)
    
    **Returns:**
    - List of terminal sessions
    """
    try:
        status_enum = TerminalStatus(status) if status else None
        sessions = await manager.list_sessions(user_id=user_id, status=status_enum)
        
        return SessionListResponse(
            sessions=[SessionResponse(**s.to_dict()) for s in sessions],
            total=len(sessions)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.get("/sessions/{session_id}/history", response_model=CommandHistoryResponse)
async def get_command_history(
    session_id: str,
    limit: Optional[int] = None,
    manager: TerminalManager = Depends(get_terminal_manager)
):
    """
    Get command history for a session
    
    **Parameters:**
    - **session_id**: Session ID
    - **limit**: Maximum number of commands to return
    
    **Returns:**
    - List of executed commands with results
    """
    try:
        history = await manager.get_command_history(session_id, limit)
        
        return CommandHistoryResponse(
            commands=[CommandResponse(**cmd.to_dict()) for cmd in history],
            total=len(history)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.post("/sessions/{session_id}/close")
async def close_session(
    session_id: str,
    manager: TerminalManager = Depends(get_terminal_manager)
):
    """
    Close a terminal session
    
    **Parameters:**
    - **session_id**: Session ID
    
    **Returns:**
    - Success message
    """
    try:
        await manager.close_session(session_id)
        return {"message": f"Session {session_id} closed successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close session: {str(e)}")


@router.post("/commands/{command_id}/cancel")
async def cancel_command(
    command_id: str,
    manager: TerminalManager = Depends(get_terminal_manager)
):
    """
    Cancel a running command
    
    **Parameters:**
    - **command_id**: Command ID
    
    **Returns:**
    - Success message
    """
    try:
        success = await manager.cancel_command(command_id)
        
        if success:
            return {"message": f"Command {command_id} cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Command {command_id} not found or not running")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel command: {str(e)}")


@router.post("/cleanup")
async def cleanup_inactive_sessions(
    max_idle_hours: int = 24,
    manager: TerminalManager = Depends(get_terminal_manager)
):
    """
    Clean up inactive sessions
    
    **Parameters:**
    - **max_idle_hours**: Maximum idle time in hours (default: 24)
    
    **Returns:**
    - Number of sessions cleaned up
    """
    try:
        cleaned = await manager.cleanup_inactive_sessions(max_idle_hours)
        return {
            "cleaned": cleaned,
            "message": f"Cleaned up {cleaned} inactive sessions"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sessions: {str(e)}")


# WebSocket endpoint for real-time terminal interaction
@router.websocket("/ws/{session_id}")
async def websocket_terminal(
    websocket: WebSocket,
    session_id: str,
    manager: TerminalManager = Depends(get_terminal_manager)
):
    """
    WebSocket endpoint for real-time terminal interaction
    
    Allows bidirectional communication for interactive terminal sessions.
    
    **Protocol:**
    - Client sends: {"command": "ls -la"}
    - Server sends: {"type": "stdout", "data": "..."}
    - Server sends: {"type": "stderr", "data": "..."}
    - Server sends: {"type": "exit", "code": 0}
    """
    await websocket.accept()
    
    try:
        # Verify session exists
        session = await manager.get_session(session_id)
        if not session:
            await websocket.send_json({
                "type": "error",
                "message": f"Session {session_id} not found"
            })
            await websocket.close()
            return
        
        while True:
            # Receive command from client
            data = await websocket.receive_json()
            command = data.get("command")
            
            if not command:
                await websocket.send_json({
                    "type": "error",
                    "message": "No command provided"
                })
                continue
            
            # Execute command
            try:
                execution = await manager.execute_command(
                    session_id=session_id,
                    command=command,
                    stream_output=False
                )
                
                # Send stdout
                if execution.stdout:
                    await websocket.send_json({
                        "type": "stdout",
                        "data": execution.stdout
                    })
                
                # Send stderr
                if execution.stderr:
                    await websocket.send_json({
                        "type": "stderr",
                        "data": execution.stderr
                    })
                
                # Send exit code
                await websocket.send_json({
                    "type": "exit",
                    "code": execution.exit_code,
                    "execution_time": execution.execution_time
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
        finally:
            await websocket.close()


# Health check endpoint
@router.get("/health")
async def health_check(manager: TerminalManager = Depends(get_terminal_manager)):
    """
    Check terminal service health
    
    **Returns:**
    - Service status and statistics
    """
    try:
        sessions = await manager.list_sessions()
        
        status_counts = {}
        for session in sessions:
            status = session.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "status": "healthy",
            "total_sessions": len(sessions),
            "status_breakdown": status_counts,
            "active_processes": len(manager.active_processes)
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }