"""
iTechSmart Analytics - Dashboard Builder
Create and manage custom analytics dashboards with widgets
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from enum import Enum
import json


class WidgetType(str, Enum):
    """Available widget types"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    TABLE = "table"
    METRIC_CARD = "metric_card"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    TREEMAP = "treemap"
    SANKEY = "sankey"


class AggregationType(str, Enum):
    """Data aggregation types"""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"


class DashboardBuilder:
    """Build and manage custom analytics dashboards"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_dashboard(
        self,
        name: str,
        description: str,
        user_id: int,
        layout: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new dashboard
        
        Args:
            name: Dashboard name
            description: Dashboard description
            user_id: Owner user ID
            layout: Optional layout configuration
        
        Returns:
            Created dashboard details
        """
        
        dashboard = {
            "id": self._generate_id(),
            "name": name,
            "description": description,
            "user_id": user_id,
            "layout": layout or self._default_layout(),
            "widgets": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_public": False,
            "tags": []
        }
        
        # In production, save to database
        
        return dashboard
    
    async def add_widget(
        self,
        dashboard_id: int,
        widget_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add widget to dashboard
        
        Args:
            dashboard_id: Dashboard ID
            widget_config: Widget configuration
        
        Returns:
            Created widget details
        """
        
        # Validate widget config
        self._validate_widget_config(widget_config)
        
        widget = {
            "id": self._generate_id(),
            "dashboard_id": dashboard_id,
            "type": widget_config["type"],
            "title": widget_config["title"],
            "data_source": widget_config["data_source"],
            "config": widget_config.get("config", {}),
            "position": widget_config.get("position", {"x": 0, "y": 0, "w": 6, "h": 4}),
            "refresh_interval": widget_config.get("refresh_interval", 60),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return widget
    
    async def update_widget(
        self,
        widget_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update widget configuration
        
        Args:
            widget_id: Widget ID
            updates: Update data
        
        Returns:
            Updated widget details
        """
        
        # In production, fetch from database and update
        widget = {
            "id": widget_id,
            "updated_at": datetime.utcnow().isoformat()
        }
        widget.update(updates)
        
        return widget
    
    async def remove_widget(
        self,
        dashboard_id: int,
        widget_id: int
    ) -> Dict[str, str]:
        """
        Remove widget from dashboard
        
        Args:
            dashboard_id: Dashboard ID
            widget_id: Widget ID
        
        Returns:
            Success message
        """
        
        # In production, delete from database
        
        return {
            "status": "success",
            "message": f"Widget {widget_id} removed from dashboard {dashboard_id}"
        }
    
    async def get_dashboard(
        self,
        dashboard_id: int,
        include_data: bool = False
    ) -> Dict[str, Any]:
        """
        Get dashboard details
        
        Args:
            dashboard_id: Dashboard ID
            include_data: Whether to include widget data
        
        Returns:
            Dashboard details with widgets
        """
        
        # In production, fetch from database
        dashboard = {
            "id": dashboard_id,
            "name": "Sample Dashboard",
            "description": "Analytics dashboard",
            "widgets": []
        }
        
        if include_data:
            # Fetch data for each widget
            for widget in dashboard["widgets"]:
                widget["data"] = await self._fetch_widget_data(widget)
        
        return dashboard
    
    async def list_dashboards(
        self,
        user_id: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List dashboards
        
        Args:
            user_id: Filter by user ID
            tags: Filter by tags
        
        Returns:
            List of dashboards
        """
        
        # In production, query database with filters
        dashboards = []
        
        return dashboards
    
    async def duplicate_dashboard(
        self,
        dashboard_id: int,
        new_name: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Duplicate existing dashboard
        
        Args:
            dashboard_id: Source dashboard ID
            new_name: Name for duplicated dashboard
            user_id: Owner user ID
        
        Returns:
            Duplicated dashboard details
        """
        
        # Get source dashboard
        source = await self.get_dashboard(dashboard_id)
        
        # Create duplicate
        duplicate = await self.create_dashboard(
            name=new_name,
            description=f"Copy of {source['name']}",
            user_id=user_id,
            layout=source.get("layout")
        )
        
        # Copy widgets
        for widget in source.get("widgets", []):
            widget_config = {
                "type": widget["type"],
                "title": widget["title"],
                "data_source": widget["data_source"],
                "config": widget.get("config"),
                "position": widget.get("position")
            }
            await self.add_widget(duplicate["id"], widget_config)
        
        return duplicate
    
    async def export_dashboard(
        self,
        dashboard_id: int,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export dashboard configuration
        
        Args:
            dashboard_id: Dashboard ID
            format: Export format (json, yaml)
        
        Returns:
            Exported dashboard data
        """
        
        dashboard = await self.get_dashboard(dashboard_id, include_data=False)
        
        if format == "json":
            return {
                "format": "json",
                "data": json.dumps(dashboard, indent=2)
            }
        
        return dashboard
    
    async def import_dashboard(
        self,
        dashboard_data: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Import dashboard from configuration
        
        Args:
            dashboard_data: Dashboard configuration
            user_id: Owner user ID
        
        Returns:
            Imported dashboard details
        """
        
        # Create dashboard
        dashboard = await self.create_dashboard(
            name=dashboard_data["name"],
            description=dashboard_data.get("description", ""),
            user_id=user_id,
            layout=dashboard_data.get("layout")
        )
        
        # Import widgets
        for widget_data in dashboard_data.get("widgets", []):
            await self.add_widget(dashboard["id"], widget_data)
        
        return dashboard
    
    async def share_dashboard(
        self,
        dashboard_id: int,
        share_with: List[int],
        permissions: str = "view"
    ) -> Dict[str, Any]:
        """
        Share dashboard with users
        
        Args:
            dashboard_id: Dashboard ID
            share_with: List of user IDs to share with
            permissions: Permission level (view, edit)
        
        Returns:
            Share details
        """
        
        shares = []
        for user_id in share_with:
            shares.append({
                "dashboard_id": dashboard_id,
                "user_id": user_id,
                "permissions": permissions,
                "shared_at": datetime.utcnow().isoformat()
            })
        
        return {
            "dashboard_id": dashboard_id,
            "shares": shares,
            "total_shares": len(shares)
        }
    
    # Widget Templates
    
    async def create_metric_card(
        self,
        title: str,
        metric: str,
        data_source: str,
        comparison: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create metric card widget configuration"""
        
        return {
            "type": WidgetType.METRIC_CARD,
            "title": title,
            "data_source": data_source,
            "config": {
                "metric": metric,
                "comparison": comparison,
                "format": "number",
                "show_trend": True
            }
        }
    
    async def create_line_chart(
        self,
        title: str,
        metrics: List[str],
        data_source: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """Create line chart widget configuration"""
        
        return {
            "type": WidgetType.LINE_CHART,
            "title": title,
            "data_source": data_source,
            "config": {
                "metrics": metrics,
                "time_range": time_range,
                "show_legend": True,
                "show_grid": True
            }
        }
    
    async def create_bar_chart(
        self,
        title: str,
        metric: str,
        dimension: str,
        data_source: str
    ) -> Dict[str, Any]:
        """Create bar chart widget configuration"""
        
        return {
            "type": WidgetType.BAR_CHART,
            "title": title,
            "data_source": data_source,
            "config": {
                "metric": metric,
                "dimension": dimension,
                "orientation": "vertical",
                "show_values": True
            }
        }
    
    async def create_pie_chart(
        self,
        title: str,
        metric: str,
        dimension: str,
        data_source: str
    ) -> Dict[str, Any]:
        """Create pie chart widget configuration"""
        
        return {
            "type": WidgetType.PIE_CHART,
            "title": title,
            "data_source": data_source,
            "config": {
                "metric": metric,
                "dimension": dimension,
                "show_labels": True,
                "show_percentages": True
            }
        }
    
    # Helper methods
    
    def _generate_id(self) -> int:
        """Generate unique ID"""
        import random
        return random.randint(1000, 9999)
    
    def _default_layout(self) -> Dict[str, Any]:
        """Get default dashboard layout"""
        
        return {
            "type": "grid",
            "columns": 12,
            "row_height": 80,
            "margin": [10, 10],
            "container_padding": [10, 10]
        }
    
    def _validate_widget_config(self, config: Dict[str, Any]):
        """Validate widget configuration"""
        
        required_fields = ["type", "title", "data_source"]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        if config["type"] not in [t.value for t in WidgetType]:
            raise ValueError(f"Invalid widget type: {config['type']}")
    
    async def _fetch_widget_data(self, widget: Dict[str, Any]) -> Any:
        """Fetch data for widget"""
        
        # In production, fetch from data source
        return {
            "values": [],
            "timestamp": datetime.utcnow().isoformat()
        }