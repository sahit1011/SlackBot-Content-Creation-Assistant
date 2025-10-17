# EPIC-008: Bonus Features & Enhancements

**Priority:** P1 (Nice to Have)  
**Story Points:** 10  
**Duration:** 1 Day  
**Owner:** Developer  

---

## SLACK-028: Implement /regenerate Command

**Type:** Feature  
**Priority:** Medium  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Allow users to regenerate outlines and post ideas for existing batches without re-uploading keywords.

**Acceptance Criteria:**
- [ ] Regenerate all clusters in a batch
- [ ] Regenerate specific cluster by number
- [ ] Validates batch ownership
- [ ] Uses fresh search results
- [ ] Updates database with new content
- [ ] Posts updated results to Slack

**Deliverables:**
- Already implemented in `command_handlers.py`
- `DatabaseService.update_cluster_outline()` method

**Dependencies:** SLACK-018, SLACK-019

**Code Implementation:**

```python
# Add to app/services/data/database.py

def update_cluster_outline(self, batch_id: str, cluster_id: str, outline: Dict, post_idea: Dict):
    """Update cluster outline and post idea"""
    try:
        self.client.table('keyword_clusters').update({
            'outline_json': outline,
            'post_idea': post_idea.get('title', ''),
            'post_idea_metadata': post_idea
        }).eq('batch_id', batch_id).eq('id', cluster_id).execute()
        
        return True
    except Exception as e:
        print(f"Error updating cluster: {str(e)}")
        return False

def get_clusters_by_batch(self, batch_id: str) -> List[Dict]:
    """Get all clusters for a batch"""
    try:
        response = self.client.table('keyword_clusters')\
            .select('*')\
            .eq('batch_id', batch_id)\
            .order('cluster_number')\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching clusters: {str(e)}")
        return []

def get_batch_by_id(self, batch_id: str) -> Optional[Dict]:
    """Get batch by ID with fuzzy matching"""
    try:
        # Try exact match first
        response = self.client.table('keyword_batches')\
            .select('*')\
            .eq('id', batch_id)\
            .execute()
        
        if response.data:
            return response.data[0]
        
        # Try partial match (first 8 chars)
        response = self.client.table('keyword_batches')\
            .select('*')\
            .ilike('id', f'{batch_id}%')\
            .execute()
        
        if response.data:
            return response.data[0]
        
        return None
    except Exception as e:
        print(f"Error fetching batch: {str(e)}")
        return None
```

**Testing:**
```bash
# Test regenerate all
/regenerate abc12345

# Test regenerate specific cluster
/regenerate abc12345 2

# Test invalid batch
/regenerate invalid_id

# Test non-owned batch
/regenerate (another user's batch)
```

---

## SLACK-029: Implement /set_email Command

**Type:** Feature  
**Priority:** Medium  
**Story Points:** 2  
**Estimated Time:** 1.5 hours  

**Description:**
Allow users to set their email address to receive PDF reports automatically after processing.

**Acceptance Criteria:**
- [ ] Validates email format
- [ ] Stores email in database
- [ ] Updates existing user record
- [ ] Confirms to user with success message
- [ ] Integrates with email service

**Deliverables:**
- Already implemented in `command_handlers.py`
- Email integration in pipeline

**Dependencies:** SLACK-023 (Email Service)

**Code Implementation:**

```python
# Update app/services/pipeline.py to include email delivery

def _process_keywords(self, raw_keywords: List[str], source: str):
    """Main processing pipeline with email delivery"""
    batch_id = None
    
    try:
        # ... existing processing code ...
        
        # After PDF upload to Slack
        # Check if user has email set
        user_email = self.db.get_user_email(self.user_id)
        
        if user_email:
            self._send_progress("📧 Sending report to your email...")
            
            try:
                from app.services.email_service import EmailService
                email_service = EmailService()
                
                email_sent = email_service.send_report(
                    to_email=user_email,
                    pdf_path=pdf_path,
                    batch_id=batch_id,
                    keyword_count=len(cleaned_keywords),
                    cluster_count=len(clusters)
                )
                
                if email_sent:
                    self.client.chat_postMessage(
                        channel=self.channel_id,
                        text=f"📧 Report sent to `{user_email}`!"
                    )
                    
                    # Update report status
                    self.db.update_report_email_status(batch_id, True, user_email)
                else:
                    self.client.chat_postMessage(
                        channel=self.channel_id,
                        text="⚠️ Email delivery failed. Please download from Slack."
                    )
            except Exception as e:
                print(f"Email delivery error: {str(e)}")
                self.client.chat_postMessage(
                    channel=self.channel_id,
                    text="⚠️ Email delivery encountered an issue. Report available in Slack."
                )
        
        # ... rest of processing ...
    
    except Exception as e:
        # ... error handling ...
```

