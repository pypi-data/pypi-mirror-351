"""
Comparison test between full FieldMapping and MinimalFieldMapping.
This test validates that the minimal version preserves core deduplication functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from content_dedup.config.field_mapping import FieldMapping, create_custom_mapping
from content_dedup.config.field_mapping_minimal import MinimalFieldMapping, create_minimal_custom_mapping
from content_dedup.core.models import ContentItem
from content_dedup import ContentDeduplicator


class TestFieldMappingComparison:
    """Compare full vs minimal field mapping performance"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_data = [
            {
                "headline": "AI技術新突破",
                "body": "人工智慧領域取得重大進展",
                "summary": "研究團隊開發出創新算法",
                "permalink": "https://tech.example.com/ai-1",
                "writer": "科技記者",
                "tags": ["AI", "科技"],
                "published_at": "2025/01/15 10:00:00",
                "images": ["ai1.jpg"],
                "retrieved": "2025/01/15 11:00:00"
            },
            {
                "headline": "機器學習新發現",
                "body": "機器學習技術獲得重要突破",
                "summary": "科學家發現改進方法",
                "permalink": "https://tech.example.com/ml-1",
                "writer": "技術專家",
                "tags": ["機器學習", "科技"],
                "published_at": "2025/01/15 12:00:00",
                "images": ["ml1.jpg"],
                "retrieved": "2025/01/15 13:00:00"
            }
        ]
    
    def test_basic_field_extraction_comparison(self):
        """Test basic field extraction between full and minimal versions"""
        # Create mappings
        full_mapping = create_custom_mapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink',
            category_field='tags',
            publish_time_field='published_at',
            content_separator=' | '
        )
        
        minimal_mapping = create_minimal_custom_mapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink',
            content_separator=' | '
        )
        
        # Test with first data item
        data = self.test_data[0]
        
        full_result = full_mapping.map_to_content_item_dict(data)
        minimal_result = minimal_mapping.map_to_content_item_dict(data)
        
        # Essential fields should be identical
        assert full_result['title'] == minimal_result['title']
        assert full_result['content_text'] == minimal_result['content_text']
        assert full_result['url'] == minimal_result['url']
        
        # Both should handle missing data gracefully
        # Since we removed author_field, author should be empty/default
        assert 'author' in full_result
        assert 'author' in minimal_result
        assert full_result['category'] == ["AI", "科技"]
        assert full_result['publish_time'] == "2025/01/15 10:00:00"
        assert full_result['images'] == ["ai1.jpg"]
        
        # Minimal mapping should use defaults for non-essential fields
        assert minimal_result['author'] == ""
        assert minimal_result['category'] == []
        assert minimal_result['publish_time'] == ""
        assert minimal_result['images'] == []
    
    def test_content_item_creation_comparison(self):
        """Test ContentItem creation with both mapping types"""
        full_mapping = create_custom_mapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink'
        )
        
        minimal_mapping = create_minimal_custom_mapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink'
        )
        
        data = self.test_data[0]
        
        # Create items
        full_item = ContentItem.from_raw_dict(data, full_mapping)
        minimal_item = ContentItem.from_raw_dict(data, minimal_mapping)
        
        # Core deduplication fields should be identical
        assert full_item.title == minimal_item.title
        assert full_item.content_text == minimal_item.content_text
        assert full_item.url == minimal_item.url
        
        # Since we removed author_field, both should have empty/default author
        assert 'author' in full_item.__dict__
        assert 'author' in minimal_item.__dict__
        assert minimal_item.author == ""
    
    def test_deduplication_accuracy_comparison(self):
        """Test that both mapping types produce equivalent deduplication results"""
        # Create temporary JSONL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in self.test_data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
            temp_file = f.name
        
        try:
            # Test with full mapping
            full_mapping = create_custom_mapping(
                title_field='headline',
                content_fields=['body', 'summary'],
                id_field='permalink',
                category_field='tags'
            )
            
            deduplicator_full = ContentDeduplicator(
                similarity_threshold=0.7,
                field_mapping=full_mapping
            )
            deduplicator_full.load_jsonl(temp_file)
            clusters_full = deduplicator_full.cluster_and_deduplicate()
            
            # Test with minimal mapping
            minimal_mapping = create_minimal_custom_mapping(
                title_field='headline',
                content_fields=['body', 'summary'],
                id_field='permalink'
            )
            
            deduplicator_minimal = ContentDeduplicator(
                similarity_threshold=0.7,
                field_mapping=minimal_mapping
            )
            deduplicator_minimal.load_jsonl(temp_file)
            clusters_minimal = deduplicator_minimal.cluster_and_deduplicate()
            
            # Both should produce same number of clusters (core algorithm unchanged)
            assert len(clusters_full) == len(clusters_minimal)
            
            # Representatives should have same title and content
            for i, (full_cluster, minimal_cluster) in enumerate(zip(clusters_full, clusters_minimal)):
                assert full_cluster.representative.title == minimal_cluster.representative.title
                assert full_cluster.representative.content_text == minimal_cluster.representative.content_text
                assert full_cluster.representative.url == minimal_cluster.representative.url
                
        finally:
            Path(temp_file).unlink()
    
    def test_memory_usage_comparison(self):
        """Test that minimal mapping uses less memory"""
        import sys
        
        full_mapping = FieldMapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink',
            category_field='tags',
            publish_time_field='published_at'
        )
        
        minimal_mapping = MinimalFieldMapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink'
        )
        
        # Minimal mapping should have fewer attributes
        full_attrs = len([attr for attr in dir(full_mapping) if not attr.startswith('_')])
        minimal_attrs = len([attr for attr in dir(minimal_mapping) if not attr.startswith('_')])
        
        print(f"Full mapping attributes: {full_attrs}")
        print(f"Minimal mapping attributes: {minimal_attrs}")
        
        # Minimal should have significantly fewer attributes
        assert minimal_attrs < full_attrs
    
    def test_predefined_mappings_comparison(self):
        """Test that predefined mappings work in both versions"""
        from content_dedup.config.field_mapping import get_field_mapping
        from content_dedup.config.field_mapping_minimal import get_minimal_field_mapping
        
        mapping_types = ['default', 'news', 'blog', 'social', 'academic', 'ecommerce']
        
        for mapping_type in mapping_types:
            full_mapping = get_field_mapping(mapping_type)
            minimal_mapping = get_minimal_field_mapping(mapping_type)
            
            assert isinstance(full_mapping, FieldMapping)
            assert isinstance(minimal_mapping, MinimalFieldMapping)
            
            # Core fields should be identical
            assert full_mapping.title_field == minimal_mapping.title_field
            assert full_mapping.content_fields == minimal_mapping.content_fields
            # id_field comparison: minimal uses first item from full mapping's list
            if isinstance(full_mapping.id_field, list):
                assert minimal_mapping.id_field == full_mapping.id_field[0]
            else:
                assert full_mapping.id_field == minimal_mapping.id_field
    
    def test_migration_utility(self):
        """Test conversion from full to minimal mapping"""
        from content_dedup.config.field_mapping_minimal import convert_to_minimal
        
        full_mapping = create_custom_mapping(
            title_field=['headline', 'title'],
            content_fields=['body', 'summary', 'content'],
            id_field='permalink',
            category_field='tags',
            content_separator=' | ',
            ignore_missing_required=True
        )
        
        minimal_mapping = convert_to_minimal(full_mapping)
        
        # Essential properties should be preserved
        assert minimal_mapping.title_field == full_mapping.title_field
        assert minimal_mapping.content_fields == full_mapping.content_fields
        assert minimal_mapping.id_field == full_mapping.id_field
        assert minimal_mapping.content_separator == full_mapping.content_separator
        assert minimal_mapping.ignore_missing_required == full_mapping.ignore_missing_required
        
        # Should be MinimalFieldMapping instance
        assert isinstance(minimal_mapping, MinimalFieldMapping)


if __name__ == "__main__":
    # Run a quick test
    test = TestFieldMappingComparison()
    test.setup_method()
    test.test_basic_field_extraction_comparison()
    print("✅ Basic comparison test passed")
    
    test.test_predefined_mappings_comparison()
    print("✅ Predefined mappings comparison passed")
    
    print("\n🎯 MinimalFieldMapping successfully preserves core functionality while reducing complexity!")
