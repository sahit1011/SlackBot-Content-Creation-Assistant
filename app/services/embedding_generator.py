from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import hashlib
import json
import redis
from app.config import Config

class EmbeddingGenerator:
    """Generate embeddings for keywords"""
    
    def __init__(self):
        self.model = None
        self.redis_client = None
        
        try:
            if Config.REDIS_URL:
                self.redis_client = redis.from_url(Config.REDIS_URL)
        except:
            pass
    
    def load_model(self):
        """Load sentence transformer model"""
        if self.model is None:
            # Use lightweight model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def generate_embeddings(self, keywords: List[str]) -> np.ndarray:
        """
        Generate embeddings for keywords
        
        Args:
            keywords: List of cleaned keywords
            
        Returns:
            Numpy array of shape (n_keywords, embedding_dim)
        """
        # Check cache first
        cache_key = self._get_cache_key(keywords)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Load model
        self.load_model()
        
        # Generate embeddings
        embeddings = self.model.encode(keywords, show_progress_bar=True)
        
        # Cache results
        self._save_to_cache(cache_key, embeddings)
        
        return embeddings
    
    def _get_cache_key(self, keywords: List[str]) -> str:
        """Generate cache key from keywords"""
        content = json.dumps(sorted(keywords))
        return f"embeddings:{hashlib.md5(content.encode()).hexdigest()}"
    
    def _get_from_cache(self, key: str):
        """Get embeddings from Redis cache"""
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                return np.frombuffer(cached, dtype=np.float32).reshape(-1, 384)
        except:
            return None
    
    def _save_to_cache(self, key: str, embeddings: np.ndarray):
        """Save embeddings to Redis cache (24 hour TTL)"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                key,
                86400,  # 24 hours
                embeddings.astype(np.float32).tobytes()
            )
        except:
            pass