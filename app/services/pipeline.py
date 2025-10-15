# app/services/pipeline.py
import threading
import os
from typing import List
from app.services.keyword_cleaner import KeywordCleaner
from app.services.embedding_generator import EmbeddingGenerator
from app.services.keyword_clusterer import KeywordClusterer
from app.services.web_search import WebSearchService
from app.services.content_scraper import ContentScraper
from app.services.outline_generator import OutlineGenerator
from app.services.idea_generator import IdeaGenerator
from app.services.database import DatabaseService
from app.services.report_generator import ReportGenerator
from app.services.email_service import EmailService
from app.utils.slack_formatters import SlackFormatter

class ProcessingPipeline:
    """Orchestrate the complete keyword processing workflow"""

    def __init__(self, slack_client, channel_id: str, user_id: str):
        self.client = slack_client
        self.channel_id = channel_id
        self.slack_user_id = user_id
        self.db = DatabaseService()
        self.formatter = SlackFormatter()
        # Ensure user exists in database and get UUID
        user = self.db.get_or_create_user(user_id)
        self.user_id = user['id']

    def start_from_keywords(self, keywords: List[str], source: str = 'text'):
        """Start processing in background thread"""
        thread = threading.Thread(
            target=self._process_keywords,
            args=(keywords, source)
        )
        thread.daemon = True
        thread.start()

    def _process_keywords(self, raw_keywords: List[str], source: str):
        """Main processing pipeline"""
        batch_id = None

        try:
            # Step 1: Clean keywords
            self._send_progress("🧹 Cleaning keywords...")
            cleaner = KeywordCleaner()
            result = cleaner.clean_keywords(raw_keywords)
            cleaned_keywords = result['keywords']

            self._send_progress(
                f"✓ Cleaned: {result['original_count']} → {result['cleaned_count']} unique keywords"
            )

            # Save batch to database
            batch_data = self.db.save_batch(
                self.user_id,
                raw_keywords,
                cleaned_keywords,
                source
            )
            batch_id = batch_data['id']

            # Step 2: Generate embeddings
            self._send_progress("🔍 Analyzing keyword relationships...")
            embedding_gen = EmbeddingGenerator()
            embeddings = embedding_gen.generate_embeddings(cleaned_keywords)

            # Step 3: Cluster keywords
            self._send_progress("📊 Grouping keywords into clusters...")
            clusterer = KeywordClusterer()
            clusters = clusterer.cluster_keywords(cleaned_keywords, embeddings)

            self._send_progress(f"✓ Created {len(clusters)} keyword clusters")

            # Send cluster summary
            cluster_blocks = self.formatter.format_clusters_summary(clusters)
            self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=cluster_blocks
            )

            # Step 4: Process each cluster
            search_service = WebSearchService()
            scraper = ContentScraper()
            outline_gen = OutlineGenerator()
            idea_gen = IdeaGenerator()

            for idx, cluster in enumerate(clusters, 1):
                self._send_progress(f"📝 Processing cluster {idx}/{len(clusters)}: {cluster['cluster_name']}")

                # Search top results
                main_keyword = cluster['keywords'][0]
                search_results = search_service.search_single(main_keyword, count=5)

                # Scrape content
                urls = [r['url'] for r in search_results[:3]]
                scraped_data = scraper.scrape_urls(urls)

                # Generate outline
                outline = outline_gen.generate_outline(cluster, scraped_data)
                cluster['outline'] = outline

                # Generate post idea
                post_idea = idea_gen.generate_idea(cluster, outline)
                cluster['post_idea'] = post_idea

                # Save cluster to database
                self.db.save_cluster(batch_id, cluster, post_idea, outline)

                # Send detailed cluster info
                detail_blocks = self.formatter.format_cluster_detail(
                    cluster, post_idea, outline
                )
                self.client.chat_postMessage(
                    channel=self.channel_id,
                    blocks=detail_blocks
                )

            # Step 5: Generate report
            self._send_progress("📄 Generating comprehensive report...")
            report_gen = ReportGenerator()
            pdf_path = report_gen.generate_report(
                batch_data,
                cleaned_keywords,
                clusters
            )

            # Upload report to Slack
            try:
                # First upload the file
                with open(pdf_path, 'rb') as f:
                    upload_response = self.client.files_upload_v2(
                        channel=self.channel_id,
                        file=f,
                        filename=os.path.basename(pdf_path),
                        title=f"Content_Strategy_Report_{batch_id[:8]}.pdf"
                    )

                # Get file info
                file_id = upload_response.get('file', {}).get('id')
                file_url = upload_response.get('file', {}).get('permalink', '')

                if file_id:
                    # Share the file in the channel with a message
                    self.client.files_share(
                        channel=self.channel_id,
                        file=file_id,
                        text="📄 *Your comprehensive content strategy report is ready!*\n\n"
                             "This report includes:\n"
                             "• All processed keywords\n"
                             "• Semantic keyword clusters\n"
                             "• Content outlines for each cluster\n"
                             "• Creative post ideas\n\n"
                             "Download and share with your team!"
                    )

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

                # Notify user with file location
                self.client.chat_postMessage(
                    channel=self.channel_id,
                    text=f"⚠️ Report generated but upload failed. Report saved locally as: `{os.path.basename(pdf_path)}`\n"
                         f"📁 Location: `reports/{os.path.basename(pdf_path)}`"
                )

            # Step 6: Send completion summary
            summary_blocks = self.formatter.format_completion_summary({
                'keyword_count': len(cleaned_keywords),
                'cluster_count': len(clusters),
                'outline_count': len(clusters),
                'idea_count': len(clusters)
            })
            self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=summary_blocks
            )

            # Update batch status
            self.db.update_batch_status(batch_id, 'completed')

            # Optional: Send email if user wants it (before file deletion)
            user_email = self.db.get_user_email(self.user_id)

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

        except Exception as e:
            error_msg = str(e)
            print(f"Pipeline error: {error_msg}")

            # Send error to user
            error_blocks = self.formatter.format_error(
                "An error occurred during processing",
                "Please try again or contact support if the issue persists",
                batch_id
            )
            self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=error_blocks
            )

            # Update batch status
            if batch_id:
                self.db.update_batch_status(batch_id, 'failed', error_msg)

    def _send_progress(self, message: str):
        """Send progress update to Slack"""
        formatted = self.formatter.format_progress(message)
        self.client.chat_postMessage(
            channel=self.channel_id,
            text=formatted
        )