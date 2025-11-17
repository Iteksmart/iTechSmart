"""
API endpoints for QA checks management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.models import (
    QACheck,
    QAResult,
    Product,
    CheckStatus,
    CheckCategory,
    CheckSeverity,
)
from app.core.qa_engine import QAEngine
from pydantic import BaseModel

router = APIRouter(prefix="/qa-checks", tags=["qa-checks"])


# Pydantic models
class QACheckCreate(BaseModel):
    product_id: int
    check_id: str
    name: str
    description: Optional[str] = None
    category: CheckCategory
    severity: CheckSeverity = CheckSeverity.MEDIUM
    is_enabled: bool = True
    can_auto_fix: bool = False
    check_interval_minutes: int = 60
    timeout_seconds: int = 300
    pass_threshold: Optional[float] = None
    warning_threshold: Optional[float] = None
    tags: Optional[dict] = None
    config: Optional[dict] = None


class QACheckUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[CheckCategory] = None
    severity: Optional[CheckSeverity] = None
    is_enabled: Optional[bool] = None
    can_auto_fix: Optional[bool] = None
    check_interval_minutes: Optional[int] = None
    timeout_seconds: Optional[int] = None
    pass_threshold: Optional[float] = None
    warning_threshold: Optional[float] = None
    tags: Optional[dict] = None
    config: Optional[dict] = None


class QACheckResponse(BaseModel):
    id: int
    product_id: int
    check_id: str
    name: str
    description: Optional[str]
    category: CheckCategory
    severity: CheckSeverity
    is_enabled: bool
    can_auto_fix: bool
    check_interval_minutes: int
    timeout_seconds: int
    pass_threshold: Optional[float]
    warning_threshold: Optional[float]
    tags: Optional[dict]
    config: Optional[dict]
    created_at: datetime
    updated_at: datetime
    last_run: Optional[datetime]

    class Config:
        from_attributes = True


class QAResultResponse(BaseModel):
    id: int
    product_id: int
    check_id: int
    status: CheckStatus
    score: Optional[float]
    message: Optional[str]
    details: Optional[dict]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    auto_fix_attempted: bool
    auto_fix_successful: Optional[bool]
    auto_fix_details: Optional[dict]
    environment: Optional[str]
    triggered_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RunCheckRequest(BaseModel):
    auto_fix: bool = False
    environment: Optional[str] = "production"


@router.get("/", response_model=List[QACheckResponse])
async def list_checks(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    category: Optional[CheckCategory] = None,
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List all QA checks with optional filtering"""
    query = db.query(QACheck)

    if product_id is not None:
        query = query.filter(QACheck.product_id == product_id)

    if category is not None:
        query = query.filter(QACheck.category == category)

    if is_enabled is not None:
        query = query.filter(QACheck.is_enabled == is_enabled)

    checks = query.offset(skip).limit(limit).all()
    return checks


@router.get("/{check_id}", response_model=QACheckResponse)
async def get_check(check_id: int, db: Session = Depends(get_db)):
    """Get a specific QA check by ID"""
    check = db.query(QACheck).filter(QACheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="QA check not found")
    return check


@router.post("/", response_model=QACheckResponse, status_code=status.HTTP_201_CREATED)
async def create_check(check: QACheckCreate, db: Session = Depends(get_db)):
    """Create a new QA check"""
    # Verify product exists
    product = db.query(Product).filter(Product.id == check.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if check_id already exists
    existing = db.query(QACheck).filter(QACheck.check_id == check.check_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Check ID already exists")

    db_check = QACheck(**check.dict())
    db.add(db_check)
    db.commit()
    db.refresh(db_check)
    return db_check


@router.put("/{check_id}", response_model=QACheckResponse)
async def update_check(
    check_id: int, check: QACheckUpdate, db: Session = Depends(get_db)
):
    """Update a QA check"""
    db_check = db.query(QACheck).filter(QACheck.id == check_id).first()
    if not db_check:
        raise HTTPException(status_code=404, detail="QA check not found")

    # Update fields
    update_data = check.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_check, field, value)

    db_check.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_check)
    return db_check


@router.delete("/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_check(check_id: int, db: Session = Depends(get_db)):
    """Delete a QA check"""
    db_check = db.query(QACheck).filter(QACheck.id == check_id).first()
    if not db_check:
        raise HTTPException(status_code=404, detail="QA check not found")

    db.delete(db_check)
    db.commit()
    return None


@router.post("/{check_id}/run", response_model=QAResultResponse)
async def run_check(
    check_id: int,
    request: RunCheckRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Run a specific QA check"""
    check = db.query(QACheck).filter(QACheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="QA check not found")

    if not check.is_enabled:
        raise HTTPException(status_code=400, detail="Check is disabled")

    product = db.query(Product).filter(Product.id == check.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Initialize QA engine
    qa_engine = QAEngine()

    # Run the check
    started_at = datetime.utcnow()
    result = await qa_engine.run_single_check(product.name, check.check_id)
    completed_at = datetime.utcnow()
    duration = (completed_at - started_at).total_seconds()

    # Create result record
    db_result = QAResult(
        product_id=product.id,
        check_id=check.id,
        status=CheckStatus(result["status"]),
        score=result.get("score"),
        message=result.get("message"),
        details=result.get("details"),
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=duration,
        auto_fix_attempted=request.auto_fix and check.can_auto_fix,
        environment=request.environment,
        triggered_by="api",
    )

    # Attempt auto-fix if requested and available
    if request.auto_fix and check.can_auto_fix and result["status"] == "failed":
        fix_result = await qa_engine.auto_fix_issue(
            product.name, check.check_id, result
        )
        db_result.auto_fix_successful = fix_result.get("success", False)
        db_result.auto_fix_details = fix_result

    db.add(db_result)

    # Update check last_run
    check.last_run = completed_at

    db.commit()
    db.refresh(db_result)

    return db_result


@router.get("/{check_id}/results", response_model=List[QAResultResponse])
async def get_check_results(
    check_id: int,
    skip: int = 0,
    limit: int = 50,
    status: Optional[CheckStatus] = None,
    db: Session = Depends(get_db),
):
    """Get results for a specific check"""
    check = db.query(QACheck).filter(QACheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="QA check not found")

    query = db.query(QAResult).filter(QAResult.check_id == check_id)

    if status is not None:
        query = query.filter(QAResult.status == status)

    results = query.order_by(QAResult.created_at.desc()).offset(skip).limit(limit).all()
    return results


@router.post("/{check_id}/enable")
async def enable_check(check_id: int, db: Session = Depends(get_db)):
    """Enable a QA check"""
    check = db.query(QACheck).filter(QACheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="QA check not found")

    check.is_enabled = True
    check.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Check enabled successfully", "check_id": check_id}


@router.post("/{check_id}/disable")
async def disable_check(check_id: int, db: Session = Depends(get_db)):
    """Disable a QA check"""
    check = db.query(QACheck).filter(QACheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="QA check not found")

    check.is_enabled = False
    check.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Check disabled successfully", "check_id": check_id}


@router.get("/categories/list")
async def list_categories():
    """List all available check categories"""
    return {
        "categories": [
            {"value": cat.value, "name": cat.value.replace("_", " ").title()}
            for cat in CheckCategory
        ]
    }


@router.get("/severities/list")
async def list_severities():
    """List all available severity levels"""
    return {
        "severities": [
            {"value": sev.value, "name": sev.value.upper()} for sev in CheckSeverity
        ]
    }
