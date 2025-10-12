## EPIC-003: Content Research System
**Priority:** P0 (Critical Path)  
**Story Points:** 15  
**Duration:** 2 Days  
**Owner:** Developer  

### Tasks:

#### SLACK-010: Build Web Search Service
**Type:** Feature  
**Priority:** High  
**Story Points:** 4  
**Estimated Time:** 3 hours  

**Description:**
Integrate web search API to find top-ranking content for keywords.

**Acceptance Criteria:**
- [ ] Uses Brave Search API
- [ ] Returns top 5-10 results per query
- [ ] Handles rate limiting
- [ ] Implements retry logic
- [ ] Returns clean result structure

**Deliverables:**
- `app/services/web_search.py`

**Dependencies:** SLACK-005

**Code Implementation:**
```python
# app/services/web_search.py
import requests
import time
from typing import List, Dict
from app.config import Config

class WebSearchService:
    """Search the web for top-ranking content"""
    
    def __init__(self):
        self.api_key = Config.BRAVE_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
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
        # Rate limiting
        self._wait_for_rate_limit()
        
        params = {
            'q': query,
            'count': count,
            'search_lang': 'en'
        }
        
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': self.api_key
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
        
        web_results = data.get('web', {}).get('results', [])
        
        for result in web_results:
            results.append({
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'description': result.get('description', ''),
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
```

**Testing:**
```python
def test_web_search():
    search = WebSearchService()
    
    results = search.search_single('best running shoes', count=5)
    
    assert len(results) <= 5
    assert all('url' in r for r in results)
    assert all('title' in r for r in results)
```

---

#### SLACK-011: Build Content Scraper
**Type:** Feature  
**Priority:** High  
**Story Points:** 4  
**Estimated Time:** 3 hours  

**Description:**
Scrape web pages to extract headings and structure.

**Acceptance Criteria:**
- [ ] Extracts H1, H2, H3 tags
- [ ] Handles failed requests gracefully
- [ ] Respects timeout limits
- [ ] Returns structured heading data
- [ ] Cleans extracted text

**Deliverables:**
- `app/services/content_scraper.py`

**Dependencies:** SLACK-010

**Code Implementation:**
```python
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
```

**Testing:**
```python
def test_scraper():
    scraper = ContentScraper()
    
    # Test with a real URL
    result = scraper.scrape_single('https://example.com')
    
    assert 'url' in result
    assert 'success' in result
    
    if result['success']:
        assert 'headings' in result
        assert 'title' in result
```

---

#### SLACK-012: Build Outline Generator
**Type:** Feature  
**Priority:** High  
**Story Points:** 4  
**Estimated Time:** 3 hours  

**Description:**
Generate structured content outlines based on scraped content.

**Acceptance Criteria:**
- [ ] Creates intro, body sections, conclusion
- [ ] Based on common topics from top content
- [ ] Well-structured with subsections
- [ ] Uses LLM for intelligent structuring
- [ ] Fallback to rule-based if LLM fails

**Deliverables:**
- `app/services/outline_generator.py`

**Dependencies:** SLACK-011

