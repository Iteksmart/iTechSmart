"""
Grafana Integration - The Open Observability Platform
Create dashboards, visualize metrics, and manage alerts
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import aiohttp
import json
from datetime import datetime, timedelta

from ..core.models import Alert, AlertSource, SeverityLevel


class GrafanaIntegration:
    """Integration with Grafana for visualization and alerting"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    async def create_dashboard(
        self,
        title: str,
        panels: List[Dict[str, Any]],
        folder_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a Grafana dashboard"""
        
        dashboard = {
            'dashboard': {
                'title': title,
                'panels': panels,
                'schemaVersion': 16,
                'version': 0,
                'refresh': '30s'
            },
            'folderId': folder_id,
            'overwrite': False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/dashboards/db",
                    headers=self.headers,
                    json=dashboard
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"Dashboard created: {title}")
                        return data
                    else:
                        error = await response.text()
                        self.logger.error(f"Failed to create dashboard: {error}")
                        return {}
        
        except Exception as e:
            self.logger.error(f"Dashboard creation error: {e}")
            return {}
    
    async def create_itechsmart_dashboard(self) -> Dict[str, Any]:
        """Create iTechSmart Supreme monitoring dashboard"""
        
        panels = [
            {
                'id': 1,
                'title': 'Active Alerts',
                'type': 'stat',
                'gridPos': {'x': 0, 'y': 0, 'w': 6, 'h': 4},
                'targets': [{
                    'expr': 'itechsmart_active_alerts',
                    'refId': 'A'
                }]
            }
        ]
        
        return await self.create_dashboard(
            title='iTechSmart Supreme - Overview',
            panels=panels
        )
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get Grafana alerts"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/alerts",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Failed to get alerts: {response.status}")
                        return []
        
        except Exception as e:
            self.logger.error(f"Error getting alerts: {e}")
            return []