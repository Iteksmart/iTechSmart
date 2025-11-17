"""
iTechSmart Supreme - Billing API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from app.core.database import get_db
from app.core.supreme_engine import SupremeEngine
from app.models.models import BillingStatus

router = APIRouter(prefix="/api/billing", tags=["Billing"])


class BillCreate(BaseModel):
    patient_id: int
    service_date: date
    description: Optional[str] = None
    amount: float
    insurance_amount: float = 0.0
    due_date: Optional[date] = None
    notes: Optional[str] = None


class PaymentProcess(BaseModel):
    payment_amount: float


class BillResponse(BaseModel):
    id: int
    patient_id: int
    bill_number: str
    service_date: date
    amount: float
    insurance_amount: float
    patient_amount: float
    paid_amount: float
    balance: float
    status: BillingStatus

    class Config:
        from_attributes = True


@router.post("/", response_model=BillResponse)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    """Create new bill"""
    engine = SupremeEngine(db)
    return engine.create_bill(bill.dict())


@router.get("/patient/{patient_id}", response_model=List[BillResponse])
def get_patient_bills(
    patient_id: int,
    status: Optional[BillingStatus] = Query(None),
    db: Session = Depends(get_db),
):
    """Get patient bills"""
    engine = SupremeEngine(db)
    return engine.get_patient_bills(patient_id, status)


@router.post("/{bill_id}/payment", response_model=BillResponse)
def process_payment(
    bill_id: int, payment: PaymentProcess, db: Session = Depends(get_db)
):
    """Process bill payment"""
    engine = SupremeEngine(db)

    try:
        return engine.process_payment(bill_id, payment.payment_amount)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
