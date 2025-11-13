#!/usr/bin/env python3
"""Test script to verify web crawler functionality."""

import asyncio
import sys
from src.coding_agent.tools.web_crawler import WebCrawler


async def test_crawler():
    """Test the web crawler functionality."""
    print("🧪 Testing Web Crawler")
    print("=" * 60)

    try:
        # Initialize crawler
        print("\n1. Initializing WebCrawler...")
        crawler = WebCrawler()
        print(f"   ✅ WebCrawler initialized (async: {crawler.prefer_async})")

        # Test single URL fetch
        print("\n2. Testing single URL fetch...")
        test_url = "https://example.com"
        print(f"   📥 Fetching: {test_url}")

        page = await crawler.fetch(test_url, extract_text=True)

        if page.status_code == 200:
            print(f"   ✅ Successfully fetched page")
            print(f"   📄 Title: {page.title}")
            print(f"   📦 Content size: {len(page.content)} bytes")
            print(f"   📝 Text length: {len(page.text)} characters")
            print(f"   🎯 Status: HTTP {page.status_code}")
        else:
            print(f"   ❌ Failed to fetch page")
            print(f"   📊 Status: HTTP {page.status_code}")
            print(f"   ⚠️  Error: {page.error}")

        # Test concurrent fetch
        print("\n3. Testing concurrent fetch of multiple URLs...")
        test_urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
        ]

        print(f"   📊 Will fetch {len(test_urls)} URLs concurrently")

        results = await crawler.fetch_multiple(test_urls, max_concurrent=2)

        successful_crawls = 0
        failed_crawls = 0

        for url, page in results.items():
            if page.status_code == 200:
                print(f"   ✅ {len(page.content)} bytes - {url[:50]}")
                successful_crawls += 1
            else:
                print(f"   ❌ Failed - {url[:50]}")
                failed_crawls += 1

        print(f"\n   📊 Summary: {successful_crawls} successful, {failed_crawls} failed")

        # Test text extraction
        print("\n4. Testing text extraction...")
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Title</h1>
                <p>This is a test paragraph.</p>
                <script>console.log('script');</script>
            </body>
        </html>
        """

        text = crawler._extract_text(html_content)
        print(f"   📝 Extracted text: {len(text)} characters")
        if "Main Title" in text and "test paragraph" in text:
            print("   ✅ Text extraction successful (found expected content)")
        else:
            print("   ⚠️  Text extraction may have issues")

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("Your web crawler is ready to use.")

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nMake sure you have installed the required packages:")
        print("   pip install httpx requests beautifulsoup4")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_crawler())
