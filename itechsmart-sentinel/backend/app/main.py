"""
iTechSmart Sentinel - Main Application
Real-Time Observability & Incident Management Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.database import init_db
from app.api import tracing, alerts, logs, incidents, slo


# Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for application startup and shutdown
    """
    # Startup
    print("🚀 Starting iTechSmart Sentinel...")

    # Initialize database
    init_db()
    print("✅ Database initialized")

    # Initialize integrations
    try:
        from app.integrations.hub_integration import hub_client
        from app.integrations.ninja_integration import ninja_client

        await hub_client.initialize()
        await ninja_client.initialize()
        print("✅ Suite integrations initialized")
    except Exception as e:
        print(f"⚠️  Suite integrations not available: {e}")

    print("✅ iTechSmart Sentinel is ready!")

    yield

    # Shutdown
    print("🛑 Shutting down iTechSmart Sentinel...")

    try:
        from app.integrations.hub_integration import hub_client
        from app.integrations.ninja_integration import ninja_client

        await hub_client.shutdown()
        await ninja_client.shutdown()
        print("✅ Suite integrations shut down")
    except Exception as e:
        print(f"⚠️  Error during shutdown: {e}")

    print("👋 iTechSmart Sentinel stopped")


# Create FastAPI app
app = FastAPI(
    title="iTechSmart Sentinel",
    description="""
    **Real-Time Observability & Incident Management Platform**
    
    iTechSmart Sentinel provides comprehensive observability across your entire infrastructure:
    
    - 🔍 **Distributed Tracing**: Track requests across all services with OpenTelemetry support
    - 🚨 **Smart Alerting**: ML-based alert fatigue reduction and intelligent routing
    - 📊 **Log Aggregation**: Centralized logs with natural language search and anomaly detection
    - 🎯 **Incident Management**: Automated incident creation, runbooks, and post-mortems
    - 📈 **SLO Tracking**: Service Level Objectives with error budgets and burn rate alerts
    
    **Part of the iTechSmart Suite** - Fully integrated with all 30+ products
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tracing.router)
app.include_router(alerts.router)
app.include_router(logs.router)
app.include_router(incidents.router)
app.include_router(slo.router)


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "iTechSmart Sentinel",
        "version": "1.0.0",
        "description": "Real-Time Observability & Incident Management Platform",
        "status": "operational",
        "suite": "iTechSmart Suite",
        "product_number": 31,
        "capabilities": [
            "Distributed Tracing",
            "Smart Alerting",
            "Log Aggregation",
            "Incident Management",
            "SLO Tracking",
        ],
        "endpoints": {
            "tracing": "/api/tracing",
            "alerts": "/api/alerts",
            "logs": "/api/logs",
            "incidents": "/api/incidents",
            "slo": "/api/slo",
            "docs": "/docs",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "iTechSmart Sentinel", "version": "1.0.0"}


@app.get("/suite-info")
async def suite_info():
    """iTechSmart Suite integration information"""
    try:
        from app.integrations.hub_integration import hub_client
        from app.integrations.ninja_integration import ninja_client

        return {
            "suite_member": True,
            "product_name": "iTechSmart Sentinel",
            "product_number": 31,
            "hub_connected": hub_client.is_connected,
            "ninja_connected": ninja_client.is_connected,
            "capabilities": [
                "Distributed Tracing",
                "Smart Alerting",
                "Log Aggregation",
                "Incident Management",
                "SLO Tracking",
            ],
        }
    except Exception as e:
        return {
            "suite_member": True,
            "product_name": "iTechSmart Sentinel",
            "product_number": 31,
            "hub_connected": False,
            "ninja_connected": False,
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8310"))

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
