# JIRA Development Roadmap
## Slackbot Content Creation Assistant

**Project Code:** SLACK-BOT  
**Sprint Duration:** 10 Days  
**Team Size:** 1 Developer  
**Velocity Target:** Complete MVP + Bonus Features  

---

## 🎯 SPRINT OVERVIEW

| Sprint | Duration | Focus | Deliverables |
|--------|----------|-------|--------------|
| **Sprint 0** | Day 1 | Setup & Infrastructure | All accounts, environment ready |
| **Sprint 1** | Days 2-3 | Core Processing | Keyword processing & clustering |
| **Sprint 2** | Days 4-5 | Content Intelligence | Research, outlines, post ideas |
| **Sprint 3** | Day 6 | Slack Integration | Commands, events, formatting |
| **Sprint 4** | Day 7 | Deployment | Docker, Render, production |
| **Sprint 5** | Day 8 | Bonus Features | History, regenerate, email |
| **Sprint 6** | Days 9-10 | Testing & Documentation | QA, docs, polish |

---

# 📋 EPIC BREAKDOWN

## EPIC-001: Project Setup & Infrastructure
**Priority:** P0 (Blocker)  
**Story Points:** 8  
**Duration:** 1 Day  
**Owner:** Developer  

### Tasks:

#### SLACK-001: Create All Service Accounts ⭐ START HERE
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 2  
**Estimated Time:** 1 hour  

**Description:**
Set up all required external service accounts and obtain API credentials.

**Acceptance Criteria:**
- [ ] Slack workspace created
- [ ] Slack app created at api.slack.com/apps
- [ ] Bot token and signing secret obtained
- [ ] Supabase project created
- [ ] Upstash Redis database created
- [ ] Brave Search API key obtained (or SerpAPI)
- [ ] Groq API key obtained
- [ ] SendGrid account created and sender verified

**Deliverables:**
- Document with all credentials (store securely)
- Screenshot of each service dashboard

**Dependencies:** None

**Subtasks:**
- [ ] Create Slack app with Bot Token Scopes: `chat:write`, `files:write`, `files:read`, `commands`
- [ ] Enable Socket Mode or Events API
- [ ] Create slash commands: `/process_keywords`, `/history`, `/regenerate`
- [ ] Create Supabase project and get URL + anon key
- [ ] Create Upstash Redis database and get REST URL
- [ ] Sign up for Brave Search API (2000 free queries/month)
- [ ] Create Groq account and get API key
- [ ] Create SendGrid account, verify sender email

**Testing:**
- Verify each API key works with a test request

---

#### SLACK-002: Initialize Project Structure
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 2  
**Estimated Time:** 30 minutes  

**Description:**
Create the project directory structure and initialize version control.

**Acceptance Criteria:**
- [ ] Git repository initialized
- [ ] Project structure created
- [ ] Virtual environment set up
- [ ] .gitignore configured

**Deliverables:**
- Working project structure
- Initial Git commit

**Dependencies:** None

**Implementation Steps:**
```bash
# Create project
mkdir slackbot-content-assistant
cd slackbot-content-assistant
git init

# Create structure
mkdir -p app/{handlers,services,utils,models}
touch app/__init__.py
touch app/main.py
touch app/config.py
touch requirements.txt
touch Dockerfile
touch .env
touch .env.example
touch README.md
touch .gitignore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Create .gitignore
echo "venv/
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.log
*.pdf
.DS_Store" > .gitignore
```

**Testing:**
- Verify directory structure is correct
- Ensure virtual environment activates

---

#### SLACK-003: Configure Environment Variables
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 1  
**Estimated Time:** 20 minutes  

**Description:**
Create configuration management for all API keys and settings.

**Acceptance Criteria:**
- [ ] .env.example file created with all variables
- [ ] config.py loads environment variables
- [ ] Sensitive data not committed to Git

**Deliverables:**
- `app/config.py` with Config class
- `.env.example` template

**Dependencies:** SLACK-001, SLACK-002

**Code Template:**
```python
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Slack
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
    
    # Database
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL')
    
    # APIs
    BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')
    
    # Application
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_KEYWORDS = int(os.getenv('MAX_KEYWORDS', '1000'))
```

**Testing:**
- Import config and verify variables load
- Test with missing .env file (should not crash)

---

#### SLACK-004: Set Up Database Schema
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 2  
**Estimated Time:** 45 minutes  

**Description:**
Create all database tables in Supabase.

**Acceptance Criteria:**
- [ ] All 4 tables created (users, keyword_batches, keyword_clusters, reports)
- [ ] Indexes created
- [ ] Foreign key relationships established
- [ ] Test data inserted successfully

**Deliverables:**
- SQL migration file
- Database connection test script

**Dependencies:** SLACK-001, SLACK-003

**SQL Script:**
```sql
-- Create users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  slack_user_id VARCHAR(50) UNIQUE NOT NULL,
  slack_team_id VARCHAR(50),
  email VARCHAR(255),
  display_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  last_active_at TIMESTAMP DEFAULT NOW()
);

-- Create keyword_batches table
CREATE TABLE keyword_batches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  batch_name VARCHAR(255),
  status VARCHAR(50) NOT NULL,
  raw_keywords TEXT[],
  cleaned_keywords TEXT[],
  keyword_count INT,
  cluster_count INT,
  source_type VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  error_message TEXT
);

CREATE INDEX idx_batches_user ON keyword_batches(user_id);
CREATE INDEX idx_batches_status ON keyword_batches(status);

-- Create keyword_clusters table
CREATE TABLE keyword_clusters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  batch_id UUID REFERENCES keyword_batches(id) ON DELETE CASCADE,
  cluster_number INT NOT NULL,
  cluster_name VARCHAR(255) NOT NULL,
  keywords TEXT[] NOT NULL,
  keyword_count INT,
  post_idea TEXT,
  post_idea_metadata JSONB,
  outline_json JSONB,
  top_urls TEXT[],
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_clusters_batch ON keyword_clusters(batch_id);

-- Create reports table
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  batch_id UUID REFERENCES keyword_batches(id) ON DELETE CASCADE,
  pdf_filename VARCHAR(255),
  pdf_url TEXT,
  file_size_kb INT,
  sent_via_email BOOLEAN DEFAULT FALSE,
  email_sent_to VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reports_batch ON reports(batch_id);
```

**Testing:**
- Run SQL in Supabase SQL editor
- Test insert/select on each table
- Verify foreign keys work

---

#### SLACK-005: Install Dependencies
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 1  
**Estimated Time:** 15 minutes  

**Description:**
Install all required Python packages.

**Acceptance Criteria:**
- [ ] requirements.txt created with all dependencies
- [ ] All packages install without errors
- [ ] Version conflicts resolved

**Deliverables:**
- Complete requirements.txt file

**Dependencies:** SLACK-002

**Requirements File:**
```txt
# requirements.txt
slack-bolt==1.18.0
slack-sdk==3.23.0
python-dotenv==1.0.0

# Database & Cache
supabase==2.0.3
redis==5.0.1

# ML & Data Processing
sentence-transformers==2.2.2
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.0

# Web Scraping & Search
requests==2.31.0
beautifulsoup4==4.12.2

# LLM
groq==0.4.1

# PDF Generation
reportlab==4.0.7

# Email
sendgrid==6.11.0

# Utilities
python-slugify==8.0.1
```

**Installation:**
```bash
pip install -r requirements.txt
```

**Testing:**
- Import each major library in Python REPL
- No import errors

---

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

## EPIC-004: Slack Bot Integration
**Priority:** P0 (Critical Path)  
**Story Points:** 13  
**Duration:** 1 Day  
**Owner:** Developer  

### Tasks:

#### SLACK-014: Build Slack Bot Framework
**Type:** Feature  
**Priority:** Critical  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Set up basic Slack bot with Bolt framework.

**Acceptance Criteria:**
- [ ] Slack bot connects successfully
- [ ] Responds to simple commands
- [ ] Event handlers work
- [ ] Logging configured

**Deliverables:**
- `app/main.py`
- `app/handlers/__init__.py`

**Dependencies:** SLACK-003, SLACK-005

**Code Implementation:**
```python
# app/main.py
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from app.config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)

# Import handlers
from app.handlers import command_handlers, event_handlers

# Register handlers
command_handlers.register(app)
event_handlers.register(app)

# Health check
@app.event("app_mention")
def handle_app_mention(event, say):
    say(f"👋 Hi <@{event['user']}>! I'm ready to help with keyword processing.")

def main():
    """Start the Slack bot"""
    logger.info("Starting Slackbot Content Assistant...")
    
    # Start socket mode handler
    handler = SocketModeHandler(app, Config.SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    main()
```

**Testing:**
- Mention bot in Slack channel
- Should respond with greeting

---

#### SLACK-015: Implement /process_keywords Command
**Type:** Feature  
**Priority:** Critical  
**Story Points:** 4  
**Estimated Time:** 3 hours  

**Description:**
Implement main command to initiate keyword processing.

**Acceptance Criteria:**
- [ ] Command responds immediately
- [ ] Sets user state in Redis
- [ ] Provides clear instructions
- [ ] Handles concurrent users

**Deliverables:**
- `app/handlers/command_handlers.py`

**Dependencies:** SLACK-014

**Code Implementation:**
```python
# app/handlers/command_handlers.py
import redis
import json
from app.config import Config
from app.services.pipeline import ProcessingPipeline

# Redis client
redis_client = redis.from_url(Config.REDIS_URL) if Config.REDIS_URL else None

def register(app):
    """Register all command handlers"""
    
    @app.command("/process_keywords")
    def handle_process_keywords(ack, command, client):
        """Handle /process_keywords command"""
        ack()  # Acknowledge command immediately
        
        user_id = command['user_id']
        channel_id = command['channel_id']
        text = command.get('text', '').strip()
        
        # Send initial response
        client.chat_postMessage(
            channel=channel_id,
            text="🚀 *Keyword Processing Started!*\n\n"
                 "You can now:\n"
                 "• Upload a CSV file with keywords\n"
                 "• Paste comma or newline-separated keywords\n\n"
                 "I'll process them automatically!"
        )
        
        # If text provided, process immediately
        if text:
            pipeline = ProcessingPipeline(client, channel_id, user_id)
            pipeline.start_from_text(text)
        else:
            # Set state to await input
            if redis_client:
                redis_client.setex(
                    f"user:{user_id}:state",
                    3600,  # 1 hour expiry
                    json.dumps({
                        "status": "awaiting_input",
                        "channel_id": channel_id
                    })
                )
    
    @app.command("/history")
    def handle_history(ack, command, client):
        """Handle /history command"""
        ack()
        
        user_id = command['user_id']
        channel_id = command['channel_id']
        
        # Import database service
        from app.services.database import DatabaseService
        db = DatabaseService()
        
        # Get user history
        history = db.get_user_history(user_id, limit=5)
        
        if not history:
            client.chat_postMessage(
                channel=channel_id,
                text="📊 No processing history found. Use `/process_keywords` to get started!"
            )
            return
        
        # Format history
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📊 Your Processing History"}
            },
            {"type": "divider"}
        ]
        
        for batch in history:
            blocks.append({
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Batch:* {batch['id'][:8]}..."},
                    {"type": "mrkdwn", "text": f"*Date:* {batch['created_at'][:10]}"},
                    {"type": "mrkdwn", "text": f"*Keywords:* {batch['keyword_count']}"},
                    {"type": "mrkdwn", "text": f"*Status:* {batch['status']}"}
                ]
            })
            blocks.append({"type": "divider"})
        
        client.chat_postMessage(
            channel=channel_id,
            blocks=blocks
        )
```

**Testing:**
- Run /process_keywords in Slack
- Verify response appears
- Check Redis for user state

---

#### SLACK-016: Implement File Upload Handler
**Type:** Feature  
**Priority:** Critical  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Handle CSV file uploads from users.

**Acceptance Criteria:**
- [ ] Detects file uploads
- [ ] Downloads and parses CSV
- [ ] Triggers processing pipeline
- [ ] Handles file errors

**Deliverables:**
- `app/handlers/event_handlers.py`

**Dependencies:** SLACK-015, SLACK-006

**Code Implementation:**
```python
# app/handlers/event_handlers.py
import redis
import json
from app.config import Config
from app.services.keyword_parser import KeywordParser
from app.services.pipeline import ProcessingPipeline

redis_client = redis.from_url(Config.REDIS_URL) if Config.REDIS_URL else None

def register(app):
    """Register all event handlers"""
    
    @app.event("file_shared")
    def handle_file_upload(event, client):
        """Handle file uploads"""
        file_id = event['file_id']
        user_id = event['user_id']
        channel_id = event.get('channel_id')
        
        # Get file info
        file_info = client.files_info(file=file_id)
        file_data = file_info['file']
        
        # Check if CSV
        if not file_data['name'].endswith('.csv'):
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Please upload a CSV file containing keywords."
            )
            return
        
        # Download and parse
        try:
            parser = KeywordParser()
            keywords = parser.parse_csv_from_url(
                file_data['url_private'],
                Config.SLACK_BOT_TOKEN
            )
            
            # Start processing
            pipeline = ProcessingPipeline(client, channel_id, user_id)
            pipeline.start_from_keywords(keywords, source='csv')
            
        except Exception as e:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Error processing file: {str(e)}"
            )
    
    @app.event("message")
    def handle_message(event, client):
        """Handle text messages"""
        # Skip bot messages
        if event.get('bot_id'):
            return
        
        user_id = event['user']
        channel_id = event['channel']
        text = event.get('text', '').strip()
        
        # Check if user is awaiting input
        if redis_client:
            state_key = f"user:{user_id}:state"
            state_data = redis_client.get(state_key)
            
            if state_data:
                state = json.loads(state_data)
                
                if state.get('status') == 'awaiting_input':
                    # Parse keywords from message
                    parser = KeywordParser()
                    keywords = parser.parse_text(text)
                    
                    if len(keywords) < 1:
                        client.chat_postMessage(
                            channel=channel_id,
                            text="⚠️ No keywords detected. Please provide at least one keyword."
                        )
                        return
                    
                    # Clear state
                    redis_client.delete(state_key)
                    
                    # Start processing
                    pipeline = ProcessingPipeline(client, channel_id, user_id)
                    pipeline.start_from_keywords(keywords, source='text')
```

**Testing:**
- Upload CSV to Slack
- Verify bot downloads and processes
- Try uploading non-CSV file

---

#### SLACK-017: Build Message Formatters
**Type:** Feature  
**Priority:** High  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Create formatters for beautiful Slack messages.

**Acceptance Criteria:**
- [ ] Progress updates formatted nicely
- [ ] Results displayed clearly
- [ ] Uses Slack blocks API
- [ ] Mobile-friendly

**Deliverables:**
- `app/utils/slack_formatters.py`

**Dependencies:** SLACK-014

**Code Implementation:**
```python
# app/utils/slack_formatters.py
from typing import List, Dict

class SlackFormatter:
    """Format messages for Slack"""
    
    @staticmethod
    def format_progress(message: str, emoji: str = "⏳") -> str:
        """Format progress update"""
        return f"{emoji} {message}"
    
    @staticmethod
    def format_clusters(clusters: List[Dict]) -> List[Dict]:
        """Format clusters as Slack blocks"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🎯 Keyword Clusters"}
            },
            {"type": "divider"}
        ]
        
        for cluster in clusters:
            # Cluster header
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Cluster {cluster['cluster_number']}: {cluster['cluster_name']}*\n"
                           f"📊 {cluster['keyword_count']} keywords"
                }
            })
            
            # Show first 5 keywords
            keywords_display = cluster['keywords'][:5]
            if len(cluster['keywords']) > 5:
                keywords_display.append(f"... and {len(cluster['keywords']) - 5} more")
            
            blocks.append({
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": ", ".join(f"`{kw}`" for kw in keywords_display)
                }]
            })
            
            blocks.append({"type": "divider"})
        
        return blocks
    
    @staticmethod
    def format_cluster_detail(cluster: Dict, post_idea: Dict, outline: Dict) -> List[Dict]:
        """Format detailed cluster information"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📁 {cluster['cluster_name']}"
                }
            },
            {"type": "divider"}
        ]
        
        # Keywords
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Keywords ({cluster['keyword_count']}):*\n" +
                       "\n".join(f"• {kw}" for kw in cluster['keywords'])
            }
        })
        
        # Post Idea
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Post Idea:*\n{post_idea['post_idea']}"
            }
        })
        
        # Outline
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Outline:*\n" +
                       "\n".join(f"• {k}" for k in outline['outline'])
            }
        })
        
        return blocks
