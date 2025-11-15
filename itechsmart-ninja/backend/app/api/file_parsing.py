"""
File Parsing API Endpoints for iTechSmart Ninja
Provides REST API for file content extraction and parsing
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel

from ..core.file_parser import (
    FileManager,
    FileMetadata,
    ParsedContent,
    FileType,
    ParsingStatus,
    get_file_manager
)

router = APIRouter(prefix="/file-parsing", tags=["file-parsing"])


# Response Models
class FileMetadataResponse(BaseModel):
    """Response with file metadata"""
    file_id: str
    filename: str
    file_type: str
    mime_type: str
    size_bytes: int
    hash_md5: str
    hash_sha256: str
    uploaded_at: str
    uploaded_by: str


class ParsedContentResponse(BaseModel):
    """Response with parsed content"""
    file_id: str
    status: str
    content_type: str
    text_content: Optional[str]
    structured_data: Optional[dict]
    metadata: dict
    page_count: Optional[int]
    word_count: Optional[int]
    parsed_at: Optional[str]
    error_message: Optional[str]


class FileListResponse(BaseModel):
    """Response with list of files"""
    files: List[FileMetadataResponse]
    total: int


# API Endpoints
@router.post("/upload", response_model=FileMetadataResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    manager: FileManager = Depends(get_file_manager)
):
    """
    Upload a file for parsing
    
    **Parameters:**
    - **file**: File to upload
    - **user_id**: User ID
    
    **Returns:**
    - File metadata including ID, type, size, and hashes
    
    **Supported Formats:**
    - Documents: PDF, DOCX, DOC, TXT, RTF
    - Spreadsheets: XLSX, XLS, CSV
    - Data: JSON, XML
    - Web: HTML, Markdown
    - Images: JPG, PNG, GIF
    - Audio: MP3, WAV
    - Video: MP4, AVI
    - Archives: ZIP, TAR, GZ
    - Code: PY, JS, JAVA, CPP
    """
    try:
        # Read file content
        content = await file.read()
        
        # Upload file
        metadata = await manager.upload_file(
            filename=file.filename,
            content=content,
            user_id=user_id,
            mime_type=file.content_type
        )
        
        return FileMetadataResponse(**metadata.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/upload-multiple", response_model=FileListResponse)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    user_id: str = Form(...),
    manager: FileManager = Depends(get_file_manager)
):
    """
    Upload multiple files for parsing
    
    **Parameters:**
    - **files**: List of files to upload
    - **user_id**: User ID
    
    **Returns:**
    - List of file metadata for all uploaded files
    """
    try:
        uploaded_files = []
        
        for file in files:
            content = await file.read()
            metadata = await manager.upload_file(
                filename=file.filename,
                content=content,
                user_id=user_id,
                mime_type=file.content_type
            )
            uploaded_files.append(FileMetadataResponse(**metadata.to_dict()))
        
        return FileListResponse(
            files=uploaded_files,
            total=len(uploaded_files)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {str(e)}")


@router.post("/parse/{file_id}", response_model=ParsedContentResponse)
async def parse_file(
    file_id: str,
    manager: FileManager = Depends(get_file_manager)
):
    """
    Parse a file and extract content
    
    **Parameters:**
    - **file_id**: File ID
    
    **Returns:**
    - Parsed content including text, structured data, and metadata
    
    **Parsing Capabilities:**
    - **Text Extraction**: Extract text from documents
    - **Structure Parsing**: Parse tables, headers, links
    - **Metadata Extraction**: Extract document properties
    - **Word/Page Counting**: Count words and pages
    """
    try:
        parsed = await manager.parse_file(file_id)
        return ParsedContentResponse(**parsed.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")


@router.get("/{file_id}/metadata", response_model=FileMetadataResponse)
async def get_file_metadata(
    file_id: str,
    manager: FileManager = Depends(get_file_manager)
):
    """
    Get file metadata
    
    **Parameters:**
    - **file_id**: File ID
    
    **Returns:**
    - File metadata including type, size, and hashes
    """
    metadata = await manager.get_file_metadata(file_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail=f"File {file_id} not found")
    
    return FileMetadataResponse(**metadata.to_dict())


@router.get("/{file_id}/content", response_model=ParsedContentResponse)
async def get_parsed_content(
    file_id: str,
    manager: FileManager = Depends(get_file_manager)
):
    """
    Get parsed content for a file
    
    **Parameters:**
    - **file_id**: File ID
    
    **Returns:**
    - Parsed content if available, otherwise triggers parsing
    """
    # Check if already parsed
    parsed = await manager.get_parsed_content(file_id)
    
    if not parsed:
        # Parse file if not already parsed
        parsed = await manager.parse_file(file_id)
    
    return ParsedContentResponse(**parsed.to_dict())


@router.get("/list", response_model=FileListResponse)
async def list_files(
    user_id: Optional[str] = None,
    file_type: Optional[str] = None,
    manager: FileManager = Depends(get_file_manager)
):
    """
    List all files with optional filtering
    
    **Parameters:**
    - **user_id**: Filter by user ID
    - **file_type**: Filter by file type
    
    **Returns:**
    - List of file metadata
    """
    try:
        file_type_enum = FileType(file_type) if file_type else None
        files = await manager.list_files(user_id=user_id, file_type=file_type_enum)
        
        return FileListResponse(
            files=[FileMetadataResponse(**f.to_dict()) for f in files],
            total=len(files)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    manager: FileManager = Depends(get_file_manager)
):
    """
    Delete a file
    
    **Parameters:**
    - **file_id**: File ID
    
    **Returns:**
    - Success message
    """
    try:
        await manager.delete_file(file_id)
        return {"message": f"File {file_id} deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.post("/batch-parse")
async def batch_parse_files(
    file_ids: List[str],
    manager: FileManager = Depends(get_file_manager)
):
    """
    Parse multiple files in batch
    
    **Parameters:**
    - **file_ids**: List of file IDs to parse
    
    **Returns:**
    - List of parsed content for all files
    """
    try:
        results = []
        
        for file_id in file_ids:
            try:
                parsed = await manager.parse_file(file_id)
                results.append({
                    "file_id": file_id,
                    "status": "success",
                    "parsed": ParsedContentResponse(**parsed.to_dict())
                })
            except Exception as e:
                results.append({
                    "file_id": file_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "results": results,
            "total": len(results),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "failed"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to batch parse files: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check(manager: FileManager = Depends(get_file_manager)):
    """
    Check file parsing service health
    
    **Returns:**
    - Service status and statistics
    """
    try:
        files = await manager.list_files()
        
        type_counts = {}
        total_size = 0
        
        for file in files:
            file_type = file.file_type.value
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
            total_size += file.size_bytes
        
        return {
            "status": "healthy",
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "type_breakdown": type_counts,
            "supported_types": [t.value for t in FileType],
            "storage_path": manager.storage_path
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }