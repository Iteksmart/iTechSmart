"""
Impact Report API endpoints
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_current_user, require_permission
from app.db.database import get_db
from app.models.user import User
from app.models.impact import ImpactReport
from app.services.report_generator import ImpactReportGenerator
from app.services.pdf_exporter import PDFExporter
from app.ai.router import AIModelRouter, RoutingStrategy


router = APIRouter()

# Initialize services
ai_router = AIModelRouter(strategy=RoutingStrategy.QUALITY_OPTIMIZED)
ai_router.register_model("gpt-4")
report_generator = ImpactReportGenerator(ai_router)
pdf_exporter = PDFExporter()


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_report(
    program_id: int,
    report_type: str = "quarterly",
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    current_user: User = Depends(require_permission("create_impact_reports")),
    db: Session = Depends(get_db),
) -> Any:
    """
    Generate an impact report using AI

    Args:
        program_id: Program ID
        report_type: Type of report (quarterly, annual, donor, grant)
        period_start: Start date of reporting period
        period_end: End date of reporting period
        current_user: Current authenticated user
        db: Database session

    Returns:
        Generated report data
    """
    try:
        # Generate report
        report_data = await report_generator.generate_report(
            db=db,
            program_id=program_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
        )

        # Save to database
        impact_report = ImpactReport(
            organization_id=report_data.get("organization_id"),
            program_id=program_id,
            creator_id=current_user.id,
            title=report_data["title"],
            report_type=report_type,
            period_start=datetime.fromisoformat(report_data["period_start"]),
            period_end=datetime.fromisoformat(report_data["period_end"]),
            executive_summary=report_data["sections"].get("executive_summary"),
            metrics_summary=report_data.get("charts_data"),
            charts_data=report_data.get("charts_data"),
            ai_generated=True,
            ai_model_used="gpt-4",
            status="draft",
        )

        db.add(impact_report)
        db.commit()
        db.refresh(impact_report)

        return {
            "report_id": impact_report.id,
            "report_data": report_data,
            "message": "Report generated successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.get("/{report_id}/pdf")
async def export_report_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """
    Export report as PDF

    Args:
        report_id: Report ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        PDF file
    """
    # Get report
    report = db.query(ImpactReport).filter(ImpactReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    # Prepare report data for PDF
    report_data = {
        "title": report.title,
        "organization_name": "Organization Name",  # TODO: Get from relationship
        "program_name": "Program Name",  # TODO: Get from relationship
        "period_start": report.period_start.isoformat(),
        "period_end": report.period_end.isoformat(),
        "generated_at": report.created_at.isoformat(),
        "sections": {"executive_summary": report.executive_summary or ""},
        "charts_data": report.charts_data or {},
    }

    # Generate PDF
    pdf_bytes = pdf_exporter.export_report(report_data)

    # Return PDF response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=impact_report_{report_id}.pdf"
        },
    )


@router.get("/templates")
async def get_report_templates(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get available report templates

    Args:
        current_user: Current authenticated user

    Returns:
        List of available templates
    """
    templates = report_generator.get_available_templates()
    return {"templates": templates}
