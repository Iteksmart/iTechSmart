"""
iTechSmart Analytics - Reports API Endpoints
REST API for report generation and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from app.core.report_generator import (
    ReportGenerator,
    ReportFormat,
    ReportFrequency,
    DeliveryMethod,
)
from app.core.database import get_db

router = APIRouter(prefix="/api/reports", tags=["reports"])


# Pydantic models
class ReportCreateRequest(BaseModel):
    name: str
    description: str
    data_sources: List[int]
    metrics: List[str]
    format: str = "pdf"
    template: Optional[str] = None


class GenerateReportRequest(BaseModel):
    report_id: int
    date_range: Optional[Dict[str, str]] = None
    filters: Optional[Dict[str, Any]] = None


class ScheduleReportRequest(BaseModel):
    report_id: int
    frequency: str
    delivery_method: str
    delivery_config: Dict[str, Any]
    filters: Optional[Dict[str, Any]] = None


class CustomReportRequest(BaseModel):
    title: str
    sections: List[Dict[str, Any]]
    format: str = "pdf"


class ExportDataRequest(BaseModel):
    data_source_id: int
    metrics: List[str]
    format: str
    date_range: Optional[Dict[str, str]] = None


@router.post("/")
async def create_report(
    request: ReportCreateRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new report definition

    Args:
        name: Report name
        description: Report description
        data_sources: List of data source IDs
        metrics: List of metrics to include
        format: Output format (pdf, excel, csv, html, json)
        template: Optional template name

    Returns:
        Created report details
    """

    generator = ReportGenerator(db)

    try:
        format_enum = ReportFormat(request.format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid format: {request.format}")

    report = await generator.create_report(
        request.name,
        request.description,
        request.data_sources,
        request.metrics,
        format_enum,
        request.template,
    )

    return report


@router.post("/generate")
async def generate_report(
    request: GenerateReportRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate a report

    Args:
        report_id: Report ID
        date_range: Optional date range filter
        filters: Optional additional filters

    Returns:
        Generated report with data
    """

    generator = ReportGenerator(db)

    result = await generator.generate_report(
        request.report_id, request.date_range, request.filters
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@router.post("/schedule")
async def schedule_report(
    request: ScheduleReportRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Schedule automated report generation

    Args:
        report_id: Report ID
        frequency: Generation frequency (daily, weekly, monthly, quarterly)
        delivery_method: How to deliver (email, download, api, webhook, storage)
        delivery_config: Delivery configuration
        filters: Optional filters

    Returns:
        Scheduled report details
    """

    generator = ReportGenerator(db)

    try:
        frequency_enum = ReportFrequency(request.frequency)
        delivery_enum = DeliveryMethod(request.delivery_method)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")

    schedule = await generator.schedule_report(
        request.report_id,
        frequency_enum,
        delivery_enum,
        request.delivery_config,
        request.filters,
    )

    return schedule


@router.get("/")
async def list_reports(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    List all report definitions

    Returns:
        List of reports
    """

    # In production, query from database
    return []


@router.get("/{report_id}")
async def get_report(report_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get report definition

    Args:
        report_id: Report ID

    Returns:
        Report details
    """

    generator = ReportGenerator(db)
    report = await generator._get_report(report_id)

    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: int, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete a report definition

    Args:
        report_id: Report ID

    Returns:
        Success message
    """

    # In production, delete from database
    return {"status": "success", "message": f"Report {report_id} deleted"}


@router.post("/dashboard/{dashboard_id}")
async def generate_dashboard_report(
    dashboard_id: int,
    format: str = Query("pdf"),
    include_data: bool = Query(True),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate report from dashboard

    Args:
        dashboard_id: Dashboard ID
        format: Output format
        include_data: Whether to include raw data

    Returns:
        Generated dashboard report
    """

    generator = ReportGenerator(db)

    try:
        format_enum = ReportFormat(format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid format: {format}")

    result = await generator.create_dashboard_report(
        dashboard_id, format_enum, include_data
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@router.post("/custom")
async def create_custom_report(
    request: CustomReportRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create custom report with multiple sections

    Args:
        title: Report title
        sections: List of report sections
        format: Output format

    Returns:
        Generated custom report
    """

    generator = ReportGenerator(db)

    try:
        format_enum = ReportFormat(request.format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid format: {request.format}")

    result = await generator.create_custom_report(
        request.title, request.sections, format_enum
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@router.post("/export")
async def export_data(
    request: ExportDataRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Export raw data

    Args:
        data_source_id: Data source ID
        metrics: Metrics to export
        format: Export format
        date_range: Optional date range

    Returns:
        Exported data
    """

    generator = ReportGenerator(db)

    try:
        format_enum = ReportFormat(request.format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid format: {request.format}")

    result = await generator.export_data(
        request.data_source_id, request.metrics, format_enum, request.date_range
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@router.get("/templates/executive-summary")
async def generate_executive_summary(
    data_sources: List[int] = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate executive summary report

    Args:
        data_sources: List of data source IDs
        start_date: Start date (ISO format)
        end_date: End date (ISO format)

    Returns:
        Executive summary report
    """

    generator = ReportGenerator(db)

    date_range = {"start": start_date, "end": end_date}

    result = await generator.create_executive_summary(data_sources, date_range)

    return result


@router.get("/templates/performance")
async def generate_performance_report(
    data_sources: List[int] = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate performance report

    Args:
        data_sources: List of data source IDs
        start_date: Start date (ISO format)
        end_date: End date (ISO format)

    Returns:
        Performance report
    """

    generator = ReportGenerator(db)

    date_range = {"start": start_date, "end": end_date}

    result = await generator.create_performance_report(data_sources, date_range)

    return result


@router.get("/scheduled")
async def list_scheduled_reports(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    List all scheduled reports

    Returns:
        List of scheduled reports
    """

    # In production, query from database
    return []


@router.delete("/scheduled/{schedule_id}")
async def cancel_scheduled_report(
    schedule_id: int, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Cancel a scheduled report

    Args:
        schedule_id: Schedule ID

    Returns:
        Success message
    """

    # In production, delete from database
    return {"status": "success", "message": f"Scheduled report {schedule_id} cancelled"}
