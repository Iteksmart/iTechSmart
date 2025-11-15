"""
iTechSmart Observatory - Main Application
Product #36: Application Performance Monitoring & Observability Platform

FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import API routers
from .api import metrics, traces, logs, alerts, services


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    print("🚀 iTechSmart Observatory starting up...")
    yield
    # Shutdown
    print("🛑 iTechSmart Observatory shutting down...")


# Create FastAPI application
app = FastAPI(
    title="iTechSmart Observatory",
    description="Application Performance Monitoring & Observability Platform",
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
app.include_router(metrics.router)
app.include_router(traces.router)
app.include_router(logs.router)
app.include_router(alerts.router)
app.include_router(services.router)


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "service": "iTechSmart Observatory",
        "version": "1.0.0",
        "status": "operational",
        "description": "Application Performance Monitoring & Observability Platform"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "observatory",
        "version": "1.0.0"
    }


@app.get("/api/observatory/dashboard/stats")
async def get_dashboard_stats():
    """
    Get dashboard statistics
    """
    # TODO: Implement dashboard stats
    return {
        "total_services": 0,
        "active_alerts": 0,
        "total_traces": 0,
        "error_rate": 0.0,
        "avg_response_time": 0.0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8036)