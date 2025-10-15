import pandas as pd
from typing import List
import io

class KeywordParser:
    """Parse keywords from various input formats"""
    
    @staticmethod
    def parse_csv(file_path: str) -> List[str]:
        """
        Parse keywords from CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of raw keywords
        """
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            # Get first column or column named 'keyword'
            if 'keyword' in df.columns:
                keywords = df['keyword'].tolist()
            else:
                keywords = df.iloc[:, 0].tolist()
            
            # Remove NaN values
            keywords = [str(k) for k in keywords if pd.notna(k)]
            
            return keywords
            
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
    
    @staticmethod
    def parse_text(text: str) -> List[str]:
        """
        Parse keywords from plain text
        
        Args:
            text: Comma or newline separated keywords
            
        Returns:
            List of raw keywords
        """
        # Try comma separation first
        if ',' in text:
            keywords = text.split(',')
        else:
            # Try newline separation
            keywords = text.split('\n')
        
        # Clean up
        keywords = [k.strip() for k in keywords if k.strip()]
        
        return keywords
    
    @staticmethod
    def parse_csv_from_url(url: str, token: str) -> List[str]:
        """
        Parse CSV from Slack file URL
        
        Args:
            url: Slack file URL
            token: Slack bot token for authentication
            
        Returns:
            List of raw keywords
        """
        import requests
        
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse CSV from bytes
        csv_data = io.StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_data)
        
        if 'keyword' in df.columns:
            keywords = df['keyword'].tolist()
        else:
            keywords = df.iloc[:, 0].tolist()
        
        keywords = [str(k) for k in keywords if pd.notna(k)]
        
        return keywords