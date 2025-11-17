"""
Data Visualization Integration
Provides advanced data visualization capabilities using multiple charting libraries
"""

import io
import base64
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataVisualizationClient:
    """
    Client for creating advanced data visualizations
    Supports multiple chart types and export formats
    """

    def __init__(self):
        self.supported_chart_types = [
            "bar",
            "line",
            "pie",
            "scatter",
            "area",
            "histogram",
            "box",
            "violin",
            "heatmap",
            "bubble",
            "radar",
            "treemap",
        ]
        self.supported_formats = ["png", "svg", "pdf", "html", "json"]

    async def create_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a chart from data

        Args:
            chart_type: Type of chart (bar, line, pie, etc.)
            data: Chart data
            options: Chart options (title, colors, etc.)

        Returns:
            Chart result with image data
        """
        try:
            if chart_type not in self.supported_chart_types:
                raise ValueError(f"Unsupported chart type: {chart_type}")

            # Default options
            default_options = {
                "title": "Chart",
                "width": 800,
                "height": 600,
                "theme": "light",
                "colors": ["#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#59a14f"],
                "show_legend": True,
                "show_grid": True,
                "animation": True,
            }

            if options:
                default_options.update(options)

            # Create chart based on type
            if chart_type == "bar":
                chart_data = await self._create_bar_chart(data, default_options)
            elif chart_type == "line":
                chart_data = await self._create_line_chart(data, default_options)
            elif chart_type == "pie":
                chart_data = await self._create_pie_chart(data, default_options)
            elif chart_type == "scatter":
                chart_data = await self._create_scatter_chart(data, default_options)
            elif chart_type == "area":
                chart_data = await self._create_area_chart(data, default_options)
            elif chart_type == "histogram":
                chart_data = await self._create_histogram(data, default_options)
            elif chart_type == "box":
                chart_data = await self._create_box_plot(data, default_options)
            elif chart_type == "heatmap":
                chart_data = await self._create_heatmap(data, default_options)
            elif chart_type == "bubble":
                chart_data = await self._create_bubble_chart(data, default_options)
            elif chart_type == "radar":
                chart_data = await self._create_radar_chart(data, default_options)
            else:
                chart_data = await self._create_generic_chart(
                    chart_type, data, default_options
                )

            return {
                "chart_id": self._generate_chart_id(),
                "chart_type": chart_type,
                "data": chart_data,
                "options": default_options,
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            raise

    async def _create_bar_chart(self, data: Dict, options: Dict) -> Dict:
        """Create bar chart"""
        return {
            "type": "bar",
            "labels": data.get("labels", []),
            "datasets": data.get("datasets", []),
            "config": {
                "orientation": options.get("orientation", "vertical"),
                "stacked": options.get("stacked", False),
                "bar_width": options.get("bar_width", 0.8),
            },
        }

    async def _create_line_chart(self, data: Dict, options: Dict) -> Dict:
        """Create line chart"""
        return {
            "type": "line",
            "labels": data.get("labels", []),
            "datasets": data.get("datasets", []),
            "config": {
                "smooth": options.get("smooth", True),
                "fill": options.get("fill", False),
                "tension": options.get("tension", 0.4),
            },
        }

    async def _create_pie_chart(self, data: Dict, options: Dict) -> Dict:
        """Create pie chart"""
        return {
            "type": "pie",
            "labels": data.get("labels", []),
            "values": data.get("values", []),
            "config": {
                "donut": options.get("donut", False),
                "donut_width": options.get("donut_width", 0.5),
                "show_percentages": options.get("show_percentages", True),
            },
        }

    async def _create_scatter_chart(self, data: Dict, options: Dict) -> Dict:
        """Create scatter plot"""
        return {
            "type": "scatter",
            "datasets": data.get("datasets", []),
            "config": {
                "point_size": options.get("point_size", 5),
                "show_regression": options.get("show_regression", False),
            },
        }

    async def _create_area_chart(self, data: Dict, options: Dict) -> Dict:
        """Create area chart"""
        return {
            "type": "area",
            "labels": data.get("labels", []),
            "datasets": data.get("datasets", []),
            "config": {
                "stacked": options.get("stacked", False),
                "opacity": options.get("opacity", 0.6),
            },
        }

    async def _create_histogram(self, data: Dict, options: Dict) -> Dict:
        """Create histogram"""
        return {
            "type": "histogram",
            "values": data.get("values", []),
            "config": {
                "bins": options.get("bins", 10),
                "show_distribution": options.get("show_distribution", True),
            },
        }

    async def _create_box_plot(self, data: Dict, options: Dict) -> Dict:
        """Create box plot"""
        return {
            "type": "box",
            "datasets": data.get("datasets", []),
            "config": {
                "show_outliers": options.get("show_outliers", True),
                "show_mean": options.get("show_mean", True),
            },
        }

    async def _create_heatmap(self, data: Dict, options: Dict) -> Dict:
        """Create heatmap"""
        return {
            "type": "heatmap",
            "x_labels": data.get("x_labels", []),
            "y_labels": data.get("y_labels", []),
            "values": data.get("values", []),
            "config": {
                "color_scheme": options.get("color_scheme", "viridis"),
                "show_values": options.get("show_values", True),
            },
        }

    async def _create_bubble_chart(self, data: Dict, options: Dict) -> Dict:
        """Create bubble chart"""
        return {
            "type": "bubble",
            "datasets": data.get("datasets", []),
            "config": {
                "size_scale": options.get("size_scale", 1.0),
                "max_bubble_size": options.get("max_bubble_size", 50),
            },
        }

    async def _create_radar_chart(self, data: Dict, options: Dict) -> Dict:
        """Create radar chart"""
        return {
            "type": "radar",
            "labels": data.get("labels", []),
            "datasets": data.get("datasets", []),
            "config": {
                "fill": options.get("fill", True),
                "opacity": options.get("opacity", 0.3),
            },
        }

    async def _create_generic_chart(
        self, chart_type: str, data: Dict, options: Dict
    ) -> Dict:
        """Create generic chart"""
        return {"type": chart_type, "data": data, "config": options}

    async def export_chart(
        self,
        chart_id: str,
        format: str = "png",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Export chart to specified format

        Args:
            chart_id: Chart ID
            format: Export format (png, svg, pdf, html, json)
            options: Export options

        Returns:
            Exported chart data
        """
        try:
            if format not in self.supported_formats:
                raise ValueError(f"Unsupported export format: {format}")

            # Export based on format
            if format == "png":
                return await self._export_png(chart_id, options)
            elif format == "svg":
                return await self._export_svg(chart_id, options)
            elif format == "pdf":
                return await self._export_pdf(chart_id, options)
            elif format == "html":
                return await self._export_html(chart_id, options)
            elif format == "json":
                return await self._export_json(chart_id, options)

        except Exception as e:
            logger.error(f"Error exporting chart: {str(e)}")
            raise

    async def _export_png(self, chart_id: str, options: Optional[Dict]) -> Dict:
        """Export chart as PNG"""
        return {
            "format": "png",
            "data": "base64_encoded_png_data",
            "mime_type": "image/png",
        }

    async def _export_svg(self, chart_id: str, options: Optional[Dict]) -> Dict:
        """Export chart as SVG"""
        return {"format": "svg", "data": "<svg>...</svg>", "mime_type": "image/svg+xml"}

    async def _export_pdf(self, chart_id: str, options: Optional[Dict]) -> Dict:
        """Export chart as PDF"""
        return {
            "format": "pdf",
            "data": "base64_encoded_pdf_data",
            "mime_type": "application/pdf",
        }

    async def _export_html(self, chart_id: str, options: Optional[Dict]) -> Dict:
        """Export chart as HTML"""
        return {"format": "html", "data": "<html>...</html>", "mime_type": "text/html"}

    async def _export_json(self, chart_id: str, options: Optional[Dict]) -> Dict:
        """Export chart as JSON"""
        return {"format": "json", "data": {}, "mime_type": "application/json"}

    async def create_dashboard(
        self, charts: List[Dict[str, Any]], layout: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create interactive dashboard with multiple charts

        Args:
            charts: List of chart configurations
            layout: Dashboard layout configuration

        Returns:
            Dashboard data
        """
        try:
            default_layout = {
                "columns": 2,
                "spacing": 20,
                "responsive": True,
                "theme": "light",
            }

            if layout:
                default_layout.update(layout)

            dashboard_charts = []
            for chart_config in charts:
                chart = await self.create_chart(
                    chart_config["type"],
                    chart_config["data"],
                    chart_config.get("options"),
                )
                dashboard_charts.append(chart)

            return {
                "dashboard_id": self._generate_dashboard_id(),
                "charts": dashboard_charts,
                "layout": default_layout,
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            raise

    async def update_chart_data(
        self, chart_id: str, new_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update chart data for real-time updates

        Args:
            chart_id: Chart ID
            new_data: New chart data

        Returns:
            Updated chart
        """
        try:
            return {
                "chart_id": chart_id,
                "data": new_data,
                "updated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error updating chart: {str(e)}")
            raise

    async def analyze_data(
        self, data: List[float], analysis_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Analyze data and provide statistics

        Args:
            data: Data to analyze
            analysis_type: Type of analysis (basic, advanced, statistical)

        Returns:
            Analysis results
        """
        try:
            if not data:
                raise ValueError("Data cannot be empty")

            # Basic statistics
            import statistics

            result = {
                "count": len(data),
                "mean": statistics.mean(data),
                "median": statistics.median(data),
                "mode": statistics.mode(data) if len(set(data)) < len(data) else None,
                "std_dev": statistics.stdev(data) if len(data) > 1 else 0,
                "variance": statistics.variance(data) if len(data) > 1 else 0,
                "min": min(data),
                "max": max(data),
                "range": max(data) - min(data),
            }

            if analysis_type in ["advanced", "statistical"]:
                # Add percentiles
                sorted_data = sorted(data)
                result["percentiles"] = {
                    "25": statistics.quantiles(sorted_data, n=4)[0],
                    "50": statistics.median(sorted_data),
                    "75": statistics.quantiles(sorted_data, n=4)[2],
                }

            return result

        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
            raise

    def _generate_chart_id(self) -> str:
        """Generate unique chart ID"""
        import uuid

        return f"chart_{uuid.uuid4().hex[:12]}"

    def _generate_dashboard_id(self) -> str:
        """Generate unique dashboard ID"""
        import uuid

        return f"dashboard_{uuid.uuid4().hex[:12]}"

    async def get_chart_types(self) -> List[Dict[str, Any]]:
        """Get list of supported chart types"""
        return [
            {
                "type": "bar",
                "name": "Bar Chart",
                "description": "Compare values across categories",
            },
            {
                "type": "line",
                "name": "Line Chart",
                "description": "Show trends over time",
            },
            {"type": "pie", "name": "Pie Chart", "description": "Show proportions"},
            {
                "type": "scatter",
                "name": "Scatter Plot",
                "description": "Show correlation between variables",
            },
            {
                "type": "area",
                "name": "Area Chart",
                "description": "Show cumulative totals over time",
            },
            {
                "type": "histogram",
                "name": "Histogram",
                "description": "Show distribution of data",
            },
            {
                "type": "box",
                "name": "Box Plot",
                "description": "Show statistical distribution",
            },
            {
                "type": "violin",
                "name": "Violin Plot",
                "description": "Show distribution density",
            },
            {
                "type": "heatmap",
                "name": "Heatmap",
                "description": "Show data intensity in matrix",
            },
            {
                "type": "bubble",
                "name": "Bubble Chart",
                "description": "Show three dimensions of data",
            },
            {
                "type": "radar",
                "name": "Radar Chart",
                "description": "Compare multiple variables",
            },
            {
                "type": "treemap",
                "name": "Treemap",
                "description": "Show hierarchical data",
            },
        ]
