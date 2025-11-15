"""
Port Manager Integration for iTechSmart MDM Deployment Agent

Provides integration with iTechSmart Port Manager for port conflict detection,
dynamic port assignment, and port availability checks.
"""

import logging
from typing import Optional, Dict, Any, List
import aiohttp

logger = logging.getLogger(__name__)


class PortManagerIntegration:
    """
    Integration client for iTechSmart Port Manager
    
    Features:
    - Port conflict detection
    - Dynamic port assignment
    - Port availability checks
    - Port reservation
    """
    
    def __init__(
        self,
        port_manager_url: str = "http://localhost:8100"
    ):
        """
        Initialize Port Manager Integration
        
        Args:
            port_manager_url: URL of Port Manager service
        """
        self.port_manager_url = port_manager_url
        
        logger.info("Port Manager Integration initialized")
    
    async def check_port_available(self, port: int) -> bool:
        """
        Check if a port is available
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.port_manager_url}/api/ports/{port}/available",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("available", False)
                    else:
                        return False
                        
        except Exception as e:
            logger.error(f"Error checking port availability: {e}")
            return False
    
    async def assign_port(
        self,
        service_name: str,
        preferred_port: Optional[int] = None
    ) -> Optional[int]:
        """
        Assign a port for a service
        
        Args:
            service_name: Name of the service
            preferred_port: Preferred port number (optional)
            
        Returns:
            Assigned port number or None if assignment failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "service_name": service_name,
                    "preferred_port": preferred_port
                }
                
                async with session.post(
                    f"{self.port_manager_url}/api/ports/assign",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        assigned_port = result.get("port")
                        logger.info(f"Port {assigned_port} assigned to {service_name}")
                        return assigned_port
                    else:
                        logger.error(f"Failed to assign port: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error assigning port: {e}")
            return None
    
    async def release_port(self, port: int, service_name: str) -> bool:
        """
        Release a port
        
        Args:
            port: Port number to release
            service_name: Name of the service
            
        Returns:
            True if release successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "service_name": service_name
                }
                
                async with session.delete(
                    f"{self.port_manager_url}/api/ports/{port}",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Port {port} released by {service_name}")
                        return True
                    else:
                        logger.error(f"Failed to release port: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error releasing port: {e}")
            return False
    
    async def get_service_port(self, service_name: str) -> Optional[int]:
        """
        Get the port assigned to a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Port number or None if not found
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.port_manager_url}/api/services/{service_name}/port",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("port")
                    else:
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting service port: {e}")
            return None
    
    async def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        Detect port conflicts
        
        Returns:
            List of port conflicts
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.port_manager_url}/api/ports/conflicts",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("conflicts", [])
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return []
    
    async def resolve_conflict(
        self,
        service_name: str,
        current_port: int
    ) -> Optional[int]:
        """
        Resolve a port conflict by assigning a new port
        
        Args:
            service_name: Name of the service
            current_port: Current conflicting port
            
        Returns:
            New port number or None if resolution failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "service_name": service_name,
                    "current_port": current_port
                }
                
                async with session.post(
                    f"{self.port_manager_url}/api/ports/resolve-conflict",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        new_port = result.get("new_port")
                        logger.info(f"Conflict resolved: {service_name} moved from {current_port} to {new_port}")
                        return new_port
                    else:
                        logger.error(f"Failed to resolve conflict: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return None
    
    async def get_available_ports(self, count: int = 1) -> List[int]:
        """
        Get a list of available ports
        
        Args:
            count: Number of ports to get
            
        Returns:
            List of available port numbers
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.port_manager_url}/api/ports/available?count={count}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("ports", [])
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting available ports: {e}")
            return []
