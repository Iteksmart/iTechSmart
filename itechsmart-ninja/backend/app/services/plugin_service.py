"""
Plugin Ecosystem Service
Manages plugin marketplace, installation, and execution
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import json
import importlib.util
import sys
from pathlib import Path
import logging
import hashlib
import zipfile
import io

logger = logging.getLogger(__name__)


class PluginStatus(str, Enum):
    """Plugin status"""

    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    SUSPENDED = "suspended"


class PluginCategory(str, Enum):
    """Plugin categories"""

    AI_MODELS = "ai_models"
    DATA_PROCESSING = "data_processing"
    INTEGRATIONS = "integrations"
    AUTOMATION = "automation"
    ANALYTICS = "analytics"
    SECURITY = "security"
    UTILITIES = "utilities"
    CUSTOM = "custom"


class PluginPermission(str, Enum):
    """Plugin permissions"""

    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    NETWORK_ACCESS = "network_access"
    DATABASE_ACCESS = "database_access"
    API_ACCESS = "api_access"
    SYSTEM_COMMANDS = "system_commands"
    USER_DATA = "user_data"


@dataclass
class PluginVersion:
    """Plugin version information"""

    version: str
    release_date: datetime
    changelog: str
    download_url: str
    file_hash: str
    file_size: int
    min_platform_version: str

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "release_date": self.release_date.isoformat()}


@dataclass
class PluginMetadata:
    """Plugin metadata"""

    plugin_id: str
    name: str
    slug: str
    description: str
    author: str
    author_email: str
    category: PluginCategory
    tags: List[str]
    icon_url: Optional[str]
    homepage_url: Optional[str]
    documentation_url: Optional[str]
    repository_url: Optional[str]
    license: str
    current_version: str
    versions: List[PluginVersion]
    permissions: List[PluginPermission]
    dependencies: List[str]
    status: PluginStatus
    created_at: datetime
    updated_at: datetime
    downloads: int
    rating: float
    reviews_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "author": self.author,
            "author_email": self.author_email,
            "category": self.category.value,
            "tags": self.tags,
            "icon_url": self.icon_url,
            "homepage_url": self.homepage_url,
            "documentation_url": self.documentation_url,
            "repository_url": self.repository_url,
            "license": self.license,
            "current_version": self.current_version,
            "versions": [v.to_dict() for v in self.versions],
            "permissions": [p.value for p in self.permissions],
            "dependencies": self.dependencies,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "downloads": self.downloads,
            "rating": self.rating,
            "reviews_count": self.reviews_count,
        }


@dataclass
class InstalledPlugin:
    """Installed plugin information"""

    installation_id: str
    plugin_id: str
    workspace_id: str
    version: str
    installed_at: datetime
    installed_by: str
    enabled: bool
    config: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "installed_at": self.installed_at.isoformat()}


@dataclass
class PluginReview:
    """Plugin review"""

    review_id: str
    plugin_id: str
    user_id: str
    rating: int
    title: str
    comment: str
    created_at: datetime
    helpful_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "created_at": self.created_at.isoformat()}


class PluginExecutor:
    """Executes plugin code safely"""

    def __init__(self, plugin_path: Path, permissions: List[PluginPermission]):
        self.plugin_path = plugin_path
        self.permissions = permissions
        self.module = None

    def load(self) -> Dict[str, Any]:
        """Load plugin module"""
        try:
            spec = importlib.util.spec_from_file_location(
                "plugin_module", self.plugin_path / "main.py"
            )

            if not spec or not spec.loader:
                return {"success": False, "error": "Invalid plugin structure"}

            self.module = importlib.util.module_from_spec(spec)
            sys.modules["plugin_module"] = self.module
            spec.loader.exec_module(self.module)

            # Validate plugin interface
            if not hasattr(self.module, "Plugin"):
                return {"success": False, "error": "Plugin class not found"}

            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to load plugin: {e}")
            return {"success": False, "error": str(e)}

    def execute(self, method: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute plugin method"""
        if not self.module:
            return {"success": False, "error": "Plugin not loaded"}

        try:
            plugin_instance = self.module.Plugin()

            if not hasattr(plugin_instance, method):
                return {"success": False, "error": f"Method {method} not found"}

            # Check permissions before execution
            if not self._check_permissions(method):
                return {"success": False, "error": "Insufficient permissions"}

            result = getattr(plugin_instance, method)(*args, **kwargs)

            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"Plugin execution failed: {e}")
            return {"success": False, "error": str(e)}

    def _check_permissions(self, method: str) -> bool:
        """Check if plugin has required permissions"""
        # Simplified permission check
        # In production, implement granular permission checking
        return True


