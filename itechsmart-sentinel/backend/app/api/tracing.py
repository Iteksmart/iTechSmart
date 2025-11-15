"""
iTechSmart Sentinel - Tracing API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.tracing_engine import TracingEngine


router = APIRouter(prefix="/api/tracing", tags=["Distributed Tracing"])


class CreateTraceRequest(BaseModel):
    service_name: str
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status_code: Optional[int] = None
    http_method: Optional[str] = None
    http_url: Optional[str] = None
    user_agent: Optional[str] = None
    client_ip: Optional[str] = None
    tags: Optional[dict] = None
    metadata: Optional[dict] = None


class AddSpanRequest(BaseModel):
    trace_id: str
    operation_name: str
    service_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    parent_span_id: Optional[str] = None
    span_type: Optional[str] = None
    is_error: bool = False
    error_message: Optional[str] = None
    tags: Optional[dict] = None
    metadata: Optional[dict] = None


@router.post("/traces")
async def create_trace(
    request: CreateTraceRequest,
    db: Session = Depends(get_db)
):
    """Create a new distributed trace"""
    engine = TracingEngine(db)
    trace = await engine.create_trace(**request.dict())
    return {"trace_id": trace.trace_id, "id": trace.id}


@router.post("/spans")
async def add_span(
    request: AddSpanRequest,
    db: Session = Depends(get_db)
):
    """Add a span to an existing trace"""
    engine = TracingEngine(db)
    span = await engine.add_span(**request.dict())
    return {"span_id": span.span_id, "id": span.id}


@router.get("/traces/{trace_id}")
async def get_trace(
    trace_id: str,
    db: Session = Depends(get_db)
):
    """Get complete trace with all spans"""
    engine = TracingEngine(db)
    trace = await engine.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace


@router.get("/traces")
async def search_traces(
    service_name: Optional[str] = None,
    operation_name: Optional[str] = None,
    is_error: Optional[bool] = None,
    min_duration_ms: Optional[float] = None,
    max_duration_ms: Optional[float] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Search traces with filters"""
    engine = TracingEngine(db)
    traces = await engine.search_traces(
        service_name=service_name,
        operation_name=operation_name,
        is_error=is_error,
        min_duration_ms=min_duration_ms,
        max_duration_ms=max_duration_ms,
        limit=limit,
        offset=offset
    )
    return {"traces": traces, "count": len(traces)}


@router.get("/services/{service_name}/dependencies")
async def get_service_dependencies(
    service_name: str,
    db: Session = Depends(get_db)
):
    """Get service dependency graph"""
    engine = TracingEngine(db)
    dependencies = await engine.get_service_dependencies(service_name)
    return dependencies


@router.get("/statistics")
async def get_trace_statistics(
    service_name: Optional[str] = None,
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get trace statistics"""
    engine = TracingEngine(db)
    stats = await engine.get_trace_statistics(service_name, hours)
    return stats


@router.get("/slow-traces")
async def get_slow_traces(
    service_name: Optional[str] = None,
    threshold_ms: float = Query(1000.0, ge=0),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    """Get slowest traces above threshold"""
    engine = TracingEngine(db)
    traces = await engine.get_slow_traces(service_name, threshold_ms, limit)
    return {"slow_traces": traces, "count": len(traces)}


@router.get("/services/{service_name}/patterns")
async def analyze_trace_patterns(
    service_name: str,
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Analyze common trace patterns"""
    engine = TracingEngine(db)
    patterns = await engine.analyze_trace_patterns(service_name, hours)
    return patterns