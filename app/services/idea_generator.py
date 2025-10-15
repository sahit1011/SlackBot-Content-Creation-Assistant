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

        try:
            idea = self._generate_with_llm(keywords, outline)
        except Exception as e:
            error_msg = f"LLM Idea Generation Failed: {str(e)}"
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

        self.logger.info(f"Sending request to Groq API with keywords: {keywords}")
        self.logger.debug(f"Full prompt: {prompt}")

        try:
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
                model="llama-3.1-8b-instant",
                temperature=0.8,
                max_tokens=500
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