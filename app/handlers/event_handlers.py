import redis
import json
from app.config import Config
from app.services.processing.keyword_parser import KeywordParser
from app.services.processing.pipeline import ProcessingPipeline
from slack_sdk import WebClient

redis_client = redis.from_url(Config.REDIS_URL) if Config.REDIS_URL else None
client = WebClient(token=Config.SLACK_BOT_TOKEN)

def register(app):
    """Register all event handlers"""

    @app.event("file_shared")
    def handle_file_upload(event, say):
        file_id = event['file_id']
        user_id = event['user_id']
        channel_id = event.get('channel_id')

        # Get file info
        file_info = client.files_info(file=file_id)
        file_data = file_info['file']

        # Check if CSV
        if not file_data['name'].endswith('.csv'):
            say("⚠️ Please upload a CSV file containing keywords.")
            return

        try:
            # Download and parse
            parser = KeywordParser()
            keywords = parser.parse_csv_from_url(
                file_data['url_private'],
                Config.SLACK_BOT_TOKEN
            )

            if len(keywords) == 0:
                say("⚠️ No keywords found in the file.\n\n"
                          "Please ensure your CSV has a 'keyword' column.")
                return

            # Acknowledge
            say(f"✅ File Received: *{file_data['name']}*\n\n"
                      f"📊 Found {len(keywords)} keywords\n"
                      f"🔄 Processing started...")

            # Start processing
            pipeline = ProcessingPipeline(say, channel_id, user_id)
            pipeline.start_from_keywords(keywords, source='csv')

        except Exception as e:
            say(f"❌ Error processing file: {str(e)}\n\n"
                      f"Please check the file format and try again.")

    @app.event("message")
    def handle_message(event, say):
        # Skip bot messages
        if event.get('bot_id'):
            return

        user_id = event['user']
        channel_id = event['channel']
        text = event.get('text', '').strip()

        # Check if user is awaiting input
        if redis_client:
            state_key = f"user:{user_id}:state"
            state_data = redis_client.get(state_key)

            if state_data:
                state = json.loads(state_data)

                if state.get('status') == 'awaiting_input':
                    # Parse keywords from message
                    parser = KeywordParser()
                    keywords = parser.parse_text(text)

                    if len(keywords) < 1:
                        say("⚠️ No keywords detected. Please provide at least one keyword.")
                        return

                    # Clear state
                    redis_client.delete(state_key)

                    # Acknowledge
                    say(f"✅ Received {len(keywords)} keywords!\n"
                              f"🔄 Processing started...")

                    # Start processing
                    # pipeline = ProcessingPipeline(say, channel_id, user_id)
                    # pipeline.start_from_keywords(keywords, source='text')