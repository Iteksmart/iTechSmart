"""
API endpoints for QA scan management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.models import QAScan, Product, QAResult, CheckStatus
from app.core.qa_engine import QAEngine
from pydantic import BaseModel

router = APIRouter(prefix="/scans", tags=["scans"])


# Pydantic models
class ScanRequest(BaseModel):
    scan_type: str = "full"  # full, incremental, targeted
    product_ids: Optional[List[int]] = None  # None = all products
    check_categories: Optional[List[str]] = None  # None = all categories
    auto_fix: bool = False
    environment: str = "production"


class ScanResponse(BaseModel):
    id: int
    scan_type: str
    triggered_by: str
    product_ids: Optional[List[int]]
    check_categories: Optional[List[str]]
    total_products: int
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    skipped_checks: int
    overall_score: float
    average_product_score: float
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    status: str
    auto_fixes_attempted: int
    auto_fixes_successful: int
    config: Optional[dict]
    summary: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Create and start a new QA scan"""

    # Determine which products to scan
    if request.product_ids:
        products = (
            db.query(Product)
            .filter(Product.id.in_(request.product_ids), Product.is_active == True)
            .all()
        )
    else:
        products = db.query(Product).filter(Product.is_active == True).all()

    if not products:
        raise HTTPException(status_code=400, detail="No active products found to scan")

    # Create scan record
    scan = QAScan(
        scan_type=request.scan_type,
        triggered_by="api",
        product_ids=[p.id for p in products],
        check_categories=request.check_categories,
        total_products=len(products),
        started_at=datetime.utcnow(),
        status="running",
        config={"auto_fix": request.auto_fix, "environment": request.environment},
    )

    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Run scan in background
    background_tasks.add_task(
        run_scan_task,
        scan.id,
        [p.name for p in products],
        request.check_categories,
        request.auto_fix,
    )

    return scan


async def run_scan_task(
    scan_id: int,
    product_names: List[str],
    check_categories: Optional[List[str]],
    auto_fix: bool,
):
    """Background task to run the scan"""
    from app.core.database import get_db_context

    with get_db_context() as db:
        scan = db.query(QAScan).filter(QAScan.id == scan_id).first()
        if not scan:
            return

        try:
            qa_engine = QAEngine()

            total_checks = 0
            passed_checks = 0
            failed_checks = 0
            warning_checks = 0
            skipped_checks = 0
            auto_fixes_attempted = 0
            auto_fixes_successful = 0
            product_scores = []

            # Run checks for each product
            for product_name in product_names:
                results = await qa_engine.run_all_checks(product_name)

                for result in results:
                    total_checks += 1

                    if result["status"] == "passed":
                        passed_checks += 1
                    elif result["status"] == "failed":
                        failed_checks += 1

                        # Attempt auto-fix if enabled
                        if auto_fix and result.get("can_auto_fix"):
                            auto_fixes_attempted += 1
                            fix_result = await qa_engine.auto_fix_issue(
                                product_name, result["check_id"], result
                            )
                            if fix_result.get("success"):
                                auto_fixes_successful += 1
                    elif result["status"] == "warning":
                        warning_checks += 1
                    elif result["status"] == "skipped":
                        skipped_checks += 1

                # Calculate product score
                product = db.query(Product).filter(Product.name == product_name).first()
                if product:
                    product_scores.append(product.qa_score)

            # Calculate overall scores
            overall_score = (
                (passed_checks / total_checks * 100) if total_checks > 0 else 0
            )
            average_product_score = (
                sum(product_scores) / len(product_scores) if product_scores else 0
            )

            # Update scan record
            scan.total_checks = total_checks
            scan.passed_checks = passed_checks
            scan.failed_checks = failed_checks
            scan.warning_checks = warning_checks
            scan.skipped_checks = skipped_checks
            scan.overall_score = overall_score
            scan.average_product_score = average_product_score
            scan.auto_fixes_attempted = auto_fixes_attempted
            scan.auto_fixes_successful = auto_fixes_successful
            scan.completed_at = datetime.utcnow()
            scan.duration_seconds = (
                scan.completed_at - scan.started_at
            ).total_seconds()
            scan.status = "completed"
            scan.summary = {
                "total_products": len(product_names),
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "warning_checks": warning_checks,
                "pass_rate": (
                    (passed_checks / total_checks * 100) if total_checks > 0 else 0
                ),
                "auto_fix_success_rate": (
                    (auto_fixes_successful / auto_fixes_attempted * 100)
                    if auto_fixes_attempted > 0
                    else 0
                ),
            }

            db.commit()

        except Exception as e:
            scan.status = "failed"
            scan.completed_at = datetime.utcnow()
            scan.duration_seconds = (
                scan.completed_at - scan.started_at
            ).total_seconds()
            scan.summary = {"error": str(e)}
            db.commit()


