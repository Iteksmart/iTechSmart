"""
Research API - Deep Research with Citations
Provides endpoints for enhanced research capabilities
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.agents.enhanced_researcher_agent import (
    enhanced_researcher,
    CitationStyle,
    Source,
    SourceType,
    CredibilityLevel,
)
from app.core.security import get_current_user
from app.models.database import User

router = APIRouter(prefix="/api/research", tags=["research"])


# ==================== REQUEST/RESPONSE MODELS ====================


class DeepResearchRequest(BaseModel):
    """Request for deep research"""

    query: str
    num_sources: int = 10
    citation_style: CitationStyle = CitationStyle.APA
    verify_facts: bool = True
    min_credibility: float = 50.0


class CitationRequest(BaseModel):
    """Request for citation formatting"""

    url: str
    title: str
    author: Optional[str] = None
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    citation_style: CitationStyle = CitationStyle.APA


class CredibilityCheckRequest(BaseModel):
    """Request for credibility check"""

    url: str
    content: str
    title: str
    author: Optional[str] = None
    publication_date: Optional[str] = None
    publisher: Optional[str] = None


class FactVerificationRequest(BaseModel):
    """Request for fact verification"""

    claim: str
    sources: List[Dict[str, Any]]


class ResearchReportRequest(BaseModel):
    """Request for research report generation"""

    query: str
    content: str
    sources: List[Dict[str, Any]]
    citation_style: CitationStyle = CitationStyle.APA


# ==================== ENDPOINTS ====================


@router.post("/deep-research")
async def perform_deep_research(
    request: DeepResearchRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Perform deep research with multi-source verification

    Args:
        request: Research request with query and parameters

    Returns:
        Complete research results with sources, citations, and report
    """
    try:
        results = await enhanced_researcher.deep_research(
            query=request.query,
            num_sources=request.num_sources,
            citation_style=request.citation_style,
            verify_facts=request.verify_facts,
        )

        # Filter sources by minimum credibility
        if request.min_credibility > 0:
            results["sources"] = [
                s
                for s in results["sources"]
                if s["credibility_score"] >= request.min_credibility
            ]

        return {"success": True, "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@router.post("/format-citation")
async def format_citation(
    request: CitationRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Format a citation in specified style

    Args:
        request: Citation request with source details

    Returns:
        Formatted citation string
    """
    try:
        # Create Source object
        from datetime import datetime

        publication_date = None
        if request.publication_date:
            try:
                publication_date = datetime.fromisoformat(request.publication_date)
            except:
                pass

        source = Source(
            url=request.url,
            title=request.title,
            content="",  # Not needed for citation
            author=request.author,
            publication_date=publication_date,
            publisher=request.publisher,
        )

        citation = enhanced_researcher.format_citation(source, request.citation_style)

        return {
            "success": True,
            "citation": citation,
            "style": request.citation_style.value,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Citation formatting failed: {str(e)}"
        )


@router.post("/check-credibility")
async def check_source_credibility(
    request: CredibilityCheckRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check source credibility

    Args:
        request: Credibility check request with source details

    Returns:
        Credibility score and analysis
    """
    try:
        from datetime import datetime

        publication_date = None
        if request.publication_date:
            try:
                publication_date = datetime.fromisoformat(request.publication_date)
            except:
                pass

        source = Source(
            url=request.url,
            title=request.title,
            content=request.content,
            author=request.author,
            publication_date=publication_date,
            publisher=request.publisher,
        )

        # Classify source type
        source.source_type = (
            enhanced_researcher.credibility_scorer.classify_source_type(
                source.url, source.content
            )
        )

        # Score credibility
        source.credibility_score = enhanced_researcher.score_credibility(source)

        return {
            "success": True,
            "credibility_score": source.credibility_score,
            "credibility_level": source.get_credibility_level().value,
            "source_type": source.source_type.value,
            "domain": source.domain,
            "analysis": {
                "has_author": bool(source.author),
                "has_publication_date": bool(source.publication_date),
                "has_publisher": bool(source.publisher),
                "content_length": len(source.content),
                "domain_reputation": (
                    "high"
                    if source.credibility_score >= 75
                    else "medium" if source.credibility_score >= 50 else "low"
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Credibility check failed: {str(e)}"
        )


@router.post("/verify-fact")
async def verify_fact(
    request: FactVerificationRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify a fact across multiple sources

    Args:
        request: Fact verification request with claim and sources

    Returns:
        Verification results with confidence score
    """
    try:
        # Convert source dicts to Source objects
        sources = []
        for source_dict in request.sources:
            from datetime import datetime

            publication_date = None
            if source_dict.get("publication_date"):
                try:
                    publication_date = datetime.fromisoformat(
                        source_dict["publication_date"]
                    )
                except:
                    pass

            source = Source(
                url=source_dict["url"],
                title=source_dict["title"],
                content=source_dict.get("content", ""),
                author=source_dict.get("author"),
                publication_date=publication_date,
                publisher=source_dict.get("publisher"),
            )
            sources.append(source)

        verification = enhanced_researcher.fact_verifier.verify_claim(
            request.claim, sources
        )

        return {"success": True, "verification": verification}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Fact verification failed: {str(e)}"
        )


@router.post("/generate-report")
async def generate_research_report(
    request: ResearchReportRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate formatted research report

    Args:
        request: Report generation request with content and sources

    Returns:
        Formatted research report in Markdown
    """
    try:
        from app.agents.enhanced_researcher_agent import ResearchReport
        from datetime import datetime

        # Convert source dicts to Source objects
        sources = []
        for source_dict in request.sources:
            publication_date = None
            if source_dict.get("publication_date"):
                try:
                    publication_date = datetime.fromisoformat(
                        source_dict["publication_date"]
                    )
                except:
                    pass

            source = Source(
                url=source_dict["url"],
                title=source_dict["title"],
                content=source_dict.get("content", ""),
                author=source_dict.get("author"),
                publication_date=publication_date,
                publisher=source_dict.get("publisher"),
                source_type=SourceType(source_dict.get("source_type", "unknown")),
                credibility_score=source_dict.get("credibility_score", 0.0),
            )
            sources.append(source)

        report = ResearchReport(request.query, sources, request.citation_style)
        markdown_report = report.generate_markdown_report(request.content)

        return {
            "success": True,
            "report": markdown_report,
            "citation_style": request.citation_style.value,
            "total_sources": len(sources),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Report generation failed: {str(e)}"
        )


@router.get("/citation-styles")
async def get_citation_styles(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get available citation styles

    Returns:
        List of supported citation styles
    """
    styles = [
        {
            "id": CitationStyle.APA.value,
            "name": "APA (7th Edition)",
            "description": "American Psychological Association style",
        },
        {
            "id": CitationStyle.MLA.value,
            "name": "MLA (9th Edition)",
            "description": "Modern Language Association style",
        },
        {
            "id": CitationStyle.CHICAGO.value,
            "name": "Chicago (17th Edition)",
            "description": "Chicago Manual of Style",
        },
        {
            "id": CitationStyle.HARVARD.value,
            "name": "Harvard",
            "description": "Harvard referencing style",
        },
        {
            "id": CitationStyle.IEEE.value,
            "name": "IEEE",
            "description": "Institute of Electrical and Electronics Engineers style",
        },
    ]

    return {"success": True, "styles": styles}


@router.get("/source-types")
async def get_source_types(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get available source types

    Returns:
        List of source types with descriptions
    """
    types = [
        {
            "id": SourceType.ACADEMIC.value,
            "name": "Academic",
            "description": "Peer-reviewed journals, research papers",
            "credibility": "Very High",
        },
        {
            "id": SourceType.GOVERNMENT.value,
            "name": "Government",
            "description": "Official government sources",
            "credibility": "Very High",
        },
        {
            "id": SourceType.ORGANIZATION.value,
            "name": "Organization",
            "description": "Non-profit and professional organizations",
            "credibility": "High",
        },
        {
            "id": SourceType.NEWS.value,
            "name": "News",
            "description": "News outlets and journalism",
            "credibility": "Medium to High",
        },
        {
            "id": SourceType.BLOG.value,
            "name": "Blog",
            "description": "Personal or corporate blogs",
            "credibility": "Low to Medium",
        },
        {
            "id": SourceType.SOCIAL_MEDIA.value,
            "name": "Social Media",
            "description": "Social media posts and content",
            "credibility": "Low",
        },
    ]

    return {"success": True, "types": types}


@router.get("/credibility-levels")
async def get_credibility_levels(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get credibility level definitions

    Returns:
        List of credibility levels with score ranges
    """
    levels = [
        {
            "id": CredibilityLevel.VERY_HIGH.value,
            "name": "Very High",
            "score_range": "90-100",
            "description": "Highly trustworthy sources (academic, government)",
        },
        {
            "id": CredibilityLevel.HIGH.value,
            "name": "High",
            "score_range": "75-89",
            "description": "Trustworthy sources (reputable news, organizations)",
        },
        {
            "id": CredibilityLevel.MEDIUM.value,
            "name": "Medium",
            "score_range": "50-74",
            "description": "Moderately trustworthy sources",
        },
        {
            "id": CredibilityLevel.LOW.value,
            "name": "Low",
            "score_range": "25-49",
            "description": "Less trustworthy sources (blogs, opinion pieces)",
        },
        {
            "id": CredibilityLevel.VERY_LOW.value,
            "name": "Very Low",
            "score_range": "0-24",
            "description": "Questionable sources (social media, unverified)",
        },
    ]

    return {"success": True, "levels": levels}
