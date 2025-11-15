"""
Files API Routes
Handles file uploads, downloads, and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import shutil
import os
import uuid
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.database import User
from app.api.auth import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Maximum file size (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    # Documents
    ".txt", ".md", ".pdf", ".doc", ".docx",
    # Code
    ".py", ".js", ".ts", ".java", ".go", ".rs", ".c", ".cpp", ".rb", ".php",
    # Data
    ".json", ".csv", ".xml", ".yaml", ".yml",
    # Images
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
    # Archives
    ".zip", ".tar", ".gz",
    # Other
    ".html", ".css", ".sql"
}

class FileInfo(BaseModel):
    filename: str
    filepath: str
    size: int
    content_type: str
    uploaded_at: str
    url: str

class FileListResponse(BaseModel):
    files: List[FileInfo]
    total: int

def get_user_upload_dir(user_id: int) -> Path:
    """Get upload directory for specific user"""
    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(exist_ok=True)
    return user_dir

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return Path(filename).suffix.lower()

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename"""
    ext = get_file_extension(original_filename)
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name = Path(original_filename).stem[:50]  # Limit name length
    return f"{name}_{timestamp}_{unique_id}{ext}"

@router.post("/upload", response_model=FileInfo, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file
    
    - **file**: File to upload (max 50MB)
    
    Supported formats: txt, md, pdf, doc, docx, py, js, ts, java, go, rs, c, cpp, rb, php,
    json, csv, xml, yaml, yml, jpg, jpeg, png, gif, svg, webp, zip, tar, gz, html, css, sql
    """
    # Check file extension
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to start
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    
    # Get user upload directory
    user_dir = get_user_upload_dir(current_user.id)
    file_path = user_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving file"
        )
    
    logger.info(f"File uploaded: {unique_filename} by user {current_user.email}")
    
    # Return file info
    return FileInfo(
        filename=file.filename,
        filepath=str(file_path.relative_to(UPLOAD_DIR)),
        size=file_size,
        content_type=file.content_type or "application/octet-stream",
        uploaded_at=datetime.utcnow().isoformat(),
        url=f"/api/v1/files/download/{current_user.id}/{unique_filename}"
    )

@router.get("/", response_model=FileListResponse)
async def list_files(
    current_user: User = Depends(get_current_user)
):
    """List all files uploaded by current user"""
    user_dir = get_user_upload_dir(current_user.id)
    
    files = []
    for file_path in user_dir.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append(FileInfo(
                filename=file_path.name,
                filepath=str(file_path.relative_to(UPLOAD_DIR)),
                size=stat.st_size,
                content_type="application/octet-stream",
                uploaded_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                url=f"/api/v1/files/download/{current_user.id}/{file_path.name}"
            ))
    
    # Sort by upload time (newest first)
    files.sort(key=lambda x: x.uploaded_at, reverse=True)
    
    return FileListResponse(
        files=files,
        total=len(files)
    )

@router.get("/download/{user_id}/{filename}")
async def download_file(
    user_id: int,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a file
    
    Users can only download their own files unless they are admin
    """
    # Check permissions
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this file"
        )
    
    # Get file path
    file_path = UPLOAD_DIR / str(user_id) / filename
    
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Return file
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )

@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a file"""
    # Get file path
    file_path = UPLOAD_DIR / str(current_user.id) / filename
    
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete file
    try:
        file_path.unlink()
        logger.info(f"File deleted: {filename} by user {current_user.email}")
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file"
        )
    
    return None

@router.get("/info/{filename}")
async def get_file_info(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Get file information"""
    # Get file path
    file_path = UPLOAD_DIR / str(current_user.id) / filename
    
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Get file stats
    stat = file_path.stat()
    
    return FileInfo(
        filename=filename,
        filepath=str(file_path.relative_to(UPLOAD_DIR)),
        size=stat.st_size,
        content_type="application/octet-stream",
        uploaded_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
        url=f"/api/v1/files/download/{current_user.id}/{filename}"
    )

@router.post("/upload-multiple", response_model=List[FileInfo])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple files at once
    
    Maximum 10 files per request
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files per request"
        )
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Check file extension
            if not is_allowed_file(file.filename):
                errors.append(f"{file.filename}: File type not allowed")
                continue
            
            # Check file size
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                errors.append(f"{file.filename}: File too large")
                continue
            
            # Generate unique filename
            unique_filename = generate_unique_filename(file.filename)
            
            # Get user upload directory
            user_dir = get_user_upload_dir(current_user.id)
            file_path = user_dir / unique_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(FileInfo(
                filename=file.filename,
                filepath=str(file_path.relative_to(UPLOAD_DIR)),
                size=file_size,
                content_type=file.content_type or "application/octet-stream",
                uploaded_at=datetime.utcnow().isoformat(),
                url=f"/api/v1/files/download/{current_user.id}/{unique_filename}"
            ))
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    if errors:
        logger.warning(f"Some files failed to upload: {errors}")
    
    logger.info(f"{len(uploaded_files)} files uploaded by user {current_user.email}")
    
    return uploaded_files