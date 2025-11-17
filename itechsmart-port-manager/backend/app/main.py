"""
iTechSmart Port Manager - Main Application
Dynamic port configuration and management for the entire iTechSmart Suite
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from typing import Dict, List, Optional
import logging

from app.core.port_manager import PortManager
from app.core.suite_communicator import SuiteCommunicator
from app.integrations.integration import initialize_integration, shutdown_integration
from app.api import ports, services, health, websocket_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
port_manager: Optional[PortManager] = None
suite_communicator: Optional[SuiteCommunicator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global port_manager, suite_communicator

    # Startup
    logger.info("🚀 iTechSmart Port Manager starting up...")

    # Initialize port manager
    port_manager = PortManager()
    await port_manager.initialize()

    # Initialize suite communicator
    suite_communicator = SuiteCommunicator(port_manager)
    await suite_communicator.initialize()

    # Initialize iTechSmart Suite integration
    await initialize_integration()

    logger.info("✅ iTechSmart Port Manager ready!")

    yield

    # Shutdown
    logger.info("👋 iTechSmart Port Manager shutting down...")
    await shutdown_integration()
    await suite_communicator.shutdown()
    await port_manager.shutdown()


# Initialize FastAPI app
app = FastAPI(
    title="iTechSmart Port Manager",
    description="Dynamic Port Configuration and Management for iTechSmart Suite",
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

# Include routers
app.include_router(ports.router, prefix="/api/ports", tags=["Port Management"])
app.include_router(services.router, prefix="/api/services", tags=["Service Management"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(websocket_api.router, prefix="/ws", tags=["WebSocket"])


@app.get("/")
async def root():
    return {
        "message": "iTechSmart Port Manager",
        "version": "1.0.0",
        "description": "Dynamic Port Configuration and Management for iTechSmart Suite",
        "suite": "iTechSmart Suite Member",
        "features": [
            "Dynamic port allocation",
            "Port conflict detection",
            "Automatic port reassignment",
            "Real-time port monitoring",
            "Suite-wide port management",
            "Individual service configuration",
            "Port availability checking",
            "Configuration backup/restore",
            "WebSocket real-time updates",
            "Integration with Enterprise Hub",
            "Integration with Ninja",
        ],
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "iTechSmart Port Manager",
        "suite": "iTechSmart",
        "port_manager": "active" if port_manager else "inactive",
        "suite_communicator": "active" if suite_communicator else "inactive",
    }


def get_port_manager() -> PortManager:
    """Get the global port manager instance"""
    if port_manager is None:
        raise HTTPException(status_code=500, detail="Port Manager not initialized")
    return port_manager


def get_suite_communicator() -> SuiteCommunicator:
    """Get the global suite communicator instance"""
    if suite_communicator is None:
        raise HTTPException(
            status_code=500, detail="Suite Communicator not initialized"
        )
    return suite_communicator


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8100, reload=True)
