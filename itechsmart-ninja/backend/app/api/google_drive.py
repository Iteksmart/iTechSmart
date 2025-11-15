"""
Google Drive Integration API Endpoints
Provides REST API for Google Drive file sync and collaboration
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

from ..services.google_drive_service import (
    google_drive_service,
    SyncDirection,
    SyncStatus
)

router = APIRouter(prefix="/api/integrations/google-drive", tags=["google-drive"])


# Request Models
class ConnectDriveRequest(BaseModel):
    workspace_id: str
    access_token: str
    refresh_token: str
    token_expiry: datetime


class DownloadFileRequest(BaseModel):
    file_id: str
    local_path: str


class UploadFileRequest(BaseModel):
    local_path: str
    drive_folder_id: Optional[str] = None
    file_name: Optional[str] = None


class SyncFolderRequest(BaseModel):
    local_folder: str
    drive_folder_id: str
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL


class CreateFolderRequest(BaseModel):
    folder_name: str
    parent_folder_id: Optional[str] = None


class ShareFileRequest(BaseModel):
    file_id: str
    email: EmailStr
    role: str = Field("reader", regex="^(reader|writer|commenter|owner)$")


# Response Models
class ConnectionResponse(BaseModel):
    success: bool
    connection: Optional[dict] = None
    error: Optional[str] = None


class FileOperationResponse(BaseModel):
    success: bool
    task: Optional[dict] = None
    error: Optional[str] = None


# Helper function to get current user
def get_current_user_id(user_id: str = Query(...)) -> str:
    """Get current authenticated user ID"""
    return user_id


# Connection Endpoints

@router.post("/connect", response_model=ConnectionResponse)
async def connect_drive(
    request: ConnectDriveRequest,
    user_id: str = Query(...)
):
    """
    Connect Google Drive account
    
    Requires OAuth2 tokens from Google authentication flow
    Enables file sync and collaboration features
    """
    result = google_drive_service.connect_drive(
        workspace_id=request.workspace_id,
        user_id=user_id,
        access_token=request.access_token,
        refresh_token=request.refresh_token,
        token_expiry=request.token_expiry
    )
    
    return ConnectionResponse(**result)


@router.delete("/disconnect")
async def disconnect_drive(
    workspace_id: str = Query(...),
    user_id: str = Query(...)
):
    """
    Disconnect Google Drive account
    
    Removes connection and stops file sync
    """
    result = google_drive_service.disconnect_drive(workspace_id)
    return result


@router.get("/connection")
async def get_connection(
    workspace_id: str = Query(...),
    user_id: str = Query(...)
):
    """
    Get Google Drive connection status
    
    Returns connection details and sync status
    """
    connection = google_drive_service.get_connection(workspace_id)
    
    if not connection:
        return {
            "success": False,
            "connected": False,
            "error": "Not connected to Google Drive"
        }
    
    return {
        "success": True,
        "connected": True,
        "connection": connection.to_dict()
    }


# File Operations

@router.get("/files")
async def list_files(
    workspace_id: str = Query(...),
    folder_id: Optional[str] = None,
    query: Optional[str] = None,
    page_size: int = Query(100, ge=1, le=1000),
    user_id: str = Query(...)
):
    """
    List files in Google Drive
    
    Supports filtering by folder and search query
    Returns file metadata including sharing status
    """
    result = google_drive_service.list_files(
        workspace_id=workspace_id,
        folder_id=folder_id,
        query=query,
        page_size=page_size
    )
    
    return result


@router.post("/download", response_model=FileOperationResponse)
async def download_file(
    workspace_id: str = Query(...),
    request: DownloadFileRequest = None,
    user_id: str = Query(...)
):
    """
    Download file from Google Drive
    
    Downloads file to local workspace storage
    Creates sync task for tracking progress
    """
    result = google_drive_service.download_file(
        workspace_id=workspace_id,
        file_id=request.file_id,
        local_path=request.local_path
    )
    
    return FileOperationResponse(**result)


@router.post("/upload", response_model=FileOperationResponse)
async def upload_file(
    workspace_id: str = Query(...),
    request: UploadFileRequest = None,
    user_id: str = Query(...)
):
    """
    Upload file to Google Drive
    
    Uploads local file to specified Drive folder
    Creates sync task for tracking progress
    """
    result = google_drive_service.upload_file(
        workspace_id=workspace_id,
        local_path=request.local_path,
        drive_folder_id=request.drive_folder_id,
        file_name=request.file_name
    )
    
    return FileOperationResponse(**result)


# Folder Operations

@router.post("/sync-folder")
async def sync_folder(
    workspace_id: str = Query(...),
    request: SyncFolderRequest = None,
    user_id: str = Query(...)
):
    """
    Sync folder with Google Drive
    
    Synchronizes entire folder bidirectionally
    Supports upload-only, download-only, or bidirectional sync
    """
    result = google_drive_service.sync_folder(
        workspace_id=workspace_id,
        local_folder=request.local_folder,
        drive_folder_id=request.drive_folder_id,
        direction=request.direction
    )
    
    return result


@router.post("/create-folder")
async def create_folder(
    workspace_id: str = Query(...),
    request: CreateFolderRequest = None,
    user_id: str = Query(...)
):
    """
    Create folder in Google Drive
    
    Creates new folder in specified parent folder
    """
    result = google_drive_service.create_folder(
        workspace_id=workspace_id,
        folder_name=request.folder_name,
        parent_folder_id=request.parent_folder_id
    )
    
    return result


# Sharing Operations

@router.post("/share")
async def share_file(
    workspace_id: str = Query(...),
    request: ShareFileRequest = None,
    user_id: str = Query(...)
):
    """
    Share file with user
    
    Grants access to file with specified role
    Roles: reader, writer, commenter, owner
    """
    result = google_drive_service.share_file(
        workspace_id=workspace_id,
        file_id=request.file_id,
        email=request.email,
        role=request.role
    )
    
    return result


# Sync Task Management

@router.get("/sync-tasks")
async def list_sync_tasks(
    workspace_id: str = Query(...),
    status: Optional[SyncStatus] = None,
    user_id: str = Query(...)
):
    """
    List sync tasks
    
    Returns all sync tasks for workspace
    Optionally filter by status
    """
    tasks = google_drive_service.list_sync_tasks(workspace_id, status)
    
    return {
        "success": True,
        "total": len(tasks),
        "tasks": tasks
    }


@router.get("/sync-tasks/{task_id}")
async def get_sync_task(
    task_id: str,
    user_id: str = Query(...)
):
    """
    Get sync task status
    
    Returns detailed task information including progress
    """
    task = google_drive_service.get_sync_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "success": True,
        "task": task
    }


# Webhook Endpoints (for real-time sync)

@router.post("/webhook")
async def drive_webhook(
    channel_id: str = Query(...),
    resource_id: str = Query(...),
    resource_state: str = Query(...)
):
    """
    Google Drive webhook endpoint
    
    Receives notifications about file changes
    Triggers automatic sync when files are modified
    """
    # Handle Drive webhook notifications
    # In production, implement proper webhook verification
    
    return {
        "success": True,
        "message": "Webhook received",
        "channel_id": channel_id,
        "resource_id": resource_id,
        "state": resource_state
    }


# Statistics

@router.get("/stats")
async def get_drive_stats(
    workspace_id: str = Query(...),
    user_id: str = Query(...)
):
    """
    Get Google Drive integration statistics
    
    Returns sync statistics and usage metrics
    """
    connection = google_drive_service.get_connection(workspace_id)
    
    if not connection:
        raise HTTPException(status_code=404, detail="Not connected to Google Drive")
    
    tasks = google_drive_service.list_sync_tasks(workspace_id)
    
    completed_tasks = [t for t in tasks if t["status"] == SyncStatus.COMPLETED.value]
    failed_tasks = [t for t in tasks if t["status"] == SyncStatus.FAILED.value]
    in_progress_tasks = [t for t in tasks if t["status"] == SyncStatus.IN_PROGRESS.value]
    
    total_bytes = sum(t["total_bytes"] for t in completed_tasks)
    
    return {
        "success": True,
        "stats": {
            "connected": True,
            "last_sync": connection.last_sync.isoformat() if connection.last_sync else None,
            "sync_enabled": connection.sync_enabled,
            "total_tasks": len(tasks),
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "in_progress_tasks": len(in_progress_tasks),
            "total_bytes_synced": total_bytes,
            "total_mb_synced": round(total_bytes / (1024 * 1024), 2)
        }
    }