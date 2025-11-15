"""
Impact Report Generator Service
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from app.models.impact import ImpactReport, Evidence
from app.models.program import Program, ProgramMetric
from app.models.user import Organization
from app.ai.router import AIModelRouter
from app.ai.context import ConversationContext


class ReportTemplate:
    """Report template definitions"""
    
    QUARTERLY_TEMPLATE = {
        "name": "Quarterly Impact Report",
        "sections": [
            "executive_summary",
            "program_overview",
            "key_metrics",
            "success_stories",
            "challenges",
            "financial_summary",
            "next_quarter_plans"
        ],
        "charts": ["metrics_progress", "beneficiary_demographics", "budget_utilization"]
    }
    
    ANNUAL_TEMPLATE = {
        "name": "Annual Impact Report",
        "sections": [
            "executive_summary",
            "year_in_review",
            "program_highlights",
            "impact_metrics",
            "success_stories",
            "financial_overview",
            "challenges_and_learnings",
            "future_vision",
            "acknowledgments"
        ],
        "charts": [
            "annual_metrics",
            "beneficiary_growth",
            "program_distribution",
            "financial_breakdown",
            "geographic_reach"
        ]
    }
    
    DONOR_TEMPLATE = {
        "name": "Donor Impact Report",
        "sections": [
            "thank_you_message",
            "your_impact",
            "program_results",
            "beneficiary_stories",
            "financial_transparency",
            "future_plans"
        ],
        "charts": ["donation_impact", "program_outcomes", "cost_per_beneficiary"]
    }
    
    GRANT_TEMPLATE = {
        "name": "Grant Impact Report",
        "sections": [
            "executive_summary",
            "grant_objectives_review",
            "activities_completed",
            "outcomes_achieved",
            "metrics_analysis",
            "budget_report",
            "challenges_and_solutions",
            "sustainability_plan"
        ],
        "charts": ["objectives_progress", "budget_vs_actual", "outcome_metrics"]
    }


class ImpactReportGenerator:
    """Generate impact reports with AI assistance"""
    
    def __init__(self, ai_router: AIModelRouter):
        """
        Initialize report generator
        
        Args:
            ai_router: AI model router for text generation
        """
        self.ai_router = ai_router
        self.templates = {
            "quarterly": ReportTemplate.QUARTERLY_TEMPLATE,
            "annual": ReportTemplate.ANNUAL_TEMPLATE,
            "donor": ReportTemplate.DONOR_TEMPLATE,
            "grant": ReportTemplate.GRANT_TEMPLATE
        }
    
    async def generate_report(
        self,
        db: Session,
        program_id: int,
        report_type: str = "quarterly",
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        custom_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate an impact report
        
        Args:
            db: Database session
            program_id: Program ID
            report_type: Type of report (quarterly, annual, donor, grant)
            period_start: Start date of reporting period
            period_end: End date of reporting period
            custom_sections: Custom sections to include
            
        Returns:
            Generated report data
        """
        # Get program data
        program = db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise ValueError(f"Program not found: {program_id}")
        
        # Get organization data
        organization = db.query(Organization).filter(
            Organization.id == program.organization_id
        ).first()
        
        # Set default period if not provided
        if not period_end:
            period_end = datetime.utcnow()
        if not period_start:
            if report_type == "quarterly":
                period_start = period_end - timedelta(days=90)
            elif report_type == "annual":
                period_start = period_end - timedelta(days=365)
            else:
                period_start = period_end - timedelta(days=90)
        
        # Get template
        template = self.templates.get(report_type, self.templates["quarterly"])
        sections_to_generate = custom_sections or template["sections"]
        
        # Collect program data
        program_data = await self._collect_program_data(db, program, period_start, period_end)
        
        # Generate report sections
        report_content = {}
        for section in sections_to_generate:
            content = await self._generate_section(
                section=section,
                program=program,
                organization=organization,
                program_data=program_data,
                period_start=period_start,
                period_end=period_end
            )
            report_content[section] = content
        
        # Generate visualizations
        charts_data = await self._generate_charts(
            program_data=program_data,
            chart_types=template.get("charts", [])
        )
        
        return {
            "title": f"{template['name']} - {program.name}",
            "report_type": report_type,
            "program_id": program_id,
            "program_name": program.name,
            "organization_name": organization.name,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "sections": report_content,
            "charts_data": charts_data,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_generated": True
        }
    
    async def _collect_program_data(
        self,
        db: Session,
        program: Program,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Collect program data for report generation"""
        
        # Get metrics
        metrics = db.query(ProgramMetric).filter(
            ProgramMetric.program_id == program.id,
            ProgramMetric.is_active == True
        ).all()
        
        metrics_data = []
        for metric in metrics:
            metrics_data.append({
                "name": metric.name,
                "description": metric.description,
                "category": metric.category,
                "unit": metric.unit,
                "target_value": metric.target_value,
                "current_value": metric.current_value,
                "achievement_rate": (metric.current_value / metric.target_value * 100) 
                    if metric.target_value else 0
            })
        
        # Get evidence
        evidence = db.query(Evidence).filter(
            Evidence.program_id == program.id,
            Evidence.date_collected >= period_start,
            Evidence.date_collected <= period_end
        ).all()
        
        evidence_data = []
        for ev in evidence:
            evidence_data.append({
                "title": ev.title,
                "type": ev.evidence_type,
                "description": ev.description,
                "date": ev.date_collected.isoformat() if ev.date_collected else None
            })
        
        return {
            "program": {
                "name": program.name,
                "description": program.description,
                "category": program.category,
                "target_population": program.target_population,
                "geographic_area": program.geographic_area,
                "goals": program.goals,
                "objectives": program.objectives,
                "status": program.status
            },
            "metrics": metrics_data,
            "evidence": evidence_data,
            "budget": {
                "total": program.total_budget,
                "spent": program.spent_budget,
                "remaining": program.total_budget - program.spent_budget,
                "utilization_rate": (program.spent_budget / program.total_budget * 100) 
                    if program.total_budget else 0
            },
            "timeline": {
                "start_date": program.start_date.isoformat() if program.start_date else None,
                "end_date": program.end_date.isoformat() if program.end_date else None
            }
        }
    
    async def _generate_section(
        self,
        section: str,
        program: Program,
        organization: Organization,
        program_data: Dict[str, Any],
        period_start: datetime,
        period_end: datetime
    ) -> str:
        """Generate a report section using AI"""
        
        # Create prompt based on section type
        prompts = {
            "executive_summary": f"""
Write a compelling executive summary for an impact report with the following information:

Program: {program.name}
Organization: {organization.name}
Period: {period_start.strftime('%B %d, %Y')} to {period_end.strftime('%B %d, %Y')}

Program Description: {program.description}

Key Metrics:
{json.dumps(program_data['metrics'], indent=2)}

Budget Utilization: {program_data['budget']['utilization_rate']:.1f}%

Write a 2-3 paragraph executive summary that highlights the program's impact, key achievements, and value delivered.
""",
            "program_overview": f"""
Write a detailed program overview with the following information:

Program: {program.name}
Category: {program.category}
Target Population: {program.target_population}
Geographic Area: {program.geographic_area}

Goals:
{json.dumps(program_data['program']['goals'], indent=2)}

Objectives:
{json.dumps(program_data['program']['objectives'], indent=2)}

Provide a comprehensive overview that explains the program's purpose, approach, and target beneficiaries.
""",
            "key_metrics": f"""
Analyze and present the following program metrics:

{json.dumps(program_data['metrics'], indent=2)}

For each metric, provide:
1. Current performance vs. target
2. Trend analysis
3. Significance of the achievement
4. Areas for improvement

Present the analysis in a clear, data-driven format.
""",
            "success_stories": f"""
Based on the following evidence and program data, create 2-3 compelling success stories:

Program: {program.name}
Evidence:
{json.dumps(program_data['evidence'][:5], indent=2)}

Each story should:
1. Feature a specific beneficiary or outcome (anonymized if needed)
2. Show the before/after transformation
3. Include specific, measurable results
4. Be emotionally engaging yet factual
""",
            "challenges": f"""
Analyze the program data and identify key challenges faced during this period:

Program: {program.name}
Metrics Achievement:
{json.dumps([m for m in program_data['metrics'] if m['achievement_rate'] < 90], indent=2)}

Budget Status: {program_data['budget']['utilization_rate']:.1f}% utilized

Discuss:
1. Main challenges encountered
2. Root causes
3. Mitigation strategies implemented
4. Lessons learned
5. Adjustments made
""",
            "financial_summary": f"""
Create a financial summary with the following data:

Total Budget: ${program_data['budget']['total']:,.2f}
Amount Spent: ${program_data['budget']['spent']:,.2f}
Remaining: ${program_data['budget']['remaining']:,.2f}
Utilization Rate: {program_data['budget']['utilization_rate']:.1f}%

Provide:
1. Budget breakdown by major categories
2. Cost per beneficiary analysis
3. Financial efficiency assessment
4. Budget forecast for next period
""",
            "next_quarter_plans": f"""
Based on the current program status and achievements, outline plans for the next quarter:

Current Status: {program.status}
Current Metrics:
{json.dumps(program_data['metrics'], indent=2)}

Include:
1. Key objectives for next quarter
2. Planned activities and initiatives
3. Target metrics and milestones
4. Resource requirements
5. Risk mitigation strategies
"""
        }
        
        prompt = prompts.get(section, f"Write a section about {section} for the impact report.")
        
        # Generate content using AI
        result = await self.ai_router.generate(
            prompt=prompt,
            system_prompt="You are an expert impact report writer for nonprofit organizations. Write clear, compelling, and data-driven content.",
            temperature=0.7,
            max_tokens=1500
        )
        
        return result["text"]
    
    async def _generate_charts(
        self,
        program_data: Dict[str, Any],
        chart_types: List[str]
    ) -> Dict[str, Any]:
        """Generate chart data for visualizations"""
        
        charts = {}
        
        if "metrics_progress" in chart_types:
            charts["metrics_progress"] = {
                "type": "bar",
                "title": "Metrics Progress vs. Target",
                "data": [
                    {
                        "metric": m["name"],
                        "current": m["current_value"],
                        "target": m["target_value"],
                        "achievement": m["achievement_rate"]
                    }
                    for m in program_data["metrics"]
                ]
            }
        
        if "budget_utilization" in chart_types:
            charts["budget_utilization"] = {
                "type": "pie",
                "title": "Budget Utilization",
                "data": [
                    {"label": "Spent", "value": program_data["budget"]["spent"]},
                    {"label": "Remaining", "value": program_data["budget"]["remaining"]}
                ]
            }
        
        if "beneficiary_demographics" in chart_types:
            # Placeholder - would need actual demographic data
            charts["beneficiary_demographics"] = {
                "type": "pie",
                "title": "Beneficiary Demographics",
                "data": [
                    {"label": "Youth (0-18)", "value": 40},
                    {"label": "Adults (19-64)", "value": 45},
                    {"label": "Seniors (65+)", "value": 15}
                ]
            }
        
        return charts
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available report templates"""
        return [
            {
                "type": key,
                "name": template["name"],
                "sections": template["sections"],
                "charts": template.get("charts", [])
            }
            for key, template in self.templates.items()
        ]