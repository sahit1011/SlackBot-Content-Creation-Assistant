#!/usr/bin/env python3
"""Test script for ProcessingPipeline"""

from app.services.processing.pipeline import ProcessingPipeline
from unittest.mock import Mock
import time

class MockSlackClient:
    """Mock Slack client for testing"""

    def __init__(self):
        self.messages = []
        self.files = []

    def chat_postMessage(self, channel, text=None, blocks=None):
        message = {
            'channel': channel,
            'text': text,
            'blocks': blocks
        }
        self.messages.append(message)
        # Handle encoding issues with emojis
        safe_text = text or 'Blocks sent'
        try:
            print(f"Slack Message: {safe_text}")
        except UnicodeEncodeError:
            print(f"Slack Message: {safe_text.encode('ascii', 'ignore').decode('ascii')}")

    def files_upload_v2(self, channel, file, title, initial_comment):
        upload = {
            'channel': channel,
            'file': file,
            'title': title,
            'comment': initial_comment
        }
        self.files.append(upload)
        print(f"📎 File Uploaded: {title}")

def test_pipeline():
    print("Testing ProcessingPipeline...")

    # Create mock client
    mock_client = MockSlackClient()

    # Test keywords - comprehensive set for content creation
    test_keywords = [
        "best running shoes 2024",
        "yoga mats for beginners",
        "protein powder reviews",
        "fitness trackers comparison",
        "workout clothes women",
        "home gym equipment",
        "meal prep ideas",
        "weight loss tips",
        "muscle building supplements",
        "cardio workout plans"
    ]

    # Payment Gateway Test Scenarios - Based on White-Label Payment Gateways Guide
    payment_gateway_scenarios = {
        "common_user_prompts": [
            # Typical keyword lists for payment gateway content
            [
                "white label payment gateway",
                "payment gateway white label solution",
                "best white label payment gateway",
                "white label payment gateway software",
                "white label payment gateway platform"
            ],
            [
                "white label cryptocurrency payment gateway",
                "crypto payment gateway white label",
                "white label crypto payment gateway",
                "white label crypto payments gateway",
                "white label crypto payment gateway solution"
            ],
            [
                "white label payment gateway uk",
                "white label payment gateway solution company in europe",
                "white label payment gateway solution company in uk"
            ],
            [
                "white label payment gateway price",
                "white label payment gateway prices",
                "white label payment gateway cost",
                "how much do white label payment gateways cost"
            ]
        ],
        "edge_cases": [
            # Empty inputs
            [],
            # Single keyword
            ["white label payment gateway"],
            # Duplicates
            ["white label payment gateway", "white label payment gateway", "payment gateway white label solution", "payment gateway white label solution"],
            # Very long list (50+ keywords)
            [
                "white label payment gateway", "white-label payment gateway", "white label payment gateways",
                "what is white label payment gateway", "what is a white label payment gateway", "white label payment gateway meaning",
                "benefits of white label payment gateway", "benefits of using a white-label payment gateway",
                "white label payment gateway uk", "white label payment gateway solution company in europe",
                "white label payment gateway solution company in uk", "white label payment gateway price",
                "white label payment gateway prices", "white label payment gateway cost",
                "white label payment gateway solution", "payment gateway white label solution",
                "white label payment gateway solutions", "white label payment gateway software",
                "white-label payment gateway software", "white label payment gateway platform",
                "best white label payment gateway", "best white-label payment gateway for businesses",
                "best white label payment gateways", "white label cryptocurrency payment gateway",
                "crypto payment gateway white label", "white label crypto payment gateway",
                "white label crypto payments gateway", "white label crypto payments gateway solution",
                "white label crypto payment gateway development", "white-label cryptocurrency payment gateway development",
                "how do payment gateways work", "types of businesses use white-label payment gateways",
                "ecommerce white label payment gateway", "trading white label payment gateway",
                "PSP white label payment gateway", "crypto white label payment gateway",
                "benefits of using a white-label payment gateway", "cost effective white label payment gateway",
                "custom branding white label payment gateway", "fast deployment white label payment gateway",
                "global access white label payment gateway", "built-in compliance white label payment gateway",
                "how to choose the right white label payment gateway", "cost structure white label payment gateway",
                "pricing white label payment gateway", "security standards white label payment gateway",
                "compliance white label payment gateway", "customization capabilities white label payment gateway",
                "integration options white label payment gateway", "industry expertise white label payment gateway",
                "how much do white label payment gateways cost", "best white label payment gateway providers in 2025",
                "ivy white label payment gateway", "stripe white label payment gateway",
                "decta white label payment gateway", "corefy white label payment gateway",
                "payabl white label payment gateway"
            ],
            # Ambiguous/unclear keywords
            ["payment", "gateway", "white", "label", "solution", "best", "2025"],
            # Mixed with irrelevant terms
            ["white label payment gateway", "cats", "dogs", "pizza recipes", "best running shoes 2024"],
            # Special characters and formatting
            ["white-label payment gateway!", "payment gateway @ white label", "white#label$payment%gateway"],
            # Very short keywords
            ["a", "b", "c", "d", "e"]
        ]
    }

    # Initialize pipeline with a valid UUID for user_id
    import uuid
    test_user_id = str(uuid.uuid4())
    pipeline = ProcessingPipeline(mock_client, "test_channel", test_user_id)

    print(f"Starting pipeline with {len(test_keywords)} keywords...")
    pipeline.start_from_keywords(test_keywords, source='test')

    # Wait for processing to complete (since it's async)
    print("Waiting for processing to complete...")
    time.sleep(30)  # Adjust based on expected processing time

    print(f"\nTest completed!")
    print(f"Messages sent: {len(mock_client.messages)}")
    print(f"Files uploaded: {len(mock_client.files)}")

    # Check if processing completed
    if mock_client.messages:
        print("\nLast few messages:")
        for msg in mock_client.messages[-3:]:
            safe_text = msg['text'] or 'Blocks sent'
            try:
                print(f"  - {safe_text}")
            except UnicodeEncodeError:
                print(f"  - {safe_text.encode('ascii', 'ignore').decode('ascii')}")

    if mock_client.files:
        print(f"\nFiles uploaded: {len(mock_client.files)}")
        for file in mock_client.files:
            print(f"  - {file['title']}")

