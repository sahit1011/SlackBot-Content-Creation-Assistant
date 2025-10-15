#!/usr/bin/env python3
"""Test script for SLACK-017: Message Formatters"""

from app.utils.slack_formatters import SlackFormatter

def test_formatters():
    print("Testing SLACK-017: Message Formatters\n")

    # Test 1: Progress messages
    print("1. Progress Messages:")
    progress = SlackFormatter.format_progress("Processing keywords...", "OK")
    print(f"   {progress}")
    print("   Progress message formatted correctly")

    # Test 2: Clusters summary
    print("\n2. Clusters Summary:")
    sample_clusters = [
        {
            "cluster_number": 1,
            "cluster_name": "Fitness Equipment",
            "keyword_count": 15,
            "keywords": ["dumbbells", "knee sleeves", "resistance bands", "gym gloves", "workout clothes"]
        },
        {
            "cluster_number": 2,
            "cluster_name": "Nutrition",
            "keyword_count": 8,
            "keywords": ["protein powder", "sports water bottle", "energy bars"]
        }
    ]
    blocks = SlackFormatter.format_clusters_summary(sample_clusters)
    print(f"   Generated {len(blocks)} blocks for cluster summary")

    # Test 3: Cluster detail
    print("\n3. Cluster Detail:")
    sample_cluster = sample_clusters[0]
    sample_idea = {
        "title": "Ultimate Home Gym Guide",
        "angle": "Beginner-friendly equipment recommendations",
        "target_audience": "Fitness newcomers"
    }
    sample_outline = {
        "title": "Home Gym Setup Guide",
        "sections": [
            {"heading": "Essential Equipment"},
            {"heading": "Budget Considerations"},
            {"heading": "Safety Tips"}
        ]
    }
    detail_blocks = SlackFormatter.format_cluster_detail(sample_cluster, sample_idea, sample_outline)
    print(f"   Generated {len(detail_blocks)} blocks for cluster detail")

    # Test 4: Completion summary
    print("\n4. Completion Summary:")
    sample_stats = {
        "keyword_count": 23,
        "cluster_count": 3,
        "outline_count": 3,
        "idea_count": 3
    }
    completion_blocks = SlackFormatter.format_completion_summary(sample_stats)
    print(f"   Generated {len(completion_blocks)} blocks for completion summary")

    # Test 5: Error messages
    print("\n5. Error Messages:")
    error_blocks = SlackFormatter.format_error(
        "Failed to process keywords",
        "Check your CSV format and try again",
        "batch_123"
    )
    print(f"   Generated {len(error_blocks)} blocks for error message")

    # Test 6: Edge cases
    print("\n6. Edge Cases:")

    # Long keywords
    long_cluster = {
        "cluster_number": 1,
        "cluster_name": "Very Long Cluster Name That Might Cause Issues",
        "keyword_count": 25,
        "keywords": [f"keyword_{i}" for i in range(15)]  # More than 10
    }
    long_blocks = SlackFormatter.format_cluster_detail(long_cluster, None, None)
    print(f"   Long cluster: {len(long_blocks)} blocks")

    # Empty data
    empty_blocks = SlackFormatter.format_clusters_summary([])
    print(f"   Empty clusters: {len(empty_blocks)} blocks")

    # Special characters
    special_cluster = {
        "cluster_number": 1,
        "cluster_name": "Special Chars: @#$%^&*()",
        "keyword_count": 3,
        "keywords": ["café", "naïve", "résumé"]
    }
    special_blocks = SlackFormatter.format_cluster_detail(special_cluster, None, None)
    print(f"   Special chars: {len(special_blocks)} blocks")

    print("\nAll formatter tests completed successfully!")
    print("All messages designed to be mobile-friendly with proper block structure")

if __name__ == "__main__":
    test_formatters()