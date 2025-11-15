"""
Plugin Ecosystem API Endpoints
Provides REST API for plugin marketplace and management
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

from ..services.plugin_service import (
    plugin_service,
    PluginCategory,
    PluginPermission,
    PluginStatus
)

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


# Request Models
class PublishPluginRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=3, max_length=50, regex="^[a-z0-9-]+$")
    description: str = Field(..., min_length=10, max_length=1000)
    author: str
    author_email: EmailStr
    category: PluginCategory
    version: str = Field(..., regex=r"^\d+\.\d+\.\d+$")
    permissions: List[PluginPermission]
    tags: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    license: str = "MIT"
    icon_url: Optional[str] = None
    homepage_url: Optional[str] = None
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None


class UpdatePluginRequest(BaseModel):
    version: str = Field(..., regex=r"^\d+\.\d+\.\d+$")
    changelog: str = Field(..., min_length=10)
    min_platform_version: Optional[str] = None


class InstallPluginRequest(BaseModel):
    workspace_id: str
    version: Optional[str] = None
    config: Optional[dict] = None


class ExecutePluginRequest(BaseModel):
    method: str
    args: Optional[List] = None
    kwargs: Optional[dict] = None


class AddReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=5, max_length=100)
    comment: str = Field(..., min_length=10, max_length=1000)


# Response Models
class PluginResponse(BaseModel):
    success: bool
    plugin: Optional[dict] = None
    error: Optional[str] = None


class InstallationResponse(BaseModel):
    success: bool
    installation: Optional[dict] = None
    error: Optional[str] = None


class ReviewResponse(BaseModel):
    success: bool
    review: Optional[dict] = None
    error: Optional[str] = None


# Helper function to get current user
def get_current_user_id(user_id: str = Query(...)) -> str:
    """Get current authenticated user ID"""
    return user_id


# Marketplace Endpoints

@router.post("/publish", response_model=PluginResponse)
async def publish_plugin(
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(...),
    author: str = Form(...),
    author_email: str = Form(...),
    category: PluginCategory = Form(...),
    version: str = Form(...),
    permissions: str = Form(...),  # JSON string
    license: str = Form("MIT"),
    tags: Optional[str] = Form(None),  # JSON string
    dependencies: Optional[str] = Form(None),  # JSON string
    icon_url: Optional[str] = Form(None),
    homepage_url: Optional[str] = Form(None),
    documentation_url: Optional[str] = Form(None),
    repository_url: Optional[str] = Form(None),
    plugin_file: UploadFile = File(...),
    user_id: str = Query(...)
):
    """
    Publish plugin to marketplace
    
    Upload plugin as ZIP file containing:
    - main.py (plugin entry point)
    - requirements.txt (dependencies)
    - README.md (documentation)
    - LICENSE (license file)
    """
    import json
    
    # Parse JSON fields
    permissions_list = [PluginPermission(p) for p in json.loads(permissions)]
    tags_list = json.loads(tags) if tags else None
    dependencies_list = json.loads(dependencies) if dependencies else None
    
    # Read plugin file
    plugin_data = await plugin_file.read()
    
    result = plugin_service.publish_plugin(
        name=name,
        slug=slug,
        description=description,
        author=author,
        author_email=author_email,
        category=category,
        version=version,
        plugin_file=plugin_data,
        permissions=permissions_list,
        tags=tags_list,
        dependencies=dependencies_list,
        license=license,
        icon_url=icon_url,
        homepage_url=homepage_url,
        documentation_url=documentation_url,
        repository_url=repository_url
    )
    
    return PluginResponse(**result)


@router.get("/marketplace")
async def list_marketplace_plugins(
    query: Optional[str] = None,
    category: Optional[PluginCategory] = None,
    tags: Optional[str] = None,  # Comma-separated
    limit: int = Query(20, ge=1, le=100)
):
    """
    List plugins in marketplace
    
    Supports filtering by:
    - Search query (name/description)
    - Category
    - Tags
    """
    tags_list = tags.split(",") if tags else None
    
    plugins = plugin_service.search_plugins(
        query=query,
        category=category,
        tags=tags_list,
        limit=limit
    )
    
    return {
        "success": True,
        "total": len(plugins),
        "plugins": plugins
    }


@router.get("/{plugin_id}", response_model=PluginResponse)
async def get_plugin(plugin_id: str):
    """
    Get plugin details
    
    Returns complete plugin information including versions and reviews
    """
    plugin = plugin_service.get_plugin(plugin_id)
    
    if not plugin:
        return PluginResponse(success=False, error="Plugin not found")
    
    return PluginResponse(success=True, plugin=plugin.to_dict())


@router.get("/slug/{slug}", response_model=PluginResponse)
async def get_plugin_by_slug(slug: str):
    """
    Get plugin by slug
    
    Retrieves plugin using its unique slug identifier
    """
    plugin = plugin_service.get_plugin_by_slug(slug)
    
    if not plugin:
        return PluginResponse(success=False, error="Plugin not found")
    
    return PluginResponse(success=True, plugin=plugin.to_dict())


@router.post("/{plugin_id}/update", response_model=PluginResponse)
async def update_plugin(
    plugin_id: str,
    version: str = Form(...),
    changelog: str = Form(...),
    min_platform_version: Optional[str] = Form(None),
    plugin_file: UploadFile = File(...),
    user_id: str = Query(...)
):
    """
    Update plugin with new version
    
    Publishes new version while maintaining version history
    """
    plugin_data = await plugin_file.read()
    
    result = plugin_service.update_plugin(
        plugin_id=plugin_id,
        version=version,
        plugin_file=plugin_data,
        changelog=changelog,
        min_platform_version=min_platform_version
    )
    
    return PluginResponse(**result)


# Installation Endpoints

@router.post("/{plugin_id}/install", response_model=InstallationResponse)
async def install_plugin(
    plugin_id: str,
    request: InstallPluginRequest,
    user_id: str = Query(...)
):
    """
    Install plugin to workspace
    
    Downloads and installs plugin with specified configuration
    """
    result = plugin_service.install_plugin(
        plugin_id=plugin_id,
        workspace_id=request.workspace_id,
        user_id=user_id,
        version=request.version,
        config=request.config
    )
    
    return InstallationResponse(**result)


@router.delete("/installations/{installation_id}", response_model=InstallationResponse)
async def uninstall_plugin(
    installation_id: str,
    workspace_id: str = Query(...),
    user_id: str = Query(...)
):
    """
    Uninstall plugin from workspace
    
    Removes plugin and cleans up resources
    """
    result = plugin_service.uninstall_plugin(
        installation_id=installation_id,
        workspace_id=workspace_id
    )
    
    return InstallationResponse(**result)


@router.post("/installations/{installation_id}/enable")
async def enable_plugin(
    installation_id: str,
    user_id: str = Query(...)
):
    """
    Enable installed plugin
    
    Activates plugin for use
    """
    result = plugin_service.enable_plugin(installation_id)
    return result


@router.post("/installations/{installation_id}/disable")
async def disable_plugin(
    installation_id: str,
    user_id: str = Query(...)
):
    """
    Disable installed plugin
    
    Deactivates plugin without uninstalling
    """
    result = plugin_service.disable_plugin(installation_id)
    return result


@router.get("/workspace/{workspace_id}/installed")
async def list_installed_plugins(
    workspace_id: str,
    user_id: str = Query(...)
):
    """
    List installed plugins for workspace
    
    Returns all plugins installed in the workspace
    """
    installations = plugin_service.get_workspace_plugins(workspace_id)
    
    return {
        "success": True,
        "total": len(installations),
        "installations": installations
    }


# Execution Endpoints

@router.post("/installations/{installation_id}/execute")
async def execute_plugin(
    installation_id: str,
    request: ExecutePluginRequest,
    user_id: str = Query(...)
):
    """
    Execute plugin method
    
    Runs plugin code with specified method and parameters
    """
    args = request.args or []
    kwargs = request.kwargs or {}
    
    result = plugin_service.execute_plugin(
        installation_id=installation_id,
        method=request.method,
        *args,
        **kwargs
    )
    
    return result


# Review Endpoints

@router.post("/{plugin_id}/reviews", response_model=ReviewResponse)
async def add_review(
    plugin_id: str,
    request: AddReviewRequest,
    user_id: str = Query(...)
):
    """
    Add plugin review
    
    Submit rating and review for plugin
    """
    result = plugin_service.add_review(
        plugin_id=plugin_id,
        user_id=user_id,
        rating=request.rating,
        title=request.title,
        comment=request.comment
    )
    
    return ReviewResponse(**result)


@router.get("/{plugin_id}/reviews")
async def get_reviews(
    plugin_id: str,
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get plugin reviews
    
    Returns user reviews and ratings
    """
    reviews = plugin_service.get_plugin_reviews(plugin_id, limit)
    
    return {
        "success": True,
        "total": len(reviews),
        "reviews": reviews
    }


