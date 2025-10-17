# app/services/idea_generator.py
import logging
from typing import Dict, List
from groq import Groq
from app.config import Config

class IdeaGenerator:
    """Generate creative post ideas"""

    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
        self.logger = logging.getLogger(__name__)

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
        cluster_name = cluster['cluster_name']

        self.logger.info(f" Generating post idea for cluster '{cluster_name}'")

        try:
            self.logger.info(" Calling Groq API for idea generation")
            idea = self._generate_with_llm(keywords, outline)
            self.logger.info(f" Post idea generated: '{idea.get('title', 'N/A')}'")
        except Exception as e:
            error_msg = f"LLM Idea Generation Failed: {str(e)}"
            self.logger.error(error_msg)
            print(error_msg)
            raise Exception(error_msg)  # Re-raise to stop pipeline

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

        prompt = f"""Generate ONE unique, compelling, and user-friendly blog post idea that drives engagement and conversions.

Keywords: {', '.join(keywords[:5])}{outline_context}

Requirements:
- Create a catchy, click-worthy title that sparks curiosity
- Propose a unique angle that stands out from typical content
- Define the target audience clearly with demographics and pain points
- Make it actionable and valuable with specific benefits
- Include content format suggestions (listicle, how-to, case study, etc.)
- Add estimated reading time and difficulty level
- Suggest social media hooks and sharing angles
- Include monetization potential (affiliate, lead gen, etc.)

Format as JSON:
{{
  "title": "Catchy post title",
  "angle": "Unique perspective or approach",
  "target_audience": "Who this is for (demographics, pain points, interests)",
  "value_proposition": "What readers will gain (specific benefits)",
  "content_format": "Suggested format (how-to guide, listicle, case study, etc.)",
  "estimated_reading_time": "5-7 minutes",
  "difficulty_level": "Beginner/Intermediate/Advanced",
  "social_hooks": ["Hook 1", "Hook 2", "Hook 3"],
  "monetization_potential": "Affiliate products, lead generation, etc.",
  "seo_optimization": {{
    "primary_keyword": "main keyword",
    "search_intent": "informational/commercial/transactional",
    "competitor_analysis": "What makes this different"
  }}
}}

Respond ONLY with valid JSON."""

        self.logger.info(f"Sending request to Groq API with keywords: {keywords}")
        self.logger.debug(f"Full prompt: {prompt}")

        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior content marketing strategist with expertise in viral content creation, SEO, and audience psychology. Generate highly engaging, conversion-focused post ideas that combine creativity with strategic marketing principles."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.8,
                max_tokens=1000
            )

            self.logger.info("Received response from Groq API")
            self.logger.debug(f"Raw response: {response}")

            import json
            idea_text = response.choices[0].message.content

            self.logger.debug(f"Response content: {idea_text}")

            # Extract JSON
            if '```json' in idea_text:
                idea_text = idea_text.split('```json')[1].split('```')[0]
            elif '```' in idea_text:
                idea_text = idea_text.split('```')[1].split('```')[0]

            idea = json.loads(idea_text.strip())

            self.logger.info(f"Successfully parsed idea: {idea}")

            return idea

        except Exception as e:
            self.logger.error(f"Failed to generate idea with Groq API: {str(e)}")
            raise e