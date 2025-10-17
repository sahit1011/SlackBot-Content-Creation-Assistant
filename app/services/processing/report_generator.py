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
        """Create custom paragraph styles with professional fonts"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=40,
            alignment=TA_CENTER,
            leading=32
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=25,
            alignment=TA_CENTER
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor('#2b6cb0'),
            spaceBefore=25,
            spaceAfter=15,
            leading=22,
            borderColor=colors.HexColor('#e2e8f0'),
            borderWidth=0,
            borderPadding=0
        ))

        # Subsection style
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#2d3748'),
            spaceBefore=15,
            spaceAfter=10,
            leading=18
        ))

        # Custom body text style
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=8,
            leading=14
        ))

        # Highlight style
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=colors.HexColor('#c53030'),
            spaceAfter=8,
            leading=14
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=colors.HexColor('#718096'),
            alignment=TA_CENTER
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
        # Use current directory reports folder instead of /tmp
        reports_dir = os.path.join(os.getcwd(), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)

        # Create PDF document with professional settings
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=36,  # Increased bottom margin for footer
            title="Content Strategy Report",
            author="AI Content Strategy Assistant",
            subject="Content Analysis and Strategy Recommendations"
        )

        # Build content with table of contents
        story = []

        # Cover page
        story.extend(self._create_cover_page(batch_data, clusters))
        story.append(PageBreak())

        # Table of contents
        story.extend(self._create_table_of_contents(clusters))
        story.append(PageBreak())

        # Executive summary
        story.extend(self._create_executive_summary(batch_data, keywords, clusters))
        story.append(PageBreak())

        # Keywords section
        story.extend(self._create_keywords_section(batch_data, clusters))
        story.append(PageBreak())

        # Clusters section
        story.extend(self._create_clusters_section(clusters))

        # Build PDF
        doc.build(story)

        return filepath

    def _create_cover_page(self, batch_data: Dict, clusters: List[Dict] = None) -> List:
        """Create professional cover page"""
        content = []

        # Add spacing from top
        content.append(Spacer(1, 1.5*inch))

        # Main title
        title = Paragraph("Content Strategy Report", self.styles['CustomTitle'])
        content.append(title)
        content.append(Spacer(1, 0.2*inch))

        # Subtitle
        subtitle = Paragraph("AI-Powered Content Analysis & Strategy", self.styles['Subtitle'])
        content.append(subtitle)
        content.append(Spacer(1, 0.8*inch))

        # Decorative line
        from reportlab.lib.colors import Color
        content.append(Spacer(1, 0.1*inch))

        # Get actual cluster count from the clusters parameter
        actual_cluster_count = len(clusters) if clusters else 0

        # Batch info box
        batch_info = f"""
        <para align=center>
        <b>Report ID:</b> {batch_data.get('id', 'N/A')[:12]}<br/>
        <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Keywords Analyzed:</b> {batch_data.get('keyword_count', 0)}<br/>
        <b>Content Clusters:</b> {actual_cluster_count}
        </para>
        """
        content.append(Paragraph(batch_info, self.styles['CustomBodyText']))
        content.append(Spacer(1, 1.2*inch))

        # Professional footer
        footer = Paragraph(
            "Generated by AI Content Strategy Assistant | Confidential",
            self.styles['Footer']
        )
        content.append(footer)

        return content

    def _create_table_of_contents(self, clusters: List[Dict]) -> List:
        """Create table of contents"""
        content = []

        content.append(Paragraph("Table of Contents", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.3*inch))

        toc_data = [
            ["1. Executive Summary", "3"],
            ["2. Content Clusters & Strategy", "4"]
        ]

        # Add cluster entries
        for idx, cluster in enumerate(clusters, 1):
            cluster_name = cluster.get('cluster_name', f'Cluster {idx}')
            cluster_name = cluster_name[:30] + "..." if len(cluster_name) > 30 else cluster_name
            toc_data.append([f"   2.{idx} {cluster_name}", str(4 + idx)])

        toc_table = Table(toc_data, colWidths=[4*inch, 0.5*inch])
        toc_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))

        content.append(toc_table)
        content.append(Spacer(1, 0.2*inch))

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
        The analysis identified {len(clusters) if clusters else 0} distinct content clusters, each with detailed
        outlines and post ideas based on competitive research of top-ranking content.
        """
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 0.3*inch))

        # Statistics table
        cluster_count = len(clusters) if clusters else 0
        stats_data = [
            ['Metric', 'Value'],
            ['Total Keywords', str(len(keywords))],
            ['Unique Keywords', str(batch_data.get('keyword_count', len(keywords)))],
            ['Content Clusters', str(cluster_count)],
            ['Outlines Generated', str(cluster_count)],
            ['Post Ideas', str(cluster_count)]
        ]

        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        content.append(stats_table)

        return content

    def _create_keywords_section(self, batch_data: Dict, clusters: List[Dict]) -> List:
        """Create keywords section organized by clusters"""
        content = []

        content.append(Paragraph("1. Keywords Analysis", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.2*inch))

        # Summary statistics
        total_keywords = sum(len(cluster.get('keywords', [])) for cluster in clusters)
        content.append(Paragraph("1.1 Keywords Summary", self.styles['SubSection']))
        summary_text = f"""
        Total Keywords Processed: {total_keywords}<br/>
        Number of Content Clusters: {len(clusters)}<br/>
        Average Keywords per Cluster: {total_keywords // len(clusters) if clusters else 0}
        """
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 0.3*inch))

        if not clusters:
            content.append(Paragraph("No clusters available for analysis.", self.styles['CustomBodyText']))
            return content

        # Keywords organized by clusters in a table format
        content.append(Paragraph("1.2 Keywords by Content Cluster", self.styles['SubSection']))
        content.append(Spacer(1, 0.1*inch))

        # Create table data
        table_data = [['Cluster Name', 'Keywords Count', 'Keywords List']]

        for cluster in clusters:
            cluster_name = cluster.get('cluster_name', f'Cluster {len(table_data)}')
            keywords_list = cluster.get('keywords', [])
            keyword_count = len(keywords_list)

            # Format keywords list - show all keywords line by line in a single cell
            if keywords_list:
                if len(keywords_list) <= 10:
                    # Show all keywords, one per line
                    keywords_display = "\n".join(f"• {kw}" for kw in keywords_list)
                else:
                    # Show first 10, then truncate with count
                    shown_keywords = "\n".join(f"• {kw}" for kw in keywords_list[:10])
                    remaining = len(keywords_list) - 10
                    keywords_display = f"{shown_keywords}\n... and {remaining} more keywords"
            else:
                keywords_display = "No keywords available"

            table_data.append([cluster_name, str(keyword_count), keywords_display])

        # Create table
        col_widths = [2.5*inch, 1*inch, 4*inch]
        keywords_table = Table(table_data, colWidths=col_widths)

        # Style the table
        table_style = [
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Center the count column
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),

            # Grid lines
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ]

        # Alternate row colors for existing rows
        for i in range(2, len(table_data), 2):
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#edf2f7')))

        keywords_table.setStyle(TableStyle(table_style))

        content.append(keywords_table)

        return content

    def _create_clusters_section(self, clusters: List[Dict]) -> List:
        """Create professional clusters section with enhanced details"""
        content = []

        content.append(Paragraph("2. Content Clusters & Strategy", self.styles['SectionHeader']))
        content.append(Spacer(1, 0.2*inch))

        if not clusters:
            content.append(Paragraph("No clusters available for report generation.", self.styles['CustomBodyText']))
            return content

        for idx, cluster in enumerate(clusters, 1):
            # Cluster header with better formatting - use LLM-generated cluster name
            cluster_name = cluster.get('cluster_name', f'Cluster {idx}')
            cluster_title = f"2.{idx} Content Cluster: {cluster_name}"
            content.append(Paragraph(cluster_title, self.styles['SubSection']))
            content.append(Spacer(1, 0.1*inch))

            # Keywords in this cluster with professional styling
            keywords_list = cluster.get('keywords', [])
            keyword_count = len(keywords_list)
            content.append(Paragraph(
                f"<b>Keywords ({keyword_count}):</b>",
                self.styles['Highlight']
            ))
            if keywords_list:
                keywords_text = ", ".join(keywords_list)
                content.append(Paragraph(keywords_text, self.styles['CustomBodyText']))
            else:
                content.append(Paragraph("No keywords available", self.styles['CustomBodyText']))
            content.append(Spacer(1, 0.15*inch))

            # Enhanced Post idea section
            post_idea = cluster.get('post_idea', {})
            if post_idea:
                content.append(Paragraph("📝 <b>Strategic Post Idea</b>", self.styles['Highlight']))

                idea_text = f"""
                <b>Title:</b> {post_idea.get('title', 'N/A')}<br/>
                <b>Unique Angle:</b> {post_idea.get('angle', 'N/A')}<br/>
                <b>Target Audience:</b> {post_idea.get('target_audience', 'N/A')}<br/>
                <b>Value Proposition:</b> {post_idea.get('value_proposition', 'N/A')}<br/>
                <b>Content Format:</b> {post_idea.get('content_format', 'N/A')}<br/>
                <b>Reading Time:</b> {post_idea.get('estimated_reading_time', 'N/A')} | <b>Level:</b> {post_idea.get('difficulty_level', 'N/A')}
                """
                content.append(Paragraph(idea_text, self.styles['CustomBodyText']))
                content.append(Spacer(1, 0.15*inch))

                # Social hooks if available
                social_hooks = post_idea.get('social_hooks', [])
                if social_hooks:
                    content.append(Paragraph("<b>Social Media Hooks:</b>", self.styles['Highlight']))
                    hooks_text = " • " + "\n • ".join(social_hooks[:3])
                    content.append(Paragraph(hooks_text, self.styles['CustomBodyText']))
                    content.append(Spacer(1, 0.1*inch))

            # Enhanced Outline section
            outline = cluster.get('outline', {})
            if outline:
                content.append(Paragraph("📋 <b>Detailed Content Outline</b>", self.styles['Highlight']))

                # Outline title
                outline_title = outline.get('title', 'Content Outline')
                content.append(Paragraph(f"<i>{outline_title}</i>", self.styles['CustomBodyText']))
                content.append(Spacer(1, 0.1*inch))

                # Enhanced Introduction
                intro = outline.get('introduction', {})
                if intro:
                    content.append(Paragraph("🎯 <b>Introduction Strategy</b>", self.styles['SubSection']))
                    if isinstance(intro, dict):
                        hooks = intro.get('hooks', [])
                        if hooks:
                            content.append(Paragraph("<b>Opening Hooks:</b>", self.styles['BodyText']))
                            for hook in hooks[:3]:
                                content.append(Paragraph(f"  • {hook}", self.styles['CustomBodyText']))
                        overview = intro.get('overview', '')
                        if overview:
                            content.append(Paragraph(f"<b>Overview:</b> {overview}", self.styles['CustomBodyText']))
                        target_audience = intro.get('target_audience', '')
                        if target_audience:
                            content.append(Paragraph(f"<b>Target Audience:</b> {target_audience}", self.styles['CustomBodyText']))
                    content.append(Spacer(1, 0.1*inch))

                # Enhanced Sections
                sections = outline.get('sections', [])
                for sec_idx, section in enumerate(sections[:8], 1):  # Increased limit
                    heading = section.get('heading', f'Section {sec_idx}')
                    word_count = section.get('word_count_estimate', 0)
                    content.append(Paragraph(f"<b>{sec_idx}. {heading}</b> ({word_count} words)", self.styles['SubSection']))

                    # SEO keywords
                    seo_keywords = section.get('seo_keywords', [])
                    if seo_keywords:
                        content.append(Paragraph(f"<i>SEO Keywords: {', '.join(seo_keywords)}</i>", self.styles['CustomBodyText']))

                    # Description
                    description = section.get('description', '')
                    if description:
                        content.append(Paragraph(description, self.styles['CustomBodyText']))

                    # Enhanced Subsections
                    subsections = section.get('subsections', [])
                    if subsections:
                        content.append(Spacer(1, 0.05*inch))
                        for subsec in subsections[:4]:  # Increased limit
                            if isinstance(subsec, dict):
                                sub_heading = subsec.get('heading', '')
                                content_ideas = subsec.get('content_ideas', [])
                                content.append(Paragraph(f"  ▶ <b>{sub_heading}</b>", self.styles['CustomBodyText']))
                                for idea in content_ideas[:2]:
                                    content.append(Paragraph(f"    • {idea}", self.styles['CustomBodyText']))
                            else:
                                content.append(Paragraph(f"  ▶ {subsec}", self.styles['CustomBodyText']))

                    content.append(Spacer(1, 0.08*inch))

                # Enhanced Conclusion
                conclusion = outline.get('conclusion', {})
                if conclusion:
                    content.append(Paragraph("🎯 <b>Conclusion & Call-to-Action</b>", self.styles['SubSection']))
                    if isinstance(conclusion, dict):
                        summary = conclusion.get('summary', '')
                        if summary:
                            content.append(Paragraph(f"<b>Key Takeaways:</b> {summary}", self.styles['CustomBodyText']))
                        actionable_insights = conclusion.get('actionable_insights', [])
                        if actionable_insights:
                            content.append(Paragraph("<b>Actionable Insights:</b>", self.styles['CustomBodyText']))
                            for insight in actionable_insights[:3]:
                                content.append(Paragraph(f"  • {insight}", self.styles['CustomBodyText']))
                        cta = conclusion.get('cta', '')
                        if cta:
                            content.append(Paragraph(f"<b>Call-to-Action:</b> {cta}", self.styles['CustomBodyText']))
                    content.append(Spacer(1, 0.1*inch))

                # SEO Notes
                seo_notes = outline.get('seo_notes', {})
                if seo_notes:
                    content.append(Paragraph("🔍 <b>SEO Optimization Notes</b>", self.styles['Highlight']))
                    primary_kw = seo_notes.get('primary_keyword', '')
                    if primary_kw:
                        content.append(Paragraph(f"<b>Primary Keyword:</b> {primary_kw}", self.styles['CustomBodyText']))
                    meta_desc = seo_notes.get('meta_description', '')
                    if meta_desc:
                        content.append(Paragraph(f"<b>Meta Description:</b> {meta_desc}", self.styles['CustomBodyText']))

            content.append(Spacer(1, 0.3*inch))

            # Page break after each cluster (except last)
            if idx < len(clusters):
                content.append(PageBreak())

        return content