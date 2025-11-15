"""
iTechSmart Sentinel - Log Aggregation API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.log_engine import LogEngine


router = APIRouter(prefix="/api/logs", tags=["Log Aggregation"])


class IngestLogRequest(BaseModel):
    service_name: str
    level: str
    message: str
    timestamp: Optional[datetime] = None
    logger_name: Optional[str] = None
    file_name: Optional[str] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    tags: Optional[dict] = None
    metadata: Optional[dict] = None
    stack_trace: Optional[str] = None


@router.post("/ingest")
async def ingest_log(
    request: IngestLogRequest,
    db: Session = Depends(get_db)
):
    """Ingest a log entry"""
    engine = LogEngine(db)
    log_entry = await engine.ingest_log(**request.dict())
    return {"id": log_entry.id, "is_anomaly": log_entry.is_anomaly}


@router.get("/search")
async def search_logs(
    query: Optional[str] = None,
    service_name: Optional[str] = None,
    level: Optional[str] = None,
    trace_id: Optional[str] = None,
    is_anomaly: Optional[bool] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Search logs with natural language query"""
    engine = LogEngine(db)
    logs = await engine.search_logs(
        query=query,
        service_name=service_name,
        level=level,
        trace_id=trace_id,
        is_anomaly=is_anomaly,
        limit=limit,
        offset=offset
    )
    return {"logs": logs, "count": len(logs)}


@router.get("/patterns")
async def get_log_patterns(
    service_name: Optional[str] = None,
    hours: int = Query(24, le=168),
    min_occurrences: int = Query(5, ge=1),
    db: Session = Depends(get_db)
):
    """Identify common log patterns"""
    engine = LogEngine(db)
    patterns = await engine.get_log_patterns(service_name, hours, min_occurrences)
    return {"patterns": patterns, "count": len(patterns)}


@router.get("/statistics")
async def get_log_statistics(
    service_name: Optional[str] = None,
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get log statistics"""
    engine = LogEngine(db)
    stats = await engine.get_log_statistics(service_name, hours)
    return stats


@router.get("/errors")
async def get_error_logs(
    service_name: Optional[str] = None,
    hours: int = Query(24, le=168),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get recent error and critical logs"""
    engine = LogEngine(db)
    logs = await engine.get_error_logs(service_name, hours, limit)
    return {"error_logs": logs, "count": len(logs)}


@router.get("/anomalies")
async def get_anomalous_logs(
    service_name: Optional[str] = None,
    hours: int = Query(24, le=168),
    min_score: float = Query(0.7, ge=0.0, le=1.0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get logs detected as anomalies"""
    engine = LogEngine(db)
    logs = await engine.get_anomalous_logs(service_name, hours, min_score, limit)
    return {"anomalous_logs": logs, "count": len(logs)}


@router.get("/trace/{trace_id}")
async def correlate_logs_with_trace(
    trace_id: str,
    db: Session = Depends(get_db)
):
    """Get all logs correlated with a trace"""
    engine = LogEngine(db)
    logs = await engine.correlate_logs_with_traces(trace_id)
    return {"logs": logs, "count": len(logs)}