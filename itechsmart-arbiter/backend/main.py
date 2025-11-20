from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import logging
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

from app.core.config import settings
from app.core.security import get_current_user
from app.api.v1.api import api_router
from app.core.logging import setup_logging
from app.services.arbiter_engine import ArbiterEngine
from app.services.simulation_engine import SimulationEngine
from app.services.notification_service import NotificationService
from app.models.schemas import (
    ActionRequest,
    ActionResponse,
    SimulationRequest,
    SimulationResponse,
    ConstitutionUpdate,
    EmergencyStopRequest
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="iTechSmart Arbiter",
    description="AI Governance & Safety Layer",
    version="1.6.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
arbiter_engine = ArbiterEngine()
simulation_engine = SimulationEngine()
notification_service = NotificationService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🛡️ iTechSmart Arbiter starting up...")
    await arbiter_engine.initialize()
    await simulation_engine.initialize()
    await notification_service.initialize()
    logger.info("✅ iTechSmart Arbiter ready for governance operations")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 iTechSmart Arbiter shutting down...")
    await arbiter_engine.cleanup()
    await simulation_engine.cleanup()
    logger.info("👋 iTechSmart Arbiter shutdown complete")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "iTechSmart Arbiter",
        "version": "1.6.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "description": "AI Governance & Safety Layer"
    }

@app.get("/api/v1/status")
async def get_status():
    """Get system status"""
    return {
        "status": "healthy",
        "arbiter_engine": await arbiter_engine.health_check(),
        "simulation_engine": await simulation_engine.health_check(),
        "notification_service": await notification_service.health_check(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/evaluate", response_model=ActionResponse)
async def evaluate_action(
    request: ActionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Evaluate an AI action request for safety and compliance
    
    This is the core endpoint that all AI agents must call before executing
    any action on infrastructure.
    """
    try:
        logger.info(f"🔍 Evaluating action from agent {request.agent_id} on {request.target_system}")
        
        # Evaluate the action through Arbiter engine
        result = await arbiter_engine.evaluate_request(
            agent_id=request.agent_id,
            command=request.command,
            target_system=request.target_system,
            context=request.context or {}
        )
        
        # If high-risk and requires approval, send notification
        if result["status"] == "PENDING_APPROVAL":
            background_tasks.add_task(
                notification_service.send_approval_request,
                request.agent_id,
                request.command,
                result["approval_id"]
            )
        
        # Log the decision
        await arbiter_engine.log_decision(request, result)
        
        logger.info(f"✅ Action evaluation complete: {result['status']}")
        return ActionResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Error evaluating action: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.post("/api/v1/simulate", response_model=SimulationResponse)
async def simulate_action(
    request: SimulationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Run a simulation of the proposed action
    """
    try:
        logger.info(f"🎮 Running simulation for: {request.command}")
        
        result = await simulation_engine.run_simulation(
            command=request.command,
            target_system=request.target_system,
            context=request.context or {}
        )
        
        logger.info(f"✅ Simulation complete: {result['status']}")
        return SimulationResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Error running simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@app.get("/api/v1/constitution")
async def get_constitution():
    """Get current constitution/policies"""
    try:
        return await arbiter_engine.get_constitution()
    except Exception as e:
        logger.error(f"❌ Error getting constitution: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve constitution")

@app.put("/api/v1/constitution")
async def update_constitution(
    update: ConstitutionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update constitution/policies"""
    try:
        logger.info(f"📝 Updating constitution by user {current_user.get('sub')}")
        
        result = await arbiter_engine.update_constitution(
            policies=update.policies,
            updated_by=current_user.get('sub')
        )
        
        logger.info("✅ Constitution updated successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error updating constitution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Constitution update failed: {str(e)}")

@app.post("/api/v1/emergency-stop")
async def emergency_stop(
    request: EmergencyStopRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Emergency stop - immediately revoke AI privileges
    """
    try:
        logger.warning(f"🚨 EMERGENCY STOP activated by {current_user.get('sub')}")
        
        result = await arbiter_engine.emergency_stop(
            reason=request.reason,
            initiated_by=current_user.get('sub')
        )
        
        # Send emergency notification
        await notification_service.send_emergency_alert(
            initiated_by=current_user.get('sub'),
            reason=request.reason
        )
        
        logger.warning("✅ Emergency stop activated successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error activating emergency stop: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Emergency stop failed: {str(e)}")

@app.get("/api/v1/metrics")
async def get_metrics():
    """Get risk metrics and statistics"""
    try:
        return await arbiter_engine.get_metrics()
    except Exception as e:
        logger.error(f"❌ Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@app.get("/api/v1/audit-log")
async def get_audit_log(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get governance audit log"""
    try:
        return await arbiter_engine.get_audit_log(limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"❌ Error getting audit log: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit log")

# Include API router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
        log_level="info"
    )