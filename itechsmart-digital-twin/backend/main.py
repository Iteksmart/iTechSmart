from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import json
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.logging import setup_logging
from app.services.simulation_engine import SimulationEngine
from app.services.environment_manager import EnvironmentManager
from app.services.prediction_service import PredictionService
from app.models.schemas import (
    SimulationRequest,
    SimulationResponse,
    PredictionRequest,
    EnvironmentSync,
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global services
simulation_engine = None
environment_manager = None
prediction_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("🎮 iTechSmart Digital Twin starting up...")
    global simulation_engine, environment_manager, prediction_service

    try:
        simulation_engine = SimulationEngine()
        environment_manager = EnvironmentManager()
        prediction_service = PredictionService()

        await simulation_engine.initialize()
        await environment_manager.initialize()
        await prediction_service.initialize()

        logger.info("✅ iTechSmart Digital Twin ready for simulation operations")
        yield

    except Exception as e:
        logger.error(f"❌ Failed to initialize Digital Twin: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("🔄 iTechSmart Digital Twin shutting down...")
        if simulation_engine:
            await simulation_engine.cleanup()
        if environment_manager:
            await environment_manager.cleanup()
        if prediction_service:
            await prediction_service.cleanup()
        logger.info("👋 iTechSmart Digital Twin shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="iTechSmart Digital Twin",
    description="Predictive Simulation Engine",
    version="1.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "iTechSmart Digital Twin",
        "version": "1.6.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "description": "Predictive Simulation Engine",
    }


@app.get("/api/v1/status")
async def get_status():
    """Get system status"""
    return {
        "status": "healthy",
        "simulation_engine": await simulation_engine.health_check(),
        "environment_manager": await environment_manager.health_check(),
        "prediction_service": await prediction_service.health_check(),
        "active_simulations": len(await simulation_engine.get_active_simulations()),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/v1/simulation/create", response_model=SimulationResponse)
async def create_simulation(request: SimulationRequest):
    """
    Create a new simulation environment
    """
    try:
        logger.info(f"🎮 Creating simulation for: {request.target_system}")

        simulation = await simulation_engine.create_simulation(
            change_type=request.change_type,
            target_system=request.target_system,
            changes=request.changes,
            duration_hours=request.duration_hours,
            context=request.context or {},
        )

        logger.info(f"✅ Simulation created: {simulation['id']}")
        return SimulationResponse(**simulation)

    except Exception as e:
        logger.error(f"❌ Error creating simulation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Simulation creation failed: {str(e)}"
        )


@app.post("/api/v1/simulation/run")
async def run_simulation(simulation_id: str):
    """
    Execute a simulation
    """
    try:
        logger.info(f"🚀 Running simulation: {simulation_id}")

        # Start simulation in background
        asyncio.create_task(run_simulation_background(simulation_id))

        return {
            "status": "started",
            "simulation_id": simulation_id,
            "message": "Simulation started successfully",
        }

    except Exception as e:
        logger.error(f"❌ Error starting simulation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start simulation: {str(e)}"
        )


async def run_simulation_background(simulation_id: str):
    """Run simulation in background and broadcast updates"""
    try:
        # Send initial update
        await manager.broadcast(
            json.dumps(
                {
                    "type": "simulation_update",
                    "simulation_id": simulation_id,
                    "status": "running",
                    "progress": 0,
                }
            )
        )

        # Run simulation with progress updates
        async for update in simulation_engine.run_simulation(simulation_id):
            await manager.broadcast(
                json.dumps(
                    {
                        "type": "simulation_update",
                        "simulation_id": simulation_id,
                        **update,
                    }
                )
            )

        # Send completion
        result = await simulation_engine.get_simulation_result(simulation_id)
        await manager.broadcast(
            json.dumps(
                {
                    "type": "simulation_complete",
                    "simulation_id": simulation_id,
                    "result": result,
                }
            )
        )

    except Exception as e:
        await manager.broadcast(
            json.dumps(
                {
                    "type": "simulation_error",
                    "simulation_id": simulation_id,
                    "error": str(e),
                }
            )
        )


@app.get("/api/v1/simulation/{simulation_id}")
async def get_simulation(simulation_id: str):
    """Get simulation details and results"""
    try:
        simulation = await simulation_engine.get_simulation(simulation_id)
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation not found")

        return simulation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting simulation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve simulation: {str(e)}"
        )


@app.delete("/api/v1/simulation/{simulation_id}")
async def delete_simulation(simulation_id: str):
    """Clean up simulation environment"""
    try:
        logger.info(f"🧹 Cleaning up simulation: {simulation_id}")

        await simulation_engine.cleanup_simulation(simulation_id)

        return {
            "status": "deleted",
            "simulation_id": simulation_id,
            "message": "Simulation cleaned up successfully",
        }

    except Exception as e:
        logger.error(f"❌ Error cleaning up simulation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to cleanup simulation: {str(e)}"
        )


@app.get("/api/v1/environments")
async def get_environments():
    """List available environments"""
    try:
        return await environment_manager.list_environments()
    except Exception as e:
        logger.error(f"❌ Error getting environments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve environments")


@app.post("/api/v1/environments/sync")
async def sync_environment(sync_request: EnvironmentSync):
    """Sync virtual environment with real system"""
    try:
        logger.info(f"🔄 Syncing environment: {sync_request.environment_id}")

        result = await environment_manager.sync_environment(
            environment_id=sync_request.environment_id,
            force=sync_request.force or False,
        )

        logger.info("✅ Environment sync complete")
        return result

    except Exception as e:
        logger.error(f"❌ Error syncing environment: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Environment sync failed: {str(e)}"
        )


@app.post("/api/v1/predict/impact")
async def predict_impact(request: PredictionRequest):
    """
    Predict the impact of proposed changes
    """
    try:
        logger.info(f"🔮 Predicting impact for: {request.target_system}")

        prediction = await prediction_service.predict_impact(
            target_system=request.target_system,
            changes=request.changes,
            context=request.context or {},
        )

        logger.info("✅ Impact prediction complete")
        return prediction

    except Exception as e:
        logger.error(f"❌ Error predicting impact: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Impact prediction failed: {str(e)}"
        )


@app.post("/api/v1/predict/performance")
async def predict_performance(request: PredictionRequest):
    """
    Predict performance changes
    """
    try:
        logger.info(f"📊 Predicting performance for: {request.target_system}")

        prediction = await prediction_service.predict_performance(
            target_system=request.target_system,
            changes=request.changes,
            context=request.context or {},
        )

        logger.info("✅ Performance prediction complete")
        return prediction

    except Exception as e:
        logger.error(f"❌ Error predicting performance: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Performance prediction failed: {str(e)}"
        )


@app.get("/api/v1/predict/failures")
async def predict_failures(target_system: str):
    """
    Predict potential failures
    """
    try:
        logger.info(f"⚠️ Predicting failures for: {target_system}")

        failures = await prediction_service.predict_failures(target_system)

        logger.info("✅ Failure prediction complete")
        return failures

    except Exception as e:
        logger.error(f"❌ Error predicting failures: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failure prediction failed: {str(e)}"
        )


@app.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time simulation updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Include API router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8090, reload=settings.DEBUG, log_level="info"
    )
