#!/usr/bin/env python3
"""Test script for IdeaGenerator"""

import logging
from app.services.ai.idea_generator import IdeaGenerator
import json

def test_idea_generator():
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Testing IdeaGenerator...")

    # Initialize generator
    generator = IdeaGenerator()
    print("IdeaGenerator initialized successfully")

    try:
        # Test data
        cluster = {
            'keywords': ['running shoes', 'best running shoes'],
            'cluster_name': 'Running Shoes'
        }

        print("\nGenerating idea...")
        idea = generator.generate_idea(cluster)

        print("Idea generated successfully!")

        # Check structure
        required_keys = ['title', 'angle', 'target_audience', 'value_proposition']
        print("\nValidating idea structure:")
        for key in required_keys:
            if key in idea:
                print(f"  [OK] {key}: present")
                print(f"    Value: {idea[key]}")
            else:
                print(f"  [MISSING] {key}: missing")

        # Pretty print the full idea
        print("\n" + "="*50)
        print("GENERATED IDEA:")
        print("="*50)
        print(json.dumps(idea, indent=2))

        print("\n" + "="*50)
        print("Test completed successfully!")

    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_idea_generator()