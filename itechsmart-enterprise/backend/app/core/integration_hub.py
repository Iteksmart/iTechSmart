"""
iTechSmart Enterprise Integration Hub
Central hub for all iTechSmart products to communicate and integrate
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pathlib import Path
import json
import aiohttp
from enum import Enum

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.integration import (
    RegisteredService,
    ServiceHealth,
    IntegrationEvent,
    CrossServiceCall,
    ServiceDependency,
)

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """iTechSmart product types"""

    ENTERPRISE = "itechsmart-enterprise"  # Hub
    NINJA = "itechsmart-ninja"  # Controller/Fixer
    SUPREME = "itechsmart-supreme"  # Self-healing infrastructure
    HL7 = "itechsmart-hl7"  # Healthcare integration
    IMPACTOS = "itechsmart-impactos"  # Impact measurement
    PASSPORT = "itechsmart-passport"  # Identity management
    PROOFLINK = "itechsmart-prooflink"  # Document verification


class IntegrationHub:
    """
    Central integration hub that:
    1. Registers all iTechSmart services
    2. Manages service discovery
    3. Routes requests between services
    4. Monitors service health
    5. Coordinates cross-service operations
    6. Enables Ninja to control/fix all services
    """

    def __init__(self, db: Session):
        self.db = db
        self.services: Dict[str, Dict[str, Any]] = {}
        self.event_subscribers: Dict[str, Set[str]] = {}
        self.health_check_interval = 30  # seconds

        # Hub configuration
        self.config = {
            "hub_url": "http://localhost:8000",
            "api_gateway_enabled": True,
            "event_bus_enabled": True,
            "auto_discovery": True,
            "health_monitoring": True,
            "ninja_control_enabled": True,
        }

    async def start_hub(self):
        """Start the integration hub"""
        logger.info("🌐 Starting iTechSmart Enterprise Integration Hub")

        # Start background tasks
        await asyncio.gather(
            self._service_discovery_loop(),
            self._health_monitoring_loop(),
            self._event_processing_loop(),
        )

    async def register_service(
        self,
        service_type: ServiceType,
        service_name: str,
        base_url: str,
        api_key: str,
        capabilities: List[str],
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Register a service with the hub"""

        logger.info(f"📝 Registering service: {service_name} ({service_type})")

        service_id = f"{service_type}:{service_name}"

        # Store in memory
        self.services[service_id] = {
            "service_id": service_id,
            "service_type": service_type,
            "service_name": service_name,
            "base_url": base_url,
            "api_key": api_key,
            "capabilities": capabilities,
            "metadata": metadata or {},
            "status": "active",
            "registered_at": datetime.utcnow().isoformat(),
            "last_heartbeat": datetime.utcnow().isoformat(),
        }

        # Store in database
        service = RegisteredService(
            service_id=service_id,
            service_type=service_type,
            service_name=service_name,
            base_url=base_url,
            api_key=api_key,
            capabilities=capabilities,
            metadata=metadata or {},
            status="active",
        )
        self.db.add(service)
        self.db.commit()

        # Notify other services
        await self._broadcast_event(
            "service.registered",
            {
                "service_id": service_id,
                "service_type": service_type,
                "capabilities": capabilities,
            },
        )

        logger.info(f"✅ Service registered: {service_id}")

        return {
            "service_id": service_id,
            "status": "registered",
            "hub_url": self.config["hub_url"],
        }

    async def unregister_service(self, service_id: str):
        """Unregister a service"""

        if service_id in self.services:
            del self.services[service_id]

            # Update database
            service = (
                self.db.query(RegisteredService)
                .filter(RegisteredService.service_id == service_id)
                .first()
            )

            if service:
                service.status = "inactive"
                self.db.commit()

            # Notify other services
            await self._broadcast_event(
                "service.unregistered", {"service_id": service_id}
            )

            logger.info(f"Service unregistered: {service_id}")

    async def discover_services(
        self,
        service_type: Optional[ServiceType] = None,
        capability: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Discover available services"""

        services = list(self.services.values())

        # Filter by type
        if service_type:
            services = [s for s in services if s["service_type"] == service_type]

        # Filter by capability
        if capability:
            services = [s for s in services if capability in s["capabilities"]]

        return services

    async def call_service(
        self,
        service_id: str,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make a call to another service"""

        service = self.services.get(service_id)

        if not service:
            raise ValueError(f"Service not found: {service_id}")

        url = f"{service['base_url']}{endpoint}"

        # Add authentication
        if not headers:
            headers = {}
        headers["X-API-Key"] = service["api_key"]
        headers["X-Hub-Request"] = "true"

        # Log the call
        call_log = CrossServiceCall(
            source_service="enterprise-hub",
            target_service=service_id,
            endpoint=endpoint,
            method=method,
            request_data=data,
            timestamp=datetime.utcnow(),
        )
        self.db.add(call_log)
        self.db.commit()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    result = await response.json()

                    # Update call log
                    call_log.response_data = result
                    call_log.status_code = response.status
                    call_log.success = response.status < 400
                    self.db.commit()

                    return result

        except Exception as e:
            logger.error(f"Error calling service {service_id}: {e}")
            call_log.success = False
            call_log.error_message = str(e)
            self.db.commit()
            raise

    async def broadcast_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        source_service: str = "enterprise-hub",
    ):
        """Broadcast an event to all subscribed services"""

        await self._broadcast_event(event_type, event_data, source_service)

    async def subscribe_to_events(self, service_id: str, event_types: List[str]):
        """Subscribe a service to specific event types"""

        for event_type in event_types:
            if event_type not in self.event_subscribers:
                self.event_subscribers[event_type] = set()

            self.event_subscribers[event_type].add(service_id)

        logger.info(f"Service {service_id} subscribed to events: {event_types}")

    async def get_service_health(self, service_id: str) -> Dict[str, Any]:
        """Get health status of a service"""

        service = self.services.get(service_id)

        if not service:
            return {"status": "not_found"}

        try:
            # Call health endpoint
            result = await self.call_service(service_id, "/health", method="GET")

            # Store health check
            health = ServiceHealth(
                service_id=service_id,
                status=result.get("status", "unknown"),
                response_time_ms=result.get("response_time_ms", 0),
                metrics=result.get("metrics", {}),
                timestamp=datetime.utcnow(),
            )
            self.db.add(health)
            self.db.commit()

            return result

        except Exception as e:
            logger.error(f"Health check failed for {service_id}: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def ninja_control_command(
        self, target_service: str, command: str, parameters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Allow Ninja to send control commands to any service
        Commands: fix, update, restart, optimize, diagnose
        """

        logger.info(f"🥷 Ninja control command: {command} → {target_service}")

        # Verify Ninja is registered
        ninja_services = await self.discover_services(ServiceType.NINJA)
        if not ninja_services:
            raise ValueError("Ninja service not registered")

        # Send command to target service
        result = await self.call_service(
            target_service,
            "/api/ninja-control",
            method="POST",
            data={
                "command": command,
                "parameters": parameters or {},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        # Log the control action
        await self._broadcast_event(
            "ninja.control",
            {"target_service": target_service, "command": command, "result": result},
        )

        return result

    async def cross_service_workflow(
        self, workflow_name: str, steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a workflow across multiple services
        Example: User verification (Passport) → Document check (ProofLink) → Impact tracking (ImpactOS)
        """

        logger.info(f"🔄 Starting cross-service workflow: {workflow_name}")

        results = []

        for step in steps:
            service_id = step["service_id"]
            endpoint = step["endpoint"]
            method = step.get("method", "POST")
            data = step.get("data", {})

            # Execute step
            try:
                result = await self.call_service(service_id, endpoint, method, data)

                results.append(
                    {
                        "step": step["name"],
                        "service": service_id,
                        "success": True,
                        "result": result,
                    }
                )

                # Pass result to next step if needed
                if step.get("pass_result_to_next"):
                    if len(steps) > len(results):
                        steps[len(results)]["data"].update(result)

            except Exception as e:
                logger.error(f"Workflow step failed: {step['name']}: {e}")
                results.append(
                    {
                        "step": step["name"],
                        "service": service_id,
                        "success": False,
                        "error": str(e),
                    }
                )

                # Stop workflow on error
                if step.get("stop_on_error", True):
                    break

        return {
            "workflow": workflow_name,
            "steps_completed": len(results),
            "total_steps": len(steps),
            "success": all(r["success"] for r in results),
            "results": results,
        }

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get overall integration status"""

        return {
            "hub_status": "active",
            "registered_services": len(self.services),
            "services": [
                {
                    "service_id": s["service_id"],
                    "service_type": s["service_type"],
                    "status": s["status"],
                    "last_heartbeat": s["last_heartbeat"],
                }
                for s in self.services.values()
            ],
            "event_subscribers": {
                event_type: len(subscribers)
                for event_type, subscribers in self.event_subscribers.items()
            },
            "capabilities": self._get_all_capabilities(),
        }

    def _get_all_capabilities(self) -> Dict[str, List[str]]:
        """Get all capabilities across all services"""

        capabilities = {}

        for service in self.services.values():
            service_type = service["service_type"]
            if service_type not in capabilities:
                capabilities[service_type] = []

            capabilities[service_type].extend(service["capabilities"])

        return capabilities

    async def _service_discovery_loop(self):
        """Continuously discover new services"""

        while True:
            try:
                if self.config["auto_discovery"]:
                    # Auto-discover services on common ports
                    await self._auto_discover_services()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in service discovery: {e}")
                await asyncio.sleep(60)

    async def _health_monitoring_loop(self):
        """Continuously monitor service health"""

        while True:
            try:
                if self.config["health_monitoring"]:
                    for service_id in list(self.services.keys()):
                        await self.get_service_health(service_id)

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(self.health_check_interval)

    async def _event_processing_loop(self):
        """Process events from event bus"""

        while True:
            try:
                if self.config["event_bus_enabled"]:
                    # Process pending events
                    await self._process_pending_events()

                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in event processing: {e}")
                await asyncio.sleep(1)

    async def _broadcast_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        source_service: str = "enterprise-hub",
    ):
        """Broadcast event to subscribers"""

        # Store event
        event = IntegrationEvent(
            event_type=event_type,
            event_data=event_data,
            source_service=source_service,
            timestamp=datetime.utcnow(),
        )
        self.db.add(event)
        self.db.commit()

        # Get subscribers
        subscribers = self.event_subscribers.get(event_type, set())

        # Send to each subscriber
        for service_id in subscribers:
            try:
                await self.call_service(
                    service_id,
                    "/api/events",
                    method="POST",
                    data={
                        "event_type": event_type,
                        "event_data": event_data,
                        "source_service": source_service,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
            except Exception as e:
                logger.error(f"Error sending event to {service_id}: {e}")

    async def _auto_discover_services(self):
        """Auto-discover services on network"""

        # Common ports for iTechSmart services
        service_ports = {
            ServiceType.NINJA: 8001,
            ServiceType.SUPREME: 8002,
            ServiceType.HL7: 8003,
            ServiceType.IMPACTOS: 8004,
            ServiceType.PASSPORT: 8005,
            ServiceType.PROOFLINK: 8006,
        }

        for service_type, port in service_ports.items():
            try:
                url = f"http://localhost:{port}/api/service-info"

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url, timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            info = await response.json()

                            service_id = f"{service_type}:{info['name']}"

                            # Register if not already registered
                            if service_id not in self.services:
                                await self.register_service(
                                    service_type=service_type,
                                    service_name=info["name"],
                                    base_url=f"http://localhost:{port}",
                                    api_key=info.get("api_key", ""),
                                    capabilities=info.get("capabilities", []),
                                    metadata=info.get("metadata", {}),
                                )

            except Exception:
                # Service not available, skip
                pass

    async def _process_pending_events(self):
        """Process any pending events"""

        # Get unprocessed events from database
        events = (
            self.db.query(IntegrationEvent)
            .filter(IntegrationEvent.processed == False)
            .limit(100)
            .all()
        )

        for event in events:
            try:
                await self._broadcast_event(
                    event.event_type, event.event_data, event.source_service
                )

                event.processed = True
                self.db.commit()

            except Exception as e:
                logger.error(f"Error processing event {event.id}: {e}")
