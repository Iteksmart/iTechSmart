"""
iTechSmart Sandbox - Suite Integration Module
Integrates with Enterprise Hub and Ninja for monitoring and self-healing
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class SandboxIntegration:
    """
    Integration client for iTechSmart Sandbox

    Connects to:
    - Enterprise Hub (service registration, health reporting)
    - Ninja (error reporting, self-healing)
    - All 32 iTechSmart products (for testing)
    """

    def __init__(
        self,
        service_name: str = "itechsmart-sandbox",
        service_port: int = 8033,
        hub_url: str = "http://localhost:8001",
        ninja_url: str = "http://localhost:8002",
    ):
        self.service_name = service_name
        self.service_port = service_port
        self.hub_url = hub_url
        self.ninja_url = ninja_url
        self.running = False
        self.client = httpx.AsyncClient(timeout=10.0)

        # All iTechSmart products for testing
        self.suite_products = [
            {"name": "itechsmart-enterprise", "port": 8001},
            {"name": "itechsmart-ninja", "port": 8002},
            {"name": "itechsmart-analytics", "port": 8003},
            {"name": "itechsmart-supreme", "port": 8004},
            {"name": "itechsmart-hl7", "port": 8005},
            {"name": "prooflink", "port": 8006},
            {"name": "passport", "port": 8007},
            {"name": "impactos", "port": 8008},
            {"name": "legalai-pro", "port": 8009},
            {"name": "itechsmart-dataflow", "port": 8010},
            {"name": "itechsmart-pulse", "port": 8011},
            {"name": "itechsmart-connect", "port": 8012},
            {"name": "itechsmart-vault", "port": 8013},
            {"name": "itechsmart-notify", "port": 8014},
            {"name": "itechsmart-ledger", "port": 8015},
            {"name": "itechsmart-copilot", "port": 8016},
            {"name": "itechsmart-shield", "port": 8017},
            {"name": "itechsmart-workflow", "port": 8018},
            {"name": "itechsmart-marketplace", "port": 8019},
            {"name": "itechsmart-cloud", "port": 8020},
            {"name": "itechsmart-devops", "port": 8021},
            {"name": "itechsmart-mobile", "port": 8022},
            {"name": "itechsmart-ai", "port": 8023},
            {"name": "itechsmart-compliance", "port": 8024},
            {"name": "itechsmart-data-platform", "port": 8025},
            {"name": "itechsmart-customer-success", "port": 8026},
            {"name": "itechsmart-port-manager", "port": 8100},
            {"name": "itechsmart-mdm-agent", "port": 8200},
            {"name": "itechsmart-qaqc", "port": 8300},
            {"name": "itechsmart-thinktank", "port": 8030},
            {"name": "itechsmart-sentinel", "port": 8031},
            {"name": "itechsmart-forge", "port": 8032},
        ]

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
                "service_type": "sandbox_environment",
                "version": "1.0.0",
                "port": self.service_port,
                "endpoints": {
                    "health": f"http://localhost:{self.service_port}/health",
                    "api": f"http://localhost:{self.service_port}/api",
                    "docs": f"http://localhost:{self.service_port}/docs",
                },
                "capabilities": [
                    "secure_code_execution",
                    "docker_isolation",
                    "gpu_support",
                    "persistent_storage",
                    "port_exposure",
                    "filesystem_snapshots",
                    "resource_monitoring",
                    "test_execution",
                    "suite_testing",
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
                    "metrics": {
                        "uptime": "operational",
                        "response_time": "normal",
                        "active_sandboxes": 0,
                    },
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
                        "active_sandboxes": 0,
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

    async def test_product(
        self, product_name: str, test_type: str = "health"
    ) -> Dict[str, Any]:
        """Test an iTechSmart product"""
        product = next(
            (p for p in self.suite_products if p["name"] == product_name), None
        )

        if not product:
            return {"success": False, "error": "Product not found"}

        try:
            # Test product health endpoint
            response = await self.client.get(
                f"http://localhost:{product['port']}/health", timeout=5.0
            )

            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global integration instance
integration: Optional[SandboxIntegration] = None


async def init_integration():
    """Initialize integration"""
    integration = SandboxIntegration()
    await integration.start()


async def shutdown_integration():
    """Shutdown integration"""
    if integration:
        await integration.stop()
