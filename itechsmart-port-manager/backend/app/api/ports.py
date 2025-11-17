"""
Port Management API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys

sys.path.append("..")
from app.main import get_port_manager, get_suite_communicator

router = APIRouter()


class PortAssignment(BaseModel):
    service_id: str
    port: Optional[int] = None
    force: bool = False


class PortReassignment(BaseModel):
    service_id: str
    new_port: Optional[int] = None


class BulkPortUpdate(BaseModel):
    updates: Dict[str, int]  # {service_id: new_port}


class PortReservation(BaseModel):
    port: int


@router.get("/assignments")
async def get_all_port_assignments():
    """Get all current port assignments"""
    port_manager = get_port_manager()
    assignments = await port_manager.get_all_assignments()
    return {"success": True, "assignments": assignments, "total": len(assignments)}


@router.get("/assignments/{service_id}")
async def get_service_port(service_id: str):
    """Get port assignment for a specific service"""
    port_manager = get_port_manager()
    port = await port_manager.get_service_port(service_id)

    if port is None:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")

    return {"success": True, "service_id": service_id, "port": port}


@router.post("/assign")
async def assign_port(assignment: PortAssignment):
    """Assign a port to a service"""
    port_manager = get_port_manager()
    success, port, message = await port_manager.assign_port(
        assignment.service_id, assignment.port, assignment.force
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "service_id": assignment.service_id,
        "port": port,
        "message": message,
    }


@router.post("/reassign")
async def reassign_port(reassignment: PortReassignment):
    """Reassign a service to a different port"""
    port_manager = get_port_manager()
    suite_communicator = get_suite_communicator()

    # Validate the change
    validation = await suite_communicator.validate_port_change(
        reassignment.service_id, reassignment.new_port
    )

    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["reason"])

    # Perform reassignment
    success, new_port, message = await port_manager.reassign_port(
        reassignment.service_id, reassignment.new_port
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Update the service
    update_result = await suite_communicator.update_service_port(
        reassignment.service_id, new_port
    )

    # Broadcast the change
    await suite_communicator.broadcast_port_change(
        reassignment.service_id, validation["current_port"], new_port
    )

    return {
        "success": True,
        "service_id": reassignment.service_id,
        "old_port": validation["current_port"],
        "new_port": new_port,
        "message": message,
        "update_result": update_result,
    }


@router.post("/bulk-update")
async def bulk_update_ports(bulk_update: BulkPortUpdate):
    """Update ports for multiple services"""
    suite_communicator = get_suite_communicator()

    results = await suite_communicator.update_multiple_services(bulk_update.updates)

    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    return {
        "success": True,
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "results": results,
    }


@router.get("/conflicts")
async def detect_conflicts():
    """Detect port conflicts"""
    port_manager = get_port_manager()
    conflicts = await port_manager.detect_conflicts()

    return {"success": True, "conflicts": conflicts, "count": len(conflicts)}


@router.post("/resolve-conflicts")
async def resolve_conflicts():
    """Automatically resolve detected conflicts"""
    port_manager = get_port_manager()
    resolutions = await port_manager.resolve_conflicts()

    return {"success": True, "resolutions": resolutions, "count": len(resolutions)}


@router.get("/available")
async def find_available_port(start_port: int = 8000):
    """Find an available port"""
    port_manager = get_port_manager()
    port = await port_manager.find_available_port(start_port)

    if port is None:
        raise HTTPException(status_code=404, detail="No available ports found")

    return {"success": True, "port": port}


@router.get("/history/{service_id}")
async def get_port_history(service_id: str):
    """Get port history for a service"""
    port_manager = get_port_manager()
    history = await port_manager.get_service_history(service_id)

    if not history:
        raise HTTPException(
            status_code=404, detail=f"No history found for {service_id}"
        )

    return {"success": True, "service_id": service_id, "history": history}


@router.post("/reserve")
async def reserve_port(reservation: PortReservation):
    """Reserve a port to prevent assignment"""
    port_manager = get_port_manager()
    success = await port_manager.reserve_port(reservation.port)

    if not success:
        raise HTTPException(
            status_code=400, detail=f"Port {reservation.port} already reserved"
        )

    return {
        "success": True,
        "port": reservation.port,
        "message": f"Port {reservation.port} reserved",
    }


@router.delete("/reserve/{port}")
async def unreserve_port(port: int):
    """Remove port reservation"""
    port_manager = get_port_manager()
    success = await port_manager.unreserve_port(port)

    if not success:
        raise HTTPException(status_code=404, detail=f"Port {port} not reserved")

    return {"success": True, "port": port, "message": f"Port {port} unreserved"}


@router.get("/statistics")
async def get_statistics():
    """Get port usage statistics"""
    port_manager = get_port_manager()
    stats = await port_manager.get_port_statistics()

    return {"success": True, "statistics": stats}


@router.post("/backup")
async def backup_configuration(backup_file: Optional[str] = None):
    """Create a backup of current configuration"""
    port_manager = get_port_manager()
    filename = await port_manager.backup_configuration(backup_file)

    return {
        "success": True,
        "backup_file": filename,
        "message": f"Configuration backed up to {filename}",
    }


@router.post("/restore")
async def restore_configuration(backup_file: str):
    """Restore configuration from backup"""
    port_manager = get_port_manager()
    success = await port_manager.restore_configuration(backup_file)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to restore configuration")

    return {"success": True, "message": f"Configuration restored from {backup_file}"}


@router.post("/reset")
async def reset_to_defaults():
    """Reset all port assignments to defaults"""
    port_manager = get_port_manager()
    success = await port_manager.reset_to_defaults()

    return {"success": True, "message": "Port assignments reset to defaults"}
