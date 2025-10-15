# EPIC-006: Report Generation System

**Priority:** P0 (Critical Path)  
**Story Points:** 10  
**Duration:** 1 Day  
**Owner:** Developer  

---

## SLACK-021: Build PDF Report Generator

**Type:** Feature  
**Priority:** Critical  
**Story Points:** 5  
**Estimated Time:** 4 hours  

**Description:**
Generate comprehensive PDF reports containing all processing results including keywords, clusters, outlines, and post ideas.

**Acceptance Criteria:**
- [ ] Generates professional-looking PDF
- [ ] Includes all sections (keywords, clusters, outlines, ideas)
- [ ] Table of contents with page numbers
- [ ] Proper formatting and structure
- [ ] File size under 5MB
- [ ] Handles large datasets (100+ keywords)

**Deliverables:**
- `app/services/report_generator.py`

**Dependencies:** SLACK-018, SLACK-019

**Code Implementation:**

```python
# app/services/report_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from typing import List, Dict
import os

class ReportGenerator:
    """Generate PDF reports for keyword analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceBefore=20,
            spaceAfter=12
        ))
        
        # Subsection style
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#444444'),
            spaceBefore=12,
            spaceAfter=8
        ))
    
    def generate_report(
        self,
        batch_data: Dict,
        keywords: List[str],
        clusters: List[Dict]
    ) -> str:
        """Generate complete PDF report"""
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"content_strategy_report_{timestamp}.pdf"
        filepath = os.path.join('/tmp', filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Cover page
        story.extend(self._create_cover_page(batch_data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(batch_data, keywords, clusters))
        story.append(PageBreak())
        
        # Keywords section
        story.extend(self._create_keywords_section(batch_data, keywords))
        story.append(PageBreak())
        
        # Clusters section
        story.extend(self._create_clusters_section(clusters))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _create_cover_page(self, batch_data: Dict) -> List:
        """Create cover page"""
        content = []
        
        # Add spacing from top
        content.append(Spacer(1, 2*inch))
        
        # Title
        title = Paragraph("Content Strategy Report", self.styles['CustomTitle'])
        content.append(title)
        content.append(Spacer(1, 0.3*inch))
        
        # Batch info
        batch_info = f"""
        <para align=center>
        <b>Batch ID:</b> {batch_data.get('id', 'N/A')[:8]}...<br/>
        <b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
        <b>Keywords Processed:</b> {batch_data.get('keyword_count', 0)}
        </para>
        """
        content.append(Paragraph(batch_info, self.styles['Normal']))
        content.append(Spacer(1, 1*inch))
        
        # Footer
        footer = Paragraph(
            "<para align=center><i>AI-Powered Content Strategy Assistant</i></para>",
            self.styles['Normal']
        )
        content.append(footer)
        
        return content
    
    def _create_executive_summary(
        self,
        batch_data: Dict,
        keywords: List[str],
        clusters: List[Dict]
    ) -> List:
        """Create executive summary"""
        content = []
        
        content.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.2*inch))
        
        summary_text = f"""
        This report contains a comprehensive content strategy analysis for {len(keywords)} keywords.
        The analysis identified {len(clusters)} distinct content clusters, each with detailed 
        outlines and post ideas based on competitive research of top-ranking content.
        """
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 0.3*inch))
        
        # Statistics table
        stats_data = [
            ['Metric', 'Value'],
            ['Total Keywords', str(len(keywords))],
            ['Unique Keywords', str(batch_data.get('keyword_count', len(keywords)))],
            ['Content Clusters', str(len(clusters))],
            ['Outlines Generated', str(len(clusters))],
            ['Post Ideas', str(len(clusters))]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(stats_table)
        
        return content
    
    def _create_keywords_section(self, batch_data: Dict, keywords: List[str]) -> List:
        """Create keywords section"""
        content = []
        
        content.append(Paragraph("1. Keywords Analysis", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.2*inch))
        
        # Raw keywords
        content.append(Paragraph("1.1 Original Keywords", self.styles['SubSection']))
        raw_keywords = batch_data.get('raw_keywords', keywords)
        raw_text = ", ".join(raw_keywords[:50])
        if len(raw_keywords) > 50:
            raw_text += f" ... and {len(raw_keywords) - 50} more"
        content.append(Paragraph(raw_text, self.styles['Normal']))
        content.append(Spacer(1, 0.2*inch))
        
        # Cleaned keywords
        content.append(Paragraph("1.2 Processed Keywords", self.styles['SubSection']))
        clean_text = ", ".join(keywords[:50])
        if len(keywords) > 50:
            clean_text += f" ... and {len(keywords) - 50} more"
        content.append(Paragraph(clean_text, self.styles['Normal']))
        
        return content
    
    def _create_clusters_section(self, clusters: List[Dict]) -> List:
        """Create clusters section with details"""
        content = []
        
        content.append(Paragraph("2. Content Clusters & Strategy", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.2*inch))
        
        for idx, cluster in enumerate(clusters, 1):
            # Cluster header
            cluster_title = f"2.{idx} Cluster: {cluster['cluster_name']}"
            content.append(Paragraph(cluster_title, self.styles['SubSection']))
            content.append(Spacer(1, 0.1*inch))
            
            # Keywords in this cluster
            content.append(Paragraph(
                f"<b>Keywords ({cluster['keyword_count']}):</b>",
                self.styles['Normal']
            ))
            keywords_text = ", ".join(cluster['keywords'])
            content.append(Paragraph(keywords_text, self.styles['Normal']))
            content.append(Spacer(1, 0.15*inch))
            
            # Post idea
            post_idea = cluster.get('post_idea', {})
            if post_idea:
                content.append(Paragraph("<b>Post Idea:</b>", self.styles['Normal']))
                
                idea_text = f"""
                <b>Title:</b> {post_idea.get('title', 'N/A')}<br/>
                <b>Angle:</b> {post_idea.get('angle', 'N/A')}<br/>
                <b>Target Audience:</b> {post_idea.get('target_audience', 'N/A')}<br/>
                <b>Value Proposition:</b> {post_idea.get('value_proposition', 'N/A')}
                """
                content.append(Paragraph(idea_text, self.styles['Normal']))
                content.append(Spacer(1, 0.15*inch))
            
            # Outline
            outline = cluster.get('outline', {})
            if outline:
                content.append(Paragraph("<b>Content Outline:</b>", self.styles['Normal']))
                
                # Outline title
                outline_title = outline.get('title', 'Content Outline')
                content.append(Paragraph(f"<i>{outline_title}</i>", self.styles['Normal']))
                content.append(Spacer(1, 0.1*inch))
                
                # Introduction
                intro = outline.get('introduction', {})
                if intro:
                    content.append(Paragraph("<b>Introduction</b>", self.styles['Normal']))
                    if isinstance(intro, dict):
                        intro_text = intro.get('hook', '') or intro.get('overview', '')
                    else:
                        intro_text = str(intro)
                    content.append(Paragraph(intro_text, self.styles['Normal']))
                    content.append(Spacer(1, 0.1*inch))
                
                # Sections
                sections = outline.get('sections', [])
                for sec_idx, section in enumerate(sections[:7], 1):  # Limit to 7 sections
                    heading = section.get('heading', f'Section {sec_idx}')
                    content.append(Paragraph(f"<b>{sec_idx}. {heading}</b>", self.styles['Normal']))
                    
                    # Subsections
                    subsections = section.get('subsections', [])
                    if subsections:
                        for subsec in subsections[:3]:  # Limit to 3 subsections
                            content.append(Paragraph(f"  • {subsec}", self.styles['Normal']))
                    
                    description = section.get('description', '')
                    if description:
                        content.append(Paragraph(f"  <i>{description}</i>", self.styles['Normal']))
                    
                    content.append(Spacer(1, 0.05*inch))
                
                # Conclusion
                conclusion = outline.get('conclusion', {})
                if conclusion:
                    content.append(Paragraph("<b>Conclusion</b>", self.styles['Normal']))
                    if isinstance(conclusion, dict):
                        concl_text = conclusion.get('summary', '') or conclusion.get('cta', '')
                    else:
                        concl_text = str(conclusion)
                    content.append(Paragraph(concl_text, self.styles['Normal']))
            
            content.append(Spacer(1, 0.3*inch))
            
            # Page break after each cluster (except last)
            if idx < len(clusters):
                content.append(PageBreak())
        
        return content
```

