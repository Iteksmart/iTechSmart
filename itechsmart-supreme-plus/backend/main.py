"""
iTechSmart Supreme Plus - AI-Powered Infrastructure Auto-Remediation Platform
Main FastAPI Application Entry Point

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from database import engine, Base
from api import incidents, remediations, integrations, monitoring, devices

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting iTechSmart Supreme Plus...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down iTechSmart Supreme Plus...")


app = FastAPI(
    title="iTechSmart Supreme Plus",
    description="AI-Powered Infrastructure Auto-Remediation Platform - Enhanced with Workstation, Server & Network Device Support",
    version="1.1.0",
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

# Include routers
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(
    remediations.router, prefix="/api/remediations", tags=["Remediations"]
)
app.include_router(
    integrations.router, prefix="/api/integrations", tags=["Integrations"]
)
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "iTechSmart Supreme Plus",
        "version": "1.1.0",
        "description": "AI-Powered Infrastructure Auto-Remediation Platform",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "launch_date": "2025-08-08",
        "capabilities": [
            "AI-Powered Incident Analysis",
            "Automated Remediation",
            "Workstation Support (Windows/Linux)",
            "Server Management and Diagnostics",
            "Network Device Support (Cisco/Juniper/Palo Alto/F5)",
            "SSH/PowerShell/WinRM Execution",
            "Real-time Monitoring",
            "Integration Management",
        ],
        "supported_devices": [
            "Linux Servers",
            "Windows Servers",
            "Windows Workstations",
            "Linux Workstations",
            "Cisco IOS/NX-OS",
            "Juniper JunOS",
            "Palo Alto Firewalls",
            "F5 BIG-IP",
            "Arista EOS",
            "HP ProCurve",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "supreme-plus",
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    from sqlalchemy.orm import Session
    from database import SessionLocal
    from models import Incident, Remediation, Integration

    db = SessionLocal()
    try:
        total_incidents = db.query(Incident).count()
        active_incidents = db.query(Incident).filter(Incident.status == "open").count()
        total_remediations = db.query(Remediation).count()
        successful_remediations = (
            db.query(Remediation).filter(Remediation.status == "success").count()
        )
        active_integrations = (
            db.query(Integration).filter(Integration.enabled == True).count()
        )

        success_rate = (
            (successful_remediations / total_remediations * 100)
            if total_remediations > 0
            else 0
        )

        return {
            "incidents": {
                "total": total_incidents,
                "active": active_incidents,
                "resolved": total_incidents - active_incidents,
            },
            "remediations": {
                "total": total_remediations,
                "successful": successful_remediations,
                "failed": total_remediations - successful_remediations,
                "success_rate": round(success_rate, 2),
            },
            "integrations": {"active": active_integrations},
            "timestamp": datetime.utcnow().isoformat(),
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8034)
