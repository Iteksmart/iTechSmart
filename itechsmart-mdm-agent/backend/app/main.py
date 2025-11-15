"""
iTechSmart MDM Deployment Agent - Main Application

Intelligent deployment orchestrator for the iTechSmart Suite with AI-powered
optimization, automated configuration, and continuous monitoring.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import deployment, configuration, monitoring, ai
from app.core.database import init_db
from app.integrations.hub_integration import HubIntegration
from app.integrations.ninja_integration import NinjaIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global integration instances
hub_integration: HubIntegration = None
ninja_integration: NinjaIntegration = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting iTechSmart MDM Deployment Agent...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Initialize integrations
    global hub_integration, ninja_integration
    
    try:
        hub_integration = HubIntegration(
            hub_url="http://localhost:8001",
            service_name="itechsmart-mdm-agent",
            service_port=8200
        )
        await hub_integration.start()
        logger.info("Hub integration started")
    except Exception as e:
        logger.error(f"Failed to start Hub integration: {e}")
    
    try:
        ninja_integration = NinjaIntegration(
            ninja_url="http://localhost:8002",
            service_name="itechsmart-mdm-agent"
        )
        await ninja_integration.start()
        logger.info("Ninja integration started")
    except Exception as e:
        logger.error(f"Failed to start Ninja integration: {e}")
    
    logger.info("iTechSmart MDM Deployment Agent started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down iTechSmart MDM Deployment Agent...")
    
    if hub_integration:
        await hub_integration.stop()
        logger.info("Hub integration stopped")
    
    if ninja_integration:
        await ninja_integration.stop()
        logger.info("Ninja integration stopped")
    
    logger.info("iTechSmart MDM Deployment Agent stopped")


# Create FastAPI application
app = FastAPI(
    title="iTechSmart MDM Deployment Agent",
    description="Intelligent deployment orchestrator for the iTechSmart Suite with AI-powered optimization",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(deployment.router)
app.include_router(configuration.router)
app.include_router(monitoring.router)
app.include_router(ai.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "iTechSmart MDM Deployment Agent",
        "version": "1.0.0",
        "status": "running",
        "description": "Intelligent deployment orchestrator for the iTechSmart Suite",
        "capabilities": [
            "Product deployment",
            "Suite deployment",
            "Configuration management",
            "Health monitoring",
            "AI optimization",
            "Auto-healing"
        ],
        "endpoints": {
            "deployment": "/api/deploy",
            "configuration": "/api/config",
            "monitoring": "/api/monitor",
            "ai": "/api/ai",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "itechsmart-mdm-agent",
        "version": "1.0.0",
        "integrations": {
            "hub": hub_integration.registered if hub_integration else False,
            "ninja": ninja_integration.running if ninja_integration else False
        }
    }


@app.get("/info")
async def get_info():
    """Get service information"""
    return {
        "service_name": "iTechSmart MDM Deployment Agent",
        "version": "1.0.0",
        "description": "Intelligent deployment orchestrator for the iTechSmart Suite",
        "features": [
            "Individual product deployment",
            "Full suite deployment (27 products)",
            "AI-powered resource optimization",
            "Automated configuration management",
            "Continuous health monitoring",
            "Self-healing integration",
            "Multi-strategy deployment (Docker Compose, Kubernetes, Manual)",
            "Multi-environment support (Dev, Staging, Production)",
            "Zero-downtime updates",
            "Automatic rollback",
            "Deployment analytics"
        ],
        "supported_products": 27,
        "deployment_strategies": ["docker_compose", "kubernetes", "manual"],
        "environments": ["development", "staging", "production"],
        "ai_capabilities": [
            "Resource optimization",
            "Deployment strategy recommendation",
            "Configuration tuning",
            "Error prediction",
            "Performance optimization",
            "Pattern analysis"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
