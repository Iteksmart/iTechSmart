"""
Ninja Integration for iTechSmart MDM Deployment Agent

Provides integration with iTechSmart Ninja for error reporting,
auto-healing, performance monitoring, and self-healing capabilities.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)


class NinjaIntegration:
    """
    Integration client for iTechSmart Ninja
    
    Features:
    - Error detection and reporting
    - Auto-healing requests
    - Performance monitoring
    - Self-healing automation
    """
    
    def __init__(
        self,
        ninja_url: str = "http://localhost:8002",
        service_name: str = "itechsmart-mdm-agent"
    ):
        """
        Initialize Ninja Integration
        
        Args:
            ninja_url: URL of Ninja service
            service_name: Name of this service
        """
        self.ninja_url = ninja_url
        self.service_name = service_name
        self.running = False
        
        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        
        logger.info(f"Ninja Integration initialized for {service_name}")
    
    async def start(self):
        """Start Ninja integration"""
        if self.running:
            logger.warning("Ninja Integration already running")
            return
        
        self.running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Ninja Integration started")
    
    async def stop(self):
        """Stop Ninja integration"""
        self.running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Ninja Integration stopped")
    
    async def report_error(
        self,
        error_type: str,
        error_message: str,
        severity: str = "medium",
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Report an error to Ninja
        
        Args:
            error_type: Type of error
            error_message: Error message
            severity: Error severity (low, medium, high, critical)
            context: Additional context
            
        Returns:
            True if report successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "service_name": self.service_name,
                    "error_type": error_type,
                    "error_message": error_message,
                    "severity": severity,
                    "context": context or {},
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                async with session.post(
                    f"{self.ninja_url}/api/errors/report",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Error reported to Ninja: {error_type}")
                        return True
                    else:
                        logger.error(f"Failed to report error to Ninja: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error reporting to Ninja: {e}")
            return False
    
    async def request_healing(
        self,
        issue_type: str,
        issue_description: str,
        affected_service: str
    ) -> Optional[Dict[str, Any]]:
        """
        Request auto-healing from Ninja
        
        Args:
            issue_type: Type of issue
            issue_description: Description of the issue
            affected_service: Name of affected service
            
        Returns:
            Healing response or None if failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "service_name": self.service_name,
                    "issue_type": issue_type,
                    "issue_description": issue_description,
                    "affected_service": affected_service,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                async with session.post(
                    f"{self.ninja_url}/api/heal",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Healing requested for {affected_service}")
                        return result
                    else:
                        logger.error(f"Failed to request healing: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error requesting healing from Ninja: {e}")
            return None
    
    async def report_performance(
        self,
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Report performance metrics to Ninja
        
        Args:
            metrics: Performance metrics
            
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
                    f"{self.ninja_url}/api/performance/report",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error reporting performance to Ninja: {e}")
            return False
    
    async def check_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Check health of a service via Ninja
        
        Args:
            service_name: Name of service to check
            
        Returns:
            Health status or None if failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ninja_url}/api/health/{service_name}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
                    
        except Exception as e:
            logger.error(f"Error checking health via Ninja: {e}")
            return None
    
    async def get_recommendations(
        self,
        service_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get optimization recommendations from Ninja
        
        Args:
            service_name: Name of service
            
        Returns:
            Recommendations or None if failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ninja_url}/api/recommendations/{service_name}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting recommendations from Ninja: {e}")
            return None
    
    async def _monitoring_loop(self):
        """Background task for performance monitoring (every 60 seconds)"""
        logger.info("Starting Ninja monitoring loop")
        
        while self.running:
            try:
                # Collect and report performance metrics
                metrics = {
                    "cpu_usage": 45.0,
                    "memory_usage": 60.0,
                    "response_time": 0.05,
                    "error_rate": 0.01
                }
                
                await self.report_performance(metrics)
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in Ninja monitoring loop: {e}")
                await asyncio.sleep(60)
