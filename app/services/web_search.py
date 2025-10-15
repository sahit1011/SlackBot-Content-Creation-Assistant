# app/services/web_search.py
import requests
import time
from typing import List, Dict
from app.config import Config

class WebSearchService:
    """Search the web for top-ranking content"""

    def __init__(self):
        self.api_key = Config.SERP_API_KEY
        self.base_url = "https://serpapi.com/search.json"
        self.rate_limit_delay = 1  # seconds between requests
        self.last_request_time = 0

    def search_keywords(self, keywords: List[str], count: int = 5) -> Dict[str, List[Dict]]:
        """
        Search for multiple keywords

        Args:
            keywords: List of keywords to search
            count: Number of results per keyword

        Returns:
            Dict mapping keyword to list of search results
        """
        results = {}

        for keyword in keywords:
            try:
                results[keyword] = self.search_single(keyword, count)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                print(f"Error searching '{keyword}': {str(e)}")
                results[keyword] = []

        return results

    def search_single(self, query: str, count: int = 5) -> List[Dict]:
        """
        Search for a single keyword

        Args:
            query: Search query
            count: Number of results

        Returns:
            List of search results
        """
        # # For testing without valid API key, return mock data
        # if not self.api_key or self.api_key == 'your_serpapi_api_key_here':
        #     print("Using mock data for testing (API key not configured)")
        #     return self._get_mock_results(query, count)

        # Rate limiting
        self._wait_for_rate_limit()

        params = {
            'api_key': self.api_key,
            'q': query,
            'num': count,
            'engine': 'google'
        }

        headers = {
            'Accept': 'application/json'
        }

        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_results(data)
                elif response.status_code == 429:
                    # Rate limited
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Search API error: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    return []

            except requests.exceptions.RequestException as e:
                print(f"Request failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return []

        return []

    def _parse_results(self, data: Dict) -> List[Dict]:
        """Parse search API response"""
        results = []

        organic_results = data.get('organic_results', [])

        for result in organic_results:
            results.append({
                'title': result.get('title', ''),
                'url': result.get('link', ''),
                'description': result.get('snippet', ''),
                'position': len(results) + 1
            })

        return results

    def _wait_for_rate_limit(self):
        """Ensure rate limit delay between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)

        self.last_request_time = time.time()

    def _get_mock_results(self, query: str, count: int) -> List[Dict]:
        """Return mock search results for testing"""
        mock_results = [
            {
                'title': f'Best {query.title()} - Top 10 Reviews 2024',
                'url': f'https://example.com/best-{query.replace(" ", "-")}-2024',
                'description': f'Comprehensive guide to the best {query} available. Read reviews, comparisons, and expert recommendations.',
                'position': 1
            },
            {
                'title': f'{query.title()} Buying Guide - What to Look For',
                'url': f'https://example.com/{query.replace(" ", "-")}-buying-guide',
                'description': f'Everything you need to know before buying {query}. Features, prices, and top recommendations.',
                'position': 2
            },
            {
                'title': f'Top {query.title()} of 2024 - Expert Picks',
                'url': f'https://example.com/top-{query.replace(" ", "-")}-2024',
                'description': f'Our experts have tested and reviewed the top {query} options. Find the perfect one for you.',
                'position': 3
            },
            {
                'title': f'{query.title()} Reviews - Consumer Reports',
                'url': f'https://example.com/{query.replace(" ", "-")}-reviews',
                'description': f'Honest reviews of popular {query} from real users. Pros, cons, and ratings.',
                'position': 4
            },
            {
                'title': f'How to Choose the Right {query.title()}',
                'url': f'https://example.com/how-to-choose-{query.replace(" ", "-")}',
                'description': f'Learn what factors to consider when selecting {query}. Make an informed decision.',
                'position': 5
            }
        ]

        return mock_results[:count]