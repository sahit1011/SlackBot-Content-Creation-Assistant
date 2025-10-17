import redis
import json
import re
import threading
from app.config import Config
from app.services.processing.keyword_parser import KeywordParser
from app.services.processing.pipeline import ProcessingPipeline

redis_client = redis.from_url(Config.REDIS_URL) if Config.REDIS_URL else None

def register(app):
    """Register all command handlers"""
    
    @app.command("/process_keywords")
    def handle_process_keywords(ack, body, client):
        ack()
        
        user_id = body['user_id']
        channel_id = body['channel_id']
        text = body.get('text', '').strip()
        
        if text:
            # Process immediately
            parser = KeywordParser()
            keywords = parser.parse_text(text)
            
            client.chat_postMessage(
                channel=channel_id,
                text=f"🚀 Processing {len(keywords)} keywords...\n\nI'll update you when complete!"
            )
            
            # Start pipeline
            pipeline = ProcessingPipeline(client, channel_id, user_id)
            pipeline.start_from_keywords(keywords, source='text')
        else:
            # Set state and wait for input
            client.chat_postMessage(
                channel=channel_id,
                text="🚀 *Keyword Processing Initiated!*\n\n"
                     "Please provide keywords:\n\n"
                     "📁 *Upload a CSV file*\n"
                     "The CSV should have a 'keyword' column.\n\n"
                     "✍️ *Paste keywords*\n"
                     "Reply with keywords separated by commas.\n\n"
                     "Example: `running shoes, yoga mats, protein powder`"
            )
            
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
    def handle_history(ack, body, client):
        ack()

        slack_user_id = body['user_id']
        channel_id = body['channel_id']

        from app.services.data.database import DatabaseService
        db = DatabaseService()

        # Get or create user to ensure we have the UUID
        user = db.get_or_create_user(slack_user_id)
        user_id = user['id']

        history = db.get_user_history(user_id, limit=5)
        
        if not history:
            client.chat_postMessage(
                channel=channel_id,
                text="📊 No processing history found.\n\nUse `/process_keywords` to get started!"
            )
            return
        
        # Format history with enhanced details
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "📊 Your Processing History"}},
            {"type": "divider"}
        ]
        
        for batch in history:
            # Get cluster count for this batch
            clusters = db.get_clusters_by_batch(batch['id'])
            cluster_count = len(clusters) if clusters else 0
            
            # Get report info
            try:
                report_info = db.client.table('reports').select('*').eq('batch_id', batch['id']).execute()
                has_report = bool(report_info.data)
            except:
                has_report = False
            
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
                    {"type": "mrkdwn", "text": f"*Keywords:* {batch.get('keyword_count', 0)}"},
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
        completed_batches = sum(1 for b in history if b.get('status') == 'completed')
        total_keywords = sum(b.get('keyword_count', 0) for b in history)
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Summary:* {total_batches} batches, {completed_batches} completed, {total_keywords} total keywords processed"
            }
        })
        
        client.chat_postMessage(channel=channel_id, blocks=blocks)

    @app.action(re.compile(r"regenerate_.*"))
    def handle_regenerate_action(ack, body, client):
        ack()

        action_id = body['actions'][0]['action_id']
        batch_id = body['actions'][0]['value']
        slack_user_id = body['user']['id']
        channel_id = body['container']['channel_id']

        from app.services.data.database import DatabaseService
        db = DatabaseService()

        # Get or create user to ensure we have the UUID
        user = db.get_or_create_user(slack_user_id)
        user_id = user['id']

        # Verify batch exists and belongs to user
        batch = db.get_batch_by_id(batch_id)
        if not batch or str(batch.get('user_id', '')) != str(user_id):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Batch not found or access denied."
            )
            return

        if batch.get('status') != 'completed':
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Batch is not completed yet. Please wait for processing to finish."
            )
            return

        # Get all clusters for this batch
        clusters = db.get_clusters_by_batch(batch_id)

        if not clusters:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No clusters found for this batch."
            )
            return

        # Regenerate all clusters
        client.chat_postMessage(
            channel=channel_id,
            text=f"♻️ Regenerating all outlines for batch `{batch_id[:8]}`..."
        )

        # Start regeneration in background
        thread = threading.Thread(
            target=regenerate_outlines,
            args=(client, channel_id, user_id, batch_id, clusters)
        )
        thread.daemon = True
        thread.start()

    @app.action(re.compile(r"details_.*"))
    def handle_details_action(ack, body, client):
        ack()

        action_id = body['actions'][0]['action_id']
        batch_id = body['actions'][0]['value']
        slack_user_id = body['user']['id']
        channel_id = body['container']['channel_id']

        from app.services.data.database import DatabaseService
        from app.utils.slack_formatters import SlackFormatter

        db = DatabaseService()
        formatter = SlackFormatter()

        # Get or create user to ensure we have the UUID
        user = db.get_or_create_user(slack_user_id)
        user_id = user['id']

        # Verify batch exists and belongs to user
        batch = db.get_batch_by_id(batch_id)
        if not batch or str(batch.get('user_id', '')) != str(user_id):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Batch not found or access denied."
            )
            return

        # Get clusters for this batch
        clusters = db.get_clusters_by_batch(batch_id)

        if not clusters:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No clusters found for this batch."
            )
            return

        # Format detailed view
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": f"📋 Batch Details: {batch_id[:8]}"}},
            {"type": "divider"}
        ]

        # Batch info
        blocks.append({
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Batch ID:* `{batch_id}`"},
                {"type": "mrkdwn", "text": f"*Created:* {batch['created_at'][:10]}"},
                {"type": "mrkdwn", "text": f"*Keywords:* {batch.get('keyword_count', 0)}"},
                {"type": "mrkdwn", "text": f"*Status:* {batch['status']}"}
            ]
        })

        blocks.append({"type": "divider"})

        # Clusters
        for cluster in clusters:
            cluster_name = cluster.get('cluster_name', 'Unnamed Cluster')
            keywords = cluster.get('keywords', [])
            outline = cluster.get('outline_json', {})
            post_idea = cluster.get('post_idea_metadata', {})

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Cluster {cluster.get('cluster_number', '?')}: {cluster_name}*\n"
                           f"Keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}\n"
                           f"Post Idea: {post_idea.get('title', 'N/A')}"
                }
            })

            # Add outline sections if available
            if outline.get('sections'):
                sections = outline['sections']
                if isinstance(sections, list) and sections:
                    # sections_text = "\n".join([f"• {s.get('title', 'Untitled')}" for s in sections[:3]])
                    sections_text = "\n".join([
    f"• {s.get('title') or s.get('heading') or s.get('content', '')[:40] or 'No title'}"
    for s in sections[:3]
])
                    if len(sections) > 3:
                        sections_text += f"\n• ... and {len(sections) - 3} more sections"

                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Outline Sections:*\n{sections_text}"
                        }
                    })

            blocks.append({"type": "divider"})

        client.chat_postMessage(channel=channel_id, blocks=blocks)

    @app.command("/regenerate")
    def handle_regenerate(ack, body, client):
        ack()
        
        user_id = body['user_id']
        channel_id = body['channel_id']
        text = body.get('text', '').strip()
        
        if not text:
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Please provide a batch ID and optional cluster number.\n\n"
                     "Usage:\n"
                     "`/regenerate <batch_id>` - Regenerate all outlines\n"
                     "`/regenerate <batch_id> <cluster_number>` - Regenerate specific cluster\n\n"
                     "Example: `/regenerate abc12345` or `/regenerate abc12345 2`"
            )
            return
        
        parts = text.split()
        batch_id = parts[0]
        cluster_number = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
        
        from app.services.data.database import DatabaseService
        db = DatabaseService()
        
        # Verify batch exists and belongs to user
        batch = db.get_batch_by_id(batch_id)
        if not batch or str(batch.get('user_id', '')) != str(user_id):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Batch not found or access denied."
            )
            return
        
        if batch.get('status') != 'completed':
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Batch is not completed yet. Please wait for processing to finish."
            )
            return
        
        # Get clusters for this batch
        clusters = db.get_clusters_by_batch(batch_id)
        
        if not clusters:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No clusters found for this batch."
            )
            return
        
        if cluster_number:
            # Regenerate specific cluster
            target_clusters = [c for c in clusters if c.get('cluster_number') == cluster_number]
            if not target_clusters:
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"❌ Cluster {cluster_number} not found in batch {batch_id}"
                )
                return
            clusters = target_clusters
            client.chat_postMessage(
                channel=channel_id,
                text=f"♻️ Regenerating outline for cluster {cluster_number} in batch `{batch_id[:8]}`..."
            )
        else:
            # Regenerate all clusters
            client.chat_postMessage(
                channel=channel_id,
                text=f"♻️ Regenerating all outlines for batch `{batch_id[:8]}`..."
            )
        
        # Start regeneration in background
        thread = threading.Thread(
            target=regenerate_outlines,
            args=(client, channel_id, user_id, batch_id, clusters)
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
                cluster_name = cluster.get('cluster_name', 'Unnamed Cluster')
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"🔄 Regenerating outline for cluster: {cluster_name}"
                )
                
                # Re-search and scrape content
                keywords = cluster.get('keywords', [])
                main_keyword = keywords[0] if keywords else cluster_name.split()[0]
                search_results = search_service.search_single(main_keyword, count=5)
                
                urls = [r['url'] for r in search_results[:3]]
                scraped_data = scraper.scrape_urls(urls)
                
                # Generate new outline
                new_outline = outline_gen.generate_outline(cluster, scraped_data)
                
                # Generate new post idea
                new_idea = idea_gen.generate_idea(cluster, new_outline)
                
                # Update database
                db.update_cluster_outline(batch_id, cluster.get('cluster_id', cluster.get('id')), new_outline, new_idea)
                
                # Send updated results
                detail_blocks = formatter.format_cluster_detail(
                    {
                        'cluster_name': cluster_name,
                        'keywords': keywords,
                        'keyword_count': len(keywords),
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
    def handle_set_email(ack, body, client):
        ack()
        
        user_id = body['user_id']
        channel_id = body['channel_id']
        email = body.get('text', '').strip()
        
        if not email:
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Please provide an email address.\n\nUsage: `/set_email your.email@example.com`"
            )
            return
        
        # Basic email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Invalid email format. Please provide a valid email address."
            )
            return
        
        from app.services.data.database import DatabaseService
        db = DatabaseService()
        
        try:
            # Get or create user
            user = db.get_or_create_user(user_id)
            
            # Update email
            db.client.table('users').update({'email': email}).eq('id', user['id']).execute()
            
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Email address set to: `{email}`\n\nYou'll now receive PDF reports via email after processing is complete!"
            )
        except Exception as e:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Failed to set email: {str(e)}"
            )
    
    @app.command("/export")
    def handle_export(ack, body, client):
        ack()
        
        user_id = body['user_id']
        channel_id = body['channel_id']
        text = body.get('text', '').strip()
        
        if not text:
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Please specify export destination.\n\n"
                     "Usage:\n"
                     "`/export notion <batch_id>` - Export to Notion\n"
                     "`/export sheets <batch_id>` - Export to Google Sheets\n\n"
                     "Example: `/export notion abc12345`"
            )
            return
        
        parts = text.split()
        if len(parts) != 2:
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Invalid format. Use: `/export <destination> <batch_id>`"
            )
            return
        
        destination, batch_id = parts
        
        if destination not in ['notion', 'sheets']:
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Invalid destination. Choose 'notion' or 'sheets'."
            )
            return
        
        from app.services.data.database import DatabaseService
        db = DatabaseService()
        
        # Verify batch exists and belongs to user
        batch = db.get_batch_by_id(batch_id)
        if not batch or str(batch.get('user_id', '')) != str(user_id):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Batch not found or access denied."
            )
            return
        
        if batch.get('status') != 'completed':
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Batch is not completed yet. Please wait for processing to finish."
            )
            return
        
        # Start export in background
        thread = threading.Thread(
            target=export_batch,
            args=(client, channel_id, batch_id, destination)
        )
        thread.daemon = True
        thread.start()
        
        client.chat_postMessage(
            channel=channel_id,
            text=f"📤 Starting export to {destination.title()} for batch `{batch_id[:8]}`..."
        )
    
    def export_batch(client, channel_id, batch_id, destination):
        """Export batch data to external service"""
        try:
            from app.services.data.database import DatabaseService
            
            db = DatabaseService()
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
                         f"📊 Exported {len(clusters) if clusters else 0} clusters to Notion"
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
                         f"📈 Created spreadsheet with {len(clusters) if clusters else 0} cluster worksheets"
                )
        
        except Exception as e:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Export failed: {str(e)}"
            )