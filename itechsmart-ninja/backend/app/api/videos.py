"""
Video Generation API Routes
AI-powered video generation and editing
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import os
import tempfile

from ..database import get_db
from ..models.database import VideoGeneration, User
from ..integrations.video_generation import (
    video_client,
    VideoProvider,
    VideoResolution,
    VideoStyle,
)
from ..auth import get_current_user

router = APIRouter(prefix="/api/video", tags=["video"])
logger = logging.getLogger(__name__)


# Request/Response Models
from pydantic import BaseModel


class GenerateVideoRequest(BaseModel):
    prompt: str
    provider: str = "runway"
    duration: int = 4
    resolution: str = "1080p"
    style: Optional[str] = None
    motion_strength: float = 0.5
    seed: Optional[int] = None


class GenerateFromImageRequest(BaseModel):
    image_path: str
    prompt: Optional[str] = None
    provider: str = "runway"
    duration: int = 4
    motion_strength: float = 0.5


class TransformVideoRequest(BaseModel):
    video_path: str
    prompt: str
    provider: str = "runway"
    strength: float = 0.7


class UpscaleVideoRequest(BaseModel):
    video_path: str
    target_resolution: str = "4k"
    enhance_quality: bool = True


class EditVideoRequest(BaseModel):
    video_path: str
    operation: str
    parameters: Dict[str, Any]


@router.post("/generate")
async def generate_video(
    request: GenerateVideoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate video from text prompt

    Example:
    ```json
    {
        "prompt": "A serene sunset over the ocean with waves",
        "provider": "runway",
        "duration": 4,
        "resolution": "1080p",
        "style": "cinematic",
        "motion_strength": 0.7
    }
    ```
    """
    try:
        # Validate provider
        try:
            provider = VideoProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Supported: {[p.value for p in VideoProvider]}",
            )

        # Validate resolution
        try:
            resolution = VideoResolution(request.resolution)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resolution. Supported: {[r.value for r in VideoResolution]}",
            )

        # Validate style if provided
        style = None
        if request.style:
            try:
                style = VideoStyle(request.style)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid style. Supported: {[s.value for s in VideoStyle]}",
                )

        # Generate video
        result = await video_client.generate_from_text(
            prompt=request.prompt,
            provider=provider,
            duration=request.duration,
            resolution=resolution,
            style=style,
            motion_strength=request.motion_strength,
            seed=request.seed,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        # Save to database
        db_video = VideoGeneration(
            user_id=current_user.id,
            prompt=request.prompt,
            provider=request.provider,
            duration=request.duration,
            resolution=request.resolution,
            video_url=result.get("video_url"),
            status="completed",
            metadata=result.get("metadata", {}),
            created_at=datetime.utcnow(),
        )

        db.add(db_video)
        db.commit()
        db.refresh(db_video)

        return {
            "success": True,
            "video": {
                "id": db_video.id,
                "video_url": db_video.video_url,
                "prompt": db_video.prompt,
                "duration": db_video.duration,
                "resolution": db_video.resolution,
                "provider": db_video.provider,
                "created_at": db_video.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-from-image")
async def generate_from_image(
    request: GenerateFromImageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate video from image

    Example:
    ```json
    {
        "image_path": "/path/to/image.jpg",
        "prompt": "Make the clouds move",
        "provider": "runway",
        "duration": 4,
        "motion_strength": 0.5
    }
    ```
    """
    try:
        # Validate provider
        try:
            provider = VideoProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Supported: {[p.value for p in VideoProvider]}",
            )

        # Check if image exists
        if not os.path.exists(request.image_path):
            raise HTTPException(status_code=404, detail="Image file not found")

        # Generate video
        result = await video_client.generate_from_image(
            image_path=request.image_path,
            prompt=request.prompt,
            provider=provider,
            duration=request.duration,
            motion_strength=request.motion_strength,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        # Save to database
        db_video = VideoGeneration(
            user_id=current_user.id,
            prompt=request.prompt or "Image to video",
            provider=request.provider,
            duration=request.duration,
            video_url=result.get("video_url"),
            status="completed",
            metadata={"source_image": request.image_path, **result.get("metadata", {})},
            created_at=datetime.utcnow(),
        )

        db.add(db_video)
        db.commit()
        db.refresh(db_video)

        return {
            "success": True,
            "video": {
                "id": db_video.id,
                "video_url": db_video.video_url,
                "source_image": request.image_path,
                "prompt": db_video.prompt,
                "duration": db_video.duration,
                "provider": db_video.provider,
                "created_at": db_video.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate video from image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transform")
async def transform_video(
    request: TransformVideoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Transform existing video with AI

    Example:
    ```json
    {
        "video_path": "/path/to/video.mp4",
        "prompt": "Make it look like a watercolor painting",
        "provider": "runway",
        "strength": 0.7
    }
    ```
    """
    try:
        # Validate provider
        try:
            provider = VideoProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Supported: {[p.value for p in VideoProvider]}",
            )

        # Check if video exists
        if not os.path.exists(request.video_path):
            raise HTTPException(status_code=404, detail="Video file not found")

        # Transform video
        result = await video_client.transform_video(
            video_path=request.video_path,
            prompt=request.prompt,
            provider=provider,
            strength=request.strength,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        # Save to database
        db_video = VideoGeneration(
            user_id=current_user.id,
            prompt=request.prompt,
            provider=request.provider,
            video_url=result.get("video_url"),
            status="completed",
            metadata={
                "source_video": request.video_path,
                "operation": "transform",
                **result.get("metadata", {}),
            },
            created_at=datetime.utcnow(),
        )

        db.add(db_video)
        db.commit()
        db.refresh(db_video)

        return {
            "success": True,
            "video": {
                "id": db_video.id,
                "video_url": db_video.video_url,
                "source_video": request.video_path,
                "prompt": db_video.prompt,
                "provider": db_video.provider,
                "created_at": db_video.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to transform video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upscale")
async def upscale_video(
    request: UpscaleVideoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upscale video resolution

    Example:
    ```json
    {
        "video_path": "/path/to/video.mp4",
        "target_resolution": "4k",
        "enhance_quality": true
    }
    ```
    """
    try:
        # Validate resolution
        try:
            resolution = VideoResolution(request.target_resolution)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resolution. Supported: {[r.value for r in VideoResolution]}",
            )

        # Check if video exists
        if not os.path.exists(request.video_path):
            raise HTTPException(status_code=404, detail="Video file not found")

        # Upscale video
        result = await video_client.upscale_video(
            video_path=request.video_path,
            target_resolution=resolution,
            enhance_quality=request.enhance_quality,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        # Save to database
        db_video = VideoGeneration(
            user_id=current_user.id,
            prompt="Video upscaling",
            resolution=request.target_resolution,
            video_url=result.get("video_path"),
            status="completed",
            metadata={
                "source_video": request.video_path,
                "operation": "upscale",
                "enhanced": request.enhance_quality,
            },
            created_at=datetime.utcnow(),
        )

        db.add(db_video)
        db.commit()
        db.refresh(db_video)

        return {
            "success": True,
            "video": {
                "id": db_video.id,
                "video_path": result.get("video_path"),
                "source_video": request.video_path,
                "resolution": request.target_resolution,
                "enhanced": request.enhance_quality,
                "created_at": db_video.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upscale video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edit")
async def edit_video(
    request: EditVideoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Edit video (trim, merge, effects)

    Example for trim:
    ```json
    {
        "video_path": "/path/to/video.mp4",
        "operation": "trim",
        "parameters": {
            "start_time": 0,
            "end_time": 10
        }
    }
    ```

    Example for merge:
    ```json
    {
        "video_path": "/path/to/video1.mp4",
        "operation": "merge",
        "parameters": {
            "additional_videos": ["/path/to/video2.mp4", "/path/to/video3.mp4"]
        }
    }
    ```

    Example for effect:
    ```json
    {
        "video_path": "/path/to/video.mp4",
        "operation": "effect",
        "parameters": {
            "effect": "speed",
            "factor": 2.0
        }
    }
    ```
    """
    try:
        # Check if video exists
        if not os.path.exists(request.video_path):
            raise HTTPException(status_code=404, detail="Video file not found")

        # Edit video
        result = await video_client.edit_video(
            video_path=request.video_path,
            operation=request.operation,
            **request.parameters,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        # Save to database
        db_video = VideoGeneration(
            user_id=current_user.id,
            prompt=f"Video editing: {request.operation}",
            video_url=result.get("video_path"),
            status="completed",
            metadata={
                "source_video": request.video_path,
                "operation": request.operation,
                "parameters": request.parameters,
            },
            created_at=datetime.utcnow(),
        )

        db.add(db_video)
        db.commit()
        db.refresh(db_video)

        return {
            "success": True,
            "video": {
                "id": db_video.id,
                "video_path": result.get("video_path"),
                "source_video": request.video_path,
                "operation": request.operation,
                "created_at": db_video.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to edit video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generations")
async def list_generations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all video generations for current user"""
    try:
        videos = (
            db.query(VideoGeneration)
            .filter(VideoGeneration.user_id == current_user.id)
            .order_by(VideoGeneration.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return {
            "success": True,
            "videos": [
                {
                    "id": video.id,
                    "prompt": video.prompt,
                    "provider": video.provider,
                    "duration": video.duration,
                    "resolution": video.resolution,
                    "video_url": video.video_url,
                    "status": video.status,
                    "created_at": video.created_at.isoformat(),
                }
                for video in videos
            ],
            "total": len(videos),
        }

    except Exception as e:
        logger.error(f"Failed to list video generations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generations/{video_id}")
async def get_generation(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific video generation"""
    try:
        video = (
            db.query(VideoGeneration)
            .filter(
                VideoGeneration.id == video_id,
                VideoGeneration.user_id == current_user.id,
            )
            .first()
        )

        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        return {
            "success": True,
            "video": {
                "id": video.id,
                "prompt": video.prompt,
                "provider": video.provider,
                "duration": video.duration,
                "resolution": video.resolution,
                "video_url": video.video_url,
                "status": video.status,
                "metadata": video.metadata,
                "created_at": video.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/generations/{video_id}")
async def delete_generation(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete video generation"""
    try:
        video = (
            db.query(VideoGeneration)
            .filter(
                VideoGeneration.id == video_id,
                VideoGeneration.user_id == current_user.id,
            )
            .first()
        )

        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        db.delete(video)
        db.commit()

        return {
            "success": True,
            "message": f"Video generation {video_id} deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete video generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def list_providers(current_user: User = Depends(get_current_user)):
    """List available video generation providers"""
    try:
        providers = video_client.get_providers()

        return {"success": True, "providers": providers}

    except Exception as e:
        logger.error(f"Failed to list providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
