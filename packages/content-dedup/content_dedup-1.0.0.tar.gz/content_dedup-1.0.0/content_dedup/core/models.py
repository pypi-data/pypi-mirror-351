"""
Data models for content deduplication.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ContentItem:
    """Content item data model"""
    title: str
    content_text: str
    url: str
    original_url: str
    category: List[str]
    publish_time: str
    author: str
    images: List[str]
    fetch_time: str
    language: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'title': self.title,
            'content_text': self.content_text,
            'url': self.url,
            'original_url': self.original_url,
            'category': self.category,
            'publish_time': self.publish_time,
            'author': self.author,
            'images': self.images,
            'fetch_time': self.fetch_time,
            'language': self.language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentItem":
        """Create ContentItem from dictionary"""
        return cls(
            title=data.get('title', ''),
            content_text=data.get('content_text', ''),
            url=data.get('url', ''),
            original_url=data.get('original_url', ''),
            category=data.get('category', []),
            publish_time=data.get('publish_time', ''),
            author=data.get('author', ''),
            images=data.get('images', []),
            fetch_time=data.get('fetch_time', ''),
            language=data.get('language')
        )
    
    @classmethod
    def from_raw_dict(cls, data: Dict[str, Any], field_mapping) -> "ContentItem":
        """
        Create ContentItem from raw dictionary using field mapping
        
        Args:
            data: Raw JSON data
            field_mapping: Field mapping configuration
            
        Returns:
            ContentItem instance
        """
        mapped_data = field_mapping.map_to_content_item_dict(data)
        return cls.from_dict(mapped_data)
    
    @classmethod
    def from_raw_dict(cls, data: Dict[str, Any], field_mapping: 'FieldMapping') -> "ContentItem":
        """
        Create ContentItem from raw dictionary using field mapping
        
        Args:
            data: Raw JSON data
            field_mapping: Field mapping configuration
            
        Returns:
            ContentItem instance
        """
        from ..config.field_mapping import FieldMapping
        
        mapped_data = field_mapping.map_to_content_item_dict(data)
        return cls.from_dict(mapped_data)


@dataclass
class ContentCluster:
    """Content cluster data model"""
    representative: ContentItem
    members: List[ContentItem]
    cluster_id: str
    dominant_language: str
    language_distribution: Dict[str, float] = field(default_factory=dict)
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'cluster_id': self.cluster_id,
            'representative': self.representative.to_dict(),
            'members': [item.to_dict() for item in self.members],
            'member_count': len(self.members),
            'dominant_language': self.dominant_language,
            'language_distribution': self.language_distribution,
            'similarity_scores': self.similarity_scores
        }
    
    @property
    def size(self) -> int:
        """Get cluster size"""
        return len(self.members)
    
    def is_mixed_language(self, threshold: float = 0.3) -> bool:
        """Check if cluster contains mixed languages"""
        if not self.language_distribution:
            return False
        
        sorted_langs = sorted(self.language_distribution.values(), reverse=True)
        return len(sorted_langs) >= 2 and sorted_langs[1] > threshold
