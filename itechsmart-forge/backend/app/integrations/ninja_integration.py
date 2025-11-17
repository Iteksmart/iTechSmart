"""
iTechSmart Forge - Ninja Self-Healing Integration
"""

import asyncio
import httpx
from datetime import datetime
import os


class NinjaIntegrationClient:
    """Integration client for iTechSmart Ninja (Self-Healing)"""

    def __init__(self):
        self.ninja_url = os.getenv("NINJA_URL", "http://localhost:8002")
        self.service_name = "itechsmart-forge"
        self.is_connected = False
        self._performance_task = None

    async def initialize(self):
        """Initialize Ninja integration"""
        try:
            await self.register_with_ninja()
            self._performance_task = asyncio.create_task(self._performance_monitor())
            self.is_connected = True
            print(f"✅ Connected to Ninja at {self.ninja_url}")
        except Exception as e:
            print(f"⚠️  Could not connect to Ninja: {e}")
            self.is_connected = False

    async def register_with_ninja(self):
        """Register with Ninja for monitoring"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ninja_url}/api/suite-control/register",
                json={
                    "service_name": self.service_name,
                    "service_type": "low_code_platform",
                    "version": "1.0.0",
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                print("✅ Registered with Ninja")

    async def _performance_monitor(self):
        """Monitor and report performance to Ninja every 60 seconds"""
        while True:
            try:
                await asyncio.sleep(60)
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.ninja_url}/api/suite-control/performance",
                        json={
                            "service_name": self.service_name,
                            "timestamp": datetime.utcnow().isoformat(),
                            "metrics": {
                                "cpu_usage": 0.0,
                                "memory_usage": 0.0,
                                "response_time_ms": 0.0,
                            },
                        },
                        timeout=5.0,
                    )
            except Exception as e:
                print(f"⚠️  Performance report to Ninja failed: {e}")

    async def shutdown(self):
        """Shutdown Ninja integration"""
        if self._performance_task:
            self._performance_task.cancel()
        print("✅ Ninja integration shut down")


# Global instance
ninja_client = NinjaIntegrationClient()
