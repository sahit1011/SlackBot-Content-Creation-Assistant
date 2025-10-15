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