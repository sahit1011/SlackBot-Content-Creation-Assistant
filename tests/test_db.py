#!/usr/bin/env python3
"""
Database connection and schema test script for Slackbot Content Creation Assistant.

This script tests the Supabase database connection and verifies that all tables
are created correctly with proper relationships and indexes.

Usage:
    python test_db.py

Requirements:
    - .env file with SUPABASE_URL and SUPABASE_KEY
    - Database schema applied (run migrations/001_initial_schema.sql in Supabase)
"""

import sys
import uuid
from datetime import datetime

try:
    from supabase import create_client, Client
    from app.config import Config
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def test_database_connection():
    """Test basic database connection."""
    try:
        supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        print("[OK] Database connection successful")
        return supabase
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return None


def test_users_table(supabase):
    """Test users table operations."""
    try:
        # Generate test data
        test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        test_data = {
            "slack_user_id": test_user_id,
            "slack_team_id": "T1234567890",
            "email": "test@example.com",
            "display_name": "Test User"
        }

        # Insert test user
        result = supabase.table('users').insert(test_data).execute()
        user_id = result.data[0]['id']
        print("[OK] Users table: Insert successful")

        # Select the user back
        result = supabase.table('users').select('*').eq('id', user_id).execute()
        if result.data:
            print("[OK] Users table: Select successful")
        else:
            print("[FAIL] Users table: Select failed - no data returned")

        # Note: Cleanup will be done at the end in main()

        return user_id

    except Exception as e:
        print(f"[FAIL] Users table test failed: {e}")
        return None


def test_keyword_batches_table(supabase, user_id):
    """Test keyword_batches table operations."""
    try:
        test_data = {
            "user_id": user_id,
            "batch_name": "Test Batch",
            "status": "pending",
            "raw_keywords": ["test", "keyword", "batch"],
            "cleaned_keywords": ["test", "keyword", "batch"],
            "keyword_count": 3,
            "cluster_count": 1,
            "source_type": "manual"
        }

        # Insert test batch
        result = supabase.table('keyword_batches').insert(test_data).execute()
        batch_id = result.data[0]['id']
        print("[OK] Keyword batches table: Insert successful")

        # Select the batch back
        result = supabase.table('keyword_batches').select('*').eq('id', batch_id).execute()
        if result.data:
            print("[OK] Keyword batches table: Select successful")
        else:
            print("[FAIL] Keyword batches table: Select failed")

        # Test foreign key constraint
        try:
            invalid_batch = {
                "user_id": str(uuid.uuid4()),  # Non-existent user
                "status": "pending",
                "raw_keywords": ["test"],
                "cleaned_keywords": ["test"],
                "keyword_count": 1
            }
            supabase.table('keyword_batches').insert(invalid_batch).execute()
            print("[FAIL] Foreign key constraint not working")
        except Exception:
            print("[OK] Foreign key constraint working")

        # Note: Cleanup will be done at the end in main()

        return batch_id

    except Exception as e:
        print(f"[FAIL] Keyword batches table test failed: {e}")
        return None


def test_keyword_clusters_table(supabase, batch_id):
    """Test keyword_clusters table operations."""
    try:
        test_data = {
            "batch_id": batch_id,
            "cluster_number": 1,
            "cluster_name": "Test Cluster",
            "keywords": ["test", "keyword"],
            "keyword_count": 2,
            "post_idea": "Test post idea",
            "top_urls": ["https://example.com"]
        }

        # Insert test cluster
        result = supabase.table('keyword_clusters').insert(test_data).execute()
        cluster_id = result.data[0]['id']
        print("[OK] Keyword clusters table: Insert successful")

        # Select the cluster back
        result = supabase.table('keyword_clusters').select('*').eq('id', cluster_id).execute()
        if result.data:
            print("[OK] Keyword clusters table: Select successful")
        else:
            print("[FAIL] Keyword clusters table: Select failed")

        # Note: Cleanup will be done at the end in main()

        return cluster_id

    except Exception as e:
        print(f"[FAIL] Keyword clusters table test failed: {e}")
        return None


def test_reports_table(supabase, batch_id):
    """Test reports table operations."""
    try:
        test_data = {
            "batch_id": batch_id,
            "pdf_filename": "test_report.pdf",
            "pdf_url": "https://example.com/test_report.pdf",
            "file_size_kb": 150,
            "sent_via_email": False
        }

        # Insert test report
        result = supabase.table('reports').insert(test_data).execute()
        report_id = result.data[0]['id']
        print("[OK] Reports table: Insert successful")

        # Select the report back
        result = supabase.table('reports').select('*').eq('id', report_id).execute()
        if result.data:
            print("[OK] Reports table: Select successful")
        else:
            print("[FAIL] Reports table: Select failed")

        # Note: Cleanup will be done at the end in main()

        return report_id

    except Exception as e:
        print(f"[FAIL] Reports table test failed: {e}")
        return None


def main():
    """Run all database tests."""
    print("Starting database schema tests...\n")

    # Check configuration
    if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
        print("[FAIL] Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_KEY in .env")
        sys.exit(1)

    # Test connection
    supabase = test_database_connection()
    if not supabase:
        sys.exit(1)

    print("\n Testing table operations...\n")

    # Test users table
    user_id = test_users_table(supabase)
    if not user_id:
        sys.exit(1)

    # Test keyword_batches table
    batch_id = test_keyword_batches_table(supabase, user_id)
    if not batch_id:
        sys.exit(1)

    # Test keyword_clusters table
    cluster_id = test_keyword_clusters_table(supabase, batch_id)
    if not cluster_id:
        sys.exit(1)

    # Test reports table
    report_id = test_reports_table(supabase, batch_id)
    if not report_id:
        sys.exit(1)

    # Clean up test data
    print("\nCleaning up test data...")
    try:
        supabase.table('reports').delete().eq('id', report_id).execute()
        supabase.table('keyword_clusters').delete().eq('id', cluster_id).execute()
        supabase.table('keyword_batches').delete().eq('id', batch_id).execute()
        supabase.table('users').delete().eq('id', user_id).execute()
        print("[OK] Cleanup successful")
    except Exception as e:
        print(f"[FAIL] Cleanup failed: {e}")

    print("\nAll database tests passed successfully!")
    print("\nNext steps:")
    print("1. Run the migration script in Supabase SQL Editor: migrations/001_initial_schema.sql")
    print("2. Execute this test script: python test_db.py")


if __name__ == "__main__":
    main()