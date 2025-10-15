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

        # Format history with enhanced details
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "📊 Your Processing History"}},
            {"type": "divider"}
        ]

        for batch in history:
            # Get cluster count for this batch
            clusters = db.get_clusters_by_batch(batch['id'])
            cluster_count = len(clusters)

            # Get report info
            report_info = db.client.table('reports').select('*').eq('batch_id', batch['id']).execute()
            has_report = bool(report_info.data)

            status_emoji = {
                'completed': '✅',
                'processing': '🔄',
                'failed': '❌'
            }.get(batch['status'], '❓')

            blocks.append({
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Batch:* `{batch['id'][:8]}`"},
                    {"type": "mrkdwn", "text": f"*Date:* {batch['created_at'][:10]}"},
                    {"type": "mrkdwn", "text": f"*Keywords:* {batch['keyword_count']}"},
                    {"type": "mrkdwn", "text": f"*Clusters:* {cluster_count}"},
                    {"type": "mrkdwn", "text": f"*Status:* {status_emoji} {batch['status']}"},
                    {"type": "mrkdwn", "text": f"*Report:* {'📄 Available' if has_report else 'Not generated'}"}
                ]
            })

            # Add action buttons for completed batches
            if batch['status'] == 'completed':
                blocks.append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "🔄 Regenerate"},
                            "action_id": f"regenerate_{batch['id'][:8]}",
                            "value": batch['id']
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "📋 View Details"},
                            "action_id": f"details_{batch['id'][:8]}",
                            "value": batch['id']
                        }
                    ]
                })

            blocks.append({"type": "divider"})

        # Add summary
        total_batches = len(history)
        completed_batches = sum(1 for b in history if b['status'] == 'completed')
        total_keywords = sum(b['keyword_count'] for b in history)

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Summary:* {total_batches} batches, {completed_batches} completed, {total_keywords} total keywords processed"
            }
        })

        say(blocks=blocks)

    @app.command("/regenerate")
    def handle_regenerate(ack, body, say):
        ack()

        user_id = body['user_id']
        channel_id = body['channel_id']
        text = body.get('text', '').strip()

        if not text:
            say("⚠️ Please provide a batch ID and optional cluster number.\n\n"
                "Usage:\n"
                "`/regenerate <batch_id>` - Regenerate all outlines\n"
                "`/regenerate <batch_id> <cluster_number>` - Regenerate specific cluster\n\n"
                "Example: `/regenerate abc12345` or `/regenerate abc12345 2`")
            return

        parts = text.split()
        batch_id = parts[0]
        cluster_number = int(parts[1]) if len(parts) > 1 else None

        from app.services.data.database import DatabaseService
        db = DatabaseService()

        # Verify batch exists and belongs to user
        batch = db.get_batch_by_id(batch_id)
        if not batch or str(batch['user_id']) != str(user_id):
            say("❌ Batch not found or access denied.")
            return

        if batch['status'] != 'completed':
            say("⚠️ Batch is not completed yet. Please wait for processing to finish.")
            return

        # Get clusters for this batch
        clusters = db.get_clusters_by_batch(batch_id)

        if cluster_number:
            # Regenerate specific cluster
            target_clusters = [c for c in clusters if c['cluster_number'] == cluster_number]
            if not target_clusters:
                say(f"❌ Cluster {cluster_number} not found in batch {batch_id}")
                return
            clusters = target_clusters
            say(f"♻️ Regenerating outline for cluster {cluster_number} in batch `{batch_id[:8]}`...")
        else:
            # Regenerate all clusters
            say(f"♻️ Regenerating all outlines for batch `{batch_id[:8]}`...")

        # Start regeneration in background
        import threading
        thread = threading.Thread(
            target=regenerate_outlines,
            args=(app.client, channel_id, user_id, batch_id, clusters)
        )
        thread.daemon = True
        thread.start()

