"""
iTechSmart Think-Tank - Suite Integration Module
Integrates with Enterprise Hub and Ninja for monitoring and self-healing
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class ThinkTankIntegration:
    """
    Integration client for iTechSmart Think-Tank

    Connects to:
    - Enterprise Hub (service registration, health reporting)
    - Ninja (error reporting, self-healing)
    """

    def __init__(
        self,
        service_name: str = "itechsmart-thinktank",
        service_port: int = 8030,
        hub_url: str = "http://localhost:8001",
        ninja_url: str = "http://localhost:8002",
    ):
        self.service_name = service_name
        self.service_port = service_port
        self.hub_url = hub_url
        self.ninja_url = ninja_url
        self.running = False
        self.client = httpx.AsyncClient(timeout=10.0)

    async def start(self):
        """Start integration"""
        self.running = True

        # Register with Hub
        await self._register_with_hub()

        # Start background tasks
        asyncio.create_task(self._health_reporter())
        asyncio.create_task(self._metrics_reporter())
        asyncio.create_task(self._ninja_monitor())

        logger.info(f"{self.service_name} integration started")

    async def stop(self):
        """Stop integration"""
        self.running = False
        await self.client.aclose()
        logger.info(f"{self.service_name} integration stopped")

    async def _register_with_hub(self):
        """Register service with Enterprise Hub"""
        try:
            registration_data = {
                "service_name": self.service_name,
                "service_type": "internal_development",
                "version": "1.0.0",
                "port": self.service_port,
                "endpoints": {
                    "health": f"http://localhost:{self.service_port}/health",
                    "api": f"http://localhost:{self.service_port}/api",
                    "docs": f"http://localhost:{self.service_port}/docs",
                },
                "capabilities": [
                    "superninja_ai",
                    "code_generation",
                    "team_collaboration",
                    "project_management",
                    "client_portal",
                ],
            }

            response = await self.client.post(
                f"{self.hub_url}/api/services/register", json=registration_data
            )

            if response.status_code == 200:
                logger.info(f"Successfully registered with Hub")
            else:
                logger.warning(f"Hub registration failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Error registering with Hub: {e}")

    async def _health_reporter(self):
        """Report health to Hub every 30 seconds"""
        while self.running:
            try:
                health_data = {
                    "service_name": self.service_name,
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": {"uptime": "operational", "response_time": "normal"},
                }

                await self.client.post(
                    f"{self.hub_url}/api/services/health", json=health_data
                )
            except Exception as e:
                logger.error(f"Error reporting health: {e}")

            await asyncio.sleep(30)

    async def _metrics_reporter(self):
        """Report metrics to Hub every 60 seconds"""
        while self.running:
            try:
                metrics_data = {
                    "service_name": self.service_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": {
                        "requests_total": 0,
                        "requests_per_second": 0,
                        "error_rate": 0,
                        "avg_response_time": 0,
                    },
                }

                await self.client.post(
                    f"{self.hub_url}/api/services/metrics", json=metrics_data
                )
            except Exception as e:
                logger.error(f"Error reporting metrics: {e}")

            await asyncio.sleep(60)

    async def _ninja_monitor(self):
        """Report to Ninja for monitoring every 60 seconds"""
        while self.running:
            try:
                monitor_data = {
                    "service_name": self.service_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "operational",
                    "performance": {"cpu_usage": 0, "memory_usage": 0, "disk_usage": 0},
                }

                await self.client.post(
                    f"{self.ninja_url}/api/monitor", json=monitor_data
                )
            except Exception as e:
                logger.error(f"Error reporting to Ninja: {e}")

            await asyncio.sleep(60)

    async def report_error(self, error: Exception, context: Dict[str, Any]):
        """Report error to Ninja for self-healing"""
        try:
            error_data = {
                "service_name": self.service_name,
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "severity": "high",
            }

            await self.client.post(
                f"{self.ninja_url}/api/errors/report", json=error_data
            )

            logger.info(f"Error reported to Ninja for self-healing")
        except Exception as e:
            logger.error(f"Error reporting to Ninja: {e}")


# Global integration instance
integration: Optional[ThinkTankIntegration] = None


async def init_integration():
    """Initialize integration"""
    integration = ThinkTankIntegration()
    await integration.start()


async def shutdown_integration():
    """Shutdown integration"""
    if integration:
        await integration.stop()
