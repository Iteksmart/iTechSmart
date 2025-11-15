"""
MCP Prompt Templates for ImpactOS
"""
from typing import Dict, Any


class ImpactOSPrompts:
    """Prompt template implementations for ImpactOS"""
    
    # Impact Report Generation Prompt
    IMPACT_REPORT_TEMPLATE = """
Generate a comprehensive impact report for the following program:

Program Name: {program_name}
Reporting Period: {period_start} to {period_end}
Organization: {organization_name}

Program Details:
{program_details}

Metrics Achieved:
{metrics_data}

Please create a detailed impact report that includes:
1. Executive Summary (2-3 paragraphs)
2. Program Overview
3. Key Achievements and Metrics
4. Success Stories and Testimonials
5. Challenges Faced and Lessons Learned
6. Financial Summary
7. Future Plans and Sustainability

Use a professional, compelling tone that demonstrates the program's value and impact.
"""

    # Grant Proposal Generation Prompt
    GRANT_PROPOSAL_TEMPLATE = """
Create a grant proposal for the following opportunity:

Grant Title: {grant_title}
Funder: {funder_name}
Requested Amount: ${requested_amount}
Organization: {organization_name}

Organization Background:
{organization_background}

Program Description:
{program_description}

Please create a compelling grant proposal that includes:
1. Executive Summary
2. Statement of Need/Problem Statement
3. Goals and Objectives
4. Methodology and Implementation Plan
5. Timeline
6. Budget and Budget Narrative
7. Evaluation Plan
8. Organizational Capacity
9. Sustainability Plan

Ensure the proposal aligns with the funder's priorities and demonstrates clear impact.
"""

    # Data Analysis Prompt
    DATA_ANALYSIS_TEMPLATE = """
Analyze the following program data and provide insights:

Program: {program_name}
Data Type: {data_type}
Time Period: {time_period}

Data:
{data}

Please provide:
1. Key Trends and Patterns
2. Performance Analysis (vs. targets and benchmarks)
3. Areas of Success
4. Areas for Improvement
5. Actionable Recommendations
6. Predictions for Next Period

Use data-driven insights and provide specific, actionable recommendations.
"""

    # Partner Matching Prompt
    PARTNER_MATCHING_TEMPLATE = """
Find potential partners for the following organization:

Organization: {organization_name}
Focus Areas: {focus_areas}
Partnership Goals: {partnership_goals}
Resources Needed: {resources_needed}

Organization Profile:
{organization_profile}

Please identify and recommend potential partners that:
1. Align with the organization's mission and focus areas
2. Can provide the needed resources or expertise
3. Have a track record of successful partnerships
4. Are geographically accessible or have remote collaboration capabilities

For each recommended partner, provide:
- Name and type
- Alignment score (0-100)
- Specific reasons for the match
- Potential collaboration opportunities
- Suggested next steps
"""

    # Impact Score Analysis Prompt
    IMPACT_SCORE_TEMPLATE = """
Calculate and analyze the impact score for the following program:

Program: {program_name}
Organization: {organization_name}

Program Data:
- Beneficiaries Served: {beneficiaries_served}
- Budget: ${budget}
- Duration: {duration}
- Outcomes Achieved: {outcomes_achieved}

Additional Context:
{additional_context}

Please calculate an impact score (0-100) based on:
1. Reach (number of beneficiaries)
2. Depth (intensity of impact per beneficiary)
3. Efficiency (cost per beneficiary and outcome)
4. Sustainability (long-term viability)
5. Innovation (novel approaches)

Provide:
- Overall impact score
- Component scores for each dimension
- Comparison to sector benchmarks
- Specific recommendations for improvement
- Predicted impact trajectory
"""

    # Strategic Planning Prompt
    STRATEGIC_PLANNING_TEMPLATE = """
Develop a strategic plan for the following organization:

Organization: {organization_name}
Current State: {current_state}
Vision: {vision}
Time Horizon: {time_horizon}

Organizational Context:
{organizational_context}

Please create a strategic plan that includes:
1. Mission and Vision Refinement
2. SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)
3. Strategic Goals (3-5 major goals)
4. Key Objectives for each goal
5. Action Plans with timelines
6. Resource Requirements
7. Success Metrics and KPIs
8. Risk Assessment and Mitigation Strategies

Ensure the plan is realistic, measurable, and aligned with the organization's capacity.
"""


def register_impactos_prompts(mcp_server):
    """
    Register all ImpactOS prompts with MCP server
    
    Args:
        mcp_server: MCP server instance
    """
    prompts = ImpactOSPrompts()
    
    # Register impact report generation prompt
    mcp_server.register_prompt(
        name="generate_impact_report",
        description="Generate a comprehensive impact report for a program",
        arguments=[
            {"name": "program_name", "description": "Name of the program", "required": True},
            {"name": "period_start", "description": "Start date of reporting period", "required": True},
            {"name": "period_end", "description": "End date of reporting period", "required": True},
            {"name": "organization_name", "description": "Name of the organization", "required": True},
            {"name": "program_details", "description": "Detailed program information", "required": True},
            {"name": "metrics_data", "description": "Metrics and achievements data", "required": True}
        ],
        template=prompts.IMPACT_REPORT_TEMPLATE,
        required_permissions=["create_impact_reports"]
    )
    
    # Register grant proposal generation prompt
    mcp_server.register_prompt(
        name="create_grant_proposal",
        description="Create a compelling grant proposal",
        arguments=[
            {"name": "grant_title", "description": "Title of the grant opportunity", "required": True},
            {"name": "funder_name", "description": "Name of the funder", "required": True},
            {"name": "requested_amount", "description": "Amount requested", "required": True},
            {"name": "organization_name", "description": "Name of the organization", "required": True},
            {"name": "organization_background", "description": "Organization background", "required": True},
            {"name": "program_description", "description": "Program description", "required": True}
        ],
        template=prompts.GRANT_PROPOSAL_TEMPLATE,
        required_permissions=["create_grant_proposals"]
    )
    
    # Register data analysis prompt
    mcp_server.register_prompt(
        name="analyze_program_data",
        description="Analyze program data and provide insights",
        arguments=[
            {"name": "program_name", "description": "Name of the program", "required": True},
            {"name": "data_type", "description": "Type of data being analyzed", "required": True},
            {"name": "time_period", "description": "Time period for analysis", "required": True},
            {"name": "data", "description": "The data to analyze", "required": True}
        ],
        template=prompts.DATA_ANALYSIS_TEMPLATE,
        required_permissions=["view_all_analytics"]
    )
    
    # Register partner matching prompt
    mcp_server.register_prompt(
        name="find_partners",
        description="Find and recommend potential partners",
        arguments=[
            {"name": "organization_name", "description": "Name of the organization", "required": True},
            {"name": "focus_areas", "description": "Focus areas for partnership", "required": True},
            {"name": "partnership_goals", "description": "Goals for partnership", "required": True},
            {"name": "resources_needed", "description": "Resources needed from partners", "required": True},
            {"name": "organization_profile", "description": "Organization profile", "required": True}
        ],
        template=prompts.PARTNER_MATCHING_TEMPLATE,
        required_permissions=["manage_partners"]
    )
    
    # Register impact score analysis prompt
    mcp_server.register_prompt(
        name="calculate_impact_score",
        description="Calculate and analyze program impact score",
        arguments=[
            {"name": "program_name", "description": "Name of the program", "required": True},
            {"name": "organization_name", "description": "Name of the organization", "required": True},
            {"name": "beneficiaries_served", "description": "Number of beneficiaries", "required": True},
            {"name": "budget", "description": "Program budget", "required": True},
            {"name": "duration", "description": "Program duration", "required": True},
            {"name": "outcomes_achieved", "description": "Outcomes achieved", "required": True},
            {"name": "additional_context", "description": "Additional context", "required": False}
        ],
        template=prompts.IMPACT_SCORE_TEMPLATE,
        required_permissions=["view_program_analytics"]
    )
    
    # Register strategic planning prompt
    mcp_server.register_prompt(
        name="develop_strategic_plan",
        description="Develop a comprehensive strategic plan",
        arguments=[
            {"name": "organization_name", "description": "Name of the organization", "required": True},
            {"name": "current_state", "description": "Current organizational state", "required": True},
            {"name": "vision", "description": "Vision for the future", "required": True},
            {"name": "time_horizon", "description": "Planning time horizon", "required": True},
            {"name": "organizational_context", "description": "Organizational context", "required": True}
        ],
        template=prompts.STRATEGIC_PLANNING_TEMPLATE,
        required_permissions=["manage_organization"]
    )