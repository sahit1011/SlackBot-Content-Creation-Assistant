# app/services/pipeline.py
import threading
import os
import logging
from typing import List
from app.services.processing.keyword_cleaner import KeywordCleaner
from app.services.ai.embedding_generator import EmbeddingGenerator
from app.services.processing.keyword_clusterer import KeywordClusterer
from app.services.external.web_search import WebSearchService
from app.services.processing.content_scraper import ContentScraper
from app.services.ai.outline_generator import OutlineGenerator
from app.services.ai.idea_generator import IdeaGenerator
from app.services.data.database import DatabaseService
from app.services.processing.report_generator import ReportGenerator
from app.services.external.email_service import EmailService
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
        # Initialize clusters count for error handling
        self.clusters_count = 0

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

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
            self.logger.info(" STARTING CONTENT CREATION PIPELINE")
            self.logger.info(f" Received {len(raw_keywords)} raw keywords from {source}")

            # Step 1: Clean keywords
            self.logger.info(" STEP 1: Keyword Cleaning")
            self._send_progress(" Cleaning keywords...")
            cleaner = KeywordCleaner()
            result = cleaner.clean_keywords(raw_keywords)
            cleaned_keywords = result['keywords']

            self.logger.info(f" Keyword cleaning complete: {result['original_count']} → {result['cleaned_count']} unique keywords")
            self.logger.info(f" Cleaned keywords: {cleaned_keywords[:5]}{'...' if len(cleaned_keywords) > 5 else ''}")
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
            self.logger.info(" STEP 2: Embedding Generation")
            self._send_progress(" Analyzing keyword relationships...")
            embedding_gen = EmbeddingGenerator()
            embeddings = embedding_gen.generate_embeddings(cleaned_keywords)
            self.logger.info(f" Generated embeddings for {len(cleaned_keywords)} keywords (shape: {embeddings.shape})")

            # Step 3: Cluster keywords
            self.logger.info(" STEP 3: Keyword Clustering")
            self._send_progress(" Grouping keywords into clusters...")
            clusterer = KeywordClusterer()
            clusters = clusterer.cluster_keywords(cleaned_keywords, embeddings)
            self.clusters_count = len(clusters)  # Store count for error handling
            self.logger.info(f" Created {len(clusters)} keyword clusters")
            for i, cluster in enumerate(clusters, 1):
                self.logger.info(f" Cluster {i}: '{cluster['cluster_name']}' ({cluster['keyword_count']} keywords)")

            self._send_progress(f" Created {len(clusters)} keyword clusters")

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

            # Step 4: Process each cluster
            self.logger.info(" STEP 4: Web Research & Content Generation")
            for idx, cluster in enumerate(clusters, 1):
                cluster_name = cluster['cluster_name']
                self.logger.info(f" Processing cluster {idx}/{len(clusters)}: '{cluster_name}'")
                self._send_progress(f" Processing cluster {idx}/{len(clusters)}: {cluster_name}")

                # Search top results
                main_keyword = cluster['keywords'][0] if cluster['keywords'] else cluster_name.split()[0]
                self.logger.info(f" Searching for '{main_keyword}' using SerpAPI")
                search_results = search_service.search_single(main_keyword, count=5)
                self.logger.info(f" Found {len(search_results)} search results")

                # Scrape content
                urls = [r['url'] for r in search_results[:3]]
                self.logger.info(f" Scraping {len(urls)} top URLs: {urls}")
                scraped_data = scraper.scrape_urls(urls)
                successful_scrapes = sum(1 for r in scraped_data if r.get('success'))
                self.logger.info(f" Successfully scraped {successful_scrapes}/{len(urls)} pages")

                # Generate outline
                self.logger.info("  Generating content outline using LLM")
                outline = outline_gen.generate_outline(cluster, scraped_data)
                cluster['outline'] = outline
                self.logger.info(f"   Generated outline with {len(outline.get('sections', []))} sections")

                # Generate post idea
                self.logger.info("   Generating post idea using LLM")
                post_idea = idea_gen.generate_idea(cluster, outline)
                cluster['post_idea'] = post_idea
                self.logger.info(f"   Generated post idea: '{post_idea.get('title', 'N/A')}'")

                # Save cluster to database
                self.db.save_cluster(batch_id, cluster, post_idea, outline)
                self.logger.info("   Saved cluster data to database")

                # Send detailed cluster info
                detail_blocks = self.formatter.format_cluster_detail(
                    cluster, post_idea, outline
                )
                self.client.chat_postMessage(
                    channel=self.channel_id,
                    blocks=detail_blocks
                )

            # Step 5: Generate report
            self.logger.info(" STEP 5: Report Generation")
            self._send_progress(" Generating comprehensive report...")
            # Debug: Check if clusters is available
            self.logger.info(f"DEBUG: Clusters defined in scope: {'clusters' in locals()}")
            if 'clusters' in locals():
                self.logger.info(f"DEBUG: Clusters length: {len(clusters)}")
            else:
                self.logger.error("DEBUG: Clusters variable not found in locals")
            report_gen = ReportGenerator()
            pdf_path = report_gen.generate_report(
                batch_data,
                cleaned_keywords,
                clusters
            )
            self.logger.info(f" Generated PDF report: {pdf_path}")

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
                'keyword_count': len(cleaned_keywords) if 'cleaned_keywords' in locals() else 0,
                'cluster_count': self.clusters_count,
                'outline_count': self.clusters_count,
                'idea_count': self.clusters_count
            })
            self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=summary_blocks
            )

            # Update batch status
            self.db.update_batch_status(batch_id, 'completed')
            self.logger.info(" Pipeline completed successfully")

            # Optional: Send email if user wants it (before file deletion)
            user_email = self.db.get_user_email(self.user_id)

            if user_email:
                self.logger.info(f"📧 Sending report to user email: {user_email}")
                email_service = EmailService()
                email_sent = email_service.send_report(
                    user_email,
                    pdf_path,
                    batch_id,
                    len(cleaned_keywords),
                    self.clusters_count
                )

                if email_sent:
                    self.logger.info("✓ Report email sent successfully")
                    self.client.chat_postMessage(
                        channel=self.channel_id,
                        text="📧 Report also sent to your email!"
                    )
                    self.db.update_report_email_status(batch_id, True, user_email)
                else:
                    self.logger.warning("✗ Failed to send report email")

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f" PIPELINE ERROR: {error_msg}")
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