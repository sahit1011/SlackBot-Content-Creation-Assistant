from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import logging
from typing import List, Dict
from collections import Counter

class KeywordClusterer:
    """Cluster keywords by semantic similarity"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def cluster_keywords(
        self, 
        keywords: List[str], 
        embeddings: np.ndarray,
        min_clusters: int = 3,
        max_clusters: int = 10
    ) -> List[Dict]:
        """
        Cluster keywords into semantic groups

        Args:
            keywords: List of cleaned keywords
            embeddings: Keyword embeddings
            min_clusters: Minimum number of clusters
            max_clusters: Maximum number of clusters

        Returns:
            List of cluster dictionaries
        """
        self.logger.info(f" Starting keyword clustering for {len(keywords)} keywords")
        n_keywords = len(keywords)

        # Handle edge cases
        if n_keywords < 3:
            self.logger.info(" Few keywords detected, creating single cluster")
            return [self._create_single_cluster(keywords, 0)]

        # Determine optimal clusters
        self.logger.debug(" Finding optimal number of clusters using silhouette score")
        optimal_k = self._find_optimal_clusters(
            embeddings,
            min_k=min(min_clusters, n_keywords),
            max_k=min(max_clusters, n_keywords)
        )
        self.logger.info(f" Optimal cluster count: {optimal_k}")

        # Perform clustering
        self.logger.debug(f" Running K-means clustering with k={optimal_k}")
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)

        # Group keywords by cluster
        clusters = []
        for cluster_id in range(optimal_k):
            cluster_keywords = [
                keywords[i] for i, label in enumerate(labels)
                if label == cluster_id
            ]

            if cluster_keywords:
                cluster = {
                    'cluster_id': cluster_id,
                    'cluster_number': cluster_id + 1,
                    'cluster_name': f"Cluster {cluster_id + 1}",  # Temporary name
                    'keywords': sorted(cluster_keywords),
                    'keyword_count': len(cluster_keywords)
                }
                clusters.append(cluster)
                self.logger.info(f" Cluster {cluster_id + 1}: ({len(cluster_keywords)} keywords)")

        # Generate names for all clusters in one batch call
        if clusters:
            cluster_names = self._generate_cluster_names_batch(clusters)
            for i, cluster in enumerate(clusters):
                if i < len(cluster_names):
                    cluster['cluster_name'] = cluster_names[i]
                self.logger.info(f" Cluster {cluster['cluster_number']}: '{cluster['cluster_name']}' ({cluster['keyword_count']} keywords)")

        self.logger.info(f" Clustering complete: {len(clusters)} clusters created")
        return clusters
    
    def _find_optimal_clusters(
        self, 
        embeddings: np.ndarray, 
        min_k: int = 3, 
        max_k: int = 10
    ) -> int:
        """
        Find optimal number of clusters using silhouette score
        """
        if len(embeddings) <= min_k:
            return max(2, len(embeddings) - 1)
        
        scores = []
        k_range = range(min_k, min(max_k + 1, len(embeddings)))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)
            scores.append((k, score))
        
        # Return k with best silhouette score
        optimal_k = max(scores, key=lambda x: x[1])[0]
        return optimal_k
    
    def _generate_cluster_names_batch(self, clusters: List[Dict]) -> List[str]:
        """
        Generate names for all clusters in one batch LLM call
        """
        try:
            # Use Groq directly to avoid circular imports
            from groq import Groq
            from app.config import Config

            groq_client = Groq(api_key=Config.GROQ_API_KEY)

            # Build the prompt with all cluster information
            cluster_info = []
            for i, cluster in enumerate(clusters, 1):
                keywords_str = ', '.join(cluster['keywords'][:8])  # Limit keywords per cluster
                if len(cluster['keywords']) > 8:
                    keywords_str += f"... (+{len(cluster['keywords']) - 8} more)"
                cluster_info.append(f"Cluster {i}: {keywords_str}")

            prompt = f"""Here are {len(clusters)} keyword clusters from a semantic analysis:

{chr(10).join(cluster_info)}

Generate unique, descriptive names for each cluster (2-4 words each). Each name should capture the main theme of that specific cluster and be different from the others.

Return your response as a JSON array of strings, like this:
["Cluster Name 1", "Cluster Name 2", "Cluster Name 3", ...]

Make sure each name is specific and reflects the unique aspect of that cluster."""

            # Use the LLM to generate cluster names
            response = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a content strategist. Generate unique, descriptive names for keyword clusters based on their semantic groupings."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.3,
                max_tokens=200  # Enough for array of names
            )

            import json
            response_text = response.choices[0].message.content.strip()

            # Try to parse as JSON array
            try:
                cluster_names = json.loads(response_text)
                if isinstance(cluster_names, list) and len(cluster_names) == len(clusters):
                    return cluster_names
            except json.JSONDecodeError:
                # Try to extract array from text if JSON parsing fails
                import re
                array_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if array_match:
                    try:
                        cluster_names = json.loads(array_match.group())
                        if isinstance(cluster_names, list) and len(cluster_names) == len(clusters):
                            return cluster_names
                    except:
                        pass

            # If parsing fails, generate fallback names
            self.logger.warning("Failed to parse LLM response for cluster names, using fallbacks")
            return self._generate_fallback_cluster_names(clusters)

        except Exception as e:
            self.logger.warning(f"Failed to generate batch cluster names: {e}")
            return self._generate_fallback_cluster_names(clusters)

    def _generate_fallback_cluster_names(self, clusters: List[Dict]) -> List[str]:
        """Generate fallback cluster names using word frequency analysis"""
        names = []
        for cluster in clusters:
            keywords = cluster['keywords']
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'for', 'with', 'to'}

            all_words = []
            for keyword in keywords:
                words = keyword.split()
                all_words.extend([w for w in words if w not in stop_words])

            # Get most common words
            word_counts = Counter(all_words)
            top_words = [word for word, count in word_counts.most_common(2)]

            if not top_words:
                cluster_name = f"Keyword Group {keywords[0][:15]}..."
            else:
                cluster_name = ' '.join(word.capitalize() for word in top_words)

            names.append(cluster_name)

        return names
    
    def _create_single_cluster(self, keywords: List[str], cluster_id: int) -> Dict:
        """Create a single cluster for all keywords"""
        return {
            'cluster_id': cluster_id,
            'cluster_number': cluster_id + 1,
            'cluster_name': self._generate_cluster_name(keywords),
            'keywords': sorted(keywords),
            'keyword_count': len(keywords)
        }