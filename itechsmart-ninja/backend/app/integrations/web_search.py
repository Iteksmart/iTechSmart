"""
Web Search Integration - Multiple Search Engines
Provides unified interface for Google, Bing, DuckDuckGo, and web scraping
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import httpx
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus, urlparse
import os


class SearchResult:
    """Represents a single search result"""
    
    def __init__(
        self,
        title: str,
        url: str,
        snippet: str,
        source: str = "unknown",
        published_date: Optional[datetime] = None,
        score: float = 0.0
    ):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.published_date = published_date
        self.score = score
        self.domain = urlparse(url).netloc
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "domain": self.domain,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "score": self.score
        }


class WebScraper:
    """Web scraping utility for extracting content from URLs"""
    
    @staticmethod
    async def scrape_url(url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Scrape content from a URL
        
        Args:
            url: URL to scrape
            timeout: Request timeout in seconds
        
        Returns:
            Dictionary with title, content, author, date, etc.
        """
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title = ""
                if soup.title:
                    title = soup.title.string.strip()
                elif soup.find('h1'):
                    title = soup.find('h1').get_text().strip()
                
                # Extract author
                author = None
                author_meta = soup.find('meta', {'name': 'author'}) or \
                             soup.find('meta', {'property': 'article:author'})
                if author_meta:
                    author = author_meta.get('content', '').strip()
                
                # Extract publication date
                published_date = None
                date_meta = soup.find('meta', {'property': 'article:published_time'}) or \
                           soup.find('meta', {'name': 'publication_date'}) or \
                           soup.find('time')
                if date_meta:
                    date_str = date_meta.get('content') or date_meta.get('datetime', '')
                    if date_str:
                        try:
                            published_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        except:
                            pass
                
                # Extract publisher
                publisher = None
                publisher_meta = soup.find('meta', {'property': 'og:site_name'})
                if publisher_meta:
                    publisher = publisher_meta.get('content', '').strip()
                
                # Extract main content
                content = ""
                
                # Try to find main content area
                main_content = soup.find('article') or \
                              soup.find('main') or \
                              soup.find('div', {'class': re.compile(r'content|article|post', re.I)})
                
                if main_content:
                    # Remove script, style, nav, footer, etc.
                    for tag in main_content.find_all(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                        tag.decompose()
                    
                    # Get text
                    paragraphs = main_content.find_all('p')
                    content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                else:
                    # Fallback: get all paragraphs
                    paragraphs = soup.find_all('p')
                    content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                
                # Clean up content
                content = re.sub(r'\s+', ' ', content)
                content = re.sub(r'\n\s*\n', '\n\n', content)
                
                return {
                    "success": True,
                    "url": url,
                    "title": title,
                    "content": content[:10000],  # Limit to 10k chars
                    "author": author,
                    "published_date": published_date,
                    "publisher": publisher,
                    "content_length": len(content)
                }
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout",
                "url": url
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}",
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Scraping error: {str(e)}",
                "url": url
            }


