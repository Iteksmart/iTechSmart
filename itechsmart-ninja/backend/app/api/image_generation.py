"""
Image Generation API - AI image generation and editing endpoints
Provides text-to-image, image-to-image, editing, and enhancement
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from PIL import Image
from io import BytesIO
import base64
import uuid
from pathlib import Path

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User
from app.integrations.image_generation import (
    ImageGenerationClient,
    ImageProvider,
    ImageSize,
    ImageStyle,
    ImageQuality
)

router = APIRouter(prefix="/api/v1/images", tags=["images"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ImageGenerationRequest(BaseModel):
    """Request to generate images"""
    prompt: str = Field(..., description="Text description of desired image")
    provider: str = Field("dalle", description="Image generation provider")
    size: str = Field("1024x1024", description="Image size")
    style: Optional[str] = Field(None, description="Image style")
    quality: str = Field("standard", description="Image quality")
    n: int = Field(1, description="Number of images to generate", ge=1, le=4)
    negative_prompt: Optional[str] = Field(None, description="What to avoid")
    seed: Optional[int] = Field(None, description="Random seed")


class ImageEditRequest(BaseModel):
    """Request to edit image"""
    prompt: str = Field(..., description="Description of desired changes")
    strength: float = Field(0.8, description="Transformation strength", ge=0.0, le=1.0)
    negative_prompt: Optional[str] = Field(None, description="What to avoid")
    seed: Optional[int] = Field(None, description="Random seed")


class ImageUpscaleRequest(BaseModel):
    """Request to upscale image"""
    scale: int = Field(2, description="Upscale factor (2 or 4)", ge=2, le=4)


class ImageResponse(BaseModel):
    """Response with generated image"""
    image_id: str
    url: Optional[str]
    data: Optional[str]  # Base64 encoded
    provider: str
    size: Optional[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ImageListResponse(BaseModel):
    """Response with list of images"""
    images: List[ImageResponse]
    total: int


class ProviderInfo(BaseModel):
    """Information about image provider"""
    name: str
    available: bool
    capabilities: List[str]


class ProvidersResponse(BaseModel):
    """Response with available providers"""
    providers: List[ProviderInfo]
    total: int


# ============================================================================
# CLIENT MANAGEMENT
# ============================================================================

# Store image generation clients per user
image_clients: Dict[int, ImageGenerationClient] = {}


def get_image_client(current_user: User = Depends(get_current_user)) -> ImageGenerationClient:
    """Get image generation client for current user"""
    if current_user.id not in image_clients:
        # Create client with API keys from environment or user settings
        import os
        client = ImageGenerationClient(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            replicate_api_key=os.getenv("REPLICATE_API_TOKEN"),
            stability_api_key=os.getenv("STABILITY_API_KEY"),
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        image_clients[current_user.id] = client
    
    return image_clients[current_user.id]


# ============================================================================
# IMAGE GENERATION ENDPOINTS
# ============================================================================

@router.post("/generate", response_model=ImageListResponse)
async def generate_images(
    request: ImageGenerationRequest,
    client: ImageGenerationClient = Depends(get_image_client),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate images from text prompt
    
    Supports multiple providers:
    - DALL-E (OpenAI)
    - FLUX (Replicate)
    - Stable Diffusion (Replicate/Stability AI)
    - Imagen (Google)
    """
    try:
        # Parse enums
        provider = ImageProvider(request.provider)
        size = ImageSize(request.size)
        style = ImageStyle(request.style) if request.style else None
        quality = ImageQuality(request.quality)
        
        # Generate images
        results = client.generate_image(
            prompt=request.prompt,
            provider=provider,
            size=size,
            style=style,
            quality=quality,
            n=request.n,
            negative_prompt=request.negative_prompt,
            seed=request.seed
        )
        
        # Convert to response format
        images = []
        for result in results:
            image_id = str(uuid.uuid4())
            images.append(ImageResponse(
                image_id=image_id,
                url=result.get("url"),
                data=result.get("data"),
                provider=result["provider"],
                size=result.get("size"),
                metadata=result
            ))
        
        return ImageListResponse(
            images=images,
            total=len(images)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-to-image", response_model=ImageListResponse)
async def image_to_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    provider: str = Form("stable_diffusion"),
    strength: float = Form(0.8),
    negative_prompt: Optional[str] = Form(None),
    seed: Optional[int] = Form(None),
    client: ImageGenerationClient = Depends(get_image_client),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate new image based on input image and prompt
    
    Transform an existing image according to a text description.
    """
    try:
        # Load image
        image_data = await image.read()
        input_image = Image.open(BytesIO(image_data))
        
        # Parse provider
        provider_enum = ImageProvider(provider)
        
        # Generate images
        results = client.image_to_image(
            image=input_image,
            prompt=prompt,
            provider=provider_enum,
            strength=strength,
            negative_prompt=negative_prompt,
            seed=seed
        )
        
        # Convert to response format
        images = []
        for result in results:
            image_id = str(uuid.uuid4())
            images.append(ImageResponse(
                image_id=image_id,
                url=result.get("url"),
                data=result.get("data"),
                provider=result["provider"],
                metadata=result
            ))
        
        return ImageListResponse(
            images=images,
            total=len(images)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# IMAGE EDITING ENDPOINTS
# ============================================================================

@router.post("/inpaint", response_model=ImageListResponse)
async def inpaint_image(
    image: UploadFile = File(...),
    mask: UploadFile = File(...),
    prompt: str = Form(...),
    provider: str = Form("dalle"),
    client: ImageGenerationClient = Depends(get_image_client),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fill masked area of image based on prompt
    
    The mask should be white where you want to fill and black where you want to keep.
    """
    try:
        # Load images
        image_data = await image.read()
        input_image = Image.open(BytesIO(image_data))
        
        mask_data = await mask.read()
        mask_image = Image.open(BytesIO(mask_data))
        
        # Parse provider
        provider_enum = ImageProvider(provider)
        
        # Inpaint
        results = client.inpaint(
            image=input_image,
            mask=mask_image,
            prompt=prompt,
            provider=provider_enum
        )
        
        # Convert to response format
        images = []
        for result in results:
            image_id = str(uuid.uuid4())
            images.append(ImageResponse(
                image_id=image_id,
                url=result.get("url"),
                data=result.get("data"),
                provider=result["provider"],
                metadata=result
            ))
        
        return ImageListResponse(
            images=images,
            total=len(images)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/variations", response_model=ImageListResponse)
async def create_variations(
    image: UploadFile = File(...),
    provider: str = Form("dalle"),
    n: int = Form(1),
    client: ImageGenerationClient = Depends(get_image_client),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create variations of an image
    
    Generate similar images based on the input image.
    """
    try:
        # Load image
        image_data = await image.read()
        input_image = Image.open(BytesIO(image_data))
        
        # Parse provider
        provider_enum = ImageProvider(provider)
        
        # Create variations
        results = client.create_variation(
            image=input_image,
            provider=provider_enum,
            n=n
        )
        
        # Convert to response format
        images = []
        for result in results:
            image_id = str(uuid.uuid4())
            images.append(ImageResponse(
                image_id=image_id,
                url=result.get("url"),
                data=result.get("data"),
                provider=result["provider"],
                metadata=result
            ))
        
        return ImageListResponse(
            images=images,
            total=len(images)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# IMAGE ENHANCEMENT ENDPOINTS
# ============================================================================

@router.post("/upscale", response_model=ImageResponse)
async def upscale_image(
    image: UploadFile = File(...),
    scale: int = Form(2),
    client: ImageGenerationClient = Depends(get_image_client),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upscale image resolution
    
    Increase image resolution by 2x or 4x using AI upscaling.
    """
    try:
        # Load image
        image_data = await image.read()
        input_image = Image.open(BytesIO(image_data))
        
        # Upscale
        result = client.upscale(
            image=input_image,
            scale=scale
        )
        
        image_id = str(uuid.uuid4())
        return ImageResponse(
            image_id=image_id,
            url=result.get("url"),
            data=result.get("data"),
            provider=result["provider"],
            metadata=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove-background", response_model=ImageResponse)
async def remove_background(
    image: UploadFile = File(...),
    client: ImageGenerationClient = Depends(get_image_client),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove background from image
    
    Automatically detect and remove the background, leaving only the subject.
    """
    try:
        # Load image
        image_data = await image.read()
        input_image = Image.open(BytesIO(image_data))
        
        # Remove background
        result = client.remove_background(input_image)
        
        image_id = str(uuid.uuid4())
        return ImageResponse(
            image_id=image_id,
            url=result.get("url"),
            data=result.get("data"),
            provider=result["provider"],
            metadata=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance-face", response_model=ImageResponse)
async def enhance_face(
    image: UploadFile = File(...),
    client: ImageGenerationClient = Depends(get_image_client),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhance/restore faces in image
    
    Improve face quality and restore details in portraits.
    """
    try:
        # Load image
        image_data = await image.read()
        input_image = Image.open(BytesIO(image_data))
        
        # Enhance face
        result = client.enhance_face(input_image)
        
        image_id = str(uuid.uuid4())
        return ImageResponse(
            image_id=image_id,
            url=result.get("url"),
            data=result.get("data"),
            provider=result["provider"],
            metadata=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROVIDER ENDPOINTS
# ============================================================================

@router.get("/providers", response_model=ProvidersResponse)
async def list_providers(
    client: ImageGenerationClient = Depends(get_image_client)
):
    """
    List available image generation providers
    
    Shows which providers are configured and available.
    """
    try:
        available = client.get_available_providers()
        
        providers = [
            ProviderInfo(
                name="DALL-E",
                available="dalle" in available,
                capabilities=["text-to-image", "inpainting", "variations"]
            ),
            ProviderInfo(
                name="FLUX",
                available="flux" in available,
                capabilities=["text-to-image", "high-quality"]
            ),
            ProviderInfo(
                name="Stable Diffusion",
                available="stable_diffusion" in available,
                capabilities=["text-to-image", "image-to-image", "inpainting"]
            ),
            ProviderInfo(
                name="Imagen",
                available="imagen" in available,
                capabilities=["text-to-image"]
            )
        ]
        
        return ProvidersResponse(
            providers=providers,
            total=len(providers)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sizes")
async def list_sizes():
    """List available image sizes"""
    sizes = [
        {"value": "256x256", "label": "256x256 (Square Small)"},
        {"value": "512x512", "label": "512x512 (Square Medium)"},
        {"value": "1024x1024", "label": "1024x1024 (Square Large)"},
        {"value": "512x768", "label": "512x768 (Portrait)"},
        {"value": "768x1024", "label": "768x1024 (Portrait Large)"},
        {"value": "768x512", "label": "768x512 (Landscape)"},
        {"value": "1024x768", "label": "1024x768 (Landscape Large)"},
        {"value": "1024x576", "label": "1024x576 (Wide)"},
        {"value": "576x1024", "label": "576x1024 (Tall)"}
    ]
    
    return {"sizes": sizes, "total": len(sizes)}


@router.get("/styles")
async def list_styles():
    """List available image styles"""
    styles = [
        {"value": "natural", "label": "Natural"},
        {"value": "vivid", "label": "Vivid"},
        {"value": "artistic", "label": "Artistic"},
        {"value": "photorealistic", "label": "Photorealistic"},
        {"value": "anime", "label": "Anime"},
        {"value": "digital_art", "label": "Digital Art"},
        {"value": "oil_painting", "label": "Oil Painting"},
        {"value": "watercolor", "label": "Watercolor"},
        {"value": "sketch", "label": "Sketch"},
        {"value": "cartoon", "label": "Cartoon"}
    ]
    
    return {"styles": styles, "total": len(styles)}