**Testing:**
- Generate report with 5 keywords
- Generate report with 50+ keywords
- Verify all sections present
- Check formatting in PDF viewer
- Test on different OS (Mac/Windows/Linux)

---

## SLACK-022: Implement Report Upload to Slack

**Type:** Feature  
**Priority:** Critical  
**Story Points:** 2  
**Estimated Time:** 1.5 hours  

**Description:**
Upload generated PDF reports to Slack channels for easy access.

**Acceptance Criteria:**
- [ ] Uploads PDF file to correct channel
- [ ] Descriptive filename with timestamp
- [ ] Includes helpful message
- [ ] Handles upload failures gracefully
- [ ] File permissions set correctly

**Deliverables:**
- Update to `app/services/pipeline.py` (already included in EPIC-005)

**Dependencies:** SLACK-021

**Code Implementation:**

```python
# Add to pipeline.py in SLACK-018
# This code is already included in the pipeline, here's the specific section:

# In _process_keywords method after report generation:

# Upload report to Slack
try:
    upload_response = self.client.files_upload_v2(
        channel=self.channel_id,
        file=pdf_path,
        title=f"Content_Strategy_Report_{batch_id[:8]}.pdf",
        initial_comment="📄 *Your comprehensive content strategy report is ready!*\n\n"
                       "This report includes:\n"
                       "• All processed keywords\n"
                       "• Semantic keyword clusters\n"
                       "• Content outlines for each cluster\n"
                       "• Creative post ideas\n\n"
                       "Download and share with your team!"
    )
    
    # Get file URL from response
    file_url = upload_response.get('file', {}).get('permalink', '')
    
    # Save report info with URL
    self.db.save_report(batch_id, pdf_path, file_url)
    
    # Clean up local file after successful upload
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        
except Exception as e:
    error_msg = f"Failed to upload report: {str(e)}"
    print(error_msg)
    
    # Still save report info even if upload fails
    self.db.save_report(batch_id, pdf_path)
    
    # Notify user
    self.client.chat_postMessage(
        channel=self.channel_id,
        text=f"⚠️ Report generated but upload failed. Report saved as: `{os.path.basename(pdf_path)}`"
    )
```

