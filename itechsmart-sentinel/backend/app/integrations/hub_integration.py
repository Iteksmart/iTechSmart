"""
iTechSmart Sentinel - Enterprise Hub Integration
"""

import asyncio
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
import os


class HubIntegrationClient:
    """
    Integration client for iTechSmart Enterprise Hub
    """
    
    def __init__(self):
        self.hub_url = os.getenv("ENTERPRISE_HUB_URL", "http://localhost:8001")
        self.service_name = "itechsmart-sentinel"
        self.service_port = int(os.getenv("PORT", "8310"))
        self.is_connected = False
        self.service_id = None
        self._health_task = None
        self._metrics_task = None
    
    async def initialize(self):
        """Initialize Hub integration"""
        try:
            await self.register_service()
            
            # Start background tasks
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
                    "service_type": "observability",
                    "version": "1.0.0",
                    "host": "localhost",
                    "port": self.service_port,
                    "health_endpoint": "/health",
                    "capabilities": [
                        "distributed_tracing",
                        "alerting",
                        "log_aggregation",
                        "incident_management",
                        "slo_tracking"
                    ],
                    "metadata": {
                        "product_number": 31,
                        "description": "Real-Time Observability & Incident Management"
                    }
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                self.service_id = data.get("service_id")
                print(f"✅ Registered with Hub (ID: {self.service_id})")
            else:
                raise Exception(f"Registration failed: {response.status_code}")
    
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
                            "checks": {
                                "database": "healthy",
                                "tracing": "operational",
                                "alerting": "operational",
                                "logs": "operational"
                            }
                        },
                        timeout=5.0
                    )
            except Exception as e:
                print(f"⚠️  Health report failed: {e}")
    
    async def _metrics_reporter(self):
        """Report metrics to Hub every 60 seconds"""
        while True:
            try:
                await asyncio.sleep(60)
                
                # TODO: Collect actual metrics
                metrics = {
                    "traces_count": 0,
                    "alerts_count": 0,
                    "logs_count": 0,
                    "incidents_count": 0,
                    "slos_count": 0
                }
                
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.hub_url}/api/integration/metrics",
                        json={
                            "service_name": self.service_name,
                            "timestamp": datetime.utcnow().isoformat(),
                            "metrics": metrics
                        },
                        timeout=5.0
                    )
            except Exception as e:
                print(f"⚠️  Metrics report failed: {e}")
    
    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Call another service via Hub routing"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    f"{self.hub_url}/api/integration/call/{service_name}{endpoint}",
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"⚠️  Service call failed: {response.status_code}")
                    return None
        except Exception as e:
            print(f"⚠️  Service call error: {e}")
            return None
    
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
                    timeout=5.0
                )
            print("✅ Unregistered from Enterprise Hub")
        except Exception as e:
            print(f"⚠️  Unregister failed: {e}")


# Global instance
hub_client = HubIntegrationClient()