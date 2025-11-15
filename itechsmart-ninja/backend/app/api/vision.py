"""
Vision Analysis API Endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import base64

from app.services.vision_service import vision_service, VisionTask, VisionProvider

router = APIRouter(prefix="/api/v1/vision", tags=["Vision Analysis"])


class VisionAnalyzeRequest(BaseModel):
    """Vision analysis request"""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    task: str = "general_analysis"
    prompt: Optional[str] = None
    provider: str = "openai"
    detail_level: str = "high"


class VisualQARequest(BaseModel):
    """Visual Q&A request"""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    question: str
    provider: str = "openai"


@router.post("/analyze")
async def analyze_image(request: VisionAnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze an image
    
    Example:
    ```json
    {
        "image_url": "https://example.com/image.jpg",
        "task": "general_analysis",
        "provider": "openai",
        "detail_level": "high"
    }
    ```
    
    Or with base64:
    ```json
    {
        "image_base64": "iVBORw0KGgoAAAANS...",
        "task": "ocr",
        "provider": "openai"
    }
    ```
    """
    try:
        # Get image
        if request.image_url:
            image = request.image_url
        elif request.image_base64:
            image = base64.b64decode(request.image_base64)
        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 required")
        
        # Map task and provider
        task = VisionTask(request.task)
        provider = VisionProvider(request.provider)
        
        # Analyze
        result = await vision_service.analyze_image(
            image=image,
            task=task,
            prompt=request.prompt,
            provider=provider,
            detail_level=request.detail_level
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    task: str = "general_analysis",
    provider: str = "openai",
    detail_level: str = "high"
) -> Dict[str, Any]:
    """
    Upload and analyze an image file
    
    Supports: JPG, PNG, GIF, WEBP
    """
    try:
        # Read file
        image_bytes = await file.read()
        
        # Map task and provider
        vision_task = VisionTask(task)
        vision_provider = VisionProvider(provider)
        
        # Analyze
        result = await vision_service.analyze_image(
            image=image_bytes,
            task=vision_task,
            provider=vision_provider,
            detail_level=detail_level
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr")
async def extract_text(request: VisionAnalyzeRequest) -> Dict[str, Any]:
    """
    Extract text from image (OCR)
    
    Example:
    ```json
    {
        "image_url": "https://example.com/document.jpg",
        "provider": "openai"
    }
    ```
    """
    try:
        # Get image
        if request.image_url:
            image = request.image_url
        elif request.image_base64:
            image = base64.b64decode(request.image_base64)
        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 required")
        
        provider = VisionProvider(request.provider)
        
        result = await vision_service.extract_text(image, provider=provider)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-code")
async def detect_code(request: VisionAnalyzeRequest) -> Dict[str, Any]:
    """
    Detect and extract code from image
    
    Useful for:
    - Screenshots of code
    - Photos of whiteboards
    - Code in presentations
    """
    try:
        # Get image
        if request.image_url:
            image = request.image_url
        elif request.image_base64:
            image = base64.b64decode(request.image_base64)
        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 required")
        
        provider = VisionProvider(request.provider)
        
        result = await vision_service.detect_code(image, provider=provider)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-diagram")
async def analyze_diagram(request: VisionAnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze diagram or flowchart
    
    Useful for:
    - Architecture diagrams
    - Flowcharts
    - UML diagrams
    - Mind maps
    """
    try:
        # Get image
        if request.image_url:
            image = request.image_url
        elif request.image_base64:
            image = base64.b64decode(request.image_base64)
        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 required")
        
        provider = VisionProvider(request.provider)
        
        result = await vision_service.analyze_diagram(image, provider=provider)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-ui")
async def analyze_ui(request: VisionAnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze UI/UX design
    
    Provides feedback on:
    - Layout and composition
    - Color scheme
    - Typography
    - User experience
    - Accessibility
    """
    try:
        # Get image
        if request.image_url:
            image = request.image_url
        elif request.image_base64:
            image = base64.b64decode(request.image_base64)
        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 required")
        
        provider = VisionProvider(request.provider)
        
        result = await vision_service.analyze_ui(image, provider=provider)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visual-qa")
async def visual_qa(request: VisualQARequest) -> Dict[str, Any]:
    """
    Answer questions about an image
    
    Example:
    ```json
    {
        "image_url": "https://example.com/chart.jpg",
        "question": "What is the trend shown in this chart?",
        "provider": "openai"
    }
    ```
    """
    try:
        # Get image
        if request.image_url:
            image = request.image_url
        elif request.image_base64:
            image = base64.b64decode(request.image_base64)
        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 required")
        
        provider = VisionProvider(request.provider)
        
        result = await vision_service.visual_qa(
            image=image,
            question=request.question,
            provider=provider
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def list_vision_tasks() -> Dict[str, Any]:
    """List available vision analysis tasks"""
    return {
        "success": True,
        "tasks": [
            {
                "name": task.value,
                "description": _get_task_description(task)
            }
            for task in VisionTask
        ]
    }


@router.get("/providers")
async def list_providers() -> Dict[str, Any]:
    """List available vision AI providers"""
    return {
        "success": True,
        "providers": [
            {
                "name": provider.value,
                "models": _get_provider_models(provider)
            }
            for provider in VisionProvider
        ]
    }


def _get_task_description(task: VisionTask) -> str:
    """Get task description"""
    descriptions = {
        VisionTask.GENERAL_ANALYSIS: "General image analysis and description",
        VisionTask.OCR: "Extract text from images (Optical Character Recognition)",
        VisionTask.OBJECT_DETECTION: "Detect and identify objects in images",
        VisionTask.SCENE_UNDERSTANDING: "Understand the scene and context",
        VisionTask.TEXT_EXTRACTION: "Extract all visible text",
        VisionTask.CODE_DETECTION: "Detect and extract code from images",
        VisionTask.DIAGRAM_ANALYSIS: "Analyze diagrams and flowcharts",
        VisionTask.UI_ANALYSIS: "Analyze UI/UX designs",
        VisionTask.VISUAL_QA: "Answer questions about images"
    }
    return descriptions.get(task, "Unknown task")


def _get_provider_models(provider: VisionProvider) -> List[str]:
    """Get provider models"""
    models = {
        VisionProvider.OPENAI: ["gpt-4o", "gpt-4-turbo"],
        VisionProvider.ANTHROPIC: ["claude-3-5-sonnet", "claude-3-opus"],
        VisionProvider.GOOGLE: ["gemini-1.5-pro", "gemini-1.5-flash"]
    }
    return models.get(provider, [])