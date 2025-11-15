"""
API Layer
REST API and WebSocket endpoints for iTechSmart HL7
"""

from .routes import api_router
from .websocket import websocket_manager

__all__ = ['api_router', 'websocket_manager']