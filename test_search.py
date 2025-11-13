#!/usr/bin/env python3
"""Test script to verify web search functionality and logging."""

import asyncio
import sys
from src.coding_agent.tools.web_search import WebSearch


async def test_search():
    """Test the web search functionality."""
    print("Testing DDGS web search functionality...")
    print("=" * 60)

    try:
        # Initialize search tool
        print("1. Initializing WebSearch tool...")
        search_tool = WebSearch()
        print("   ✅ WebSearch initialized successfully\n")

        # Test search
        query = "Python fibonacci function example"
        print(f"2. Searching for: '{query}'")
        print("-" * 60)

        results = await search_tool.search(query, max_results=3)

        if results:
            print(f"   📊 Found {len(results)} result(s):\n")
            for idx, result in enumerate(results, 1):
                if result.source != "error":
                    print(f"   {idx}. {result.title}")
                    print(f"      {result.snippet[:100]}...")
                    print(f"      URL: {result.url}")
                else:
                    print(f"   {idx}. ❌ Error: {result.snippet}")
                print()
        else:
            print("   ⚠️  No results returned")

        print("=" * 60)
        print("Test completed successfully!")
        print("If you see search results above, the ddgs integration is working.")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed the ddgs package:")
        print("   pip install ddgs")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_search())
