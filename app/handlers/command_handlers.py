import redis
import json
from app.config import Config
from app.services.processing.keyword_parser import KeywordParser
from app.services.processing.pipeline import ProcessingPipeline

redis_client = redis.from_url(Config.REDIS_URL) if Config.REDIS_URL else None

def register(app):
    """Register all command handlers"""

    @app.command("/process_keywords")
    def handle_process_keywords(ack, body, say):
        ack()

        user_id = body['user_id']
        channel_id = body['channel_id']
        text = body.get('text', '').strip()

        if text:
            # Process immediately
            parser = KeywordParser()
            keywords = parser.parse_text(text)

            say(f"🚀 Processing {len(keywords)} keywords...\n\nI'll update you when complete!")

            # Start pipeline
            pipeline = ProcessingPipeline(app.client, channel_id, user_id)
            pipeline.start_from_keywords(keywords, source='text')
        else:
            # Set state and wait for input
            say("🚀 *Keyword Processing Initiated!*\n\n"
                      "Please provide keywords:\n\n"
                      "📁 *Upload a CSV file*\n"
                      "The CSV should have a 'keyword' column.\n\n"
                      "✍️ *Paste keywords*\n"
                      "Reply with keywords separated by commas.\n\n"
                      "Example: `running shoes, yoga mats, protein powder`")

            if redis_client:
                redis_client.setex(
                    f"user:{user_id}:state",
                    3600,
                    json.dumps({
                        "status": "awaiting_input",
                        "channel_id": channel_id
                    })
                )

    @app.command("/history")
    def handle_history(ack, body, say):
        ack()

        user_id = body['user_id']

        from app.services.data.database import DatabaseService
        db = DatabaseService()

        history = db.get_user_history(user_id, limit=5)

        if not history:
            say("📊 No processing history found.\n\nUse `/process_keywords` to get started!")
            return

        # Format history
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "📊 Your Processing History"}},
            {"type": "divider"}
        ]

        for batch in history:
            blocks.append({
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Batch:* {batch['id'][:8]}..."},
                    {"type": "mrkdwn", "text": f"*Date:* {batch['created_at'][:10]}"},
                    {"type": "mrkdwn", "text": f"*Keywords:* {batch['keyword_count']}"},
                    {"type": "mrkdwn", "text": f"*Status:* {batch['status']}"}
                ]
            })
            blocks.append({"type": "divider"})

        say(blocks=blocks)

    @app.command("/regenerate")
    def handle_regenerate(ack, body, say):
        ack()

        batch_id = body.get('text', '').strip()

        if not batch_id:
            say("⚠️ Please provide a batch ID.\n\nUsage: `/regenerate <batch_id>`")
            return

        say(f"♻️ Regenerating outlines for batch `{batch_id}`...")

        # TODO: Implement regeneration logic

    @app.command("/set_email")
    def handle_set_email(ack, body, say):
        ack()

        user_id = body['user_id']
        email = body.get('text', '').strip()

        if not email:
            say("⚠️ Please provide an email address.\n\nUsage: `/set_email your.email@example.com`")
            return

        # Basic email validation
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            say("⚠️ Invalid email format. Please provide a valid email address.")
            return

        from app.services.data.database import DatabaseService
        db = DatabaseService()

        # Get or create user
        user = db.get_or_create_user(user_id)

        # Update email
        db.client.table('users').update({'email': email}).eq('id', user['id']).execute()

        say(f"✅ Email address set to: `{email}`\n\nYou'll now receive PDF reports via email after processing is complete!")