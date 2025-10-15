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

    def get_user_email(self, user_id: str) -> Optional[str]:
        """Get user's email address"""
        response = self.client.table('users')\
            .select('email')\
            .eq('id', user_id)\
            .execute()

        if response.data and response.data[0].get('email'):
            return response.data[0]['email']
        return None

    def update_report_email_status(self, batch_id: str, sent: bool, email: str):
        """Update report email delivery status"""
        self.client.table('reports')\
            .update({
                'sent_via_email': sent,
                'email_sent_to': email
            })\
            .eq('batch_id', batch_id)\
            .execute()

    def get_batch_by_id(self, batch_id: str) -> Optional[Dict]:
        """Get batch by ID (alias for get_batch)"""
        return self.get_batch(batch_id)

    def get_clusters_by_batch(self, batch_id: str) -> List[Dict]:
        """Get all clusters for a batch (alias for get_batch_clusters)"""
        return self.get_batch_clusters(batch_id)

    def update_cluster_outline(self, batch_id: str, cluster_id: int, new_outline: Dict, new_idea: Dict):
        """Update cluster outline and idea after regeneration"""
        self.client.table('keyword_clusters')\
            .update({
                'outline_json': new_outline,
                'post_idea': new_idea.get('title', ''),
                'post_idea_metadata': new_idea,
                'updated_at': datetime.now().isoformat()
            })\
            .eq('batch_id', batch_id)\
            .eq('cluster_number', cluster_id)\
            .execute()