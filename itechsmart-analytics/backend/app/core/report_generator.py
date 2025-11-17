"""
iTechSmart Analytics - Report Generator
Automated report generation with multiple formats and delivery options
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from enum import Enum
import pandas as pd
import json
from io import BytesIO
import base64


class ReportFormat(str, Enum):
    """Supported report formats"""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    JSON = "json"


class ReportFrequency(str, Enum):
    """Report generation frequency"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"


class DeliveryMethod(str, Enum):
    """Report delivery methods"""

    EMAIL = "email"
    DOWNLOAD = "download"
    API = "api"
    WEBHOOK = "webhook"
    STORAGE = "storage"


class ReportGenerator:
    """Generate and deliver analytics reports"""

    def __init__(self, db: Session):
        self.db = db
        self.templates = {}
        self.scheduled_reports = {}

    async def create_report(
        self,
        name: str,
        description: str,
        data_sources: List[int],
        metrics: List[str],
        format: ReportFormat = ReportFormat.PDF,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new report definition

        Args:
            name: Report name
            description: Report description
            data_sources: List of data source IDs
            metrics: List of metrics to include
            format: Output format
            template: Optional template name

        Returns:
            Created report details
        """

        report = {
            "id": self._generate_id(),
            "name": name,
            "description": description,
            "data_sources": data_sources,
            "metrics": metrics,
            "format": format.value,
            "template": template or "default",
            "created_at": datetime.utcnow().isoformat(),
            "last_generated": None,
            "generation_count": 0,
        }

        return report

    async def generate_report(
        self,
        report_id: int,
        date_range: Optional[Dict[str, str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a report

        Args:
            report_id: Report ID
            date_range: Optional date range filter
            filters: Optional additional filters

        Returns:
            Generated report details with data
        """

        start_time = datetime.utcnow()

        try:
            # Get report definition
            report = await self._get_report(report_id)

            # Fetch data
            data = await self._fetch_report_data(
                report["data_sources"], report["metrics"], date_range, filters
            )

            # Generate report content
            content = await self._generate_content(report, data, date_range)

            # Format report
            formatted_report = await self._format_report(
                report["format"], content, report["template"]
            )

            duration = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "report_id": report_id,
                "name": report["name"],
                "format": report["format"],
                "generated_at": datetime.utcnow().isoformat(),
                "duration_seconds": duration,
                "size_bytes": len(formatted_report["data"]),
                "data": formatted_report["data"],
                "download_url": formatted_report.get("download_url"),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def schedule_report(
        self,
        report_id: int,
        frequency: ReportFrequency,
        delivery_method: DeliveryMethod,
        delivery_config: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule automated report generation

        Args:
            report_id: Report ID
            frequency: Generation frequency
            delivery_method: How to deliver the report
            delivery_config: Delivery configuration
            filters: Optional filters

        Returns:
            Scheduled report details
        """

        schedule = {
            "id": self._generate_id(),
            "report_id": report_id,
            "frequency": frequency.value,
            "delivery_method": delivery_method.value,
            "delivery_config": delivery_config,
            "filters": filters or {},
            "status": "active",
            "next_run": self._calculate_next_run(frequency),
            "created_at": datetime.utcnow().isoformat(),
            "last_run": None,
            "run_count": 0,
        }

        self.scheduled_reports[schedule["id"]] = schedule

        return schedule

    async def deliver_report(
        self,
        report_data: Dict[str, Any],
        delivery_method: DeliveryMethod,
        delivery_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Deliver generated report

        Args:
            report_data: Generated report data
            delivery_method: Delivery method
            delivery_config: Delivery configuration

        Returns:
            Delivery result
        """

        try:
            if delivery_method == DeliveryMethod.EMAIL:
                result = await self._deliver_via_email(report_data, delivery_config)
            elif delivery_method == DeliveryMethod.WEBHOOK:
                result = await self._deliver_via_webhook(report_data, delivery_config)
            elif delivery_method == DeliveryMethod.STORAGE:
                result = await self._deliver_to_storage(report_data, delivery_config)
            else:
                result = {
                    "success": True,
                    "method": "download",
                    "message": "Report available for download",
                }

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_dashboard_report(
        self,
        dashboard_id: int,
        format: ReportFormat = ReportFormat.PDF,
        include_data: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate report from dashboard

        Args:
            dashboard_id: Dashboard ID
            format: Output format
            include_data: Whether to include raw data

        Returns:
            Generated dashboard report
        """

        # Get dashboard configuration
        dashboard = await self._get_dashboard(dashboard_id)

        # Generate report for each widget
        widget_reports = []
        for widget in dashboard.get("widgets", []):
            widget_data = await self._generate_widget_report(widget)
            widget_reports.append(widget_data)

        # Combine into single report
        report_content = {
            "dashboard_name": dashboard["name"],
            "generated_at": datetime.utcnow().isoformat(),
            "widgets": widget_reports,
        }

        # Format report
        formatted = await self._format_report(format.value, report_content, "dashboard")

        return {
            "success": True,
            "dashboard_id": dashboard_id,
            "format": format.value,
            "data": formatted["data"],
        }

    async def create_custom_report(
        self,
        title: str,
        sections: List[Dict[str, Any]],
        format: ReportFormat = ReportFormat.PDF,
    ) -> Dict[str, Any]:
        """
        Create custom report with multiple sections

        Args:
            title: Report title
            sections: List of report sections
            format: Output format

        Returns:
            Generated custom report
        """

        report_content = {
            "title": title,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": [],
        }

        # Generate each section
        for section in sections:
            section_data = await self._generate_section(section)
            report_content["sections"].append(section_data)

        # Format report
        formatted = await self._format_report(format.value, report_content, "custom")

        return {
            "success": True,
            "title": title,
            "format": format.value,
            "data": formatted["data"],
        }

    async def export_data(
        self,
        data_source_id: int,
        metrics: List[str],
        format: ReportFormat,
        date_range: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Export raw data

        Args:
            data_source_id: Data source ID
            metrics: Metrics to export
            format: Export format
            date_range: Optional date range

        Returns:
            Exported data
        """

        # Fetch data
        data = await self._fetch_report_data([data_source_id], metrics, date_range)

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Export based on format
        if format == ReportFormat.CSV:
            output = df.to_csv(index=False)
        elif format == ReportFormat.EXCEL:
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            output = base64.b64encode(buffer.getvalue()).decode()
        elif format == ReportFormat.JSON:
            output = df.to_json(orient="records")
        else:
            output = df.to_dict("records")

        return {
            "success": True,
            "format": format.value,
            "records": len(df),
            "data": output,
        }

    # Report Templates

    async def create_executive_summary(
        self, data_sources: List[int], date_range: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate executive summary report"""

        sections = [
            {
                "type": "overview",
                "title": "Executive Overview",
                "metrics": ["revenue", "users", "growth_rate"],
            },
            {"type": "trends", "title": "Key Trends", "metrics": ["revenue", "users"]},
            {"type": "insights", "title": "Key Insights", "auto_generate": True},
        ]

        return await self.create_custom_report(
            "Executive Summary", sections, ReportFormat.PDF
        )

    async def create_performance_report(
        self, data_sources: List[int], date_range: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate performance report"""

        sections = [
            {
                "type": "metrics",
                "title": "Performance Metrics",
                "metrics": ["response_time", "throughput", "error_rate"],
            },
            {
                "type": "comparison",
                "title": "Period Comparison",
                "compare_to": "previous_period",
            },
            {"type": "anomalies", "title": "Detected Anomalies", "auto_generate": True},
        ]

        return await self.create_custom_report(
            "Performance Report", sections, ReportFormat.PDF
        )

    # Private helper methods

    async def _get_report(self, report_id: int) -> Dict[str, Any]:
        """Get report definition"""
        # In production, fetch from database
        return {
            "id": report_id,
            "name": "Sample Report",
            "data_sources": [1],
            "metrics": ["revenue", "users"],
            "format": "pdf",
            "template": "default",
        }

    async def _fetch_report_data(
        self,
        data_sources: List[int],
        metrics: List[str],
        date_range: Optional[Dict[str, str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch data for report"""
        # In production, fetch from actual data sources
        return []

    async def _generate_content(
        self,
        report: Dict[str, Any],
        data: List[Dict[str, Any]],
        date_range: Optional[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Generate report content"""

        df = pd.DataFrame(data) if data else pd.DataFrame()

        content = {
            "title": report["name"],
            "description": report.get("description", ""),
            "generated_at": datetime.utcnow().isoformat(),
            "date_range": date_range,
            "summary": self._generate_summary(df, report["metrics"]),
            "data": data,
        }

        return content

    async def _format_report(
        self, format: str, content: Dict[str, Any], template: str
    ) -> Dict[str, Any]:
        """Format report based on output format"""

        if format == "json":
            return {
                "data": json.dumps(content, indent=2),
                "content_type": "application/json",
            }
        elif format == "html":
            html = self._generate_html_report(content, template)
            return {"data": html, "content_type": "text/html"}
        elif format == "pdf":
            # In production, convert HTML to PDF
            html = self._generate_html_report(content, template)
            return {
                "data": html,  # Would be PDF bytes in production
                "content_type": "application/pdf",
            }
        else:
            return {"data": str(content), "content_type": "text/plain"}

    def _generate_summary(self, df: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """Generate summary statistics"""

        if df.empty:
            return {}

        summary = {}
        for metric in metrics:
            if metric in df.columns:
                summary[metric] = {
                    "mean": float(df[metric].mean()),
                    "median": float(df[metric].median()),
                    "min": float(df[metric].min()),
                    "max": float(df[metric].max()),
                    "std": float(df[metric].std()),
                }

        return summary

    def _generate_html_report(self, content: Dict[str, Any], template: str) -> str:
        """Generate HTML report"""

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{content.get('title', 'Report')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2196F3; }}
                .summary {{ background: #f5f5f5; padding: 20px; margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #2196F3; color: white; }}
            </style>
        </head>
        <body>
            <h1>{content.get('title', 'Report')}</h1>
            <p>Generated: {content.get('generated_at', '')}</p>
            <div class="summary">
                <h2>Summary</h2>
                <pre>{json.dumps(content.get('summary', {}), indent=2)}</pre>
            </div>
        </body>
        </html>
        """

        return html

    async def _deliver_via_email(
        self, report_data: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deliver report via email"""
        # In production, send actual email
        return {
            "success": True,
            "method": "email",
            "recipients": config.get("recipients", []),
        }

    async def _deliver_via_webhook(
        self, report_data: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deliver report via webhook"""
        # In production, POST to webhook URL
        return {"success": True, "method": "webhook", "url": config.get("url")}

    async def _deliver_to_storage(
        self, report_data: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deliver report to storage"""
        # In production, upload to S3/storage
        return {"success": True, "method": "storage", "location": config.get("bucket")}

    async def _get_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        """Get dashboard configuration"""
        # In production, fetch from database
        return {"id": dashboard_id, "name": "Sample Dashboard", "widgets": []}

    async def _generate_widget_report(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report for widget"""
        return {"title": widget.get("title"), "type": widget.get("type"), "data": []}

    async def _generate_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report section"""
        return {
            "title": section.get("title"),
            "type": section.get("type"),
            "content": {},
        }

    def _calculate_next_run(self, frequency: ReportFrequency) -> str:
        """Calculate next run time"""
        if frequency == ReportFrequency.DAILY:
            delta = timedelta(days=1)
        elif frequency == ReportFrequency.WEEKLY:
            delta = timedelta(weeks=1)
        elif frequency == ReportFrequency.MONTHLY:
            delta = timedelta(days=30)
        else:
            delta = timedelta(days=90)

        return (datetime.utcnow() + delta).isoformat()

    def _generate_id(self) -> int:
        """Generate unique ID"""
        import random

        return random.randint(1000, 9999)
