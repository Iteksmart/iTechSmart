"""
Image Editing API Endpoints
Provides REST API for image manipulation and enhancement
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import base64
from enum import Enum

from ..services.image_service import (
    image_service,
    ImageFormat,
    FilterType,
    EnhancementType,
    ResizeMode
)

router = APIRouter(prefix="/api/image", tags=["image-editing"])


# Request/Response Models
class SessionCreateRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")


class SessionResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class ImageLoadResponse(BaseModel):
    success: bool
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    mode: Optional[str] = None
    error: Optional[str] = None


class ResizeRequest(BaseModel):
    session_id: str
    width: Optional[int] = None
    height: Optional[int] = None
    mode: ResizeMode = ResizeMode.FIT
    maintain_aspect: bool = True


class FilterRequest(BaseModel):
    session_id: str
    filter_type: FilterType


class EnhanceRequest(BaseModel):
    session_id: str
    enhancement_type: EnhancementType
    factor: float = Field(1.0, ge=0.0, le=3.0)


class RotateRequest(BaseModel):
    session_id: str
    degrees: float
    expand: bool = True


class FlipRequest(BaseModel):
    session_id: str
    horizontal: bool = True


class CropRequest(BaseModel):
    session_id: str
    left: int
    top: int
    right: int
    bottom: int


class AddTextRequest(BaseModel):
    session_id: str
    text: str
    x: int
    y: int
    font_size: int = 20
    color: str = "white"
    font_path: Optional[str] = None


class ConvertFormatRequest(BaseModel):
    session_id: str
    format: ImageFormat


class BatchOperation(BaseModel):
    type: str
    parameters: Dict[str, Any] = {}


class BatchProcessRequest(BaseModel):
    operations: List[BatchOperation]


class OperationResponse(BaseModel):
    success: bool
    operation_id: Optional[str] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# Endpoints

@router.post("/session/create", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """
    Create a new image editing session
    
    Each session maintains its own image state and operation history
    """
    result = image_service.create_session(request.session_id)
    return SessionResponse(**result)


@router.delete("/session/{session_id}", response_model=SessionResponse)
async def delete_session(session_id: str):
    """
    Delete an image editing session
    
    Cleans up all resources associated with the session
    """
    result = image_service.delete_session(session_id)
    return SessionResponse(**result)


@router.post("/load", response_model=ImageLoadResponse)
async def load_image(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Load an image into an editing session
    
    Supports: JPEG, PNG, WEBP, GIF, BMP, TIFF
    """
    editor = image_service.get_editor(session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    image_data = await file.read()
    result = editor.load_image(image_data)
    
    return ImageLoadResponse(**result)


@router.post("/resize", response_model=OperationResponse)
async def resize_image(request: ResizeRequest):
    """
    Resize image with various modes
    
    Modes:
    - exact: Resize to exact dimensions (may distort)
    - fit: Fit within dimensions (maintains aspect ratio)
    - fill: Fill dimensions (crops if needed)
    - crop: Center crop to dimensions
    """
    editor = image_service.get_editor(request.session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = editor.resize(
        width=request.width,
        height=request.height,
        mode=request.mode,
        maintain_aspect=request.maintain_aspect
    )
    
    return OperationResponse(
        success=result["success"],
        operation_id=result.get("operation_id"),
        error=result.get("error"),
        details={"new_size": result.get("new_size")}
    )


@router.post("/filter", response_model=OperationResponse)
async def apply_filter(request: FilterRequest):
    """
    Apply image filter
    
    Available filters:
    - blur: Gaussian blur
    - sharpen: Sharpen edges
    - smooth: Smooth image
    - edge_enhance: Enhance edges
    - emboss: Emboss effect
    - contour: Find contours
    - detail: Enhance details
    - find_edges: Edge detection
    """
    editor = image_service.get_editor(request.session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = editor.apply_filter(request.filter_type)
    
    return OperationResponse(
        success=result["success"],
        operation_id=result.get("operation_id"),
        error=result.get("error"),
        details={"filter_applied": result.get("filter_applied")}
    )


@router.post("/enhance", response_model=OperationResponse)
async def enhance_image(request: EnhanceRequest):
    """
    Enhance image properties
    
    Enhancement types:
    - brightness: Adjust brightness (0.0 = black, 1.0 = original, 2.0 = twice as bright)
    - contrast: Adjust contrast (0.0 = gray, 1.0 = original, 2.0 = high contrast)
    - color: Adjust color saturation (0.0 = grayscale, 1.0 = original, 2.0 = very saturated)
    - sharpness: Adjust sharpness (0.0 = blurred, 1.0 = original, 2.0 = very sharp)
    """
    editor = image_service.get_editor(request.session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = editor.enhance(request.enhancement_type, request.factor)
    
    return OperationResponse(
        success=result["success"],
        operation_id=result.get("operation_id"),
        error=result.get("error"),
        details={
            "enhancement_applied": result.get("enhancement_applied"),
            "factor": result.get("factor")
        }
    )


@router.post("/rotate", response_model=OperationResponse)
async def rotate_image(request: RotateRequest):
    """
    Rotate image by specified degrees
    
    Positive degrees rotate counter-clockwise
    expand=True will expand canvas to fit rotated image
    """
    editor = image_service.get_editor(request.session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = editor.rotate(request.degrees, request.expand)
    
    return OperationResponse(
        success=result["success"],
        operation_id=result.get("operation_id"),
        error=result.get("error"),
        details={
            "degrees": result.get("degrees"),
            "new_size": result.get("new_size")
        }
    )


@router.post("/flip", response_model=OperationResponse)
async def flip_image(request: FlipRequest):
    """
    Flip image horizontally or vertically
    
    horizontal=True flips left-right
    horizontal=False flips top-bottom
    """
    editor = image_service.get_editor(request.session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = editor.flip(request.horizontal)
    
    return OperationResponse(
        success=result["success"],
        operation_id=result.get("operation_id"),
        error=result.get("error"),
        details={"direction": result.get("direction")}
    )


@router.post("/crop", response_model=OperationResponse)
async def crop_image(request: CropRequest):
    """
    Crop image to specified region
    
    Coordinates are in pixels from top-left corner
    """
    editor = image_service.get_editor(request.session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = editor.crop(
        request.left,
        request.top,
        request.right,
        request.bottom
    )
    
    return OperationResponse(
        success=result["success"],
        operation_id=result.get("operation_id"),
        error=result.get("error"),
        details={"new_size": result.get("new_size")}
    )


@router.post("/text", response_model=OperationResponse)
async def add_text(request: AddTextRequest):
    """
    Add text overlay to image
    
    Position is in pixels from top-left corner
    Color can be name (e.g., 'white') or hex (e.g., '#FFFFFF')
    """
    editor = image_service.get_editor(request.session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = editor.add_text(
        text=request.text,
        position=(request.x, request.y),
        font_size=request.font_size,
        color=request.color,
        font_path=request.font_path
    )
    
    return OperationResponse(
        success=result["success"],
        operation_id=result.get("operation_id"),
        error=result.get("error"),
        details={"text_added": result.get("text_added")}
    )


@router.post("/convert", response_model=OperationResponse)
async def convert_format(request: ConvertFormatRequest):
    """
    Convert image to different format
    
    Supported formats: JPEG, PNG, WEBP, GIF, BMP, TIFF
    """
    editor = image_service.get_editor(request.session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = editor.convert_format(request.format)
    
    return OperationResponse(
        success=result["success"],
        operation_id=result.get("operation_id"),
        error=result.get("error"),
        details={"new_format": result.get("new_format")}
    )


@router.post("/undo/{session_id}", response_model=OperationResponse)
async def undo_operation(session_id: str):
    """
    Undo last operation
    
    Reverts to previous state by reapplying all operations except the last one
    """
    editor = image_service.get_editor(session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = editor.undo()
    
    return OperationResponse(
        success=result["success"],
        error=result.get("error"),
        details={"operations_remaining": result.get("operations_remaining")}
    )


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """
    Get operation history for session
    
    Returns list of all operations performed in chronological order
    """
    editor = image_service.get_editor(session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "session_id": session_id,
        "operations": editor.get_history()
    }


@router.get("/download/{session_id}")
async def download_image(
    session_id: str,
    format: ImageFormat = ImageFormat.PNG
):
    """
    Download current image
    
    Returns base64-encoded image data
    """
    editor = image_service.get_editor(session_id)
    if not editor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    image_bytes = editor.get_image_bytes(format)
    
    return {
        "success": True,
        "format": format.value,
        "image_data": base64.b64encode(image_bytes).decode(),
        "size_bytes": len(image_bytes)
    }


@router.post("/batch/process")
async def batch_process(
    request: BatchProcessRequest,
    files: List[UploadFile] = File(...)
):
    """
    Process multiple images with same operations
    
    Applies the same sequence of operations to all uploaded images
    Returns processed images as base64-encoded data
    """
    images = []
    for file in files:
        image_data = await file.read()
        images.append(image_data)
    
    operations = [op.dict() for op in request.operations]
    results = image_service.batch_process(images, operations)
    
    return {
        "success": True,
        "total_images": len(images),
        "results": results
    }