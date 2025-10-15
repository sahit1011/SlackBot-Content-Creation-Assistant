
# EPIC-004: Slack Bot Integration

**Priority:** P0 (Critical Path)  
**Story Points:** 13  
**Duration:** 1 Day  
**Owner:** Developer  

---

## SLACK-014: Build Slack Bot Framework

**Type:** Feature  
**Priority:** Critical  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Set up the foundational Slack bot application using Bolt framework to handle all Slack events and commands.

**Acceptance Criteria:**
- [ ] Slack bot connects successfully to workspace
- [ ] Bot appears online and responds to @mentions
- [ ] Health check endpoint responds
- [ ] Structured logging configured
- [ ] Graceful error handling implemented

**Deliverables:**
- `app/main.py`
- `app/handlers/__init__.py`

**Dependencies:** SLACK-001, SLACK-003, SLACK-005

**Code Implementation:**

```python
# app/main.py
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from app.config import Config

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)

from app.handlers import command_handlers, event_handlers

command_handlers.register(app)
event_handlers.register(app)

@app.event("app_mention")
def handle_app_mention(event, say):
    say(f"👋 Hi <@{event['user']}>! I'm ready to help with keyword processing.\n\n"
        f"Try:\n• `/process_keywords` - Start processing\n• `/history` - View past batches")

def main():
    logger.info("Starting Slackbot Content Assistant...")
    handler = SocketModeHandler(app, Config.SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    main()
```

```python
# app/handlers/__init__.py
# Empty init file for handlers package
```

**Testing:**
- Mention bot in Slack channel
- Verify greeting response appears
- Check logs for events

---

## SLACK-015: Implement /process_keywords Command

**Type:** Feature  
**Priority:** Critical  
**Story Points:** 4  
**Estimated Time:** 3 hours  

**Description:**
Implement the main slash command that initiates keyword processing workflow.

**Acceptance Criteria:**
- [ ] Command responds within 2 seconds
- [ ] Handles text input: `/process_keywords keyword1, keyword2`
- [ ] Handles empty input and prompts for action
- [ ] Sets user state in Redis
- [ ] Triggers processing pipeline for text input
- [ ] Supports concurrent users

**Deliverables:**
- `app/handlers/command_handlers.py`

**Dependencies:** SLACK-014, SLACK-006

**Code Implementation:**

```python
# app/handlers/command_handlers.py
import redis
import json
from app.config import Config
from app.services.keyword_parser import KeywordParser
from app.services.pipeline import ProcessingPipeline

redis_client = redis.from_url(Config.REDIS_URL) if Config.REDIS_URL else None

def register(app):
    """Register all command handlers"""
    
    @app.command("/process_keywords")
    def handle_process_keywords(ack, command, client):
        ack()
        
        user_id = command['user_id']
        channel_id = command['channel_id']
        text = command.get('text', '').strip()
        
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
    def handle_history(ack, command, client):
        ack()
        
        user_id = command['user_id']
        channel_id = command['channel_id']
        
        from app.services.database import DatabaseService
        db = DatabaseService()
        
        history = db.get_user_history(user_id, limit=5)
        
        if not history:
            client.chat_postMessage(
                channel=channel_id,
                text="📊 No processing history found.\n\nUse `/process_keywords` to get started!"
            )
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
        
        client.chat_postMessage(channel=channel_id, blocks=blocks)
    
    @app.command("/regenerate")
    def handle_regenerate(ack, command, client):
        ack()
        
        batch_id = command.get('text', '').strip()
        channel_id = command['channel_id']
        
        if not batch_id:
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Please provide a batch ID.\n\nUsage: `/regenerate <batch_id>`"
            )
            return
        
        client.chat_postMessage(
            channel=channel_id,
            text=f"♻️ Regenerating outlines for batch `{batch_id}`..."
        )
        
        # TODO: Implement regeneration logic
```

**Testing:**
- Run `/process_keywords` in Slack
- Test with keyword input
- Verify Redis state saved
- Check history command

