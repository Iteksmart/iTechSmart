"""
Research Agent - Web search, data gathering, and citation
"""

from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
import logging

from app.agents.base_agent import BaseAgent, AgentCapability, AgentResponse

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Agent specialized in research and information gathering"""

    def __init__(self, ai_provider: str = "openai"):
        super().__init__(
            name="Researcher",
            description="Specialized in web research, data gathering, and providing cited information",
            ai_provider=ai_provider,
        )

        # Define capabilities
        self.capabilities = [
            AgentCapability(
                name="web_search",
                description="Search the web for information",
                required_tools=["search_api"],
            ),
            AgentCapability(
                name="web_scraping",
                description="Extract content from web pages",
                required_tools=["httpx", "beautifulsoup"],
            ),
            AgentCapability(
                name="citation_generation",
                description="Generate proper citations for sources",
                required_tools=[],
            ),
            AgentCapability(
                name="fact_verification",
                description="Verify facts across multiple sources",
                required_tools=["search_api"],
            ),
        ]

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task"""
        try:
            query = task.get("query", "")
            research_type = task.get("type", "general")  # general, deep, fact_check

            logger.info(f"Researcher executing: {query} (type: {research_type})")

            # Plan the research
            steps = await self.plan(task)

            # Execute research based on type
            if research_type == "deep":
                result = await self._deep_research(query, task)
            elif research_type == "fact_check":
                result = await self._fact_check(query, task)
            else:
                result = await self._general_research(query, task)

            # Log execution
            self.log_execution(task, result)

            return result

        except Exception as e:
            logger.error(f"Researcher execution failed: {str(e)}")
            return {"success": False, "error": str(e), "agent": self.name}

    async def _general_research(
        self, query: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform general research"""
        # Simulate web search (in production, use actual search API)
        results = await self._search_web(query, num_results=5)

        # Extract and summarize content
        summaries = []
        citations = []

        for i, result in enumerate(results, 1):
            summary = await self._extract_content(result["url"])
            summaries.append(summary)
            citations.append(
                {
                    "number": i,
                    "title": result["title"],
                    "url": result["url"],
                    "snippet": result["snippet"],
                }
            )

        return {
            "success": True,
            "query": query,
            "summaries": summaries,
            "citations": citations,
            "sources_count": len(citations),
            "agent": self.name,
        }

    async def _deep_research(self, query: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deep research with multiple sources"""
        # Search multiple times with different angles
        search_queries = [
            query,
            f"{query} latest research",
            f"{query} expert opinion",
            f"{query} statistics data",
        ]

        all_results = []
        for search_query in search_queries:
            results = await self._search_web(search_query, num_results=3)
            all_results.extend(results)

        # Remove duplicates
        unique_results = self._deduplicate_results(all_results)

        # Extract detailed content
        detailed_findings = []
        citations = []

        for i, result in enumerate(unique_results[:10], 1):
            content = await self._extract_content(result["url"])
            detailed_findings.append(
                {
                    "source": i,
                    "content": content,
                    "relevance": result.get("relevance", 0.8),
                }
            )
            citations.append(
                {
                    "number": i,
                    "title": result["title"],
                    "url": result["url"],
                    "snippet": result["snippet"],
                }
            )

        # Synthesize findings
        synthesis = await self._synthesize_findings(detailed_findings)

        return {
            "success": True,
            "query": query,
            "type": "deep_research",
            "synthesis": synthesis,
            "detailed_findings": detailed_findings,
            "citations": citations,
            "sources_count": len(citations),
            "agent": self.name,
        }

    async def _fact_check(self, claim: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Fact-check a claim"""
        # Search for evidence
        results = await self._search_web(f"fact check {claim}", num_results=5)

        # Analyze each source
        evidence = []
        for result in results:
            content = await self._extract_content(result["url"])
            evidence.append(
                {
                    "source": result["title"],
                    "url": result["url"],
                    "content": content,
                    "credibility": self._assess_credibility(result["url"]),
                }
            )

        # Determine verdict
        verdict = self._determine_verdict(evidence)

        return {
            "success": True,
            "claim": claim,
            "verdict": verdict,
            "evidence": evidence,
            "confidence": verdict.get("confidence", 0.0),
            "agent": self.name,
        }

    async def _search_web(
        self, query: str, num_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search the web (simulated - in production use actual search API)"""
        # This is a placeholder - in production, integrate with:
        # - Google Custom Search API
        # - Bing Search API
        # - DuckDuckGo API
        # - Or use the web-search tool from the system

        return [
            {
                "title": f"Result {i} for {query}",
                "url": f"https://example.com/result-{i}",
                "snippet": f"This is a snippet for result {i} about {query}",
                "relevance": 1.0 - (i * 0.1),
            }
            for i in range(1, num_results + 1)
        ]

    async def _extract_content(self, url: str) -> str:
        """Extract content from a URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                soup = BeautifulSoup(response.text, "html.parser")

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Get text
                text = soup.get_text()

                # Clean up
                lines = (line.strip() for line in text.splitlines())
                chunks = (
                    phrase.strip() for line in lines for phrase in line.split("  ")
                )
                text = " ".join(chunk for chunk in chunks if chunk)

                return text[:1000]  # Return first 1000 chars

        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {str(e)}")
            return f"[Content extraction failed: {str(e)}]"

    def _deduplicate_results(
        self, results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL"""
        seen_urls = set()
        unique = []

        for result in results:
            url = result["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                unique.append(result)

        return unique

    async def _synthesize_findings(self, findings: List[Dict[str, Any]]) -> str:
        """Synthesize research findings into a coherent summary"""
        # In production, use AI to synthesize
        # For now, return a placeholder
        return (
            f"Synthesized findings from {len(findings)} sources. "
            f"Key insights include comprehensive analysis of the topic with "
            f"verified information from multiple credible sources."
        )

    def _assess_credibility(self, url: str) -> float:
        """Assess source credibility (simplified)"""
        # In production, use more sophisticated credibility assessment
        credible_domains = [".edu", ".gov", ".org"]
        for domain in credible_domains:
            if domain in url:
                return 0.9
        return 0.7

    def _determine_verdict(self, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine fact-check verdict"""
        # Simplified verdict determination
        avg_credibility = (
            sum(e["credibility"] for e in evidence) / len(evidence) if evidence else 0
        )

        if avg_credibility > 0.8:
            verdict = "TRUE"
            confidence = avg_credibility
        elif avg_credibility > 0.5:
            verdict = "PARTIALLY TRUE"
            confidence = avg_credibility
        else:
            verdict = "UNVERIFIED"
            confidence = avg_credibility

        return {
            "verdict": verdict,
            "confidence": confidence,
            "sources_analyzed": len(evidence),
        }
