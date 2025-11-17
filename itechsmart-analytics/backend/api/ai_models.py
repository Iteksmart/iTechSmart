"""
iTechSmart Analytics - AI Models API
Endpoints for AI model management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models_ai import AIModel, ModelType, ModelStatus
from ..ai_insights_engine import AIInsightsEngine

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================


class ModelCreate(BaseModel):
    name: str
    model_type: str
    algorithm: str
    description: Optional[str] = None
    hyperparameters: Optional[dict] = None
    features: Optional[List[str]] = None
    target_variable: Optional[str] = None


class ModelTrain(BaseModel):
    training_data: List[dict]
    validation_split: float = 0.2


class ModelResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    description: Optional[str]
    model_type: str
    status: str
    algorithm: str
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    rmse: Optional[float]
    mae: Optional[float]
    r2_score: Optional[float]
    is_deployed: bool
    created_at: datetime
    last_trained_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================


@router.post("/models", response_model=ModelResponse)
def create_model(
    model: ModelCreate, tenant_id: int = Query(...), db: Session = Depends(get_db)
):
    """Create a new AI model"""
    try:
        engine = AIInsightsEngine(db, tenant_id)

        # Convert string to enum
        model_type = ModelType[model.model_type.upper()]

        new_model = engine.create_model(
            name=model.name,
            model_type=model_type,
            algorithm=model.algorithm,
            description=model.description,
            hyperparameters=model.hyperparameters,
            features=model.features,
            target_variable=model.target_variable,
        )

        return new_model
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models", response_model=List[ModelResponse])
def list_models(
    tenant_id: int = Query(...),
    model_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all AI models"""
    query = db.query(AIModel).filter(AIModel.tenant_id == tenant_id)

    if model_type:
        query = query.filter(AIModel.model_type == ModelType[model_type.upper()])

    if status:
        query = query.filter(AIModel.status == ModelStatus[status.upper()])

    models = query.offset(skip).limit(limit).all()
    return models


@router.get("/models/{model_id}", response_model=ModelResponse)
def get_model(
    model_id: int, tenant_id: int = Query(...), db: Session = Depends(get_db)
):
    """Get a specific AI model"""
    model = (
        db.query(AIModel)
        .filter(AIModel.id == model_id, AIModel.tenant_id == tenant_id)
        .first()
    )

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model


@router.post("/models/{model_id}/train")
def train_model(
    model_id: int,
    training_data: ModelTrain,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Train an AI model"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        result = engine.train_model(
            model_id=model_id,
            training_data=training_data.training_data,
            validation_split=training_data.validation_split,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/models/{model_id}/deploy")
def deploy_model(
    model_id: int, tenant_id: int = Query(...), db: Session = Depends(get_db)
):
    """Deploy a trained model"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        result = engine.deploy_model(model_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models/{model_id}/performance")
def get_model_performance(
    model_id: int, tenant_id: int = Query(...), db: Session = Depends(get_db)
):
    """Get model performance metrics"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        performance = engine.get_model_performance(model_id)
        return performance
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models/{model_id}/feature-importance")
def get_feature_importance(
    model_id: int, tenant_id: int = Query(...), db: Session = Depends(get_db)
):
    """Get feature importance for a model"""
    try:
        engine = AIInsightsEngine(db, tenant_id)
        importance = engine.calculate_feature_importance(model_id)

        return [
            {
                "feature_name": fi.feature_name,
                "importance_score": fi.importance_score,
                "importance_rank": fi.importance_rank,
                "correlation_with_target": fi.correlation_with_target,
            }
            for fi in importance
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/models/{model_id}")
def delete_model(
    model_id: int, tenant_id: int = Query(...), db: Session = Depends(get_db)
):
    """Delete an AI model"""
    model = (
        db.query(AIModel)
        .filter(AIModel.id == model_id, AIModel.tenant_id == tenant_id)
        .first()
    )

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    db.delete(model)
    db.commit()

    return {"message": "Model deleted successfully"}


@router.put("/models/{model_id}")
def update_model(
    model_id: int,
    updates: dict,
    tenant_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Update model metadata"""
    model = (
        db.query(AIModel)
        .filter(AIModel.id == model_id, AIModel.tenant_id == tenant_id)
        .first()
    )

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    for key, value in updates.items():
        if hasattr(model, key):
            setattr(model, key, value)

    db.commit()
    db.refresh(model)

    return model
