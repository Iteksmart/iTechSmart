"""
iTechSmart Citadel - Main Application
Sovereign Digital Infrastructure Platform

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from database import engine, Base
from api import security, compliance, threats, monitoring, system_agents

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
    logger.info("Starting iTechSmart Citadel...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down iTechSmart Citadel...")

app = FastAPI(
    title="iTechSmart Citadel",
    description="Sovereign Digital Infrastructure Platform",
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
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(threats.router, prefix="/api/threats", tags=["Threats"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(system_agents.router, prefix="/api/v1/system-agents", tags=["System Agents"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "iTechSmart Citadel",
        "version": "1.0.0",
        "description": "Sovereign Digital Infrastructure Platform",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "launch_date": "2025-08-08",
        "features": [
            "Post-Quantum Cryptography",
            "Immutable OS",
            "SIEM/XDR",
            "Zero Trust Architecture",
            "Compliance Management",
            "Threat Intelligence"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "citadel"
    }

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    from sqlalchemy.orm import Session
    from database import SessionLocal
    from models import SecurityEvent, ThreatIntelligence, CompliancePolicy, Vulnerability
    
    db = SessionLocal()
    try:
        total_events = db.query(SecurityEvent).count()
        open_events = db.query(SecurityEvent).filter(SecurityEvent.status == "open").count()
        threat_indicators = db.query(ThreatIntelligence).filter(ThreatIntelligence.is_active == True).count()
        compliance_policies = db.query(CompliancePolicy).filter(CompliancePolicy.enabled == True).count()
        vulnerabilities = db.query(Vulnerability).filter(Vulnerability.status == "open").count()
        
        return {
            "security_events": {
                "total": total_events,
                "open": open_events,
                "resolved": total_events - open_events
            },
            "threat_intelligence": {
                "active_indicators": threat_indicators
            },
            "compliance": {
                "active_policies": compliance_policies
            },
            "vulnerabilities": {
                "open": vulnerabilities
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8035)