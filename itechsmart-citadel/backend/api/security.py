"""
iTechSmart Citadel - Security API
Security event and incident management endpoints

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from models import SecurityEvent, IncidentResponse, SecurityControl
from engine import CitadelEngine

router = APIRouter()


# Pydantic models
class SecurityEventCreate(BaseModel):
    event_type: str
    severity: str
    source: str
    description: str
    destination: Optional[str] = None
    metadata: Optional[dict] = None


class SecurityEventResponse(BaseModel):
    id: int
    event_type: str
    severity: str
    source: str
    destination: Optional[str]
    description: str
    status: str
    threat_level: int
    detected_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class IncidentResponseCreate(BaseModel):
    event_id: int
    action_type: str
    action_taken: str
    initiated_by: str


class SecurityControlCreate(BaseModel):
    control_type: str
    name: str
    description: str
    configuration: dict
    enabled: bool = True


@router.post("/events", response_model=SecurityEventResponse)
async def create_security_event(
    event: SecurityEventCreate, db: Session = Depends(get_db)
):
    """Create a new security event"""
    engine = CitadelEngine(db)
    new_event = engine.create_security_event(
        event_type=event.event_type,
        severity=event.severity,
        source=event.source,
        description=event.description,
        destination=event.destination,
        metadata=event.metadata,
    )
    return new_event


@router.get("/events", response_model=List[SecurityEventResponse])
async def list_security_events(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    hours: int = Query(24, le=720),
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List security events"""
    query = db.query(SecurityEvent).filter(
        SecurityEvent.detected_at >= datetime.utcnow() - timedelta(hours=hours)
    )

    if status:
        query = query.filter(SecurityEvent.status == status)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)

    events = (
        query.order_by(SecurityEvent.detected_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return events


@router.get("/events/{event_id}", response_model=SecurityEventResponse)
async def get_security_event(event_id: int, db: Session = Depends(get_db)):
    """Get security event by ID"""
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Security event not found")
    return event


@router.post("/events/{event_id}/respond")
async def respond_to_event(
    event_id: int, response: IncidentResponseCreate, db: Session = Depends(get_db)
):
    """Create incident response for an event"""
    engine = CitadelEngine(db)
    incident_response = engine.create_incident_response(
        event_id=response.event_id,
        action_type=response.action_type,
        action_taken=response.action_taken,
        initiated_by=response.initiated_by,
    )
    return incident_response


@router.post("/responses/{response_id}/execute")
async def execute_response(response_id: int, db: Session = Depends(get_db)):
    """Execute an incident response"""
    engine = CitadelEngine(db)
    try:
        result = engine.execute_incident_response(response_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/controls")
async def list_security_controls(
    control_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List security controls"""
    query = db.query(SecurityControl)

    if control_type:
        query = query.filter(SecurityControl.control_type == control_type)
    if enabled is not None:
        query = query.filter(SecurityControl.enabled == enabled)

    controls = query.all()
    return controls


@router.post("/controls")
async def create_security_control(
    control: SecurityControlCreate, db: Session = Depends(get_db)
):
    """Create a security control"""
    new_control = SecurityControl(
        control_type=control.control_type,
        name=control.name,
        description=control.description,
        configuration=control.configuration,
        enabled=control.enabled,
        created_at=datetime.utcnow(),
    )
    db.add(new_control)
    db.commit()
    db.refresh(new_control)
    return new_control


@router.get("/stats/summary")
async def get_security_stats(db: Session = Depends(get_db)):
    """Get security statistics"""
    total_events = db.query(SecurityEvent).count()
    open_events = db.query(SecurityEvent).filter(SecurityEvent.status == "open").count()
    critical_events = (
        db.query(SecurityEvent).filter(SecurityEvent.severity == "critical").count()
    )

    # Events by type
    from sqlalchemy import func

    by_type = (
        db.query(SecurityEvent.event_type, func.count(SecurityEvent.id))
        .group_by(SecurityEvent.event_type)
        .all()
    )

    return {
        "total_events": total_events,
        "open_events": open_events,
        "critical_events": critical_events,
        "by_type": {event_type: count for event_type, count in by_type},
    }
