"""
iTechSmart Sandbox - Main Entry Point
Secure Code Execution Environment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.database import init_db
from app.api import sandboxes, snapshots, tests, templates

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
    logger.info("Starting iTechSmart Sandbox...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down iTechSmart Sandbox...")


# Create FastAPI app
app = FastAPI(
    title="iTechSmart Sandbox",
    description="Secure Code Execution Environment - Part of iTechSmart Suite (Internal Use)",
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
app.include_router(sandboxes.router)
app.include_router(snapshots.router)
app.include_router(tests.router)
app.include_router(templates.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "iTechSmart Sandbox",
        "version": "1.0.0",
        "description": "Secure Code Execution Environment",
        "status": "operational",
        "suite": "iTechSmart Suite",
        "internal_use": True,
        "launch_date": "August 8, 2025",
        "features": [
            "Ultra-fast boot times (1-3 seconds)",
            "Docker container isolation",
            "GPU support (A10G, T4, V100, A100)",
            "Persistent storage volumes",
            "Port exposure with preview URLs",
            "Filesystem snapshots",
            "Resource monitoring",
            "Auto-termination",
            "Test execution for all 32 products",
            "Custom client software testing"
        ],
        "endpoints": {
            "sandboxes": "/api/sandboxes",
            "snapshots": "/api/snapshots",
            "tests": "/api/tests",
            "templates": "/api/templates",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iTechSmart Sandbox",
        "version": "1.0.0",
        "launch_date": "August 8, 2025"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8033)