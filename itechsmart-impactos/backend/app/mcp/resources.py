"""
MCP Resource Implementations for ImpactOS
"""
from typing import Dict, Any
import json


class ImpactOSResources:
    """Resource implementations for ImpactOS"""
    
    @staticmethod
    async def get_organization_profile() -> str:
        """Get organization profile resource"""
        # TODO: Implement actual database query
        profile = {
            "name": "Sample Nonprofit Organization",
            "mission": "Empowering communities through education and innovation",
            "founded": "2015",
            "ein": "12-3456789",
            "address": "123 Main St, City, State 12345",
            "contact": {
                "email": "info@samplenonprofit.org",
                "phone": "(555) 123-4567"
            },
            "focus_areas": ["education", "youth development", "technology"],
            "annual_budget": 500000,
            "staff_count": 15,
            "volunteer_count": 50
        }
        return json.dumps(profile, indent=2)
    
    @staticmethod
    async def get_program_templates() -> str:
        """Get program templates resource"""
        templates = {
            "templates": [
                {
                    "name": "Youth Education Program",
                    "category": "education",
                    "description": "Template for youth education programs",
                    "goals": [
                        "Improve academic performance",
                        "Increase graduation rates",
                        "Develop life skills"
                    ],
                    "metrics": [
                        {"name": "Students Served", "unit": "people"},
                        {"name": "Graduation Rate", "unit": "percentage"},
                        {"name": "Program Hours", "unit": "hours"}
                    ]
                },
                {
                    "name": "Community Health Initiative",
                    "category": "health",
                    "description": "Template for community health programs",
                    "goals": [
                        "Improve community health outcomes",
                        "Increase health awareness",
                        "Provide preventive care"
                    ],
                    "metrics": [
                        {"name": "Screenings Conducted", "unit": "people"},
                        {"name": "Health Education Sessions", "unit": "sessions"},
                        {"name": "Referrals Made", "unit": "referrals"}
                    ]
                }
            ]
        }
        return json.dumps(templates, indent=2)
    
    @staticmethod
    async def get_grant_database() -> str:
        """Get grant database resource"""
        grants = {
            "total_grants": 150,
            "categories": [
                "education",
                "health",
                "environment",
                "arts",
                "community_development"
            ],
            "recent_grants": [
                {
                    "id": 1,
                    "title": "Community Development Grant 2024",
                    "funder": "ABC Foundation",
                    "amount_range": [10000, 50000],
                    "deadline": "2024-06-30",
                    "focus_areas": ["education", "youth"],
                    "eligibility": "501(c)(3) organizations"
                },
                {
                    "id": 2,
                    "title": "Education Innovation Fund",
                    "funder": "XYZ Trust",
                    "amount_range": [25000, 100000],
                    "deadline": "2024-07-15",
                    "focus_areas": ["education", "technology"],
                    "eligibility": "Educational nonprofits"
                }
            ]
        }
        return json.dumps(grants, indent=2)
    
    @staticmethod
    async def get_impact_metrics_guide() -> str:
        """Get impact metrics guide resource"""
        guide = {
            "title": "Impact Metrics Guide",
            "description": "Comprehensive guide to measuring and reporting impact",
            "sections": [
                {
                    "name": "Output Metrics",
                    "description": "Direct products or services delivered",
                    "examples": [
                        "Number of people served",
                        "Hours of service provided",
                        "Materials distributed"
                    ]
                },
                {
                    "name": "Outcome Metrics",
                    "description": "Changes in knowledge, skills, or behavior",
                    "examples": [
                        "Improvement in test scores",
                        "Increase in employment rate",
                        "Change in health indicators"
                    ]
                },
                {
                    "name": "Impact Metrics",
                    "description": "Long-term changes in conditions",
                    "examples": [
                        "Reduction in poverty rate",
                        "Improvement in community health",
                        "Increase in educational attainment"
                    ]
                }
            ],
            "best_practices": [
                "Use SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)",
                "Collect baseline data before program start",
                "Use validated measurement tools when possible",
                "Track both quantitative and qualitative data",
                "Report on both successes and challenges"
            ]
        }
        return json.dumps(guide, indent=2)
    
    @staticmethod
    async def get_partner_directory() -> str:
        """Get partner directory resource"""
        directory = {
            "total_partners": 50,
            "categories": [
                "foundations",
                "corporate_partners",
                "government_agencies",
                "academic_institutions",
                "other_nonprofits"
            ],
            "featured_partners": [
                {
                    "id": 1,
                    "name": "Tech for Good Foundation",
                    "type": "foundation",
                    "focus_areas": ["education", "technology"],
                    "resources_offered": ["funding", "technical_expertise"],
                    "contact": "partnerships@techforgood.org"
                },
                {
                    "id": 2,
                    "name": "Community Volunteers Network",
                    "type": "nonprofit",
                    "focus_areas": ["education", "youth"],
                    "resources_offered": ["volunteers", "training"],
                    "contact": "info@cvnetwork.org"
                }
            ]
        }
        return json.dumps(directory, indent=2)


def register_impactos_resources(mcp_server):
    """
    Register all ImpactOS resources with MCP server
    
    Args:
        mcp_server: MCP server instance
    """
    resources = ImpactOSResources()
    
    # Register organization profile resource
    mcp_server.register_resource(
        uri="impactos://organization/profile",
        name="Organization Profile",
        description="Current organization profile and information",
        mime_type="application/json",
        handler=resources.get_organization_profile,
        required_permissions=["view_organization"]
    )
    
    # Register program templates resource
    mcp_server.register_resource(
        uri="impactos://templates/programs",
        name="Program Templates",
        description="Pre-built templates for common program types",
        mime_type="application/json",
        handler=resources.get_program_templates,
        required_permissions=["manage_programs"]
    )
    
    # Register grant database resource
    mcp_server.register_resource(
        uri="impactos://grants/database",
        name="Grant Database",
        description="Searchable database of grant opportunities",
        mime_type="application/json",
        handler=resources.get_grant_database,
        required_permissions=["view_grant_analytics"]
    )
    
    # Register impact metrics guide resource
    mcp_server.register_resource(
        uri="impactos://guides/impact-metrics",
        name="Impact Metrics Guide",
        description="Guide to measuring and reporting impact",
        mime_type="application/json",
        handler=resources.get_impact_metrics_guide,
        required_permissions=[]  # Public resource
    )
    
    # Register partner directory resource
    mcp_server.register_resource(
        uri="impactos://partners/directory",
        name="Partner Directory",
        description="Directory of potential partners and collaborators",
        mime_type="application/json",
        handler=resources.get_partner_directory,
        required_permissions=["manage_partners"]
    )