"""
Application Hosting Service for iTechSmart Ninja
Provides container orchestration and application deployment
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AppStatus(str, Enum):
    """Application deployment status"""

    DEPLOYING = "deploying"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    SCALING = "scaling"
    UPDATING = "updating"
    TERMINATED = "terminated"


class AppType(str, Enum):
    """Application types"""

    WEB = "web"
    API = "api"
    WORKER = "worker"
    SCHEDULED = "scheduled"
    STATIC = "static"


class ScalingPolicy(str, Enum):
    """Auto-scaling policies"""

    MANUAL = "manual"
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    REQUEST_BASED = "request_based"
    CUSTOM = "custom"


@dataclass
class ResourceLimits:
    """Resource limits for application"""

    cpu_cores: float = 1.0
    memory_mb: int = 512
    disk_gb: int = 10
    max_instances: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EnvironmentConfig:
    """Environment configuration"""

    variables: Dict[str, str]
    secrets: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "variables": self.variables,
            "secrets": {k: "***" for k in self.secrets.keys()},  # Mask secrets
        }


@dataclass
class DomainConfig:
    """Domain configuration"""

    domain: str
    ssl_enabled: bool = True
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    redirect_http: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "ssl_enabled": self.ssl_enabled,
            "ssl_cert": "***" if self.ssl_cert else None,
            "ssl_key": "***" if self.ssl_key else None,
            "redirect_http": self.redirect_http,
        }


@dataclass
class HealthCheck:
    """Health check configuration"""

    enabled: bool = True
    path: str = "/health"
    interval_seconds: int = 30
    timeout_seconds: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AutoScaling:
    """Auto-scaling configuration"""

    enabled: bool = False
    policy: ScalingPolicy = ScalingPolicy.MANUAL
    min_instances: int = 1
    max_instances: int = 5
    target_cpu_percent: Optional[int] = 70
    target_memory_percent: Optional[int] = 80
    target_requests_per_second: Optional[int] = 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "policy": self.policy.value,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "target_cpu_percent": self.target_cpu_percent,
            "target_memory_percent": self.target_memory_percent,
            "target_requests_per_second": self.target_requests_per_second,
        }


@dataclass
class DeploymentConfig:
    """Deployment configuration"""

    image: str
    port: int
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    working_dir: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image": self.image,
            "port": self.port,
            "command": self.command,
            "args": self.args,
            "working_dir": self.working_dir,
        }


@dataclass
class Application:
    """Hosted application"""

    app_id: str
    name: str
    description: str
    app_type: AppType
    status: AppStatus
    deployment: DeploymentConfig
    resources: ResourceLimits
    environment: EnvironmentConfig
    domains: List[DomainConfig]
    health_check: HealthCheck
    auto_scaling: AutoScaling
    current_instances: int
    owner_id: str
    created_at: datetime
    updated_at: datetime
    deployed_at: Optional[datetime]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_id": self.app_id,
            "name": self.name,
            "description": self.description,
            "app_type": self.app_type.value,
            "status": self.status.value,
            "deployment": self.deployment.to_dict(),
            "resources": self.resources.to_dict(),
            "environment": self.environment.to_dict(),
            "domains": [d.to_dict() for d in self.domains],
            "health_check": self.health_check.to_dict(),
            "auto_scaling": self.auto_scaling.to_dict(),
            "current_instances": self.current_instances,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deployed_at": self.deployed_at.isoformat() if self.deployed_at else None,
            "metadata": self.metadata,
        }


@dataclass
class DeploymentLog:
    """Deployment log entry"""

    log_id: str
    app_id: str
    timestamp: datetime
    level: str  # info, warning, error
    message: str
    details: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "app_id": self.app_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class AppMetrics:
    """Application metrics"""

    app_id: str
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_mb: int
    disk_usage_gb: float
    network_in_mb: float
    network_out_mb: float
    requests_per_second: float
    response_time_ms: float
    error_rate_percent: float
    active_connections: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_id": self.app_id,
            "timestamp": self.timestamp.isoformat(),
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "disk_usage_gb": self.disk_usage_gb,
            "network_in_mb": self.network_in_mb,
            "network_out_mb": self.network_out_mb,
            "requests_per_second": self.requests_per_second,
            "response_time_ms": self.response_time_ms,
            "error_rate_percent": self.error_rate_percent,
            "active_connections": self.active_connections,
        }


class AppHostingService:
    """Manages application hosting and deployment"""

    def __init__(self):
        """Initialize app hosting service"""
        self.applications: Dict[str, Application] = {}
        self.deployment_logs: Dict[str, List[DeploymentLog]] = {}
        self.metrics: Dict[str, List[AppMetrics]] = {}
        logger.info("AppHostingService initialized successfully")

    async def create_application(
        self,
        name: str,
        description: str,
        app_type: AppType,
        deployment: DeploymentConfig,
        owner_id: str,
        resources: Optional[ResourceLimits] = None,
        environment: Optional[EnvironmentConfig] = None,
        domains: Optional[List[DomainConfig]] = None,
        health_check: Optional[HealthCheck] = None,
        auto_scaling: Optional[AutoScaling] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Application:
        """
        Create a new application

        Args:
            name: Application name
            description: Application description
            app_type: Application type
            deployment: Deployment configuration
            owner_id: Owner user ID
            resources: Resource limits
            environment: Environment configuration
            domains: Domain configurations
            health_check: Health check configuration
            auto_scaling: Auto-scaling configuration
            metadata: Additional metadata

        Returns:
            Application object
        """
        app_id = str(uuid.uuid4())

        application = Application(
            app_id=app_id,
            name=name,
            description=description,
            app_type=app_type,
            status=AppStatus.DEPLOYING,
            deployment=deployment,
            resources=resources or ResourceLimits(),
            environment=environment or EnvironmentConfig(variables={}, secrets={}),
            domains=domains or [],
            health_check=health_check or HealthCheck(),
            auto_scaling=auto_scaling or AutoScaling(),
            current_instances=0,
            owner_id=owner_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deployed_at=None,
            metadata=metadata or {},
        )

        self.applications[app_id] = application
        self.deployment_logs[app_id] = []
        self.metrics[app_id] = []

        # Log deployment start
        await self._add_log(app_id, "info", f"Application {name} created")

        logger.info(f"Application {app_id} created: {name}")
        return application

    async def deploy_application(self, app_id: str) -> Application:
        """Deploy an application"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"Application {app_id} not found")

        try:
            app.status = AppStatus.DEPLOYING
            await self._add_log(app_id, "info", "Starting deployment")

            # Simulate deployment steps
            await self._add_log(
                app_id, "info", f"Pulling image: {app.deployment.image}"
            )
            await self._add_log(app_id, "info", "Creating containers")
            await self._add_log(app_id, "info", "Configuring networking")

            if app.domains:
                await self._add_log(
                    app_id,
                    "info",
                    f"Configuring domains: {[d.domain for d in app.domains]}",
                )

            if app.health_check.enabled:
                await self._add_log(app_id, "info", "Configuring health checks")

            # Set initial instances
            initial_instances = (
                app.auto_scaling.min_instances if app.auto_scaling.enabled else 1
            )
            app.current_instances = initial_instances

            app.status = AppStatus.RUNNING
            app.deployed_at = datetime.now()
            app.updated_at = datetime.now()

            await self._add_log(
                app_id,
                "info",
                f"Deployment successful - {initial_instances} instance(s) running",
            )

            logger.info(f"Application {app_id} deployed successfully")
            return app

        except Exception as e:
            app.status = AppStatus.FAILED
            await self._add_log(app_id, "error", f"Deployment failed: {str(e)}")
            logger.error(f"Failed to deploy application {app_id}: {e}")
            raise

    async def scale_application(self, app_id: str, instances: int) -> Application:
        """Scale application to specified number of instances"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"Application {app_id} not found")

        if app.status != AppStatus.RUNNING:
            raise ValueError(f"Application {app_id} is not running")

        if instances < 1 or instances > app.resources.max_instances:
            raise ValueError(
                f"Instances must be between 1 and {app.resources.max_instances}"
            )

        try:
            app.status = AppStatus.SCALING
            old_instances = app.current_instances

            await self._add_log(
                app_id, "info", f"Scaling from {old_instances} to {instances} instances"
            )

            app.current_instances = instances
            app.status = AppStatus.RUNNING
            app.updated_at = datetime.now()

            await self._add_log(
                app_id, "info", f"Scaling completed - {instances} instance(s) running"
            )

            logger.info(f"Application {app_id} scaled to {instances} instances")
            return app

        except Exception as e:
            app.status = AppStatus.FAILED
            await self._add_log(app_id, "error", f"Scaling failed: {str(e)}")
            logger.error(f"Failed to scale application {app_id}: {e}")
            raise

    async def stop_application(self, app_id: str) -> Application:
        """Stop an application"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"Application {app_id} not found")

        app.status = AppStatus.STOPPED
        app.current_instances = 0
        app.updated_at = datetime.now()

        await self._add_log(app_id, "info", "Application stopped")

        logger.info(f"Application {app_id} stopped")
        return app

    async def restart_application(self, app_id: str) -> Application:
        """Restart an application"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"Application {app_id} not found")

        await self._add_log(app_id, "info", "Restarting application")

        # Stop and redeploy
        await self.stop_application(app_id)
        return await self.deploy_application(app_id)

    async def update_application(
        self, app_id: str, updates: Dict[str, Any]
    ) -> Application:
        """Update application configuration"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"Application {app_id} not found")

        app.status = AppStatus.UPDATING

        # Update fields
        if "description" in updates:
            app.description = updates["description"]

        if "environment" in updates:
            env_updates = updates["environment"]
            if "variables" in env_updates:
                app.environment.variables.update(env_updates["variables"])
            if "secrets" in env_updates:
                app.environment.secrets.update(env_updates["secrets"])

        if "domains" in updates:
            app.domains = [DomainConfig(**d) for d in updates["domains"]]

        app.status = AppStatus.RUNNING
        app.updated_at = datetime.now()

        await self._add_log(app_id, "info", "Application configuration updated")

        logger.info(f"Application {app_id} updated")
        return app

    async def add_domain(self, app_id: str, domain_config: DomainConfig) -> Application:
        """Add a domain to application"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"Application {app_id} not found")

        app.domains.append(domain_config)
        app.updated_at = datetime.now()

        await self._add_log(app_id, "info", f"Domain added: {domain_config.domain}")

        logger.info(f"Domain {domain_config.domain} added to application {app_id}")
        return app

    async def remove_domain(self, app_id: str, domain: str) -> Application:
        """Remove a domain from application"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"Application {app_id} not found")

        app.domains = [d for d in app.domains if d.domain != domain]
        app.updated_at = datetime.now()

        await self._add_log(app_id, "info", f"Domain removed: {domain}")

        logger.info(f"Domain {domain} removed from application {app_id}")
        return app

    async def get_application(self, app_id: str) -> Optional[Application]:
        """Get application by ID"""
        return self.applications.get(app_id)

    async def list_applications(
        self,
        owner_id: Optional[str] = None,
        status: Optional[AppStatus] = None,
        app_type: Optional[AppType] = None,
    ) -> List[Application]:
        """List applications with optional filtering"""
        apps = list(self.applications.values())

        if owner_id:
            apps = [a for a in apps if a.owner_id == owner_id]

        if status:
            apps = [a for a in apps if a.status == status]

        if app_type:
            apps = [a for a in apps if a.app_type == app_type]

        return apps

    async def get_deployment_logs(
        self, app_id: str, limit: Optional[int] = None
    ) -> List[DeploymentLog]:
        """Get deployment logs for an application"""
        logs = self.deployment_logs.get(app_id, [])

        if limit:
            logs = logs[-limit:]

        return logs

    async def get_metrics(
        self,
        app_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[AppMetrics]:
        """Get metrics for an application"""
        metrics = self.metrics.get(app_id, [])

        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]

        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]

        return metrics

    async def record_metrics(self, app_id: str, metrics: AppMetrics) -> bool:
        """Record metrics for an application"""
        if app_id not in self.metrics:
            self.metrics[app_id] = []

        self.metrics[app_id].append(metrics)

        # Keep only last 1000 metrics
        if len(self.metrics[app_id]) > 1000:
            self.metrics[app_id] = self.metrics[app_id][-1000:]

        return True

    async def delete_application(self, app_id: str) -> bool:
        """Delete an application"""
        if app_id in self.applications:
            # Stop application first
            await self.stop_application(app_id)

            # Delete application
            del self.applications[app_id]

            # Clean up logs and metrics
            if app_id in self.deployment_logs:
                del self.deployment_logs[app_id]
            if app_id in self.metrics:
                del self.metrics[app_id]

            logger.info(f"Application {app_id} deleted")
            return True
        return False

    async def _add_log(
        self,
        app_id: str,
        level: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Add a deployment log entry"""
        log = DeploymentLog(
            log_id=str(uuid.uuid4()),
            app_id=app_id,
            timestamp=datetime.now(),
            level=level,
            message=message,
            details=details,
        )

        if app_id not in self.deployment_logs:
            self.deployment_logs[app_id] = []

        self.deployment_logs[app_id].append(log)

        # Keep only last 1000 logs
        if len(self.deployment_logs[app_id]) > 1000:
            self.deployment_logs[app_id] = self.deployment_logs[app_id][-1000:]


# Global app hosting service instance
_app_hosting_service: Optional[AppHostingService] = None


def get_app_hosting_service() -> AppHostingService:
    """Get or create global app hosting service instance"""
    global _app_hosting_service
    if _app_hosting_service is None:
        _app_hosting_service = AppHostingService()
    return _app_hosting_service
