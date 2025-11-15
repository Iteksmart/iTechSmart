"""
iTechSmart Sentinel - Incident Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.incident_engine import IncidentEngine


router = APIRouter(prefix="/api/incidents", tags=["Incident Management"])


class CreateIncidentRequest(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "medium"
    affected_services: Optional[List[int]] = None
    team: Optional[str] = None
    assigned_to: Optional[str] = None
    alert_ids: Optional[List[int]] = None


class UpdateStatusRequest(BaseModel):
    new_status: str
    author: str
    message: Optional[str] = None


class AddUpdateRequest(BaseModel):
    update_type: str
    message: str
    author: str
    metadata: Optional[dict] = None


class AssignIncidentRequest(BaseModel):
    assigned_to: str
    author: str


class AddRootCauseRequest(BaseModel):
    root_cause: str
    resolution_summary: str
    author: str


@router.post("/")
async def create_incident(
    request: CreateIncidentRequest,
    db: Session = Depends(get_db)
):
    """Create a new incident"""
    engine = IncidentEngine(db)
    incident = await engine.create_incident(**request.dict())
    return {
        "id": incident.id,
        "incident_number": incident.incident_number,
        "status": incident.status
    }


@router.post("/{incident_id}/status")
async def update_incident_status(
    incident_id: int,
    request: UpdateStatusRequest,
    db: Session = Depends(get_db)
):
    """Update incident status"""
    engine = IncidentEngine(db)
    try:
        incident = await engine.update_incident_status(
            incident_id,
            request.new_status,
            request.author,
            request.message
        )
        return {"id": incident.id, "status": incident.status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{incident_id}/updates")
async def add_incident_update(
    incident_id: int,
    request: AddUpdateRequest,
    db: Session = Depends(get_db)
):
    """Add an update to an incident"""
    engine = IncidentEngine(db)
    try:
        update = await engine.add_incident_update(
            incident_id,
            request.update_type,
            request.message,
            request.author,
            request.metadata
        )
        return {"id": update.id, "created_at": update.created_at.isoformat()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{incident_id}/assign")
async def assign_incident(
    incident_id: int,
    request: AssignIncidentRequest,
    db: Session = Depends(get_db)
):
    """Assign incident to a person"""
    engine = IncidentEngine(db)
    try:
        incident = await engine.assign_incident(
            incident_id,
            request.assigned_to,
            request.author
        )
        return {"id": incident.id, "assigned_to": incident.assigned_to}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{incident_id}/root-cause")
async def add_root_cause(
    incident_id: int,
    request: AddRootCauseRequest,
    db: Session = Depends(get_db)
):
    """Add root cause analysis"""
    engine = IncidentEngine(db)
    try:
        incident = await engine.add_root_cause(
            incident_id,
            request.root_cause,
            request.resolution_summary,
            request.author
        )
        return {"id": incident.id, "root_cause": incident.root_cause}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/active")
async def get_active_incidents(
    severity: Optional[str] = None,
    team: Optional[str] = None,
    assigned_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all active incidents"""
    engine = IncidentEngine(db)
    incidents = await engine.get_active_incidents(severity, team, assigned_to)
    return {"incidents": incidents, "count": len(incidents)}


@router.get("/{incident_id}/timeline")
async def get_incident_timeline(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Get complete incident timeline"""
    engine = IncidentEngine(db)
    try:
        timeline = await engine.get_incident_timeline(incident_id)
        return timeline
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/statistics")
async def get_incident_statistics(
    days: int = Query(30, le=365),
    db: Session = Depends(get_db)
):
    """Get incident statistics"""
    engine = IncidentEngine(db)
    stats = await engine.get_incident_statistics(days)
    return stats


@router.get("/{incident_id}/post-mortem")
async def generate_post_mortem(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Generate post-mortem template"""
    engine = IncidentEngine(db)
    try:
        post_mortem = await engine.generate_post_mortem(incident_id)
        return post_mortem
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))