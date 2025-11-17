"""
Suite Integration Module
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class SuiteIntegration:
    def __init__(self, service_name: str, service_port: int):
        self.service_name = service_name
        self.service_port = service_port
        self.hub_url = "http://localhost:8001"
        self.ninja_url = "http://localhost:8002"
        self.running = False
        self.client = httpx.AsyncClient(timeout=10.0)

    async def start(self):
        self.running = True
        await self._register_with_hub()
        asyncio.create_task(self._health_reporter())
        asyncio.create_task(self._metrics_reporter())
        logger.info(f"{self.service_name} integration started")

    async def stop(self):
        self.running = False
        await self.client.aclose()

    async def _register_with_hub(self):
        try:
            data = {
                "service_name": self.service_name,
                "port": self.service_port,
                "version": "1.0.0",
            }
            await self.client.post(f"{self.hub_url}/api/services/register", json=data)
        except Exception as e:
            logger.error(f"Hub registration error: {e}")

    async def _health_reporter(self):
        while self.running:
            try:
                data = {"service_name": self.service_name, "status": "healthy"}
                await self.client.post(f"{self.hub_url}/api/services/health", json=data)
            except:
                pass
            await asyncio.sleep(30)

    async def _metrics_reporter(self):
        while self.running:
            try:
                data = {"service_name": self.service_name, "metrics": {}}
                await self.client.post(
                    f"{self.hub_url}/api/services/metrics", json=data
                )
            except:
                pass
            await asyncio.sleep(60)


integration: Optional[SuiteIntegration] = None


async def init_integration(service_name: str, service_port: int):
    integration = SuiteIntegration(service_name, service_port)
    await integration.start()


async def shutdown_integration():
    if integration:
        await integration.stop()
