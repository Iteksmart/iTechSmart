"""
iTechSmart HL7 Main Application
FastAPI application with EMR integrations
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from .api.routes import api_router
from .api.auth import auth_router
from .api.websocket import ws_router, ws_status_router
from .api.rate_limiter import rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    logger.info("Starting iTechSmart HL7 application...")

    # Start rate limiter cleanup task
    import asyncio

    cleanup_task = asyncio.create_task(rate_limiter.start_cleanup_task())

    logger.info("iTechSmart HL7 application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down iTechSmart HL7 application...")
    cleanup_task.cancel()
    logger.info("iTechSmart HL7 application shut down successfully")


# Create FastAPI application
app = FastAPI(
    title="iTechSmart HL7",
    description="Healthcare Integration Platform with EMR connectivity and HL7 messaging",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
        },
    )


# Include routers
app.include_router(auth_router)
app.include_router(api_router)
app.include_router(ws_router)
app.include_router(ws_status_router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "name": "iTechSmart HL7",
        "version": "1.0.0",
        "description": "Healthcare Integration Platform",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "api": "/api/v1",
            "auth": "/api/v1/auth",
            "websocket": "/ws",
        },
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
