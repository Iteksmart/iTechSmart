"""
iTechSmart Supreme - Appointment API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date

from app.core.database import get_db
from app.core.supreme_engine import SupremeEngine
from app.models.models import AppointmentStatus

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


class AppointmentCreate(BaseModel):
    patient_id: int
    provider_id: int
    appointment_date: datetime
    duration_minutes: int = 30
    reason: Optional[str] = None
    notes: Optional[str] = None
    room_number: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    appointment_date: datetime
    duration_minutes: int
    reason: Optional[str]
    status: AppointmentStatus
    room_number: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=AppointmentResponse)
def schedule_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Schedule new appointment"""
    engine = SupremeEngine(db)

    try:
        return engine.schedule_appointment(appointment.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(
    patient_id: Optional[int] = Query(None),
    provider_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[AppointmentStatus] = Query(None),
    db: Session = Depends(get_db),
):
    """Get appointments with filters"""
    engine = SupremeEngine(db)
    return engine.get_appointments(
        patient_id=patient_id,
        provider_id=provider_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )


@router.put("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: int,
    status_update: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update appointment status"""
    engine = SupremeEngine(db)

    try:
        return engine.update_appointment_status(
            appointment_id, status_update.status, status_update.notes
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/analytics")
def get_appointment_analytics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    """Get appointment analytics"""
    engine = SupremeEngine(db)
    return engine.get_appointment_analytics(start_date, end_date)
