"""
Enhanced Researcher Agent - Deep Research with Citations
Implements SuperNinja-equivalent research capabilities with multi-source verification
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import re
import hashlib
from urllib.parse import urlparse
import asyncio
import httpx
from bs4 import BeautifulSoup


class CitationStyle(str, Enum):
    """Citation formatting styles"""

    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    HARVARD = "harvard"
    IEEE = "ieee"


class SourceType(str, Enum):
    """Types of sources"""

    ACADEMIC = "academic"
    NEWS = "news"
    BLOG = "blog"
    GOVERNMENT = "government"
    ORGANIZATION = "organization"
    SOCIAL_MEDIA = "social_media"
    UNKNOWN = "unknown"


class CredibilityLevel(str, Enum):
    """Source credibility levels"""

    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"  # 75-89%
    MEDIUM = "medium"  # 50-74%
    LOW = "low"  # 25-49%
    VERY_LOW = "very_low"  # 0-24%


class Source:
    """Represents a research source with metadata"""

    def __init__(
        self,
        url: str,
        title: str,
        content: str,
        author: Optional[str] = None,
        publication_date: Optional[datetime] = None,
        publisher: Optional[str] = None,
        source_type: SourceType = SourceType.UNKNOWN,
        credibility_score: float = 0.0,
    ):
        self.url = url
        self.title = title
        self.content = content
        self.author = author
        self.publication_date = publication_date
        self.publisher = publisher
        self.source_type = source_type
        self.credibility_score = credibility_score
        self.access_date = datetime.now()
        self.domain = urlparse(url).netloc
        self.id = hashlib.md5(url.encode()).hexdigest()[:8]

    def get_credibility_level(self) -> CredibilityLevel:
        """Get credibility level based on score"""
        if self.credibility_score >= 90:
            return CredibilityLevel.VERY_HIGH
        elif self.credibility_score >= 75:
            return CredibilityLevel.HIGH
        elif self.credibility_score >= 50:
            return CredibilityLevel.MEDIUM
        elif self.credibility_score >= 25:
            return CredibilityLevel.LOW
        else:
            return CredibilityLevel.VERY_LOW

    def to_dict(self) -> Dict[str, Any]:
        """Convert source to dictionary"""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "author": self.author,
            "publication_date": (
                self.publication_date.isoformat() if self.publication_date else None
            ),
            "publisher": self.publisher,
            "domain": self.domain,
            "source_type": self.source_type.value,
            "credibility_score": self.credibility_score,
            "credibility_level": self.get_credibility_level().value,
            "access_date": self.access_date.isoformat(),
        }


class CitationFormatter:
    """Formats citations in various academic styles"""

    @staticmethod
    def format_apa(source: Source) -> str:
        """Format citation in APA style (7th edition)"""
        parts = []

        # Author
        if source.author:
            parts.append(f"{source.author}.")

        # Publication date
        if source.publication_date:
            year = source.publication_date.year
            parts.append(f"({year}).")
        else:
            parts.append("(n.d.).")

        # Title
        parts.append(f"{source.title}.")

        # Publisher
        if source.publisher:
            parts.append(f"{source.publisher}.")

        # URL and access date
        parts.append(
            f"Retrieved {source.access_date.strftime('%B %d, %Y')}, from {source.url}"
        )

        return " ".join(parts)

    @staticmethod
    def format_mla(source: Source) -> str:
        """Format citation in MLA style (9th edition)"""
        parts = []

        # Author
        if source.author:
            parts.append(f"{source.author}.")

        # Title
        parts.append(f'"{source.title}."')

        # Publisher
        if source.publisher:
            parts.append(f"{source.publisher},")

        # Publication date
        if source.publication_date:
            parts.append(f"{source.publication_date.strftime('%d %b. %Y')},")
        else:
            parts.append("n.d.,")

        # URL and access date
        parts.append(
            f"{source.url}. Accessed {source.access_date.strftime('%d %b. %Y')}."
        )

        return " ".join(parts)

    @staticmethod
    def format_chicago(source: Source) -> str:
        """Format citation in Chicago style (17th edition)"""
        parts = []

        # Author
        if source.author:
            parts.append(f"{source.author}.")

        # Title
        parts.append(f'"{source.title}."')

        # Publisher
        if source.publisher:
            parts.append(f"{source.publisher}.")

        # Publication date
        if source.publication_date:
            parts.append(f"{source.publication_date.strftime('%B %d, %Y')}.")

        # URL and access date
        parts.append(
            f"{source.url} (accessed {source.access_date.strftime('%B %d, %Y')})."
        )

        return " ".join(parts)

    @staticmethod
    def format_harvard(source: Source) -> str:
        """Format citation in Harvard style"""
        parts = []

        # Author and year
        if source.author and source.publication_date:
            parts.append(f"{source.author} ({source.publication_date.year})")
        elif source.author:
            parts.append(f"{source.author} (n.d.)")

        # Title
        parts.append(f"{source.title}.")

        # Available at
        parts.append(f"Available at: {source.url}")

        # Access date
        parts.append(f"(Accessed: {source.access_date.strftime('%d %B %Y')}).")

        return " ".join(parts)

    @staticmethod
    def format_ieee(source: Source) -> str:
        """Format citation in IEEE style"""
        parts = []

        # Author
        if source.author:
            parts.append(f"{source.author},")

        # Title
        parts.append(f'"{source.title},"')

        # Publisher
        if source.publisher:
            parts.append(f"{source.publisher},")

        # Date
        if source.publication_date:
            parts.append(f"{source.publication_date.strftime('%b. %Y')}.")

        # URL and access date
        parts.append(
            f"[Online]. Available: {source.url}. [Accessed: {source.access_date.strftime('%b. %d, %Y')}]."
        )

        return " ".join(parts)

    @classmethod
    def format(cls, source: Source, style: CitationStyle) -> str:
        """Format citation in specified style"""
        formatters = {
            CitationStyle.APA: cls.format_apa,
            CitationStyle.MLA: cls.format_mla,
            CitationStyle.CHICAGO: cls.format_chicago,
            CitationStyle.HARVARD: cls.format_harvard,
            CitationStyle.IEEE: cls.format_ieee,
        }

        formatter = formatters.get(style)
        if not formatter:
            raise ValueError(f"Unsupported citation style: {style}")

        return formatter(source)


class SourceCredibilityScorer:
    """Scores source credibility based on multiple factors"""

    # Trusted domains with high credibility
    TRUSTED_DOMAINS = {
        # Academic
        "edu": 20,
        "ac.uk": 20,
        "scholar.google.com": 20,
        "arxiv.org": 18,
        "researchgate.net": 15,
        # Government
        "gov": 20,
        "gov.uk": 20,
        "europa.eu": 18,
        # News (reputable)
        "reuters.com": 18,
        "apnews.com": 18,
        "bbc.com": 17,
        "nytimes.com": 16,
        "wsj.com": 16,
        "theguardian.com": 16,
        "washingtonpost.com": 16,
        # Organizations
        "who.int": 20,
        "un.org": 20,
        "worldbank.org": 18,
        "oecd.org": 18,
        # Tech/Science
        "nature.com": 19,
        "science.org": 19,
        "ieee.org": 18,
        "acm.org": 18,
        "scientificamerican.com": 17,
    }

    @classmethod
    def score_source(cls, source: Source) -> float:
        """
        Calculate credibility score (0-100)

        Factors:
        - Domain reputation (0-20 points)
        - Source type (0-20 points)
        - Has author (0-15 points)
        - Has publication date (0-10 points)
        - Has publisher (0-10 points)
        - Content quality (0-15 points)
        - URL structure (0-10 points)
        """
        score = 0.0

        # 1. Domain reputation (0-20 points)
        domain = source.domain.lower()
        for trusted_domain, points in cls.TRUSTED_DOMAINS.items():
            if trusted_domain in domain:
                score += points
                break
        else:
            # Check TLD
            if domain.endswith(".edu") or domain.endswith(".gov"):
                score += 15
            elif domain.endswith(".org"):
                score += 10
            elif domain.endswith(".com"):
                score += 5

        # 2. Source type (0-20 points)
        source_type_scores = {
            SourceType.ACADEMIC: 20,
            SourceType.GOVERNMENT: 18,
            SourceType.ORGANIZATION: 15,
            SourceType.NEWS: 12,
            SourceType.BLOG: 5,
            SourceType.SOCIAL_MEDIA: 2,
            SourceType.UNKNOWN: 0,
        }
        score += source_type_scores.get(source.source_type, 0)

        # 3. Has author (0-15 points)
        if source.author:
            score += 15

        # 4. Has publication date (0-10 points)
        if source.publication_date:
            score += 10

            # Bonus for recent content (within 2 years)
            age_years = (datetime.now() - source.publication_date).days / 365
            if age_years <= 2:
                score += 5

        # 5. Has publisher (0-10 points)
        if source.publisher:
            score += 10

        # 6. Content quality (0-15 points)
        content_length = len(source.content)
        if content_length > 2000:
            score += 15
        elif content_length > 1000:
            score += 10
        elif content_length > 500:
            score += 5

        # Check for citations/references in content
        if re.search(r"\[\d+\]|\(\d{4}\)|et al\.", source.content):
            score += 5

        # 7. URL structure (0-10 points)
        url_lower = source.url.lower()

        # Positive indicators
        if (
            "/research/" in url_lower
            or "/paper/" in url_lower
            or "/article/" in url_lower
        ):
            score += 5
        if "/doi/" in url_lower or "doi.org" in url_lower:
            score += 5

        # Negative indicators
        if "/blog/" in url_lower or "/opinion/" in url_lower:
            score -= 5
        if (
            "?" in source.url and len(source.url.split("?")[1]) > 50
        ):  # Long query strings
            score -= 3

        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, score))

    @classmethod
    def classify_source_type(cls, url: str, content: str) -> SourceType:
        """Classify source type based on URL and content"""
        url_lower = url.lower()
        domain = urlparse(url).netloc.lower()

        # Academic
        if any(
            x in domain
            for x in [".edu", "scholar.", "arxiv.", "researchgate.", "academia."]
        ):
            return SourceType.ACADEMIC
        if any(x in url_lower for x in ["/paper/", "/research/", "/doi/", "/journal/"]):
            return SourceType.ACADEMIC

        # Government
        if ".gov" in domain or any(x in domain for x in ["europa.eu", "un.org"]):
            return SourceType.GOVERNMENT

        # News
        if any(
            x in domain
            for x in ["news", "times", "post", "guardian", "reuters", "bbc", "cnn"]
        ):
            return SourceType.NEWS

        # Organization
        if ".org" in domain and not any(x in domain for x in ["blog", "wiki"]):
            return SourceType.ORGANIZATION

        # Blog
        if any(
            x in url_lower for x in ["/blog/", "medium.com", "wordpress.", "blogger."]
        ):
            return SourceType.BLOG

        # Social Media
        if any(
            x in domain
            for x in ["twitter.", "facebook.", "linkedin.", "reddit.", "instagram."]
        ):
            return SourceType.SOCIAL_MEDIA

        return SourceType.UNKNOWN


class FactVerifier:
    """Verifies facts across multiple sources"""

    @staticmethod
    def extract_claims(text: str) -> List[str]:
        """Extract factual claims from text"""
        # Split into sentences
        sentences = re.split(r"[.!?]+", text)

        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Look for factual statements (contains numbers, dates, names, etc.)
            if any(
                [
                    re.search(r"\d+", sentence),  # Contains numbers
                    re.search(
                        r"\b(is|are|was|were|has|have|had)\b", sentence
                    ),  # Contains factual verbs
                    re.search(
                        r"\b(according to|research shows|study found)\b", sentence, re.I
                    ),  # Citations
                ]
            ):
                claims.append(sentence)

        return claims

    @staticmethod
    def verify_claim(claim: str, sources: List[Source]) -> Dict[str, Any]:
        """
        Verify a claim against multiple sources

        Returns:
            - verified: bool
            - confidence: float (0-100)
            - supporting_sources: List[str]
            - contradicting_sources: List[str]
        """
        supporting = []
        contradicting = []

        # Extract key terms from claim
        claim_lower = claim.lower()
        key_terms = set(re.findall(r"\b\w{4,}\b", claim_lower))

        for source in sources:
            content_lower = source.content.lower()

            # Check if source mentions the claim
            matching_terms = sum(1 for term in key_terms if term in content_lower)
            relevance = matching_terms / len(key_terms) if key_terms else 0

            if relevance > 0.3:  # Source is relevant
                # Simple heuristic: if claim appears in source, it's supporting
                if claim_lower in content_lower:
                    supporting.append(source.id)
                # Check for contradictory language
                elif any(
                    word in content_lower
                    for word in ["not", "false", "incorrect", "wrong"]
                ):
                    # More sophisticated check needed here
                    pass

        # Calculate confidence
        total_sources = len(supporting) + len(contradicting)
        if total_sources == 0:
            confidence = 0.0
            verified = False
        else:
            confidence = (len(supporting) / total_sources) * 100
            verified = confidence >= 50

        return {
            "claim": claim,
            "verified": verified,
            "confidence": confidence,
            "supporting_sources": supporting,
            "contradicting_sources": contradicting,
            "total_sources_checked": len(sources),
        }


class ResearchReport:
    """Generates formatted research reports"""

    def __init__(
        self,
        query: str,
        sources: List[Source],
        citation_style: CitationStyle = CitationStyle.APA,
    ):
        self.query = query
        self.sources = sources
        self.citation_style = citation_style
        self.created_at = datetime.now()

    def generate_executive_summary(self, content: str) -> str:
        """Generate executive summary (first 200 words)"""
        words = content.split()
        summary_words = words[:200]
        summary = " ".join(summary_words)

        if len(words) > 200:
            summary += "..."

        return summary

    def generate_bibliography(self) -> str:
        """Generate bibliography in specified citation style"""
        bibliography = []

        # Sort sources by author/title
        sorted_sources = sorted(
            self.sources, key=lambda s: (s.author or s.title).lower()
        )

        for source in sorted_sources:
            citation = CitationFormatter.format(source, self.citation_style)
            bibliography.append(citation)

        return "\n\n".join(bibliography)

    def generate_markdown_report(self, content: str) -> str:
        """Generate complete research report in Markdown format"""
        report = []

        # Title
        report.append(f"# Research Report: {self.query}\n")

        # Metadata
        report.append(
            f"**Generated:** {self.created_at.strftime('%B %d, %Y at %I:%M %p')}"
        )
        report.append(f"**Citation Style:** {self.citation_style.value.upper()}")
        report.append(f"**Sources Consulted:** {len(self.sources)}\n")

        # Executive Summary
        report.append("## Executive Summary\n")
        report.append(self.generate_executive_summary(content))
        report.append("\n")

        # Main Content
        report.append("## Research Findings\n")
        report.append(content)
        report.append("\n")

        # Source Quality Analysis
        report.append("## Source Quality Analysis\n")

        credibility_levels = {}
        for source in self.sources:
            level = source.get_credibility_level()
            credibility_levels[level] = credibility_levels.get(level, 0) + 1

        report.append(
            f"- **Very High Credibility:** {credibility_levels.get(CredibilityLevel.VERY_HIGH, 0)} sources"
        )
        report.append(
            f"- **High Credibility:** {credibility_levels.get(CredibilityLevel.HIGH, 0)} sources"
        )
        report.append(
            f"- **Medium Credibility:** {credibility_levels.get(CredibilityLevel.MEDIUM, 0)} sources"
        )
        report.append(
            f"- **Low Credibility:** {credibility_levels.get(CredibilityLevel.LOW, 0)} sources"
        )
        report.append(
            f"- **Very Low Credibility:** {credibility_levels.get(CredibilityLevel.VERY_LOW, 0)} sources\n"
        )

        # Average credibility score
        avg_score = (
            sum(s.credibility_score for s in self.sources) / len(self.sources)
            if self.sources
            else 0
        )
        report.append(f"**Average Credibility Score:** {avg_score:.1f}/100\n")

        # Bibliography
        report.append("## References\n")
        report.append(self.generate_bibliography())
        report.append("\n")

        # Appendix: Source Details
        report.append("## Appendix: Source Details\n")
        for i, source in enumerate(self.sources, 1):
            report.append(f"### Source {i}: {source.title}\n")
            report.append(f"- **URL:** {source.url}")
            report.append(f"- **Type:** {source.source_type.value}")
            report.append(
                f"- **Credibility:** {source.credibility_score:.1f}/100 ({source.get_credibility_level().value})"
            )
            if source.author:
                report.append(f"- **Author:** {source.author}")
            if source.publication_date:
                report.append(
                    f"- **Published:** {source.publication_date.strftime('%B %d, %Y')}"
                )
            report.append(
                f"- **Accessed:** {source.access_date.strftime('%B %d, %Y')}\n"
            )

        return "\n".join(report)


class EnhancedResearcherAgent:
    """
    Enhanced Researcher Agent with deep research capabilities
    Implements SuperNinja-equivalent research features
    """

    def __init__(self):
        self.name = "Enhanced Researcher"
        self.description = "Deep research with multi-source verification and citations"
        self.capabilities = [
            "multi_source_research",
            "source_credibility_scoring",
            "citation_formatting",
            "fact_verification",
            "research_report_generation",
        ]
        self.credibility_scorer = SourceCredibilityScorer()
        self.fact_verifier = FactVerifier()

    async def deep_research(
        self,
        query: str,
        num_sources: int = 10,
        citation_style: CitationStyle = CitationStyle.APA,
        verify_facts: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform deep research with multiple sources

        Args:
            query: Research query
            num_sources: Number of sources to consult
            citation_style: Citation formatting style
            verify_facts: Whether to verify facts across sources

        Returns:
            Complete research results with sources, citations, and report
        """
        # Gather sources from web search
        sources = await self._gather_sources(query, num_sources)

        # Score credibility
        for source in sources:
            source.source_type = self.credibility_scorer.classify_source_type(
                source.url, source.content
            )
            source.credibility_score = self.credibility_scorer.score_source(source)

        # Sort by credibility
        sources.sort(key=lambda s: s.credibility_score, reverse=True)

        # Generate research content
        content = await self._synthesize_research(query, sources)

        # Verify facts if requested
        verified_claims = []
        if verify_facts:
            claims = self.fact_verifier.extract_claims(content)
            for claim in claims[:10]:  # Verify top 10 claims
                verification = self.fact_verifier.verify_claim(claim, sources)
                verified_claims.append(verification)

        # Generate report
        report = ResearchReport(query, sources, citation_style)
        markdown_report = report.generate_markdown_report(content)

        return {
            "query": query,
            "sources": [s.to_dict() for s in sources],
            "content": content,
            "verified_claims": verified_claims,
            "report": markdown_report,
            "citation_style": citation_style.value,
            "average_credibility": (
                sum(s.credibility_score for s in sources) / len(sources)
                if sources
                else 0
            ),
            "total_sources": len(sources),
        }

    async def _gather_sources(self, query: str, num_sources: int) -> List[Source]:
        """Gather sources from web search"""
        from app.integrations.web_search import unified_search

        # Search and scrape content
        results = await unified_search.search_and_scrape(
            query=query,
            num_results=num_sources,
            engines=["duckduckgo", "google", "bing"],
        )

        # Convert to Source objects
        sources = []
        for result in results:
            source = Source(
                url=result["url"],
                title=result["title"],
                content=result["content"],
                author=result.get("author"),
                publication_date=result.get("published_date"),
                publisher=result.get("publisher"),
            )
            sources.append(source)

        return sources

    async def _synthesize_research(self, query: str, sources: List[Source]) -> str:
        """Synthesize research content from multiple sources using AI"""
        from app.integrations.enhanced_ai_providers import enhanced_ai_manager

        # Prepare context from sources
        context = f"Research Query: {query}\n\n"
        context += "Sources:\n\n"

        for i, source in enumerate(sources[:5], 1):  # Top 5 sources
            context += f"[{i}] {source.title}\n"
            context += f"URL: {source.url}\n"
            context += f"Content: {source.content[:500]}...\n\n"

        # Create synthesis prompt
        messages = [
            {
                "role": "system",
                "content": "You are a research assistant. Synthesize information from multiple sources into a coherent research summary. Include in-text citations using [number] format.",
            },
            {
                "role": "user",
                "content": f"{context}\n\nPlease synthesize the above sources into a comprehensive research summary about: {query}\n\nInclude in-text citations [1], [2], etc. for each source used.",
            },
        ]

        # Use AI to synthesize (try multiple models with fallback)
        models_to_try = ["gpt-4o-mini", "claude-3-haiku-20240307", "gemini-1.5-flash"]

        for model_id in models_to_try:
            try:
                result = await enhanced_ai_manager.generate_completion(
                    model_id=model_id,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000,
                )

                if result and "content" in result:
                    return result["content"]
            except Exception as e:
                print(f"Failed to synthesize with {model_id}: {e}")
                continue

        # Fallback: simple concatenation
        content = f"Research findings for: {query}\n\n"
        for i, source in enumerate(sources[:5], 1):
            content += f"According to {source.title} [{i}], "
            content += source.content[:200] + "...\n\n"

        return content

    def format_citation(self, source: Source, style: CitationStyle) -> str:
        """Format a single citation"""
        return CitationFormatter.format(source, style)

    def score_credibility(self, source: Source) -> float:
        """Score source credibility"""
        return self.credibility_scorer.score_source(source)


# Global instance
enhanced_researcher = EnhancedResearcherAgent()
