"""
Suite Communicator - Handles communication with all iTechSmart Suite products
"""

import asyncio
import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SuiteCommunicator:
    """
    Communicates with all iTechSmart Suite products to update port configurations
    """
    
    def __init__(self, port_manager):
        self.port_manager = port_manager
        self.client = httpx.AsyncClient(timeout=30.0)
        self.service_status: Dict[str, Dict] = {}
        self.hub_url = "http://itechsmart-enterprise:8001"
        self.ninja_url = "http://itechsmart-ninja:8002"
        
        # Service endpoints for port updates
        self.service_endpoints = {
            "itechsmart-enterprise": "http://itechsmart-enterprise:{port}/api/config/update-port",
            "itechsmart-ninja": "http://itechsmart-ninja:{port}/api/config/update-port",
            "itechsmart-analytics": "http://itechsmart-analytics:{port}/api/config/update-port",
            "itechsmart-supreme": "http://itechsmart-supreme:{port}/api/config/update-port",
            "itechsmart-hl7": "http://itechsmart-hl7:{port}/api/config/update-port",
            "prooflink-ai": "http://prooflink-ai:{port}/api/config/update-port",
            "passport": "http://passport:{port}/api/config/update-port",
            "impactos": "http://impactos:{port}/api/config/update-port",
            "legalai-pro": "http://legalai-pro:{port}/api/config/update-port",
            "itechsmart-dataflow": "http://itechsmart-dataflow:{port}/api/config/update-port",
            "itechsmart-pulse": "http://itechsmart-pulse:{port}/api/config/update-port",
            "itechsmart-connect": "http://itechsmart-connect:{port}/api/config/update-port",
            "itechsmart-vault": "http://itechsmart-vault:{port}/api/config/update-port",
            "itechsmart-notify": "http://itechsmart-notify:{port}/api/config/update-port",
            "itechsmart-ledger": "http://itechsmart-ledger:{port}/api/config/update-port",
            "itechsmart-copilot": "http://itechsmart-copilot:{port}/api/config/update-port",
            "itechsmart-shield": "http://itechsmart-shield:{port}/api/config/update-port",
            "itechsmart-workflow": "http://itechsmart-workflow:{port}/api/config/update-port",
            "itechsmart-marketplace": "http://itechsmart-marketplace:{port}/api/config/update-port",
            "itechsmart-cloud": "http://itechsmart-cloud:{port}/api/config/update-port",
            "itechsmart-devops": "http://itechsmart-devops:{port}/api/config/update-port",
            "itechsmart-mobile": "http://itechsmart-mobile:{port}/api/config/update-port",
            "itechsmart-ai": "http://itechsmart-ai:{port}/api/config/update-port",
            "itechsmart-compliance": "http://itechsmart-compliance:{port}/api/config/update-port",
            "itechsmart-data-platform": "http://itechsmart-data-platform:{port}/api/config/update-port",
            "itechsmart-customer-success": "http://itechsmart-customer-success:{port}/api/config/update-port",
        }
    
    async def initialize(self):
        """Initialize suite communicator"""
        logger.info("Initializing Suite Communicator...")
        await self.discover_services()
        logger.info("Suite Communicator initialized")
    
    async def discover_services(self) -> List[str]:
        """Discover all available services in the suite"""
        discovered = []
        
        # Try to discover via Enterprise Hub
        try:
            response = await self.client.get(f"{self.hub_url}/api/v1/services/discover")
            if response.status_code == 200:
                services = response.json()
                for service in services:
                    service_id = service.get('service_id')
                    if service_id:
                        discovered.append(service_id)
                        self.service_status[service_id] = {
                            'status': 'discovered',
                            'last_seen': datetime.utcnow().isoformat()
                        }
        except Exception as e:
            logger.warning(f"Could not discover services via Hub: {e}")
        
        # Fallback: check all known services
        if not discovered:
            for service_id in self.service_endpoints.keys():
                port = await self.port_manager.get_service_port(service_id)
                if port and await self.check_service_health(service_id, port):
                    discovered.append(service_id)
                    self.service_status[service_id] = {
                        'status': 'available',
                        'last_seen': datetime.utcnow().isoformat()
                    }
        
        logger.info(f"Discovered {len(discovered)} services")
        return discovered
    
    async def check_service_health(self, service_id: str, port: int) -> bool:
        """Check if a service is healthy and responding"""
        try:
            url = f"http://{service_id}:{port}/health"
            response = await self.client.get(url, timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
    
    async def update_service_port(self, service_id: str, new_port: int) -> Dict[str, Any]:
        """
        Update port configuration for a specific service
        Returns: {success, message, details}
        """
        try:
            # Get current port
            current_port = await self.port_manager.get_service_port(service_id)
            if not current_port:
                return {
                    'success': False,
                    'message': f"Service {service_id} not found in port assignments",
                    'service_id': service_id
                }
            
            # Get service endpoint
            endpoint_template = self.service_endpoints.get(service_id)
            if not endpoint_template:
                return {
                    'success': False,
                    'message': f"No endpoint configured for {service_id}",
                    'service_id': service_id
                }
            
            # Format endpoint with current port
            endpoint = endpoint_template.format(port=current_port)
            
            # Send port update request
            payload = {
                'new_port': new_port,
                'old_port': current_port,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'port-manager'
            }
            
            response = await self.client.post(endpoint, json=payload, timeout=10.0)
            
            if response.status_code == 200:
                # Update port manager
                success, port, message = await self.port_manager.assign_port(service_id, new_port, force=True)
                
                return {
                    'success': True,
                    'message': f"Successfully updated {service_id} to port {new_port}",
                    'service_id': service_id,
                    'old_port': current_port,
                    'new_port': new_port,
                    'response': response.json()
                }
            else:
                return {
                    'success': False,
                    'message': f"Service returned error: {response.status_code}",
                    'service_id': service_id,
                    'status_code': response.status_code
                }
        
        except httpx.TimeoutException:
            return {
                'success': False,
                'message': f"Timeout connecting to {service_id}",
                'service_id': service_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error updating {service_id}: {str(e)}",
                'service_id': service_id,
                'error': str(e)
            }
    
    async def update_multiple_services(self, updates: Dict[str, int]) -> List[Dict]:
        """
        Update ports for multiple services
        updates: {service_id: new_port}
        Returns: List of update results
        """
        results = []
        
        for service_id, new_port in updates.items():
            result = await self.update_service_port(service_id, new_port)
            results.append(result)
            
            # Small delay between updates
            await asyncio.sleep(0.5)
        
        return results
    
    async def broadcast_port_change(self, service_id: str, old_port: int, new_port: int):
        """Broadcast port change to Enterprise Hub and Ninja"""
        notification = {
            'event': 'port_changed',
            'service_id': service_id,
            'old_port': old_port,
            'new_port': new_port,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Notify Enterprise Hub
        try:
            await self.client.post(
                f"{self.hub_url}/api/v1/events/port-change",
                json=notification,
                timeout=5.0
            )
            logger.info(f"Notified Hub about port change for {service_id}")
        except Exception as e:
            logger.warning(f"Could not notify Hub: {e}")
        
        # Notify Ninja
        try:
            await self.client.post(
                f"{self.ninja_url}/api/v1/events/port-change",
                json=notification,
                timeout=5.0
            )
            logger.info(f"Notified Ninja about port change for {service_id}")
        except Exception as e:
            logger.warning(f"Could not notify Ninja: {e}")
    
    async def get_service_status(self, service_id: str) -> Dict:
        """Get current status of a service"""
        port = await self.port_manager.get_service_port(service_id)
        if not port:
            return {'status': 'unknown', 'message': 'Service not found'}
        
        is_healthy = await self.check_service_health(service_id, port)
        
        return {
            'service_id': service_id,
            'port': port,
            'status': 'healthy' if is_healthy else 'unhealthy',
            'last_checked': datetime.utcnow().isoformat()
        }
    
    async def get_all_service_status(self) -> List[Dict]:
        """Get status of all services"""
        statuses = []
        assignments = await self.port_manager.get_all_assignments()
        
        for service_id in assignments.keys():
            status = await self.get_service_status(service_id)
            statuses.append(status)
        
        return statuses
    
    async def restart_service(self, service_id: str) -> Dict:
        """Request service restart (via Hub or direct)"""
        try:
            port = await self.port_manager.get_service_port(service_id)
            if not port:
                return {'success': False, 'message': 'Service not found'}
            
            # Try via Hub first
            try:
                response = await self.client.post(
                    f"{self.hub_url}/api/v1/services/{service_id}/restart",
                    timeout=10.0
                )
                if response.status_code == 200:
                    return {'success': True, 'message': 'Restart requested via Hub'}
            except Exception:
                pass
            
            # Try direct endpoint
            endpoint = f"http://{service_id}:{port}/api/admin/restart"
            response = await self.client.post(endpoint, timeout=10.0)
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Restart requested directly'}
            else:
                return {'success': False, 'message': f'Restart failed: {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    async def validate_port_change(self, service_id: str, new_port: int) -> Dict:
        """Validate if a port change is safe"""
        # Check if port is available
        if not self.port_manager.is_port_available(new_port):
            return {
                'valid': False,
                'reason': f'Port {new_port} is already in use by system'
            }
        
        # Check if port is assigned to another service
        if self.port_manager.is_port_in_use(new_port):
            current_service = next((s for s, p in self.port_manager.port_assignments.items() 
                                   if p == new_port), None)
            return {
                'valid': False,
                'reason': f'Port {new_port} is assigned to {current_service}'
            }
        
        # Check if service exists
        current_port = await self.port_manager.get_service_port(service_id)
        if not current_port:
            return {
                'valid': False,
                'reason': f'Service {service_id} not found'
            }
        
        return {
            'valid': True,
            'current_port': current_port,
            'new_port': new_port
        }
    
    async def shutdown(self):
        """Shutdown suite communicator"""
        await self.client.aclose()
        logger.info("Suite Communicator shutdown complete")