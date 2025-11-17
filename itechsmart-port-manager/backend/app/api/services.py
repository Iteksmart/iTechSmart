"""
Service Management API Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys

sys.path.append("..")
from app.main import get_suite_communicator

router = APIRouter()


class ServiceRestartRequest(BaseModel):
    service_id: str


@router.get("/discover")
async def discover_services():
    """Discover all available services in the suite"""
    suite_communicator = get_suite_communicator()
    services = await suite_communicator.discover_services()

    return {"success": True, "services": services, "count": len(services)}


@router.get("/status")
async def get_all_service_status():
    """Get status of all services"""
    suite_communicator = get_suite_communicator()
    statuses = await suite_communicator.get_all_service_status()

    healthy = sum(1 for s in statuses if s["status"] == "healthy")
    unhealthy = len(statuses) - healthy

    return {
        "success": True,
        "statuses": statuses,
        "total": len(statuses),
        "healthy": healthy,
        "unhealthy": unhealthy,
    }


@router.get("/status/{service_id}")
async def get_service_status(service_id: str):
    """Get status of a specific service"""
    suite_communicator = get_suite_communicator()
    status = await suite_communicator.get_service_status(service_id)

    if status["status"] == "unknown":
        raise HTTPException(status_code=404, detail=status["message"])

    return {"success": True, "status": status}


@router.post("/restart")
async def restart_service(request: ServiceRestartRequest):
    """Request service restart"""
    suite_communicator = get_suite_communicator()
    result = await suite_communicator.restart_service(request.service_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {
        "success": True,
        "service_id": request.service_id,
        "message": result["message"],
    }


@router.get("/health/{service_id}")
async def check_service_health(service_id: str):
    """Check if a service is healthy"""
    suite_communicator = get_suite_communicator()
    port_manager = suite_communicator.port_manager

    port = await port_manager.get_service_port(service_id)
    if not port:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")

    is_healthy = await suite_communicator.check_service_health(service_id, port)

    return {
        "success": True,
        "service_id": service_id,
        "port": port,
        "healthy": is_healthy,
    }