```python
# Add to app/services/data/database.py

def get_user_email(self, slack_user_id: str) -> Optional[str]:
    """Get user's email address"""
    try:
        user = self.get_or_create_user(slack_user_id)
        return user.get('email') if user else None
    except Exception as e:
        print(f"Error fetching user email: {str(e)}")
        return None

def update_report_email_status(self, batch_id: str, sent: bool, email: str):
    """Update report email delivery status"""
    try:
        self.client.table('reports')\
            .update({
                'sent_via_email': sent,
                'email_sent_to': email
            })\
            .eq('batch_id', batch_id)\
            .execute()
    except Exception as e:
        print(f"Error updating report status: {str(e)}")
```

**Testing:**
```bash
# Set email
/set_email test@example.com

# Verify stored
/process_keywords test keywords
# Should receive email after completion

# Test invalid email
/set_email invalid-email

# Test email delivery failure handling
```

---

## SLACK-030: Implement /export Command (Mock)

**Type:** Feature  
**Priority:** Low  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Provide export functionality to Notion and Google Sheets (mock implementation for demo).

**Acceptance Criteria:**
- [ ] Export to Notion (mock)
- [ ] Export to Google Sheets (mock)
- [ ] Validates batch exists and is completed
- [ ] Provides helpful feedback
- [ ] Extensible for real API integration

**Deliverables:**
- Already implemented in `command_handlers.py`
- Mock export functions

**Dependencies:** SLACK-019

**Code Implementation (Real Notion Integration):**

```python
# app/services/integrations/notion_service.py
from notion_client import Client
from typing import List, Dict
from app.config import Config

class NotionService:
    """Export content strategy to Notion"""
    
    def __init__(self):
        self.client = Client(auth=Config.NOTION_API_KEY)
        self.database_id = Config.NOTION_DATABASE_ID
    
    def export_batch(self, batch_data: Dict, clusters: List[Dict]) -> str:
        """Export batch to Notion page"""
        try:
            # Create parent page
            parent_page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": f"Content Strategy - {batch_data['batch_name']}"
                                }
                            }
                        ]
                    },
                    "Status": {"select": {"name": "Completed"}},
                    "Keywords": {"number": batch_data['keyword_count']},
                    "Clusters": {"number": len(clusters)}
                }
            )
            
            page_id = parent_page['id']
            
            # Add content blocks
            children = []
            
            # Summary section
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "📊 Summary"}}]
                }
            })
            
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"Total Keywords: {batch_data['keyword_count']}\n"}}
                    ]
                }
            })
            
            # Add clusters
            for cluster in clusters:
                # Cluster heading
                children.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"text": {"content": f"📁 {cluster['cluster_name']}"}}
                        ]
                    }
                })
                
                # Keywords
                children.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {"text": {"content": f"Keywords: {', '.join(cluster['keywords'][:10])}"}}
                        ]
                    }
                })
                
                # Post idea
                post_idea = cluster.get('post_idea_metadata', {})
                if post_idea:
                    children.append({
                        "object": "block",
                        "type": "callout",
                        "callout": {
                            "icon": {"emoji": "💡"},
                            "rich_text": [
                                {"text": {"content": f"Post Idea: {post_idea.get('title', 'N/A')}"}}
                            ]
                        }
                    })
                
                # Outline (toggle list)
                outline = cluster.get('outline_json', {})
                if outline:
                    children.append({
                        "object": "block",
                        "type": "toggle",
                        "toggle": {
                            "rich_text": [{"text": {"content": "📝 Content Outline"}}],
                            "children": self._create_outline_blocks(outline)
                        }
                    })
            
            # Append blocks to page
            self.client.blocks.children.append(
                block_id=page_id,
                children=children
            )
            
            return parent_page['url']
        
        except Exception as e:
            raise Exception(f"Notion export failed: {str(e)}")
    
    def _create_outline_blocks(self, outline: Dict) -> List[Dict]:
        """Create Notion blocks for outline"""
        blocks = []
        
        for section in outline.get('sections', [])[:5]:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"text": {"content": section.get('heading', '')}}]
                }
            })
        
        return blocks
```