**Testing:**
- Upload small PDF (< 1MB)
- Upload large PDF (3-5MB)
- Test with network issues
- Verify file appears in Slack
- Test download from Slack

---

## SLACK-023: Implement Email Delivery (Bonus)

**Type:** Feature  
**Priority:** Medium (Bonus)  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Send PDF reports via email using SendGrid for users who want email delivery.

**Acceptance Criteria:**
- [ ] Professional email template
- [ ] PDF attached to email
- [ ] Email validation
- [ ] Error notifications
- [ ] Optional feature (user can enable/disable)

**Deliverables:**
- `app/services/email_service.py`

**Dependencies:** SLACK-021

**Code Implementation:**

```python
# app/services/email_service.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
import os
from app.config import Config

class EmailService:
    """Handle email delivery via SendGrid"""
    
    def __init__(self):
        self.client = SendGridAPIClient(Config.SENDGRID_API_KEY)
        self.from_email = Config.SENDGRID_FROM_EMAIL
    
    def send_report(
        self,
        to_email: str,
        pdf_path: str,
        batch_id: str,
        keyword_count: int,
        cluster_count: int
    ) -> bool:
        """Send report via email"""
        
        try:
            # Validate email
            if not self._is_valid_email(to_email):
                raise ValueError(f"Invalid email address: {to_email}")
            
            # Read PDF file
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            
            # Encode PDF
            encoded_pdf = base64.b64encode(pdf_data).decode()
            
            # Create attachment
            attachment = Attachment(
                FileContent(encoded_pdf),
                FileName(os.path.basename(pdf_path)),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            
            # Create email
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Your Content Strategy Report is Ready',
                html_content=self._generate_email_html(
                    batch_id,
                    keyword_count,
                    cluster_count
                )
            )
            
            message.attachment = attachment
            
            # Send email
            response = self.client.send(message)
            
            return response.status_code == 202
            
        except Exception as e:
            print(f"Email send error: {str(e)}")
            return False
    
    def _generate_email_html(
        self,
        batch_id: str,
        keyword_count: int,
        cluster_count: int
    ) -> str:
        """Generate email HTML content"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2c5aa0;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .stats {{
                    background-color: white;
                    padding: 15px;
                    margin: 20px 0;
                    border-left: 4px solid #2c5aa0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📄 Your Content Strategy Report</h1>
                </div>
                <div class="content">
                    <p>Hello!</p>
                    
                    <p>Your content strategy report has been generated and is attached to this email.</p>
                    
                    <div class="stats">
                        <h3>Report Summary</h3>
                        <p><strong>Batch ID:</strong> {batch_id[:8]}...</p>
                        <p><strong>Keywords Analyzed:</strong> {keyword_count}</p>
                        <p><strong>Content Clusters:</strong> {cluster_count}</p>
                        <p><strong>Generated:</strong> {self._get_current_date()}</p>
                    </div>
                    
                    <p>This comprehensive report includes:</p>
                    <ul>
                        <li>✅ All processed keywords</li>
                        <li>✅ Semantic keyword clusters</li>
                        <li>✅ Detailed content outlines</li>
                        <li>✅ Creative post ideas for each cluster</li>
                        <li>✅ Competitive analysis insights</li>
                    </ul>
                    
                    <p>Review the attached PDF and use it to guide your content creation strategy.</p>
                    
                    <p>Happy content creating!</p>
                    
                    <p>
                        <strong>Content Strategy Assistant</strong><br/>
                        <em>AI-Powered Content Planning</em>
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _get_current_date(self) -> str:
        """Get current date formatted"""
        from datetime import datetime
        return datetime.now().strftime('%B %d, %Y')


# Add to pipeline.py after report upload (optional):

# Optional: Send email if user wants it
user_email = self.db.get_user_email(self.user_id)  # Implement this method

if user_email:
    email_service = EmailService()
    email_sent = email_service.send_report(
        user_email,
        pdf_path,
        batch_id,
        len(cleaned_keywords),
        len(clusters)
    )
    
    if email_sent:
        self.client.chat_postMessage(
            channel=self.channel_id,
            text="📧 Report also sent to your email!"
        )
        self.db.update_report_email_status(batch_id, True, user_email)
```

**Additional Database Method:**

```python
# Add to database.py

def get_user_email(self, user_id: str) -> Optional[str]:
    """Get user's email address"""
    response = self.client.table('users')\
        .select('email')\
        .eq('id', user_id)\
        .execute()
    
    if response.data and response.data[0].get('email'):
        return response.data[0]['email']
    return None

def update_report_email_status(self, batch_id: str, sent: bool, email: str):
    """Update report email delivery status"""
    self.client.table('reports')\
        .update({
            'sent_via_email': sent,
            'email_sent_to': email
        })\
        .eq('batch_id', batch_id)\
        .execute()
```

**Testing:**
- Send test email
- Verify PDF attachment
- Test with invalid email
- Check email in spam folder
- Test HTML rendering

---

## Epic Completion Checklist

**All Tasks Complete:**
- [ ] SLACK-021: PDF report generator
- [ ] SLACK-022: Report upload to Slack
- [ ] SLACK-023: Email delivery (bonus)

**Quality Checks:**
- [ ] PDFs are professionally formatted
- [ ] All data included in reports
- [ ] File uploads work reliably
- [ ] Email delivery works (if implemented)
- [ ] No file size issues

**Integration Tests:**
- [ ] Generate report with small dataset (5 keywords)
- [ ] Generate report with large dataset (50+ keywords)
- [ ] Upload to Slack successfully
- [ ] Download and open PDF from Slack
- [ ] Send email (if implemented)

**Ready for Next Epic:**
- [ ] No blocking bugs
- [ ] Code committed to Git
- [ ] Tests passing
- [ ] Reports look professional