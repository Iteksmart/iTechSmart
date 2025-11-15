"""
iTechSmart Sentinel - Distributed Tracing Engine
Tracks requests across all services with OpenTelemetry support
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import uuid
import json

from app.models.models import Service, Trace, Span


class TracingEngine:
    """
    Distributed tracing engine for tracking requests across services
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_trace(
        self,
        service_name: str,
        operation_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        status_code: Optional[int] = None,
        http_method: Optional[str] = None,
        http_url: Optional[str] = None,
        user_agent: Optional[str] = None,
        client_ip: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Trace:
        """
        Create a new distributed trace
        """
        # Get or create service
        service = self.db.query(Service).filter(Service.name == service_name).first()
        if not service:
            service = Service(
                name=service_name,
                display_name=service_name,
                is_healthy=True
            )
            self.db.add(service)
            self.db.flush()
        
        # Generate trace ID
        trace_id = str(uuid.uuid4())
        
        # Calculate duration
        duration_ms = None
        if end_time:
            duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Determine if error
        is_error = False
        error_message = None
        if status_code and status_code >= 400:
            is_error = True
            error_message = f"HTTP {status_code}"
        
        # Create trace
        trace = Trace(
            trace_id=trace_id,
            service_id=service.id,
            operation_name=operation_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            status_code=status_code,
            is_error=is_error,
            error_message=error_message,
            http_method=http_method,
            http_url=http_url,
            user_agent=user_agent,
            client_ip=client_ip,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.db.add(trace)
        self.db.commit()
        self.db.refresh(trace)
        
        return trace
    
    async def add_span(
        self,
        trace_id: str,
        operation_name: str,
        service_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        parent_span_id: Optional[str] = None,
        span_type: Optional[str] = None,
        is_error: bool = False,
        error_message: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Span:
        """
        Add a span to an existing trace
        """
        # Get trace
        trace = self.db.query(Trace).filter(Trace.trace_id == trace_id).first()
        if not trace:
            raise ValueError(f"Trace {trace_id} not found")
        
        # Generate span ID
        span_id = str(uuid.uuid4())
        
        # Calculate duration
        duration_ms = None
        if end_time:
            duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Create span
        span = Span(
            span_id=span_id,
            trace_id=trace.id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=service_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            is_error=is_error,
            error_message=error_message,
            span_type=span_type,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.db.add(span)
        self.db.commit()
        self.db.refresh(span)
        
        return span
    
    async def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete trace with all spans
        """
        trace = self.db.query(Trace).filter(Trace.trace_id == trace_id).first()
        if not trace:
            return None
        
        # Get all spans
        spans = self.db.query(Span).filter(Span.trace_id == trace.id).all()
        
        return {
            "trace_id": trace.trace_id,
            "service": trace.service.name,
            "operation_name": trace.operation_name,
            "start_time": trace.start_time.isoformat(),
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "duration_ms": trace.duration_ms,
            "status_code": trace.status_code,
            "is_error": trace.is_error,
            "error_message": trace.error_message,
            "http_method": trace.http_method,
            "http_url": trace.http_url,
            "tags": trace.tags,
            "metadata": trace.metadata,
            "spans": [
                {
                    "span_id": span.span_id,
                    "parent_span_id": span.parent_span_id,
                    "operation_name": span.operation_name,
                    "service_name": span.service_name,
                    "start_time": span.start_time.isoformat(),
                    "end_time": span.end_time.isoformat() if span.end_time else None,
                    "duration_ms": span.duration_ms,
                    "is_error": span.is_error,
                    "error_message": span.error_message,
                    "span_type": span.span_type,
                    "tags": span.tags,
                    "metadata": span.metadata
                }
                for span in spans
            ]
        }
    
    async def search_traces(
        self,
        service_name: Optional[str] = None,
        operation_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_duration_ms: Optional[float] = None,
        max_duration_ms: Optional[float] = None,
        is_error: Optional[bool] = None,
        status_code: Optional[int] = None,
        tags: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search traces with filters
        """
        query = self.db.query(Trace).join(Service)
        
        # Apply filters
        if service_name:
            query = query.filter(Service.name == service_name)
        
        if operation_name:
            query = query.filter(Trace.operation_name.ilike(f"%{operation_name}%"))
        
        if start_time:
            query = query.filter(Trace.start_time >= start_time)
        
        if end_time:
            query = query.filter(Trace.start_time <= end_time)
        
        if min_duration_ms is not None:
            query = query.filter(Trace.duration_ms >= min_duration_ms)
        
        if max_duration_ms is not None:
            query = query.filter(Trace.duration_ms <= max_duration_ms)
        
        if is_error is not None:
            query = query.filter(Trace.is_error == is_error)
        
        if status_code is not None:
            query = query.filter(Trace.status_code == status_code)
        
        # Order by start time descending
        query = query.order_by(desc(Trace.start_time))
        
        # Apply pagination
        traces = query.limit(limit).offset(offset).all()
        
        return [
            {
                "trace_id": trace.trace_id,
                "service": trace.service.name,
                "operation_name": trace.operation_name,
                "start_time": trace.start_time.isoformat(),
                "duration_ms": trace.duration_ms,
                "status_code": trace.status_code,
                "is_error": trace.is_error,
                "span_count": len(trace.spans)
            }
            for trace in traces
        ]
    
    async def get_service_dependencies(self, service_name: str) -> Dict[str, Any]:
        """
        Get service dependency graph based on traces
        """
        # Get all traces for this service
        service = self.db.query(Service).filter(Service.name == service_name).first()
        if not service:
            return {"service": service_name, "dependencies": [], "dependents": []}
        
        # Get traces from last 24 hours
        since = datetime.utcnow() - timedelta(hours=24)
        traces = self.db.query(Trace).filter(
            and_(
                Trace.service_id == service.id,
                Trace.start_time >= since
            )
        ).all()
        
        # Extract dependencies from spans
        dependencies = set()
        for trace in traces:
            for span in trace.spans:
                if span.service_name and span.service_name != service_name:
                    dependencies.add(span.service_name)
        
        # Find services that depend on this service
        dependents = set()
        dependent_traces = self.db.query(Trace).join(Span).filter(
            and_(
                Span.service_name == service_name,
                Trace.start_time >= since
            )
        ).all()
        
        for trace in dependent_traces:
            if trace.service.name != service_name:
                dependents.add(trace.service.name)
        
        return {
            "service": service_name,
            "dependencies": list(dependencies),
            "dependents": list(dependents),
            "trace_count": len(traces)
        }
    
    async def get_trace_statistics(
        self,
        service_name: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get trace statistics for a time period
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(Trace).filter(Trace.start_time >= since)
        
        if service_name:
            query = query.join(Service).filter(Service.name == service_name)
        
        traces = query.all()
        
        if not traces:
            return {
                "total_traces": 0,
                "error_traces": 0,
                "error_rate": 0.0,
                "avg_duration_ms": 0.0,
                "p50_duration_ms": 0.0,
                "p95_duration_ms": 0.0,
                "p99_duration_ms": 0.0
            }
        
        # Calculate statistics
        total_traces = len(traces)
        error_traces = sum(1 for t in traces if t.is_error)
        error_rate = (error_traces / total_traces) * 100 if total_traces > 0 else 0.0
        
        durations = [t.duration_ms for t in traces if t.duration_ms is not None]
        durations.sort()
        
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        def percentile(data, p):
            if not data:
                return 0.0
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f + 1 < len(data) else f
            return data[f] + (k - f) * (data[c] - data[f])
        
        return {
            "total_traces": total_traces,
            "error_traces": error_traces,
            "error_rate": round(error_rate, 2),
            "avg_duration_ms": round(avg_duration, 2),
            "p50_duration_ms": round(percentile(durations, 50), 2),
            "p95_duration_ms": round(percentile(durations, 95), 2),
            "p99_duration_ms": round(percentile(durations, 99), 2),
            "min_duration_ms": round(min(durations), 2) if durations else 0.0,
            "max_duration_ms": round(max(durations), 2) if durations else 0.0
        }
    
    async def get_slow_traces(
        self,
        service_name: Optional[str] = None,
        threshold_ms: float = 1000.0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get slowest traces above threshold
        """
        query = self.db.query(Trace).filter(
            Trace.duration_ms >= threshold_ms
        )
        
        if service_name:
            query = query.join(Service).filter(Service.name == service_name)
        
        traces = query.order_by(desc(Trace.duration_ms)).limit(limit).all()
        
        return [
            {
                "trace_id": trace.trace_id,
                "service": trace.service.name,
                "operation_name": trace.operation_name,
                "duration_ms": trace.duration_ms,
                "start_time": trace.start_time.isoformat(),
                "http_url": trace.http_url
            }
            for trace in traces
        ]
    
    async def analyze_trace_patterns(
        self,
        service_name: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze common patterns in traces
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        service = self.db.query(Service).filter(Service.name == service_name).first()
        if not service:
            return {"error": "Service not found"}
        
        traces = self.db.query(Trace).filter(
            and_(
                Trace.service_id == service.id,
                Trace.start_time >= since
            )
        ).all()
        
        # Analyze patterns
        operation_counts = {}
        error_operations = {}
        slow_operations = {}
        
        for trace in traces:
            op = trace.operation_name
            
            # Count operations
            operation_counts[op] = operation_counts.get(op, 0) + 1
            
            # Track errors
            if trace.is_error:
                error_operations[op] = error_operations.get(op, 0) + 1
            
            # Track slow operations (>1s)
            if trace.duration_ms and trace.duration_ms > 1000:
                slow_operations[op] = slow_operations.get(op, 0) + 1
        
        # Sort by frequency
        top_operations = sorted(
            operation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        top_errors = sorted(
            error_operations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        top_slow = sorted(
            slow_operations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "service": service_name,
            "time_period_hours": hours,
            "total_traces": len(traces),
            "top_operations": [
                {"operation": op, "count": count}
                for op, count in top_operations
            ],
            "top_error_operations": [
                {"operation": op, "error_count": count}
                for op, count in top_errors
            ],
            "top_slow_operations": [
                {"operation": op, "slow_count": count}
                for op, count in top_slow
            ]
        }