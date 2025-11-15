"""
Sandbox API Endpoints for iTechSmart Ninja
Provides REST API for sandbox management and code execution
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from ..core.sandbox import (
    SandboxManager,
    SandboxConfig,
    SandboxInfo,
    SandboxStatus,
    SandboxLanguage,
    ExecutionResult,
    get_sandbox_manager
)

router = APIRouter(prefix="/sandbox", tags=["sandbox"])


# Request/Response Models
class CreateSandboxRequest(BaseModel):
    """Request to create a new sandbox"""
    language: SandboxLanguage
    memory_limit: str = Field(default="512m", description="Memory limit (e.g., '512m', '1g')")
    cpu_limit: float = Field(default=1.0, ge=0.1, le=4.0, description="CPU cores")
    timeout: int = Field(default=300, ge=10, le=3600, description="Timeout in seconds")
    network_enabled: bool = Field(default=False, description="Enable network access")
    environment_vars: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")


class ExecuteCodeRequest(BaseModel):
    """Request to execute code in a sandbox"""
    code: str = Field(..., description="Code to execute")
    filename: Optional[str] = Field(default=None, description="Optional filename")


class SandboxResponse(BaseModel):
    """Response with sandbox information"""
    sandbox_id: str
    language: str
    status: str
    container_id: Optional[str]
    created_at: str
    started_at: Optional[str]
    stopped_at: Optional[str]
    config: Dict[str, Any]
    error_message: Optional[str] = None


class ExecutionResponse(BaseModel):
    """Response with execution results"""
    sandbox_id: str
    success: bool
    output: str
    error: Optional[str]
    exit_code: int
    execution_time: float
    memory_used: Optional[int]
    cpu_used: Optional[float]


class SandboxListResponse(BaseModel):
    """Response with list of sandboxes"""
    sandboxes: List[SandboxResponse]
    total: int


class CleanupResponse(BaseModel):
    """Response for cleanup operation"""
    cleaned: int
    message: str


# API Endpoints
@router.post("/create", response_model=SandboxResponse)
async def create_sandbox(
    request: CreateSandboxRequest,
    manager: SandboxManager = Depends(get_sandbox_manager)
):
    """
    Create a new sandbox environment
    
    Creates an isolated Docker container for secure code execution.
    
    **Parameters:**
    - **language**: Programming language (python, javascript, java, etc.)
    - **memory_limit**: Memory limit (default: 512m)
    - **cpu_limit**: CPU cores (default: 1.0)
    - **timeout**: Execution timeout in seconds (default: 300)
    - **network_enabled**: Enable network access (default: false)
    - **environment_vars**: Optional environment variables
    
    **Returns:**
    - Sandbox information including ID and status
    """
    try:
        config = SandboxConfig(
            language=request.language,
            memory_limit=request.memory_limit,
            cpu_limit=request.cpu_limit,
            timeout=request.timeout,
            network_enabled=request.network_enabled,
            environment_vars=request.environment_vars or {}
        )
        
        sandbox_info = await manager.create_sandbox(
            language=request.language,
            config=config
        )
        
        return SandboxResponse(**sandbox_info.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sandbox: {str(e)}")


@router.post("/{sandbox_id}/execute", response_model=ExecutionResponse)
async def execute_code(
    sandbox_id: str,
    request: ExecuteCodeRequest,
    manager: SandboxManager = Depends(get_sandbox_manager)
):
    """
    Execute code in a sandbox
    
    Runs the provided code in an isolated sandbox environment.
    
    **Parameters:**
    - **sandbox_id**: ID of the sandbox
    - **code**: Code to execute
    - **filename**: Optional filename for the code
    
    **Returns:**
    - Execution results including output, errors, and resource usage
    """
    try:
        result = await manager.execute_code(
            sandbox_id=sandbox_id,
            code=request.code,
            filename=request.filename
        )
        
        return ExecutionResponse(
            sandbox_id=result.sandbox_id,
            success=result.success,
            output=result.output,
            error=result.error,
            exit_code=result.exit_code,
            execution_time=result.execution_time,
            memory_used=result.memory_used,
            cpu_used=result.cpu_used
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute code: {str(e)}")


@router.get("/{sandbox_id}", response_model=SandboxResponse)
async def get_sandbox(
    sandbox_id: str,
    manager: SandboxManager = Depends(get_sandbox_manager)
):
    """
    Get information about a sandbox
    
    **Parameters:**
    - **sandbox_id**: ID of the sandbox
    
    **Returns:**
    - Sandbox information including status and configuration
    """
    sandbox_info = await manager.get_sandbox_info(sandbox_id)
    
    if not sandbox_info:
        raise HTTPException(status_code=404, detail=f"Sandbox {sandbox_id} not found")
    
    return SandboxResponse(**sandbox_info.to_dict())


@router.get("/", response_model=SandboxListResponse)
async def list_sandboxes(
    status: Optional[SandboxStatus] = None,
    language: Optional[SandboxLanguage] = None,
    manager: SandboxManager = Depends(get_sandbox_manager)
):
    """
    List all sandboxes with optional filtering
    
    **Parameters:**
    - **status**: Filter by status (creating, ready, running, stopped, error, terminated)
    - **language**: Filter by language
    
    **Returns:**
    - List of sandboxes matching the filters
    """
    try:
        sandboxes = await manager.list_sandboxes(status=status, language=language)
        
        return SandboxListResponse(
            sandboxes=[SandboxResponse(**s.to_dict()) for s in sandboxes],
            total=len(sandboxes)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sandboxes: {str(e)}")


@router.post("/{sandbox_id}/stop")
async def stop_sandbox(
    sandbox_id: str,
    manager: SandboxManager = Depends(get_sandbox_manager)
):
    """
    Stop a sandbox
    
    Stops the sandbox container but keeps it for potential restart.
    
    **Parameters:**
    - **sandbox_id**: ID of the sandbox to stop
    
    **Returns:**
    - Success message
    """
    try:
        await manager.stop_sandbox(sandbox_id)
        return {"message": f"Sandbox {sandbox_id} stopped successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop sandbox: {str(e)}")


@router.delete("/{sandbox_id}")
async def terminate_sandbox(
    sandbox_id: str,
    manager: SandboxManager = Depends(get_sandbox_manager)
):
    """
    Terminate and remove a sandbox
    
    Permanently removes the sandbox and its container.
    
    **Parameters:**
    - **sandbox_id**: ID of the sandbox to terminate
    
    **Returns:**
    - Success message
    """
    try:
        await manager.terminate_sandbox(sandbox_id)
        return {"message": f"Sandbox {sandbox_id} terminated successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to terminate sandbox: {str(e)}")


@router.post("/cleanup", response_model=CleanupResponse)
async def cleanup_old_sandboxes(
    max_age_hours: int = 24,
    manager: SandboxManager = Depends(get_sandbox_manager)
):
    """
    Clean up old sandboxes
    
    Removes sandboxes older than the specified age.
    
    **Parameters:**
    - **max_age_hours**: Maximum age in hours (default: 24)
    
    **Returns:**
    - Number of sandboxes cleaned up
    """
    try:
        cleaned = await manager.cleanup_old_sandboxes(max_age_hours=max_age_hours)
        
        return CleanupResponse(
            cleaned=cleaned,
            message=f"Cleaned up {cleaned} sandboxes older than {max_age_hours} hours"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sandboxes: {str(e)}")


@router.post("/execute-quick", response_model=ExecutionResponse)
async def execute_code_quick(
    language: SandboxLanguage,
    code: str = Body(..., embed=True),
    filename: Optional[str] = Body(None, embed=True),
    manager: SandboxManager = Depends(get_sandbox_manager)
):
    """
    Quick code execution (creates temporary sandbox)
    
    Creates a temporary sandbox, executes code, and terminates the sandbox.
    Convenient for one-off code execution.
    
    **Parameters:**
    - **language**: Programming language
    - **code**: Code to execute
    - **filename**: Optional filename
    
    **Returns:**
    - Execution results
    """
    try:
        # Create temporary sandbox
        config = SandboxConfig(language=language)
        sandbox_info = await manager.create_sandbox(language=language, config=config)
        sandbox_id = sandbox_info.sandbox_id
        
        try:
            # Execute code
            result = await manager.execute_code(
                sandbox_id=sandbox_id,
                code=code,
                filename=filename
            )
            
            return ExecutionResponse(
                sandbox_id=result.sandbox_id,
                success=result.success,
                output=result.output,
                error=result.error,
                exit_code=result.exit_code,
                execution_time=result.execution_time,
                memory_used=result.memory_used,
                cpu_used=result.cpu_used
            )
            
        finally:
            # Always cleanup temporary sandbox
            try:
                await manager.terminate_sandbox(sandbox_id)
            except:
                pass  # Ignore cleanup errors
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute code: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check(manager: SandboxManager = Depends(get_sandbox_manager)):
    """
    Check sandbox service health
    
    **Returns:**
    - Service status and statistics
    """
    try:
        sandboxes = await manager.list_sandboxes()
        
        status_counts = {}
        for sandbox in sandboxes:
            status = sandbox.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "status": "healthy",
            "total_sandboxes": len(sandboxes),
            "status_breakdown": status_counts,
            "supported_languages": [lang.value for lang in SandboxLanguage]
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }