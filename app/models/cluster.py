# app/models/cluster.py
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Cluster:
    """Model for keyword cluster"""
    id: int
    name: str
    keywords: List[str]
    post_idea: Optional[Dict] = None
    outline: Optional[Dict] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'Cluster':
        """Create Cluster instance from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            keywords=data['keywords'],
            post_idea=data.get('post_idea'),
            outline=data.get('outline')
        )

    def to_dict(self) -> Dict:
        """Convert Cluster instance to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'keywords': self.keywords,
            'post_idea': self.post_idea,
            'outline': self.outline
        }