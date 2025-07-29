"""
Tests for data models
"""

import pytest
from content_dedup.core.models import ContentItem, ContentCluster


class TestContentItem:
    """Test ContentItem model"""
    
    def test_content_item_creation(self):
        """Test basic ContentItem creation"""
        item = ContentItem(
            title="Test Title",
            content_text="Test content",
            url="https://example.com/test",
            original_url="https://example.com/test",
            category=["test"],
            publish_time="2025/01/15 10:00:00",
            author="Test Author",
            images=[],
            fetch_time="2025/01/15 11:00:00"
        )
        
        assert item.title == "Test Title"
        assert item.content_text == "Test content"
        assert item.url == "https://example.com/test"
        assert item.category == ["test"]
    
    def test_content_item_to_dict(self):
        """Test ContentItem to_dict method"""
        item = ContentItem(
            title="Test Title",
            content_text="Test content",
            url="https://example.com/test",
            original_url="https://example.com/test",
            category=["test"],
            publish_time="2025/01/15 10:00:00",
            author="Test Author",
            images=["image1.jpg"],
            fetch_time="2025/01/15 11:00:00",
            language="en"
        )
        
        item_dict = item.to_dict()
        
        assert item_dict["title"] == "Test Title"
        assert item_dict["language"] == "en"
        assert item_dict["images"] == ["image1.jpg"]
    
    def test_content_item_from_dict(self):
        """Test ContentItem from_dict method"""
        data = {
            "title": "Test Title",
            "content_text": "Test content",
            "url": "https://example.com/test",
            "original_url": "https://example.com/test",
            "category": ["test"],
            "publish_time": "2025/01/15 10:00:00",
            "author": "Test Author",
            "images": [],
            "fetch_time": "2025/01/15 11:00:00",
            "language": "zh"
        }
        
        item = ContentItem.from_dict(data)
        
        assert item.title == "Test Title"
        assert item.language == "zh"


class TestContentCluster:
    """Test ContentCluster model"""
    
    def test_content_cluster_creation(self, sample_content_items):
        """Test ContentCluster creation"""
        representative = sample_content_items[0]
        members = sample_content_items[:2]
        
        cluster = ContentCluster(
            representative=representative,
            members=members,
            cluster_id="test_cluster_001",
            dominant_language="zh",
            language_distribution={"zh": 0.6, "en": 0.4}
        )
        
        assert cluster.representative == representative
        assert len(cluster.members) == 2
        assert cluster.cluster_id == "test_cluster_001"
        assert cluster.dominant_language == "zh"
    
    def test_cluster_size_property(self, sample_content_items):
        """Test cluster size property"""
        cluster = ContentCluster(
            representative=sample_content_items[0],
            members=sample_content_items[:3],
            cluster_id="test_cluster_002",
            dominant_language="zh"
        )
        
        assert cluster.size == 3
    
    def test_is_mixed_language(self, sample_content_items):
        """Test mixed language detection"""
        # Mixed language cluster
        mixed_cluster = ContentCluster(
            representative=sample_content_items[0],
            members=sample_content_items[:2],
            cluster_id="mixed_cluster",
            dominant_language="zh",
            language_distribution={"zh": 0.6, "en": 0.4}
        )
        
        assert mixed_cluster.is_mixed_language(threshold=0.3) == True
        assert mixed_cluster.is_mixed_language(threshold=0.5) == False
        
        # Single language cluster
        single_cluster = ContentCluster(
            representative=sample_content_items[0],
            members=[sample_content_items[0]],
            cluster_id="single_cluster",
            dominant_language="zh",
            language_distribution={"zh": 1.0}
        )
        
        assert single_cluster.is_mixed_language(threshold=0.3) == False
