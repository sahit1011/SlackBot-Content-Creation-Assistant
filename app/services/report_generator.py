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
        # Use current directory reports folder instead of /tmp
        reports_dir = os.path.join(os.getcwd(), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)

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