**Code Implementation (Real Google Sheets Integration):**

```python
# app/services/integrations/sheets_service.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Dict
from app.config import Config

class SheetsService:
    """Export content strategy to Google Sheets"""
    
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=credentials)
    
    def export_batch(self, batch_data: Dict, clusters: List[Dict]) -> str:
        """Export batch to Google Sheets"""
        try:
            # Create new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': f"Content Strategy - {batch_data['batch_name']}"
                },
                'sheets': [
                    {'properties': {'title': 'Summary'}},
                    {'properties': {'title': 'Clusters'}},
                    {'properties': {'title': 'Outlines'}},
                    {'properties': {'title': 'Post Ideas'}}
                ]
            }
            
            result = self.service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = result['spreadsheet_id']
            
            # Populate Summary sheet
            self._write_summary(spreadsheet_id, batch_data, clusters)
            
            # Populate Clusters sheet
            self._write_clusters(spreadsheet_id, clusters)
            
            # Populate Outlines sheet
            self._write_outlines(spreadsheet_id, clusters)
            
            # Populate Post Ideas sheet
            self._write_ideas(spreadsheet_id, clusters)
            
            # Make shareable
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            return spreadsheet_url
        
        except Exception as e:
            raise Exception(f"Google Sheets export failed: {str(e)}")
    
    def _write_summary(self, spreadsheet_id: str, batch_data: Dict, clusters: List[Dict]):
        """Write summary sheet"""
        values = [
            ['Content Strategy Report'],
            [],
            ['Batch ID', batch_data['id'][:8]],
            ['Created', batch_data['created_at'][:10]],
            ['Keywords', batch_data['keyword_count']],
            ['Clusters', len(clusters)],
            ['Status', batch_data['status']]
        ]
        
        body = {'values': values}
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Summary!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def _write_clusters(self, spreadsheet_id: str, clusters: List[Dict]):
        """Write clusters sheet"""
        values = [['Cluster #', 'Name', 'Keywords', 'Count']]
        
        for cluster in clusters:
            values.append([
                cluster['cluster_number'],
                cluster['cluster_name'],
                ', '.join(cluster['keywords'][:10]),
                cluster['keyword_count']
            ])
        
        body = {'values': values}
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Clusters!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def _write_outlines(self, spreadsheet_id: str, clusters: List[Dict]):
        """Write outlines sheet"""
        values = [['Cluster', 'Section', 'Content']]
        
        for cluster in clusters:
            outline = cluster.get('outline_json', {})
            cluster_name = cluster['cluster_name']
            
            for section in outline.get('sections', []):
                values.append([
                    cluster_name,
                    section.get('heading', ''),
                    section.get('description', '')
                ])
        
        body = {'values': values}
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Outlines!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def _write_ideas(self, spreadsheet_id: str, clusters: List[Dict]):
        """Write post ideas sheet"""
        values = [['Cluster', 'Title', 'Angle', 'Target Audience']]
        
        for cluster in clusters:
            idea = cluster.get('post_idea_metadata', {})
            values.append([
                cluster['cluster_name'],
                idea.get('title', ''),
                idea.get('angle', ''),
                idea.get('target_audience', '')
            ])
        
        body = {'values': values}
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Post Ideas!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
```

**Update command_handlers.py to use real exports:**

