"""
Case Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Case, CaseStatus, CaseType

router = APIRouter()


# Pydantic models
class CaseCreate(BaseModel):
    case_number: str
    title: str
    description: Optional[str] = None
    case_type: CaseType
    status: CaseStatus = CaseStatus.OPEN
    client_id: int
    attorney_id: int
    court_name: Optional[str] = None
    judge_name: Optional[str] = None
    opposing_party: Optional[str] = None
    opposing_counsel: Optional[str] = None
    filing_date: Optional[datetime] = None
    statute_of_limitations: Optional[datetime] = None
    trial_date: Optional[datetime] = None
    settlement_amount: Optional[float] = None
    hourly_rate: Optional[float] = None
    flat_fee: Optional[float] = None
    contingency_percentage: Optional[float] = None
    retainer_amount: Optional[float] = None
    custom_fields: Optional[dict] = None


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    case_type: Optional[CaseType] = None
    status: Optional[CaseStatus] = None
    attorney_id: Optional[int] = None
    court_name: Optional[str] = None
    judge_name: Optional[str] = None
    opposing_party: Optional[str] = None
    opposing_counsel: Optional[str] = None
    filing_date: Optional[datetime] = None
    statute_of_limitations: Optional[datetime] = None
    trial_date: Optional[datetime] = None
    settlement_amount: Optional[float] = None
    hourly_rate: Optional[float] = None
    flat_fee: Optional[float] = None
    contingency_percentage: Optional[float] = None
    retainer_amount: Optional[float] = None
    custom_fields: Optional[dict] = None


class CaseResponse(BaseModel):
    id: int
    case_number: str
    title: str
    description: Optional[str]
    case_type: CaseType
    status: CaseStatus
    client_id: int
    attorney_id: int
    court_name: Optional[str]
    judge_name: Optional[str]
    opposing_party: Optional[str]
    opposing_counsel: Optional[str]
    filing_date: Optional[datetime]
    statute_of_limitations: Optional[datetime]
    trial_date: Optional[datetime]
    settlement_amount: Optional[float]
    hourly_rate: Optional[float]
    flat_fee: Optional[float]
    contingency_percentage: Optional[float]
    retainer_amount: Optional[float]
    custom_fields: Optional[dict]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new case"""

    # Check if case number already exists
    existing_case = (
        db.query(Case).filter(Case.case_number == case_data.case_number).first()
    )
    if existing_case:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Case number already exists"
        )

    new_case = Case(**case_data.dict())
    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    return new_case


@router.get("/", response_model=List[CaseResponse])
async def get_cases(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CaseStatus] = None,
    case_type: Optional[CaseType] = None,
    client_id: Optional[int] = None,
    attorney_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all cases with optional filtering"""

    query = db.query(Case)

    if status:
        query = query.filter(Case.status == status)

    if case_type:
        query = query.filter(Case.case_type == case_type)

    if client_id:
        query = query.filter(Case.client_id == client_id)

    if attorney_id:
        query = query.filter(Case.attorney_id == attorney_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Case.case_number.ilike(search_filter))
            | (Case.title.ilike(search_filter))
            | (Case.description.ilike(search_filter))
        )

    cases = query.offset(skip).limit(limit).all()
    return cases


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific case by ID"""

    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    return case


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    case_data: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a case"""

    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Update only provided fields
    update_data = case_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    db.commit()
    db.refresh(case)

    return case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a case (archive)"""

    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Archive the case
    case.status = CaseStatus.ARCHIVED
    db.commit()

    return None


@router.get("/{case_id}/auto-fill-data")
async def get_case_auto_fill_data(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get case data formatted for auto-filling documents
    Includes both case and client information
    """

    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Get client data
    client = case.client
    attorney = case.attorney

    # Format data for auto-fill
    auto_fill_data = {
        # Case information
        "case_number": case.case_number,
        "case_title": case.title,
        "case_description": case.description or "",
        "case_type": case.case_type.value,
        "case_status": case.status.value,
        "court_name": case.court_name or "",
        "judge_name": case.judge_name or "",
        "opposing_party": case.opposing_party or "",
        "opposing_counsel": case.opposing_counsel or "",
        "filing_date": (
            case.filing_date.strftime("%m/%d/%Y") if case.filing_date else ""
        ),
        "statute_of_limitations": (
            case.statute_of_limitations.strftime("%m/%d/%Y")
            if case.statute_of_limitations
            else ""
        ),
        "trial_date": case.trial_date.strftime("%m/%d/%Y") if case.trial_date else "",
        "settlement_amount": (
            f"${case.settlement_amount:,.2f}" if case.settlement_amount else ""
        ),
        "hourly_rate": f"${case.hourly_rate:,.2f}" if case.hourly_rate else "",
        "flat_fee": f"${case.flat_fee:,.2f}" if case.flat_fee else "",
        "contingency_percentage": (
            f"{case.contingency_percentage}%" if case.contingency_percentage else ""
        ),
        "retainer_amount": (
            f"${case.retainer_amount:,.2f}" if case.retainer_amount else ""
        ),
        # Client information
        "client_full_name": f"{client.first_name} {client.last_name}",
        "client_first_name": client.first_name,
        "client_last_name": client.last_name,
        "client_company": client.company_name or "",
        "client_email": client.email or "",
        "client_phone": client.phone or "",
        "client_mobile": client.mobile or "",
        "client_address": client.address or "",
        "client_city": client.city or "",
        "client_state": client.state or "",
        "client_zip": client.zip_code or "",
        "client_country": client.country,
        "client_full_address": f"{client.address or ''}, {client.city or ''}, {client.state or ''} {client.zip_code or ''}".strip(
            ", "
        ),
        # Attorney information
        "attorney_full_name": f"{attorney.first_name} {attorney.last_name}",
        "attorney_first_name": attorney.first_name,
        "attorney_last_name": attorney.last_name,
        "attorney_email": attorney.email,
        "attorney_phone": attorney.phone or "",
        "attorney_bar_number": attorney.bar_number or "",
        # Current date
        "current_date": datetime.now().strftime("%m/%d/%Y"),
        "current_year": datetime.now().strftime("%Y"),
        # Custom fields
        **(case.custom_fields or {}),
    }

    return auto_fill_data
