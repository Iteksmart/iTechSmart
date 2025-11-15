"""
iTechSmart Analytics - AI Data Quality API
Endpoints for data quality assessment
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models_ai import DataQualityScore
from ..ai_insights_engine import AIInsightsEngine

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class DataQualityRequest(BaseModel):
    dataset_name: str
    data: List[dict]


class DataQualityResponse(BaseModel):
    id: int
    dataset_name: str
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    validity_score: float
    uniqueness_score: float
    overall_score: float
    missing_values_count: int
    duplicate_count: int
    assessed_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.post("/quality/assess", response_model=DataQualityResponse)
def assess_data_quality(
    request: DataQualityRequest,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Assess data quality"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        quality_score = engine.assess_data_quality(
            dataset_name=request.dataset_name,
            data=request.data
        )
        return quality_score
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/quality/scores", response_model=List[DataQualityResponse])
def list_quality_scores(
    tenant_id: int = Query(...),
    dataset_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List data quality scores"""
    query = db.query(DataQualityScore).filter(DataQualityScore.tenant_id == tenant_id)
    
    if dataset_name:
        query = query.filter(DataQualityScore.dataset_name == dataset_name)
    
    scores = query.order_by(DataQualityScore.assessed_at.desc()).offset(skip).limit(limit).all()
    return scores


@router.get("/quality/scores/{score_id}", response_model=DataQualityResponse)
def get_quality_score(
    score_id: int,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get a specific quality score"""
    score = db.query(DataQualityScore).filter(
        DataQualityScore.id == score_id,
        DataQualityScore.tenant_id == tenant_id
    ).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="Quality score not found")
    
    return score


@router.get("/quality/summary")
def get_quality_summary(
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get data quality summary across all datasets"""
    scores = db.query(DataQualityScore).filter(
        DataQualityScore.tenant_id == tenant_id
    ).all()
    
    if not scores:
        return {
            'total_assessments': 0,
            'avg_overall_score': 0,
            'datasets_assessed': 0
        }
    
    import statistics
    
    return {
        'total_assessments': len(scores),
        'avg_overall_score': statistics.mean([s.overall_score for s in scores]),
        'avg_completeness': statistics.mean([s.completeness_score for s in scores]),
        'avg_accuracy': statistics.mean([s.accuracy_score for s in scores]),
        'avg_consistency': statistics.mean([s.consistency_score for s in scores]),
        'avg_validity': statistics.mean([s.validity_score for s in scores]),
        'avg_uniqueness': statistics.mean([s.uniqueness_score for s in scores]),
        'datasets_assessed': len(set(s.dataset_name for s in scores)),
        'total_missing_values': sum(s.missing_values_count for s in scores),
        'total_duplicates': sum(s.duplicate_count for s in scores)
    }


@router.get("/quality/trends")
def get_quality_trends(
    tenant_id: int = Query(...),
    dataset_name: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get data quality trends over time"""
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(DataQualityScore).filter(
        DataQualityScore.tenant_id == tenant_id,
        DataQualityScore.assessed_at >= start_date
    )
    
    if dataset_name:
        query = query.filter(DataQualityScore.dataset_name == dataset_name)
    
    scores = query.order_by(DataQualityScore.assessed_at).all()
    
    return {
        'dataset_name': dataset_name,
        'time_range_days': days,
        'data_points': len(scores),
        'trend_data': [
            {
                'date': s.assessed_at.isoformat(),
                'overall_score': s.overall_score,
                'completeness': s.completeness_score,
                'accuracy': s.accuracy_score,
                'consistency': s.consistency_score
            }
            for s in scores
        ]
    }