def test_payment_gateway_scenarios():
    """Test payment gateway scenarios from the White-Label Payment Gateways Guide"""
    print("\n" + "="*60)
    print("TESTING PAYMENT GATEWAY SCENARIOS")
    print("="*60)

    # Create mock client
    mock_client = MockSlackClient()

    # Initialize pipeline with a valid UUID for user_id
    import uuid
    test_user_id = str(uuid.uuid4())

    # Test Common User Prompts
    print("\n🔍 Testing Common User Prompt Scenarios...")
    for i, keywords in enumerate(payment_gateway_scenarios["common_user_prompts"], 1):
        print(f"\n--- Scenario {i}: {len(keywords)} keywords ---")
        print(f"Keywords: {keywords}")

        # Reset mock client for each test
        mock_client = MockSlackClient()
        pipeline = ProcessingPipeline(mock_client, "test_channel", test_user_id)

        try:
            pipeline.start_from_keywords(keywords, source='payment_gateway_test')
            time.sleep(15)  # Shorter wait for smaller datasets

            print(f"✓ Processing completed - Messages: {len(mock_client.messages)}, Files: {len(mock_client.files)}")

            # Show cluster summary if available
            cluster_messages = [msg for msg in mock_client.messages if 'cluster' in (msg.get('text') or '').lower()]
            if cluster_messages:
                print(f"  📊 Clusters found: {len(cluster_messages)}")

        except Exception as e:
            print(f"✗ Error in scenario {i}: {str(e)}")

    # Test Edge Cases
    print("\n⚠️  Testing Edge Case Scenarios...")
    edge_case_names = [
        "Empty input", "Single keyword", "Duplicates", "Very long list (50+ keywords)",
        "Ambiguous keywords", "Mixed irrelevant terms", "Special characters", "Very short keywords"
    ]

    for i, (name, keywords) in enumerate(zip(edge_case_names, payment_gateway_scenarios["edge_cases"]), 1):
        print(f"\n--- Edge Case {i}: {name} ({len(keywords)} keywords) ---")
        if len(keywords) <= 10:  # Only show full list for short ones
            print(f"Keywords: {keywords}")
        else:
            print(f"Keywords: {keywords[:5]}... (showing first 5 of {len(keywords)})")

        # Reset mock client for each test
        mock_client = MockSlackClient()
        pipeline = ProcessingPipeline(mock_client, "test_channel", test_user_id)

        try:
            if not keywords:  # Handle empty list
                print("⚠️  Skipping empty keyword list")
                continue

            pipeline.start_from_keywords(keywords, source='payment_gateway_edge_case')
            time.sleep(10)  # Even shorter for edge cases

            print(f"✓ Processing completed - Messages: {len(mock_client.messages)}, Files: {len(mock_client.files)}")

            # Check for errors
            error_messages = [msg for msg in mock_client.messages if 'error' in (msg.get('text') or '').lower()]
            if error_messages:
                print(f"  ❌ Errors detected: {len(error_messages)}")

        except Exception as e:
            print(f"✗ Error in edge case {i} ({name}): {str(e)}")

    print("\n" + "="*60)
    print("PAYMENT GATEWAY SCENARIO TESTING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_pipeline()
    test_payment_gateway_scenarios()