class DuckDuckGoSearch:
    """DuckDuckGo search implementation (no API key required)"""
    
    @staticmethod
    async def search(query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Search using DuckDuckGo HTML
        
        Args:
            query: Search query
            num_results: Number of results to return
        
        Returns:
            List of SearchResult objects
        """
        results = []
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find result divs
                result_divs = soup.find_all('div', {'class': 'result'})
                
                for div in result_divs[:num_results]:
                    try:
                        # Extract title and URL
                        title_tag = div.find('a', {'class': 'result__a'})
                        if not title_tag:
                            continue
                        
                        title = title_tag.get_text().strip()
                        url = title_tag.get('href', '')
                        
                        # Extract snippet
                        snippet_tag = div.find('a', {'class': 'result__snippet'})
                        snippet = snippet_tag.get_text().strip() if snippet_tag else ""
                        
                        if title and url:
                            results.append(SearchResult(
                                title=title,
                                url=url,
                                snippet=snippet,
                                source="duckduckgo",
                                score=1.0 - (len(results) * 0.1)  # Decreasing score
                            ))
                    except Exception as e:
                        continue
                
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        
        return results


class GoogleSearchAPI:
    """Google Custom Search API implementation"""
    
    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = search_engine_id or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Search using Google Custom Search API
        
        Args:
            query: Search query
            num_results: Number of results to return
        
        Returns:
            List of SearchResult objects
        """
        if not self.api_key or not self.search_engine_id:
            return []
        
        results = []
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self.api_key,
                    "cx": self.search_engine_id,
                    "q": query,
                    "num": min(num_results, 10)  # Max 10 per request
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if "items" in data:
                    for i, item in enumerate(data["items"]):
                        results.append(SearchResult(
                            title=item.get("title", ""),
                            url=item.get("link", ""),
                            snippet=item.get("snippet", ""),
                            source="google",
                            score=1.0 - (i * 0.1)
                        ))
        
        except Exception as e:
            print(f"Google search error: {e}")
        
        return results


class BingSearchAPI:
    """Bing Search API implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BING_SEARCH_API_KEY")
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Search using Bing Search API
        
        Args:
            query: Search query
            num_results: Number of results to return
        
        Returns:
            List of SearchResult objects
        """
        if not self.api_key:
            return []
        
        results = []
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = "https://api.bing.microsoft.com/v7.0/search"
                headers = {
                    "Ocp-Apim-Subscription-Key": self.api_key
                }
                params = {
                    "q": query,
                    "count": num_results,
                    "responseFilter": "Webpages"
                }
                
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if "webPages" in data and "value" in data["webPages"]:
                    for i, item in enumerate(data["webPages"]["value"]):
                        results.append(SearchResult(
                            title=item.get("name", ""),
                            url=item.get("url", ""),
                            snippet=item.get("snippet", ""),
                            source="bing",
                            score=1.0 - (i * 0.1)
                        ))
        
        except Exception as e:
            print(f"Bing search error: {e}")
        
        return results


class UnifiedWebSearch:
    """
    Unified web search interface
    Aggregates results from multiple search engines
    """
    
    def __init__(self):
        self.google = GoogleSearchAPI()
        self.bing = BingSearchAPI()
        self.duckduckgo = DuckDuckGoSearch()
        self.scraper = WebScraper()
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        engines: List[str] = ["duckduckgo", "google", "bing"]
    ) -> List[SearchResult]:
        """
        Search across multiple engines and aggregate results
        
        Args:
            query: Search query
            num_results: Total number of results to return
            engines: List of engines to use
        
        Returns:
            Aggregated and deduplicated list of SearchResult objects
        """
        tasks = []
        
        # Create search tasks for each engine
        if "google" in engines:
            tasks.append(self.google.search(query, num_results))
        if "bing" in engines:
            tasks.append(self.bing.search(query, num_results))
        if "duckduckgo" in engines:
            tasks.append(self.duckduckgo.search(query, num_results))
        
        # Execute all searches concurrently
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        all_results = []
        for results in results_lists:
            if isinstance(results, list):
                all_results.extend(results)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        # Sort by score
        unique_results.sort(key=lambda x: x.score, reverse=True)
        
        return unique_results[:num_results]
    
    async def search_and_scrape(
        self,
        query: str,
        num_results: int = 10,
        engines: List[str] = ["duckduckgo", "google", "bing"]
    ) -> List[Dict[str, Any]]:
        """
        Search and scrape content from results
        
        Args:
            query: Search query
            num_results: Number of results to scrape
            engines: List of engines to use
        
        Returns:
            List of dictionaries with search results and scraped content
        """
        # Get search results
        search_results = await self.search(query, num_results, engines)
        
        # Scrape content from each URL
        scrape_tasks = [
            self.scraper.scrape_url(result.url)
            for result in search_results
        ]
        
        scraped_contents = await asyncio.gather(*scrape_tasks, return_exceptions=True)
        
        # Combine search results with scraped content
        combined_results = []
        
        for search_result, scraped in zip(search_results, scraped_contents):
            if isinstance(scraped, dict) and scraped.get("success"):
                combined_results.append({
                    "search_result": search_result.to_dict(),
                    "content": scraped.get("content", ""),
                    "title": scraped.get("title") or search_result.title,
                    "url": search_result.url,
                    "author": scraped.get("author"),
                    "published_date": scraped.get("published_date"),
                    "publisher": scraped.get("publisher"),
                    "snippet": search_result.snippet,
                    "source": search_result.source
                })
            else:
                # If scraping failed, use search result only
                combined_results.append({
                    "search_result": search_result.to_dict(),
                    "content": search_result.snippet,
                    "title": search_result.title,
                    "url": search_result.url,
                    "author": None,
                    "published_date": None,
                    "publisher": None,
                    "snippet": search_result.snippet,
                    "source": search_result.source
                })
        
        return combined_results


# Global instance
unified_search = UnifiedWebSearch()