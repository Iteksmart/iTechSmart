"""
iTechSmart HL7 - Service Health Manager
Monitors and manages HL7 services with automatic restart capability
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DOWN = "down"
    RESTARTING = "restarting"
    UNKNOWN = "unknown"


class ServiceType(str, Enum):
    """Types of HL7 services"""
    INTERFACE_ENGINE = "interface_engine"
    MESSAGE_PROCESSOR = "message_processor"
    DATABASE = "database"
    API_SERVER = "api_server"
    MONITORING = "monitoring"
    INTEGRATION = "integration"


class HealthCheck(BaseModel):
    """Health check result"""
    service_name: str
    status: ServiceStatus
    response_time: float  # milliseconds
    checked_at: datetime
    error: Optional[str] = None
    metrics: Dict[str, Any] = {}


class ServiceConfig(BaseModel):
    """Service configuration"""
    service_name: str
    service_type: ServiceType
    health_check_url: Optional[str] = None
    health_check_interval: int = 60  # seconds
    restart_command: Optional[str] = None
    stop_command: Optional[str] = None
    start_command: Optional[str] = None
    max_restart_attempts: int = 3
    restart_cooldown: int = 300  # 5 minutes
    dependencies: List[str] = []


class ServiceHealthManager:
    """
    Service health manager for HL7 systems
    
    Features:
    - Continuous health monitoring
    - Automatic service restart on failure
    - Dependency management
    - Health check history
    - Service metrics tracking
    - Restart cooldown to prevent restart loops
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.health_status: Dict[str, HealthCheck] = {}
        self.health_history: Dict[str, List[HealthCheck]] = {}
        self.restart_history: Dict[str, List[datetime]] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.running = False
        self.statistics = {
            "total_health_checks": 0,
            "healthy_services": 0,
            "unhealthy_services": 0,
            "total_restarts": 0,
            "successful_restarts": 0,
            "failed_restarts": 0
        }
        
    async def start(self):
        """Start the service health manager"""
        self.running = True
        logger.info("Service health manager started")
        
        # Start monitoring all registered services
        for service_name in self.services:
            await self._start_monitoring(service_name)
    
    async def stop(self):
        """Stop the service health manager"""
        self.running = False
        
        # Stop all monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        logger.info("Service health manager stopped")
    
    def register_service(self, config: ServiceConfig):
        """
        Register a service for monitoring
        
        Args:
            config: ServiceConfig for the service
        """
        self.services[config.service_name] = config
        self.health_history[config.service_name] = []
        self.restart_history[config.service_name] = []
        
        logger.info(f"Service registered: {config.service_name}")
        
        # Start monitoring if manager is running
        if self.running:
            asyncio.create_task(self._start_monitoring(config.service_name))
    
    def unregister_service(self, service_name: str):
        """Unregister a service"""
        if service_name in self.services:
            # Stop monitoring
            if service_name in self.monitoring_tasks:
                self.monitoring_tasks[service_name].cancel()
                del self.monitoring_tasks[service_name]
            
            # Remove from tracking
            del self.services[service_name]
            if service_name in self.health_status:
                del self.health_status[service_name]
            
            logger.info(f"Service unregistered: {service_name}")
    
    async def _start_monitoring(self, service_name: str):
        """Start monitoring a service"""
        config = self.services[service_name]
        
        async def monitor():
            while self.running:
                try:
                    # Perform health check
                    health = await self._check_health(service_name)
                    
                    # Store health status
                    self.health_status[service_name] = health
                    self.health_history[service_name].append(health)
                    
                    # Keep only last 1000 checks
                    if len(self.health_history[service_name]) > 1000:
                        self.health_history[service_name] = self.health_history[service_name][-1000:]
                    
                    # Update statistics
                    self.statistics["total_health_checks"] += 1
                    
                    # Handle unhealthy service
                    if health.status in [ServiceStatus.UNHEALTHY, ServiceStatus.DOWN]:
                        await self._handle_unhealthy_service(service_name, health)
                    
                    # Wait for next check
                    await asyncio.sleep(config.health_check_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error monitoring service {service_name}: {str(e)}")
                    await asyncio.sleep(config.health_check_interval)
        
        # Create and store monitoring task
        task = asyncio.create_task(monitor())
        self.monitoring_tasks[service_name] = task
        
        logger.info(f"Started monitoring service: {service_name}")
    
    async def _check_health(self, service_name: str) -> HealthCheck:
        """
        Perform health check on a service
        
        Args:
            service_name: Name of service to check
            
        Returns:
            HealthCheck result
        """
        config = self.services[service_name]
        start_time = datetime.now()
        
        try:
            # In production, this would make actual health check requests
            # For now, simulate health check
            await asyncio.sleep(0.1)
            
            # Simulate 95% healthy rate
            import random
            is_healthy = random.random() < 0.95
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if is_healthy:
                status = ServiceStatus.HEALTHY
                error = None
            else:
                status = ServiceStatus.UNHEALTHY
                error = "Simulated health check failure"
            
            health = HealthCheck(
                service_name=service_name,
                status=status,
                response_time=response_time,
                checked_at=datetime.now(),
                error=error,
                metrics={
                    "cpu_usage": random.uniform(10, 90),
                    "memory_usage": random.uniform(20, 80),
                    "active_connections": random.randint(10, 100)
                }
            )
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {str(e)}")
            
            return HealthCheck(
                service_name=service_name,
                status=ServiceStatus.DOWN,
                response_time=0,
                checked_at=datetime.now(),
                error=str(e)
            )
    
    async def _handle_unhealthy_service(self, service_name: str, health: HealthCheck):
        """Handle unhealthy service"""
        config = self.services[service_name]
        
        # Check if we should restart
        if not self._should_restart(service_name):
            logger.warning(f"Service {service_name} is unhealthy but restart not attempted (cooldown or max attempts)")
            return
        
        # Attempt restart
        logger.warning(f"Service {service_name} is unhealthy, attempting restart")
        success = await self.restart_service(service_name)
        
        if success:
            logger.info(f"Service {service_name} restarted successfully")
        else:
            logger.error(f"Failed to restart service {service_name}")
    
    def _should_restart(self, service_name: str) -> bool:
        """Determine if service should be restarted"""
        config = self.services[service_name]
        restart_history = self.restart_history[service_name]
        
        # Check if we've exceeded max restart attempts
        recent_restarts = [
            r for r in restart_history
            if r > datetime.now() - timedelta(seconds=config.restart_cooldown)
        ]
        
        if len(recent_restarts) >= config.max_restart_attempts:
            logger.warning(f"Service {service_name} has reached max restart attempts")
            return False
        
        return True
    
    async def restart_service(self, service_name: str) -> bool:
        """
        Restart a service
        
        Args:
            service_name: Name of service to restart
            
        Returns:
            True if restart successful, False otherwise
        """
        if service_name not in self.services:
            logger.error(f"Service {service_name} not registered")
            return False
        
        config = self.services[service_name]
        
        try:
            # Update status
            if service_name in self.health_status:
                self.health_status[service_name].status = ServiceStatus.RESTARTING
            
            logger.info(f"Restarting service: {service_name}")
            
            # Stop service
            if config.stop_command:
                logger.info(f"Stopping service {service_name}")
                await self._execute_command(config.stop_command)
                await asyncio.sleep(2)
            
            # Start service
            if config.start_command:
                logger.info(f"Starting service {service_name}")
                await self._execute_command(config.start_command)
                await asyncio.sleep(5)
            elif config.restart_command:
                logger.info(f"Restarting service {service_name}")
                await self._execute_command(config.restart_command)
                await asyncio.sleep(5)
            
            # Verify service is healthy
            health = await self._check_health(service_name)
            
            if health.status == ServiceStatus.HEALTHY:
                # Record successful restart
                self.restart_history[service_name].append(datetime.now())
                self.statistics["total_restarts"] += 1
                self.statistics["successful_restarts"] += 1
                
                logger.info(f"Service {service_name} restarted successfully")
                return True
            else:
                logger.error(f"Service {service_name} still unhealthy after restart")
                self.statistics["total_restarts"] += 1
                self.statistics["failed_restarts"] += 1
                return False
                
        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {str(e)}")
            self.statistics["total_restarts"] += 1
            self.statistics["failed_restarts"] += 1
            return False
    
    async def _execute_command(self, command: str):
        """Execute a system command"""
        # In production, this would execute actual commands
        # For now, simulate execution
        logger.info(f"Executing command: {command}")
        await asyncio.sleep(1)
    
    async def stop_service(self, service_name: str) -> bool:
        """Stop a service"""
        if service_name not in self.services:
            return False
        
        config = self.services[service_name]
        
        try:
            if config.stop_command:
                await self._execute_command(config.stop_command)
                logger.info(f"Service {service_name} stopped")
                return True
            return False
        except Exception as e:
            logger.error(f"Error stopping service {service_name}: {str(e)}")
            return False
    
    async def start_service(self, service_name: str) -> bool:
        """Start a service"""
        if service_name not in self.services:
            return False
        
        config = self.services[service_name]
        
        try:
            if config.start_command:
                await self._execute_command(config.start_command)
                logger.info(f"Service {service_name} started")
                return True
            return False
        except Exception as e:
            logger.error(f"Error starting service {service_name}: {str(e)}")
            return False
    
    def get_service_status(self, service_name: str) -> Optional[HealthCheck]:
        """Get current health status of a service"""
        return self.health_status.get(service_name)
    
    def get_all_service_status(self) -> Dict[str, HealthCheck]:
        """Get health status of all services"""
        return self.health_status.copy()
    
    def get_service_health_history(self, service_name: str, limit: int = 100) -> List[HealthCheck]:
        """Get health check history for a service"""
        if service_name not in self.health_history:
            return []
        return self.health_history[service_name][-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service manager statistics"""
        # Count healthy/unhealthy services
        healthy = sum(1 for h in self.health_status.values() if h.status == ServiceStatus.HEALTHY)
        unhealthy = len(self.health_status) - healthy
        
        return {
            **self.statistics,
            "healthy_services": healthy,
            "unhealthy_services": unhealthy,
            "total_services": len(self.services),
            "monitoring_services": len(self.monitoring_tasks)
        }
    
    def get_restart_history(self, service_name: str) -> List[datetime]:
        """Get restart history for a service"""
        return self.restart_history.get(service_name, [])