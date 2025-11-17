"""
iTechSmart Supreme Plus - Incidents API
Endpoints for incident management

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from models import Incident, AIAnalysis
from engine import SupremePlusEngine

router = APIRouter()


# Pydantic models
class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: str
    source: str
    node_id: Optional[int] = None
    metadata: Optional[dict] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[dict] = None


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    source: str
    node_id: Optional[int]
    metadata: dict
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=IncidentResponse)
async def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    """Create a new incident"""
    engine = SupremePlusEngine(db)
    new_incident = engine.create_incident(
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        source=incident.source,
        node_id=incident.node_id,
        metadata=incident.metadata,
    )
    return new_incident


@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    node_id: Optional[int] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List incidents with optional filters"""
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if node_id:
        query = query.filter(Incident.node_id == node_id)

    incidents = (
        query.order_by(Incident.created_at.desc()).offset(offset).limit(limit).all()
    )
    return incidents


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get incident by ID"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int, incident_update: IncidentUpdate, db: Session = Depends(get_db)
):
    """Update an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_data = incident_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)

    if incident_update.status == "resolved" and not incident.resolved_at:
        incident.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(incident)
    return incident


@router.delete("/{incident_id}")
async def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    """Delete an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    db.delete(incident)
    db.commit()
    return {"message": "Incident deleted successfully"}


@router.post("/{incident_id}/analyze")
async def analyze_incident(incident_id: int, db: Session = Depends(get_db)):
    """Analyze incident with AI"""
    engine = SupremePlusEngine(db)
    try:
        analysis = engine.analyze_incident_with_ai(incident_id)
        return {
            "analysis_id": analysis.id,
            "diagnosis": analysis.output_data.get("diagnosis"),
            "recommended_actions": analysis.output_data.get("recommended_actions"),
            "confidence": analysis.confidence_score,
            "reasoning": analysis.output_data.get("reasoning"),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incident_id}/analysis")
async def get_incident_analysis(incident_id: int, db: Session = Depends(get_db)):
    """Get AI analysis for an incident"""
    analyses = (
        db.query(AIAnalysis)
        .filter(AIAnalysis.incident_id == incident_id)
        .order_by(AIAnalysis.created_at.desc())
        .all()
    )

    return [
        {
            "id": a.id,
            "analysis_type": a.analysis_type,
            "diagnosis": a.output_data.get("diagnosis"),
            "recommended_actions": a.output_data.get("recommended_actions"),
            "confidence": a.confidence_score,
            "created_at": a.created_at,
        }
        for a in analyses
    ]


@router.get("/stats/summary")
async def get_incident_stats(db: Session = Depends(get_db)):
    """Get incident statistics"""
    total = db.query(Incident).count()
    open_incidents = db.query(Incident).filter(Incident.status == "open").count()
    resolved = db.query(Incident).filter(Incident.status == "resolved").count()

    # By severity
    critical = db.query(Incident).filter(Incident.severity == "critical").count()
    high = db.query(Incident).filter(Incident.severity == "high").count()
    medium = db.query(Incident).filter(Incident.severity == "medium").count()
    low = db.query(Incident).filter(Incident.severity == "low").count()

    # Recent incidents (last 24 hours)
    recent = (
        db.query(Incident)
        .filter(Incident.created_at >= datetime.utcnow() - timedelta(hours=24))
        .count()
    )

    return {
        "total": total,
        "open": open_incidents,
        "resolved": resolved,
        "by_severity": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        },
        "recent_24h": recent,
    }
