"""Web crawler tool for fetching and extracting content from web pages."""

import asyncio
import click
from typing import Optional, Dict, Any, List
import urllib.parse

try:
    import requests
    from bs4 import BeautifulSoup
    import httpx
except ImportError:
    requests = None
    BeautifulSoup = None
    httpx = None


class WebPage:
    """Represents a crawled web page."""

    def __init__(
        self,
        url: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        text: Optional[str] = None,
        status_code: Optional[int] = None,
        error: Optional[str] = None,
        content_type: Optional[str] = None,
    ):
        self.url = url
        self.title = title
        self.content = content
        self.text = text
        self.status_code = status_code
        self.error = error
        self.content_type = content_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "content_length": len(self.content) if self.content else 0,
            "status_code": self.status_code,
            "error": self.error,
            "content_type": self.content_type,
        }


class WebCrawler:
    """Web crawler for fetching and extracting content from web pages."""

    def __init__(
        self,
        timeout: int = 10,
        user_agent: Optional[str] = None,
        prefer_async: bool = True,
    ):
        """Initialize web crawler.

        Args:
            timeout: Request timeout in seconds (default: 10)
            user_agent: User agent string (default: browser-like)
            prefer_async: Use httpx (async) if available, otherwise requests (sync)
        """
        if httpx is None and requests is None:
            raise ImportError(
                "Required packages not installed. Run: pip install requests beautifulsoup4 httpx"
            )

        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.prefer_async = prefer_async and httpx is not None

        click.echo(f"✅ WebCrawler initialized (async: {self.prefer_async})")

    async def fetch(self, url: str, extract_text: bool = True) -> WebPage:
        """Fetch a web page.

        Args:
            url: URL to fetch
            extract_text: Extract plain text from HTML (default: True)

        Returns:
            WebPage object with fetched content
        """
        click.echo(f"\n📥 Crawling: {url}")

        if self.prefer_async and httpx:
            return await self._fetch_async(url, extract_text)
        else:
            # Run sync function in thread pool since requests is synchronous
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._fetch_sync, url, extract_text)

    async def fetch_multiple(
        self, urls: List[str], extract_text: bool = True, max_concurrent: int = 5
    ) -> Dict[str, WebPage]:
        """Fetch multiple web pages concurrently.

        Args:
            urls: List of URLs to fetch
            extract_text: Extract plain text from HTML (default: True)
            max_concurrent: Maximum concurrent requests (default: 5)

        Returns:
            Dictionary mapping URL to WebPage object
        """
        click.echo(f"\n📊 Fetching {len(urls)} URL(s) concurrently (max {max_concurrent} at a time)")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(url: str) -> WebPage:
            async with semaphore:
                return await self.fetch(url, extract_text)

        tasks = [fetch_with_semaphore(url) for url in urls]
        pages = await asyncio.gather(*tasks, return_exceptions=True)

        result = {}
        for url, page in zip(urls, pages):
            if isinstance(page, Exception):
                error_page = WebPage(url=url, error=str(page))
                result[url] = error_page
            else:
                result[url] = page

        return result

    async def _fetch_async(self, url: str, extract_text: bool = True) -> WebPage:
        """Asynchronous fetch using httpx."""
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
            ) as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(url, headers=headers)

                return self._process_response(response, url, extract_text)

        except Exception as e:
            click.echo(f"❌ Async fetch failed: {str(e)}")
            return WebPage(url=url, error=str(e), status_code=0)

    def _fetch_sync(self, url: str, extract_text: bool = True) -> WebPage:
        """Synchronous fetch using requests."""
        try:
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, timeout=self.timeout, headers=headers, allow_redirects=True)

            return self._process_response(response, url, extract_text)

        except Exception as e:
            click.echo(f"❌ Sync fetch failed: {str(e)}")
            return WebPage(url=url, error=str(e), status_code=0)

    def _process_response(self, response, url: str, extract_text: bool) -> WebPage:
        """Process HTTP response and extract content."""
        page = WebPage(url=url, status_code=response.status_code)

        # Check if request was successful
        if response.status_code != 200:
            page.error = f"HTTP {response.status_code}: {response.reason_phrase if hasattr(response, 'reason_phrase') else ''}"
            click.echo(f"❌ HTTP error: {page.error}")
            return page

        click.echo(f"✅ HTTP {response.status_code} - OK")

        # Get content type
        content_type = response.headers.get("content-type", "").lower()
        page.content_type = content_type

        # Get content
        if hasattr(response, "text"):
            page.content = response.text
        else:
            page.content = response.content.decode("utf-8", errors="ignore")

        click.echo(f"📦 Content length: {len(page.content)} bytes")

        # Extract text if HTML
        if "text/html" in content_type and extract_text:
            page.text = self._extract_text(page.content)
            click.echo(f"📝 Extracted text: {len(page.text)} characters")

            if page.text:
                # Show first few lines
                lines = page.text.strip().split("\n")[:3]
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        click.echo(f"   Line {i}: {line.strip()[:80]}...")

        elif extract_text:
            page.text = page.content
            click.echo("📝 Using raw content as text")

        # Extract title if HTML
        if "text/html" in content_type:
            page.title = self._extract_title(page.content)
            if page.title:
                click.echo(f"📄 Page title: {page.title}")

        return page

    def _extract_text(self, html: str) -> str:
        """Extract plain text from HTML."""
        if BeautifulSoup is None:
            return ""

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Get text
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            click.echo(f"⚠️  Text extraction failed: {str(e)}")
            return ""

    def _extract_title(self, html: str) -> Optional[str]:
        """Extract title from HTML."""
        if BeautifulSoup is None:
            return None

        try:
            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")
            if title_tag:
                return title_tag.get_text().strip()
        except Exception:
            pass

        return None

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            return urllib.parse.urlparse(url).netloc
        except Exception:
            return None
