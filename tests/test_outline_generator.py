#!/usr/bin/env python3
"""Test script for OutlineGenerator"""

from app.services.ai.outline_generator import OutlineGenerator
import json

def test_outline_generator():
    print("Testing OutlineGenerator...")

    # Initialize generator
    generator = OutlineGenerator()
    print("OutlineGenerator initialized successfully")

    try:
        # Test data
        cluster = {
            'keywords': ['running shoes', 'best running shoes', 'comfortable sneakers'],
            'cluster_name': 'Running Shoes'
        }

        scraped_data = [
            {
                'success': True,
                'url': 'https://example.com/running-shoes-guide',
                'headings': [
                    {'level': 'h2', 'text': 'Types of Running Shoes', 'position': 1},
                    {'level': 'h2', 'text': 'How to Choose Running Shoes', 'position': 2},
                    {'level': 'h3', 'text': 'Consider Your Foot Type', 'position': 3},
                    {'level': 'h3', 'text': 'Running Surface Matters', 'position': 4},
                    {'level': 'h2', 'text': 'Best Running Shoes 2024', 'position': 5},
                    {'level': 'h3', 'text': 'Budget-Friendly Options', 'position': 6},
                    {'level': 'h3', 'text': 'Premium Performance Shoes', 'position': 7}
                ]
            },
            {
                'success': True,
                'url': 'https://example.com/sneakers-review',
                'headings': [
                    {'level': 'h2', 'text': 'Comfortable Sneakers Guide', 'position': 1},
                    {'level': 'h2', 'text': 'How to Choose Running Shoes', 'position': 2},
                    {'level': 'h3', 'text': 'Check the Cushioning', 'position': 3},
                    {'level': 'h2', 'text': 'Top Rated Sneakers', 'position': 4}
                ]
            }
        ]

        print("\nGenerating outline...")
        outline = generator.generate_outline(cluster, scraped_data)

        print("Outline generated successfully!")
        print(f"Title: {outline.get('title', 'N/A')}")

        # Check structure
        required_keys = ['title', 'introduction', 'sections', 'conclusion']
        print("\nValidating outline structure:")
        for key in required_keys:
            if key in outline:
                print(f"  [OK] {key}: present")
            else:
                print(f"  [MISSING] {key}: missing")

        # Check introduction
        intro = outline.get('introduction', {})
        if 'hook' in intro and 'overview' in intro:
            print("  [OK] introduction: complete")
        else:
            print("  [INCOMPLETE] introduction: incomplete")

        # Check sections
        sections = outline.get('sections', [])
        print(f"  [OK] sections: {len(sections)} main sections")
        for i, section in enumerate(sections[:3], 1):  # Show first 3
            heading = section.get('heading', 'N/A')
            subsections = section.get('subsections', [])
            print(f"    Section {i}: {heading} ({len(subsections)} subsections)")

        # Check conclusion
        conclusion = outline.get('conclusion', {})
        if 'summary' in conclusion and 'cta' in conclusion:
            print("  [OK] conclusion: complete")
        else:
            print("  [INCOMPLETE] conclusion: incomplete")

        # Pretty print the full outline
        print("\n" + "="*50)
        print("GENERATED OUTLINE:")
        print("="*50)
        print(json.dumps(outline, indent=2))

        print("\n" + "="*50)
        print("Test completed successfully!")

    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_outline_generator()