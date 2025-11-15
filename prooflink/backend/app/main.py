"""
iTechSmart ProofLink - Main Application
The World's Trust Layer
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
import logging
from typing import Dict, Any

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import api_router
from app.core.exceptions import ProofLinkException

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting ProofLink.AI - The World's Trust Layer")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug Mode: {settings.APP_DEBUG}")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database tables created")
    logger.info("✅ ProofLink.AI is ready!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down ProofLink.AI")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="The World's Trust Layer - Verify anything digital in seconds",
    version="1.0.0",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan,
    openapi_tags=[
        {"name": "auth", "description": "Authentication operations"},
        {"name": "proofs", "description": "Proof creation and verification"},
        {"name": "users", "description": "User management"},
        {"name": "integrations", "description": "Third-party integrations"},
        {"name": "payments", "description": "Subscription and payments"},
        {"name": "mcp", "description": "MCP server operations"},
        {"name": "ai", "description": "AI verification services"},
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(ProofLinkException)
async def prooflink_exception_handler(request: Request, exc: ProofLinkException):
    """Handle ProofLink custom exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.APP_DEBUG else None
        }
    )


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ProofLink.AI",
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }


# Root endpoint
@app.get("/", tags=["system"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "service": "ProofLink.AI",
        "tagline": "The World's Trust Layer",
        "description": "Verify anything digital in seconds - no blockchain, no nonsense",
        "version": "1.0.0",
        "docs": f"{settings.API_URL}/docs",
        "status": "operational"
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )