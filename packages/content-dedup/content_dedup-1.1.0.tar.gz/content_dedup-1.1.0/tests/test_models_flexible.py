"""
Tests for flexible data models
"""

import pytest
from content_dedup.core.models_flexible import FlexibleContentItem, FlexibleContentCluster, create_flexible_content_item
from content_dedup.config.field_mapping import get_field_mapping


class TestFlexibleContentItem:
    """Test FlexibleContentItem model"""
    
    def test_flexible_content_item_creation(self):
        """Test basic FlexibleContentItem creation"""
        item = FlexibleContentItem.from_minimal_fields(
            title="Test Title",
            content_text="Test content", 
            url="https://example.com/test"
        )
        
        assert item.title == "Test Title"
        assert item.content_text == "Test content"
        assert item.url == "https://example.com/test"
        assert len(item.working_fields) == 3
        assert len(item.original_data) == 3
    
    def test_flexible_content_item_from_raw_data(self):
        """Test creating FlexibleContentItem from raw data"""
        raw_data = {
            "title": "Test News",
            "content": "This is test content",
            "url": "https://example.com/news",
            "author": "Test Author",
            "tags": ["test", "news"],
            "published_at": "2025-01-15T10:00:00Z",
            "extra_field": "extra_value"
        }
        
        field_mapping = get_field_mapping('news')
        item = FlexibleContentItem.from_raw_data(
            original_data=raw_data,
            field_mapping=field_mapping,
            required_fields=['title', 'content_text', 'url']
        )
        
        assert item.title == "Test News"
        assert item.content_text == "This is test content"
        assert item.url == "https://example.com/news"
        assert len(item.working_fields) == 3  # Only required fields
        assert len(item.original_data) == 7   # All original fields preserved
        
        # Test zero data loss
        assert item.get_original_field('extra_field') == "extra_value"
        assert item.get_original_field('author') == "Test Author"
    
    def test_flexible_content_item_to_dict(self):
        """Test to_dict with different modes"""
        item = FlexibleContentItem.from_minimal_fields(
            title="Test Title",
            content_text="Test content",
            url="https://example.com/test",
            extra_field="extra_value"
        )
        
        # Working mode
        working_dict = item.to_dict(mode="working")
        assert "title" in working_dict
        assert "content_text" in working_dict
        assert "url" in working_dict
        assert "extra_field" in working_dict
        
        # Original mode
        original_dict = item.to_dict(mode="original")
        assert original_dict == item.original_data
        
        # Compatible mode
        compatible_dict = item.to_dict(mode="compatible")
        expected_fields = ['title', 'content_text', 'url', 'original_url', 
                          'category', 'publish_time', 'author', 'images', 
                          'fetch_time', 'language']
        for field in expected_fields:
            assert field in compatible_dict
    
    def test_dynamic_field_access(self):
        """Test dynamic field access and extension"""
        raw_data = {
            "title": "Test",
            "content": "Content",
            "url": "https://example.com/test",
            "author": "Test Author", 
            "view_count": 1000,
            "custom_field": "custom_value"
        }
        
        field_mapping = get_field_mapping('news')
        item = create_flexible_content_item(
            original_data=raw_data,
            field_mapping=field_mapping,
            work_mode="minimal"
        )
        
        # Initially only has minimal working fields
        assert len(item.working_fields) == 3
        
        # Can access original fields without loss
        assert item.get_original_field('author') == "Test Author"
        assert item.get_original_field('view_count') == 1000
        assert item.get_original_field('custom_field') == "custom_value"
        
        # Can extend working fields dynamically
        item.extend_working_fields(['author', 'view_count'])
        assert len(item.working_fields) == 5
        assert item.get_working_field('author') == "Test Author"
        assert item.get_working_field('view_count') == 1000
    
    def test_memory_footprint(self):
        """Test memory footprint calculation"""
        item = FlexibleContentItem.from_minimal_fields(
            title="Test Title",
            content_text="Test content",
            url="https://example.com/test"
        )
        
        footprint = item.memory_footprint()
        assert 'original_data_bytes' in footprint
        assert 'working_fields_bytes' in footprint
        assert 'total_bytes' in footprint
        assert 'overhead_ratio' in footprint
        assert footprint['total_bytes'] > 0


class TestFlexibleContentCluster:
    """Test FlexibleContentCluster model"""
    
    def test_flexible_content_cluster_creation(self):
        """Test basic FlexibleContentCluster creation"""
        representative = FlexibleContentItem.from_minimal_fields(
            title="Rep Title",
            content_text="Rep content",
            url="https://example.com/rep"
        )
        
        member1 = FlexibleContentItem.from_minimal_fields(
            title="Member 1",
            content_text="Member 1 content", 
            url="https://example.com/member1"
        )
        
        member2 = FlexibleContentItem.from_minimal_fields(
            title="Member 2",
            content_text="Member 2 content",
            url="https://example.com/member2"
        )
        
        cluster = FlexibleContentCluster(
            representative=representative,
            members=[member1, member2],
            cluster_id="test_cluster",
            dominant_language="en"
        )
        
        assert cluster.size == 2
        assert cluster.cluster_id == "test_cluster"
        assert cluster.dominant_language == "en"
        assert cluster.representative.title == "Rep Title"
    
    def test_cluster_to_dict(self):
        """Test cluster to_dict conversion"""
        representative = FlexibleContentItem.from_minimal_fields(
            title="Rep Title",
            content_text="Rep content",
            url="https://example.com/rep"
        )
        
        member = FlexibleContentItem.from_minimal_fields(
            title="Member",
            content_text="Member content",
            url="https://example.com/member"
        )
        
        cluster = FlexibleContentCluster(
            representative=representative,
            members=[member],
            cluster_id="test_cluster",
            dominant_language="en",
            language_distribution={"en": 1.0},
            similarity_scores={"avg": 0.85}
        )
        
        cluster_dict = cluster.to_dict(output_mode="working", include_metadata=True)
        
        assert cluster_dict['cluster_id'] == "test_cluster"
        assert cluster_dict['member_count'] == 1
        assert cluster_dict['dominant_language'] == "en"
        assert 'representative' in cluster_dict
        assert 'members' in cluster_dict
        assert '_cluster_metadata' in cluster_dict
    
    def test_is_mixed_language(self):
        """Test mixed language detection"""
        representative = FlexibleContentItem.from_minimal_fields(
            title="Title",
            content_text="Content",
            url="https://example.com/test"
        )
        
        cluster = FlexibleContentCluster(
            representative=representative,
            members=[],
            cluster_id="test_cluster",
            dominant_language="en",
            language_distribution={"en": 0.6, "zh": 0.4}
        )
        
        # Should be mixed language (second language > 30%)
        assert cluster.is_mixed_language(threshold=0.3) == True
        
        # Should not be mixed language with higher threshold
        assert cluster.is_mixed_language(threshold=0.5) == False


class TestCreateFlexibleContentItem:
    """Test factory function for creating flexible content items"""
    
    def test_create_flexible_content_item_modes(self):
        """Test different work modes"""
        raw_data = {
            "title": "Test News",
            "content": "Test content",
            "url": "https://example.com/test",
            "author": "Test Author",
            "tags": ["test"],
            "published_at": "2025-01-15T10:00:00Z"
        }
        
        field_mapping = get_field_mapping('news')
        
        # Test minimal mode
        minimal_item = create_flexible_content_item(
            original_data=raw_data,
            field_mapping=field_mapping,
            work_mode="minimal"
        )
        assert len(minimal_item.working_fields) == 3
        
        # Test balanced mode
        balanced_item = create_flexible_content_item(
            original_data=raw_data,
            field_mapping=field_mapping,
            work_mode="balanced"
        )
        assert len(balanced_item.working_fields) == 5
        
        # Test full mode
        full_item = create_flexible_content_item(
            original_data=raw_data,
            field_mapping=field_mapping,
            work_mode="full"
        )
        assert len(full_item.working_fields) == 9
        
        # All should preserve original data completely
        for item in [minimal_item, balanced_item, full_item]:
            assert len(item.original_data) == 6
            assert item.get_original_field('author') == "Test Author"
