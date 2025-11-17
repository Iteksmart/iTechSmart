"""
Agents API Routes
Provides information about available agents and their capabilities
"""

from fastapi import APIRouter, Depends
from typing import List, Dict
import logging

from app.api.auth import get_current_user
from app.models.database import User
from app.agents.researcher_agent import ResearcherAgent
from app.agents.coder_agent import CoderAgent
from app.agents.writer_agent import WriterAgent
from app.agents.analyst_agent import AnalystAgent
from app.agents.debugger_agent import DebuggerAgent
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentInfo(BaseModel):
    name: str
    type: str
    description: str
    capabilities: List[str]
    supported_languages: List[str] = []
    example_tasks: List[str]


class AgentCapability(BaseModel):
    capability: str
    description: str
    parameters: Dict[str, str]


@router.get("/", response_model=List[AgentInfo])
async def list_agents(current_user: User = Depends(get_current_user)):
    """
    List all available agents and their capabilities
    """
    agents = [
        AgentInfo(
            name="Researcher",
            type="researcher",
            description="Searches the web, gathers information, and performs fact-checking",
            capabilities=[
                "web_search",
                "deep_research",
                "fact_checking",
                "citation_generation",
                "source_ranking",
            ],
            example_tasks=[
                "Research the latest AI trends in 2024",
                "Find information about quantum computing",
                "Fact-check a claim about climate change",
                "Gather data on market trends",
            ],
        ),
        AgentInfo(
            name="Coder",
            type="coder",
            description="Generates, executes, debugs, and reviews code in multiple languages",
            capabilities=[
                "code_generation",
                "code_execution",
                "debugging",
                "code_review",
                "test_generation",
                "refactoring",
                "security_scanning",
            ],
            supported_languages=[
                "Python",
                "JavaScript",
                "TypeScript",
                "Java",
                "Go",
                "Rust",
                "C",
                "C++",
                "Ruby",
                "PHP",
                "Swift",
                "Kotlin",
            ],
            example_tasks=[
                "Create a REST API in Python",
                "Generate unit tests for a function",
                "Debug a JavaScript error",
                "Review code for security issues",
                "Refactor legacy code",
            ],
        ),
        AgentInfo(
            name="Writer",
            type="writer",
            description="Creates documentation, articles, and technical content",
            capabilities=[
                "readme_generation",
                "api_documentation",
                "user_guides",
                "technical_guides",
                "reports",
                "tutorials",
            ],
            example_tasks=[
                "Write a README for a project",
                "Create API documentation",
                "Generate a user guide",
                "Write a technical tutorial",
                "Create a project report",
            ],
        ),
        AgentInfo(
            name="Analyst",
            type="analyst",
            description="Analyzes data, generates insights, and creates visualizations",
            capabilities=[
                "descriptive_statistics",
                "diagnostic_analysis",
                "predictive_analysis",
                "trend_analysis",
                "comparative_analysis",
                "data_visualization",
                "data_cleaning",
            ],
            example_tasks=[
                "Analyze sales data trends",
                "Generate statistical summary",
                "Create data visualizations",
                "Perform comparative analysis",
                "Clean and prepare dataset",
            ],
        ),
        AgentInfo(
            name="Debugger",
            type="debugger",
            description="Analyzes errors, identifies root causes, and suggests fixes",
            capabilities=[
                "error_classification",
                "stack_trace_analysis",
                "root_cause_analysis",
                "fix_generation",
                "performance_profiling",
                "memory_leak_detection",
            ],
            example_tasks=[
                "Debug a Python exception",
                "Analyze performance issues",
                "Find memory leaks",
                "Identify root cause of error",
                "Generate fix for bug",
            ],
        ),
    ]

    return agents


@router.get("/{agent_type}", response_model=AgentInfo)
async def get_agent_info(
    agent_type: str, current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific agent"""
    agents_map = {
        "researcher": AgentInfo(
            name="Researcher",
            type="researcher",
            description="Searches the web, gathers information, and performs fact-checking",
            capabilities=[
                "web_search",
                "deep_research",
                "fact_checking",
                "citation_generation",
                "source_ranking",
            ],
            example_tasks=[
                "Research the latest AI trends in 2024",
                "Find information about quantum computing",
                "Fact-check a claim about climate change",
            ],
        ),
        "coder": AgentInfo(
            name="Coder",
            type="coder",
            description="Generates, executes, debugs, and reviews code",
            capabilities=[
                "code_generation",
                "code_execution",
                "debugging",
                "code_review",
                "test_generation",
            ],
            supported_languages=[
                "Python",
                "JavaScript",
                "TypeScript",
                "Java",
                "Go",
                "Rust",
            ],
            example_tasks=[
                "Create a REST API in Python",
                "Generate unit tests",
                "Debug JavaScript error",
            ],
        ),
        "writer": AgentInfo(
            name="Writer",
            type="writer",
            description="Creates documentation and technical content",
            capabilities=[
                "readme_generation",
                "api_documentation",
                "user_guides",
                "tutorials",
            ],
            example_tasks=["Write a README", "Create API docs", "Generate tutorial"],
        ),
        "analyst": AgentInfo(
            name="Analyst",
            type="analyst",
            description="Analyzes data and generates insights",
            capabilities=[
                "descriptive_statistics",
                "trend_analysis",
                "data_visualization",
                "predictive_analysis",
            ],
            example_tasks=[
                "Analyze sales trends",
                "Generate statistics",
                "Create visualizations",
            ],
        ),
        "debugger": AgentInfo(
            name="Debugger",
            type="debugger",
            description="Analyzes errors and suggests fixes",
            capabilities=[
                "error_classification",
                "root_cause_analysis",
                "fix_generation",
                "performance_profiling",
            ],
            example_tasks=[
                "Debug exception",
                "Analyze performance",
                "Find memory leaks",
            ],
        ),
    }

    if agent_type not in agents_map:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent type '{agent_type}' not found",
        )

    return agents_map[agent_type]


@router.get("/{agent_type}/capabilities", response_model=List[AgentCapability])
async def get_agent_capabilities(
    agent_type: str, current_user: User = Depends(get_current_user)
):
    """Get detailed capabilities for a specific agent"""
    capabilities_map = {
        "researcher": [
            AgentCapability(
                capability="web_search",
                description="Search the web for information",
                parameters={"query": "Search query string"},
            ),
            AgentCapability(
                capability="deep_research",
                description="Perform in-depth research with multiple sources",
                parameters={
                    "topic": "Research topic",
                    "num_sources": "Number of sources (default: 5)",
                },
            ),
            AgentCapability(
                capability="fact_checking",
                description="Verify claims and check facts",
                parameters={"claim": "Claim to verify"},
            ),
        ],
        "coder": [
            AgentCapability(
                capability="code_generation",
                description="Generate code from description",
                parameters={
                    "description": "What to build",
                    "language": "Programming language",
                },
            ),
            AgentCapability(
                capability="code_execution",
                description="Execute code in sandbox",
                parameters={
                    "code": "Code to execute",
                    "language": "Programming language",
                },
            ),
            AgentCapability(
                capability="debugging",
                description="Debug and fix code errors",
                parameters={"code": "Code with error", "error": "Error message"},
            ),
        ],
        "writer": [
            AgentCapability(
                capability="readme_generation",
                description="Generate README documentation",
                parameters={"project_info": "Project information"},
            ),
            AgentCapability(
                capability="api_documentation",
                description="Create API documentation",
                parameters={"api_spec": "API specification"},
            ),
        ],
        "analyst": [
            AgentCapability(
                capability="descriptive_statistics",
                description="Calculate descriptive statistics",
                parameters={"data": "Dataset to analyze"},
            ),
            AgentCapability(
                capability="trend_analysis",
                description="Analyze trends in data",
                parameters={"data": "Time series data"},
            ),
        ],
        "debugger": [
            AgentCapability(
                capability="error_classification",
                description="Classify error types",
                parameters={"error": "Error message"},
            ),
            AgentCapability(
                capability="root_cause_analysis",
                description="Identify root cause of errors",
                parameters={"error": "Error message", "context": "Error context"},
            ),
        ],
    }

    if agent_type not in capabilities_map:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent type '{agent_type}' not found",
        )

    return capabilities_map[agent_type]
