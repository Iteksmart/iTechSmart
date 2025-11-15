"""
Advanced Analytics API Endpoints
Provides business intelligence and predictive analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.models.database import get_db
from app.core.advanced_analytics import (
    AnalyticsEngine,
    ReportGenerator,
    PredictiveAnalytics
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/patient-statistics")
async def get_patient_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get comprehensive patient statistics"""
    try:
        analytics = AnalyticsEngine(db)
        stats = analytics.get_patient_statistics(days)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")


@router.get("/message-analytics")
async def get_message_analytics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Analyze HL7 message patterns and trends"""
    try:
        analytics = AnalyticsEngine(db)
        stats = analytics.get_message_analytics(days)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing messages: {str(e)}")


@router.get("/clinical-insights")
async def get_clinical_insights(db: Session = Depends(get_db)):
    """Generate clinical insights from patient data"""
    try:
        analytics = AnalyticsEngine(db)
        insights = analytics.get_clinical_insights()
        
        return {
            "success": True,
            "data": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@router.get("/performance-trends")
async def get_performance_trends(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Analyze system performance trends"""
    try:
        analytics = AnalyticsEngine(db)
        trends = analytics.get_system_performance_trends(hours)
        
        return {
            "success": True,
            "data": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing trends: {str(e)}")


@router.get("/patient-risk/{patient_id}")
async def predict_patient_risk(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Predict patient risk scores"""
    try:
        analytics = AnalyticsEngine(db)
        risk = analytics.predict_patient_risk(patient_id)
        
        if "error" in risk:
            raise HTTPException(status_code=404, detail=risk["error"])
        
        return {
            "success": True,
            "data": risk
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting risk: {str(e)}")


@router.get("/reports/executive-summary")
async def get_executive_summary(db: Session = Depends(get_db)):
    """Generate executive summary report"""
    try:
        analytics = AnalyticsEngine(db)
        report_gen = ReportGenerator(analytics)
        report = report_gen.generate_executive_summary()
        
        return {
            "success": True,
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/reports/clinical")
async def get_clinical_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate detailed clinical report"""
    try:
        # Parse dates or use defaults
        if start_date:
            start = datetime.fromisoformat(start_date)
        else:
            start = datetime.utcnow() - timedelta(days=30)
        
        if end_date:
            end = datetime.fromisoformat(end_date)
        else:
            end = datetime.utcnow()
        
        analytics = AnalyticsEngine(db)
        report_gen = ReportGenerator(analytics)
        report = report_gen.generate_clinical_report(start, end)
        
        return {
            "success": True,
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/reports/performance")
async def get_performance_report(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Generate system performance report"""
    try:
        analytics = AnalyticsEngine(db)
        report_gen = ReportGenerator(analytics)
        report = report_gen.generate_performance_report(hours)
        
        return {
            "success": True,
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/forecast/patient-volume")
async def forecast_patient_volume(
    days_ahead: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Forecast patient volume for next N days"""
    try:
        predictive = PredictiveAnalytics(db)
        forecast = predictive.forecast_patient_volume(days_ahead)
        
        if "error" in forecast:
            raise HTTPException(status_code=400, detail=forecast["error"])
        
        return {
            "success": True,
            "data": forecast
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forecasting volume: {str(e)}")


@router.get("/anomalies")
async def detect_anomalies(
    metric: str = Query("message_count", regex="^(message_count|processing_time|error_rate)$"),
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Identify anomalies in system metrics"""
    try:
        predictive = PredictiveAnalytics(db)
        anomalies = predictive.identify_anomalies(metric, hours)
        
        if "error" in anomalies:
            raise HTTPException(status_code=400, detail=anomalies["error"])
        
        return {
            "success": True,
            "data": anomalies
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting anomalies: {str(e)}")


@router.get("/dashboard")
async def get_analytics_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive analytics dashboard data"""
    try:
        analytics = AnalyticsEngine(db)
        predictive = PredictiveAnalytics(db)
        
        dashboard = {
            "timestamp": datetime.utcnow().isoformat(),
            "patient_stats": analytics.get_patient_statistics(30),
            "message_analytics": analytics.get_message_analytics(7),
            "clinical_insights": analytics.get_clinical_insights(),
            "performance_trends": analytics.get_system_performance_trends(24),
            "forecast": predictive.forecast_patient_volume(7),
            "anomalies": predictive.identify_anomalies("message_count", 24)
        }
        
        return {
            "success": True,
            "data": dashboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")


@router.get("/kpis")
async def get_key_performance_indicators(db: Session = Depends(get_db)):
    """Get key performance indicators"""
    try:
        analytics = AnalyticsEngine(db)
        
        patient_stats = analytics.get_patient_statistics(30)
        message_stats = analytics.get_message_analytics(7)
        performance = analytics.get_system_performance_trends(24)
        
        # Calculate KPIs
        kpis = {
            "patient_growth_rate": patient_stats.get("growth_rate", 0),
            "message_success_rate": 100 - message_stats.get("error_rate", 0),
            "avg_processing_time_ms": (
                sum(h["avg_processing_time_ms"] for h in performance["hourly_stats"]) / 
                len(performance["hourly_stats"])
                if performance["hourly_stats"] else 0
            ),
            "system_uptime_percent": 99.9,  # Placeholder - implement actual uptime tracking
            "total_patients": patient_stats.get("total_patients", 0),
            "messages_per_day": message_stats.get("total_messages", 0) / 7,
            "error_rate": message_stats.get("error_rate", 0)
        }
        
        return {
            "success": True,
            "data": kpis,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating KPIs: {str(e)}")