```python
def export_batch(client, channel_id, batch_id, destination):
    """Export batch data to external service"""
    try:
        from app.services.data.database import DatabaseService
        
        db = DatabaseService()
        batch = db.get_batch_by_id(batch_id)
        clusters = db.get_clusters_by_batch(batch_id)
        
        if destination == 'notion':
            from app.services.integrations.notion_service import NotionService
            
            notion = NotionService()
            page_url = notion.export_batch(batch, clusters)
            
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ *Notion Export Complete!*\n\n"
                     f"📊 Exported {len(clusters)} clusters\n"
                     f"🔗 View in Notion: {page_url}"
            )
        
        elif destination == 'sheets':
            from app.services.integrations.sheets_service import SheetsService
            
            sheets = SheetsService()
            sheet_url = sheets.export_batch(batch, clusters)
            
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ *Google Sheets Export Complete!*\n\n"
                     f"📊 Exported {len(clusters)} clusters\n"
                     f"🔗 View spreadsheet: {sheet_url}"
            )
    
    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Export failed: {str(e)}"
        )
```

**Testing:**
```bash
# Test Notion export
/export notion abc12345

# Test Sheets export
/export sheets abc12345

# Test invalid destination
/export invalid abc12345

# Test non-existent batch
/export notion invalid_id
```

---

## SLACK-031: Enhanced History with Action Buttons

**Type:** Enhancement  
**Priority:** Low  
**Story Points:** 2  
**Estimated Time:** 1.5 hours  

**Description:**
Add interactive buttons to history view for quick actions on past batches.

**Acceptance Criteria:**
- [ ] View details button shows cluster summary
- [ ] Regenerate button triggers /regenerate
- [ ] Delete button (optional) removes batch
- [ ] Action handlers properly registered

**Deliverables:**
- Already implemented button UI in `command_handlers.py`
- Action handlers for buttons

**Dependencies:** SLACK-028

**Code Implementation:**

```python
# Add to command_handlers.py

def register(app):
    # ... existing commands ...
    
    # Action handlers for history buttons
    @app.action(re.compile("regenerate_.*"))
    def handle_regenerate_button(ack, body, client):
        ack()
        
        user_id = body['user']['id']
        channel_id = body['channel']['id']
        batch_id = body['actions'][0]['value']
        
        # Trigger regeneration
        client.chat_postMessage(
            channel=channel_id,
            text=f"♻️ Starting regeneration for batch `{batch_id[:8]}`..."
        )
        
        # Call regenerate logic
        from app.services.data.database import DatabaseService
        db = DatabaseService()
        
        batch = db.get_batch_by_id(batch_id)
        if batch:
            clusters = db.get_clusters_by_batch(batch_id)
            
            thread = threading.Thread(
                target=regenerate_outlines,
                args=(client, channel_id, user_id, batch_id, clusters)
            )
            thread.daemon = True
            thread.start()
    
    @app.action(re.compile("details_.*"))
    def handle_details_button(ack, body, client):
        ack()
        
        channel_id = body['channel']['id']
        batch_id = body['actions'][0]['value']
        
        from app.services.data.database import DatabaseService
        from app.utils.slack_formatters import SlackFormatter
        
        db = DatabaseService()
        formatter = SlackFormatter()
        
        batch = db.get_batch_by_id(batch_id)
        clusters = db.get_clusters_by_batch(batch_id)
        
        if not batch or not clusters:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Batch details not found."
            )
            return
        
        # Send detailed view
        blocks = formatter.format_clusters_summary(clusters)
        
        client.chat_postMessage(
            channel=channel_id,
            text=f"📊 Details for batch `{batch_id[:8]}`",
            blocks=blocks
        )
```

**Testing:**
```bash
# View history
/history

# Click "View Details" button
# Should show cluster summary

# Click "Regenerate" button
# Should start regeneration process
```

---

## Epic Completion Checklist

**All Tasks Complete:**
- [ ] SLACK-028: /regenerate command
- [ ] SLACK-029: /set_email command
- [ ] SLACK-030: /export command (mock or real)
- [ ] SLACK-031: Action button handlers

**Integration Tests:**
- [ ] Regenerate works for all clusters
- [ ] Regenerate works for specific cluster
- [ ] Email set and delivered successfully
- [ ] Export creates proper format (mock)
- [ ] History buttons trigger correct actions
- [ ] All commands handle errors gracefully

**User Experience:**
- [ ] Commands are intuitive
- [ ] Error messages are helpful
- [ ] Success confirmations clear
- [ ] Processing happens in background
- [ ] No blocking operations

**Ready for Production:**
- [ ] All bonus features tested
- [ ] Database methods working
- [ ] Email integration (if implemented)
- [ ] Export integrations (if real)
- [ ] No critical bugs