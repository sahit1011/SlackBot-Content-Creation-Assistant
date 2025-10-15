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

    # Test keywords
    test_keywords = [
        "running shoes",
        "yoga mats",
        "protein powder",
        "fitness trackers",
        "workout clothes"
    ]

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

if __name__ == "__main__":
    test_pipeline()