**Code Implementation:**
```python
# app/services/outline_generator.py
from typing import List, Dict
from groq import Groq
from app.config import Config

class OutlineGenerator:
    """Generate content outlines based on research"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
    
    def generate_outline(
        self, 
        cluster: Dict,
        scraped_data: List[Dict]
    ) -> Dict:
        """
        Generate content outline for a keyword cluster
        
        Args:
            cluster: Keyword cluster dictionary
            scraped_data: List of scraped content from top results
            
        Returns:
            Structured outline dictionary
        """
        keywords = cluster['keywords']
        
        # Extract common topics
        common_topics = self._extract_topics(scraped_data)
        
        # Try LLM-based generation
        try:
            outline = self._generate_with_llm(keywords, common_topics)
        except Exception as e:
            print(f"LLM generation failed: {str(e)}")
            # Fallback to rule-based
            outline = self._generate_rule_based(keywords, common_topics)
        
        return outline
    
    def _extract_topics(self, scraped_data: List[Dict]) -> List[str]:
        """Extract common topics from scraped content"""
        from collections import Counter
        
        all_headings = []
        
        for result in scraped_data:
            if result.get('success'):
                for heading in result.get('headings', []):
                    if heading['level'] in ['h2', 'h3']:
                        all_headings.append(heading['text'])
        
        # Get most common headings
        heading_counts = Counter(all_headings)
        common = [text for text, count in heading_counts.most_common(10)]
        
        return common
    
    def _generate_with_llm(
        self, 
        keywords: List[str], 
        topics: List[str]
    ) -> Dict:
        """Generate outline using Groq LLM"""
        
        prompt = f"""Create a comprehensive content outline for a blog post.

Target Keywords: {', '.join(keywords[:5])}
Common Topics in Top-Ranking Content: {', '.join(topics[:10])}

Generate a structured outline with:
1. An engaging introduction section
2. 5-7 main body sections (H2 level)
3. 2-3 subsections under each main section (H3 level)
4. A conclusion section

Format as JSON:
{{
  "title": "Suggested title",
  "introduction": {{
    "hook": "Opening hook",
    "overview": "What this post covers"
  }},
  "sections": [
    {{
      "heading": "Main section heading",
      "description": "What this section covers",
      "subsections": ["Subsection 1", "Subsection 2"]
    }}
  ],
  "conclusion": {{
    "summary": "Key takeaways",
    "cta": "Call to action"
  }}
}}

Respond ONLY with valid JSON, no additional text."""

        response = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a content strategy expert. Generate well-structured content outlines in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse JSON response
        import json
        outline_text = response.choices[0].message.content
        
        # Extract JSON if wrapped in markdown
        if '```json' in outline_text:
            outline_text = outline_text.split('```json')[1].split('```')[0]
        elif '```' in outline_text:
            outline_text = outline_text.split('```')[1].split('```')[0]
        
        outline = json.loads(outline_text.strip())
        
        return outline
    
    def _generate_rule_based(
        self, 
        keywords: List[str], 
        topics: List[str]
    ) -> Dict:
        """Fallback rule-based outline generation"""
        
        main_keyword = keywords[0] if keywords else "Topic"
        
        # Create basic sections from topics
        sections = []
        for i, topic in enumerate(topics[:6], 1):
            sections.append({
                "heading": topic,
                "description": f"Detailed information about {topic.lower()}",
                "subsections": [
                    f"Key aspects of {topic.lower()}",
                    f"Best practices for {topic.lower()}"
                ]
            })
        
        # If no topics, create generic sections
        if not sections:
            sections = [
                {
                    "heading": f"Understanding {main_keyword}",
                    "description": "Comprehensive overview",
                    "subsections": ["Key concepts", "Important considerations"]
                },
                {
                    "heading": f"Best {main_keyword} Options",
                    "description": "Top recommendations",
                    "subsections": ["Top picks", "Comparison"]
                },
                {
                    "heading": f"How to Choose {main_keyword}",
                    "description": "Selection guide",
                    "subsections": ["Factors to consider", "Decision framework"]
                }
            ]
        
        return {
            "title": f"Complete Guide to {main_keyword.title()}",
            "introduction": {
                "hook": f"Everything you need to know about {main_keyword}",
                "overview": f"This guide covers all aspects of {main_keyword}"
            },
            "sections": sections,
            "conclusion": {
                "summary": "Key points to remember",
                "cta": "Take action on what you've learned"
            }
        }
```

**Testing:**
```python
def test_outline_generator():
    generator = OutlineGenerator()
    
    cluster = {
        'keywords': ['running shoes', 'best running shoes'],
        'cluster_name': 'Running Shoes'
    }
    
    scraped_data = [
        {
            'success': True,
            'headings': [
                {'level': 'h2', 'text': 'Types of Running Shoes'},
                {'level': 'h2', 'text': 'How to Choose'}
            ]
        }
    ]
    
    outline = generator.generate_outline(cluster, scraped_data)
    
    assert 'title' in outline
    assert 'sections' in outline
    assert len(outline['sections']) > 0