---

## SLACK-016: Implement File Upload Handler

**Type:** Feature  
**Priority:** Critical  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Handle CSV file uploads from users and automatically trigger processing.

**Acceptance Criteria:**
- [ ] Detects CSV file uploads
- [ ] Downloads and parses CSV files
- [ ] Validates file contents
- [ ] Triggers processing pipeline automatically
- [ ] Handles non-CSV files with error messages
- [ ] Supports files up to 10MB

**Deliverables:**
- `app/handlers/event_handlers.py`

**Dependencies:** SLACK-014, SLACK-006

**Code Implementation:**

```python
# app/handlers/event_handlers.py
import redis
import json
from app.config import Config
from app.services.keyword_parser import KeywordParser
from app.services.pipeline import ProcessingPipeline

redis_client = redis.from_url(Config.REDIS_URL) if Config.REDIS_URL else None

def register(app):
    """Register all event handlers"""
    
    @app.event("file_shared")
    def handle_file_upload(event, client):
        file_id = event['file_id']
        user_id = event['user_id']
        channel_id = event.get('channel_id')
        
        # Get file info
        file_info = client.files_info(file=file_id)
        file_data = file_info['file']
        
        # Check if CSV
        if not file_data['name'].endswith('.csv'):
            client.chat_postMessage(
                channel=channel_id,
                text="⚠️ Please upload a CSV file containing keywords."
            )
            return
        
        try:
            # Download and parse
            parser = KeywordParser()
            keywords = parser.parse_csv_from_url(
                file_data['url_private'],
                Config.SLACK_BOT_TOKEN
            )
            
            if len(keywords) == 0:
                client.chat_postMessage(
                    channel=channel_id,
                    text="⚠️ No keywords found in the file.\n\n"
                         "Please ensure your CSV has a 'keyword' column."
                )
                return
            
            # Acknowledge
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ File Received: *{file_data['name']}*\n\n"
                     f"📊 Found {len(keywords)} keywords\n"
                     f"🔄 Processing started..."
            )
            
            # Start processing
            pipeline = ProcessingPipeline(client, channel_id, user_id)
            pipeline.start_from_keywords(keywords, source='csv')
            
        except Exception as e:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Error processing file: {str(e)}\n\n"
                     f"Please check the file format and try again."
            )
    
    @app.event("message")
    def handle_message(event, client):
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
                        client.chat_postMessage(
                            channel=channel_id,
                            text="⚠️ No keywords detected. Please provide at least one keyword."
                        )
                        return
                    
                    # Clear state
                    redis_client.delete(state_key)
                    
                    # Acknowledge
                    client.chat_postMessage(
                        channel=channel_id,
                        text=f"✅ Received {len(keywords)} keywords!\n"
                             f"🔄 Processing started..."
                    )
                    
                    # Start processing
                    pipeline = ProcessingPipeline(client, channel_id, user_id)
                    pipeline.start_from_keywords(keywords, source='text')
```

**Testing:**
- Upload CSV file in Slack
- Upload non-CSV file (should error)
- Paste keywords after /process_keywords
- Test with empty CSV

---

## SLACK-017: Build Message Formatters

**Type:** Feature  
**Priority:** High  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Create message formatting utilities for beautiful Slack messages using Blocks API.

**Acceptance Criteria:**
- [ ] Format progress updates clearly
- [ ] Format cluster summaries with proper structure
- [ ] Format detailed cluster information
- [ ] Format completion summaries
- [ ] Format error messages helpfully
- [ ] All messages mobile-friendly

**Deliverables:**
- `app/utils/slack_formatters.py`

**Dependencies:** SLACK-014

**Code Implementation:**