def regenerate_outlines(client, channel_id, user_id, batch_id, clusters):
    """Regenerate outlines for specified clusters"""
    try:
        from app.services.external.web_search import WebSearchService
        from app.services.processing.content_scraper import ContentScraper
        from app.services.ai.outline_generator import OutlineGenerator
        from app.services.ai.idea_generator import IdeaGenerator
        from app.services.data.database import DatabaseService
        from app.utils.slack_formatters import SlackFormatter

        db = DatabaseService()
        formatter = SlackFormatter()

        search_service = WebSearchService()
        scraper = ContentScraper()
        outline_gen = OutlineGenerator()
        idea_gen = IdeaGenerator()

        for cluster in clusters:
            cluster_name = cluster['cluster_name']
            client.chat_postMessage(
                channel=channel_id,
                text=f"🔄 Regenerating outline for cluster: {cluster_name}"
            )

            # Re-search and scrape content
            main_keyword = cluster['keywords'][0] if cluster['keywords'] else cluster_name.split()[0]
            search_results = search_service.search_single(main_keyword, count=5)

            urls = [r['url'] for r in search_results[:3]]
            scraped_data = scraper.scrape_urls(urls)

            # Generate new outline
            new_outline = outline_gen.generate_outline(cluster, scraped_data)

            # Generate new post idea
            new_idea = idea_gen.generate_idea(cluster, new_outline)

            # Update database
            db.update_cluster_outline(batch_id, cluster['cluster_id'], new_outline, new_idea)

            # Send updated results
            detail_blocks = formatter.format_cluster_detail(
                {
                    'cluster_name': cluster_name,
                    'keywords': cluster['keywords'],
                    'outline': new_outline,
                    'post_idea': new_idea
                },
                new_idea,
                new_outline
            )

            client.chat_postMessage(
                channel=channel_id,
                blocks=detail_blocks
            )

        client.chat_postMessage(
            channel=channel_id,
            text="✅ Outline regeneration complete!"
        )

    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Error during regeneration: {str(e)}"
        )

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

    @app.command("/export")
    def handle_export(ack, body, say):
        ack()

        user_id = body['user_id']
        text = body.get('text', '').strip()

        if not text:
            say("⚠️ Please specify export destination.\n\n"
                "Usage:\n"
                "`/export notion <batch_id>` - Export to Notion\n"
                "`/export sheets <batch_id>` - Export to Google Sheets\n\n"
                "Example: `/export notion abc12345`")
            return

        parts = text.split()
        if len(parts) != 2:
            say("⚠️ Invalid format. Use: `/export <destination> <batch_id>`")
            return

        destination, batch_id = parts

        if destination not in ['notion', 'sheets']:
            say("⚠️ Invalid destination. Choose 'notion' or 'sheets'.")
            return

        from app.services.data.database import DatabaseService
        db = DatabaseService()

        # Verify batch exists and belongs to user
        batch = db.get_batch_by_id(batch_id)
        if not batch or str(batch['user_id']) != str(user_id):
            say("❌ Batch not found or access denied.")
            return

        if batch['status'] != 'completed':
            say("⚠️ Batch is not completed yet. Please wait for processing to finish.")
            return

        # Start export in background
        import threading
        thread = threading.Thread(
            target=export_batch,
            args=(app.client, body['channel_id'], batch_id, destination)
        )
        thread.daemon = True
        thread.start()

        say(f"📤 Starting export to {destination.title()} for batch `{batch_id[:8]}`...")

def export_batch(client, channel_id, batch_id, destination):
    """Export batch data to external service"""
    try:
        from app.services.data.database import DatabaseService

        db = DatabaseService()
        batch = db.get_batch_by_id(batch_id)
        clusters = db.get_clusters_by_batch(batch_id)

        if destination == 'notion':
            # Mock Notion export (would need Notion API integration)
            client.chat_postMessage(
                channel=channel_id,
                text="📝 *Notion Export Feature*\n\n"
                     "Notion integration would create a new page with:\n"
                     "• Batch summary and metadata\n"
                     "• All keyword clusters as sections\n"
                     "• Generated outlines and post ideas\n"
                     "• Links to PDF reports\n\n"
                     f"✅ Mock export completed for batch `{batch_id[:8]}`\n"
                     f"📊 Exported {len(clusters)} clusters to Notion"
            )

        elif destination == 'sheets':
            # Mock Google Sheets export
            client.chat_postMessage(
                channel=channel_id,
                text="📊 *Google Sheets Export Feature*\n\n"
                     "Google Sheets integration would create:\n"
                     "• Summary sheet with batch info\n"
                     "• Clusters sheet with all groupings\n"
                     "• Outlines sheet with content structure\n"
                     "• Ideas sheet with post suggestions\n\n"
                     f"✅ Mock export completed for batch `{batch_id[:8]}`\n"
                     f"📈 Created spreadsheet with {len(clusters)} cluster worksheets"
            )

    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Export failed: {str(e)}"
        )