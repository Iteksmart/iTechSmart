"""
iTechSmart Observatory - Alerts API
Handles alert rules, incidents, and notifications
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/observatory/alerts", tags=["alerts"])


# ==================== REQUEST MODELS ====================


class AlertCreateRequest(BaseModel):
    name: str
    alert_type: str
    severity: str
    condition: Dict[str, Any]
    service_id: Optional[str] = None
    metric_name: Optional[str] = None
    notification_channels: Optional[List[str]] = None
    description: Optional[str] = None


class AlertUpdateRequest(BaseModel):
    name: Optional[str] = None
    severity: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    notification_channels: Optional[List[str]] = None
    is_active: Optional[bool] = None


class IncidentAcknowledgeRequest(BaseModel):
    acknowledged_by: str


class IncidentResolveRequest(BaseModel):
    resolved_by: str
    resolution_notes: Optional[str] = None


# ==================== ENDPOINTS ====================


@router.post("")
async def create_alert(
    request: AlertCreateRequest,
    created_by: str = Query(..., description="User ID creating the alert"),
    db: Session = Depends(get_db),
):
    """
    Create a new alert rule
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        alert_id = engine.create_alert(
            name=request.name,
            alert_type=request.alert_type,
            severity=request.severity,
            condition=request.condition,
            service_id=request.service_id,
            metric_name=request.metric_name,
            notification_channels=request.notification_channels,
            created_by=created_by,
        )

        return {"status": "success", "alert_id": alert_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_alerts(
    service_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_firing: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    List all alert rules
    """
    from ..models import Alert

    try:
        query = db.query(Alert)

        if service_id:
            query = query.filter(Alert.service_id == service_id)

        if is_active is not None:
            query = query.filter(Alert.is_active == is_active)

        if is_firing is not None:
            query = query.filter(Alert.is_firing == is_firing)

        alerts = query.all()

        return {
            "status": "success",
            "alerts": [
                {
                    "id": alert.id,
                    "name": alert.name,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "service_id": alert.service_id,
                    "metric_name": alert.metric_name,
                    "is_active": alert.is_active,
                    "is_firing": alert.is_firing,
                    "trigger_count": alert.trigger_count,
                    "last_triggered": (
                        alert.last_triggered.isoformat()
                        if alert.last_triggered
                        else None
                    ),
                }
                for alert in alerts
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}")
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """
    Get alert details
    """
    from ..models import Alert

    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {
            "status": "success",
            "alert": {
                "id": alert.id,
                "name": alert.name,
                "description": alert.description,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "service_id": alert.service_id,
                "metric_name": alert.metric_name,
                "condition": alert.condition,
                "notification_channels": alert.notification_channels,
                "is_active": alert.is_active,
                "is_firing": alert.is_firing,
                "trigger_count": alert.trigger_count,
                "last_triggered": (
                    alert.last_triggered.isoformat() if alert.last_triggered else None
                ),
                "created_at": alert.created_at.isoformat(),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{alert_id}")
async def update_alert(
    alert_id: str, request: AlertUpdateRequest, db: Session = Depends(get_db)
):
    """
    Update an alert rule
    """
    from ..models import Alert

    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        if request.name is not None:
            alert.name = request.name

        if request.severity is not None:
            alert.severity = request.severity

        if request.condition is not None:
            alert.condition = request.condition

        if request.notification_channels is not None:
            alert.notification_channels = request.notification_channels

        if request.is_active is not None:
            alert.is_active = request.is_active

        alert.updated_at = datetime.utcnow()
        db.commit()

        return {"status": "success", "message": "Alert updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, db: Session = Depends(get_db)):
    """
    Delete an alert rule
    """
    from ..models import Alert

    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        db.delete(alert)
        db.commit()

        return {"status": "success", "message": "Alert deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate")
async def evaluate_alerts(db: Session = Depends(get_db)):
    """
    Evaluate all active alerts
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        triggered = engine.evaluate_alerts()

        return {"status": "success", "triggered_alerts": triggered}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents/active")
async def get_active_incidents(
    service_id: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get active alert incidents
    """
    from ..models import AlertIncident, Alert

    try:
        query = db.query(AlertIncident).filter(
            AlertIncident.status.in_(["firing", "acknowledged"])
        )

        if service_id:
            query = query.join(Alert).filter(Alert.service_id == service_id)

        if severity:
            query = query.filter(AlertIncident.severity == severity)

        incidents = query.order_by(AlertIncident.started_at.desc()).all()

        return {
            "status": "success",
            "incidents": [
                {
                    "id": incident.id,
                    "alert_id": incident.alert_id,
                    "status": incident.status,
                    "severity": incident.severity,
                    "started_at": incident.started_at.isoformat(),
                    "acknowledged_at": (
                        incident.acknowledged_at.isoformat()
                        if incident.acknowledged_at
                        else None
                    ),
                    "trigger_value": incident.trigger_value,
                }
                for incident in incidents
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incidents/{incident_id}/acknowledge")
async def acknowledge_incident(
    incident_id: str, request: IncidentAcknowledgeRequest, db: Session = Depends(get_db)
):
    """
    Acknowledge an alert incident
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        success = engine.acknowledge_incident(
            incident_id=incident_id, acknowledged_by=request.acknowledged_by
        )

        if not success:
            raise HTTPException(status_code=404, detail="Incident not found")

        return {"status": "success", "message": "Incident acknowledged"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incidents/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str, request: IncidentResolveRequest, db: Session = Depends(get_db)
):
    """
    Resolve an alert incident
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        success = engine.resolve_incident(
            incident_id=incident_id,
            resolved_by=request.resolved_by,
            resolution_notes=request.resolution_notes,
        )

        if not success:
            raise HTTPException(status_code=404, detail="Incident not found")

        return {"status": "success", "message": "Incident resolved"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dependency injection
def get_db():
    """Database session dependency"""
    # TODO: Implement database session management
    pass
