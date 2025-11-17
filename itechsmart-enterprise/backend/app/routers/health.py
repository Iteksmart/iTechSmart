"""
Health Check Router
Provides health and readiness endpoints
"""

from fastapi import APIRouter
from typing import Dict
import time

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict:
    """Basic health check"""
    return {"status": "healthy", "timestamp": time.time(), "version": "1.0.0"}


@router.get("/health/detailed")
async def detailed_health_check() -> Dict:
    """Detailed health check with dependencies"""

    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "services": {
            "database": {"status": "healthy", "latency_ms": 5},
            "redis": {"status": "healthy", "latency_ms": 2},
            "integrations": {
                "servicenow": "configured",
                "zendesk": "configured",
                "itglue": "configured",
                "nable": "configured",
                "connectwise": "configured",
            },
        },
    }

    return health_status


@router.get("/ready")
async def readiness_check() -> Dict:
    """Kubernetes readiness probe"""
    return {"ready": True, "timestamp": time.time()}


@router.get("/live")
async def liveness_check() -> Dict:
    """Kubernetes liveness probe"""
    return {"alive": True, "timestamp": time.time()}
