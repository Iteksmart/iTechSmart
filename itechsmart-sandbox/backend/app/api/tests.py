"""
iTechSmart Sandbox - Test Execution API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.sandbox_engine import SandboxEngine

router = APIRouter(prefix="/api/tests", tags=["Tests"])


class TestRunCreate(BaseModel):
    sandbox_id: str
    product_name: str
    test_suite: str
    test_type: str = "integration"


@router.post("/run")
def run_test_suite(test_run: TestRunCreate, db: Session = Depends(get_db)):
    """Run test suite in sandbox"""
    engine = SandboxEngine(db)

    try:
        result = engine.run_test_suite(
            test_run.sandbox_id,
            test_run.product_name,
            test_run.test_suite,
            test_run.test_type,
        )
        return {
            "test_run_id": result.id,
            "total_tests": result.total_tests,
            "passed_tests": result.passed_tests,
            "failed_tests": result.failed_tests,
            "skipped_tests": result.skipped_tests,
            "duration_seconds": result.duration_seconds,
            "results": result.results,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
