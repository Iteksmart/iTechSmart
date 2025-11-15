"""
PDF Export Service for Impact Reports
"""
from typing import Dict, Any, Optional
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import HexColor


class PDFExporter:
    """Export impact reports to PDF"""
    
    def __init__(self):
        """Initialize PDF exporter"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=32,
            textColor=HexColor('#2b6cb0'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def export_report(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Export report to PDF
        
        Args:
            report_data: Report data dictionary
            output_path: Optional file path to save PDF
            
        Returns:
            PDF bytes
        """
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Add cover page
        story.extend(self._create_cover_page(report_data))
        story.append(PageBreak())
        
        # Add table of contents
        story.extend(self._create_table_of_contents(report_data))
        story.append(PageBreak())
        
        # Add report sections
        for section_name, section_content in report_data.get("sections", {}).items():
            story.extend(self._create_section(section_name, section_content))
            story.append(Spacer(1, 0.2 * inch))
        
        # Add charts
        if report_data.get("charts_data"):
            story.append(PageBreak())
            story.extend(self._create_charts_page(report_data["charts_data"]))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _create_cover_page(self, report_data: Dict[str, Any]) -> list:
        """Create cover page"""
        elements = []
        
        # Add logo placeholder
        elements.append(Spacer(1, 1 * inch))
        
        # Title
        title = Paragraph(report_data.get("title", "Impact Report"), self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Organization name
        org_name = Paragraph(
            report_data.get("organization_name", ""),
            self.styles['Heading2']
        )
        elements.append(org_name)
        elements.append(Spacer(1, 0.5 * inch))
        
        # Period
        period_start = datetime.fromisoformat(report_data["period_start"]).strftime("%B %d, %Y")
        period_end = datetime.fromisoformat(report_data["period_end"]).strftime("%B %d, %Y")
        period_text = f"Reporting Period: {period_start} - {period_end}"
        period = Paragraph(period_text, self.styles['Normal'])
        elements.append(period)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Generated date
        generated_date = datetime.fromisoformat(report_data["generated_at"]).strftime("%B %d, %Y")
        date_text = f"Generated: {generated_date}"
        date = Paragraph(date_text, self.styles['Normal'])
        elements.append(date)
        
        return elements
    
    def _create_table_of_contents(self, report_data: Dict[str, Any]) -> list:
        """Create table of contents"""
        elements = []
        
        # TOC title
        toc_title = Paragraph("Table of Contents", self.styles['Heading1'])
        elements.append(toc_title)
        elements.append(Spacer(1, 0.3 * inch))
        
        # TOC entries
        sections = report_data.get("sections", {})
        for i, section_name in enumerate(sections.keys(), 1):
            formatted_name = section_name.replace("_", " ").title()
            toc_entry = Paragraph(f"{i}. {formatted_name}", self.styles['Normal'])
            elements.append(toc_entry)
            elements.append(Spacer(1, 0.1 * inch))
        
        return elements
    
    def _create_section(self, section_name: str, section_content: str) -> list:
        """Create a report section"""
        elements = []
        
        # Section heading
        formatted_name = section_name.replace("_", " ").title()
        heading = Paragraph(formatted_name, self.styles['SectionHeading'])
        elements.append(heading)
        
        # Section content
        # Split content into paragraphs
        paragraphs = section_content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                p = Paragraph(para.strip(), self.styles['BodyText'])
                elements.append(p)
        
        return elements
    
    def _create_charts_page(self, charts_data: Dict[str, Any]) -> list:
        """Create charts page"""
        elements = []
        
        # Charts title
        title = Paragraph("Data Visualizations", self.styles['Heading1'])
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Add each chart
        for chart_name, chart_info in charts_data.items():
            chart_title = Paragraph(chart_info.get("title", chart_name), self.styles['SectionHeading'])
            elements.append(chart_title)
            
            # Create chart based on type
            if chart_info["type"] == "bar":
                chart = self._create_bar_chart(chart_info)
            elif chart_info["type"] == "pie":
                chart = self._create_pie_chart(chart_info)
            else:
                chart = None
            
            if chart:
                elements.append(chart)
            
            elements.append(Spacer(1, 0.5 * inch))
        
        return elements
    
    def _create_bar_chart(self, chart_info: Dict[str, Any]) -> Drawing:
        """Create a bar chart"""
        drawing = Drawing(400, 200)
        
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        
        data = chart_info.get("data", [])
        if data:
            chart.data = [[item.get("current", 0) for item in data]]
            chart.categoryAxis.categoryNames = [item.get("metric", "") for item in data]
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = max([item.get("target", 100) for item in data]) * 1.2
        
        chart.bars[0].fillColor = HexColor('#2b6cb0')
        
        drawing.add(chart)
        return drawing
    
    def _create_pie_chart(self, chart_info: Dict[str, Any]) -> Drawing:
        """Create a pie chart"""
        drawing = Drawing(400, 200)
        
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 100
        pie.height = 100
        
        data = chart_info.get("data", [])
        if data:
            pie.data = [item.get("value", 0) for item in data]
            pie.labels = [item.get("label", "") for item in data]
        
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = HexColor('#2b6cb0')
        pie.slices[1].fillColor = HexColor('#4299e1')
        pie.slices[2].fillColor = HexColor('#90cdf4')
        
        drawing.add(pie)
        return drawing
    
    def create_metrics_summary_table(self, metrics: list) -> Table:
        """Create a metrics summary table"""
        # Table data
        data = [['Metric', 'Current', 'Target', 'Achievement']]
        
        for metric in metrics:
            data.append([
                metric.get('name', ''),
                f"{metric.get('current_value', 0):.1f}",
                f"{metric.get('target_value', 0):.1f}",
                f"{metric.get('achievement_rate', 0):.1f}%"
            ])
        
        # Create table
        table = Table(data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
        
        # Style table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table