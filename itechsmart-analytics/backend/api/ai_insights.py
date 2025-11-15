"""
iTechSmart Analytics - AI Insights API
Endpoints for AI-generated insights and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models_ai import Insight, Recommendation, InsightType, InsightSeverity
from ..ai_insights_engine import AIInsightsEngine

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class InsightGenerationRequest(BaseModel):
    data: List[dict]
    metrics: List[str]
    time_range_days: int = 30


class InsightResponse(BaseModel):
    id: int
    insight_type: str
    severity: str
    title: str
    description: str
    affected_metrics: List[str]
    statistical_significance: Optional[float]
    detection_date: datetime
    is_actionable: bool
    is_acknowledged: bool
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    id: int
    recommendation_type: str
    title: str
    description: str
    expected_impact: Optional[str]
    estimated_cost_savings: Optional[float]
    priority: int
    urgency: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.post("/insights/generate")
def generate_insights(
    request: InsightGenerationRequest,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Generate AI insights from data"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        insights = engine.generate_insights(
            data=request.data,
            metrics=request.metrics,
            time_range_days=request.time_range_days
        )
        
        return {
            'total_insights': len(insights),
            'insights': [
                {
                    'id': i.id,
                    'type': i.insight_type.value,
                    'severity': i.severity.value,
                    'title': i.title,
                    'description': i.description
                }
                for i in insights
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/insights", response_model=List[InsightResponse])
def list_insights(
    tenant_id: int = Query(...),
    insight_type: Optional[str] = None,
    severity: Optional[str] = None,
    is_acknowledged: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List AI insights"""
    query = db.query(Insight).filter(Insight.tenant_id == tenant_id)
    
    if insight_type:
        query = query.filter(Insight.insight_type == InsightType[insight_type.upper()])
    
    if severity:
        query = query.filter(Insight.severity == InsightSeverity[severity.upper()])
    
    if is_acknowledged is not None:
        query = query.filter(Insight.is_acknowledged == is_acknowledged)
    
    insights = query.order_by(Insight.detection_date.desc()).offset(skip).limit(limit).all()
    return insights


@router.get("/insights/{insight_id}", response_model=InsightResponse)
def get_insight(
    insight_id: int,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get a specific insight"""
    insight = db.query(Insight).filter(
        Insight.id == insight_id,
        Insight.tenant_id == tenant_id
    ).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    return insight


@router.post("/insights/{insight_id}/acknowledge")
def acknowledge_insight(
    insight_id: int,
    user_id: int,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Acknowledge an insight"""
    insight = db.query(Insight).filter(
        Insight.id == insight_id,
        Insight.tenant_id == tenant_id
    ).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.is_acknowledged = True
    insight.acknowledged_by = user_id
    insight.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(insight)
    
    return insight


@router.post("/insights/{insight_id}/recommendations")
def generate_recommendations(
    insight_id: int,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Generate recommendations for an insight"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        recommendations = engine.generate_recommendations(insight_id)
        
        return {
            'insight_id': insight_id,
            'total_recommendations': len(recommendations),
            'recommendations': [
                {
                    'id': r.id,
                    'type': r.recommendation_type.value,
                    'title': r.title,
                    'priority': r.priority,
                    'urgency': r.urgency
                }
                for r in recommendations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recommendations", response_model=List[RecommendationResponse])
def list_recommendations(
    tenant_id: int = Query(...),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List recommendations"""
    query = db.query(Recommendation).filter(Recommendation.tenant_id == tenant_id)
    
    if status:
        query = query.filter(Recommendation.status == status)
    
    recommendations = query.order_by(Recommendation.priority).offset(skip).limit(limit).all()
    return recommendations


@router.get("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get a specific recommendation"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.tenant_id == tenant_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    return recommendation


@router.post("/recommendations/{recommendation_id}/accept")
def accept_recommendation(
    recommendation_id: int,
    user_id: int,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Accept a recommendation"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.tenant_id == tenant_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.status = "accepted"
    recommendation.accepted_by = user_id
    recommendation.accepted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(recommendation)
    
    return recommendation


@router.post("/recommendations/{recommendation_id}/implement")
def implement_recommendation(
    recommendation_id: int,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Mark recommendation as implemented"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.tenant_id == tenant_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.status = "implemented"
    recommendation.implemented_at = datetime.utcnow()
    
    db.commit()
    db.refresh(recommendation)
    
    return recommendation


@router.get("/insights/statistics")
def get_insight_statistics(
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get insight statistics"""
    insights = db.query(Insight).filter(Insight.tenant_id == tenant_id).all()
    
    if not insights:
        return {
            'total_insights': 0,
            'by_type': {},
            'by_severity': {},
            'acknowledged_count': 0
        }
    
    return {
        'total_insights': len(insights),
        'by_type': {
            'anomaly': len([i for i in insights if i.insight_type == InsightType.ANOMALY]),
            'trend': len([i for i in insights if i.insight_type == InsightType.TREND]),
            'pattern': len([i for i in insights if i.insight_type == InsightType.PATTERN]),
            'correlation': len([i for i in insights if i.insight_type == InsightType.CORRELATION])
        },
        'by_severity': {
            'critical': len([i for i in insights if i.severity == InsightSeverity.CRITICAL]),
            'high': len([i for i in insights if i.severity == InsightSeverity.HIGH]),
            'medium': len([i for i in insights if i.severity == InsightSeverity.MEDIUM]),
            'low': len([i for i in insights if i.severity == InsightSeverity.LOW]),
            'info': len([i for i in insights if i.severity == InsightSeverity.INFO])
        },
        'acknowledged_count': len([i for i in insights if i.is_acknowledged]),
        'actionable_count': len([i for i in insights if i.is_actionable])
    }