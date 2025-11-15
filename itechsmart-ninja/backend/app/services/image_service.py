"""
Image Editing and Enhancement Service
Provides AI-powered image manipulation, enhancement, and editing capabilities
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import io
import base64
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImageFormat(str, Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"


class FilterType(str, Enum):
    """Available image filters"""
    BLUR = "blur"
    SHARPEN = "sharpen"
    SMOOTH = "smooth"
    EDGE_ENHANCE = "edge_enhance"
    EMBOSS = "emboss"
    CONTOUR = "contour"
    DETAIL = "detail"
    FIND_EDGES = "find_edges"


class EnhancementType(str, Enum):
    """Image enhancement types"""
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    COLOR = "color"
    SHARPNESS = "sharpness"


class ResizeMode(str, Enum):
    """Image resize modes"""
    EXACT = "exact"
    FIT = "fit"
    FILL = "fill"
    CROP = "crop"


class ImageOperation:
    """Represents a single image operation"""
    
    def __init__(
        self,
        operation_type: str,
        parameters: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.operation_type = operation_type
        self.parameters = parameters
        self.timestamp = timestamp or datetime.utcnow()
        self.operation_id = f"op_{int(self.timestamp.timestamp() * 1000)}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "parameters": self.parameters,
            "timestamp": self.timestamp.isoformat()
        }


class ImageEditor:
    """Core image editing functionality"""
    
    def __init__(self):
        self.history: List[ImageOperation] = []
        self.current_image: Optional[Image.Image] = None
        self.original_image: Optional[Image.Image] = None
    
    def load_image(self, image_data: bytes) -> Dict[str, Any]:
        """Load image from bytes"""
        try:
            self.current_image = Image.open(io.BytesIO(image_data))
            self.original_image = self.current_image.copy()
            
            return {
                "success": True,
                "width": self.current_image.width,
                "height": self.current_image.height,
                "format": self.current_image.format,
                "mode": self.current_image.mode
            }
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return {"success": False, "error": str(e)}
    
    def resize(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        mode: ResizeMode = ResizeMode.FIT,
        maintain_aspect: bool = True
    ) -> Dict[str, Any]:
        """Resize image with various modes"""
        if not self.current_image:
            return {"success": False, "error": "No image loaded"}
        
        try:
            original_size = self.current_image.size
            
            if mode == ResizeMode.EXACT:
                new_size = (width or original_size[0], height or original_size[1])
                self.current_image = self.current_image.resize(new_size, Image.Resampling.LANCZOS)
            
            elif mode == ResizeMode.FIT:
                self.current_image.thumbnail((width or 9999, height or 9999), Image.Resampling.LANCZOS)
            
            elif mode == ResizeMode.FILL:
                # Calculate dimensions to fill target size
                target_ratio = width / height if width and height else 1
                img_ratio = original_size[0] / original_size[1]
                
                if img_ratio > target_ratio:
                    new_height = height
                    new_width = int(new_height * img_ratio)
                else:
                    new_width = width
                    new_height = int(new_width / img_ratio)
                
                self.current_image = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Crop to exact size
                left = (new_width - width) // 2
                top = (new_height - height) // 2
                self.current_image = self.current_image.crop((left, top, left + width, top + height))
            
            elif mode == ResizeMode.CROP:
                # Center crop to target size
                left = (original_size[0] - width) // 2
                top = (original_size[1] - height) // 2
                self.current_image = self.current_image.crop((left, top, left + width, top + height))
            
            operation = ImageOperation("resize", {
                "width": width,
                "height": height,
                "mode": mode.value,
                "maintain_aspect": maintain_aspect
            })
            self.history.append(operation)
            
            return {
                "success": True,
                "new_size": self.current_image.size,
                "operation_id": operation.operation_id
            }
        
        except Exception as e:
            logger.error(f"Resize failed: {e}")
            return {"success": False, "error": str(e)}
    
    def apply_filter(self, filter_type: FilterType) -> Dict[str, Any]:
        """Apply image filter"""
        if not self.current_image:
            return {"success": False, "error": "No image loaded"}
        
        try:
            filter_map = {
                FilterType.BLUR: ImageFilter.BLUR,
                FilterType.SHARPEN: ImageFilter.SHARPEN,
                FilterType.SMOOTH: ImageFilter.SMOOTH,
                FilterType.EDGE_ENHANCE: ImageFilter.EDGE_ENHANCE,
                FilterType.EMBOSS: ImageFilter.EMBOSS,
                FilterType.CONTOUR: ImageFilter.CONTOUR,
                FilterType.DETAIL: ImageFilter.DETAIL,
                FilterType.FIND_EDGES: ImageFilter.FIND_EDGES
            }
            
            self.current_image = self.current_image.filter(filter_map[filter_type])
            
            operation = ImageOperation("filter", {"filter_type": filter_type.value})
            self.history.append(operation)
            
            return {
                "success": True,
                "filter_applied": filter_type.value,
                "operation_id": operation.operation_id
            }
        
        except Exception as e:
            logger.error(f"Filter application failed: {e}")
            return {"success": False, "error": str(e)}
    
    def enhance(
        self,
        enhancement_type: EnhancementType,
        factor: float = 1.0
    ) -> Dict[str, Any]:
        """Enhance image properties"""
        if not self.current_image:
            return {"success": False, "error": "No image loaded"}
        
        try:
            enhancer_map = {
                EnhancementType.BRIGHTNESS: ImageEnhance.Brightness,
                EnhancementType.CONTRAST: ImageEnhance.Contrast,
                EnhancementType.COLOR: ImageEnhance.Color,
                EnhancementType.SHARPNESS: ImageEnhance.Sharpness
            }
            
            enhancer = enhancer_map[enhancement_type](self.current_image)
            self.current_image = enhancer.enhance(factor)
            
            operation = ImageOperation("enhance", {
                "enhancement_type": enhancement_type.value,
                "factor": factor
            })
            self.history.append(operation)
            
            return {
                "success": True,
                "enhancement_applied": enhancement_type.value,
                "factor": factor,
                "operation_id": operation.operation_id
            }
        
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            return {"success": False, "error": str(e)}
    
    def rotate(self, degrees: float, expand: bool = True) -> Dict[str, Any]:
        """Rotate image"""
        if not self.current_image:
            return {"success": False, "error": "No image loaded"}
        
        try:
            self.current_image = self.current_image.rotate(degrees, expand=expand)
            
            operation = ImageOperation("rotate", {
                "degrees": degrees,
                "expand": expand
            })
            self.history.append(operation)
            
            return {
                "success": True,
                "degrees": degrees,
                "new_size": self.current_image.size,
                "operation_id": operation.operation_id
            }
        
        except Exception as e:
            logger.error(f"Rotation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def flip(self, horizontal: bool = True) -> Dict[str, Any]:
        """Flip image horizontally or vertically"""
        if not self.current_image:
            return {"success": False, "error": "No image loaded"}
        
        try:
            if horizontal:
                self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
            
            operation = ImageOperation("flip", {"horizontal": horizontal})
            self.history.append(operation)
            
            return {
                "success": True,
                "direction": "horizontal" if horizontal else "vertical",
                "operation_id": operation.operation_id
            }
        
        except Exception as e:
            logger.error(f"Flip failed: {e}")
            return {"success": False, "error": str(e)}
    
    def crop(
        self,
        left: int,
        top: int,
        right: int,
        bottom: int
    ) -> Dict[str, Any]:
        """Crop image to specified region"""
        if not self.current_image:
            return {"success": False, "error": "No image loaded"}
        
        try:
            self.current_image = self.current_image.crop((left, top, right, bottom))
            
            operation = ImageOperation("crop", {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom
            })
            self.history.append(operation)
            
            return {
                "success": True,
                "new_size": self.current_image.size,
                "operation_id": operation.operation_id
            }
        
        except Exception as e:
            logger.error(f"Crop failed: {e}")
            return {"success": False, "error": str(e)}
    
    def add_text(
        self,
        text: str,
        position: Tuple[int, int],
        font_size: int = 20,
        color: str = "white",
        font_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add text overlay to image"""
        if not self.current_image:
            return {"success": False, "error": "No image loaded"}
        
        try:
            draw = ImageDraw.Draw(self.current_image)
            
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
            
            draw.text(position, text, fill=color, font=font)
            
            operation = ImageOperation("add_text", {
                "text": text,
                "position": position,
                "font_size": font_size,
                "color": color
            })
            self.history.append(operation)
            
            return {
                "success": True,
                "text_added": text,
                "operation_id": operation.operation_id
            }
        
        except Exception as e:
            logger.error(f"Text addition failed: {e}")
            return {"success": False, "error": str(e)}
    
    def convert_format(self, format: ImageFormat) -> Dict[str, Any]:
        """Convert image to different format"""
        if not self.current_image:
            return {"success": False, "error": "No image loaded"}
        
        try:
            # Convert mode if necessary
            if format == ImageFormat.JPEG and self.current_image.mode in ('RGBA', 'LA', 'P'):
                self.current_image = self.current_image.convert('RGB')
            
            operation = ImageOperation("convert_format", {"format": format.value})
            self.history.append(operation)
            
            return {
                "success": True,
                "new_format": format.value,
                "operation_id": operation.operation_id
            }
        
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            return {"success": False, "error": str(e)}
    
    def undo(self) -> Dict[str, Any]:
        """Undo last operation"""
        if not self.history:
            return {"success": False, "error": "No operations to undo"}
        
        try:
            self.history.pop()
            # Reapply all operations from original
            self.current_image = self.original_image.copy()
            
            for operation in self.history:
                # Reapply each operation
                self._reapply_operation(operation)
            
            return {
                "success": True,
                "operations_remaining": len(self.history)
            }
        
        except Exception as e:
            logger.error(f"Undo failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _reapply_operation(self, operation: ImageOperation):
        """Reapply a single operation"""
        op_type = operation.operation_type
        params = operation.parameters
        
        if op_type == "resize":
            self.resize(**params)
        elif op_type == "filter":
            self.apply_filter(FilterType(params["filter_type"]))
        elif op_type == "enhance":
            self.enhance(EnhancementType(params["enhancement_type"]), params["factor"])
        elif op_type == "rotate":
            self.rotate(params["degrees"], params["expand"])
        elif op_type == "flip":
            self.flip(params["horizontal"])
        elif op_type == "crop":
            self.crop(**params)
        elif op_type == "add_text":
            self.add_text(**params)
    
    def get_image_bytes(self, format: ImageFormat = ImageFormat.PNG) -> bytes:
        """Get current image as bytes"""
        if not self.current_image:
            return b""
        
        buffer = io.BytesIO()
        self.current_image.save(buffer, format=format.value.upper())
        return buffer.getvalue()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get operation history"""
        return [op.to_dict() for op in self.history]


class ImageService:
    """High-level image service with batch processing"""
    
    def __init__(self):
        self.editors: Dict[str, ImageEditor] = {}
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """Create new editing session"""
        if session_id in self.editors:
            return {"success": False, "error": "Session already exists"}
        
        self.editors[session_id] = ImageEditor()
        return {
            "success": True,
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def get_editor(self, session_id: str) -> Optional[ImageEditor]:
        """Get editor for session"""
        return self.editors.get(session_id)
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete editing session"""
        if session_id not in self.editors:
            return {"success": False, "error": "Session not found"}
        
        del self.editors[session_id]
        return {"success": True, "session_id": session_id}
    
    def batch_process(
        self,
        images: List[bytes],
        operations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process multiple images with same operations"""
        results = []
        
        for idx, image_data in enumerate(images):
            session_id = f"batch_{idx}_{int(datetime.utcnow().timestamp())}"
            self.create_session(session_id)
            editor = self.get_editor(session_id)
            
            # Load image
            load_result = editor.load_image(image_data)
            if not load_result["success"]:
                results.append({
                    "index": idx,
                    "success": False,
                    "error": load_result["error"]
                })
                continue
            
            # Apply operations
            for operation in operations:
                op_type = operation["type"]
                params = operation.get("parameters", {})
                
                if op_type == "resize":
                    editor.resize(**params)
                elif op_type == "filter":
                    editor.apply_filter(FilterType(params["filter_type"]))
                elif op_type == "enhance":
                    editor.enhance(EnhancementType(params["enhancement_type"]), params.get("factor", 1.0))
                elif op_type == "rotate":
                    editor.rotate(**params)
                elif op_type == "flip":
                    editor.flip(**params)
                elif op_type == "crop":
                    editor.crop(**params)
            
            # Get result
            result_bytes = editor.get_image_bytes()
            results.append({
                "index": idx,
                "success": True,
                "image_data": base64.b64encode(result_bytes).decode(),
                "operations_applied": len(operations)
            })
            
            # Cleanup
            self.delete_session(session_id)
        
        return results


# Global service instance
image_service = ImageService()