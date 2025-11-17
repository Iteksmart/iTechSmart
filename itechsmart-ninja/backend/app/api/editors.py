"""
Editors API - Embedded code editors endpoints
Provides API for Monaco Editor, Image Editor, Website Builder, etc.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json
import yaml
import base64
from pathlib import Path

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User

router = APIRouter(prefix="/api/v1/editors", tags=["editors"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class EditorType(str):
    """Supported editor types"""

    MONACO = "monaco"
    IMAGE = "image"
    WEBSITE = "website"
    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"


class Language(str):
    """Supported programming languages"""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HTML = "html"
    CSS = "css"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    C = "c"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SQL = "sql"
    SHELL = "shell"
    DOCKERFILE = "dockerfile"


class MonacoEditorRequest(BaseModel):
    """Request to open Monaco editor"""

    file_path: Optional[str] = Field(None, description="Path to file to open")
    content: Optional[str] = Field(None, description="Initial content")
    language: str = Field("plaintext", description="Programming language")
    theme: str = Field("vs-dark", description="Editor theme (vs-dark, vs-light)")
    read_only: bool = Field(False, description="Read-only mode")


class MonacoEditorResponse(BaseModel):
    """Response from Monaco editor"""

    editor_id: str
    file_path: Optional[str]
    language: str
    theme: str
    content: str
    line_count: int
    character_count: int


class SaveFileRequest(BaseModel):
    """Request to save file from editor"""

    editor_id: str
    file_path: str
    content: str
    create_backup: bool = Field(True, description="Create backup before saving")


class ImageEditorRequest(BaseModel):
    """Request to open image editor"""

    image_path: Optional[str] = Field(None, description="Path to image file")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    width: int = Field(800, description="Canvas width")
    height: int = Field(600, description="Canvas height")


class ImageEditorResponse(BaseModel):
    """Response from image editor"""

    editor_id: str
    width: int
    height: int
    format: str
    has_image: bool


class ImageOperation(BaseModel):
    """Image editing operation"""

    operation: str = Field(
        ..., description="Operation type (filter, crop, resize, etc.)"
    )
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WebsiteBuilderRequest(BaseModel):
    """Request to open website builder"""

    project_name: str
    template: Optional[str] = Field(None, description="Template to use")
    existing_html: Optional[str] = Field(None, description="Existing HTML to load")


class WebsiteBuilderResponse(BaseModel):
    """Response from website builder"""

    editor_id: str
    project_name: str
    template: Optional[str]
    components_count: int


class ExportWebsiteRequest(BaseModel):
    """Request to export website"""

    editor_id: str
    format: str = Field("html", description="Export format (html, zip)")
    include_assets: bool = Field(True, description="Include CSS/JS/images")


class MarkdownEditorRequest(BaseModel):
    """Request to open markdown editor"""

    file_path: Optional[str] = Field(None, description="Path to markdown file")
    content: Optional[str] = Field(None, description="Initial markdown content")
    enable_preview: bool = Field(True, description="Enable live preview")


class MarkdownEditorResponse(BaseModel):
    """Response from markdown editor"""

    editor_id: str
    file_path: Optional[str]
    content: str
    preview_html: str
    word_count: int
    heading_count: int


class JSONEditorRequest(BaseModel):
    """Request to open JSON editor"""

    file_path: Optional[str] = Field(None, description="Path to JSON file")
    content: Optional[str] = Field(None, description="Initial JSON content")
    schema: Optional[Dict[str, Any]] = Field(
        None, description="JSON schema for validation"
    )


class JSONEditorResponse(BaseModel):
    """Response from JSON editor"""

    editor_id: str
    file_path: Optional[str]
    content: str
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)
    formatted: str


class YAMLEditorRequest(BaseModel):
    """Request to open YAML editor"""

    file_path: Optional[str] = Field(None, description="Path to YAML file")
    content: Optional[str] = Field(None, description="Initial YAML content")


class YAMLEditorResponse(BaseModel):
    """Response from YAML editor"""

    editor_id: str
    file_path: Optional[str]
    content: str
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)
    formatted: str
    json_equivalent: str


class EditorListResponse(BaseModel):
    """List of active editors"""

    editors: List[Dict[str, Any]]
    total: int


class EditorInfo(BaseModel):
    """Information about an editor"""

    editor_id: str
    editor_type: str
    created_at: datetime
    last_modified: datetime
    file_path: Optional[str]
    is_modified: bool


# ============================================================================
# EDITOR MANAGER
# ============================================================================


class EditorManager:
    """Manages active editor instances"""

    def __init__(self):
        self.editors: Dict[str, Dict[str, Any]] = {}

    def create_editor(self, editor_type: str, user_id: int, **kwargs) -> str:
        """Create a new editor instance"""
        import uuid

        editor_id = str(uuid.uuid4())

        self.editors[editor_id] = {
            "editor_id": editor_id,
            "editor_type": editor_type,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_modified": datetime.utcnow(),
            "is_modified": False,
            **kwargs,
        }

        return editor_id

    def get_editor(self, editor_id: str) -> Optional[Dict[str, Any]]:
        """Get editor by ID"""
        return self.editors.get(editor_id)

    def update_editor(self, editor_id: str, **kwargs):
        """Update editor data"""
        if editor_id in self.editors:
            self.editors[editor_id].update(kwargs)
            self.editors[editor_id]["last_modified"] = datetime.utcnow()
            self.editors[editor_id]["is_modified"] = True

    def delete_editor(self, editor_id: str):
        """Delete editor instance"""
        if editor_id in self.editors:
            del self.editors[editor_id]

    def list_editors(self, user_id: int) -> List[Dict[str, Any]]:
        """List all editors for a user"""
        return [
            editor for editor in self.editors.values() if editor["user_id"] == user_id
        ]


# Global editor manager instance
editor_manager = EditorManager()


# ============================================================================
# MONACO EDITOR ENDPOINTS
# ============================================================================


@router.post("/monaco/open", response_model=MonacoEditorResponse)
async def open_monaco_editor(
    request: MonacoEditorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Open Monaco code editor

    Features:
    - Syntax highlighting for 20+ languages
    - IntelliSense and autocomplete
    - Multiple themes
    - File operations
    """
    try:
        # Load content from file if provided
        content = request.content or ""
        if request.file_path:
            file_path = Path(request.file_path)
            if file_path.exists():
                content = file_path.read_text()
            else:
                raise HTTPException(status_code=404, detail="File not found")

        # Create editor instance
        editor_id = editor_manager.create_editor(
            editor_type=EditorType.MONACO,
            user_id=current_user.id,
            file_path=request.file_path,
            content=content,
            language=request.language,
            theme=request.theme,
            read_only=request.read_only,
        )

        return MonacoEditorResponse(
            editor_id=editor_id,
            file_path=request.file_path,
            language=request.language,
            theme=request.theme,
            content=content,
            line_count=len(content.split("\n")),
            character_count=len(content),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monaco/save")
async def save_monaco_file(
    request: SaveFileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save file from Monaco editor"""
    try:
        editor = editor_manager.get_editor(request.editor_id)
        if not editor:
            raise HTTPException(status_code=404, detail="Editor not found")

        if editor["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        file_path = Path(request.file_path)

        # Create backup if requested
        if request.create_backup and file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            backup_path.write_text(file_path.read_text())

        # Save file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(request.content)

        # Update editor
        editor_manager.update_editor(
            request.editor_id,
            content=request.content,
            file_path=request.file_path,
            is_modified=False,
        )

        return {
            "success": True,
            "message": "File saved successfully",
            "file_path": request.file_path,
            "size": len(request.content),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monaco/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    languages = [
        {"id": "python", "name": "Python", "extensions": [".py"]},
        {"id": "javascript", "name": "JavaScript", "extensions": [".js", ".mjs"]},
        {"id": "typescript", "name": "TypeScript", "extensions": [".ts"]},
        {"id": "html", "name": "HTML", "extensions": [".html", ".htm"]},
        {"id": "css", "name": "CSS", "extensions": [".css"]},
        {"id": "json", "name": "JSON", "extensions": [".json"]},
        {"id": "yaml", "name": "YAML", "extensions": [".yaml", ".yml"]},
        {"id": "markdown", "name": "Markdown", "extensions": [".md"]},
        {"id": "java", "name": "Java", "extensions": [".java"]},
        {"id": "go", "name": "Go", "extensions": [".go"]},
        {"id": "rust", "name": "Rust", "extensions": [".rs"]},
        {"id": "cpp", "name": "C++", "extensions": [".cpp", ".cc", ".cxx"]},
        {"id": "c", "name": "C", "extensions": [".c", ".h"]},
        {"id": "ruby", "name": "Ruby", "extensions": [".rb"]},
        {"id": "php", "name": "PHP", "extensions": [".php"]},
        {"id": "swift", "name": "Swift", "extensions": [".swift"]},
        {"id": "kotlin", "name": "Kotlin", "extensions": [".kt"]},
        {"id": "sql", "name": "SQL", "extensions": [".sql"]},
        {"id": "shell", "name": "Shell", "extensions": [".sh", ".bash"]},
        {"id": "dockerfile", "name": "Dockerfile", "extensions": ["Dockerfile"]},
    ]

    return {"languages": languages, "total": len(languages)}


# ============================================================================
# IMAGE EDITOR ENDPOINTS
# ============================================================================


@router.post("/image/open", response_model=ImageEditorResponse)
async def open_image_editor(
    request: ImageEditorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Open image editor with Fabric.js

    Features:
    - Drawing tools (pen, shapes, text)
    - Image filters and effects
    - Layer management
    - Export to PNG/JPG/SVG
    """
    try:
        image_data = request.image_data
        has_image = False

        # Load image from file if provided
        if request.image_path:
            file_path = Path(request.image_path)
            if file_path.exists():
                with open(file_path, "rb") as f:
                    image_bytes = f.read()
                    image_data = base64.b64encode(image_bytes).decode()
                    has_image = True
        elif request.image_data:
            has_image = True

        # Create editor instance
        editor_id = editor_manager.create_editor(
            editor_type=EditorType.IMAGE,
            user_id=current_user.id,
            image_path=request.image_path,
            image_data=image_data,
            width=request.width,
            height=request.height,
        )

        return ImageEditorResponse(
            editor_id=editor_id,
            width=request.width,
            height=request.height,
            format="png",
            has_image=has_image,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/apply-operation")
async def apply_image_operation(
    editor_id: str,
    operation: ImageOperation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply image editing operation"""
    try:
        editor = editor_manager.get_editor(editor_id)
        if not editor:
            raise HTTPException(status_code=404, detail="Editor not found")

        if editor["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Note: Actual image processing would be done on frontend with Fabric.js
        # This endpoint is for tracking operations

        return {
            "success": True,
            "operation": operation.operation,
            "parameters": operation.parameters,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/export")
async def export_image(
    editor_id: str,
    format: str = "png",
    quality: int = 90,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export image from editor"""
    try:
        editor = editor_manager.get_editor(editor_id)
        if not editor:
            raise HTTPException(status_code=404, detail="Editor not found")

        if editor["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        return {
            "success": True,
            "format": format,
            "quality": quality,
            "message": "Image ready for export",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBSITE BUILDER ENDPOINTS
# ============================================================================


@router.post("/website/open", response_model=WebsiteBuilderResponse)
async def open_website_builder(
    request: WebsiteBuilderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Open website builder with GrapesJS

    Features:
    - Drag-and-drop interface
    - Component library
    - Responsive design preview
    - Export HTML/CSS/JS
    """
    try:
        # Create editor instance
        editor_id = editor_manager.create_editor(
            editor_type=EditorType.WEBSITE,
            user_id=current_user.id,
            project_name=request.project_name,
            template=request.template,
            existing_html=request.existing_html,
        )

        return WebsiteBuilderResponse(
            editor_id=editor_id,
            project_name=request.project_name,
            template=request.template,
            components_count=0,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/website/export")
async def export_website(
    request: ExportWebsiteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export website from builder"""
    try:
        editor = editor_manager.get_editor(request.editor_id)
        if not editor:
            raise HTTPException(status_code=404, detail="Editor not found")

        if editor["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        return {
            "success": True,
            "format": request.format,
            "include_assets": request.include_assets,
            "message": "Website ready for export",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/website/templates")
async def get_website_templates():
    """Get available website templates"""
    templates = [
        {"id": "blank", "name": "Blank", "description": "Start from scratch"},
        {"id": "landing", "name": "Landing Page", "description": "Single page website"},
        {"id": "portfolio", "name": "Portfolio", "description": "Showcase your work"},
        {"id": "blog", "name": "Blog", "description": "Content-focused site"},
        {"id": "business", "name": "Business", "description": "Corporate website"},
    ]

    return {"templates": templates, "total": len(templates)}


# ============================================================================
# MARKDOWN EDITOR ENDPOINTS
# ============================================================================


@router.post("/markdown/open", response_model=MarkdownEditorResponse)
async def open_markdown_editor(
    request: MarkdownEditorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Open markdown editor with live preview

    Features:
    - Live HTML preview
    - Syntax highlighting
    - Table of contents
    - Export to HTML/PDF
    """
    try:
        # Load content from file if provided
        content = request.content or ""
        if request.file_path:
            file_path = Path(request.file_path)
            if file_path.exists():
                content = file_path.read_text()

        # Generate preview HTML (simplified)
        preview_html = f"<div>{content}</div>"  # Would use markdown library

        # Count words and headings
        word_count = len(content.split())
        heading_count = content.count("#")

        # Create editor instance
        editor_id = editor_manager.create_editor(
            editor_type=EditorType.MARKDOWN,
            user_id=current_user.id,
            file_path=request.file_path,
            content=content,
            enable_preview=request.enable_preview,
        )

        return MarkdownEditorResponse(
            editor_id=editor_id,
            file_path=request.file_path,
            content=content,
            preview_html=preview_html,
            word_count=word_count,
            heading_count=heading_count,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# JSON EDITOR ENDPOINTS
# ============================================================================


@router.post("/json/open", response_model=JSONEditorResponse)
async def open_json_editor(
    request: JSONEditorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Open JSON editor with validation

    Features:
    - Schema validation
    - Auto-formatting
    - Error highlighting
    - Tree view
    """
    try:
        # Load content from file if provided
        content = request.content or "{}"
        if request.file_path:
            file_path = Path(request.file_path)
            if file_path.exists():
                content = file_path.read_text()

        # Validate JSON
        is_valid = True
        validation_errors = []
        formatted = content

        try:
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=2)
        except json.JSONDecodeError as e:
            is_valid = False
            validation_errors.append(str(e))

        # Create editor instance
        editor_id = editor_manager.create_editor(
            editor_type=EditorType.JSON,
            user_id=current_user.id,
            file_path=request.file_path,
            content=content,
            schema=request.schema,
        )

        return JSONEditorResponse(
            editor_id=editor_id,
            file_path=request.file_path,
            content=content,
            is_valid=is_valid,
            validation_errors=validation_errors,
            formatted=formatted,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# YAML EDITOR ENDPOINTS
# ============================================================================


@router.post("/yaml/open", response_model=YAMLEditorResponse)
async def open_yaml_editor(
    request: YAMLEditorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Open YAML editor with validation

    Features:
    - Syntax validation
    - Auto-formatting
    - Error highlighting
    - JSON conversion
    """
    try:
        # Load content from file if provided
        content = request.content or ""
        if request.file_path:
            file_path = Path(request.file_path)
            if file_path.exists():
                content = file_path.read_text()

        # Validate YAML
        is_valid = True
        validation_errors = []
        formatted = content
        json_equivalent = "{}"

        try:
            parsed = yaml.safe_load(content)
            formatted = yaml.dump(parsed, default_flow_style=False)
            json_equivalent = json.dumps(parsed, indent=2)
        except yaml.YAMLError as e:
            is_valid = False
            validation_errors.append(str(e))

        # Create editor instance
        editor_id = editor_manager.create_editor(
            editor_type=EditorType.YAML,
            user_id=current_user.id,
            file_path=request.file_path,
            content=content,
        )

        return YAMLEditorResponse(
            editor_id=editor_id,
            file_path=request.file_path,
            content=content,
            is_valid=is_valid,
            validation_errors=validation_errors,
            formatted=formatted,
            json_equivalent=json_equivalent,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GENERAL EDITOR ENDPOINTS
# ============================================================================


@router.get("/list", response_model=EditorListResponse)
async def list_editors(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """List all active editors for current user"""
    try:
        editors = editor_manager.list_editors(current_user.id)

        return EditorListResponse(editors=editors, total=len(editors))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{editor_id}", response_model=EditorInfo)
async def get_editor_info(
    editor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get information about a specific editor"""
    try:
        editor = editor_manager.get_editor(editor_id)
        if not editor:
            raise HTTPException(status_code=404, detail="Editor not found")

        if editor["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        return EditorInfo(
            editor_id=editor["editor_id"],
            editor_type=editor["editor_type"],
            created_at=editor["created_at"],
            last_modified=editor["last_modified"],
            file_path=editor.get("file_path"),
            is_modified=editor["is_modified"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{editor_id}")
async def close_editor(
    editor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Close an editor"""
    try:
        editor = editor_manager.get_editor(editor_id)
        if not editor:
            raise HTTPException(status_code=404, detail="Editor not found")

        if editor["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        editor_manager.delete_editor(editor_id)

        return {"success": True, "message": "Editor closed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
