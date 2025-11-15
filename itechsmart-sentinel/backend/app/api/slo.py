"""
iTechSmart Sentinel - SLO Tracking API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.slo_engine import SLOEngine


router = APIRouter(prefix="/api/slo", tags=["SLO Tracking"])


class CreateSLORequest(BaseModel):
    service_name: str
    name: str
    slo_type: str
    target_percentage: float
    window_days: int = 30
    description: Optional[str] = None
    warning_threshold: float = 95.0
    critical_threshold: float = 90.0
    alert_on_breach: bool = True
    alert_on_burn_rate: bool = True


class RecordMeasurementRequest(BaseModel):
    success_count: int
    total_count: int


@router.post("/")
async def create_slo(
    request: CreateSLORequest,
    db: Session = Depends(get_db)
):
    """Create a new SLO"""
    engine = SLOEngine(db)
    slo = await engine.create_slo(**request.dict())
    return {"id": slo.id, "name": slo.name, "status": slo.status}


@router.post("/{slo_id}/measurements")
async def record_measurement(
    slo_id: int,
    request: RecordMeasurementRequest,
    db: Session = Depends(get_db)
):
    """Record an SLO measurement"""
    engine = SLOEngine(db)
    try:
        measurement = await engine.record_measurement(
            slo_id,
            request.success_count,
            request.total_count
        )
        return {
            "id": measurement.id,
            "success_percentage": measurement.success_percentage,
            "error_budget_consumed": measurement.error_budget_consumed
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{slo_id}/status")
async def get_slo_status(
    slo_id: int,
    db: Session = Depends(get_db)
):
    """Get current SLO status"""
    engine = SLOEngine(db)
    try:
        status = await engine.get_slo_status(slo_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{slo_id}/history")
async def get_slo_history(
    slo_id: int,
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get SLO measurement history"""
    engine = SLOEngine(db)
    try:
        history = await engine.get_slo_history(slo_id, hours)
        return {"history": history, "count": len(history)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
async def get_all_slos(
    service_name: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all SLOs"""
    engine = SLOEngine(db)
    slos = await engine.get_all_slos(service_name, status)
    return {"slos": slos, "count": len(slos)}


@router.get("/violations")
async def check_slo_violations(
    service_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Check for SLO violations"""
    engine = SLOEngine(db)
    violations = await engine.check_slo_violations(service_name)
    return {"violations": violations, "count": len(violations)}


@router.get("/{slo_id}/predict")
async def predict_slo_breach(
    slo_id: int,
    hours_ahead: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Predict if SLO will breach"""
    engine = SLOEngine(db)
    try:
        prediction = await engine.predict_slo_breach(slo_id, hours_ahead)
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/report")
async def get_slo_report(
    service_name: Optional[str] = None,
    days: int = Query(30, le=365),
    db: Session = Depends(get_db)
):
    """Generate comprehensive SLO report"""
    engine = SLOEngine(db)
    report = await engine.get_slo_report(service_name, days)
    return report