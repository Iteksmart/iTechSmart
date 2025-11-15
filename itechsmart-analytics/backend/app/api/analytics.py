"""
iTechSmart Analytics - Analytics API Endpoints
REST API for analytics, forecasting, and insights
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd

from app.core.analytics_engine import AnalyticsEngine
from app.core.dashboard_builder import DashboardBuilder, WidgetType
from app.core.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Pydantic models
class ForecastRequest(BaseModel):
    metric: str
    data_source: str
    horizon: int = 30
    model_type: str = "auto"


class AnomalyDetectionRequest(BaseModel):
    metric: str
    data_source: str
    sensitivity: str = "medium"


class TrendAnalysisRequest(BaseModel):
    metric: str
    data_source: str
    period: str = "daily"


class CorrelationRequest(BaseModel):
    metrics: List[str]
    data_source: str


class DashboardCreateRequest(BaseModel):
    name: str
    description: str
    layout: Optional[Dict[str, Any]] = None


class WidgetCreateRequest(BaseModel):
    type: str
    title: str
    data_source: str
    config: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None


@router.post("/forecast")
async def generate_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate forecast for a metric
    
    Args:
        metric: Metric name to forecast
        data_source: Data source identifier
        horizon: Forecast horizon in days (default: 30)
        model_type: Model type (auto, linear, rf, prophet)
    
    Returns:
        Forecast results with confidence intervals
    """
    
    engine = AnalyticsEngine(db)
    
    # Fetch historical data (mock for now)
    data = await _fetch_data(request.data_source, request.metric)
    
    if data.empty:
        raise HTTPException(status_code=404, detail="No data found")
    
    result = await engine.forecast(
        request.metric,
        data,
        request.horizon,
        request.model_type
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/anomalies")
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Detect anomalies in metric data
    
    Args:
        metric: Metric name
        data_source: Data source identifier
        sensitivity: Detection sensitivity (low, medium, high)
    
    Returns:
        Detected anomalies with scores and severity
    """
    
    engine = AnalyticsEngine(db)
    
    # Fetch historical data
    data = await _fetch_data(request.data_source, request.metric)
    
    if data.empty:
        raise HTTPException(status_code=404, detail="No data found")
    
    result = await engine.detect_anomalies(
        request.metric,
        data,
        request.sensitivity
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/trends")
async def analyze_trends(
    request: TrendAnalysisRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze trends in metric data
    
    Args:
        metric: Metric name
        data_source: Data source identifier
        period: Aggregation period (hourly, daily, weekly, monthly)
    
    Returns:
        Trend analysis with direction, strength, and statistics
    """
    
    engine = AnalyticsEngine(db)
    
    # Fetch historical data
    data = await _fetch_data(request.data_source, request.metric)
    
    if data.empty:
        raise HTTPException(status_code=404, detail="No data found")
    
    result = await engine.analyze_trends(
        request.metric,
        data,
        request.period
    )
    
    return result


@router.post("/correlation")
async def analyze_correlation(
    request: CorrelationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze correlations between metrics
    
    Args:
        metrics: List of metric names
        data_source: Data source identifier
    
    Returns:
        Correlation matrix and strong correlations
    """
    
    engine = AnalyticsEngine(db)
    
    # Fetch data for all metrics
    data = await _fetch_multi_metric_data(request.data_source, request.metrics)
    
    if data.empty:
        raise HTTPException(status_code=404, detail="No data found")
    
    result = await engine.correlation_analysis(request.metrics, data)
    
    return result


@router.get("/insights/{data_source}")
async def get_insights(
    data_source: str,
    metric: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get automated insights for data source
    
    Args:
        data_source: Data source identifier
        metric: Optional specific metric
    
    Returns:
        Automated insights and recommendations
    """
    
    engine = AnalyticsEngine(db)
    
    insights = {
        "data_source": data_source,
        "generated_at": datetime.utcnow().isoformat(),
        "insights": []
    }
    
    # Fetch data
    if metric:
        data = await _fetch_data(data_source, metric)
        
        # Run multiple analyses
        trend = await engine.analyze_trends(metric, data)
        anomalies = await engine.detect_anomalies(metric, data)
        
        insights["insights"].append({
            "type": "trend",
            "metric": metric,
            "summary": f"Metric is {trend['trend_direction']} with {trend['trend_strength']:.1f}% strength",
            "details": trend
        })
        
        if anomalies["anomalies_detected"] > 0:
            insights["insights"].append({
                "type": "anomaly",
                "metric": metric,
                "summary": f"Detected {anomalies['anomalies_detected']} anomalies",
                "details": anomalies
            })
    
    return insights


# Dashboard endpoints
@router.post("/dashboards")
async def create_dashboard(
    request: DashboardCreateRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create new analytics dashboard
    
    Args:
        name: Dashboard name
        description: Dashboard description
        user_id: Owner user ID
        layout: Optional layout configuration
    
    Returns:
        Created dashboard details
    """
    
    builder = DashboardBuilder(db)
    
    dashboard = await builder.create_dashboard(
        request.name,
        request.description,
        user_id,
        request.layout
    )
    
    return dashboard


@router.get("/dashboards")
async def list_dashboards(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    List analytics dashboards
    
    Args:
        user_id: Optional filter by user ID
    
    Returns:
        List of dashboards
    """
    
    builder = DashboardBuilder(db)
    dashboards = await builder.list_dashboards(user_id)
    
    return dashboards


@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(
    dashboard_id: int,
    include_data: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard details
    
    Args:
        dashboard_id: Dashboard ID
        include_data: Whether to include widget data
    
    Returns:
        Dashboard details with widgets
    """
    
    builder = DashboardBuilder(db)
    dashboard = await builder.get_dashboard(dashboard_id, include_data)
    
    return dashboard


@router.post("/dashboards/{dashboard_id}/widgets")
async def add_widget(
    dashboard_id: int,
    request: WidgetCreateRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Add widget to dashboard
    
    Args:
        dashboard_id: Dashboard ID
        Widget configuration
    
    Returns:
        Created widget details
    """
    
    builder = DashboardBuilder(db)
    
    widget_config = {
        "type": request.type,
        "title": request.title,
        "data_source": request.data_source,
        "config": request.config,
        "position": request.position
    }
    
    widget = await builder.add_widget(dashboard_id, widget_config)
    
    return widget


@router.delete("/dashboards/{dashboard_id}/widgets/{widget_id}")
async def remove_widget(
    dashboard_id: int,
    widget_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Remove widget from dashboard
    
    Args:
        dashboard_id: Dashboard ID
        widget_id: Widget ID
    
    Returns:
        Success message
    """
    
    builder = DashboardBuilder(db)
    result = await builder.remove_widget(dashboard_id, widget_id)
    
    return result


@router.post("/dashboards/{dashboard_id}/duplicate")
async def duplicate_dashboard(
    dashboard_id: int,
    new_name: str = Query(...),
    user_id: int = Query(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Duplicate existing dashboard
    
    Args:
        dashboard_id: Source dashboard ID
        new_name: Name for duplicated dashboard
        user_id: Owner user ID
    
    Returns:
        Duplicated dashboard details
    """
    
    builder = DashboardBuilder(db)
    duplicate = await builder.duplicate_dashboard(dashboard_id, new_name, user_id)
    
    return duplicate


# Helper functions
async def _fetch_data(data_source: str, metric: str) -> pd.DataFrame:
    """Fetch data from data source (mock implementation)"""
    
    # Generate sample data
    dates = pd.date_range(
        start=datetime.utcnow() - timedelta(days=90),
        end=datetime.utcnow(),
        freq='D'
    )
    
    import numpy as np
    values = np.random.randn(len(dates)).cumsum() + 100
    
    return pd.DataFrame({
        'timestamp': dates,
        metric: values
    })


async def _fetch_multi_metric_data(
    data_source: str,
    metrics: List[str]
) -> pd.DataFrame:
    """Fetch data for multiple metrics"""
    
    dates = pd.date_range(
        start=datetime.utcnow() - timedelta(days=90),
        end=datetime.utcnow(),
        freq='D'
    )
    
    import numpy as np
    data = {'timestamp': dates}
    
    for metric in metrics:
        data[metric] = np.random.randn(len(dates)).cumsum() + 100
    
    return pd.DataFrame(data)