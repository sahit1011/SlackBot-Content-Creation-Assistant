import re
import logging
from typing import List, Dict
from collections import Counter

class KeywordCleaner:
    """Clean and normalize keywords"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def clean_keywords(self, keywords: List[str]) -> Dict:
        """
        Clean and deduplicate keywords

        Args:
            keywords: Raw keyword list

        Returns:
            Dict with cleaned keywords and statistics
        """
        self.logger.info(f" Starting keyword cleaning for {len(keywords)} raw keywords")
        original_count = len(keywords)

        # Step 1: Basic cleaning
        self.logger.debug(" Applying basic cleaning: lowercase, whitespace, special chars")
        cleaned = []
        for keyword in keywords:
            # Convert to string and lowercase
            kw = str(keyword).lower()

            # Remove extra whitespace
            kw = ' '.join(kw.split())

            # Remove special characters except hyphens and spaces
            kw = re.sub(r'[^a-z0-9\s-]', '', kw)

            # Trim
            kw = kw.strip()

            if kw:  # Not empty
                cleaned.append(kw)

        # Step 2: Remove duplicates (preserve order)
        self.logger.debug(" Removing duplicates while preserving order")
        seen = set()
        unique_keywords = []
        for kw in cleaned:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        # Step 3: Sort alphabetically
        unique_keywords.sort()

        result = {
            'original_count': original_count,
            'cleaned_count': len(unique_keywords),
            'removed_count': original_count - len(unique_keywords),
            'keywords': unique_keywords
        }

        self.logger.info(f" Keyword cleaning complete: {result['original_count']} → {result['cleaned_count']} unique keywords")
        return result
    
    @staticmethod
    def get_keyword_stats(keywords: List[str]) -> Dict:
        """Get statistics about keywords"""
        word_counts = [len(kw.split()) for kw in keywords]
        char_counts = [len(kw) for kw in keywords]
        
        return {
            'total_keywords': len(keywords),
            'avg_word_count': sum(word_counts) / len(word_counts) if word_counts else 0,
            'avg_char_count': sum(char_counts) / len(char_counts) if char_counts else 0,
            'shortest': min(keywords, key=len) if keywords else '',
            'longest': max(keywords, key=len) if keywords else ''
        }