"""
iTechSmart Sandbox - Sandbox API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.core.sandbox_engine import SandboxEngine
from app.models.models import SandboxStatus

router = APIRouter(prefix="/api/sandboxes", tags=["Sandboxes"])


class SandboxCreate(BaseModel):
    name: Optional[str] = None
    image: str = "python:3.11-slim"
    cpu: float = 1.0
    memory: str = "1Gi"
    gpu: Optional[str] = None
    python_version: str = "3.11"
    packages: Optional[List[str]] = None
    env_vars: Optional[Dict[str, str]] = None
    secrets: Optional[List[str]] = None
    volumes: Optional[List[str]] = None
    keep_warm_seconds: int = 3600
    auto_terminate: bool = True
    project_id: Optional[int] = None


class SandboxResponse(BaseModel):
    id: int
    sandbox_id: str
    name: str
    status: SandboxStatus
    image: str
    cpu: float
    memory: str
    gpu: Optional[str]
    exposed_ports: List[int]
    preview_urls: Dict[str, str]
    created_at: str

    class Config:
        from_attributes = True


class CodeExecute(BaseModel):
    code: str
    timeout: int = 60


class CommandExecute(BaseModel):
    command: str
    args: Optional[List[str]] = None
    cwd: Optional[str] = None
    timeout: int = 60


class FileUpload(BaseModel):
    local_path: str
    remote_path: str


class FileDownload(BaseModel):
    remote_path: str
    local_path: str


class PortExpose(BaseModel):
    port: int


class TTLUpdate(BaseModel):
    seconds: int


@router.post("/", response_model=SandboxResponse)
def create_sandbox(sandbox: SandboxCreate, db: Session = Depends(get_db)):
    """Create new sandbox"""
    engine = SandboxEngine(db)
    return engine.create_sandbox(**sandbox.dict())


@router.get("/", response_model=List[SandboxResponse])
def list_sandboxes(
    status: Optional[SandboxStatus] = Query(None),
    project_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List sandboxes"""
    engine = SandboxEngine(db)
    return engine.list_sandboxes(status=status, project_id=project_id, limit=limit)


@router.get("/{sandbox_id}", response_model=SandboxResponse)
def get_sandbox(sandbox_id: str, db: Session = Depends(get_db)):
    """Get sandbox details"""
    engine = SandboxEngine(db)
    sandbox = engine.get_sandbox(sandbox_id)

    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")

    return sandbox


@router.delete("/{sandbox_id}")
def terminate_sandbox(sandbox_id: str, db: Session = Depends(get_db)):
    """Terminate sandbox"""
    engine = SandboxEngine(db)

    try:
        sandbox = engine.terminate_sandbox(sandbox_id)
        return {"message": "Sandbox terminated", "sandbox_id": sandbox_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{sandbox_id}/ttl", response_model=SandboxResponse)
def update_ttl(sandbox_id: str, ttl: TTLUpdate, db: Session = Depends(get_db)):
    """Update sandbox TTL"""
    engine = SandboxEngine(db)

    try:
        return engine.update_ttl(sandbox_id, ttl.seconds)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{sandbox_id}/code")
def run_code(sandbox_id: str, code_exec: CodeExecute, db: Session = Depends(get_db)):
    """Execute Python code in sandbox"""
    engine = SandboxEngine(db)

    try:
        process = engine.run_code(sandbox_id, code_exec.code, code_exec.timeout)
        return {
            "process_id": process.process_id,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "exit_code": process.exit_code,
            "status": process.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{sandbox_id}/exec")
def exec_command(sandbox_id: str, cmd: CommandExecute, db: Session = Depends(get_db)):
    """Execute shell command in sandbox"""
    engine = SandboxEngine(db)

    try:
        process = engine.exec_command(
            sandbox_id, cmd.command, cmd.args, cmd.cwd, cmd.timeout
        )
        return {
            "process_id": process.process_id,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "exit_code": process.exit_code,
            "status": process.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{sandbox_id}/files/upload")
def upload_file(sandbox_id: str, file: FileUpload, db: Session = Depends(get_db)):
    """Upload file to sandbox"""
    engine = SandboxEngine(db)

    try:
        sandbox_file = engine.upload_file(sandbox_id, file.local_path, file.remote_path)
        return {
            "file_id": sandbox_file.id,
            "file_path": sandbox_file.file_path,
            "message": "File uploaded successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{sandbox_id}/files/download")
def download_file(sandbox_id: str, file: FileDownload, db: Session = Depends(get_db)):
    """Download file from sandbox"""
    engine = SandboxEngine(db)

    try:
        success = engine.download_file(sandbox_id, file.remote_path, file.local_path)
        return {"success": success, "message": "File downloaded successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{sandbox_id}/files")
def list_files(
    sandbox_id: str, path: str = Query("/workspace"), db: Session = Depends(get_db)
):
    """List files in sandbox"""
    engine = SandboxEngine(db)

    try:
        files = engine.list_files(sandbox_id, path)
        return {"files": files}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{sandbox_id}/expose", response_model=Dict[str, str])
def expose_port(sandbox_id: str, port_data: PortExpose, db: Session = Depends(get_db)):
    """Expose sandbox port"""
    engine = SandboxEngine(db)

    try:
        preview_url = engine.expose_port(sandbox_id, port_data.port)
        return {
            "port": str(port_data.port),
            "preview_url": preview_url,
            "message": "Port exposed successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{sandbox_id}/metrics")
def get_metrics(
    sandbox_id: str,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get sandbox metrics"""
    engine = SandboxEngine(db)

    try:
        metrics = engine.get_metrics(sandbox_id, limit)
        return {"metrics": metrics}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
