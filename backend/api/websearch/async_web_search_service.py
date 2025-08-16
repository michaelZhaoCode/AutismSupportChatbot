"""
Async Web Search Service

This module provides an async web search service that:
1. Takes a user prompt and generates multiple search queries using LLM
2. For each search query, retrieves multiple web results concurrently
3. Extracts content from each web result concurrently
4. Returns the first m characters of every result for LLM processing

All operations are performed asynchronously using asyncio for maximum performance.
"""

import os
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
# Add PDF extraction support
import io
import PyPDF2
from urllib.parse import urlparse
from constants import ALLOWED_DOMAINS, ENABLE_DOMAIN_FILTERING

load_dotenv()
logger = logging.getLogger(__name__)


class AsyncWebSearchService:
    """
    Advanced async web search service that generates multiple queries and extracts content concurrently.
    """
    
    def __init__(self, 
                 num_search_queries: int = 3,
                 num_results_per_query: int = 3,
                 request_timeout: int = 10,
                 max_concurrent_requests: int = 10):
        """
        Initialize the async web search service.
        
        Args:
            num_search_queries: Number of search queries to generate from prompt
            num_results_per_query: Number of web results per search query
            request_timeout: Timeout for web requests in seconds
            max_concurrent_requests: Maximum concurrent HTTP requests
        """
        # Search API configuration
        self.google_api_key = os.environ["GOOGLE_SEARCH_API_KEY"]
        self.google_search_engine_id = os.environ["GOOGLE_SEARCH_ENGINE_ID"]
        self.serpapi_key = os.environ["SERPAPI_KEY"]
        
        # Service configuration
        self.num_search_queries = num_search_queries
        self.num_results_per_query = num_results_per_query
        self.request_timeout = request_timeout
        self.max_concurrent_requests = max_concurrent_requests
        
        # Create semaphore for limiting concurrent requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # Headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Domain filtering configuration
        self.enable_domain_filtering = ENABLE_DOMAIN_FILTERING
        self.allowed_domains = ALLOWED_DOMAINS

    
    def is_url_allowed(self, url: str) -> bool:
        """
        Check if a URL is from an allowed domain.
        
        Args:
            url: The URL to check
            
        Returns:
            True if domain filtering is disabled or URL is from allowed domain, False otherwise
        """
        # If domain filtering is disabled, allow all URLs
        if not self.enable_domain_filtering:
            return True
        
        try:
            parsed_url = urlparse(url.lower())
            domain = parsed_url.netloc
            
            # Remove 'www.' prefix for comparison
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check against allowed domains
            for allowed_domain in self.allowed_domains:
                allowed_domain_lower = allowed_domain.lower()
                if domain in allowed_domain_lower or allowed_domain_lower in domain:
                    return True
            
            logger.debug(f"URL blocked by domain filter: {url} (domain: {domain})")
            return False
            
        except Exception as e:
            logger.error(f"Error parsing URL for domain check: {url}, error: {str(e)}")
            return False
    
    async def generate_search_queries(self, prompt: str, llm_generate_func: callable) -> list[str]:
        """
        Generate multiple search queries from a user prompt using LLM asynchronously.
        
        Args:
            prompt: The original user prompt
            llm_generate_func: Async function to call LLM for query generation
            
        Returns:
            List of search queries (always returns at least the original prompt)
        """
        try:
            query_generation_prompt = f"""
            Given the following user question, generate {self.num_search_queries} different search queries that would help find comprehensive information to answer the question.
            
            Make the search queries:
            1. Specific and focused
            2. Use different keywords and approaches
            3. Cover different aspects of the topic
            4. Be suitable for web search engines
            
            User question: {prompt}
            
            Respond with only the search queries, one per line, without numbering or bullets:
            """
            
            response = await llm_generate_func(query_generation_prompt)
            
            # Parse the response to extract individual queries
            queries = []
            for line in response.strip().split('\n'):
                line = line.strip()
                # Remove any numbering or bullets
                line = re.sub(r'^\d+\.?\s*', '', line)
                line = re.sub(r'^[-*•]\s*', '', line)
                if line and len(line) > 5:  # Minimum length check
                    queries.append(line)
            
            # Ensure we have at least the original prompt
            if not queries:
                queries = [prompt]
            
            # Fill up to desired number with variations if needed
            while len(queries) < self.num_search_queries:
                if len(queries) == 1:
                    queries.append(f"what is {prompt}")
                elif len(queries) == 2:
                    queries.append(f"how to {prompt}")
                else:
                    break
            
            logger.info(f"Generated {len(queries)} search queries: {queries}")
            return queries[:self.num_search_queries]
            
        except Exception as e:
            logger.error(f"Error generating search queries: {str(e)}")
            # Always return at least the original prompt
            return [prompt]
    
    async def search_google_custom(self, session: aiohttp.ClientSession, query: str) -> list[dict]:
        """
        Perform search using Google Custom Search API asynchronously.
        
        Args:
            session: aiohttp ClientSession
            query: Search query string
            
        Returns:
            List of search results, or None if search fails
        """
        if not self.google_api_key or not self.google_search_engine_id:
            return None
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_search_engine_id,
                "q": query,
                "num": self.num_results_per_query
            }
            
            async with self.semaphore:
                async with session.get(url, params=params, timeout=self.request_timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        if "items" in data:
                            for item in data["items"]:
                                results.append({
                                    "title": item.get("title", ""),
                                    "snippet": item.get("snippet", ""),
                                    "url": item.get("link", ""),
                                    "source": "Google Custom Search"
                                })
                        
                        return results if results else None
                    else:
                        logger.error(f"Google Custom Search API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error with Google Custom Search: {str(e)}")
            return None
    
    async def search_serpapi(self, session: aiohttp.ClientSession, query: str) -> list[dict]:
        """
        Perform search using SerpAPI asynchronously.
        
        Args:
            session: aiohttp ClientSession
            query: Search query string
            
        Returns:
            List of search results, or None if search fails
        """
        if not self.serpapi_key:
            return None
        
        try:
            url = "https://serpapi.com/search"
            params = {
                "api_key": self.serpapi_key,
                "engine": "google",
                "q": query,
                "num": self.num_results_per_query
            }
            
            async with self.semaphore:
                async with session.get(url, params=params, timeout=self.request_timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        if "organic_results" in data:
                            for item in data["organic_results"]:
                                results.append({
                                    "title": item.get("title", ""),
                                    "snippet": item.get("snippet", ""),
                                    "url": item.get("link", ""),
                                    "source": "SerpAPI"
                                })
                        
                        return results if results else None
                    else:
                        logger.error(f"SerpAPI error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error with SerpAPI: {str(e)}")
            return None
    
    async def extract_content_from_url(self, session: aiohttp.ClientSession, url: str) -> str:
        """
        Extract text content from a web page or PDF asynchronously.
        
        Args:
            session: aiohttp ClientSession
            url: URL to extract content from
            
        Returns:
            Extracted text content, or None if extraction fails
        """
        try:
            # Check if URL is a PDF
            is_pdf = 'pdf' in url.lower()
            
            # Skip other document types that we can't process
            skip_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                logger.debug(f"Skipping unsupported file type: {url}")
                return None
            
            async with self.semaphore:
                async with session.get(url, headers=self.headers, timeout=self.request_timeout) as response:
                    if response.status != 200:
                        logger.debug(f"HTTP {response.status} for URL: {url}")
                        return None
                    
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Handle PDF content
                    if is_pdf or 'application/pdf' in content_type:
                        return await self._extract_pdf_content(response)
                    
                    # Handle HTML content
                    elif 'text/html' in content_type or not content_type:
                        content = await response.text()
                        return self._extract_html_content(content)
                    
                    # Handle plain text
                    elif 'text/plain' in content_type:
                        text_content = await response.text()
                        return self._clean_text(text_content)
                    
                    else:
                        logger.debug(f"Unsupported content type '{content_type}' for URL: {url}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout while fetching content from {url}")
            return None
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return None
    
    async def _extract_pdf_content(self, response: aiohttp.ClientResponse) -> str:
        """Extract text content from PDF response."""
        try:
            pdf_data = await response.read()
            pdf_file = io.BytesIO(pdf_data)
            
            reader = PyPDF2.PdfReader(pdf_file)
            text_content = ""
            
            # Extract text from all pages
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            return self._clean_text(text_content)
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            return None
    
    def _extract_html_content(self, html_content: str) -> str:
        """Extract and clean text content from HTML."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 
                                'meta', 'link', 'noscript', 'iframe']):
                element.decompose()
            
            # Try to find main content areas in order of preference
            content_selectors = [
                'article',
                'main', 
                '[role="main"]',
                '.content',
                '#content',
                '.post-content',
                '.entry-content', 
                '.article-content',
                '.article-body',
                '.story-body',
                '.post-body'
            ]
            
            extracted_content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    # Get text from all matching elements
                    texts = []
                    for elem in elements:
                        elem_text = elem.get_text(separator=' ', strip=True)
                        if len(elem_text) > 100:  # Only include substantial content
                            texts.append(elem_text)
                    
                    if texts:
                        extracted_content = ' '.join(texts)
                        break
            
            # Fallback: extract from body but filter out noise
            if not extracted_content or len(extracted_content) < 200:
                body = soup.find('body')
                if body:
                    # Remove common noise elements from body
                    for noise in body.select('.advertisement, .ads, .social-share, .comments, '
                                           '.related-articles, .sidebar, .menu, .navigation'):
                        noise.decompose()
                    
                    extracted_content = body.get_text(separator=' ', strip=True)
            
            return self._clean_text(extracted_content)
            
        except Exception as e:
            logger.error(f"HTML parsing error: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return None
        
        try:
            # Remove extra whitespace and normalize
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Return None if text is empty after cleaning
            if not text:
                return None
            
            # Remove common web artifacts
            text = re.sub(r'Cookie\s+Policy|Privacy\s+Policy|Terms\s+of\s+Service', '', text, flags=re.IGNORECASE)
            text = re.sub(r'Skip\s+to\s+(main\s+)?content', '', text, flags=re.IGNORECASE)
            text = re.sub(r'Advertisement\s*', '', text, flags=re.IGNORECASE)
            
            # Remove excessive repetition (basic deduplication)
            words = text.split()
            if len(words) > 10:
                # Remove if more than 30% of content is repeated words
                word_counts = {}
                for word in words:
                    if len(word) > 3:  # Only check words longer than 3 chars
                        word_counts[word.lower()] = word_counts.get(word.lower(), 0) + 1
                
                total_words = len([w for w in words if len(w) > 3])
                repeated_words = sum(count - 1 for count in word_counts.values() if count > 1)
                
                if total_words > 0 and repeated_words / total_words > 0.3:
                    logger.debug("Content appears to be highly repetitive, may be low quality")
            
            return text if text.strip() else None
            
        except Exception as e:
            logger.error(f"Text cleaning error: {str(e)}")
            return None
    
    async def search_single_query(self, session: aiohttp.ClientSession, query: str) -> list[dict]:
        """
        Search for a single query using available APIs asynchronously.
        
        Args:
            session: aiohttp ClientSession
            query: Search query
            
        Returns:
            List of search results (empty list if all searches fail)
        """
        search_results = []
        
        # Try Google Custom Search first
        if self.google_api_key:
            google_results = await self.search_google_custom(session, query)
            if google_results is not None:
                search_results = google_results
        
        # Fallback to SerpAPI if Google didn't work
        if not search_results and self.serpapi_key:
            serpapi_results = await self.search_serpapi(session, query)
            if serpapi_results is not None:
                search_results = serpapi_results
        
        return search_results
    
    async def extract_content_from_results(self, session: aiohttp.ClientSession, search_results: list[dict], query: str) -> list[dict]:
        """
        Extract content from all search results concurrently.
        
        Args:
            session: aiohttp ClientSession
            search_results: List of search results
            query: Original search query
            
        Returns:
            List of results with extracted content (empty list if all extractions fail)
        """
        # Create tasks for concurrent content extraction
        extraction_tasks = []
        for result in search_results:
            url = result.get('url', '')
            if url and self.is_url_allowed(url):
                task = self.extract_content_from_url(session, url)
                extraction_tasks.append((task, result))
        
        # Execute all extraction tasks concurrently
        results_with_content = []
        if extraction_tasks:
            # Extract all tasks and their corresponding results
            tasks, results = zip(*extraction_tasks)
            extracted_contents = await asyncio.gather(*tasks, return_exceptions=False)
            
            for (extracted_content, result) in zip(extracted_contents, results):
      
                # Use extracted content or fallback to snippet
                if extracted_content is not None:
                    final_content = extracted_content
                else:
                    # Fallback to snippet if content extraction failed
                    final_content = result.get('snippet', '')
                
                # Only include results with some content
                if final_content and final_content.strip():
                    result_entry = {
                        'title': result.get('title', 'Untitled'),
                        'contents': final_content,
                        'url': result.get('url', ''),
                        'query': query,
                        'source': result.get('source', 'Unknown'),
                        'content_length': len(final_content)
                    }
                    results_with_content.append(result_entry)
        
        return results_with_content
    
    async def search_and_extract(self, prompt: str, llm_generate_func: callable) -> list[dict]:
        """
        Main async method: generate queries, search, and extract content concurrently.
        
        Args:
            prompt: User's original prompt
            llm_generate_func: Async function to call LLM for query generation
            
        Returns:
            List of dictionaries containing search results with extracted content
        """
        logger.info(f"Starting async web search and content extraction for prompt: {prompt}")
        
        # Step 1: Generate multiple search queries
        search_queries = await self.generate_search_queries(prompt, llm_generate_func)
        logger.info(f"Generated {len(search_queries)} search queries")
        
        # Create aiohttp session with timeout
        timeout = aiohttp.ClientTimeout(total=self.request_timeout * 2)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Step 2: Search for all queries concurrently
            search_tasks = [self.search_single_query(session, query) for query in search_queries]
            search_results_lists = await asyncio.gather(*search_tasks, return_exceptions=False)
            
            # Flatten search results and associate with queries
            all_search_results = []
            for i, search_results in enumerate(search_results_lists):
                query = search_queries[i]
                # Filter out empty results
                if search_results:
                    logger.info(f"Found {len(search_results)} search results for query: {query}")
                    all_search_results.append((query, search_results))
                else:
                    logger.warning(f"No search results found for query: {query}")
            
            # Step 3: Extract content from all URLs concurrently
            extraction_tasks = []
            for query, search_results in all_search_results:
                task = self.extract_content_from_results(session, search_results, query)
                extraction_tasks.append(task)
            
            # Execute all content extraction tasks concurrently
            all_results_lists = await asyncio.gather(*extraction_tasks, return_exceptions=False)
            
            # Flatten all results and filter out empty ones
            all_results = []
            for results_list in all_results_lists:
                if results_list:  # Only extend if results_list is not empty
                    all_results.extend(results_list)
        
        logger.info(f"Completed async web search and extraction. Total results: {len(all_results)}")
        return all_results
    

def create_async_web_search_service(num_search_queries: int = 3,
                                  num_results_per_query: int = 3,
                                  max_concurrent_requests: int = 10) -> AsyncWebSearchService:
    """
    Factory function to create an AsyncWebSearchService instance.
    
    Args:
        num_search_queries: Number of search queries to generate
        num_results_per_query: Number of results per query
        max_concurrent_requests: Maximum concurrent HTTP requests
        
    Returns:
        AsyncWebSearchService instance
    """
    return AsyncWebSearchService(
        num_search_queries=num_search_queries,
        num_results_per_query=num_results_per_query,
        max_concurrent_requests=max_concurrent_requests
    ) 