"""
iTechSmart Analytics - Main Entry Point
ML-Powered Analytics Platform with AI Insights
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.database import init_db
from .api import ai_models, ai_predictions, ai_insights, ai_quality, agents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting iTechSmart Analytics...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down iTechSmart Analytics...")


# Create FastAPI app
app = FastAPI(
    title="iTechSmart Analytics",
    description="ML-Powered Analytics Platform with AI Insights - Part of iTechSmart Suite",
    version="1.1.0",
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

# Include AI routers
app.include_router(ai_models.router, prefix="/api/v1/ai", tags=["AI Models"])
app.include_router(ai_predictions.router, prefix="/api/v1/ai", tags=["AI Predictions"])
app.include_router(ai_insights.router, prefix="/api/v1/ai", tags=["AI Insights"])
app.include_router(ai_quality.router, prefix="/api/v1/ai", tags=["AI Quality"])

# Include Agent router
app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "iTechSmart Analytics",
        "version": "1.1.0",
        "description": "ML-Powered Analytics Platform with AI Insights",
        "status": "operational",
        "suite": "iTechSmart Suite",
        "features": [
            "AI/ML Model Management",
            "Predictive Analytics",
            "Anomaly Detection",
            "Trend Analysis",
            "Pattern Recognition",
            "Forecasting",
            "AI-Generated Insights",
            "Intelligent Recommendations",
            "Data Quality Assessment",
            "Feature Importance Analysis",
            "Dashboard Builder (12 widget types)",
            "Data Ingestion (100+ connectors)",
            "Report Generator (5 formats)",
            "Real-time Analytics"
        ],
        "endpoints": {
            "ai_models": "/api/v1/ai/models",
            "ai_predictions": "/api/v1/ai/predictions",
            "ai_insights": "/api/v1/ai/insights",
            "ai_quality": "/api/v1/ai/quality",
               "agents": "/api/v1/agents",
            "analytics": "/api/analytics",
            "dashboards": "/api/dashboards",
            "reports": "/api/reports",
            "data": "/api/data",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iTechSmart Analytics",
        "version": "1.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)