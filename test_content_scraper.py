#!/usr/bin/env python3
"""Test script for ContentScraper"""

from app.services.content_scraper import ContentScraper
import json

def test_content_scraper():
    print("Testing ContentScraper...")

    # Initialize scraper
    scraper = ContentScraper()
    print("ContentScraper initialized successfully")

    try:
        # Test with a real URL that has more content and headings
        test_url = 'https://www.runnersworld.com/gear/a19663621/best-running-shoes/'  # Real article with headings
        print(f"\nTesting scrape_single with: {test_url}")

        result = scraper.scrape_single(test_url)
        print(f"Result keys: {list(result.keys())}")
        print(f"Success: {result.get('success', False)}")

        if result.get('success'):
            print(f"Title: {result.get('title', 'N/A')}")
            print(f"Description: {result.get('description', 'N/A')}")
            print(f"Heading count: {result.get('heading_count', 0)}")

            headings = result.get('headings', [])
            print(f"Headings found: {len(headings)}")

            if headings:
                print("\nFirst few headings:")
                for i, heading in enumerate(headings[:5], 1):
                    print(f"  {i}. {heading['level']}: {heading['text'][:60]}...")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

        # Test with multiple URLs
        print("\nTesting scrape_urls with multiple URLs...")
        urls = [
            'https://httpbin.org/html',
            'https://example.com',
            'https://httpbin.org/status/404'  # This should fail
        ]

        multi_results = scraper.scrape_urls(urls)
        print(f"Multi-scrape results: {len(multi_results)}")

        success_count = sum(1 for r in multi_results if r.get('success'))
        print(f"Successful scrapes: {success_count}/{len(multi_results)}")

        # Test extract_common_topics
        print("\nTesting extract_common_topics...")
        if multi_results:
            common_topics = scraper.extract_common_topics(multi_results)
            print(f"Common topics found: {len(common_topics)}")
            if common_topics:
                print("Top common topics:")
                for topic in common_topics[:5]:
                    print(f"  - {topic}")

        print("\nContentScraper test completed successfully!")

    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_content_scraper()