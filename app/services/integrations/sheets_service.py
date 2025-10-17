try:
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
except ImportError:
    # Fallback for when google-api-python-client is not installed
    from typing import List, Dict

    class SheetsService:
        def __init__(self):
            raise ImportError("google-api-python-client and google-auth packages are required for Google Sheets integration")

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