"""
iTechSmart Observatory - Traces API
Handles distributed tracing ingestion and analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import and_
from .database import get_db

router = APIRouter(prefix="/api/observatory/traces", tags=["traces"])


# ==================== REQUEST MODELS ====================


class TraceIngestRequest(BaseModel):
    service_id: str
    trace_id: str
    trace_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "ok"
    http_method: Optional[str] = None
    http_url: Optional[str] = None
    http_status_code: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None


class SpanIngestRequest(BaseModel):
    trace_id: str
    span_id: str
    span_name: str
    service_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    parent_span_id: Optional[str] = None
    span_kind: str = "internal"
    status: str = "ok"
    attributes: Optional[Dict[str, Any]] = None


# ==================== ENDPOINTS ====================


@router.post("/ingest")
async def ingest_trace(request: TraceIngestRequest, db: Session = Depends(get_db)):
    """
    Ingest a distributed trace
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        trace_id = engine.ingest_trace(
            service_id=request.service_id,
            trace_id=request.trace_id,
            trace_name=request.trace_name,
            start_time=request.start_time,
            end_time=request.end_time,
            status=request.status,
            http_method=request.http_method,
            http_url=request.http_url,
            http_status_code=request.http_status_code,
            attributes=request.attributes,
        )

        return {"status": "success", "trace_id": trace_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/spans/ingest")
async def ingest_span(request: SpanIngestRequest, db: Session = Depends(get_db)):
    """
    Ingest a span within a trace
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        span_id = engine.ingest_span(
            trace_id=request.trace_id,
            span_id=request.span_id,
            span_name=request.span_name,
            service_name=request.service_name,
            start_time=request.start_time,
            end_time=request.end_time,
            parent_span_id=request.parent_span_id,
            span_kind=request.span_kind,
            status=request.status,
            attributes=request.attributes,
        )

        return {"status": "success", "span_id": span_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trace_id}")
async def get_trace_details(trace_id: str, db: Session = Depends(get_db)):
    """
    Get complete trace with all spans
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        trace = engine.get_trace_details(trace_id)

        if not trace:
            raise HTTPException(status_code=404, detail="Trace not found")

        return {"status": "success", "trace": trace}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trace_id}/analyze")
async def analyze_trace_performance(trace_id: str, db: Session = Depends(get_db)):
    """
    Analyze trace performance and identify bottlenecks
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        analysis = engine.analyze_trace_performance(trace_id)

        return {"status": "success", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service/{service_id}")
async def list_traces(
    service_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    """
    List traces for a service
    """
    from ..models import Trace
    from sqlalchemy import and_

    try:
        query = db.query(Trace).filter(Trace.service_id == service_id)

        if start_time:
            query = query.filter(Trace.start_time >= start_time)

        if end_time:
            query = query.filter(Trace.start_time <= end_time)

        if status:
            query = query.filter(Trace.status == status)

        traces = query.order_by(Trace.start_time.desc()).limit(limit).all()

        return {
            "status": "success",
            "traces": [
                {
                    "trace_id": t.id,
                    "trace_name": t.trace_name,
                    "start_time": t.start_time.isoformat(),
                    "duration_ms": t.duration_ms,
                    "status": t.status,
                    "http_method": t.http_method,
                    "http_status_code": t.http_status_code,
                }
                for t in traces
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service/{service_id}/statistics")
async def get_trace_statistics(
    service_id: str,
    time_range: str = Query("1h", description="Time range (e.g., 1h, 24h, 7d)"),
    db: Session = Depends(get_db),
):
    """
    Get trace statistics for a service
    """
    from ..models import Trace
    from sqlalchemy import func
    from datetime import datetime, timedelta

    try:
        # Parse time range
        if time_range.endswith("h"):
            hours = int(time_range[:-1])
            start_time = datetime.utcnow() - timedelta(hours=hours)
        elif time_range.endswith("d"):
            days = int(time_range[:-1])
            start_time = datetime.utcnow() - timedelta(days=days)
        else:
            start_time = datetime.utcnow() - timedelta(hours=1)

        # Get statistics
        stats = (
            db.query(
                func.count(Trace.id).label("total_traces"),
                func.avg(Trace.duration_ms).label("avg_duration"),
                func.min(Trace.duration_ms).label("min_duration"),
                func.max(Trace.duration_ms).label("max_duration"),
            )
            .filter(
                and_(Trace.service_id == service_id, Trace.start_time >= start_time)
            )
            .first()
        )

        # Get error count
        error_count = (
            db.query(func.count(Trace.id))
            .filter(
                and_(
                    Trace.service_id == service_id,
                    Trace.start_time >= start_time,
                    Trace.status == "error",
                )
            )
            .scalar()
        )

        total = stats.total_traces or 0
        error_rate = (error_count / total * 100) if total > 0 else 0

        return {
            "status": "success",
            "statistics": {
                "total_traces": total,
                "avg_duration_ms": stats.avg_duration,
                "min_duration_ms": stats.min_duration,
                "max_duration_ms": stats.max_duration,
                "error_count": error_count,
                "error_rate": error_rate,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dependency injection
def get_db():
    """Database session dependency"""
    # TODO: Implement database session management
    pass
