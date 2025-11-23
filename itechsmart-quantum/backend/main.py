"""
iTechSmart Quantum Computing Service

FastAPI application providing quantum computing capabilities.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from api.quantum import router as quantum_router
from core.quantum_config import QuantumConfig, get_quantum_config
from services.quantum_computing_service import get_quantum_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting iTechSmart Quantum Computing Service...")
    
    # Initialize quantum service
    try:
        quantum_service = get_quantum_service()
        backend_info = quantum_service.get_backend_info()
        print(f"✅ Quantum service initialized")
        print(f"   - Available backends: {backend_info['total_jobs']}")
        print(f"   - Qiskit available: {backend_info['qiskit_available']}")
        
        app.state.quantum_service = quantum_service
        app.state.config = get_quantum_config()
        
    except Exception as e:
        print(f"❌ Failed to initialize quantum service: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🛑 Shutting down iTechSmart Quantum Computing Service...")


# Create FastAPI application
app = FastAPI(
    title="iTechSmart Quantum Computing",
    description="Advanced quantum computing capabilities for optimization, simulation, and computational tasks",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(quantum_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "iTechSmart Quantum Computing",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "quantum": "/api/v1/quantum",
            "health": "/api/v1/quantum/health"
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check."""
    try:
        quantum_service = get_quantum_service()
        backend_info = quantum_service.get_backend_info()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "iTechSmart Quantum Computing",
            "qiskit_available": backend_info.get("qiskit_available", False),
            "available_backends": len([b for b in backend_info.get("available_backends", []) if b["available"]])
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get service metrics."""
    try:
        quantum_service = get_quantum_service()
        backend_info = quantum_service.get_backend_info()
        
        return {
            "metrics": {
                "total_jobs": backend_info.get("total_jobs", 0),
                "active_jobs": backend_info.get("active_jobs", 0),
                "available_backends": len([b for b in backend_info.get("available_backends", []) if b["available"]]),
                "qiskit_available": backend_info.get("qiskit_available", False),
                "service_uptime": "unknown"  # Would calculate from startup time
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8042,
        reload=True,
        log_level="info"
    )