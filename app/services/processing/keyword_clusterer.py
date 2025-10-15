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
                cluster_name = self._generate_cluster_name(cluster_keywords)
                cluster = {
                    'cluster_id': cluster_id,
                    'cluster_number': cluster_id + 1,
                    'cluster_name': cluster_name,
                    'keywords': sorted(cluster_keywords),
                    'keyword_count': len(cluster_keywords)
                }
                clusters.append(cluster)
                self.logger.info(f" Cluster {cluster_id + 1}: '{cluster_name}' ({len(cluster_keywords)} keywords)")

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
    
    def _generate_cluster_name(self, keywords: List[str]) -> str:
        """
        Generate descriptive name for cluster
        """
        # Extract most common words (excluding stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'for', 'with', 'to'}

        all_words = []
        for keyword in keywords:
            words = keyword.split()
            all_words.extend([w for w in words if w not in stop_words])

        # Get most common words
        word_counts = Counter(all_words)
        top_words = [word for word, count in word_counts.most_common(2)]

        if not top_words:
            return f"Group {keywords[0][:15]}..."

        # Capitalize first letter of each word and join with comma
        cluster_name = ', '.join(word.capitalize() for word in top_words)

        return cluster_name
    
    def _create_single_cluster(self, keywords: List[str], cluster_id: int) -> Dict:
        """Create a single cluster for all keywords"""
        return {
            'cluster_id': cluster_id,
            'cluster_number': cluster_id + 1,
            'cluster_name': self._generate_cluster_name(keywords),
            'keywords': sorted(keywords),
            'keyword_count': len(keywords)
        }