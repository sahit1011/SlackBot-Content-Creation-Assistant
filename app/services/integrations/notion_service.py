try:
    from notion_client import Client
    from typing import List, Dict
    from app.config import Config

    class NotionService:
        """Export content strategy to Notion"""

        def __init__(self):
            self.client = Client(auth=Config.NOTION_API_KEY)
            self.database_id = Config.NOTION_DATABASE_ID
except ImportError:
    # Fallback for when notion-client is not installed
    from typing import List, Dict

    class NotionService:
        def __init__(self):
            raise ImportError("notion-client package is required for Notion integration")

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
                            {"text": {"content": f"📁 {cluster['cluster_name']}"}},
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