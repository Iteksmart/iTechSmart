"""
Application Hosting API Endpoints for iTechSmart Ninja
Provides REST API for application deployment and management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from ..core.app_hosting import (
    AppHostingService,
    Application,
    DeploymentConfig,
    ResourceLimits,
    EnvironmentConfig,
    DomainConfig,
    HealthCheck,
    AutoScaling,
    AppStatus,
    AppType,
    ScalingPolicy,
    get_app_hosting_service,
)

router = APIRouter(prefix="/app-hosting", tags=["app-hosting"])


# Request/Response Models
class DeploymentConfigRequest(BaseModel):
    """Request for deployment configuration"""

    image: str = Field(..., description="Docker image")
    port: int = Field(..., ge=1, le=65535, description="Application port")
    command: Optional[List[str]] = Field(default=None, description="Command to run")
    args: Optional[List[str]] = Field(default=None, description="Command arguments")
    working_dir: Optional[str] = Field(default=None, description="Working directory")


class ResourceLimitsRequest(BaseModel):
    """Request for resource limits"""

    cpu_cores: float = Field(default=1.0, ge=0.1, le=16.0)
    memory_mb: int = Field(default=512, ge=128, le=32768)
    disk_gb: int = Field(default=10, ge=1, le=1000)
    max_instances: int = Field(default=5, ge=1, le=100)


class EnvironmentConfigRequest(BaseModel):
    """Request for environment configuration"""

    variables: Dict[str, str] = Field(default_factory=dict)
    secrets: Dict[str, str] = Field(default_factory=dict)


class DomainConfigRequest(BaseModel):
    """Request for domain configuration"""

    domain: str = Field(..., description="Domain name")
    ssl_enabled: bool = Field(default=True)
    ssl_cert: Optional[str] = Field(default=None)
    ssl_key: Optional[str] = Field(default=None)
    redirect_http: bool = Field(default=True)


class HealthCheckRequest(BaseModel):
    """Request for health check configuration"""

    enabled: bool = Field(default=True)
    path: str = Field(default="/health")
    interval_seconds: int = Field(default=30, ge=5, le=300)
    timeout_seconds: int = Field(default=5, ge=1, le=60)
    healthy_threshold: int = Field(default=2, ge=1, le=10)
    unhealthy_threshold: int = Field(default=3, ge=1, le=10)


class AutoScalingRequest(BaseModel):
    """Request for auto-scaling configuration"""

    enabled: bool = Field(default=False)
    policy: str = Field(default="manual")
    min_instances: int = Field(default=1, ge=1, le=100)
    max_instances: int = Field(default=5, ge=1, le=100)
    target_cpu_percent: Optional[int] = Field(default=70, ge=1, le=100)
    target_memory_percent: Optional[int] = Field(default=80, ge=1, le=100)
    target_requests_per_second: Optional[int] = Field(default=100, ge=1)


class CreateApplicationRequest(BaseModel):
    """Request to create an application"""

    name: str = Field(..., description="Application name")
    description: str = Field(..., description="Application description")
    app_type: str = Field(..., description="Application type")
    deployment: DeploymentConfigRequest = Field(..., description="Deployment config")
    owner_id: str = Field(..., description="Owner user ID")
    resources: Optional[ResourceLimitsRequest] = Field(default=None)
    environment: Optional[EnvironmentConfigRequest] = Field(default=None)
    domains: Optional[List[DomainConfigRequest]] = Field(default=None)
    health_check: Optional[HealthCheckRequest] = Field(default=None)
    auto_scaling: Optional[AutoScalingRequest] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class UpdateApplicationRequest(BaseModel):
    """Request to update an application"""

    description: Optional[str] = None
    environment: Optional[EnvironmentConfigRequest] = None
    domains: Optional[List[DomainConfigRequest]] = None


class ScaleApplicationRequest(BaseModel):
    """Request to scale an application"""

    instances: int = Field(..., ge=1, le=100, description="Number of instances")


class ApplicationResponse(BaseModel):
    """Response with application information"""

    app_id: str
    name: str
    description: str
    app_type: str
    status: str
    deployment: Dict[str, Any]
    resources: Dict[str, Any]
    environment: Dict[str, Any]
    domains: List[Dict[str, Any]]
    health_check: Dict[str, Any]
    auto_scaling: Dict[str, Any]
    current_instances: int
    owner_id: str
    created_at: str
    updated_at: str
    deployed_at: Optional[str]
    metadata: Dict[str, Any]


class ApplicationListResponse(BaseModel):
    """Response with list of applications"""

    applications: List[ApplicationResponse]
    total: int


class DeploymentLogResponse(BaseModel):
    """Response with deployment log"""

    log_id: str
    app_id: str
    timestamp: str
    level: str
    message: str
    details: Optional[Dict[str, Any]]


class MetricsResponse(BaseModel):
    """Response with application metrics"""

    app_id: str
    timestamp: str
    cpu_usage_percent: float
    memory_usage_mb: int
    disk_usage_gb: float
    network_in_mb: float
    network_out_mb: float
    requests_per_second: float
    response_time_ms: float
    error_rate_percent: float
    active_connections: int


# API Endpoints
@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    request: CreateApplicationRequest,
    service: AppHostingService = Depends(get_app_hosting_service),
):
    """
    Create a new application

    **App Types:** web, api, worker, scheduled, static

    **Returns:**
    - Application information
    """
    try:
        # Convert request to objects
        deployment = DeploymentConfig(
            image=request.deployment.image,
            port=request.deployment.port,
            command=request.deployment.command,
            args=request.deployment.args,
            working_dir=request.deployment.working_dir,
        )

        resources = None
        if request.resources:
            resources = ResourceLimits(
                cpu_cores=request.resources.cpu_cores,
                memory_mb=request.resources.memory_mb,
                disk_gb=request.resources.disk_gb,
                max_instances=request.resources.max_instances,
            )

        environment = None
        if request.environment:
            environment = EnvironmentConfig(
                variables=request.environment.variables,
                secrets=request.environment.secrets,
            )

        domains = None
        if request.domains:
            domains = [
                DomainConfig(
                    domain=d.domain,
                    ssl_enabled=d.ssl_enabled,
                    ssl_cert=d.ssl_cert,
                    ssl_key=d.ssl_key,
                    redirect_http=d.redirect_http,
                )
                for d in request.domains
            ]

        health_check = None
        if request.health_check:
            health_check = HealthCheck(
                enabled=request.health_check.enabled,
                path=request.health_check.path,
                interval_seconds=request.health_check.interval_seconds,
                timeout_seconds=request.health_check.timeout_seconds,
                healthy_threshold=request.health_check.healthy_threshold,
                unhealthy_threshold=request.health_check.unhealthy_threshold,
            )

        auto_scaling = None
        if request.auto_scaling:
            auto_scaling = AutoScaling(
                enabled=request.auto_scaling.enabled,
                policy=ScalingPolicy(request.auto_scaling.policy),
                min_instances=request.auto_scaling.min_instances,
                max_instances=request.auto_scaling.max_instances,
                target_cpu_percent=request.auto_scaling.target_cpu_percent,
                target_memory_percent=request.auto_scaling.target_memory_percent,
                target_requests_per_second=request.auto_scaling.target_requests_per_second,
            )

        app = await service.create_application(
            name=request.name,
            description=request.description,
            app_type=AppType(request.app_type),
            deployment=deployment,
            owner_id=request.owner_id,
            resources=resources,
            environment=environment,
            domains=domains,
            health_check=health_check,
            auto_scaling=auto_scaling,
            metadata=request.metadata,
        )

        return ApplicationResponse(**app.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create application: {str(e)}"
        )


@router.post("/applications/{app_id}/deploy", response_model=ApplicationResponse)
async def deploy_application(
    app_id: str, service: AppHostingService = Depends(get_app_hosting_service)
):
    """Deploy an application"""
    try:
        app = await service.deploy_application(app_id)
        return ApplicationResponse(**app.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to deploy application: {str(e)}"
        )


@router.post("/applications/{app_id}/scale", response_model=ApplicationResponse)
async def scale_application(
    app_id: str,
    request: ScaleApplicationRequest,
    service: AppHostingService = Depends(get_app_hosting_service),
):
    """Scale an application"""
    try:
        app = await service.scale_application(app_id, request.instances)
        return ApplicationResponse(**app.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to scale application: {str(e)}"
        )


@router.post("/applications/{app_id}/stop", response_model=ApplicationResponse)
async def stop_application(
    app_id: str, service: AppHostingService = Depends(get_app_hosting_service)
):
    """Stop an application"""
    try:
        app = await service.stop_application(app_id)
        return ApplicationResponse(**app.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to stop application: {str(e)}"
        )


@router.post("/applications/{app_id}/restart", response_model=ApplicationResponse)
async def restart_application(
    app_id: str, service: AppHostingService = Depends(get_app_hosting_service)
):
    """Restart an application"""
    try:
        app = await service.restart_application(app_id)
        return ApplicationResponse(**app.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to restart application: {str(e)}"
        )


@router.put("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str,
    request: UpdateApplicationRequest,
    service: AppHostingService = Depends(get_app_hosting_service),
):
    """Update application configuration"""
    try:
        updates = request.dict(exclude_none=True)
        app = await service.update_application(app_id, updates)
        return ApplicationResponse(**app.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update application: {str(e)}"
        )


@router.post("/applications/{app_id}/domains")
async def add_domain(
    app_id: str,
    domain: DomainConfigRequest,
    service: AppHostingService = Depends(get_app_hosting_service),
):
    """Add a domain to application"""
    try:
        domain_config = DomainConfig(
            domain=domain.domain,
            ssl_enabled=domain.ssl_enabled,
            ssl_cert=domain.ssl_cert,
            ssl_key=domain.ssl_key,
            redirect_http=domain.redirect_http,
        )
        await service.add_domain(app_id, domain_config)
        return {"message": f"Domain {domain.domain} added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add domain: {str(e)}")


@router.delete("/applications/{app_id}/domains/{domain}")
async def remove_domain(
    app_id: str,
    domain: str,
    service: AppHostingService = Depends(get_app_hosting_service),
):
    """Remove a domain from application"""
    try:
        await service.remove_domain(app_id, domain)
        return {"message": f"Domain {domain} removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to remove domain: {str(e)}"
        )


@router.get("/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: str, service: AppHostingService = Depends(get_app_hosting_service)
):
    """Get application information"""
    app = await service.get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
    return ApplicationResponse(**app.to_dict())


@router.get("/applications", response_model=ApplicationListResponse)
async def list_applications(
    owner_id: Optional[str] = None,
    status: Optional[str] = None,
    app_type: Optional[str] = None,
    service: AppHostingService = Depends(get_app_hosting_service),
):
    """List all applications"""
    try:
        status_enum = AppStatus(status) if status else None
        type_enum = AppType(app_type) if app_type else None

        apps = await service.list_applications(
            owner_id=owner_id, status=status_enum, app_type=type_enum
        )

        return ApplicationListResponse(
            applications=[ApplicationResponse(**a.to_dict()) for a in apps],
            total=len(apps),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list applications: {str(e)}"
        )


@router.get("/applications/{app_id}/logs", response_model=List[DeploymentLogResponse])
async def get_deployment_logs(
    app_id: str,
    limit: Optional[int] = Query(default=100, ge=1, le=1000),
    service: AppHostingService = Depends(get_app_hosting_service),
):
    """Get deployment logs"""
    try:
        logs = await service.get_deployment_logs(app_id, limit)
        return [DeploymentLogResponse(**log.to_dict()) for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


@router.get("/applications/{app_id}/metrics", response_model=List[MetricsResponse])
async def get_metrics(
    app_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    service: AppHostingService = Depends(get_app_hosting_service),
):
    """Get application metrics"""
    try:
        start = (
            datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            if start_time
            else None
        )
        end = (
            datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            if end_time
            else None
        )

        metrics = await service.get_metrics(app_id, start, end)
        return [MetricsResponse(**m.to_dict()) for m in metrics]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.delete("/applications/{app_id}")
async def delete_application(
    app_id: str, service: AppHostingService = Depends(get_app_hosting_service)
):
    """Delete an application"""
    try:
        success = await service.delete_application(app_id)
        if success:
            return {"message": f"Application {app_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=404, detail=f"Application {app_id} not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete application: {str(e)}"
        )


@router.get("/health")
async def health_check(service: AppHostingService = Depends(get_app_hosting_service)):
    """Check app hosting service health"""
    try:
        apps = await service.list_applications()

        status_counts = {}
        for app in apps:
            status = app.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "status": "healthy",
            "total_applications": len(apps),
            "status_breakdown": status_counts,
            "supported_app_types": [t.value for t in AppType],
            "supported_scaling_policies": [p.value for p in ScalingPolicy],
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
