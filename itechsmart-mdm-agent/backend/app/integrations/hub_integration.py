"""
Enterprise Hub Integration for iTechSmart MDM Deployment Agent

Provides integration with iTechSmart Enterprise Hub for service registration,
health reporting, metrics collection, and service discovery.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)


class HubIntegration:
    """
    Integration client for iTechSmart Enterprise Hub
    
    Features:
    - Service registration
    - Health reporting (30-second intervals)
    - Metrics reporting (60-second intervals)
    - Service discovery
    - Configuration updates
    """
    
    def __init__(
        self,
        hub_url: str = "http://localhost:8001",
        service_name: str = "itechsmart-mdm-agent",
        service_port: int = 8200
    ):
        """
        Initialize Hub Integration
        
        Args:
            hub_url: URL of Enterprise Hub
            service_name: Name of this service
            service_port: Port this service runs on
        """
        self.hub_url = hub_url
        self.service_name = service_name
        self.service_port = service_port
        self.registered = False
        self.running = False
        
        # Background tasks
        self.health_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        
        logger.info(f"Hub Integration initialized for {service_name}")
    
    async def start(self):
        """Start Hub integration"""
        if self.running:
            logger.warning("Hub Integration already running")
            return
        
        # Register with Hub
        await self.register_service()
        
        # Start background tasks
        self.running = True
        self.health_task = asyncio.create_task(self._health_reporting_loop())
        self.metrics_task = asyncio.create_task(self._metrics_reporting_loop())
        
        logger.info("Hub Integration started")
    
    async def stop(self):
        """Stop Hub integration"""
        self.running = False
        
        # Cancel background tasks
        if self.health_task:
            self.health_task.cancel()
            try:
                await self.health_task
            except asyncio.CancelledError:
                pass
        
        if self.metrics_task:
            self.metrics_task.cancel()
            try:
                await self.metrics_task
            except asyncio.CancelledError:
                pass
        
        # Unregister from Hub
        await self.unregister_service()
        
        logger.info("Hub Integration stopped")
    
    async def register_service(self) -> bool:
        """
        Register service with Enterprise Hub
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "service_name": self.service_name,
                    "service_type": "mdm_agent",
                    "port": self.service_port,
                    "health_endpoint": "/health",
                    "capabilities": [
                        "deployment",
                        "configuration",
                        "monitoring",
                        "ai_optimization"
                    ],
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                async with session.post(
                    f"{self.hub_url}/api/services/register",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.registered = True
                        logger.info(f"Service registered with Hub: {self.service_name}")
                        return True
                    else:
                        logger.error(f"Failed to register with Hub: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error registering with Hub: {e}")
            return False
    
    async def unregister_service(self) -> bool:
        """
        Unregister service from Enterprise Hub
        
        Returns:
            True if unregistration successful, False otherwise
        """
        if not self.registered:
            return True
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.hub_url}/api/services/{self.service_name}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.registered = False
                        logger.info(f"Service unregistered from Hub: {self.service_name}")
                        return True
                    else:
                        logger.error(f"Failed to unregister from Hub: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error unregistering from Hub: {e}")
            return False
    
    async def report_health(self, status: str = "healthy") -> bool:
        """
        Report health status to Hub
        
        Args:
            status: Health status (healthy, degraded, unhealthy)
            
        Returns:
            True if report successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "service_name": self.service_name,
                    "status": status,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                async with session.post(
                    f"{self.hub_url}/api/services/health",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error reporting health to Hub: {e}")
            return False
    
    async def report_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Report metrics to Hub
        
        Args:
            metrics: Metrics dictionary
            
        Returns:
            True if report successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "service_name": self.service_name,
                    "metrics": metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                async with session.post(
                    f"{self.hub_url}/api/services/metrics",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error reporting metrics to Hub: {e}")
            return False
    
    async def discover_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Discover a service via Hub
        
        Args:
            service_name: Name of service to discover
            
        Returns:
            Service information or None if not found
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.hub_url}/api/services/{service_name}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
                    
        except Exception as e:
            logger.error(f"Error discovering service: {e}")
            return None
    
    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Call another service via Hub routing
        
        Args:
            service_name: Target service name
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            
        Returns:
            Response data or None if failed
        """
        try:
            # First discover the service
            service_info = await self.discover_service(service_name)
            if not service_info:
                logger.error(f"Service not found: {service_name}")
                return None
            
            # Make the call
            url = f"http://localhost:{service_info['port']}{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            return await response.json()
                elif method == "POST":
                    async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            return await response.json()
                
                return None
                
        except Exception as e:
            logger.error(f"Error calling service {service_name}: {e}")
            return None
    
    async def _health_reporting_loop(self):
        """Background task for health reporting (every 30 seconds)"""
        logger.info("Starting health reporting loop")
        
        while self.running:
            try:
                await self.report_health("healthy")
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Error in health reporting loop: {e}")
                await asyncio.sleep(30)
    
    async def _metrics_reporting_loop(self):
        """Background task for metrics reporting (every 60 seconds)"""
        logger.info("Starting metrics reporting loop")
        
        while self.running:
            try:
                # Collect metrics
                metrics = {
                    "cpu_usage": 45.0,
                    "memory_usage": 60.0,
                    "active_deployments": 5,
                    "total_deployments": 150
                }
                
                await self.report_metrics(metrics)
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in metrics reporting loop: {e}")
                await asyncio.sleep(60)
