"""
API endpoints for integration hub
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.integration_hub import IntegrationHub, ServiceType
from app.models.integration import (
    RegisteredService,
    ServiceHealth,
    IntegrationEvent,
    CrossServiceCall,
    WorkflowExecution,
)

router = APIRouter(prefix="/api/integration", tags=["integration"])


# Pydantic models
class ServiceRegistration(BaseModel):
    service_type: ServiceType
    service_name: str
    base_url: str
    api_key: str
    capabilities: List[str]
    metadata: Optional[dict] = None


class ServiceCallRequest(BaseModel):
    service_id: str
    endpoint: str
    method: str = "GET"
    data: Optional[dict] = None
    headers: Optional[dict] = None


class EventBroadcast(BaseModel):
    event_type: str
    event_data: dict
    source_service: str = "enterprise-hub"


class EventSubscription(BaseModel):
    service_id: str
    event_types: List[str]


class NinjaCommand(BaseModel):
    target_service: str
    command: str
    parameters: Optional[dict] = None


class WorkflowRequest(BaseModel):
    workflow_name: str
    steps: List[dict]


# Endpoints
@router.post("/register")
async def register_service(
    registration: ServiceRegistration, db: Session = Depends(get_db)
):
    """Register a service with the integration hub"""

    hub = IntegrationHub(db)

    result = await hub.register_service(
        service_type=registration.service_type,
        service_name=registration.service_name,
        base_url=registration.base_url,
        api_key=registration.api_key,
        capabilities=registration.capabilities,
        metadata=registration.metadata,
    )

    return result


@router.delete("/unregister/{service_id}")
async def unregister_service(service_id: str, db: Session = Depends(get_db)):
    """Unregister a service"""

    hub = IntegrationHub(db)
    await hub.unregister_service(service_id)

    return {"message": "Service unregistered", "service_id": service_id}


@router.get("/discover")
async def discover_services(
    service_type: Optional[ServiceType] = None,
    capability: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Discover available services"""

    hub = IntegrationHub(db)
    services = await hub.discover_services(service_type, capability)

    return {"services": services, "count": len(services)}


@router.post("/call")
async def call_service(request: ServiceCallRequest, db: Session = Depends(get_db)):
    """Make a call to another service"""

    hub = IntegrationHub(db)

    result = await hub.call_service(
        service_id=request.service_id,
        endpoint=request.endpoint,
        method=request.method,
        data=request.data,
        headers=request.headers,
    )

    return result


@router.post("/events/broadcast")
async def broadcast_event(event: EventBroadcast, db: Session = Depends(get_db)):
    """Broadcast an event to all subscribed services"""

    hub = IntegrationHub(db)

    await hub.broadcast_event(
        event_type=event.event_type,
        event_data=event.event_data,
        source_service=event.source_service,
    )

    return {"message": "Event broadcast", "event_type": event.event_type}


@router.post("/events/subscribe")
async def subscribe_to_events(
    subscription: EventSubscription, db: Session = Depends(get_db)
):
    """Subscribe a service to specific event types"""

    hub = IntegrationHub(db)

    await hub.subscribe_to_events(
        service_id=subscription.service_id, event_types=subscription.event_types
    )

    return {
        "message": "Subscribed to events",
        "service_id": subscription.service_id,
        "event_types": subscription.event_types,
    }


@router.get("/health/{service_id}")
async def get_service_health(service_id: str, db: Session = Depends(get_db)):
    """Get health status of a service"""

    hub = IntegrationHub(db)
    health = await hub.get_service_health(service_id)

    return health


@router.post("/ninja/control")
async def ninja_control(command: NinjaCommand, db: Session = Depends(get_db)):
    """Send a control command from Ninja to a service"""

    hub = IntegrationHub(db)

    result = await hub.ninja_control_command(
        target_service=command.target_service,
        command=command.command,
        parameters=command.parameters,
    )

    return result


@router.post("/workflow/execute")
async def execute_workflow(
    workflow: WorkflowRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Execute a cross-service workflow"""

    hub = IntegrationHub(db)

    result = await hub.cross_service_workflow(
        workflow_name=workflow.workflow_name, steps=workflow.steps
    )

    return result


@router.get("/status")
async def get_integration_status(db: Session = Depends(get_db)):
    """Get overall integration status"""

    hub = IntegrationHub(db)
    status = await hub.get_integration_status()

    return status


@router.get("/services")
async def list_services(db: Session = Depends(get_db)):
    """List all registered services"""

    services = (
        db.query(RegisteredService).filter(RegisteredService.status == "active").all()
    )

    return {
        "services": [
            {
                "service_id": s.service_id,
                "service_type": s.service_type,
                "service_name": s.service_name,
                "base_url": s.base_url,
                "capabilities": s.capabilities,
                "status": s.status,
                "registered_at": s.registered_at.isoformat(),
                "last_heartbeat": s.last_heartbeat.isoformat(),
            }
            for s in services
        ],
        "count": len(services),
    }


@router.get("/events")
async def list_events(
    limit: int = 100, event_type: Optional[str] = None, db: Session = Depends(get_db)
):
    """List integration events"""

    query = db.query(IntegrationEvent)

    if event_type:
        query = query.filter(IntegrationEvent.event_type == event_type)

    events = query.order_by(IntegrationEvent.timestamp.desc()).limit(limit).all()

    return {
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "event_data": e.event_data,
                "source_service": e.source_service,
                "timestamp": e.timestamp.isoformat(),
                "processed": e.processed,
            }
            for e in events
        ],
        "count": len(events),
    }


@router.get("/calls")
async def list_service_calls(
    limit: int = 100,
    source_service: Optional[str] = None,
    target_service: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List cross-service calls"""

    query = db.query(CrossServiceCall)

    if source_service:
        query = query.filter(CrossServiceCall.source_service == source_service)

    if target_service:
        query = query.filter(CrossServiceCall.target_service == target_service)

    calls = query.order_by(CrossServiceCall.timestamp.desc()).limit(limit).all()

    return {
        "calls": [
            {
                "id": c.id,
                "source_service": c.source_service,
                "target_service": c.target_service,
                "endpoint": c.endpoint,
                "method": c.method,
                "success": c.success,
                "status_code": c.status_code,
                "timestamp": c.timestamp.isoformat(),
            }
            for c in calls
        ],
        "count": len(calls),
    }


@router.get("/workflows")
async def list_workflows(
    limit: int = 50, status: Optional[str] = None, db: Session = Depends(get_db)
):
    """List workflow executions"""

    query = db.query(WorkflowExecution)

    if status:
        query = query.filter(WorkflowExecution.status == status)

    workflows = query.order_by(WorkflowExecution.started_at.desc()).limit(limit).all()

    return {
        "workflows": [
            {
                "id": w.id,
                "workflow_name": w.workflow_name,
                "status": w.status,
                "started_at": w.started_at.isoformat(),
                "completed_at": w.completed_at.isoformat() if w.completed_at else None,
            }
            for w in workflows
        ],
        "count": len(workflows),
    }


@router.post("/start")
async def start_hub(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Start the integration hub"""

    hub = IntegrationHub(db)
    background_tasks.add_task(hub.start_hub)

    return {"message": "Integration hub started", "status": "running"}


@router.get("/capabilities")
async def get_all_capabilities(db: Session = Depends(get_db)):
    """Get all capabilities across all services"""

    hub = IntegrationHub(db)
    capabilities = hub._get_all_capabilities()

    return {"capabilities": capabilities, "total_services": len(hub.services)}
