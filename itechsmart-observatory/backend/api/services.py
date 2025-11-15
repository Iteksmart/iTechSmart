"""
iTechSmart Observatory - Services API
Handles service registration, health, and topology
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/observatory/services", tags=["services"])


# ==================== REQUEST MODELS ====================

class ServiceRegisterRequest(BaseModel):
    name: str
    service_type: str
    environment: str
    version: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class ServiceHealthUpdateRequest(BaseModel):
    health_status: str


class DashboardCreateRequest(BaseModel):
    name: str
    layout: Dict[str, Any]
    widgets: List[Dict[str, Any]]
    description: Optional[str] = None
    is_public: bool = False


class SLOCreateRequest(BaseModel):
    service_id: str
    name: str
    slo_type: str
    target_value: float
    metric_name: str
    measurement_window: str = "30d"
    description: Optional[str] = None


# ==================== ENDPOINTS ====================

@router.post("/register")
async def register_service(
    request: ServiceRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new service for monitoring
    """
    from ..engine.observatory_engine import ObservatoryEngine
    
    engine = ObservatoryEngine(db)
    
    try:
        result = engine.register_service(
            name=request.name,
            service_type=request.service_type,
            environment=request.environment,
            version=request.version,
            language=request.language,
            framework=request.framework,
            metadata=request.metadata,
            tags=request.tags
        )
        
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_services(
    environment: Optional[str] = None,
    service_type: Optional[str] = None,
    health_status: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List all registered services
    """
    from ..models import Service
    
    try:
        query = db.query(Service)
        
        if environment:
            query = query.filter(Service.environment == environment)
        
        if service_type:
            query = query.filter(Service.service_type == service_type)
        
        if health_status:
            query = query.filter(Service.health_status == health_status)
        
        if is_active is not None:
            query = query.filter(Service.is_active == is_active)
        
        services = query.all()
        
        return {
            "status": "success",
            "services": [
                {
                    "id": service.id,
                    "name": service.name,
                    "service_type": service.service_type,
                    "environment": service.environment,
                    "version": service.version,
                    "health_status": service.health_status,
                    "last_seen": service.last_seen.isoformat() if service.last_seen else None,
                    "is_active": service.is_active
                }
                for service in services
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service_id}")
async def get_service(
    service_id: str,
    db: Session = Depends(get_db)
):
    """
    Get service details
    """
    from ..models import Service
    
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return {
            "status": "success",
            "service": {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "service_type": service.service_type,
                "environment": service.environment,
                "version": service.version,
                "language": service.language,
                "framework": service.framework,
                "metadata": service.metadata,
                "tags": service.tags,
                "health_status": service.health_status,
                "last_seen": service.last_seen.isoformat() if service.last_seen else None,
                "is_active": service.is_active,
                "created_at": service.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{service_id}/health")
async def update_service_health(
    service_id: str,
    request: ServiceHealthUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update service health status
    """
    from ..engine.observatory_engine import ObservatoryEngine
    
    engine = ObservatoryEngine(db)
    
    try:
        success = engine.update_service_health(
            service_id=service_id,
            health_status=request.health_status
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return {
            "status": "success",
            "message": "Health status updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service_id}/topology")
async def get_service_topology(
    service_id: str,
    db: Session = Depends(get_db)
):
    """
    Get service dependency topology
    """
    from ..engine.observatory_engine import ObservatoryEngine
    
    engine = ObservatoryEngine(db)
    
    try:
        topology = engine.get_service_topology(service_id)
        
        return {
            "status": "success",
            "topology": topology
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboards")
async def create_dashboard(
    request: DashboardCreateRequest,
    owner_id: str = Query(..., description="User ID creating the dashboard"),
    db: Session = Depends(get_db)
):
    """
    Create a custom dashboard
    """
    from ..engine.observatory_engine import ObservatoryEngine
    
    engine = ObservatoryEngine(db)
    
    try:
        dashboard_id = engine.create_dashboard(
            name=request.name,
            layout=request.layout,
            widgets=request.widgets,
            owner_id=owner_id,
            description=request.description,
            is_public=request.is_public
        )
        
        return {
            "status": "success",
            "dashboard_id": dashboard_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboards")
async def list_dashboards(
    owner_id: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List dashboards
    """
    from ..models import Dashboard
    
    try:
        query = db.query(Dashboard)
        
        if owner_id:
            query = query.filter(Dashboard.owner_id == owner_id)
        
        if is_public is not None:
            query = query.filter(Dashboard.is_public == is_public)
        
        dashboards = query.all()
        
        return {
            "status": "success",
            "dashboards": [
                {
                    "id": dashboard.id,
                    "name": dashboard.name,
                    "description": dashboard.description,
                    "is_public": dashboard.is_public,
                    "owner_id": dashboard.owner_id,
                    "created_at": dashboard.created_at.isoformat()
                }
                for dashboard in dashboards
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboards/{dashboard_id}")
async def get_dashboard_data(
    dashboard_id: str,
    time_range: str = Query("1h", description="Time range for widget data"),
    db: Session = Depends(get_db)
):
    """
    Get dashboard with widget data
    """
    from ..engine.observatory_engine import ObservatoryEngine
    
    engine = ObservatoryEngine(db)
    
    try:
        data = engine.get_dashboard_data(
            dashboard_id=dashboard_id,
            time_range=time_range
        )
        
        return {
            "status": "success",
            **data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/slos")
async def create_slo(
    request: SLOCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a Service Level Objective
    """
    from ..engine.observatory_engine import ObservatoryEngine
    
    engine = ObservatoryEngine(db)
    
    try:
        slo_id = engine.create_slo(
            service_id=request.service_id,
            name=request.name,
            slo_type=request.slo_type,
            target_value=request.target_value,
            metric_name=request.metric_name,
            measurement_window=request.measurement_window,
            description=request.description
        )
        
        return {
            "status": "success",
            "slo_id": slo_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slos/{slo_id}/evaluate")
async def evaluate_slo(
    slo_id: str,
    db: Session = Depends(get_db)
):
    """
    Evaluate SLO compliance
    """
    from ..engine.observatory_engine import ObservatoryEngine
    
    engine = ObservatoryEngine(db)
    
    try:
        result = engine.evaluate_slo(slo_id)
        
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slos")
async def list_slos(
    service_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List Service Level Objectives
    """
    from ..models import SLO
    
    try:
        query = db.query(SLO)
        
        if service_id:
            query = query.filter(SLO.service_id == service_id)
        
        if is_active is not None:
            query = query.filter(SLO.is_active == is_active)
        
        slos = query.all()
        
        return {
            "status": "success",
            "slos": [
                {
                    "id": slo.id,
                    "service_id": slo.service_id,
                    "name": slo.name,
                    "slo_type": slo.slo_type,
                    "target_value": slo.target_value,
                    "current_value": slo.current_value,
                    "compliance_status": slo.compliance_status,
                    "error_budget_remaining": slo.error_budget_remaining,
                    "is_active": slo.is_active
                }
                for slo in slos
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dependency injection
def get_db():
    """Database session dependency"""
    # TODO: Implement database session management
    pass