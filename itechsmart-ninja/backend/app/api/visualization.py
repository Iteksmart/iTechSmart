"""
Visualization API Routes
Provides endpoints for data visualization and dashboard creation
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, Chart, Dashboard
from app.integrations.data_visualization import DataVisualizationClient

router = APIRouter(prefix="/api/visualization", tags=["visualization"])

# Initialize visualization client
viz_client = DataVisualizationClient()


@router.post("/charts/create")
async def create_chart(
    chart_type: str,
    data: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new chart

    Args:
        chart_type: Type of chart (bar, line, pie, etc.)
        data: Chart data
        options: Chart options (title, colors, etc.)

    Returns:
        Chart object with ID and configuration
    """
    try:
        chart = await viz_client.create_chart(chart_type, data, options)

        # Save chart to database
        chart_db = Chart(
            user_id=current_user.id,
            chart_id=chart["chart_id"],
            chart_type=chart_type,
            title=(
                options.get("title", "Untitled Chart") if options else "Untitled Chart"
            ),
            description=options.get("description", "") if options else "",
            data=data,
            options=options or {},
            is_public=options.get("is_public", False) if options else False,
            tags=options.get("tags", []) if options else [],
        )
        db.add(chart_db)
        db.commit()
        db.refresh(chart_db)

        return {
            "success": True,
            "chart": chart,
            "chart_id": chart_db.id,
            "message": "Chart created successfully",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts")
async def list_charts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all charts for current user"""
    try:
        charts = (
            db.query(Chart)
            .filter(Chart.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        chart_list = []
        for chart in charts:
            chart_list.append(
                {
                    "id": chart.id,
                    "chart_id": chart.chart_id,
                    "chart_type": chart.chart_type,
                    "title": chart.title,
                    "description": chart.description,
                    "is_public": chart.is_public,
                    "tags": chart.tags,
                    "created_at": (
                        chart.created_at.isoformat() if chart.created_at else None
                    ),
                    "updated_at": (
                        chart.updated_at.isoformat() if chart.updated_at else None
                    ),
                }
            )

        return {
            "success": True,
            "charts": chart_list,
            "total": len(chart_list),
            "message": "Charts retrieved successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/{chart_id}")
async def get_chart(
    chart_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get specific chart by ID"""
    try:
        chart = (
            db.query(Chart)
            .filter(Chart.chart_id == chart_id, Chart.user_id == current_user.id)
            .first()
        )

        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")

        return {
            "success": True,
            "chart": {
                "id": chart.id,
                "chart_id": chart.chart_id,
                "chart_type": chart.chart_type,
                "title": chart.title,
                "description": chart.description,
                "data": chart.data,
                "options": chart.options,
                "is_public": chart.is_public,
                "tags": chart.tags,
                "created_at": (
                    chart.created_at.isoformat() if chart.created_at else None
                ),
                "updated_at": (
                    chart.updated_at.isoformat() if chart.updated_at else None
                ),
            },
            "message": "Chart retrieved successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/charts/{chart_id}")
async def update_chart(
    chart_id: str,
    data: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update existing chart"""
    try:
        chart = (
            db.query(Chart)
            .filter(Chart.chart_id == chart_id, Chart.user_id == current_user.id)
            .first()
        )

        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")

        # Update fields if provided
        if data is not None:
            chart.data = data
        if options is not None:
            chart.options = options
        if title is not None:
            chart.title = title
        if description is not None:
            chart.description = description

        db.commit()
        db.refresh(chart)

        return {
            "success": True,
            "chart": {
                "id": chart.id,
                "chart_id": chart.chart_id,
                "title": chart.title,
                "updated_at": (
                    chart.updated_at.isoformat() if chart.updated_at else None
                ),
            },
            "message": "Chart updated successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/charts/{chart_id}")
async def delete_chart(
    chart_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete chart"""
    try:
        chart = (
            db.query(Chart)
            .filter(Chart.chart_id == chart_id, Chart.user_id == current_user.id)
            .first()
        )

        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")

        db.delete(chart)
        db.commit()

        return {"success": True, "message": "Chart deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/charts/{chart_id}/export")
async def export_chart(
    chart_id: str,
    format: str = "png",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export chart to specified format

    Args:
        chart_id: Chart ID
        format: Export format (png, svg, pdf, html, json)
    """
    try:
        result = await viz_client.export_chart(chart_id, format)
        return {
            "success": True,
            "export": result,
            "message": f"Chart exported as {format}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboards/create")
async def create_dashboard(
    title: str,
    charts: List[str],
    layout: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create dashboard with multiple charts"""
    try:
        # Generate dashboard ID
        import uuid

        dashboard_id = f"dashboard_{uuid.uuid4().hex[:12]}"

        # Create dashboard
        dashboard_db = Dashboard(
            user_id=current_user.id,
            dashboard_id=dashboard_id,
            title=title,
            description=description or "",
            layout=layout or {"columns": 2, "spacing": 20, "responsive": True},
            chart_ids=charts,
            is_public=False,
            tags=[],
        )
        db.add(dashboard_db)
        db.commit()
        db.refresh(dashboard_db)

        return {
            "success": True,
            "dashboard": {
                "id": dashboard_db.id,
                "dashboard_id": dashboard_db.dashboard_id,
                "title": dashboard_db.title,
                "chart_ids": dashboard_db.chart_ids,
                "layout": dashboard_db.layout,
                "created_at": (
                    dashboard_db.created_at.isoformat()
                    if dashboard_db.created_at
                    else None
                ),
            },
            "message": "Dashboard created successfully",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboards")
async def list_dashboards(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all dashboards"""
    try:
        dashboards = (
            db.query(Dashboard)
            .filter(Dashboard.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        dashboard_list = []
        for dashboard in dashboards:
            dashboard_list.append(
                {
                    "id": dashboard.id,
                    "dashboard_id": dashboard.dashboard_id,
                    "title": dashboard.title,
                    "description": dashboard.description,
                    "chart_count": (
                        len(dashboard.chart_ids) if dashboard.chart_ids else 0
                    ),
                    "is_public": dashboard.is_public,
                    "created_at": (
                        dashboard.created_at.isoformat()
                        if dashboard.created_at
                        else None
                    ),
                    "updated_at": (
                        dashboard.updated_at.isoformat()
                        if dashboard.updated_at
                        else None
                    ),
                }
            )

        return {
            "success": True,
            "dashboards": dashboard_list,
            "total": len(dashboard_list),
            "message": "Dashboards retrieved successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_data(
    data: List[float],
    analysis_type: str = "basic",
    current_user: User = Depends(get_current_user),
):
    """
    Analyze data and provide statistics

    Args:
        data: Data to analyze
        analysis_type: Type of analysis (basic, advanced, statistical)
    """
    try:
        result = await viz_client.analyze_data(data, analysis_type)
        return {
            "success": True,
            "analysis": result,
            "message": "Data analyzed successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart-types")
async def get_chart_types():
    """Get list of supported chart types"""
    try:
        chart_types = await viz_client.get_chart_types()
        return {
            "success": True,
            "chart_types": chart_types,
            "message": "Chart types retrieved successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
