"""
iTechSmart Observatory - Metrics API
Handles metric ingestion, querying, and analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/observatory/metrics", tags=["metrics"])


# ==================== REQUEST MODELS ====================


class MetricIngestRequest(BaseModel):
    service_id: str
    metric_name: str
    value: float
    metric_type: str = "gauge"
    unit: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    timestamp: Optional[datetime] = None


class MetricQueryRequest(BaseModel):
    service_id: str
    metric_name: str
    start_time: datetime
    end_time: datetime
    aggregation: str = "avg"
    interval: str = "5m"
    labels: Optional[Dict[str, str]] = None


class BatchMetricIngestRequest(BaseModel):
    metrics: List[MetricIngestRequest]


# ==================== ENDPOINTS ====================


@router.post("/ingest")
async def ingest_metric(request: MetricIngestRequest, db: Session = Depends(get_db)):
    """
    Ingest a single metric data point
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        metric_id = engine.ingest_metric(
            service_id=request.service_id,
            metric_name=request.metric_name,
            value=request.value,
            metric_type=request.metric_type,
            unit=request.unit,
            labels=request.labels,
            timestamp=request.timestamp,
        )

        return {"status": "success", "metric_id": metric_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/batch")
async def ingest_metrics_batch(
    request: BatchMetricIngestRequest, db: Session = Depends(get_db)
):
    """
    Ingest multiple metrics in batch
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)
    ingested_count = 0

    try:
        for metric in request.metrics:
            engine.ingest_metric(
                service_id=metric.service_id,
                metric_name=metric.metric_name,
                value=metric.value,
                metric_type=metric.metric_type,
                unit=metric.unit,
                labels=metric.labels,
                timestamp=metric.timestamp,
            )
            ingested_count += 1

        return {"status": "success", "ingested_count": ingested_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query_metrics(request: MetricQueryRequest, db: Session = Depends(get_db)):
    """
    Query metrics with aggregation
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        data = engine.query_metrics(
            service_id=request.service_id,
            metric_name=request.metric_name,
            start_time=request.start_time,
            end_time=request.end_time,
            aggregation=request.aggregation,
            interval=request.interval,
            labels=request.labels,
        )

        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/{service_id}/{metric_name}")
async def get_metric_statistics(
    service_id: str,
    metric_name: str,
    time_range: str = Query("1h", description="Time range (e.g., 1h, 24h, 7d)"),
    db: Session = Depends(get_db),
):
    """
    Get statistical summary of a metric
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        stats = engine.get_metric_statistics(
            service_id=service_id, metric_name=metric_name, time_range=time_range
        )

        return {"status": "success", "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{service_id}")
async def list_metrics(service_id: str, db: Session = Depends(get_db)):
    """
    List all metrics for a service
    """
    from ..models import Metric

    try:
        metrics = (
            db.query(Metric.metric_name)
            .filter(Metric.service_id == service_id)
            .distinct()
            .all()
        )

        return {"status": "success", "metrics": [m[0] for m in metrics]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies/{service_id}/{metric_name}")
async def detect_metric_anomalies(
    service_id: str,
    metric_name: str,
    time_range: str = Query("24h", description="Time range for anomaly detection"),
    db: Session = Depends(get_db),
):
    """
    Detect anomalies in metric data
    """
    from ..engine.observatory_engine import ObservatoryEngine

    engine = ObservatoryEngine(db)

    try:
        anomalies = engine.detect_anomalies(
            service_id=service_id, metric_name=metric_name, time_range=time_range
        )

        return {"status": "success", "anomalies": anomalies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dependency injection
def get_db():
    """Database session dependency"""
    # TODO: Implement database session management
    pass
