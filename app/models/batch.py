# app/models/batch.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Batch:
    """Model for keyword processing batch"""
    id: str
    user_id: str
    keywords: List[str]
    status: str
    created_at: datetime
    updated_at: datetime
    clusters: Optional[List[Dict]] = None
    report_path: Optional[str] = None
    report_url: Optional[str] = None
    email_sent: bool = False
    email_address: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'Batch':
        """Create Batch instance from dictionary"""
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            keywords=data['keywords'],
            status=data['status'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            clusters=data.get('clusters'),
            report_path=data.get('report_path'),
            report_url=data.get('report_url'),
            email_sent=data.get('email_sent', False),
            email_address=data.get('email_address')
        )

    def to_dict(self) -> Dict:
        """Convert Batch instance to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'keywords': self.keywords,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'clusters': self.clusters,
            'report_path': self.report_path,
            'report_url': self.report_url,
            'email_sent': self.email_sent,
            'email_address': self.email_address
        }