class PluginService:
    """Manages plugin ecosystem"""

    def __init__(self):
        self.plugins: Dict[str, PluginMetadata] = {}
        self.installed_plugins: Dict[str, InstalledPlugin] = {}
        self.reviews: Dict[str, List[PluginReview]] = {}
        self.plugin_slugs: Dict[str, str] = {}  # slug -> plugin_id
        self.workspace_plugins: Dict[str, Set[str]] = {}  # workspace_id -> plugin_ids
        self.plugin_executors: Dict[str, PluginExecutor] = {}

        # Plugin storage path
        self.plugins_dir = Path("/workspace/plugins")
        self.plugins_dir.mkdir(exist_ok=True)

    def publish_plugin(
        self,
        name: str,
        slug: str,
        description: str,
        author: str,
        author_email: str,
        category: PluginCategory,
        version: str,
        plugin_file: bytes,
        permissions: List[PluginPermission],
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        license: str = "MIT",
        **metadata,
    ) -> Dict[str, Any]:
        """Publish new plugin to marketplace"""
        try:
            # Validate slug uniqueness
            if slug in self.plugin_slugs:
                return {"success": False, "error": "Plugin slug already exists"}

            plugin_id = str(uuid.uuid4())
            now = datetime.utcnow()

            # Calculate file hash
            file_hash = hashlib.sha256(plugin_file).hexdigest()

            # Create version
            plugin_version = PluginVersion(
                version=version,
                release_date=now,
                changelog="Initial release",
                download_url=f"/plugins/{plugin_id}/{version}/download",
                file_hash=file_hash,
                file_size=len(plugin_file),
                min_platform_version="0.9.0",
            )

            # Create plugin metadata
            plugin = PluginMetadata(
                plugin_id=plugin_id,
                name=name,
                slug=slug,
                description=description,
                author=author,
                author_email=author_email,
                category=category,
                tags=tags or [],
                icon_url=metadata.get("icon_url"),
                homepage_url=metadata.get("homepage_url"),
                documentation_url=metadata.get("documentation_url"),
                repository_url=metadata.get("repository_url"),
                license=license,
                current_version=version,
                versions=[plugin_version],
                permissions=permissions,
                dependencies=dependencies or [],
                status=PluginStatus.PUBLISHED,
                created_at=now,
                updated_at=now,
                downloads=0,
                rating=0.0,
                reviews_count=0,
            )

            # Save plugin file
            plugin_dir = self.plugins_dir / plugin_id / version
            plugin_dir.mkdir(parents=True, exist_ok=True)

            # Extract plugin archive
            with zipfile.ZipFile(io.BytesIO(plugin_file)) as zf:
                zf.extractall(plugin_dir)

            self.plugins[plugin_id] = plugin
            self.plugin_slugs[slug] = plugin_id

            logger.info(f"Published plugin {plugin_id}: {name}")

            return {"success": True, "plugin": plugin.to_dict()}

        except Exception as e:
            logger.error(f"Failed to publish plugin: {e}")
            return {"success": False, "error": str(e)}

    def get_plugin(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get plugin by ID"""
        return self.plugins.get(plugin_id)

    def get_plugin_by_slug(self, slug: str) -> Optional[PluginMetadata]:
        """Get plugin by slug"""
        plugin_id = self.plugin_slugs.get(slug)
        return self.plugins.get(plugin_id) if plugin_id else None

    def update_plugin(
        self,
        plugin_id: str,
        version: str,
        plugin_file: bytes,
        changelog: str,
        **updates,
    ) -> Dict[str, Any]:
        """Update plugin with new version"""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return {"success": False, "error": "Plugin not found"}

        try:
            now = datetime.utcnow()

            # Calculate file hash
            file_hash = hashlib.sha256(plugin_file).hexdigest()

            # Create new version
            new_version = PluginVersion(
                version=version,
                release_date=now,
                changelog=changelog,
                download_url=f"/plugins/{plugin_id}/{version}/download",
                file_hash=file_hash,
                file_size=len(plugin_file),
                min_platform_version=updates.get("min_platform_version", "0.9.0"),
            )

            # Save plugin file
            plugin_dir = self.plugins_dir / plugin_id / version
            plugin_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(io.BytesIO(plugin_file)) as zf:
                zf.extractall(plugin_dir)

            plugin.versions.append(new_version)
            plugin.current_version = version
            plugin.updated_at = now

            # Update other fields
            for field, value in updates.items():
                if hasattr(plugin, field):
                    setattr(plugin, field, value)

            logger.info(f"Updated plugin {plugin_id} to version {version}")

            return {"success": True, "plugin": plugin.to_dict()}

        except Exception as e:
            logger.error(f"Failed to update plugin: {e}")
            return {"success": False, "error": str(e)}

    def install_plugin(
        self,
        plugin_id: str,
        workspace_id: str,
        user_id: str,
        version: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Install plugin to workspace"""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return {"success": False, "error": "Plugin not found"}

        if plugin.status != PluginStatus.PUBLISHED:
            return {"success": False, "error": "Plugin not available"}

        try:
            installation_id = str(uuid.uuid4())
            install_version = version or plugin.current_version

            # Check if version exists
            version_exists = any(v.version == install_version for v in plugin.versions)
            if not version_exists:
                return {"success": False, "error": "Version not found"}

            installation = InstalledPlugin(
                installation_id=installation_id,
                plugin_id=plugin_id,
                workspace_id=workspace_id,
                version=install_version,
                installed_at=datetime.utcnow(),
                installed_by=user_id,
                enabled=True,
                config=config or {},
            )

            self.installed_plugins[installation_id] = installation

            if workspace_id not in self.workspace_plugins:
                self.workspace_plugins[workspace_id] = set()
            self.workspace_plugins[workspace_id].add(installation_id)

            # Increment download count
            plugin.downloads += 1

            # Load plugin executor
            plugin_path = self.plugins_dir / plugin_id / install_version
            executor = PluginExecutor(plugin_path, plugin.permissions)
            load_result = executor.load()

            if load_result["success"]:
                self.plugin_executors[installation_id] = executor

            logger.info(f"Installed plugin {plugin_id} to workspace {workspace_id}")

            return {"success": True, "installation": installation.to_dict()}

        except Exception as e:
            logger.error(f"Failed to install plugin: {e}")
            return {"success": False, "error": str(e)}

    def uninstall_plugin(
        self, installation_id: str, workspace_id: str
    ) -> Dict[str, Any]:
        """Uninstall plugin from workspace"""
        installation = self.installed_plugins.get(installation_id)
        if not installation:
            return {"success": False, "error": "Installation not found"}

        if installation.workspace_id != workspace_id:
            return {"success": False, "error": "Access denied"}

        try:
            del self.installed_plugins[installation_id]
            self.workspace_plugins[workspace_id].discard(installation_id)

            if installation_id in self.plugin_executors:
                del self.plugin_executors[installation_id]

            logger.info(f"Uninstalled plugin {installation_id}")

            return {"success": True, "installation_id": installation_id}

        except Exception as e:
            logger.error(f"Failed to uninstall plugin: {e}")
            return {"success": False, "error": str(e)}

    def enable_plugin(self, installation_id: str) -> Dict[str, Any]:
        """Enable installed plugin"""
        installation = self.installed_plugins.get(installation_id)
        if not installation:
            return {"success": False, "error": "Installation not found"}

        installation.enabled = True
        return {"success": True, "installation": installation.to_dict()}

    def disable_plugin(self, installation_id: str) -> Dict[str, Any]:
        """Disable installed plugin"""
        installation = self.installed_plugins.get(installation_id)
        if not installation:
            return {"success": False, "error": "Installation not found"}

        installation.enabled = False
        return {"success": True, "installation": installation.to_dict()}

    def execute_plugin(
        self, installation_id: str, method: str, *args, **kwargs
    ) -> Dict[str, Any]:
        """Execute plugin method"""
        installation = self.installed_plugins.get(installation_id)
        if not installation:
            return {"success": False, "error": "Installation not found"}

        if not installation.enabled:
            return {"success": False, "error": "Plugin is disabled"}

        executor = self.plugin_executors.get(installation_id)
        if not executor:
            return {"success": False, "error": "Plugin not loaded"}

        return executor.execute(method, *args, **kwargs)

    def search_plugins(
        self,
        query: Optional[str] = None,
        category: Optional[PluginCategory] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search plugins in marketplace"""
        results = []

        for plugin in self.plugins.values():
            if plugin.status != PluginStatus.PUBLISHED:
                continue

            # Filter by query
            if query:
                query_lower = query.lower()
                if not (
                    query_lower in plugin.name.lower()
                    or query_lower in plugin.description.lower()
                ):
                    continue

            # Filter by category
            if category and plugin.category != category:
                continue

            # Filter by tags
            if tags:
                if not any(tag in plugin.tags for tag in tags):
                    continue

            results.append(plugin.to_dict())

            if len(results) >= limit:
                break

        # Sort by downloads and rating
        results.sort(key=lambda x: (x["downloads"], x["rating"]), reverse=True)

        return results

    def get_workspace_plugins(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get installed plugins for workspace"""
        installation_ids = self.workspace_plugins.get(workspace_id, set())

        installations = []
        for installation_id in installation_ids:
            installation = self.installed_plugins.get(installation_id)
            if installation:
                plugin = self.get_plugin(installation.plugin_id)
                install_dict = installation.to_dict()
                install_dict["plugin"] = plugin.to_dict() if plugin else None
                installations.append(install_dict)

        return installations

    def add_review(
        self, plugin_id: str, user_id: str, rating: int, title: str, comment: str
    ) -> Dict[str, Any]:
        """Add plugin review"""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return {"success": False, "error": "Plugin not found"}

        if rating < 1 or rating > 5:
            return {"success": False, "error": "Rating must be between 1 and 5"}

        try:
            review_id = str(uuid.uuid4())

            review = PluginReview(
                review_id=review_id,
                plugin_id=plugin_id,
                user_id=user_id,
                rating=rating,
                title=title,
                comment=comment,
                created_at=datetime.utcnow(),
                helpful_count=0,
            )

            if plugin_id not in self.reviews:
                self.reviews[plugin_id] = []
            self.reviews[plugin_id].append(review)

            # Update plugin rating
            all_ratings = [r.rating for r in self.reviews[plugin_id]]
            plugin.rating = sum(all_ratings) / len(all_ratings)
            plugin.reviews_count = len(all_ratings)

            logger.info(f"Added review for plugin {plugin_id}")

            return {"success": True, "review": review.to_dict()}

        except Exception as e:
            logger.error(f"Failed to add review: {e}")
            return {"success": False, "error": str(e)}

    def get_plugin_reviews(
        self, plugin_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get plugin reviews"""
        reviews = self.reviews.get(plugin_id, [])

        # Sort by helpful count and date
        sorted_reviews = sorted(
            reviews, key=lambda r: (r.helpful_count, r.created_at), reverse=True
        )

        return [r.to_dict() for r in sorted_reviews[:limit]]


# Global service instance
plugin_service = PluginService()
