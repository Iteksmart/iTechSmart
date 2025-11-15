"""
iTechSmart Supreme - Healthcare Management System
FastAPI Backend Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.database import init_db
from app.api import patients, appointments, billing, dashboard

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
    logger.info("Starting iTechSmart Supreme...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down iTechSmart Supreme...")


# Create FastAPI app
app = FastAPI(
    title="iTechSmart Supreme",
    description="Healthcare Management System - Part of iTechSmart Suite",
    version="1.0.0",
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

# Include routers
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(billing.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "iTechSmart Supreme",
        "version": "1.0.0",
        "description": "Healthcare Management System",
        "status": "operational",
        "suite": "iTechSmart Suite",
        "endpoints": {
            "patients": "/api/patients",
            "appointments": "/api/appointments",
            "billing": "/api/billing",
            "dashboard": "/api/dashboard",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iTechSmart Supreme",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)