# Statistics Endpoints

@router.get("/{plugin_id}/stats")
async def get_plugin_stats(plugin_id: str):
    """
    Get plugin statistics
    
    Returns download count, ratings, and usage metrics
    """
    plugin = plugin_service.get_plugin(plugin_id)
    
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    return {
        "success": True,
        "stats": {
            "downloads": plugin.downloads,
            "rating": plugin.rating,
            "reviews_count": plugin.reviews_count,
            "versions_count": len(plugin.versions),
            "current_version": plugin.current_version,
            "created_at": plugin.created_at.isoformat(),
            "updated_at": plugin.updated_at.isoformat()
        }
    }


@router.get("/categories/list")
async def list_categories():
    """
    List all plugin categories
    
    Returns available categories for filtering
    """
    categories = [
        {
            "value": cat.value,
            "label": cat.value.replace("_", " ").title()
        }
        for cat in PluginCategory
    ]
    
    return {
        "success": True,
        "categories": categories
    }


@router.get("/permissions/list")
async def list_permissions():
    """
    List all plugin permissions
    
    Returns available permissions for plugin development
    """
    permissions = [
        {
            "value": perm.value,
            "label": perm.value.replace("_", " ").title(),
            "description": f"Allows plugin to {perm.value.replace('_', ' ')}"
        }
        for perm in PluginPermission
    ]
    
    return {
        "success": True,
        "permissions": permissions
    }


@router.get("/trending")
async def get_trending_plugins(
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get trending plugins
    
    Returns most popular plugins by downloads and ratings
    """
    all_plugins = [
        p.to_dict() for p in plugin_service.plugins.values()
        if p.status == PluginStatus.PUBLISHED
    ]
    
    # Sort by downloads and rating
    trending = sorted(
        all_plugins,
        key=lambda x: (x["downloads"], x["rating"]),
        reverse=True
    )[:limit]
    
    return {
        "success": True,
        "plugins": trending
    }


@router.get("/featured")
async def get_featured_plugins(
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get featured plugins
    
    Returns curated list of high-quality plugins
    """
    all_plugins = [
        p.to_dict() for p in plugin_service.plugins.values()
        if p.status == PluginStatus.PUBLISHED and p.rating >= 4.0
    ]
    
    # Sort by rating and reviews
    featured = sorted(
        all_plugins,
        key=lambda x: (x["rating"], x["reviews_count"]),
        reverse=True
    )[:limit]
    
    return {
        "success": True,
        "plugins": featured
    }