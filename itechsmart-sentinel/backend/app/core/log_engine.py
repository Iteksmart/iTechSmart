"""
iTechSmart Sentinel - Log Aggregation Engine
Centralized logs with NL search and anomaly detection
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import re
from collections import Counter

from app.models.models import Service, LogEntry


class LogEngine:
    """
    Centralized log aggregation with natural language search and anomaly detection
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.anomaly_baseline = {}  # Baseline for anomaly detection
    
    async def ingest_log(
        self,
        service_name: str,
        level: str,
        message: str,
        timestamp: Optional[datetime] = None,
        logger_name: Optional[str] = None,
        file_name: Optional[str] = None,
        line_number: Optional[int] = None,
        function_name: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> LogEntry:
        """
        Ingest a log entry
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
        
        # Use current time if not provided
        if not timestamp:
            timestamp = datetime.utcnow()
        
        # Detect anomalies
        is_anomaly, anomaly_score = await self._detect_anomaly(
            service_name,
            level,
            message
        )
        
        # Create log entry
        log_entry = LogEntry(
            service_id=service.id,
            timestamp=timestamp,
            level=level.upper(),
            message=message,
            logger_name=logger_name,
            file_name=file_name,
            line_number=line_number,
            function_name=function_name,
            trace_id=trace_id,
            span_id=span_id,
            tags=tags or {},
            metadata=metadata or {},
            stack_trace=stack_trace,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        return log_entry
    
    async def search_logs(
        self,
        query: Optional[str] = None,
        service_name: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        trace_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        is_anomaly: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search logs with natural language query support
        """
        db_query = self.db.query(LogEntry)
        
        # Service filter
        if service_name:
            db_query = db_query.join(Service).filter(Service.name == service_name)
        
        # Level filter
        if level:
            db_query = db_query.filter(LogEntry.level == level.upper())
        
        # Time range filter
        if start_time:
            db_query = db_query.filter(LogEntry.timestamp >= start_time)
        if end_time:
            db_query = db_query.filter(LogEntry.timestamp <= end_time)
        
        # Trace correlation
        if trace_id:
            db_query = db_query.filter(LogEntry.trace_id == trace_id)
        
        # Anomaly filter
        if is_anomaly is not None:
            db_query = db_query.filter(LogEntry.is_anomaly == is_anomaly)
        
        # Natural language query
        if query:
            # Parse natural language query
            search_terms = self._parse_nl_query(query)
            
            # Build search conditions
            conditions = []
            for term in search_terms:
                conditions.append(LogEntry.message.ilike(f"%{term}%"))
            
            if conditions:
                db_query = db_query.filter(or_(*conditions))
        
        # Order by timestamp descending
        db_query = db_query.order_by(desc(LogEntry.timestamp))
        
        # Apply pagination
        logs = db_query.limit(limit).offset(offset).all()
        
        return [
            {
                "id": log.id,
                "service": log.service.name,
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "logger_name": log.logger_name,
                "trace_id": log.trace_id,
                "is_anomaly": log.is_anomaly,
                "anomaly_score": log.anomaly_score,
                "tags": log.tags
            }
            for log in logs
        ]
    
    async def get_log_patterns(
        self,
        service_name: Optional[str] = None,
        hours: int = 24,
        min_occurrences: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Identify common log patterns
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(LogEntry).filter(LogEntry.timestamp >= since)
        
        if service_name:
            query = query.join(Service).filter(Service.name == service_name)
        
        logs = query.all()
        
        # Extract patterns using regex
        patterns = Counter()
        pattern_examples = {}
        
        for log in logs:
            # Normalize message (replace numbers, IDs, etc.)
            normalized = self._normalize_log_message(log.message)
            patterns[normalized] += 1
            
            if normalized not in pattern_examples:
                pattern_examples[normalized] = log.message
        
        # Filter by minimum occurrences
        common_patterns = [
            {
                "pattern": pattern,
                "count": count,
                "example": pattern_examples[pattern]
            }
            for pattern, count in patterns.most_common()
            if count >= min_occurrences
        ]
        
        return common_patterns[:50]  # Top 50 patterns
    
    async def get_log_statistics(
        self,
        service_name: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get log statistics for a time period
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(LogEntry).filter(LogEntry.timestamp >= since)
        
        if service_name:
            query = query.join(Service).filter(Service.name == service_name)
        
        logs = query.all()
        
        # Calculate statistics
        total_logs = len(logs)
        
        by_level = {
            "DEBUG": 0,
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0
        }
        
        anomaly_count = 0
        
        for log in logs:
            by_level[log.level] = by_level.get(log.level, 0) + 1
            if log.is_anomaly:
                anomaly_count += 1
        
        # Calculate error rate
        error_logs = by_level["ERROR"] + by_level["CRITICAL"]
        error_rate = (error_logs / total_logs * 100) if total_logs > 0 else 0.0
        
        # Calculate logs per minute
        if total_logs > 0:
            time_span_minutes = hours * 60
            logs_per_minute = total_logs / time_span_minutes
        else:
            logs_per_minute = 0.0
        
        return {
            "time_period_hours": hours,
            "total_logs": total_logs,
            "by_level": by_level,
            "error_rate": round(error_rate, 2),
            "anomaly_count": anomaly_count,
            "anomaly_rate": round((anomaly_count / total_logs * 100) if total_logs > 0 else 0.0, 2),
            "logs_per_minute": round(logs_per_minute, 2)
        }
    
    async def get_error_logs(
        self,
        service_name: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent error and critical logs
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(LogEntry).filter(
            and_(
                LogEntry.timestamp >= since,
                LogEntry.level.in_(["ERROR", "CRITICAL"])
            )
        )
        
        if service_name:
            query = query.join(Service).filter(Service.name == service_name)
        
        logs = query.order_by(desc(LogEntry.timestamp)).limit(limit).all()
        
        return [
            {
                "id": log.id,
                "service": log.service.name,
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "stack_trace": log.stack_trace,
                "trace_id": log.trace_id,
                "file_name": log.file_name,
                "line_number": log.line_number
            }
            for log in logs
        ]
    
    async def get_anomalous_logs(
        self,
        service_name: Optional[str] = None,
        hours: int = 24,
        min_score: float = 0.7,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get logs detected as anomalies
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(LogEntry).filter(
            and_(
                LogEntry.timestamp >= since,
                LogEntry.is_anomaly == True,
                LogEntry.anomaly_score >= min_score
            )
        )
        
        if service_name:
            query = query.join(Service).filter(Service.name == service_name)
        
        logs = query.order_by(
            desc(LogEntry.anomaly_score),
            desc(LogEntry.timestamp)
        ).limit(limit).all()
        
        return [
            {
                "id": log.id,
                "service": log.service.name,
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "anomaly_score": log.anomaly_score,
                "trace_id": log.trace_id
            }
            for log in logs
        ]
    
    async def correlate_logs_with_traces(
        self,
        trace_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all logs correlated with a specific trace
        """
        logs = self.db.query(LogEntry).filter(
            LogEntry.trace_id == trace_id
        ).order_by(LogEntry.timestamp).all()
        
        return [
            {
                "id": log.id,
                "service": log.service.name,
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "span_id": log.span_id,
                "file_name": log.file_name,
                "line_number": log.line_number
            }
            for log in logs
        ]
    
    def _parse_nl_query(self, query: str) -> List[str]:
        """
        Parse natural language query into search terms
        """
        # Remove common words
        stop_words = {
            "show", "me", "find", "get", "all", "the", "logs", "with",
            "that", "have", "containing", "about", "for", "in", "on"
        }
        
        # Split and clean
        terms = query.lower().split()
        terms = [t.strip() for t in terms if t.strip() not in stop_words]
        
        return terms
    
    def _normalize_log_message(self, message: str) -> str:
        """
        Normalize log message for pattern detection
        """
        # Replace numbers
        normalized = re.sub(r'\d+', 'N', message)
        
        # Replace UUIDs
        normalized = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            'UUID',
            normalized,
            flags=re.IGNORECASE
        )
        
        # Replace IP addresses
        normalized = re.sub(
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            'IP',
            normalized
        )
        
        # Replace timestamps
        normalized = re.sub(
            r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
            'TIMESTAMP',
            normalized
        )
        
        return normalized
    
    async def _detect_anomaly(
        self,
        service_name: str,
        level: str,
        message: str
    ) -> tuple[bool, Optional[float]]:
        """
        Detect if log is anomalous using simple heuristics
        (Can be enhanced with ML models)
        """
        anomaly_score = 0.0
        
        # Check for error keywords
        error_keywords = [
            "exception", "error", "failed", "failure", "crash",
            "panic", "fatal", "critical", "timeout", "refused"
        ]
        
        message_lower = message.lower()
        keyword_matches = sum(1 for kw in error_keywords if kw in message_lower)
        
        if keyword_matches > 0:
            anomaly_score += 0.3 * keyword_matches
        
        # High severity level
        if level in ["ERROR", "CRITICAL"]:
            anomaly_score += 0.4
        
        # Check for unusual patterns
        if len(message) > 1000:  # Very long message
            anomaly_score += 0.2
        
        if message.count("null") > 3:  # Multiple nulls
            anomaly_score += 0.2
        
        # Cap at 1.0
        anomaly_score = min(anomaly_score, 1.0)
        
        # Consider anomaly if score > 0.6
        is_anomaly = anomaly_score > 0.6
        
        return is_anomaly, anomaly_score if is_anomaly else None