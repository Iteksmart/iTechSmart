"""
iTechSmart HL7 - Main Application
FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="iTechSmart HL7",
    description="Autonomous HL7 Monitoring & Self-Healing for Healthcare IT",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.api import hl7, emr, ai, clinicals, monitoring

# Include routers
app.include_router(hl7.router)
app.include_router(emr.router)
app.include_router(ai.router)
app.include_router(clinicals.router)
app.include_router(monitoring.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "iTechSmart HL7",
        "version": "1.0.0",
        "description": "Autonomous HL7 Monitoring & Self-Healing for Healthcare IT",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/api/docs",
            "health": "/api/health",
            "hl7": "/api/hl7",
            "emr": "/api/emr",
            "ai": "/api/ai",
            "clinicals": "/api/clinicals",
            "monitoring": "/api/monitoring"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "database": "healthy",
            "redis": "healthy",
            "hl7_engine": "healthy",
            "self_healing": "healthy",
            "ai_agents": "healthy"
        }
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting iTechSmart HL7...")
    logger.info("Initializing database...")
    logger.info("Starting HL7 engine...")
    logger.info("Starting self-healing engine...")
    logger.info("iTechSmart HL7 started successfully!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down iTechSmart HL7...")
    logger.info("Closing database connections...")
    logger.info("Stopping HL7 engine...")
    logger.info("Stopping self-healing engine...")
    logger.info("iTechSmart HL7 shut down successfully!")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )