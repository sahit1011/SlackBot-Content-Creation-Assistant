# EPIC-005: Processing Pipeline Orchestration

**Priority:** P0 (Critical Path)  
**Story Points:** 10  
**Duration:** 1 Day  
**Owner:** Developer  

---

## SLACK-018: Build Main Processing Pipeline

**Type:** Feature  
**Priority:** Critical  
**Story Points:** 5  
**Estimated Time:** 4 hours  

**Description:**
Create the main orchestrator that coordinates all processing steps from keywords to final results.

**Acceptance Criteria:**
- [ ] Orchestrates complete workflow (clean → cluster → research → generate)
- [ ] Sends progress updates to Slack in real-time
- [ ] Handles errors gracefully without crashing
- [ ] Saves all results to database
- [ ] Runs asynchronously (doesn't block Slack)
- [ ] Supports concurrent processing for multiple users

**Deliverables:**
- `app/services/pipeline.py`

**Dependencies:** SLACK-009, SLACK-012, SLACK-013, SLACK-017, SLACK-019

**Code Implementation:**

```python
# app/services/pipeline.py
import threading
from typing import List
from app.services.keyword_cleaner import KeywordCleaner
from app.services.embedding_generator import EmbeddingGenerator
from app.services.keyword_clusterer import KeywordClusterer
from app.services.web_search import WebSearchService
from app.services.content_scraper import ContentScraper
from app.services.outline_generator import OutlineGenerator
from app.services.idea_generator import IdeaGenerator
from app.services.database import DatabaseService
from app.services.report_generator import ReportGenerator
from app.utils.slack_formatters import SlackFormatter

class ProcessingPipeline:
    """Orchestrate the complete keyword processing workflow"""
    
    def __init__(self, slack_client, channel_id: str, user_id: str):
        self.client = slack_client
        self.channel_id = channel_id
        self.user_id = user_id
        self.db = DatabaseService()
        self.formatter = SlackFormatter()
    
    def start_from_keywords(self, keywords: List[str], source: str = 'text'):
        """Start processing in background thread"""
        thread = threading.Thread(
            target=self._process_keywords,
            args=(keywords, source)
        )
        thread.daemon = True
        thread.start()
    
    def _process_keywords(self, raw_keywords: List[str], source: str):
        """Main processing pipeline"""
        batch_id = None
        
        try:
            # Step 1: Clean keywords
            self._send_progress("🧹 Cleaning keywords...")
            cleaner = KeywordCleaner()
            result = cleaner.clean_keywords(raw_keywords)
            cleaned_keywords = result['keywords']
            
            self._send_progress(
                f"✓ Cleaned: {result['original_count']} → {result['cleaned_count']} unique keywords"
            )
            
            # Save batch to database
            batch_data = self.db.save_batch(
                self.user_id,
                raw_keywords,
                cleaned_keywords,
                source
            )
            batch_id = batch_data['id']
            
            # Step 2: Generate embeddings
            self._send_progress("🔍 Analyzing keyword relationships...")
            embedding_gen = EmbeddingGenerator()
            embeddings = embedding_gen.generate_embeddings(cleaned_keywords)
            
            # Step 3: Cluster keywords
            self._send_progress("📊 Grouping keywords into clusters...")
            clusterer = KeywordClusterer()
            clusters = clusterer.cluster_keywords(cleaned_keywords, embeddings)
            
            self._send_progress(f"✓ Created {len(clusters)} keyword clusters")
            
            # Send cluster summary
            cluster_blocks = self.formatter.format_clusters_summary(clusters)
            self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=cluster_blocks
            )
            
            # Step 4: Process each cluster
            search_service = WebSearchService()
            scraper = ContentScraper()
            outline_gen = OutlineGenerator()
            idea_gen = IdeaGenerator()
            
            for idx, cluster in enumerate(clusters, 1):
                self._send_progress(f"📝 Processing cluster {idx}/{len(clusters)}: {cluster['cluster_name']}")
                
                # Search top results
                main_keyword = cluster['keywords'][0]
                search_results = search_service.search_single(main_keyword, count=5)
                
                # Scrape content
                urls = [r['url'] for r in search_results[:3]]
                scraped_data = scraper.scrape_urls(urls)
                
                # Generate outline
                outline = outline_gen.generate_outline(cluster, scraped_data)
                cluster['outline'] = outline
                
                # Generate post idea
                post_idea = idea_gen.generate_idea(cluster, outline)
                cluster['post_idea'] = post_idea
                
                # Save cluster to database
                self.db.save_cluster(batch_id, cluster, post_idea, outline)
                
                # Send detailed cluster info
                detail_blocks = self.formatter.format_cluster_detail(
                    cluster, post_idea, outline
                )
                self.client.chat_postMessage(
                    channel=self.channel_id,
                    blocks=detail_blocks
                )
            
            # Step 5: Generate report
            self._send_progress("📄 Generating comprehensive report...")
            report_gen = ReportGenerator()
            pdf_path = report_gen.generate_report(
                batch_data,
                cleaned_keywords,
                clusters
            )
            
            # Upload report to Slack
            self.client.files_upload_v2(
                channel=self.channel_id,
                file=pdf_path,
                title=f"Content_Strategy_Report_{batch_id[:8]}.pdf",
                initial_comment="📄 Your comprehensive content strategy report is ready!"
            )
            
            # Save report info
            self.db.save_report(batch_id, pdf_path)
            
            # Step 6: Send completion summary
            summary_blocks = self.formatter.format_completion_summary({
                'keyword_count': len(cleaned_keywords),
                'cluster_count': len(clusters),
                'outline_count': len(clusters),
                'idea_count': len(clusters)
            })
            self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=summary_blocks
            )
            
            # Update batch status
            self.db.update_batch_status(batch_id, 'completed')
            
        except Exception as e:
            error_msg = str(e)
            print(f"Pipeline error: {error_msg}")
            
            # Send error to user
            error_blocks = self.formatter.format_error(
                "An error occurred during processing",
                "Please try again or contact support if the issue persists",
                batch_id
            )
            self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=error_blocks
            )
            
            # Update batch status
            if batch_id:
                self.db.update_batch_status(batch_id, 'failed', error_msg)
    
    def _send_progress(self, message: str):
        """Send progress update to Slack"""
        formatted = self.formatter.format_progress(message)
        self.client.chat_postMessage(
            channel=self.channel_id,
            text=formatted
        )
```

**Testing:**
- Process 5 keywords end-to-end
- Verify all steps complete
- Check database records
- Confirm Slack messages sent
- Test error scenarios

---

## SLACK-019: Build Database Service

**Type:** Feature  
**Priority:** Critical  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Create service layer for all database operations with Supabase.

**Acceptance Criteria:**
- [ ] CRUD operations for all tables
- [ ] Connection pooling implemented
- [ ] Proper error handling
- [ ] Returns structured data
- [ ] Supports transactions where needed

**Deliverables:**
- `app/services/database.py`

**Dependencies:** SLACK-004

**Code Implementation:**

```python
# app/services/database.py
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime
from app.config import Config

class DatabaseService:
    """Handle all database operations"""
    
    def __init__(self):
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
    
    def save_batch(
        self,
        user_id: str,
        raw_keywords: List[str],
        cleaned_keywords: List[str],
        source_type: str
    ) -> Dict:
        """Save a new keyword batch"""
        data = {
            'user_id': user_id,
            'batch_name': f"Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'status': 'processing',
            'raw_keywords': raw_keywords,
            'cleaned_keywords': cleaned_keywords,
            'keyword_count': len(cleaned_keywords),
            'source_type': source_type
        }
        
        response = self.client.table('keyword_batches').insert(data).execute()
        return response.data[0] if response.data else None
    
    def update_batch_status(
        self,
        batch_id: str,
        status: str,
        error_message: str = None
    ):
        """Update batch status"""
        data = {
            'status': status,
            'completed_at': datetime.now().isoformat() if status == 'completed' else None
        }
        
        if error_message:
            data['error_message'] = error_message
        
        self.client.table('keyword_batches').update(data).eq('id', batch_id).execute()
    
    def save_cluster(
        self,
        batch_id: str,
        cluster: Dict,
        post_idea: Dict,
        outline: Dict
    ):
        """Save a keyword cluster with its analysis"""
        data = {
            'batch_id': batch_id,
            'cluster_number': cluster['cluster_number'],
            'cluster_name': cluster['cluster_name'],
            'keywords': cluster['keywords'],
            'keyword_count': cluster['keyword_count'],
            'post_idea': post_idea.get('title', ''),
            'post_idea_metadata': post_idea,
            'outline_json': outline
        }
        
        self.client.table('keyword_clusters').insert(data).execute()
    
    def save_report(self, batch_id: str, pdf_path: str, pdf_url: str = None):
        """Save report information"""
        import os
        
        data = {
            'batch_id': batch_id,
            'pdf_filename': os.path.basename(pdf_path),
            'pdf_url': pdf_url or pdf_path,
            'file_size_kb': os.path.getsize(pdf_path) // 1024 if os.path.exists(pdf_path) else 0
        }
        
        self.client.table('reports').insert(data).execute()
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's processing history"""
        response = self.client.table('keyword_batches')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data if response.data else []
    
    def get_batch(self, batch_id: str) -> Optional[Dict]:
        """Get batch by ID"""
        response = self.client.table('keyword_batches')\
            .select('*')\
            .eq('id', batch_id)\
            .execute()
        
        return response.data[0] if response.data else None
    
    def get_batch_clusters(self, batch_id: str) -> List[Dict]:
        """Get all clusters for a batch"""
        response = self.client.table('keyword_clusters')\
            .select('*')\
            .eq('batch_id', batch_id)\
            .order('cluster_number')\
            .execute()
        
        return response.data if response.data else []
    
    def get_or_create_user(self, slack_user_id: str, display_name: str = None) -> Dict:
        """Get or create user record"""
        # Try to find existing user
        response = self.client.table('users')\
            .select('*')\
            .eq('slack_user_id', slack_user_id)\
            .execute()
        
        if response.data:
            # Update last active
            user = response.data[0]
            self.client.table('users').update({
                'last_active_at': datetime.now().isoformat()
            }).eq('id', user['id']).execute()
            return user
        
        # Create new user
        data = {
            'slack_user_id': slack_user_id,
            'display_name': display_name
        }
        
        response = self.client.table('users').insert(data).execute()
        return response.data[0] if response.data else None
```

**Testing:**
- Test each CRUD operation
- Verify foreign keys work
- Test with invalid data
- Check error handling
- Test concurrent operations

---

## SLACK-020: Build Redis Cache Service

**Type:** Feature  
**Priority:** High  
**Story Points:** 2  
**Estimated Time:** 1.5 hours  

**Description:**
Create Redis service for caching embeddings, search results, and managing user state.

**Acceptance Criteria:**
- [ ] Cache embeddings with TTL
- [ ] Cache search results (1 hour)
- [ ] Manage user session state
- [ ] Handle Redis connection failures gracefully
- [ ] Clear stale cache entries

**Deliverables:**
- `app/services/cache.py`

**Dependencies:** SLACK-003

**Code Implementation:**

```python
# app/services/cache.py
import redis
import json
import hashlib
from typing import Any, Optional
from app.config import Config

class CacheService:
    """Handle Redis caching operations"""
    
    def __init__(self):
        try:
            self.client = redis.from_url(Config.REDIS_URL) if Config.REDIS_URL else None
            if self.client:
                self.client.ping()
        except:
            self.client = None
            print("Warning: Redis unavailable, caching disabled")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (default 1 hour)"""
        if not self.client:
            return False
        
        try:
            self.client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.client:
            return
        
        try:
            self.client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    def get_user_state(self, user_id: str) -> Optional[Dict]:
        """Get user session state"""
        return self.get(f"user:{user_id}:state")
    
    def set_user_state(self, user_id: str, state: Dict, ttl: int = 3600):
        """Set user session state"""
        self.set(f"user:{user_id}:state", state, ttl)
    
    def clear_user_state(self, user_id: str):
        """Clear user session state"""
        self.delete(f"user:{user_id}:state")
    
    def cache_search_results(self, query: str, results: list):
        """Cache search results for 1 hour"""
        cache_key = self._generate_cache_key("search", query)
        self.set(cache_key, results, ttl=3600)
    
    def get_cached_search(self, query: str) -> Optional[list]:
        """Get cached search results"""
        cache_key = self._generate_cache_key("search", query)
        return self.get(cache_key)
    
    def cache_embeddings(self, keywords: list, embeddings: Any):
        """Cache embeddings for 24 hours"""
        cache_key = self._generate_cache_key("embeddings", str(sorted(keywords)))
        # Store as binary data
        if self.client:
            try:
                import numpy as np
                self.client.setex(
                    cache_key,
                    86400,  # 24 hours
                    embeddings.astype(np.float32).tobytes()
                )
            except:
                pass
    
    def get_cached_embeddings(self, keywords: list) -> Optional[Any]:
        """Get cached embeddings"""
        cache_key = self._generate_cache_key("embeddings", str(sorted(keywords)))
        if self.client:
            try:
                import numpy as np
                cached = self.client.get(cache_key)
                if cached:
                    return np.frombuffer(cached, dtype=np.float32)
            except:
                pass
        return None
    
    def increment_rate_limit(self, user_id: str, action: str) -> int:
        """Increment rate limit counter"""
        if not self.client:
            return 0
        
        key = f"ratelimit:{user_id}:{action}"
        try:
            count = self.client.incr(key)
            if count == 1:
                self.client.expire(key, 3600)  # 1 hour window
            return count
        except:
            return 0
    
    def check_rate_limit(self, user_id: str, action: str, max_requests: int = 10) -> bool:
        """Check if user has exceeded rate limit"""
        count = self.increment_rate_limit(user_id, action)
        return count <= max_requests
    
    def _generate_cache_key(self, prefix: str, data: str) -> str:
        """Generate cache key from data"""
        hash_value = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
```

**Testing:**
- Test set/get operations
- Verify TTL expiration
- Test with Redis unavailable
- Check rate limiting
- Test cache invalidation

---

## Epic Completion Checklist

**All Tasks Complete:**
- [ ] SLACK-018: Processing pipeline
- [ ] SLACK-019: Database service
- [ ] SLACK-020: Redis cache service

**Integration Tests:**
- [ ] Full end-to-end processing works
- [ ] Database saves all data correctly
- [ ] Cache improves performance
- [ ] Error handling works
- [ ] Progress updates appear

**Performance:**
- [ ] Processes 10 keywords in < 2 minutes
- [ ] Processes 50 keywords in < 5 minutes
- [ ] No memory leaks
- [ ] Handles concurrent users

**Ready for Next Epic:**
- [ ] No blocking bugs
- [ ] Code committed to Git
- [ ] Tests passing
- [ ] Documentation updated