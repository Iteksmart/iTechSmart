"""
iTechSmart Supreme - Dashboard API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.supreme_engine import SupremeEngine

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    engine = SupremeEngine(db)
    return engine.get_dashboard_stats()