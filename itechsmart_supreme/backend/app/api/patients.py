"""
iTechSmart Supreme - Patient API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import date

from app.core.database import get_db
from app.core.supreme_engine import SupremeEngine
from app.models.models import PatientStatus

router = APIRouter(prefix="/api/patients", tags=["Patients"])


# Pydantic models
class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_group_number: Optional[str] = None


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_group_number: Optional[str] = None
    status: Optional[PatientStatus] = None


class PatientResponse(BaseModel):
    id: int
    mrn: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    status: PatientStatus

    class Config:
        from_attributes = True


@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create new patient"""
    engine = SupremeEngine(db)
    return engine.create_patient(patient.dict())


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get patient by ID"""
    engine = SupremeEngine(db)
    patient = engine.get_patient(patient_id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


@router.get("/", response_model=List[PatientResponse])
def search_patients(
    query: Optional[str] = Query(None, description="Search query"),
    status: Optional[PatientStatus] = Query(None, description="Patient status"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Search patients"""
    engine = SupremeEngine(db)
    return engine.search_patients(query=query, status=status, limit=limit)


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int, updates: PatientUpdate, db: Session = Depends(get_db)
):
    """Update patient information"""
    engine = SupremeEngine(db)

    # Filter out None values
    update_data = {k: v for k, v in updates.dict().items() if v is not None}

    try:
        return engine.update_patient(patient_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
