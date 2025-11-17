"""
iTechSmart QA/QC System - Main Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from datetime import datetime

from app.core.database import init_db, check_db_connection
from app.api import products, qa_checks, scans, documentation, alerts
from app.integrations.hub_integration import HubIntegration
from app.integrations.ninja_integration import NinjaIntegration
from app.core.qa_engine import QAEngine
from app.core.documentation_manager import DocumentationManager

# Global integration instances
hub_integration = None
ninja_integration = None
qa_engine = None
doc_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    global hub_integration, ninja_integration, qa_engine, doc_manager

    print("🚀 Starting iTechSmart QA/QC System...")

    # Initialize database
    init_db()

    # Check database connection
    if not check_db_connection():
        print("⚠️  Warning: Database connection failed")

    # Initialize core engines
    qa_engine = QAEngine()
    doc_manager = DocumentationManager()
    print("✅ Core engines initialized")

    # Initialize integrations
    try:
        hub_integration = HubIntegration()
        await hub_integration.start()
        print("✅ Enterprise Hub integration started")
    except Exception as e:
        print(f"⚠️  Warning: Hub integration failed: {e}")

    try:
        ninja_integration = NinjaIntegration()
        await ninja_integration.start()
        print("✅ Ninja integration started")
    except Exception as e:
        print(f"⚠️  Warning: Ninja integration failed: {e}")

    # Start continuous monitoring
    if qa_engine:
        await qa_engine.start_continuous_monitoring()
        print("✅ Continuous QA monitoring started")

    print("✅ iTechSmart QA/QC System is ready!")
    print(f"📊 API Documentation: http://localhost:8300/docs")
    print(f"🔍 Health Check: http://localhost:8300/health")

    yield

    # Shutdown
    print("🛑 Shutting down iTechSmart QA/QC System...")

    if qa_engine:
        await qa_engine.stop_continuous_monitoring()

    if hub_integration:
        await hub_integration.stop()

    if ninja_integration:
        await ninja_integration.stop()

    print("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="iTechSmart QA/QC System",
    description="Comprehensive Quality Assurance and Quality Control system for the iTechSmart Suite",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url),
        },
    )


# Include routers
app.include_router(products.router, prefix="/api/v1")
app.include_router(qa_checks.router, prefix="/api/v1")
app.include_router(scans.router, prefix="/api/v1")
app.include_router(documentation.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "iTechSmart QA/QC System",
        "version": "1.0.0",
        "status": "operational",
        "description": "Comprehensive Quality Assurance and Quality Control system for the iTechSmart Suite",
        "features": [
            "40+ automated QA checks across 10 categories",
            "15 checks with auto-fix capabilities",
            "Continuous monitoring (hourly per product)",
            "Documentation management and auto-generation",
            "Integration with Enterprise Hub and Ninja",
            "Real-time alerts and notifications",
            "Comprehensive reporting and analytics",
        ],
        "endpoints": {
            "api_docs": "/docs",
            "health": "/health",
            "products": "/api/v1/products",
            "qa_checks": "/api/v1/qa-checks",
            "scans": "/api/v1/scans",
            "documentation": "/api/v1/documentation",
            "alerts": "/api/v1/alerts",
        },
        "integrations": {
            "enterprise_hub": hub_integration is not None
            and hub_integration.is_connected,
            "ninja": ninja_integration is not None and ninja_integration.is_connected,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


# Health endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    db_healthy = check_db_connection()

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "iTechSmart QA/QC System",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "qa_engine": "healthy" if qa_engine else "unhealthy",
            "doc_manager": "healthy" if doc_manager else "unhealthy",
            "hub_integration": (
                "connected"
                if (hub_integration and hub_integration.is_connected)
                else "disconnected"
            ),
            "ninja_integration": (
                "connected"
                if (ninja_integration and ninja_integration.is_connected)
                else "disconnected"
            ),
        },
        "uptime_seconds": 0,  # TODO: Track actual uptime
    }


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring"""
    from app.core.database import get_db_context
    from app.models.models import Product, QACheck, QAResult, Alert, Documentation

    with get_db_context() as db:
        total_products = db.query(Product).count()
        active_products = db.query(Product).filter(Product.is_active == True).count()
        total_checks = db.query(QACheck).count()
        enabled_checks = db.query(QACheck).filter(QACheck.is_enabled == True).count()
        total_results = db.query(QAResult).count()
        open_alerts = db.query(Alert).filter(Alert.is_resolved == False).count()
        total_docs = db.query(Documentation).count()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "products": {"total": total_products, "active": active_products},
            "checks": {"total": total_checks, "enabled": enabled_checks},
            "results": {"total": total_results},
            "alerts": {"open": open_alerts},
            "documentation": {"total": total_docs},
        }


# Info endpoint
@app.get("/info")
async def info():
    """System information endpoint"""
    return {
        "service": "iTechSmart QA/QC System",
        "version": "1.0.0",
        "description": "Comprehensive Quality Assurance and Quality Control system",
        "port": 8300,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": os.getenv("DATABASE_URL", "sqlite:///./qaqc.db"),
        "features": {
            "qa_checks": {
                "total_categories": 10,
                "total_checks": "40+",
                "auto_fix_capable": 15,
            },
            "documentation": {
                "types": 9,
                "auto_generation": True,
                "freshness_monitoring": True,
            },
            "monitoring": {
                "continuous": True,
                "interval": "hourly",
                "real_time_alerts": True,
            },
            "integrations": {
                "enterprise_hub": True,
                "ninja": True,
                "port_manager": True,
            },
        },
        "api_version": "v1",
        "documentation_url": "/docs",
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8300))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
