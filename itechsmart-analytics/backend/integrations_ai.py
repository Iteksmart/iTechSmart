"""
iTechSmart Analytics - AI Insights Integration Module
Integration with other iTechSmart products for AI capabilities
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx


class AIInsightsIntegration:
    """Integration layer for AI Insights with other iTechSmart products"""

    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
        self.hub_url = "http://itechsmart-hub:8001"
        self.timeout = 30.0

    # ==================== HUB INTEGRATION ====================

    async def register_with_hub(self) -> Dict[str, Any]:
        """Register AI Insights capabilities with iTechSmart Hub"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.hub_url}/api/v1/services/register",
                    json={
                        "service_name": "analytics_ai_insights",
                        "service_type": "ai_ml",
                        "version": "1.1.0",
                        "capabilities": [
                            "predictive_analytics",
                            "anomaly_detection",
                            "trend_analysis",
                            "pattern_recognition",
                            "forecasting",
                            "recommendations",
                            "data_quality_assessment",
                        ],
                        "endpoints": {
                            "models": "/api/v1/ai/models",
                            "predictions": "/api/v1/ai/predictions",
                            "insights": "/api/v1/ai/insights",
                            "quality": "/api/v1/ai/quality",
                        },
                    },
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def notify_hub_insight(self, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Notify Hub of new critical insight"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.hub_url}/api/v1/events",
                    json={
                        "event_type": "ai_insight_generated",
                        "tenant_id": self.tenant_id,
                        "severity": insight_data.get("severity"),
                        "data": insight_data,
                    },
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    # ==================== OBSERVATORY INTEGRATION ====================

    async def get_observatory_metrics(
        self, service_name: str, metric_names: List[str], time_range_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get metrics from Observatory for AI analysis"""
        observatory_url = "http://itechsmart-observatory:8036"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{observatory_url}/api/v1/metrics",
                    params={
                        "tenant_id": self.tenant_id,
                        "service_name": service_name,
                        "metric_names": ",".join(metric_names),
                        "time_range_hours": time_range_hours,
                    },
                )
                return response.json()
            except Exception as e:
                return []

    async def send_anomaly_to_observatory(
        self, service_name: str, anomaly_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send detected anomaly to Observatory"""
        observatory_url = "http://itechsmart-observatory:8036"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{observatory_url}/api/v1/anomalies",
                    json={
                        "tenant_id": self.tenant_id,
                        "service_name": service_name,
                        "anomaly_data": anomaly_data,
                    },
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    # ==================== PULSE INTEGRATION ====================

    async def create_pulse_incident_from_insight(
        self, insight_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create Pulse incident from critical insight"""
        pulse_url = "http://itechsmart-pulse:8011"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{pulse_url}/api/v1/incidents",
                    json={
                        "tenant_id": self.tenant_id,
                        "title": insight_data.get("title"),
                        "description": insight_data.get("description"),
                        "severity": insight_data.get("severity"),
                        "source": "ai_insights",
                        "metadata": insight_data,
                    },
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_pulse_incident_metrics(self) -> List[Dict[str, Any]]:
        """Get incident metrics from Pulse for analysis"""
        pulse_url = "http://itechsmart-pulse:8011"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{pulse_url}/api/v1/incidents/metrics",
                    params={"tenant_id": self.tenant_id},
                )
                return response.json()
            except Exception as e:
                return []

    # ==================== SUPREME PLUS INTEGRATION ====================

    async def trigger_supreme_plus_remediation(
        self, recommendation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger Supreme Plus auto-remediation from recommendation"""
        supreme_plus_url = "http://itechsmart-supreme-plus:8034"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{supreme_plus_url}/api/v1/remediations/trigger",
                    json={
                        "tenant_id": self.tenant_id,
                        "source": "ai_recommendation",
                        "recommendation": recommendation_data,
                    },
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_supreme_plus_infrastructure_data(self) -> List[Dict[str, Any]]:
        """Get infrastructure data from Supreme Plus for AI analysis"""
        supreme_plus_url = "http://itechsmart-supreme-plus:8034"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{supreme_plus_url}/api/v1/monitoring/metrics",
                    params={"tenant_id": self.tenant_id},
                )
                return response.json()
            except Exception as e:
                return []

    # ==================== WORKFLOW INTEGRATION ====================

    async def trigger_workflow_from_recommendation(
        self, recommendation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger automated workflow from AI recommendation"""
        workflow_url = "http://itechsmart-workflow:8023"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{workflow_url}/api/v1/workflows/trigger",
                    json={
                        "tenant_id": self.tenant_id,
                        "trigger_type": "ai_recommendation",
                        "data": recommendation_data,
                    },
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_workflow_execution_metrics(self) -> List[Dict[str, Any]]:
        """Get workflow execution metrics for AI analysis"""
        workflow_url = "http://itechsmart-workflow:8023"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{workflow_url}/api/v1/workflows/metrics",
                    params={"tenant_id": self.tenant_id},
                )
                return response.json()
            except Exception as e:
                return []

    # ==================== NOTIFY INTEGRATION ====================

    async def send_insight_notification(
        self, insight_data: Dict[str, Any], recipients: List[str]
    ) -> Dict[str, Any]:
        """Send notification about critical insight"""
        notify_url = "http://itechsmart-notify:8014"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{notify_url}/api/v1/notifications/send",
                    json={
                        "tenant_id": self.tenant_id,
                        "type": "ai_insight",
                        "priority": (
                            "high"
                            if insight_data.get("severity") in ["high", "critical"]
                            else "normal"
                        ),
                        "subject": f"AI Insight: {insight_data.get('title')}",
                        "message": insight_data.get("description"),
                        "recipients": recipients,
                        "metadata": insight_data,
                    },
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    # ==================== COMPLIANCE INTEGRATION ====================

    async def check_compliance_impact(
        self, insight_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if insight has compliance implications"""
        compliance_url = "http://itechsmart-compliance:8019"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{compliance_url}/api/v1/compliance/check-impact",
                    json={
                        "tenant_id": self.tenant_id,
                        "event_type": "ai_insight",
                        "data": insight_data,
                    },
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_compliance_metrics(self) -> List[Dict[str, Any]]:
        """Get compliance metrics for AI analysis"""
        compliance_url = "http://itechsmart-compliance:8019"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{compliance_url}/api/v1/compliance/metrics",
                    params={"tenant_id": self.tenant_id},
                )
                return response.json()
            except Exception as e:
                return []

    # ==================== DATA PLATFORM INTEGRATION ====================

    async def get_data_platform_datasets(self) -> List[Dict[str, Any]]:
        """Get datasets from Data Platform for AI training"""
        data_platform_url = "http://itechsmart-data-platform:8026"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{data_platform_url}/api/v1/datasets",
                    params={"tenant_id": self.tenant_id},
                )
                return response.json()
            except Exception as e:
                return []

    async def publish_model_to_data_platform(
        self, model_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publish trained model to Data Platform"""
        data_platform_url = "http://itechsmart-data-platform:8026"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{data_platform_url}/api/v1/models/publish",
                    json={"tenant_id": self.tenant_id, "model_data": model_data},
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    # ==================== ENTERPRISE INTEGRATION ====================

    async def get_enterprise_tenant_data(self) -> Dict[str, Any]:
        """Get tenant data from Enterprise for context"""
        enterprise_url = "http://itechsmart-enterprise:8002"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{enterprise_url}/api/v1/tenants/{self.tenant_id}"
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    # ==================== CITADEL INTEGRATION ====================

    async def send_security_insight_to_citadel(
        self, insight_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send security-related insight to Citadel"""
        citadel_url = "http://itechsmart-citadel:8035"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{citadel_url}/api/v1/threats/ai-insight",
                    json={"tenant_id": self.tenant_id, "insight_data": insight_data},
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_citadel_security_metrics(self) -> List[Dict[str, Any]]:
        """Get security metrics from Citadel for AI analysis"""
        citadel_url = "http://itechsmart-citadel:8035"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{citadel_url}/api/v1/security/metrics",
                    params={"tenant_id": self.tenant_id},
                )
                return response.json()
            except Exception as e:
                return []

    # ==================== MARKETPLACE INTEGRATION ====================

    async def publish_model_to_marketplace(
        self, model_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publish AI model to Marketplace"""
        marketplace_url = "http://itechsmart-marketplace:8024"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{marketplace_url}/api/v1/products/publish",
                    json={
                        "tenant_id": self.tenant_id,
                        "product_type": "ai_model",
                        "product_data": model_data,
                    },
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    # ==================== UTILITY METHODS ====================

    async def get_cross_product_metrics(
        self, products: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics from multiple products for comprehensive analysis"""
        results = {}

        for product in products:
            if product == "observatory":
                results[product] = await self.get_observatory_metrics(
                    "all", ["response_time", "error_rate"], 24
                )
            elif product == "pulse":
                results[product] = await self.get_pulse_incident_metrics()
            elif product == "workflow":
                results[product] = await self.get_workflow_execution_metrics()
            elif product == "compliance":
                results[product] = await self.get_compliance_metrics()
            elif product == "citadel":
                results[product] = await self.get_citadel_security_metrics()
            elif product == "supreme_plus":
                results[product] = await self.get_supreme_plus_infrastructure_data()

        return results

    async def broadcast_critical_insight(
        self, insight_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Broadcast critical insight to all relevant products"""
        results = {
            "hub_notification": await self.notify_hub_insight(insight_data),
            "pulse_incident": None,
            "citadel_alert": None,
            "notification_sent": None,
        }

        # Create incident if critical
        if insight_data.get("severity") in ["high", "critical"]:
            results["pulse_incident"] = await self.create_pulse_incident_from_insight(
                insight_data
            )

        # Send to Citadel if security-related
        if "security" in insight_data.get("affected_metrics", []):
            results["citadel_alert"] = await self.send_security_insight_to_citadel(
                insight_data
            )

        # Send notifications
        results["notification_sent"] = await self.send_insight_notification(
            insight_data,
            recipients=["admin@tenant.com"],  # Would be dynamic in production
        )

        return results
