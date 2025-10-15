# app/services/content_scraper.py
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time

class ContentScraper:
    """Scrape and extract content structure from web pages"""

    def __init__(self):
        self.timeout = 10
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape_urls(self, urls: List[str]) -> List[Dict]:
        """
        Scrape multiple URLs

        Args:
            urls: List of URLs to scrape

        Returns:
            List of scraping results
        """
        results = []

        for url in urls:
            try:
                result = self.scrape_single(url)
                results.append(result)
                time.sleep(0.5)  # Be polite
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })

        return results

    def scrape_single(self, url: str) -> Dict:
        """
        Scrape a single URL

        Args:
            url: URL to scrape

        Returns:
            Dictionary with headings and metadata
        """
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract headings
            headings = self._extract_headings(soup)

            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''

            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''

            return {
                'url': url,
                'success': True,
                'title': title_text,
                'description': description,
                'headings': headings,
                'heading_count': len(headings)
            }

        except requests.exceptions.Timeout:
            return {
                'url': url,
                'success': False,
                'error': 'Request timeout'
            }
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'success': False,
                'error': str(e)
            }

    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all headings from HTML"""
        headings = []

        for tag in ['h1', 'h2', 'h3']:
            for heading in soup.find_all(tag):
                text = heading.get_text().strip()

                # Clean text
                text = ' '.join(text.split())

                if text and len(text) > 3:  # Filter very short headings
                    headings.append({
                        'level': tag,
                        'text': text,
                        'position': len(headings) + 1
                    })

        return headings

    def extract_common_topics(self, scraped_results: List[Dict]) -> List[str]:
        """
        Find common topics across multiple pages

        Args:
            scraped_results: List of scraping results

        Returns:
            List of common heading texts
        """
        from collections import Counter

        all_headings = []

        for result in scraped_results:
            if result.get('success'):
                for heading in result.get('headings', []):
                    # Normalize heading text
                    text = heading['text'].lower()
                    all_headings.append(text)

        # Count occurrences
        heading_counts = Counter(all_headings)

        # Return headings that appear in at least 2 pages
        common = [
            text for text, count in heading_counts.most_common()
            if count >= 2
        ]

        return common[:20]  # Top 20