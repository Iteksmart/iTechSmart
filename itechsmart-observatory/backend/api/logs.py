"""
iTechSmart Observatory - Logs API
Handles log ingestion, search, and analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from .database import get_db

router = APIRouter(prefix="/api/observatory/logs", tags=["logs"])


# ==================== REQUEST MODELS ====================


class LogIngestRequest(BaseModel):
    service_id: str
    level: str
    message: str
    timestamp: Optional[datetime] = None
    logger_name: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None


class BatchLogIngestRequest(BaseModel):
    logs: List[LogIngestRequest]


class LogSearchRequest(BaseModel):
    service_id: Optional[str] = None
    level: Optional[str] = None
    search_query: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    trace_id: Optional[str] = None
    limit: int = 100


# ==================== ENDPOINTS ====================


@router.post("/ingest")
async def ingest_log(request: LogIngestRequest, db: Session = Depends(get_db)):
    """
    Ingest a single log entry
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        log_id = engine.ingest_log(
            service_id=request.service_id,
            level=request.level,
            message=request.message,
            timestamp=request.timestamp,
            logger_name=request.logger_name,
            trace_id=request.trace_id,
            span_id=request.span_id,
            attributes=request.attributes,
            stack_trace=request.stack_trace,
        )

        return {"status": "success", "log_id": log_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/batch")
async def ingest_logs_batch(
    request: BatchLogIngestRequest, db: Session = Depends(get_db)
):
    """
    Ingest multiple logs in batch
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)
    ingested_count = 0

    try:
        for log in request.logs:
            engine.ingest_log(
                service_id=log.service_id,
                level=log.level,
                message=log.message,
                timestamp=log.timestamp,
                logger_name=log.logger_name,
                trace_id=log.trace_id,
                span_id=log.span_id,
                attributes=log.attributes,
                stack_trace=log.stack_trace,
            )
            ingested_count += 1

        return {"status": "success", "ingested_count": ingested_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_logs(request: LogSearchRequest, db: Session = Depends(get_db)):
    """
    Search logs with filters
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        logs = engine.search_logs(
            service_id=request.service_id,
            level=request.level,
            search_query=request.search_query,
            start_time=request.start_time,
            end_time=request.end_time,
            trace_id=request.trace_id,
            limit=request.limit,
        )

        return {"status": "success", "logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service/{service_id}")
async def get_service_logs(
    service_id: str,
    level: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    """
    Get logs for a specific service
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        logs = engine.search_logs(
            service_id=service_id,
            level=level,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

        return {"status": "success", "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/{service_id}")
async def get_log_statistics(
    service_id: str,
    time_range: str = Query("1h", description="Time range (e.g., 1h, 24h, 7d)"),
    db: Session = Depends(get_db),
):
    """
    Get log statistics by level
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        stats = engine.get_log_statistics(service_id=service_id, time_range=time_range)

        return {"status": "success", "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trace/{trace_id}")
async def get_trace_logs(trace_id: str, db: Session = Depends(get_db)):
    """
    Get all logs associated with a trace
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        logs = engine.search_logs(trace_id=trace_id, limit=1000)

        return {"status": "success", "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors/{service_id}")
async def get_error_logs(
    service_id: str,
    time_range: str = Query("1h", description="Time range"),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    """
    Get error and critical logs for a service
    """
    from ..models import LogEntry
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

        logs = (
            db.query(LogEntry)
            .filter(
                LogEntry.service_id == service_id,
                LogEntry.timestamp >= start_time,
                LogEntry.level.in_(["ERROR", "CRITICAL"]),
            )
            .order_by(LogEntry.timestamp.desc())
            .limit(limit)
            .all()
        )

        return {
            "status": "success",
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message,
                    "logger_name": log.logger_name,
                    "trace_id": log.trace_id,
                    "stack_trace": log.stack_trace,
                }
                for log in logs
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dependency injection
def get_db():
    """Database session dependency"""
    # TODO: Implement database session management
    pass
