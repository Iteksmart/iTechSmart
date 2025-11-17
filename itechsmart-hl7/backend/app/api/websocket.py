"""
WebSocket Manager
Real-time communication for HL7 messages and EMR events
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts
    """

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(
        self, websocket: WebSocket, client_id: str, channel: str = "default"
    ):
        """
        Connect a new WebSocket client
        """
        await websocket.accept()

        if channel not in self.active_connections:
            self.active_connections[channel] = set()

        self.active_connections[channel].add(websocket)
        self.user_connections[client_id] = websocket

        logger.info(f"Client {client_id} connected to channel {channel}")

        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "channel": channel,
                "timestamp": datetime.now().isoformat(),
            },
            websocket,
        )

    def disconnect(
        self, websocket: WebSocket, client_id: str, channel: str = "default"
    ):
        """
        Disconnect a WebSocket client
        """
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

            if not self.active_connections[channel]:
                del self.active_connections[channel]

        if client_id in self.user_connections:
            del self.user_connections[client_id]

        logger.info(f"Client {client_id} disconnected from channel {channel}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to specific client
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict, channel: str = "default"):
        """
        Broadcast message to all clients in channel
        """
        if channel not in self.active_connections:
            return

        disconnected = set()

        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections[channel].discard(connection)

    async def broadcast_to_user(self, message: dict, client_id: str):
        """
        Send message to specific user
        """
        if client_id in self.user_connections:
            await self.send_personal_message(message, self.user_connections[client_id])

    def get_connection_count(self, channel: str = None) -> int:
        """
        Get number of active connections
        """
        if channel:
            return len(self.active_connections.get(channel, set()))
        return sum(len(conns) for conns in self.active_connections.values())

    def get_channels(self) -> List[str]:
        """
        Get list of active channels
        """
        return list(self.active_connections.keys())


# Global WebSocket manager
websocket_manager = ConnectionManager()


class HL7EventBroadcaster:
    """
    Broadcasts HL7 events to WebSocket clients
    """

    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def broadcast_hl7_message(
        self, message_type: str, message_data: dict, channel: str = "hl7"
    ):
        """
        Broadcast HL7 message event
        """
        event = {
            "type": "hl7_message",
            "message_type": message_type,
            "data": message_data,
            "timestamp": datetime.now().isoformat(),
        }

        await self.manager.broadcast(event, channel)

    async def broadcast_patient_update(
        self, patient_id: str, update_type: str, data: dict, channel: str = "patients"
    ):
        """
        Broadcast patient update event
        """
        event = {
            "type": "patient_update",
            "patient_id": patient_id,
            "update_type": update_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

        await self.manager.broadcast(event, channel)

    async def broadcast_connection_status(
        self, connection_id: str, status: str, channel: str = "connections"
    ):
        """
        Broadcast EMR connection status change
        """
        event = {
            "type": "connection_status",
            "connection_id": connection_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }

        await self.manager.broadcast(event, channel)

    async def broadcast_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "info",
        channel: str = "alerts",
    ):
        """
        Broadcast system alert
        """
        event = {
            "type": "alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
        }

        await self.manager.broadcast(event, channel)

    async def broadcast_observation(
        self, patient_id: str, observation: dict, channel: str = "observations"
    ):
        """
        Broadcast new observation
        """
        event = {
            "type": "new_observation",
            "patient_id": patient_id,
            "observation": observation,
            "timestamp": datetime.now().isoformat(),
        }

        await self.manager.broadcast(event, channel)

    async def broadcast_medication(
        self, patient_id: str, medication: dict, channel: str = "medications"
    ):
        """
        Broadcast medication event
        """
        event = {
            "type": "medication_event",
            "patient_id": patient_id,
            "medication": medication,
            "timestamp": datetime.now().isoformat(),
        }

        await self.manager.broadcast(event, channel)


# Global event broadcaster
event_broadcaster = HL7EventBroadcaster(websocket_manager)


# WebSocket endpoint handler
async def websocket_endpoint(
    websocket: WebSocket, client_id: str, channel: str = "default"
):
    """
    WebSocket endpoint handler
    """
    await websocket_manager.connect(websocket, client_id, channel)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle different message types
                message_type = message.get("type")

                if message_type == "ping":
                    # Respond to ping
                    await websocket_manager.send_personal_message(
                        {"type": "pong", "timestamp": datetime.now().isoformat()},
                        websocket,
                    )

                elif message_type == "subscribe":
                    # Subscribe to channel
                    new_channel = message.get("channel")
                    if new_channel:
                        await websocket_manager.connect(
                            websocket, client_id, new_channel
                        )

                elif message_type == "unsubscribe":
                    # Unsubscribe from channel
                    old_channel = message.get("channel")
                    if old_channel:
                        websocket_manager.disconnect(websocket, client_id, old_channel)

                elif message_type == "broadcast":
                    # Broadcast message to channel
                    broadcast_channel = message.get("channel", channel)
                    broadcast_data = message.get("data", {})

                    await websocket_manager.broadcast(
                        {
                            "type": "broadcast",
                            "from": client_id,
                            "data": broadcast_data,
                            "timestamp": datetime.now().isoformat(),
                        },
                        broadcast_channel,
                    )

                else:
                    # Echo unknown messages
                    await websocket_manager.send_personal_message(
                        {
                            "type": "echo",
                            "original": message,
                            "timestamp": datetime.now().isoformat(),
                        },
                        websocket,
                    )

            except json.JSONDecodeError:
                await websocket_manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON",
                        "timestamp": datetime.now().isoformat(),
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, client_id, channel)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket, client_id, channel)


# WebSocket routes
from fastapi import APIRouter

ws_router = APIRouter()


@ws_router.websocket("/ws/{client_id}")
async def websocket_default(websocket: WebSocket, client_id: str):
    """
    Default WebSocket endpoint
    """
    await websocket_endpoint(websocket, client_id, "default")


@ws_router.websocket("/ws/{client_id}/{channel}")
async def websocket_channel(websocket: WebSocket, client_id: str, channel: str):
    """
    Channel-specific WebSocket endpoint
    """
    await websocket_endpoint(websocket, client_id, channel)


# WebSocket status endpoint
from fastapi import APIRouter as HTTPRouter

ws_status_router = HTTPRouter(prefix="/api/v1/websocket", tags=["websocket"])


@ws_status_router.get("/status")
async def get_websocket_status():
    """
    Get WebSocket connection status
    """
    return {
        "total_connections": websocket_manager.get_connection_count(),
        "channels": websocket_manager.get_channels(),
        "connections_by_channel": {
            channel: websocket_manager.get_connection_count(channel)
            for channel in websocket_manager.get_channels()
        },
        "timestamp": datetime.now().isoformat(),
    }
