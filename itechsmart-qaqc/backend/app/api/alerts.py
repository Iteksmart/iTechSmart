"""
API endpoints for alerts management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.models import Alert, Product, QACheck, CheckSeverity
from pydantic import BaseModel

router = APIRouter(prefix="/alerts", tags=["alerts"])


# Pydantic models
class AlertCreate(BaseModel):
    alert_type: str
    severity: CheckSeverity
    title: str
    message: str
    product_id: Optional[int] = None
    check_id: Optional[int] = None
    recommended_actions: Optional[dict] = None
    auto_fix_available: bool = False
    details: Optional[dict] = None
    tags: Optional[dict] = None


class AlertUpdate(BaseModel):
    is_resolved: Optional[bool] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: CheckSeverity
    title: str
    message: str
    product_id: Optional[int]
    check_id: Optional[int]
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    resolution_notes: Optional[str]
    recommended_actions: Optional[dict]
    auto_fix_available: bool
    details: Optional[dict]
    tags: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    is_resolved: Optional[bool] = None,
    severity: Optional[CheckSeverity] = None,
    alert_type: Optional[str] = None,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List all alerts with optional filtering"""
    query = db.query(Alert)

    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)

    if severity is not None:
        query = query.filter(Alert.severity == severity)

    if alert_type is not None:
        query = query.filter(Alert.alert_type == alert_type)

    if product_id is not None:
        query = query.filter(Alert.product_id == product_id)

    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert by ID"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert"""
    # Verify product exists if provided
    if alert.product_id:
        product = db.query(Product).filter(Product.id == alert.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

    # Verify check exists if provided
    if alert.check_id:
        check = db.query(QACheck).filter(QACheck.id == alert.check_id).first()
        if not check:
            raise HTTPException(status_code=404, detail="Check not found")

    db_alert = Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int, alert: AlertUpdate, db: Session = Depends(get_db)
):
    """Update an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Update fields
    update_data = alert.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)

    # Set resolved_at if marking as resolved
    if alert.is_resolved and not db_alert.resolved_at:
        db_alert.resolved_at = datetime.utcnow()

    db_alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(db_alert)
    db.commit()
    return None


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    resolved_by: str,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Mark an alert as resolved"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = resolved_by
    alert.resolution_notes = resolution_notes
    alert.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Alert resolved successfully",
        "alert_id": alert_id,
        "resolved_at": alert.resolved_at,
    }


@router.post("/{alert_id}/reopen")
async def reopen_alert(alert_id: int, db: Session = Depends(get_db)):
    """Reopen a resolved alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_resolved = False
    alert.resolved_at = None
    alert.resolved_by = None
    alert.resolution_notes = None
    alert.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Alert reopened successfully", "alert_id": alert_id}


@router.get("/stats/summary")
async def get_alert_stats(db: Session = Depends(get_db)):
    """Get overall alert statistics"""
    total_alerts = db.query(Alert).count()
    open_alerts = db.query(Alert).filter(Alert.is_resolved == False).count()
    resolved_alerts = db.query(Alert).filter(Alert.is_resolved == True).count()

    # Count by severity
    critical = (
        db.query(Alert)
        .filter(Alert.severity == CheckSeverity.CRITICAL, Alert.is_resolved == False)
        .count()
    )
    high = (
        db.query(Alert)
        .filter(Alert.severity == CheckSeverity.HIGH, Alert.is_resolved == False)
        .count()
    )
    medium = (
        db.query(Alert)
        .filter(Alert.severity == CheckSeverity.MEDIUM, Alert.is_resolved == False)
        .count()
    )
    low = (
        db.query(Alert)
        .filter(Alert.severity == CheckSeverity.LOW, Alert.is_resolved == False)
        .count()
    )

    # Count by type
    from sqlalchemy import func

    alert_types = (
        db.query(Alert.alert_type, func.count(Alert.id).label("count"))
        .filter(Alert.is_resolved == False)
        .group_by(Alert.alert_type)
        .all()
    )

    return {
        "total_alerts": total_alerts,
        "open_alerts": open_alerts,
        "resolved_alerts": resolved_alerts,
        "by_severity": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        },
        "by_type": {at[0]: at[1] for at in alert_types},
        "resolution_rate": round(
            (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 0, 2
        ),
    }


@router.post("/bulk-resolve")
async def bulk_resolve_alerts(
    alert_ids: List[int],
    resolved_by: str,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Resolve multiple alerts at once"""
    alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()

    if not alerts:
        raise HTTPException(status_code=404, detail="No alerts found")

    resolved_count = 0
    for alert in alerts:
        if not alert.is_resolved:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = resolved_by
            alert.resolution_notes = resolution_notes
            alert.updated_at = datetime.utcnow()
            resolved_count += 1

    db.commit()

    return {
        "message": f"Resolved {resolved_count} alerts",
        "resolved_count": resolved_count,
        "total_requested": len(alert_ids),
    }
