#!/usr/bin/env python3
"""Test script for WebSearchService"""

from app.services.web_search import WebSearchService
import json

def test_web_search():
    print("Testing WebSearchService with SerpAPI...")

    # Initialize service
    search = WebSearchService()
    print(f"Service initialized with API key: {bool(search.api_key)}")
    print(f"Base URL: {search.base_url}")

    try:
        # Test single search
        print("\nTesting search_single...")
        results = search.search_single('best running shoes', count=3)
        print(f"Number of results: {len(results)}")

        if results:
            print("\nFirst result:")
            print(json.dumps(results[0], indent=2))

            # Validate structure
            required_keys = ['title', 'url', 'description', 'position']
            print("\nValidating result structure:")
            for i, result in enumerate(results, 1):
                missing_keys = [key for key in required_keys if key not in result]
                if missing_keys:
                    print(f"Result {i}: MISSING keys {missing_keys}")
                else:
                    print(f"Result {i}: OK - {result['title'][:50]}...")
        else:
            print("No results returned")

        # Test multiple keywords
        print("\nTesting search_keywords...")
        multi_results = search.search_keywords(['running shoes', 'best sneakers'], count=2)
        print(f"Multi-search results for {len(multi_results)} keywords")

        for keyword, res in multi_results.items():
            print(f"  {keyword}: {len(res)} results")

        print("\nTest completed successfully!")

    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_search()