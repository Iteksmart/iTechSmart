"""
iTechSmart Analytics - Enterprise Integration
Integration with iTechSmart Enterprise hub for seamless data flow
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
import asyncio
import httpx


class EnterpriseIntegration:
    """Integration with iTechSmart Enterprise hub"""
    
    def __init__(self, db: Session, enterprise_url: str, api_key: str):
        self.db = db
        self.enterprise_url = enterprise_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=enterprise_url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
    
    async def register_with_enterprise(self) -> Dict[str, Any]:
        """
        Register Analytics service with Enterprise hub
        
        Returns:
            Registration result
        """
        
        registration_data = {
            "name": "iTechSmart Analytics",
            "service_type": "analytics",
            "version": "1.0.0",
            "endpoint_url": "http://analytics:8000",
            "capabilities": [
                "forecasting",
                "anomaly_detection",
                "trend_analysis",
                "reporting",
                "dashboards"
            ],
            "health_check_url": "/health",
            "metadata": {
                "description": "Advanced analytics and reporting platform",
                "features": [
                    "ML-powered forecasting",
                    "Real-time anomaly detection",
                    "Custom dashboards",
                    "Automated reports"
                ]
            }
        }
        
        try:
            response = await self.client.post(
                "/api/integration/services",
                json=registration_data
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "service_id": response.json()["id"],
                "registered_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sync_data_from_enterprise(
        self,
        service_name: str,
        metrics: List[str],
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Sync data from Enterprise hub
        
        Args:
            service_name: Source service name
            metrics: Metrics to sync
            date_range: Optional date range
        
        Returns:
            Sync result
        """
        
        try:
            response = await self.client.post(
                "/api/integration/sync",
                json={
                    "source_service": service_name,
                    "target_service": "iTechSmart Analytics",
                    "data_type": "metrics",
                    "metrics": metrics,
                    "date_range": date_range
                }
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "records_synced": response.json()["records_synced"],
                "synced_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def publish_analytics_results(
        self,
        analysis_type: str,
        results: Dict[str, Any],
        target_services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Publish analytics results to Enterprise hub
        
        Args:
            analysis_type: Type of analysis
            results: Analysis results
            target_services: Optional list of target services
        
        Returns:
            Publish result
        """
        
        try:
            response = await self.client.post(
                "/api/integration/events",
                json={
                    "service_name": "iTechSmart Analytics",
                    "event_type": f"analytics_{analysis_type}",
                    "event_data": results,
                    "target_services": target_services
                }
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "event_id": response.json()["id"],
                "published_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_enterprise_metrics(
        self,
        service_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get metrics from Enterprise hub
        
        Args:
            service_name: Optional service filter
        
        Returns:
            Enterprise metrics
        """
        
        try:
            params = {}
            if service_name:
                params["service"] = service_name
            
            response = await self.client.get(
                "/api/dashboard/metrics/realtime",
                params=params
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def create_cross_product_dashboard(
        self,
        name: str,
        services: List[str],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """
        Create dashboard combining data from multiple services
        
        Args:
            name: Dashboard name
            services: List of service names
            metrics: List of metrics
        
        Returns:
            Created dashboard
        """
        
        # Fetch data from each service
        dashboard_data = {
            "name": name,
            "services": services,
            "metrics": {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        for service in services:
            service_data = await self.sync_data_from_enterprise(
                service,
                metrics
            )
            dashboard_data["metrics"][service] = service_data
        
        return dashboard_data
    
    async def setup_automated_sync(
        self,
        service_name: str,
        metrics: List[str],
        interval_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        Setup automated data sync from Enterprise
        
        Args:
            service_name: Source service name
            metrics: Metrics to sync
            interval_minutes: Sync interval in minutes
        
        Returns:
            Sync configuration
        """
        
        sync_config = {
            "id": self._generate_id(),
            "service_name": service_name,
            "metrics": metrics,
            "interval_minutes": interval_minutes,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "last_sync": None
        }
        
        # Start sync task
        asyncio.create_task(
            self._automated_sync_loop(sync_config)
        )
        
        return sync_config
    
    async def send_alert_to_enterprise(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send alert to Enterprise hub
        
        Args:
            alert_type: Type of alert
            severity: Alert severity
            message: Alert message
            details: Optional alert details
        
        Returns:
            Alert result
        """
        
        try:
            response = await self.client.post(
                "/api/integration/events",
                json={
                    "service_name": "iTechSmart Analytics",
                    "event_type": f"alert_{alert_type}",
                    "event_data": {
                        "severity": severity,
                        "message": message,
                        "details": details,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "alert_id": response.json()["id"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_service_health(
        self,
        service_name: str
    ) -> Dict[str, Any]:
        """
        Get health status of a service from Enterprise
        
        Args:
            service_name: Service name
        
        Returns:
            Service health status
        """
        
        try:
            response = await self.client.get(
                f"/api/integration/services/{service_name}/health"
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def trigger_ninja_analysis(
        self,
        analysis_type: str,
        target_service: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger Ninja to perform analysis or fixes
        
        Args:
            analysis_type: Type of analysis
            target_service: Target service name
            parameters: Analysis parameters
        
        Returns:
            Trigger result
        """
        
        try:
            response = await self.client.post(
                "/api/suite-control/analyze",
                json={
                    "analysis_type": analysis_type,
                    "target_service": target_service,
                    "parameters": parameters,
                    "requested_by": "iTechSmart Analytics"
                }
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "task_id": response.json()["task_id"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # Private helper methods
    
    async def _automated_sync_loop(self, config: Dict[str, Any]):
        """Automated sync loop"""
        
        while config["status"] == "active":
            try:
                # Sync data
                result = await self.sync_data_from_enterprise(
                    config["service_name"],
                    config["metrics"]
                )
                
                config["last_sync"] = datetime.utcnow().isoformat()
                
                # Wait for next interval
                await asyncio.sleep(config["interval_minutes"] * 60)
                
            except Exception as e:
                print(f"Error in automated sync: {str(e)}")
                await asyncio.sleep(60)
    
    def _generate_id(self) -> int:
        """Generate unique ID"""
        import random
        return random.randint(1000, 9999)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()