@router.get("/", response_model=List[ScanResponse])
async def list_scans(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all scans with optional filtering"""
    query = db.query(QAScan)

    if status:
        query = query.filter(QAScan.status == status)

    scans = query.order_by(QAScan.created_at.desc()).offset(skip).limit(limit).all()
    return scans


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: int, db: Session = Depends(get_db)):
    """Get a specific scan by ID"""
    scan = db.query(QAScan).filter(QAScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/{scan_id}/results")
async def get_scan_results(
    scan_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[CheckStatus] = None,
    db: Session = Depends(get_db),
):
    """Get detailed results for a scan"""
    scan = db.query(QAScan).filter(QAScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Get results for products in this scan
    query = db.query(QAResult).filter(
        QAResult.product_id.in_(scan.product_ids),
        QAResult.created_at >= scan.started_at,
    )

    if scan.completed_at:
        query = query.filter(QAResult.created_at <= scan.completed_at)

    if status:
        query = query.filter(QAResult.status == status)

    results = query.order_by(QAResult.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "scan_id": scan_id,
        "total_results": query.count(),
        "results": [
            {
                "id": r.id,
                "product_id": r.product_id,
                "check_id": r.check_id,
                "status": r.status,
                "score": r.score,
                "message": r.message,
                "duration_seconds": r.duration_seconds,
                "auto_fix_attempted": r.auto_fix_attempted,
                "auto_fix_successful": r.auto_fix_successful,
                "created_at": r.created_at,
            }
            for r in results
        ],
    }


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    """Delete a scan"""
    scan = db.query(QAScan).filter(QAScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    db.delete(scan)
    db.commit()
    return None


@router.get("/stats/summary")
async def get_scan_stats(db: Session = Depends(get_db)):
    """Get overall scan statistics"""
    total_scans = db.query(QAScan).count()
    completed_scans = db.query(QAScan).filter(QAScan.status == "completed").count()
    running_scans = db.query(QAScan).filter(QAScan.status == "running").count()
    failed_scans = db.query(QAScan).filter(QAScan.status == "failed").count()

    # Get latest scan
    latest_scan = db.query(QAScan).order_by(QAScan.created_at.desc()).first()

    # Calculate average scores
    completed = db.query(QAScan).filter(QAScan.status == "completed").all()
    avg_overall_score = (
        sum(s.overall_score for s in completed) / len(completed) if completed else 0
    )
    avg_product_score = (
        sum(s.average_product_score for s in completed) / len(completed)
        if completed
        else 0
    )

    return {
        "total_scans": total_scans,
        "completed_scans": completed_scans,
        "running_scans": running_scans,
        "failed_scans": failed_scans,
        "average_overall_score": round(avg_overall_score, 2),
        "average_product_score": round(avg_product_score, 2),
        "latest_scan": (
            {
                "id": latest_scan.id,
                "status": latest_scan.status,
                "overall_score": latest_scan.overall_score,
                "started_at": latest_scan.started_at,
                "completed_at": latest_scan.completed_at,
            }
            if latest_scan
            else None
        ),
    }
