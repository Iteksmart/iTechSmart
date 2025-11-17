"""
iTechSmart Inc. - API Endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel
import numpy as np

from ..core.ai_engine import ai_engine, ModelType, ModelStatus


router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


# Request/Response Models
class CreateModelRequest(BaseModel):
    name: str
    model_type: str
    algorithm: str
    version: str = "1.0.0"


class TrainModelRequest(BaseModel):
    X_train: List[List[float]]
    y_train: List[Union[float, int, str]]
    params: Optional[Dict[str, Any]] = None


class EvaluateModelRequest(BaseModel):
    X_test: List[List[float]]
    y_test: List[Union[float, int, str]]


class PredictRequest(BaseModel):
    input_data: List[List[float]]


class NLPRequest(BaseModel):
    text: str


class TextClassificationRequest(BaseModel):
    text: str
    categories: List[str]


class SummarizationRequest(BaseModel):
    text: str
    max_sentences: int = 3


class KeywordExtractionRequest(BaseModel):
    text: str
    top_k: int = 5


# Model Management Endpoints
@router.post("/models", response_model=Dict[str, str])
async def create_model(request: CreateModelRequest):
    """Create a new AI model"""
    try:
        model_id = ai_engine.create_model(
            name=request.name,
            model_type=ModelType(request.model_type),
            algorithm=request.algorithm,
            version=request.version,
        )

        return {"model_id": model_id, "message": "Model created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models")
async def list_models(model_type: Optional[str] = None, status: Optional[str] = None):
    """List all models"""
    try:
        model_type_enum = ModelType(model_type) if model_type else None
        status_enum = ModelStatus(status) if status else None

        models = ai_engine.list_models(model_type=model_type_enum, status=status_enum)

        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models/{model_id}")
async def get_model(model_id: str):
    """Get model details"""
    try:
        model_info = ai_engine.get_model_info(model_id)
        return model_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a model"""
    success = ai_engine.delete_model(model_id)

    if not success:
        raise HTTPException(status_code=404, detail="Model not found")

    return {"message": "Model deleted successfully"}


# Model Training Endpoints
@router.post("/models/{model_id}/train")
async def train_model(model_id: str, request: TrainModelRequest):
    """Train a model"""
    try:
        training_data = {"X_train": request.X_train, "y_train": request.y_train}

        ai_engine.train_model(
            model_id=model_id, training_data=training_data, params=request.params
        )

        return {"message": "Model training completed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/models/{model_id}/evaluate")
async def evaluate_model(model_id: str, request: EvaluateModelRequest):
    """Evaluate a model"""
    try:
        test_data = {"X_test": request.X_test, "y_test": request.y_test}

        metrics = ai_engine.evaluate_model(model_id=model_id, test_data=test_data)

        return {"metrics": metrics}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/models/{model_id}/deploy")
async def deploy_model(model_id: str):
    """Deploy a model"""
    try:
        ai_engine.deploy_model(model_id)
        return {"message": "Model deployed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Prediction Endpoints
@router.post("/models/{model_id}/predict")
async def predict(model_id: str, request: PredictRequest):
    """Make predictions with a model"""
    try:
        predictions = ai_engine.predict(
            model_id=model_id, input_data=request.input_data
        )

        return {"predictions": predictions}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# NLP Endpoints
@router.post("/nlp/sentiment")
async def sentiment_analysis(request: NLPRequest):
    """Analyze sentiment of text"""
    try:
        result = ai_engine.nlp_engine.sentiment_analysis(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/nlp/classify")
async def text_classification(request: TextClassificationRequest):
    """Classify text into categories"""
    try:
        result = ai_engine.nlp_engine.text_classification(
            text=request.text, categories=request.categories
        )
        return {"scores": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/nlp/entities")
async def named_entity_recognition(request: NLPRequest):
    """Extract named entities from text"""
    try:
        entities = ai_engine.nlp_engine.named_entity_recognition(request.text)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/nlp/summarize")
async def text_summarization(request: SummarizationRequest):
    """Summarize text"""
    try:
        summary = ai_engine.nlp_engine.text_summarization(
            text=request.text, max_sentences=request.max_sentences
        )
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/nlp/keywords")
async def keyword_extraction(request: KeywordExtractionRequest):
    """Extract keywords from text"""
    try:
        keywords = ai_engine.nlp_engine.keyword_extraction(
            text=request.text, top_k=request.top_k
        )
        return {"keywords": keywords}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Computer Vision Endpoints
@router.post("/cv/classify")
async def image_classification(
    image: UploadFile = File(...), classes: str = "person,car,dog,cat,building"
):
    """Classify image"""
    try:
        # Read image data
        image_data = await image.read()

        # Convert to numpy array (simplified)
        # In production, use PIL or OpenCV
        image_array = np.frombuffer(image_data, dtype=np.uint8)

        classes_list = classes.split(",")
        result = ai_engine.cv_engine.image_classification(
            image_data=image_array, classes=classes_list
        )

        return {"scores": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cv/detect")
async def object_detection(image: UploadFile = File(...)):
    """Detect objects in image"""
    try:
        image_data = await image.read()
        image_array = np.frombuffer(image_data, dtype=np.uint8)

        objects = ai_engine.cv_engine.object_detection(image_array)

        return {"objects": objects}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cv/faces")
async def face_detection(image: UploadFile = File(...)):
    """Detect faces in image"""
    try:
        image_data = await image.read()
        image_array = np.frombuffer(image_data, dtype=np.uint8)

        faces = ai_engine.cv_engine.face_detection(image_array)

        return {"faces": faces}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Model Marketplace Endpoints
@router.get("/marketplace/models")
async def list_pretrained_models():
    """List available pre-trained models"""
    models = ai_engine.list_pretrained_models()
    return {"models": models}


@router.post("/marketplace/models/{model_id}/deploy")
async def deploy_pretrained_model(model_id: str):
    """Deploy a pre-trained model from marketplace"""
    # In production, this would download and deploy the model
    return {
        "message": f"Pre-trained model {model_id} deployed successfully",
        "endpoint": f"/api/v1/ai/marketplace/models/{model_id}/predict",
    }


# AutoML Endpoints
@router.post("/automl/train")
async def automl_train(
    X_train: List[List[float]],
    y_train: List[Union[float, int, str]],
    task_type: str = "classification",
):
    """Automatically train and select best model"""
    try:
        # Try multiple algorithms
        algorithms = {
            "classification": ["random_forest", "logistic_regression", "xgboost"],
            "regression": ["random_forest", "linear_regression", "xgboost"],
        }

        best_model_id = None
        best_score = 0

        for algorithm in algorithms.get(task_type, []):
            # Create model
            model_id = ai_engine.create_model(
                name=f"AutoML_{algorithm}",
                model_type=ModelType(task_type.upper()),
                algorithm=algorithm,
            )

            # Train model
            training_data = {"X_train": X_train, "y_train": y_train}
            ai_engine.train_model(model_id, training_data)

            # Evaluate (using training data for simplicity)
            test_data = {"X_test": X_train[:10], "y_test": y_train[:10]}
            metrics = ai_engine.evaluate_model(model_id, test_data)

            score = metrics.get("accuracy", metrics.get("r2_score", 0))

            if score > best_score:
                best_score = score
                best_model_id = model_id

        return {
            "best_model_id": best_model_id,
            "best_score": best_score,
            "message": "AutoML training completed",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Health Check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iTechSmart Inc.",
        "models_count": len(ai_engine.models),
        "nlp_available": True,
        "cv_available": True,
    }
