"""
iTechSmart Supreme Plus - Devices API
Workstation and network device management endpoints

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models import InfrastructureNode, Remediation
from engine import SupremePlusEngine
from config import (
    WORKSTATION_ACTIONS,
    SERVER_ACTIONS,
    NETWORK_DEVICE_TYPES,
    NETWORK_COMMANDS,
)

router = APIRouter()


# Pydantic models
class WorkstationRemediationCreate(BaseModel):
    node_id: int
    action_type: str
    parameters: Optional[dict] = None


class NetworkDeviceCommandCreate(BaseModel):
    node_id: int
    command: str
    device_type: str = "cisco"


class ServerDiagnosticsRequest(BaseModel):
    node_id: int


@router.get("/workstation-actions")
async def list_workstation_actions():
    """List available workstation remediation actions"""
    return {
        "actions": [
            {
                "action_type": key,
                "name": action["name"],
                "description": action["description"],
            }
            for key, action in WORKSTATION_ACTIONS.items()
        ]
    }


@router.post("/workstation/remediate")
async def execute_workstation_remediation(
    remediation: WorkstationRemediationCreate, db: Session = Depends(get_db)
):
    """Execute workstation-specific remediation"""
    engine = SupremePlusEngine(db)
    try:
        result = engine.execute_workstation_remediation(
            node_id=remediation.node_id,
            action_type=remediation.action_type,
            parameters=remediation.parameters,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/server-actions")
async def list_server_actions():
    """List available server diagnostic actions"""
    return {
        "actions": [
            {
                "action_type": key,
                "name": action["name"],
                "description": action["description"],
            }
            for key, action in SERVER_ACTIONS.items()
        ]
    }


@router.post("/server/diagnostics")
async def run_server_diagnostics(
    request: ServerDiagnosticsRequest, db: Session = Depends(get_db)
):
    """Run comprehensive server diagnostics"""
    engine = SupremePlusEngine(db)
    try:
        results = engine.run_server_diagnostics(request.node_id)
        return {
            "node_id": request.node_id,
            "diagnostics": results,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network-devices/types")
async def list_network_device_types():
    """List supported network device types"""
    return {
        "device_types": [
            {
                "type": key,
                "name": device["name"],
                "connection": device["connection"],
                "port": device["port"],
            }
            for key, device in NETWORK_DEVICE_TYPES.items()
        ]
    }


@router.get("/network-devices/commands/{device_type}")
async def list_network_device_commands(device_type: str):
    """List available commands for a network device type"""
    if device_type not in ["cisco", "juniper", "palo_alto"]:
        raise HTTPException(status_code=400, detail="Unsupported device type")

    commands = NETWORK_COMMANDS.get(device_type, {})
    return {"device_type": device_type, "commands": commands}


@router.post("/network-devices/execute")
async def execute_network_device_command(
    command: NetworkDeviceCommandCreate, db: Session = Depends(get_db)
):
    """Execute command on network device"""
    engine = SupremePlusEngine(db)

    # Get node
    node = (
        db.query(InfrastructureNode)
        .filter(InfrastructureNode.id == command.node_id)
        .first()
    )

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Create a simple template for the command
    template = {"commands": {command.device_type: command.command}}

    try:
        result = engine._execute_network_device_command(node, template, {})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/by-type")
async def get_device_stats(db: Session = Depends(get_db)):
    """Get statistics by device type"""
    from sqlalchemy import func

    stats = (
        db.query(InfrastructureNode.node_type, func.count(InfrastructureNode.id))
        .group_by(InfrastructureNode.node_type)
        .all()
    )

    return {
        "by_type": {node_type: count for node_type, count in stats},
        "total": sum(count for _, count in stats),
    }


@router.post("/bulk-remediate")
async def bulk_remediate(
    node_ids: List[int],
    action_type: str,
    parameters: Optional[dict] = None,
    db: Session = Depends(get_db),
):
    """Execute remediation on multiple devices"""
    engine = SupremePlusEngine(db)
    results = []

    for node_id in node_ids:
        try:
            node = (
                db.query(InfrastructureNode)
                .filter(InfrastructureNode.id == node_id)
                .first()
            )

            if not node:
                results.append(
                    {"node_id": node_id, "success": False, "error": "Node not found"}
                )
                continue

            # Determine remediation type based on node type
            if node.node_type == "workstation":
                result = engine.execute_workstation_remediation(
                    node_id=node_id, action_type=action_type, parameters=parameters
                )
            else:
                # Use standard remediation
                remediation = engine.create_remediation(
                    incident_id=None,
                    action_type=action_type,
                    target_node_id=node_id,
                    parameters=parameters,
                    auto_execute=True,
                )
                result = {"success": True, "remediation_id": remediation.id}

            results.append(
                {
                    "node_id": node_id,
                    "success": result.get("success", True),
                    "result": result,
                }
            )

        except Exception as e:
            results.append({"node_id": node_id, "success": False, "error": str(e)})

    return {
        "total": len(node_ids),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results,
    }
