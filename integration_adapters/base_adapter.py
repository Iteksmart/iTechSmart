"""
Base adapter for iTechSmart service integration
All services implement this adapter to integrate with the suite
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseServiceAdapter(ABC):
    """
    Base adapter that all iTechSmart services must implement
    Provides standardized integration with Enterprise hub
    """

    def __init__(
        self, service_type: str, service_name: str, base_url: str, api_key: str
    ):
        self.service_type = service_type
        self.service_name = service_name
        self.base_url = base_url
        self.api_key = api_key

        # Hub connection
        self.hub_url = "http://localhost:8000"
        self.registered = False
        self.service_id = f"{service_type}:{service_name}"

        # Event subscriptions
        self.event_handlers: Dict[str, callable] = {}

    async def initialize(self):
        """Initialize the adapter and register with hub"""
        logger.info(f"🔌 Initializing adapter for {self.service_name}")

        # Register with hub
        await self.register_with_hub()

        # Subscribe to events
        await self.subscribe_to_events()

        # Start heartbeat
        asyncio.create_task(self._heartbeat_loop())

        logger.info(f"✅ Adapter initialized for {self.service_name}")

    async def register_with_hub(self):
        """Register this service with Enterprise hub"""

        try:
            capabilities = await self.get_capabilities()
            metadata = await self.get_metadata()

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hub_url}/api/integration/register",
                    json={
                        "service_type": self.service_type,
                        "service_name": self.service_name,
                        "base_url": self.base_url,
                        "api_key": self.api_key,
                        "capabilities": capabilities,
                        "metadata": metadata,
                    },
                ) as response:
                    result = await response.json()
                    self.registered = True
                    logger.info(f"✅ Registered with hub: {result}")

        except Exception as e:
            logger.error(f"Failed to register with hub: {e}")
            self.registered = False

    async def unregister_from_hub(self):
        """Unregister from hub on shutdown"""

        if not self.registered:
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.hub_url}/api/integration/unregister/{self.service_id}"
                ) as response:
                    logger.info("Unregistered from hub")
                    self.registered = False

        except Exception as e:
            logger.error(f"Failed to unregister: {e}")

    async def call_service(
        self,
        target_service: str,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Call another service through the hub"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hub_url}/api/integration/call",
                    json={
                        "service_id": target_service,
                        "endpoint": endpoint,
                        "method": method,
                        "data": data,
                    },
                    headers={"X-API-Key": self.api_key},
                ) as response:
                    return await response.json()

        except Exception as e:
            logger.error(f"Error calling service {target_service}: {e}")
            raise

    async def publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish an event to the hub"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hub_url}/api/integration/events/broadcast",
                    json={
                        "event_type": event_type,
                        "event_data": event_data,
                        "source_service": self.service_id,
                    },
                    headers={"X-API-Key": self.api_key},
                ) as response:
                    logger.info(f"Published event: {event_type}")

        except Exception as e:
            logger.error(f"Error publishing event: {e}")

    async def subscribe_to_events(self):
        """Subscribe to events from other services"""

        event_types = await self.get_event_subscriptions()

        if not event_types:
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hub_url}/api/integration/events/subscribe",
                    json={"service_id": self.service_id, "event_types": event_types},
                    headers={"X-API-Key": self.api_key},
                ) as response:
                    logger.info(f"Subscribed to events: {event_types}")

        except Exception as e:
            logger.error(f"Error subscribing to events: {e}")

    def register_event_handler(self, event_type: str, handler: callable):
        """Register a handler for a specific event type"""
        self.event_handlers[event_type] = handler

    async def handle_event(
        self, event_type: str, event_data: Dict[str, Any], source_service: str
    ):
        """Handle an incoming event"""

        handler = self.event_handlers.get(event_type)

        if handler:
            try:
                await handler(event_data, source_service)
            except Exception as e:
                logger.error(f"Error handling event {event_type}: {e}")
        else:
            logger.warning(f"No handler for event type: {event_type}")

    async def handle_ninja_command(
        self, command: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle a command from Ninja"""

        logger.info(f"🥷 Received Ninja command: {command}")

        if command == "fix":
            return await self.handle_fix_command(parameters)
        elif command == "update":
            return await self.handle_update_command(parameters)
        elif command == "optimize":
            return await self.handle_optimize_command(parameters)
        elif command == "restart":
            return await self.handle_restart_command(parameters)
        elif command == "diagnose":
            return await self.handle_diagnose_command(parameters)
        else:
            return {"success": False, "error": f"Unknown command: {command}"}

    async def _heartbeat_loop(self):
        """Send periodic heartbeat to hub"""

        while self.registered:
            try:
                # Update last heartbeat
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.hub_url}/api/integration/heartbeat",
                        json={"service_id": self.service_id},
                        headers={"X-API-Key": self.api_key},
                    ) as response:
                        pass

                await asyncio.sleep(30)  # Every 30 seconds

            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                await asyncio.sleep(30)

    # Abstract methods that each service must implement

    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """Return list of service capabilities"""
        pass

    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """Return service metadata"""
        pass

    @abstractmethod
    async def get_event_subscriptions(self) -> List[str]:
        """Return list of event types to subscribe to"""
        pass

    @abstractmethod
    async def handle_fix_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fix command from Ninja"""
        pass

    @abstractmethod
    async def handle_update_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update command from Ninja"""
        pass

    @abstractmethod
    async def handle_optimize_command(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle optimize command from Ninja"""
        pass

    @abstractmethod
    async def handle_restart_command(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle restart command from Ninja"""
        pass

    @abstractmethod
    async def handle_diagnose_command(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle diagnose command from Ninja"""
        pass

    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """Return current health status"""
        pass

    @abstractmethod
    async def get_service_info(self) -> Dict[str, Any]:
        """Return service information"""
        pass


class StandaloneMode:
    """
    Mixin for services that can run in standalone mode
    """

    def __init__(self):
        self.standalone_mode = False

    def enable_standalone_mode(self):
        """Enable standalone mode (no hub connection)"""
        self.standalone_mode = True
        logger.info("🔓 Standalone mode enabled")

    def disable_standalone_mode(self):
        """Disable standalone mode (connect to hub)"""
        self.standalone_mode = False
        logger.info("🔌 Standalone mode disabled - connecting to hub")

    async def initialize_standalone(self):
        """Initialize in standalone mode"""
        logger.info("🔓 Initializing in standalone mode")
        # Skip hub registration
        self.registered = False

    def is_standalone(self) -> bool:
        """Check if running in standalone mode"""
        return self.standalone_mode
