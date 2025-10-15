# app/models/user.py
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Model for Slack user"""
    id: str
    slack_user_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create User instance from dictionary"""
        return cls(
            id=data['id'],
            slack_user_id=data['slack_user_id'],
            display_name=data.get('display_name'),
            email=data.get('email'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

    def to_dict(self) -> Dict:
        """Convert User instance to dictionary"""
        return {
            'id': self.id,
            'slack_user_id': self.slack_user_id,
            'display_name': self.display_name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }