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