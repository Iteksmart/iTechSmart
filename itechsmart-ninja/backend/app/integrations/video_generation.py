"""
Video Generation Integration
AI-powered video generation from text, images, and video transformations
"""

import os
import asyncio
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import logging
import base64
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import video processing libraries
try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    logger.warning("replicate not installed")

try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
    import moviepy.video.fx.all as vfx
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.warning("moviepy not installed")

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    logger.warning("ffmpeg-python not installed")


class VideoProvider(str, Enum):
    """Supported video generation providers"""
    RUNWAY = "runway"
    STABILITY = "stability"
    PIKA = "pika"
    CUSTOM = "custom"


class VideoResolution(str, Enum):
    """Supported video resolutions"""
    SD = "720p"
    HD = "1080p"
    FHD = "1920p"
    UHD = "4k"


class VideoStyle(str, Enum):
    """Video style presets"""
    REALISTIC = "realistic"
    ANIMATED = "animated"
    CINEMATIC = "cinematic"
    ARTISTIC = "artistic"
    DOCUMENTARY = "documentary"
    ABSTRACT = "abstract"


class VideoGenerationClient:
    """Client for video generation operations"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("REPLICATE_API_TOKEN")
        self.temp_dir = tempfile.mkdtemp(prefix="video_gen_")
        
    async def generate_from_text(
        self,
        prompt: str,
        provider: VideoProvider = VideoProvider.RUNWAY,
        duration: int = 4,
        resolution: VideoResolution = VideoResolution.HD,
        style: Optional[VideoStyle] = None,
        motion_strength: float = 0.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt
        
        Args:
            prompt: Text description of the video
            provider: Video generation provider
            duration: Video duration in seconds (2-60)
            resolution: Output resolution
            style: Style preset
            motion_strength: Motion intensity (0.0-1.0)
            seed: Random seed for reproducibility
            
        Returns:
            Dict with video URL and metadata
        """
        try:
            if not REPLICATE_AVAILABLE:
                return {
                    "success": False,
                    "error": "Replicate library not installed"
                }
                
            logger.info(f"Generating video from text: {prompt[:50]}...")
            
            # Select model based on provider
            model = self._get_model(provider, "text-to-video")
            
            # Prepare input
            input_data = {
                "prompt": prompt,
                "duration": duration,
                "motion_strength": motion_strength
            }
            
            if seed:
                input_data["seed"] = seed
                
            if style:
                input_data["style"] = style.value
                
            # Generate video
            output = await self._run_model(model, input_data)
            
            if output:
                video_url = output if isinstance(output, str) else output[0]
                
                return {
                    "success": True,
                    "video_url": video_url,
                    "prompt": prompt,
                    "duration": duration,
                    "resolution": resolution.value,
                    "provider": provider.value,
                    "metadata": {
                        "style": style.value if style else None,
                        "motion_strength": motion_strength,
                        "seed": seed
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Video generation failed"
                }
                
        except Exception as e:
            logger.error(f"Failed to generate video from text: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def generate_from_image(
        self,
        image_path: str,
        prompt: Optional[str] = None,
        provider: VideoProvider = VideoProvider.RUNWAY,
        duration: int = 4,
        motion_strength: float = 0.5
    ) -> Dict[str, Any]:
        """
        Generate video from image
        
        Args:
            image_path: Path to input image
            prompt: Optional text prompt for guidance
            provider: Video generation provider
            duration: Video duration in seconds
            motion_strength: Motion intensity
            
        Returns:
            Dict with video URL and metadata
        """
        try:
            if not REPLICATE_AVAILABLE:
                return {
                    "success": False,
                    "error": "Replicate library not installed"
                }
                
            logger.info(f"Generating video from image: {image_path}")
            
            # Select model
            model = self._get_model(provider, "image-to-video")
            
            # Read image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
                
            # Prepare input
            input_data = {
                "image": f"data:image/png;base64,{image_data}",
                "duration": duration,
                "motion_strength": motion_strength
            }
            
            if prompt:
                input_data["prompt"] = prompt
                
            # Generate video
            output = await self._run_model(model, input_data)
            
            if output:
                video_url = output if isinstance(output, str) else output[0]
                
                return {
                    "success": True,
                    "video_url": video_url,
                    "source_image": image_path,
                    "prompt": prompt,
                    "duration": duration,
                    "provider": provider.value,
                    "metadata": {
                        "motion_strength": motion_strength
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Video generation failed"
                }
                
        except Exception as e:
            logger.error(f"Failed to generate video from image: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def transform_video(
        self,
        video_path: str,
        prompt: str,
        provider: VideoProvider = VideoProvider.RUNWAY,
        strength: float = 0.7
    ) -> Dict[str, Any]:
        """
        Transform existing video with AI
        
        Args:
            video_path: Path to input video
            prompt: Transformation description
            provider: Video generation provider
            strength: Transformation strength (0.0-1.0)
            
        Returns:
            Dict with transformed video URL
        """
        try:
            if not REPLICATE_AVAILABLE:
                return {
                    "success": False,
                    "error": "Replicate library not installed"
                }
                
            logger.info(f"Transforming video: {video_path}")
            
            # Select model
            model = self._get_model(provider, "video-to-video")
            
            # Read video
            with open(video_path, 'rb') as f:
                video_data = base64.b64encode(f.read()).decode()
                
            # Prepare input
            input_data = {
                "video": f"data:video/mp4;base64,{video_data}",
                "prompt": prompt,
                "strength": strength
            }
            
            # Transform video
            output = await self._run_model(model, input_data)
            
            if output:
                video_url = output if isinstance(output, str) else output[0]
                
                return {
                    "success": True,
                    "video_url": video_url,
                    "source_video": video_path,
                    "prompt": prompt,
                    "provider": provider.value,
                    "metadata": {
                        "strength": strength
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Video transformation failed"
                }
                
        except Exception as e:
            logger.error(f"Failed to transform video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def upscale_video(
        self,
        video_path: str,
        target_resolution: VideoResolution = VideoResolution.UHD,
        enhance_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Upscale video resolution
        
        Args:
            video_path: Path to input video
            target_resolution: Target resolution
            enhance_quality: Apply quality enhancement
            
        Returns:
            Dict with upscaled video path
        """
        try:
            if not FFMPEG_AVAILABLE:
                return {
                    "success": False,
                    "error": "ffmpeg-python not installed"
                }
                
            logger.info(f"Upscaling video: {video_path}")
            
            # Parse target resolution
            resolution_map = {
                VideoResolution.SD: (1280, 720),
                VideoResolution.HD: (1920, 1080),
                VideoResolution.FHD: (1920, 1080),
                VideoResolution.UHD: (3840, 2160)
            }
            
            width, height = resolution_map[target_resolution]
            
            # Generate output path
            output_path = os.path.join(
                self.temp_dir,
                f"upscaled_{os.path.basename(video_path)}"
            )
            
            # Upscale with ffmpeg
            stream = ffmpeg.input(video_path)
            
            if enhance_quality:
                stream = ffmpeg.filter(stream, 'scale', width, height, flags='lanczos')
                stream = ffmpeg.filter(stream, 'unsharp', 5, 5, 1.0, 5, 5, 0.0)
            else:
                stream = ffmpeg.filter(stream, 'scale', width, height)
                
            stream = ffmpeg.output(stream, output_path, vcodec='libx264', crf=18)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return {
                "success": True,
                "video_path": output_path,
                "source_video": video_path,
                "resolution": target_resolution.value,
                "enhanced": enhance_quality
            }
            
        except Exception as e:
            logger.error(f"Failed to upscale video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def edit_video(
        self,
        video_path: str,
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Edit video (trim, merge, effects)
        
        Args:
            video_path: Path to input video
            operation: Edit operation (trim, merge, effect)
            **kwargs: Operation-specific parameters
            
        Returns:
            Dict with edited video path
        """
        try:
            if not MOVIEPY_AVAILABLE:
                return {
                    "success": False,
                    "error": "moviepy not installed"
                }
                
            logger.info(f"Editing video: {video_path} ({operation})")
            
            if operation == "trim":
                return await self._trim_video(video_path, **kwargs)
            elif operation == "merge":
                return await self._merge_videos(video_path, **kwargs)
            elif operation == "effect":
                return await self._apply_effect(video_path, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
                
        except Exception as e:
            logger.error(f"Failed to edit video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _trim_video(
        self,
        video_path: str,
        start_time: float = 0,
        end_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Trim video to specified duration"""
        clip = VideoFileClip(video_path)
        
        if end_time is None:
            end_time = clip.duration
            
        trimmed = clip.subclip(start_time, end_time)
        
        output_path = os.path.join(
            self.temp_dir,
            f"trimmed_{os.path.basename(video_path)}"
        )
        
        trimmed.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        clip.close()
        trimmed.close()
        
        return {
            "success": True,
            "video_path": output_path,
            "operation": "trim",
            "start_time": start_time,
            "end_time": end_time
        }
        
    async def _merge_videos(
        self,
        video_path: str,
        additional_videos: List[str]
    ) -> Dict[str, Any]:
        """Merge multiple videos"""
        clips = [VideoFileClip(video_path)]
        
        for video in additional_videos:
            clips.append(VideoFileClip(video))
            
        merged = concatenate_videoclips(clips)
        
        output_path = os.path.join(
            self.temp_dir,
            f"merged_{os.path.basename(video_path)}"
        )
        
        merged.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        for clip in clips:
            clip.close()
        merged.close()
        
        return {
            "success": True,
            "video_path": output_path,
            "operation": "merge",
            "video_count": len(clips)
        }
        
    async def _apply_effect(
        self,
        video_path: str,
        effect: str,
        **params
    ) -> Dict[str, Any]:
        """Apply video effect"""
        clip = VideoFileClip(video_path)
        
        # Apply effect
        if effect == "speed":
            speed_factor = params.get("factor", 1.0)
            clip = clip.fx(vfx.speedx, speed_factor)
        elif effect == "reverse":
            clip = clip.fx(vfx.time_mirror)
        elif effect == "fade":
            duration = params.get("duration", 1.0)
            clip = clip.fx(vfx.fadein, duration).fx(vfx.fadeout, duration)
        elif effect == "blur":
            clip = clip.fx(vfx.blur, 5)
        else:
            return {
                "success": False,
                "error": f"Unknown effect: {effect}"
            }
            
        output_path = os.path.join(
            self.temp_dir,
            f"{effect}_{os.path.basename(video_path)}"
        )
        
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        clip.close()
        
        return {
            "success": True,
            "video_path": output_path,
            "operation": "effect",
            "effect": effect,
            "params": params
        }
        
    def _get_model(self, provider: VideoProvider, task: str) -> str:
        """Get model identifier for provider and task"""
        models = {
            VideoProvider.RUNWAY: {
                "text-to-video": "runwayml/gen-2",
                "image-to-video": "runwayml/gen-2",
                "video-to-video": "runwayml/gen-2"
            },
            VideoProvider.STABILITY: {
                "text-to-video": "stability-ai/stable-video-diffusion",
                "image-to-video": "stability-ai/stable-video-diffusion",
                "video-to-video": "stability-ai/stable-video-diffusion"
            },
            VideoProvider.PIKA: {
                "text-to-video": "pika/pika-1.0",
                "image-to-video": "pika/pika-1.0",
                "video-to-video": "pika/pika-1.0"
            }
        }
        
        return models.get(provider, {}).get(task, "runwayml/gen-2")
        
    async def _run_model(self, model: str, input_data: Dict) -> Any:
        """Run model with replicate"""
        if not self.api_key:
            raise ValueError("Replicate API key not configured")
            
        # Run model asynchronously
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(
            None,
            lambda: replicate.run(model, input=input_data)
        )
        
        return output
        
    def get_providers(self) -> List[Dict[str, Any]]:
        """Get list of available video providers"""
        providers = [
            {
                "id": VideoProvider.RUNWAY.value,
                "name": "Runway Gen-2",
                "capabilities": ["text-to-video", "image-to-video", "video-to-video"],
                "max_duration": 16,
                "resolutions": ["720p", "1080p"]
            },
            {
                "id": VideoProvider.STABILITY.value,
                "name": "Stability AI Video",
                "capabilities": ["text-to-video", "image-to-video"],
                "max_duration": 4,
                "resolutions": ["720p", "1080p"]
            },
            {
                "id": VideoProvider.PIKA.value,
                "name": "Pika Labs",
                "capabilities": ["text-to-video", "image-to-video"],
                "max_duration": 3,
                "resolutions": ["720p", "1080p"]
            }
        ]
        
        return providers
        
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temp directory: {self.temp_dir}")


# Global video generation client
video_client = VideoGenerationClient()