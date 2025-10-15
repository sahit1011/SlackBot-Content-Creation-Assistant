# app/services/outline_generator.py
from typing import List, Dict
from groq import Groq
from app.config import Config
import logging

class OutlineGenerator:
    """Generate content outlines based on research"""

    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
        self.logger = logging.getLogger(__name__)

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
        cluster_name = cluster['cluster_name']

        self.logger.info(f" Generating outline for cluster '{cluster_name}'")

        # Extract common topics
        self.logger.debug(" Extracting common topics from scraped content")
        common_topics = self._extract_topics(scraped_data)
        self.logger.debug(f" Found {len(common_topics)} common topics: {common_topics[:3]}{'...' if len(common_topics) > 3 else ''}")

        # Only use LLM-based generation - no fallbacks
        try:
            self.logger.info(" Calling Groq API for outline generation")
            outline = self._generate_with_llm(keywords, common_topics)
            self.logger.info(f" Outline generated: '{outline.get('title', 'N/A')}' with {len(outline.get('sections', []))} sections")
        except Exception as e:
            error_msg = f"LLM Outline Generation Failed: {str(e)}"
            self.logger.error(error_msg)
            print(error_msg)
            raise Exception(error_msg)  # Re-raise to stop pipeline

        return outline

    def _extract_topics(self, scraped_data: List[Dict]) -> List[str]:
        """Extract common topics from scraped content"""
        from collections import Counter

        all_headings = []

        for result in scraped_data:
            if result.get('success'):
                for heading in result.get('headings', []):
                    if heading['level'] in ['h2', 'h3']:
                        # Clean and normalize heading text
                        text = heading['text'].strip().lower()
                        # Skip very short or generic headings
                        if len(text) > 3 and not any(word in text for word in ['buy', 'price', 'review', 'best', 'top']):
                            all_headings.append(text)

        # Get most common headings (at least 2 occurrences)
        heading_counts = Counter(all_headings)
        common = [text for text, count in heading_counts.most_common(10) if count >= 2]

        # If no common topics found, use any headings
        if not common:
            common = [text for text, count in heading_counts.most_common(5)]

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
            model="llama-3.1-8b-instant",
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
            # Capitalize first letter of each word for better headings
            heading = ' '.join(word.capitalize() for word in topic.split())
            sections.append({
                "heading": heading,
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