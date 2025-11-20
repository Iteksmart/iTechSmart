"""
iTechSmart Suite v1.7.0 - AI Inference Service
Next Generation AI-Native IT Operations Platform

Real-time AI inference service with sub-50ms response time
for predictive maintenance and intelligent automation.
"""

import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any

import torch
import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus Metrics
PREDICTION_COUNTER = Counter('ai_predictions_total', 'Total AI predictions', ['model', 'status'])
PREDICTION_LATENCY = Histogram('ai_prediction_duration_seconds', 'AI prediction latency')
MODEL_ACCURACY = Gauge('ai_model_accuracy', 'Current model accuracy', ['model'])
ACTIVE_CONNECTIONS = Gauge('ai_active_connections', 'Active inference connections')

# Global model cache
model_cache = {}
model_metadata = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("Starting AI Inference Service v1.7.0")
    
    # Load models on startup
    await load_models()
    
    logger.info("AI Inference Service ready")
    yield
    
    logger.info("Shutting down AI Inference Service")

app = FastAPI(
    title="iTechSmart AI Inference Service",
    description="Real-time AI inference for predictive maintenance",
    version="1.7.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AIModel:
    """Base AI Model class"""
    
    def __init__(self, model_path: str, model_name: str):
        self.model_path = model_path
        self.model_name = model_name
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.last_updated = time.time()
        
    async def load(self):
        """Load model from disk"""
        try:
            # Load PyTorch model
            self.model = torch.load(self.model_path, map_location=self.device)
            self.model.eval()
            logger.info(f"Model {self.model_name} loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
            
    async def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction"""
        start_time = time.time()
        
        try:
            # Convert input to tensor
            input_tensor = self._preprocess(input_data)
            
            # Make prediction
            with torch.no_grad():
                output = self.model(input_tensor)
                
            # Post-process output
            prediction = self._postprocess(output)
            
            # Update metrics
            latency = time.time() - start_time
            PREDICTION_LATENCY.observe(latency)
            PREDICTION_COUNTER.labels(model=self.model_name, status='success').inc()
            
            return {
                "prediction": prediction,
                "confidence": float(torch.max(output)),
                "latency_ms": latency * 1000,
                "model_version": "1.7.0",
                "timestamp": time.time()
            }
            
        except Exception as e:
            PREDICTION_COUNTER.labels(model=self.model_name, status='error').inc()
            logger.error(f"Prediction failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    def _preprocess(self, input_data: Dict[str, Any]) -> torch.Tensor:
        """Preprocess input data"""
        # Feature extraction and normalization
        features = np.array([
            input_data.get('cpu_usage', 0),
            input_data.get('memory_usage', 0),
            input_data.get('disk_usage', 0),
            input_data.get('network_io', 0),
            input_data.get('error_rate', 0),
            input_data.get('response_time', 0)
        ], dtype=np.float32)
        
        # Normalize features
        features = (features - np.mean(features)) / (np.std(features) + 1e-8)
        
        # Convert to tensor and add batch dimension
        return torch.FloatTensor(features).unsqueeze(0).to(self.device)
        
    def _postprocess(self, output: torch.Tensor) -> Dict[str, Any]:
        """Post-process model output"""
        probabilities = torch.softmax(output, dim=1)
        prediction = torch.argmax(probabilities, dim=1)
        
        return {
            "class": int(prediction[0]),
            "probabilities": probabilities[0].cpu().numpy().tolist(),
            "risk_level": "high" if float(probabilities[0][1]) > 0.8 else "medium" if float(probabilities[0][1]) > 0.5 else "low"
        }

async def load_models():
    """Load all AI models"""
    models_to_load = [
        {
            "name": "predictive_maintenance",
            "path": "/models/predictive-maintenance-v1.7.0/model.pth"
        },
        {
            "name": "anomaly_detection",
            "path": "/models/anomaly-detection-v1.7.0/model.pth"
        },
        {
            "name": "performance_optimization",
            "path": "/models/performance-optimization-v1.7.0/model.pth"
        }
    ]
    
    for model_config in models_to_load:
        try:
            model = AIModel(model_config["path"], model_config["name"])
            await model.load()
            model_cache[model_config["name"]] = model
            model_metadata[model_config["name"]] = {
                "loaded_at": time.time(),
                "version": "1.7.0",
                "path": model_config["path"]
            }
            logger.info(f"Loaded model: {model_config['name']}")
        except Exception as e:
            logger.error(f"Failed to load model {model_config['name']}: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "iTechSmart AI Inference Service",
        "version": "1.7.0",
        "status": "healthy",
        "models_loaded": len(model_cache),
        "device": str(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "models": list(model_cache.keys()),
        "device": str(torch.device("cuda" if torch.cuda.is_available() else "cpu")),
        "memory_usage": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    if len(model_cache) == 0:
        raise HTTPException(status_code=503, detail="Models not loaded")
    return {"status": "ready", "models_loaded": len(model_cache)}

@app.post("/predict")
async def predict(request_data: Dict[str, Any]):
    """Real-time AI prediction endpoint"""
    ACTIVE_CONNECTIONS.inc()
    
    try:
        model_name = request_data.get("model", "predictive_maintenance")
        
        if model_name not in model_cache:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
            
        model = model_cache[model_name]
        result = await model.predict(request_data)
        
        return result
        
    finally:
        ACTIVE_CONNECTIONS.dec()

@app.post("/batch_predict")
async def batch_predict(request_data: Dict[str, Any]):
    """Batch prediction endpoint"""
    ACTIVE_CONNECTIONS.inc()
    
    try:
        model_name = request_data.get("model", "predictive_maintenance")
        inputs = request_data.get("inputs", [])
        
        if model_name not in model_cache:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
            
        model = model_cache[model_name]
        results = []
        
        for input_data in inputs:
            result = await model.predict(input_data)
            results.append(result)
            
        return {
            "results": results,
            "batch_size": len(inputs),
            "total_latency_ms": sum(r["latency_ms"] for r in results)
        }
        
    finally:
        ACTIVE_CONNECTIONS.dec()

@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "models": list(model_cache.keys()),
        "metadata": model_metadata
    }

@app.post("/reload_model")
async def reload_model(request_data: Dict[str, Any]):
    """Reload a specific model"""
    model_name = request_data.get("model")
    
    if not model_name or model_name not in model_cache:
        raise HTTPException(status_code=404, detail="Model not found")
        
    try:
        # Reload model
        model = model_cache[model_name]
        await model.load()
        
        # Update metadata
        model_metadata[model_name]["loaded_at"] = time.time()
        
        logger.info(f"Reloaded model: {model_name}")
        return {"status": "success", "model": model_name}
        
    except Exception as e:
        logger.error(f"Failed to reload model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Update model accuracy gauge (example values)
    for model_name in model_cache:
        MODEL_ACCURACY.labels(model=model_name).set(0.95)  # 95% accuracy
        
    return generate_latest()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        workers=4,
        loop="uvloop",
        http="httptools"
    )