```python
# app/utils/slack_formatters.py
from typing import List, Dict

class SlackFormatter:
    """Format messages for Slack display"""
    
    @staticmethod
    def format_progress(message: str, emoji: str = "⏳") -> str:
        """Format simple progress message"""
        return f"{emoji} {message}"
    
    @staticmethod
    def format_clusters_summary(clusters: List[Dict]) -> List[Dict]:
        """Format clusters as Slack blocks"""
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "🎯 Keyword Clusters"}},
            {"type": "divider"}
        ]
        
        for cluster in clusters:
            keywords_display = cluster['keywords'][:5]
            if len(cluster['keywords']) > 5:
                keywords_display.append(f"... +{len(cluster['keywords']) - 5} more")
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📁 Cluster {cluster['cluster_number']}: {cluster['cluster_name']}*\n"
                           f"📊 {cluster['keyword_count']} keywords\n"
                           f"Keywords: {', '.join(f'`{k}`' for k in keywords_display)}"
                }
            })
            blocks.append({"type": "divider"})
        
        return blocks
    
    @staticmethod
    def format_cluster_detail(cluster: Dict, post_idea: Dict, outline: Dict) -> List[Dict]:
        """Format detailed cluster information"""
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": f"📁 {cluster['cluster_name']}"}},
            {"type": "divider"}
        ]
        
        # Keywords section
        keywords_text = "\n".join(f"• {k}" for k in cluster['keywords'][:10])
        if len(cluster['keywords']) > 10:
            keywords_text += f"\n... and {len(cluster['keywords']) - 10} more"
        
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Keywords ({cluster['keyword_count']}):*\n{keywords_text}"}
        })
        
        # Post idea section
        if post_idea:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💡 Post Idea*\n\n"
                           f"*Title:* {post_idea.get('title', 'N/A')}\n"
                           f"*Angle:* {post_idea.get('angle', 'N/A')}\n"
                           f"*Target Audience:* {post_idea.get('target_audience', 'N/A')}"
                }
            })
        
        # Outline section
        if outline:
            blocks.append({"type": "divider"})
            outline_text = f"*📝 Suggested Outline*\n\n*{outline.get('title', 'Content Outline')}*\n\n"
            
            for i, section in enumerate(outline.get('sections', [])[:5], 1):
                outline_text += f"{i}. {section.get('heading', 'Section')}\n"
            
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": outline_text}
            })
        
        return blocks
    
    @staticmethod
    def format_completion_summary(stats: Dict) -> List[Dict]:
        """Format processing completion summary"""
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "✅ Processing Complete!"}},
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Keywords Processed:*\n{stats.get('keyword_count', 0)}"},
                    {"type": "mrkdwn", "text": f"*Clusters Created:*\n{stats.get('cluster_count', 0)}"},
                    {"type": "mrkdwn", "text": f"*Outlines Generated:*\n{stats.get('outline_count', 0)}"},
                    {"type": "mrkdwn", "text": f"*Post Ideas:*\n{stats.get('idea_count', 0)}"}
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "📄 *Your report is ready!*\nDownload the PDF below."}
            }
        ]
        
        return blocks
    
    @staticmethod
    def format_error(error_msg: str, suggestion: str = None, batch_id: str = None) -> List[Dict]:
        """Format error message"""
        error_text = f"❌ *Error*\n\n{error_msg}"
        
        if suggestion:
            error_text += f"\n\n*Suggestion:* {suggestion}"
        
        if batch_id:
            error_text += f"\n\n*Batch ID:* `{batch_id}`"
        
        blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": error_text}}
        ]
        
        return blocks
```

**Testing:**
- Create sample data
- Format each message type
- Send to Slack test channel
- Verify mobile display
- Test edge cases (long text, special chars)

---

## Epic Completion Checklist

**All Tasks Complete:**
- [ ] SLACK-014: Bot framework
- [ ] SLACK-015: /process_keywords command
- [ ] SLACK-016: File upload handler
- [ ] SLACK-017: Message formatters

**Integration Tests:**
- [ ] Bot connects and responds
- [ ] Commands work end-to-end
- [ ] File uploads process correctly
- [ ] Messages display beautifully
- [ ] Error handling works

**Ready for Next Epic:**
- [ ] No blocking bugs
- [ ] Code committed to Git
- [ ] Tests passing