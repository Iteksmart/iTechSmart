"""
iTechSmart Sentinel - Alerting API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.alerting_engine import AlertingEngine


router = APIRouter(prefix="/api/alerts", tags=["Alerting"])


class CreateAlertRequest(BaseModel):
    service_name: str
    alert_name: str
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    condition: Optional[dict] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    tags: Optional[dict] = None
    metadata: Optional[dict] = None


class AcknowledgeAlertRequest(BaseModel):
    acknowledged_by: str


class ResolveAlertRequest(BaseModel):
    resolution_note: Optional[str] = None


class SilenceAlertRequest(BaseModel):
    duration_minutes: int = 60
    silenced_by: Optional[str] = None


@router.post("/")
async def create_alert(request: CreateAlertRequest, db: Session = Depends(get_db)):
    """Create a new alert"""
    engine = AlertingEngine(db)
    alert = await engine.create_alert(**request.dict())
    return {"id": alert.id, "fingerprint": alert.fingerprint, "status": alert.status}


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int, request: AcknowledgeAlertRequest, db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    engine = AlertingEngine(db)
    try:
        alert = await engine.acknowledge_alert(alert_id, request.acknowledged_by)
        return {"id": alert.id, "status": alert.status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int, request: ResolveAlertRequest, db: Session = Depends(get_db)
):
    """Resolve an alert"""
    engine = AlertingEngine(db)
    try:
        alert = await engine.resolve_alert(alert_id, request.resolution_note)
        return {"id": alert.id, "status": alert.status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{alert_id}/silence")
async def silence_alert(
    alert_id: int, request: SilenceAlertRequest, db: Session = Depends(get_db)
):
    """Silence an alert for a duration"""
    engine = AlertingEngine(db)
    try:
        alert = await engine.silence_alert(
            alert_id, request.duration_minutes, request.silenced_by
        )
        return {"id": alert.id, "status": alert.status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/active")
async def get_active_alerts(
    service_name: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """Get all active alerts"""
    engine = AlertingEngine(db)
    alerts = await engine.get_active_alerts(service_name, severity, limit)
    return {"alerts": alerts, "count": len(alerts)}


@router.get("/statistics")
async def get_alert_statistics(
    service_name: Optional[str] = None,
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db),
):
    """Get alert statistics"""
    engine = AlertingEngine(db)
    stats = await engine.get_alert_statistics(service_name, hours)
    return stats


@router.get("/fatigue")
async def detect_alert_fatigue(
    service_name: Optional[str] = None,
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db),
):
    """Detect alert fatigue patterns"""
    engine = AlertingEngine(db)
    fatigue = await engine.detect_alert_fatigue(service_name, hours)
    return fatigue