```

---

#### SLACK-013: Build Post Idea Generator
**Type:** Feature  
**Priority:** High  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Generate creative post ideas using LLM.

**Acceptance Criteria:**
- [ ] One unique post idea per cluster
- [ ] Includes title, angle, target audience
- [ ] Creative and actionable
- [ ] Considers keyword intent
- [ ] Fallback to rule-based generation

**Deliverables:**
- `app/services/idea_generator.py`

**Dependencies:** SLACK-011

**Code Implementation:**
```python
# app/services/idea_generator.py
from typing import Dict, List
from groq import Groq
from app.config import Config

class IdeaGenerator:
    """Generate creative post ideas"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
    
    def generate_idea(
        self,
        cluster: Dict,
        outline: Dict = None
    ) -> Dict:
        """
        Generate a post idea for keyword cluster
        
        Args:
            cluster: Keyword cluster
            outline: Optional generated outline
            
        Returns:
            Post idea dictionary
        """
        keywords = cluster['keywords']
        
        try:
            idea = self._generate_with_llm(keywords, outline)
        except Exception as e:
            print(f"LLM idea generation failed: {str(e)}")
            idea = self._generate_rule_based(keywords)
        
        return idea
    
    def _generate_with_llm(
        self,
        keywords: List[str],
        outline: Dict = None
    ) -> Dict:
        """Generate idea using Groq LLM"""
        
        outline_context = ""
        if outline:
            sections = [s.get('heading', '') for s in outline.get('sections', [])]
            outline_context = f"\n\nOutline sections: {', '.join(sections)}"
        
        prompt = f"""Generate ONE unique and compelling blog post idea.

Keywords: {', '.join(keywords[:5])}{outline_context}

Requirements:
- Create a catchy, click-worthy title
- Propose a unique angle that stands out from typical content
- Define the target audience clearly
- Make it actionable and valuable

Format as JSON:
{{
  "title": "Catchy post title",
  "angle": "Unique perspective or approach",
  "target_audience": "Who this is for",
  "value_proposition": "What readers will gain"
}}

Respond ONLY with valid JSON."""

        response = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative content strategist. Generate unique, engaging post ideas."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",
            temperature=0.8,
            max_tokens=500
        )
        
        import json
        idea_text = response.choices[0].message.content
        
        # Extract JSON
        if '```json' in idea_text:
            idea_text = idea_text.split('```json')[1].split('```')[0]
        elif '```' in idea_text:
            idea_text = idea_text.split('```')[1].split('```')[0]
        
        idea = json.loads(idea_text.strip())
        
        return idea
    
    def _generate_rule_based(self, keywords: List[str]) -> Dict:
        """Fallback rule-based idea generation"""
        
        main_keyword = keywords[0] if keywords else "Topic"
        
        # Simple templates
        templates = [
            {
                "title": f"The Ultimate {main_keyword.title()} Guide for 2025",
                "angle": "Comprehensive guide covering all aspects",
                "target_audience": "Beginners and intermediate users",
                "value_proposition": "Complete knowledge from basics to advanced"
            },
            {
                "title": f"{main_keyword.title()}: What Experts Won't Tell You",
                "angle": "Insider knowledge and lesser-known tips",
                "target_audience": "People looking for expert insights",
                "value_proposition": "Learn what most guides miss"
            },
            {
                "title": f"How to Choose the Best {main_keyword.title()}",
                "angle": "Decision-making framework",
                "target_audience": "People making a purchase decision",
                "value_proposition": "Make confident, informed choices"
            }
        ]
        
        # Pick first template
        return templates[0]
```

**Testing:**
```python
def test_idea_generator():
    generator = IdeaGenerator()
    
    cluster = {
        'keywords': ['running shoes', 'best running shoes'],
        'cluster_name': 'Running Shoes'
    }
    
    idea = generator.generate_idea(cluster)
    
    assert 'title' in idea
    assert 'angle' in idea
    assert 'target_audience' in idea
```

---
