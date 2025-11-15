"""
iTechSmart Observatory - Core Engine
Product #36: Application Performance Monitoring & Observability Platform

This module provides the core business logic for the Observatory system including:
- Metrics ingestion and querying
- Trace collection and analysis
- Log aggregation and search
- Alert evaluation and notification
- Dashboard data preparation
- Anomaly detection
- SLO tracking
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import statistics
import json


class ObservatoryEngine:
    """
    Core engine for Observatory operations
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    # ==================== SERVICE MANAGEMENT ====================

    def register_service(
        self,
        name: str,
        service_type: str,
        environment: str,
        version: Optional[str] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Register a new service for monitoring
        """
        from ..models import Service

        service = Service(
            id=str(uuid.uuid4()),
            name=name,
            service_type=service_type,
            environment=environment,
            version=version,
            language=language,
            framework=framework,
            metadata=metadata or {},
            tags=tags or [],
            health_status="unknown",
            last_seen=datetime.utcnow(),
            is_active=True
        )

        self.db.add(service)
        self.db.commit()

        return {
            "service_id": service.id,
            "name": service.name,
            "environment": service.environment,
            "status": "registered"
        }

    def update_service_health(self, service_id: str, health_status: str) -> bool:
        """
        Update service health status
        """
        from ..models import Service

        service = self.db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return False

        service.health_status = health_status
        service.last_seen = datetime.utcnow()
        self.db.commit()

        return True

    def get_service_topology(self, service_id: str) -> Dict[str, Any]:
        """
        Get service dependency topology
        """
        from ..models import Service, ServiceDependency

        service = self.db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return {}

        # Get dependencies
        dependencies = self.db.query(ServiceDependency).filter(
            ServiceDependency.service_id == service_id
        ).all()

        # Get dependents (services that depend on this service)
        dependents = self.db.query(ServiceDependency).filter(
            ServiceDependency.depends_on_service_id == service_id
        ).all()

        return {
            "service": {
                "id": service.id,
                "name": service.name,
                "type": service.service_type,
                "health": service.health_status
            },
            "dependencies": [
                {
                    "service_id": dep.depends_on_service_id,
                    "type": dep.dependency_type,
                    "health": dep.health_status,
                    "latency_ms": dep.avg_latency_ms
                }
                for dep in dependencies
            ],
            "dependents": [
                {
                    "service_id": dep.service_id,
                    "type": dep.dependency_type,
                    "health": dep.health_status
                }
                for dep in dependents
            ]
        }

    # ==================== METRICS ====================

    def ingest_metric(
        self,
        service_id: str,
        metric_name: str,
        value: float,
        metric_type: str = "gauge",
        unit: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Ingest a metric data point
        """
        from ..models import Metric

        metric = Metric(
            id=str(uuid.uuid4()),
            service_id=service_id,
            metric_name=metric_name,
            metric_type=metric_type,
            value=value,
            unit=unit,
            labels=labels or {},
            timestamp=timestamp or datetime.utcnow()
        )

        self.db.add(metric)
        self.db.commit()

        # Trigger aggregation if needed
        self._aggregate_metrics(service_id, metric_name)

        return metric.id

    def query_metrics(
        self,
        service_id: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        aggregation: str = "avg",
        interval: str = "5m",
        labels: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query metrics with aggregation
        """
        from ..models import Metric

        query = self.db.query(Metric).filter(
            and_(
                Metric.service_id == service_id,
                Metric.metric_name == metric_name,
                Metric.timestamp >= start_time,
                Metric.timestamp <= end_time
            )
        )

        if labels:
            for key, value in labels.items():
                query = query.filter(Metric.labels[key].astext == value)

        metrics = query.order_by(Metric.timestamp).all()

        # Aggregate by interval
        return self._aggregate_by_interval(metrics, interval, aggregation)

    def get_metric_statistics(
        self,
        service_id: str,
        metric_name: str,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get statistical summary of a metric
        """
        from ..models import Metric

        start_time = self._parse_time_range(time_range)
        
        metrics = self.db.query(Metric).filter(
            and_(
                Metric.service_id == service_id,
                Metric.metric_name == metric_name,
                Metric.timestamp >= start_time
            )
        ).all()

        if not metrics:
            return {}

        values = [m.value for m in metrics]

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "median": statistics.median(values),
            "stddev": statistics.stdev(values) if len(values) > 1 else 0,
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99)
        }

    # ==================== TRACES ====================

    def ingest_trace(
        self,
        service_id: str,
        trace_id: str,
        trace_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        status: str = "ok",
        http_method: Optional[str] = None,
        http_url: Optional[str] = None,
        http_status_code: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Ingest a distributed trace
        """
        from ..models import Trace

        duration_ms = None
        if end_time:
            duration_ms = (end_time - start_time).total_seconds() * 1000

        trace = Trace(
            id=trace_id,
            service_id=service_id,
            trace_name=trace_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            status=status,
            http_method=http_method,
            http_url=http_url,
            http_status_code=http_status_code,
            attributes=attributes or {}
        )

        self.db.add(trace)
        self.db.commit()

        return trace.id

    def ingest_span(
        self,
        trace_id: str,
        span_id: str,
        span_name: str,
        service_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        parent_span_id: Optional[str] = None,
        span_kind: str = "internal",
        status: str = "ok",
        attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Ingest a span within a trace
        """
        from ..models import Span

        duration_ms = None
        if end_time:
            duration_ms = (end_time - start_time).total_seconds() * 1000

        span = Span(
            id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            span_name=span_name,
            span_kind=span_kind,
            service_name=service_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            status=status,
            attributes=attributes or {}
        )

        self.db.add(span)
        self.db.commit()

        return span.id

    def get_trace_details(self, trace_id: str) -> Dict[str, Any]:
        """
        Get complete trace with all spans
        """
        from ..models import Trace, Span

        trace = self.db.query(Trace).filter(Trace.id == trace_id).first()
        if not trace:
            return {}

        spans = self.db.query(Span).filter(Span.trace_id == trace_id).all()

        return {
            "trace_id": trace.id,
            "service_id": trace.service_id,
            "trace_name": trace.trace_name,
            "start_time": trace.start_time.isoformat(),
            "duration_ms": trace.duration_ms,
            "status": trace.status,
            "spans": [
                {
                    "span_id": span.id,
                    "parent_span_id": span.parent_span_id,
                    "span_name": span.span_name,
                    "service_name": span.service_name,
                    "duration_ms": span.duration_ms,
                    "status": span.status
                }
                for span in spans
            ]
        }

    def analyze_trace_performance(self, trace_id: str) -> Dict[str, Any]:
        """
        Analyze trace performance and identify bottlenecks
        """
        from ..models import Span

        spans = self.db.query(Span).filter(Span.trace_id == trace_id).all()
        
        if not spans:
            return {}

        # Find slowest spans
        sorted_spans = sorted(spans, key=lambda s: s.duration_ms or 0, reverse=True)
        
        total_duration = sum(s.duration_ms or 0 for s in spans)
        
        return {
            "total_spans": len(spans),
            "total_duration_ms": total_duration,
            "slowest_spans": [
                {
                    "span_name": span.span_name,
                    "service_name": span.service_name,
                    "duration_ms": span.duration_ms,
                    "percentage": (span.duration_ms / total_duration * 100) if total_duration > 0 else 0
                }
                for span in sorted_spans[:5]
            ],
            "error_spans": [
                {
                    "span_name": span.span_name,
                    "error_message": span.error_message
                }
                for span in spans if span.status == "error"
            ]
        }

    # ==================== LOGS ====================

    def ingest_log(
        self,
        service_id: str,
        level: str,
        message: str,
        timestamp: Optional[datetime] = None,
        logger_name: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> str:
        """
        Ingest a log entry
        """
        from ..models import LogEntry

        log = LogEntry(
            id=str(uuid.uuid4()),
            service_id=service_id,
            timestamp=timestamp or datetime.utcnow(),
            level=level.upper(),
            message=message,
            logger_name=logger_name,
            trace_id=trace_id,
            span_id=span_id,
            attributes=attributes or {},
            stack_trace=stack_trace
        )

        self.db.add(log)
        self.db.commit()

        return log.id

    def search_logs(
        self,
        service_id: Optional[str] = None,
        level: Optional[str] = None,
        search_query: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        trace_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search logs with filters
        """
        from ..models import LogEntry

        query = self.db.query(LogEntry)

        if service_id:
            query = query.filter(LogEntry.service_id == service_id)
        
        if level:
            query = query.filter(LogEntry.level == level.upper())
        
        if search_query:
            query = query.filter(LogEntry.message.ilike(f"%{search_query}%"))
        
        if start_time:
            query = query.filter(LogEntry.timestamp >= start_time)
        
        if end_time:
            query = query.filter(LogEntry.timestamp <= end_time)
        
        if trace_id:
            query = query.filter(LogEntry.trace_id == trace_id)

        logs = query.order_by(desc(LogEntry.timestamp)).limit(limit).all()

        return [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "service_id": log.service_id,
                "trace_id": log.trace_id
            }
            for log in logs
        ]

    def get_log_statistics(
        self,
        service_id: str,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get log statistics by level
        """
        from ..models import LogEntry

        start_time = self._parse_time_range(time_range)

        stats = self.db.query(
            LogEntry.level,
            func.count(LogEntry.id).label('count')
        ).filter(
            and_(
                LogEntry.service_id == service_id,
                LogEntry.timestamp >= start_time
            )
        ).group_by(LogEntry.level).all()

        return {
            level: count for level, count in stats
        }

    # ==================== ALERTS ====================

    def create_alert(
        self,
        name: str,
        alert_type: str,
        severity: str,
        condition: Dict[str, Any],
        service_id: Optional[str] = None,
        metric_name: Optional[str] = None,
        notification_channels: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> str:
        """
        Create an alert rule
        """
        from ..models import Alert

        alert = Alert(
            id=str(uuid.uuid4()),
            name=name,
            alert_type=alert_type,
            severity=severity,
            service_id=service_id,
            metric_name=metric_name,
            condition=condition,
            notification_channels=notification_channels or [],
            is_active=True,
            created_by=created_by
        )

        self.db.add(alert)
        self.db.commit()

        return alert.id

    def evaluate_alerts(self) -> List[Dict[str, Any]]:
        """
        Evaluate all active alerts
        """
        from ..models import Alert

        alerts = self.db.query(Alert).filter(Alert.is_active == True).all()
        
        triggered_alerts = []

        for alert in alerts:
            if self._evaluate_alert_condition(alert):
                incident_id = self._create_alert_incident(alert)
                triggered_alerts.append({
                    "alert_id": alert.id,
                    "alert_name": alert.name,
                    "severity": alert.severity,
                    "incident_id": incident_id
                })

        return triggered_alerts

    def acknowledge_incident(
        self,
        incident_id: str,
        acknowledged_by: str
    ) -> bool:
        """
        Acknowledge an alert incident
        """
        from ..models import AlertIncident

        incident = self.db.query(AlertIncident).filter(
            AlertIncident.id == incident_id
        ).first()

        if not incident:
            return False

        incident.status = "acknowledged"
        incident.acknowledged_at = datetime.utcnow()
        incident.acknowledged_by = acknowledged_by
        self.db.commit()

        return True

    def resolve_incident(
        self,
        incident_id: str,
        resolved_by: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """
        Resolve an alert incident
        """
        from ..models import AlertIncident

        incident = self.db.query(AlertIncident).filter(
            AlertIncident.id == incident_id
        ).first()

        if not incident:
            return False

        incident.status = "resolved"
        incident.resolved_at = datetime.utcnow()
        incident.resolved_by = resolved_by
        incident.resolution_notes = resolution_notes
        incident.duration_seconds = int(
            (incident.resolved_at - incident.started_at).total_seconds()
        )
        self.db.commit()

        return True

    # ==================== DASHBOARDS ====================

    def create_dashboard(
        self,
        name: str,
        layout: Dict[str, Any],
        widgets: List[Dict[str, Any]],
        owner_id: str,
        description: Optional[str] = None,
        is_public: bool = False
    ) -> str:
        """
        Create a custom dashboard
        """
        from ..models import Dashboard

        dashboard = Dashboard(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            layout=layout,
            widgets=widgets,
            owner_id=owner_id,
            is_public=is_public
        )

        self.db.add(dashboard)
        self.db.commit()

        return dashboard.id

    def get_dashboard_data(
        self,
        dashboard_id: str,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get data for all widgets in a dashboard
        """
        from ..models import Dashboard

        dashboard = self.db.query(Dashboard).filter(
            Dashboard.id == dashboard_id
        ).first()

        if not dashboard:
            return {}

        widget_data = []
        for widget in dashboard.widgets:
            data = self._get_widget_data(widget, time_range)
            widget_data.append({
                "widget_id": widget.get("id"),
                "widget_type": widget.get("type"),
                "data": data
            })

        return {
            "dashboard_id": dashboard.id,
            "name": dashboard.name,
            "widgets": widget_data
        }

    # ==================== ANOMALY DETECTION ====================

    def detect_anomalies(
        self,
        service_id: str,
        metric_name: str,
        time_range: str = "24h"
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metric data
        """
        from ..models import Metric, AnomalyDetection

        start_time = self._parse_time_range(time_range)

        metrics = self.db.query(Metric).filter(
            and_(
                Metric.service_id == service_id,
                Metric.metric_name == metric_name,
                Metric.timestamp >= start_time
            )
        ).order_by(Metric.timestamp).all()

        if len(metrics) < 10:
            return []

        anomalies = []
        values = [m.value for m in metrics]
        mean = statistics.mean(values)
        stddev = statistics.stdev(values) if len(values) > 1 else 0

        for metric in metrics:
            if stddev > 0:
                z_score = abs((metric.value - mean) / stddev)
                
                if z_score > 3:  # 3 standard deviations
                    anomaly = AnomalyDetection(
                        id=str(uuid.uuid4()),
                        service_id=service_id,
                        anomaly_type="outlier",
                        metric_name=metric_name,
                        detected_at=metric.timestamp,
                        severity="high" if z_score > 4 else "medium",
                        confidence_score=min(z_score / 5, 1.0),
                        expected_value=mean,
                        actual_value=metric.value,
                        deviation_percent=((metric.value - mean) / mean * 100) if mean != 0 else 0
                    )
                    
                    self.db.add(anomaly)
                    anomalies.append({
                        "timestamp": metric.timestamp.isoformat(),
                        "expected": mean,
                        "actual": metric.value,
                        "severity": anomaly.severity
                    })

        self.db.commit()
        return anomalies

    # ==================== SLO TRACKING ====================

    def create_slo(
        self,
        service_id: str,
        name: str,
        slo_type: str,
        target_value: float,
        metric_name: str,
        measurement_window: str = "30d",
        description: Optional[str] = None
    ) -> str:
        """
        Create a Service Level Objective
        """
        from ..models import SLO

        slo = SLO(
            id=str(uuid.uuid4()),
            service_id=service_id,
            name=name,
            description=description,
            slo_type=slo_type,
            target_value=target_value,
            metric_name=metric_name,
            measurement_window=measurement_window,
            is_active=True
        )

        self.db.add(slo)
        self.db.commit()

        return slo.id

    def evaluate_slo(self, slo_id: str) -> Dict[str, Any]:
        """
        Evaluate SLO compliance
        """
        from ..models import SLO, Metric

        slo = self.db.query(SLO).filter(SLO.id == slo_id).first()
        if not slo:
            return {}

        start_time = self._parse_time_range(slo.measurement_window)

        metrics = self.db.query(Metric).filter(
            and_(
                Metric.service_id == slo.service_id,
                Metric.metric_name == slo.metric_name,
                Metric.timestamp >= start_time
            )
        ).all()

        if not metrics:
            return {"status": "no_data"}

        values = [m.value for m in metrics]
        current_value = statistics.mean(values)

        # Determine compliance
        if slo.slo_type == "availability":
            compliant = current_value >= slo.target_value
        elif slo.slo_type == "latency":
            compliant = current_value <= slo.target_value
        elif slo.slo_type == "error_rate":
            compliant = current_value <= slo.target_value
        else:
            compliant = current_value >= slo.target_value

        # Calculate error budget
        if slo.slo_type == "availability":
            error_budget_remaining = ((current_value - slo.target_value) / (100 - slo.target_value)) * 100
        else:
            error_budget_remaining = 100 if compliant else 0

        # Update SLO
        slo.current_value = current_value
        slo.compliance_status = "compliant" if compliant else "breached"
        slo.error_budget_remaining = max(0, error_budget_remaining)
        slo.last_evaluated = datetime.utcnow()
        self.db.commit()

        return {
            "slo_id": slo.id,
            "name": slo.name,
            "target": slo.target_value,
            "current": current_value,
            "compliant": compliant,
            "error_budget_remaining": error_budget_remaining
        }

    # ==================== HELPER METHODS ====================

    def _parse_time_range(self, time_range: str) -> datetime:
        """
        Parse time range string to datetime
        """
        units = {
            'm': 'minutes',
            'h': 'hours',
            'd': 'days'
        }
        
        value = int(time_range[:-1])
        unit = time_range[-1]
        
        if unit in units:
            delta = timedelta(**{units[unit]: value})
            return datetime.utcnow() - delta
        
        return datetime.utcnow() - timedelta(hours=1)

    def _aggregate_by_interval(
        self,
        metrics: List,
        interval: str,
        aggregation: str
    ) -> List[Dict[str, Any]]:
        """
        Aggregate metrics by time interval
        """
        # Simple implementation - group by interval and aggregate
        result = []
        # TODO: Implement proper time-series aggregation
        return result

    def _percentile(self, values: List[float], percentile: int) -> float:
        """
        Calculate percentile
        """
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def _aggregate_metrics(self, service_id: str, metric_name: str):
        """
        Aggregate metrics for faster queries
        """
        # TODO: Implement metric aggregation
        pass

    def _evaluate_alert_condition(self, alert) -> bool:
        """
        Evaluate if alert condition is met
        """
        # TODO: Implement alert condition evaluation
        return False

    def _create_alert_incident(self, alert) -> str:
        """
        Create an alert incident
        """
        from ..models import AlertIncident

        incident = AlertIncident(
            id=str(uuid.uuid4()),
            alert_id=alert.id,
            status="firing",
            severity=alert.severity,
            started_at=datetime.utcnow()
        )

        self.db.add(incident)
        self.db.commit()

        return incident.id

    def _get_widget_data(self, widget: Dict[str, Any], time_range: str) -> Dict[str, Any]:
        """
        Get data for a specific widget
        """
        # TODO: Implement widget data retrieval
        return {}