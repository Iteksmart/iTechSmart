"""
iTechSmart Sentinel - Ninja Self-Healing Integration
"""

import asyncio
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
import os


class NinjaIntegrationClient:
    """
    Integration client for iTechSmart Ninja (Self-Healing)
    """
    
    def __init__(self):
        self.ninja_url = os.getenv("NINJA_URL", "http://localhost:8002")
        self.service_name = "itechsmart-sentinel"
        self.is_connected = False
        self._error_monitor_task = None
        self._performance_task = None
    
    async def initialize(self):
        """Initialize Ninja integration"""
        try:
            await self.register_with_ninja()
            
            # Start background tasks
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
                    "service_type": "observability",
                    "version": "1.0.0",
                    "capabilities": [
                        "distributed_tracing",
                        "alerting",
                        "log_aggregation"
                    ]
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                print("✅ Registered with Ninja")
            else:
                raise Exception(f"Ninja registration failed: {response.status_code}")
    
    async def report_error(
        self,
        error_type: str,
        error_message: str,
        severity: str = "medium",
        context: Optional[Dict[str, Any]] = None
    ):
        """Report an error to Ninja for auto-fixing"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.ninja_url}/api/suite-control/error",
                    json={
                        "service_name": self.service_name,
                        "error_type": error_type,
                        "error_message": error_message,
                        "severity": severity,
                        "timestamp": datetime.utcnow().isoformat(),
                        "context": context or {}
                    },
                    timeout=5.0
                )
        except Exception as e:
            print(f"⚠️  Error report to Ninja failed: {e}")
    
    async def _performance_monitor(self):
        """Monitor and report performance to Ninja every 60 seconds"""
        while True:
            try:
                await asyncio.sleep(60)
                
                # TODO: Collect actual performance metrics
                performance = {
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "response_time_ms": 0.0,
                    "error_rate": 0.0
                }
                
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.ninja_url}/api/suite-control/performance",
                        json={
                            "service_name": self.service_name,
                            "timestamp": datetime.utcnow().isoformat(),
                            "metrics": performance
                        },
                        timeout=5.0
                    )
            except Exception as e:
                print(f"⚠️  Performance report to Ninja failed: {e}")
    
    async def request_healing(
        self,
        issue_description: str,
        suggested_action: Optional[str] = None
    ) -> bool:
        """Request Ninja to perform healing action"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ninja_url}/api/suite-control/heal",
                    json={
                        "service_name": self.service_name,
                        "issue": issue_description,
                        "suggested_action": suggested_action,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    timeout=30.0
                )
                
                return response.status_code == 200
        except Exception as e:
            print(f"⚠️  Healing request failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown Ninja integration"""
        if self._error_monitor_task:
            self._error_monitor_task.cancel()
        if self._performance_task:
            self._performance_task.cancel()
        
        print("✅ Ninja integration shut down")


# Global instance
ninja_client = NinjaIntegrationClient()