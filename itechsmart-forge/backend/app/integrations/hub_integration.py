"""
iTechSmart Forge - Enterprise Hub Integration
"""

import asyncio
import httpx
from datetime import datetime
import os


class HubIntegrationClient:
    """Integration client for iTechSmart Enterprise Hub"""

    def __init__(self):
        self.hub_url = os.getenv("ENTERPRISE_HUB_URL", "http://localhost:8001")
        self.service_name = "itechsmart-forge"
        self.service_port = int(os.getenv("PORT", "8320"))
        self.is_connected = False
        self.service_id = None
        self._health_task = None
        self._metrics_task = None

    async def initialize(self):
        """Initialize Hub integration"""
        try:
            await self.register_service()
            self._health_task = asyncio.create_task(self._health_reporter())
            self._metrics_task = asyncio.create_task(self._metrics_reporter())
            self.is_connected = True
            print(f"✅ Connected to Enterprise Hub at {self.hub_url}")
        except Exception as e:
            print(f"⚠️  Could not connect to Enterprise Hub: {e}")
            self.is_connected = False

    async def register_service(self):
        """Register service with Enterprise Hub"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.hub_url}/api/integration/register",
                json={
                    "service_name": self.service_name,
                    "service_type": "low_code_platform",
                    "version": "1.0.0",
                    "host": "localhost",
                    "port": self.service_port,
                    "health_endpoint": "/health",
                    "capabilities": [
                        "visual_app_builder",
                        "ai_generation",
                        "data_connectors",
                        "workflow_automation",
                        "one_click_deployment",
                    ],
                    "metadata": {
                        "product_number": 32,
                        "description": "Low-Code/No-Code Application Builder",
                    },
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                data = response.json()
                self.service_id = data.get("service_id")
                print(f"✅ Registered with Hub (ID: {self.service_id})")

    async def _health_reporter(self):
        """Report health to Hub every 30 seconds"""
        while True:
            try:
                await asyncio.sleep(30)
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.hub_url}/api/integration/health",
                        json={
                            "service_name": self.service_name,
                            "status": "healthy",
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        timeout=5.0,
                    )
            except Exception as e:
                print(f"⚠️  Health report failed: {e}")

    async def _metrics_reporter(self):
        """Report metrics to Hub every 60 seconds"""
        while True:
            try:
                await asyncio.sleep(60)
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.hub_url}/api/integration/metrics",
                        json={
                            "service_name": self.service_name,
                            "timestamp": datetime.utcnow().isoformat(),
                            "metrics": {
                                "apps_count": 0,
                                "deployments_count": 0,
                                "ai_requests_count": 0,
                            },
                        },
                        timeout=5.0,
                    )
            except Exception as e:
                print(f"⚠️  Metrics report failed: {e}")

    async def shutdown(self):
        """Shutdown Hub integration"""
        if self._health_task:
            self._health_task.cancel()
        if self._metrics_task:
            self._metrics_task.cancel()

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.hub_url}/api/integration/unregister",
                    json={"service_name": self.service_name},
                    timeout=5.0,
                )
            print("✅ Unregistered from Enterprise Hub")
        except Exception as e:
            print(f"⚠️  Unregister failed: {e}")


# Global instance
hub_client = HubIntegrationClient()
