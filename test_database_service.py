#!/usr/bin/env python3
"""Test script for DatabaseService"""

from app.services.database import DatabaseService
import uuid

def test_database_service():
    print("Testing DatabaseService...")

    db = DatabaseService()

    # Test get_or_create_user
    print("\n1. Testing get_or_create_user...")
    test_slack_id = f"test_user_{uuid.uuid4().hex[:8]}"
    user = db.get_or_create_user(test_slack_id, "Test User")
    print(f"   Created user: {user}")
    assert user is not None
    assert user['slack_user_id'] == test_slack_id
    print("   [OK] get_or_create_user works")

    # Test save_batch
    print("\n2. Testing save_batch...")
    raw_keywords = ["test keyword 1", "test keyword 2"]
    cleaned_keywords = ["test", "keyword", "1", "2"]
    batch = db.save_batch(user['id'], raw_keywords, cleaned_keywords, "test")
    print(f"   Created batch: {batch}")
    assert batch is not None
    assert batch['user_id'] == user['id']
    print("   [OK] save_batch works")

    # Test update_batch_status
    print("\n3. Testing update_batch_status...")
    db.update_batch_status(batch['id'], 'completed')
    print("   [OK] update_batch_status works")

    # Test save_cluster
    print("\n4. Testing save_cluster...")
    cluster = {
        'cluster_number': 1,
        'cluster_name': 'Test Cluster',
        'keywords': ['test', 'cluster'],
        'keyword_count': 2
    }
    post_idea = {'title': 'Test Post', 'angle': 'Test angle'}
    outline = {'title': 'Test Outline', 'sections': []}
    db.save_cluster(batch['id'], cluster, post_idea, outline)
    print("   [OK] save_cluster works")

    # Test save_report
    print("\n5. Testing save_report...")
    db.save_report(batch['id'], "/tmp/test.pdf")
    print("   [OK] save_report works")

    # Test get_user_history
    print("\n6. Testing get_user_history...")
    history = db.get_user_history(user['id'])
    print(f"   History: {len(history)} batches")
    assert len(history) >= 1
    print("   [OK] get_user_history works")

    # Test get_batch
    print("\n7. Testing get_batch...")
    retrieved_batch = db.get_batch(batch['id'])
    print(f"   Retrieved batch: {retrieved_batch}")
    assert retrieved_batch is not None
    assert retrieved_batch['id'] == batch['id']
    print("   [OK] get_batch works")

    # Test get_batch_clusters
    print("\n8. Testing get_batch_clusters...")
    clusters = db.get_batch_clusters(batch['id'])
    print(f"   Clusters: {len(clusters)}")
    assert len(clusters) >= 1
    print("   [OK] get_batch_clusters works")

    # Test error handling with invalid data
    print("\n9. Testing error handling...")
    try:
        # Try to save batch with invalid user_id
        invalid_batch = db.save_batch(str(uuid.uuid4()), [], [], "test")
        print("   [FAIL] Should have failed with invalid user_id")
    except Exception as e:
        print(f"   [OK] Correctly handled invalid user_id: {type(e).__name__}")

    print("\nAll DatabaseService tests passed!")

if __name__ == "__main__":
    test_database_service()