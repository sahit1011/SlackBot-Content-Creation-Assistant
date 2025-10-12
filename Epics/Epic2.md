## EPIC-002: Keyword Processing Engine
**Priority:** P0 (Critical Path)  
**Story Points:** 13  
**Duration:** 2 Days  
**Owner:** Developer  

### Tasks:

#### SLACK-006: Build Keyword Parser Module
**Type:** Feature  
**Priority:** High  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Create functions to parse keywords from CSV files and text input.

**Acceptance Criteria:**
- [ ] Parses CSV files correctly
- [ ] Handles text input (comma and newline separated)
- [ ] Returns list of raw keywords
- [ ] Handles encoding issues (UTF-8, Latin-1)
- [ ] Error handling for corrupt files

**Deliverables:**
- `app/services/keyword_parser.py`

**Dependencies:** SLACK-005

**Code Implementation:**
```python
# app/services/keyword_parser.py
import pandas as pd
from typing import List
import io

class KeywordParser:
    """Parse keywords from various input formats"""
    
    @staticmethod
    def parse_csv(file_path: str) -> List[str]:
        """
        Parse keywords from CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of raw keywords
        """
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            # Get first column or column named 'keyword'
            if 'keyword' in df.columns:
                keywords = df['keyword'].tolist()
            else:
                keywords = df.iloc[:, 0].tolist()
            
            # Remove NaN values
            keywords = [str(k) for k in keywords if pd.notna(k)]
            
            return keywords
            
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
    
    @staticmethod
    def parse_text(text: str) -> List[str]:
        """
        Parse keywords from plain text
        
        Args:
            text: Comma or newline separated keywords
            
        Returns:
            List of raw keywords
        """
        # Try comma separation first
        if ',' in text:
            keywords = text.split(',')
        else:
            # Try newline separation
            keywords = text.split('\n')
        
        # Clean up
        keywords = [k.strip() for k in keywords if k.strip()]
        
        return keywords
    
    @staticmethod
    def parse_csv_from_url(url: str, token: str) -> List[str]:
        """
        Parse CSV from Slack file URL
        
        Args:
            url: Slack file URL
            token: Slack bot token for authentication
            
        Returns:
            List of raw keywords
        """
        import requests
        
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse CSV from bytes
        csv_data = io.StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_data)
        
        if 'keyword' in df.columns:
            keywords = df['keyword'].tolist()
        else:
            keywords = df.iloc[:, 0].tolist()
        
        keywords = [str(k) for k in keywords if pd.notna(k)]
        
        return keywords
```

**Testing:**
```python
# Test with sample CSV
def test_parser():
    # Create test CSV
    with open('test.csv', 'w') as f:
        f.write('keyword\n')
        f.write('best running shoes\n')
        f.write('marathon training\n')
    
    parser = KeywordParser()
    keywords = parser.parse_csv('test.csv')
    assert len(keywords) == 2
    assert 'best running shoes' in keywords
    
    # Test text parsing
    text = "keyword1, keyword2, keyword3"
    keywords = parser.parse_text(text)
    assert len(keywords) == 3
```

---

#### SLACK-007: Build Keyword Cleaner Module
**Type:** Feature  
**Priority:** High  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Clean, normalize, and deduplicate keywords.

**Acceptance Criteria:**
- [ ] Converts to lowercase
- [ ] Removes special characters (except hyphens)
- [ ] Trims whitespace
- [ ] Removes duplicates (case-insensitive)
- [ ] Filters empty strings
- [ ] Returns cleaned list with statistics

**Deliverables:**
- `app/services/keyword_cleaner.py`

**Dependencies:** SLACK-006

**Code Implementation:**
```python
# app/services/keyword_cleaner.py
import re
from typing import List, Dict
from collections import Counter

class KeywordCleaner:
    """Clean and normalize keywords"""
    
    @staticmethod
    def clean_keywords(keywords: List[str]) -> Dict:
        """
        Clean and deduplicate keywords
        
        Args:
            keywords: Raw keyword list
            
        Returns:
            Dict with cleaned keywords and statistics
        """
        original_count = len(keywords)
        
        # Step 1: Basic cleaning
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
        seen = set()
        unique_keywords = []
        for kw in cleaned:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        # Step 3: Sort alphabetically
        unique_keywords.sort()
        
        return {
            'original_count': original_count,
            'cleaned_count': len(unique_keywords),
            'removed_count': original_count - len(unique_keywords),
            'keywords': unique_keywords
        }
    
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
```

**Testing:**
```python
def test_cleaner():
    cleaner = KeywordCleaner()
    
    raw = [
        'Best Running Shoes',
        'BEST RUNNING SHOES',  # duplicate
        'Best Running Shoes!',  # duplicate with special char
        '  trail running  ',    # extra whitespace
        'Yoga-Mats',
        '',                     # empty
        'SEO Tools'
    ]
    
    result = cleaner.clean_keywords(raw)
    
    assert result['original_count'] == 7
    assert result['cleaned_count'] == 4
    assert 'best running shoes' in result['keywords']
    assert 'yoga-mats' in result['keywords']
```

---

#### SLACK-008: Build Embedding Generator
**Type:** Feature  
**Priority:** High  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Generate vector embeddings for keywords using sentence-transformers.

**Acceptance Criteria:**
- [ ] Uses free sentence-transformers model
- [ ] Handles batch processing
- [ ] Returns numpy array of embeddings
- [ ] Caches results in Redis
- [ ] Error handling for model loading

**Deliverables:**
- `app/services/embedding_generator.py`

**Dependencies:** SLACK-007

**Code Implementation:**
```python
# app/services/embedding_generator.py
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
```

**Testing:**
```python
def test_embeddings():
    generator = EmbeddingGenerator()
    
    keywords = [
        'running shoes',
        'marathon training',
        'yoga mats',
        'meditation cushions'
    ]
    
    embeddings = generator.generate_embeddings(keywords)
    
    assert embeddings.shape[0] == 4
    assert embeddings.shape[1] == 384  # Model dimension
    
    # Test similarity
    from sklearn.metrics.pairwise import cosine_similarity
    sim_matrix = cosine_similarity(embeddings)
    
    # Running shoes and marathon training should be similar
    assert sim_matrix[0][1] > 0.5
```

---

#### SLACK-009: Build Clustering Engine
**Type:** Feature  
**Priority:** High  
**Story Points:** 4  
**Estimated Time:** 3 hours  

**Description:**
Cluster keywords into semantic groups using embeddings.

**Acceptance Criteria:**
- [ ] Determines optimal number of clusters (3-10)
- [ ] Uses KMeans clustering
- [ ] Generates descriptive cluster names
- [ ] Returns clusters with keywords
- [ ] Handles edge cases (too few keywords, outliers)

**Deliverables:**
- `app/services/keyword_clusterer.py`

**Dependencies:** SLACK-008

**Code Implementation:**
```python
# app/services/keyword_clusterer.py
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
from typing import List, Dict
from collections import Counter

class KeywordClusterer:
    """Cluster keywords by semantic similarity"""
    
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
        n_keywords = len(keywords)
        
        # Handle edge cases
        if n_keywords < 3:
            return [self._create_single_cluster(keywords, 0)]
        
        # Determine optimal clusters
        optimal_k = self._find_optimal_clusters(
            embeddings, 
            min_k=min(min_clusters, n_keywords),
            max_k=min(max_clusters, n_keywords)
        )
        
        # Perform clustering
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
                    'cluster_name': self._generate_cluster_name(cluster_keywords),
                    'keywords': sorted(cluster_keywords),
                    'keyword_count': len(cluster_keywords)
                }
                clusters.append(cluster)
        
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
        top_words = [word for word, count in word_counts.most_common(3)]
        
        if not top_words:
            return f"Group {keywords[0][:15]}..."
        
        # Capitalize first letter of each word
        cluster_name = ' '.join(word.capitalize() for word in top_words)
        
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
```

**Testing:**
```python
def test_clustering():
    clusterer = KeywordClusterer()
    
    keywords = [
        'running shoes', 'marathon shoes', 'trail running shoes',
        'yoga mat', 'meditation cushion', 'yoga blocks',
        'protein powder', 'whey protein', 'vegan protein'
    ]
    
    # Generate dummy embeddings (in real use, get from embedding generator)
    embeddings = np.random.rand(9, 384)
    
    clusters = clusterer.cluster_keywords(keywords, embeddings)
    
    assert len(clusters) >= 2
    assert len(clusters) <= 5
    
    # Check all keywords are assigned
    all_clustered = []
    for cluster in clusters:
        all_clustered.extend(cluster['keywords'])
    
    assert set(all_clustered) == set(keywords)
```

---