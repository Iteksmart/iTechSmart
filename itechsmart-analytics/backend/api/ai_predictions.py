"""
iTechSmart Analytics - AI Predictions API
Endpoints for making predictions and forecasts
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models_ai import Prediction, PredictionStatus
from ..ai_insights_engine import AIInsightsEngine

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class PredictionRequest(BaseModel):
    model_id: int
    input_data: dict
    prediction_horizon: Optional[int] = None


class BatchPredictionRequest(BaseModel):
    model_id: int
    input_data_list: List[dict]


class ForecastRequest(BaseModel):
    metric_name: str
    historical_data: List[dict]
    forecast_periods: int = 30


class PredictionResponse(BaseModel):
    id: int
    model_id: int
    prediction_type: str
    predicted_value: dict
    confidence_score: float
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.post("/predictions", response_model=PredictionResponse)
def make_prediction(
    request: PredictionRequest,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Make a single prediction"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        prediction = engine.make_prediction(
            model_id=request.model_id,
            input_data=request.input_data,
            prediction_horizon=request.prediction_horizon
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/predictions/batch")
def batch_predict(
    request: BatchPredictionRequest,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Make batch predictions"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        predictions = engine.batch_predict(
            model_id=request.model_id,
            input_data_list=request.input_data_list
        )
        
        return {
            'total_predictions': len(predictions),
            'predictions': [
                {
                    'id': p.id,
                    'predicted_value': p.predicted_value,
                    'confidence_score': p.confidence_score
                }
                for p in predictions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/predictions", response_model=List[PredictionResponse])
def list_predictions(
    tenant_id: int = Query(...),
    model_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List predictions"""
    query = db.query(Prediction).filter(Prediction.tenant_id == tenant_id)
    
    if model_id:
        query = query.filter(Prediction.model_id == model_id)
    
    if status:
        query = query.filter(Prediction.status == PredictionStatus[status.upper()])
    
    predictions = query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    return predictions


@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
def get_prediction(
    prediction_id: int,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get a specific prediction"""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.tenant_id == tenant_id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return prediction


@router.post("/predictions/{prediction_id}/validate")
def validate_prediction(
    prediction_id: int,
    actual_value: dict,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Validate a prediction with actual value"""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.tenant_id == tenant_id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    prediction.actual_value = actual_value
    prediction.validated_at = datetime.utcnow()
    
    # Calculate error if numeric
    if isinstance(prediction.predicted_value, (int, float)) and isinstance(actual_value, (int, float)):
        prediction.prediction_error = abs(prediction.predicted_value - actual_value)
    
    db.commit()
    db.refresh(prediction)
    
    return prediction


@router.post("/forecast")
def forecast_metric(
    request: ForecastRequest,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Forecast future values for a metric"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        forecasts = engine.forecast_metric(
            metric_name=request.metric_name,
            historical_data=request.historical_data,
            forecast_periods=request.forecast_periods
        )
        
        return {
            'metric_name': request.metric_name,
            'forecast_periods': request.forecast_periods,
            'forecasts': forecasts
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/predictions/statistics")
def get_prediction_statistics(
    tenant_id: int = Query(...),
    model_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get prediction statistics"""
    query = db.query(Prediction).filter(Prediction.tenant_id == tenant_id)
    
    if model_id:
        query = query.filter(Prediction.model_id == model_id)
    
    predictions = query.all()
    
    if not predictions:
        return {
            'total_predictions': 0,
            'avg_confidence': 0,
            'avg_execution_time_ms': 0
        }
    
    import statistics
    
    return {
        'total_predictions': len(predictions),
        'avg_confidence': statistics.mean([p.confidence_score for p in predictions]),
        'avg_execution_time_ms': statistics.mean([p.execution_time_ms for p in predictions if p.execution_time_ms]),
        'status_breakdown': {
            'completed': len([p for p in predictions if p.status == PredictionStatus.COMPLETED]),
            'pending': len([p for p in predictions if p.status == PredictionStatus.PENDING]),
            'failed': len([p for p in predictions if p.status == PredictionStatus.FAILED])
        }
    }