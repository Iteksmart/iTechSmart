"""
WebSocket API for Real-Time Updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Active WebSocket connections
active_connections: List[WebSocket] = []


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time port updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Port Manager updates"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            # Echo back for now (can be extended for commands)
            await websocket.send_json({
                "type": "echo",
                "data": data
            })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_port_change(service_id: str, old_port: int, new_port: int):
    """Broadcast port change to all connected clients"""
    message = {
        "type": "port_change",
        "service_id": service_id,
        "old_port": old_port,
        "new_port": new_port,
        "timestamp": asyncio.get_event_loop().time()
    }
    await manager.broadcast(message)


async def broadcast_conflict_detected(conflicts: list):
    """Broadcast conflict detection to all connected clients"""
    message = {
        "type": "conflicts_detected",
        "conflicts": conflicts,
        "count": len(conflicts),
        "timestamp": asyncio.get_event_loop().time()
    }
    await manager.broadcast(message)


async def broadcast_service_status(service_id: str, status: str):
    """Broadcast service status change to all connected clients"""
    message = {
        "type": "service_status",
        "service_id": service_id,
        "status": status,
        "timestamp": asyncio.get_event_loop().time()
    }
    await manager.broadcast(message)