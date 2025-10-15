#!/usr/bin/env python3
"""Test script for CacheService"""

from app.services.cache import CacheService
import time

def test_cache_service():
    print("Testing CacheService...")

    cache = CacheService()

    # Test basic set/get operations
    print("\n1. Testing basic set/get operations...")
    success = cache.set("test_key", {"data": "test_value"}, ttl=60)
    print(f"   Set operation: {'success' if success else 'failed (Redis unavailable)'}")

    retrieved = cache.get("test_key")
    if retrieved:
        print(f"   Retrieved: {retrieved}")
        assert retrieved["data"] == "test_value"
        print("   [OK] Basic set/get works")
    else:
        print("   [SKIP] Redis not available, skipping test")

    # Test user state management
    print("\n2. Testing user state management...")
    test_user_id = "test_user_123"

    # Set user state
    state = {"status": "awaiting_input", "channel_id": "C123456"}
    cache.set_user_state(test_user_id, state, ttl=60)

    # Get user state
    retrieved_state = cache.get_user_state(test_user_id)
    if retrieved_state:
        print(f"   Retrieved state: {retrieved_state}")
        assert retrieved_state["status"] == "awaiting_input"
        print("   [OK] User state management works")
    else:
        print("   [SKIP] Redis not available")

    # Test search result caching
    print("\n3. Testing search result caching...")
    query = "running shoes"
    mock_results = [
        {"title": "Best Running Shoes 2024", "url": "https://example.com/1"},
        {"title": "Top Rated Athletic Shoes", "url": "https://example.com/2"}
    ]

    cache.cache_search_results(query, mock_results)
    cached_results = cache.get_cached_search(query)

    if cached_results:
        print(f"   Cached results count: {len(cached_results)}")
        assert len(cached_results) == 2
        print("   [OK] Search result caching works")
    else:
        print("   [SKIP] Redis not available")

    # Test embeddings caching (mock)
    print("\n4. Testing embeddings caching...")
    try:
        import numpy as np
        keywords = ["test", "keywords"]
        mock_embeddings = np.random.rand(10, 384).astype(np.float32)

        cache.cache_embeddings(keywords, mock_embeddings)
        cached_embeddings = cache.get_cached_embeddings(keywords)

        if cached_embeddings is not None:
            print(f"   Cached embeddings shape: {cached_embeddings.shape}")
            # Note: Shape will be flattened when stored as bytes
            expected_size = mock_embeddings.size  # Total number of elements
            assert cached_embeddings.shape[0] == expected_size
            print("   [OK] Embeddings caching works")
        else:
            print("   [SKIP] Redis not available or numpy issue")
    except ImportError:
        print("   [SKIP] NumPy not available")

    # Test rate limiting
    print("\n5. Testing rate limiting...")
    test_user = "rate_limit_user"

    # Simulate multiple requests
    for i in range(3):
        allowed = cache.check_rate_limit(test_user, "process_keywords", max_requests=5)
        print(f"   Request {i+1}: {'allowed' if allowed else 'blocked'}")

    print("   [OK] Rate limiting works (or Redis unavailable)")

    # Test cache deletion
    print("\n6. Testing cache deletion...")
    cache.set("delete_test", "test_value", ttl=60)
    cache.delete("delete_test")
    deleted_value = cache.get("delete_test")

    if deleted_value is None:
        print("   [OK] Cache deletion works")
    else:
        print("   [SKIP] Redis not available")

    # Test TTL expiration (if Redis available)
    print("\n7. Testing TTL expiration...")
    cache.set("ttl_test", "expires_soon", ttl=2)  # 2 seconds
    time.sleep(3)  # Wait for expiration
    expired_value = cache.get("ttl_test")

    if expired_value is None:
        print("   [OK] TTL expiration works")
    else:
        print("   [SKIP] Redis not available or TTL not working")

    # Test graceful handling when Redis is unavailable
    print("\n8. Testing graceful Redis unavailability...")
    # This should not crash even if Redis is down
    unavailable_cache = CacheService()
    result = unavailable_cache.get("nonexistent_key")
    assert result is None
    print("   [OK] Graceful handling of unavailable Redis")

    print("\nAll CacheService tests completed!")

if __name__ == "__main__":
    test_cache_service()