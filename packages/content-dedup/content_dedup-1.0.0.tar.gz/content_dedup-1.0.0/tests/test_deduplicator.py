"""
Tests for ContentDeduplicator
"""

import pytest
import tempfile
import json
from pathlib import Path

from content_dedup.core.deduplicator import ContentDeduplicator
from content_dedup.core.models import ContentItem, ContentCluster


class TestContentDeduplicator:
    """Test ContentDeduplicator functionality"""
    
    def test_deduplicator_initialization(self):
        """Test ContentDeduplicator initialization"""
        deduplicator = ContentDeduplicator()
        
        assert deduplicator.language == 'auto'
        assert deduplicator.similarity_threshold == 0.8
        assert deduplicator.mixed_language_threshold == 0.3
        assert len(deduplicator.content_items) == 0
        assert len(deduplicator.clusters) == 0
    
    def test_deduplicator_custom_settings(self):
        """Test ContentDeduplicator with custom settings"""
        deduplicator = ContentDeduplicator(
            language='zh',
            similarity_threshold=0.9,
            mixed_language_threshold=0.2
        )
        
        assert deduplicator.language == 'zh'
        assert deduplicator.similarity_threshold == 0.9
        assert deduplicator.mixed_language_threshold == 0.2
    
    def test_load_jsonl(self, sample_jsonl_file):
        """Test loading JSONL file"""
        deduplicator = ContentDeduplicator()
        deduplicator.load_jsonl(sample_jsonl_file)
        
        assert len(deduplicator.content_items) == 4
        assert all(isinstance(item, ContentItem) for item in deduplicator.content_items)
        assert deduplicator.language_stats  # Should have language statistics
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_load_jsonl_with_language_setting(self, sample_jsonl_file):
        """Test loading JSONL with specific language setting"""
        deduplicator = ContentDeduplicator(language='zh')
        deduplicator.load_jsonl(sample_jsonl_file)
        
        # All items should have 'zh' language when forced
        assert all(item.language == 'zh' for item in deduplicator.content_items)
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_exact_duplicate_check(self, sample_content_items):
        """Test exact duplicate removal"""
        deduplicator = ContentDeduplicator()
        
        # Add duplicate items
        duplicate_item = ContentItem(
            title="AI技術突破：新演算法提升效率",  # Same title as first item
            content_text="Different content",
            url="https://example.com/ai-breakthrough",  # Same URL as first item
            original_url="https://example.com/ai-breakthrough",
            category=["科技"],
            publish_time="2025/01/15 10:00:00",
            author="Different Author",
            images=[],
            fetch_time="2025/01/15 11:00:00"
        )
        
        deduplicator.content_items = sample_content_items + [duplicate_item]
        unique_items = deduplicator.exact_duplicate_check()
        
        # Should remove the duplicate
        assert len(unique_items) == len(sample_content_items)
    
    def test_cluster_and_deduplicate(self, sample_jsonl_file):
        """Test full clustering and deduplication process"""
        deduplicator = ContentDeduplicator(similarity_threshold=0.5)
        deduplicator.load_jsonl(sample_jsonl_file)
        
        clusters = deduplicator.cluster_and_deduplicate()
        
        assert len(clusters) > 0
        assert all(isinstance(cluster, ContentCluster) for cluster in clusters)
        assert all(cluster.representative is not None for cluster in clusters)
        assert all(len(cluster.members) > 0 for cluster in clusters)
        
        # Total members should equal original items (after deduplication)
        total_members = sum(len(cluster.members) for cluster in clusters)
        assert total_members <= len(deduplicator.content_items)
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_get_representatives(self, sample_jsonl_file):
        """Test getting cluster representatives"""
        deduplicator = ContentDeduplicator()
        deduplicator.load_jsonl(sample_jsonl_file)
        deduplicator.cluster_and_deduplicate()
        
        representatives = deduplicator.get_representatives()
        
        assert len(representatives) == len(deduplicator.clusters)
        assert all(isinstance(rep, ContentItem) for rep in representatives)
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_save_results_clusters(self, sample_jsonl_file, temp_output_dir):
        """Test saving cluster results"""
        deduplicator = ContentDeduplicator()
        deduplicator.load_jsonl(sample_jsonl_file)
        deduplicator.cluster_and_deduplicate()
        
        output_path = Path(temp_output_dir) / "clusters.json"
        deduplicator.save_results(str(output_path), format='clusters')
        
        assert output_path.exists()
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'metadata' in data
        assert 'clusters' in data
        assert len(data['clusters']) == len(deduplicator.clusters)
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_save_results_representatives(self, sample_jsonl_file, temp_output_dir):
        """Test saving representative results"""
        deduplicator = ContentDeduplicator()
        deduplicator.load_jsonl(sample_jsonl_file)
        deduplicator.cluster_and_deduplicate()
        
        output_path = Path(temp_output_dir) / "representatives.jsonl"
        deduplicator.save_results(str(output_path), format='representatives')
        
        assert output_path.exists()
        
        # Verify content
        representatives = []
        with open(output_path, 'r', encoding='utf-8') as f:
            for line in f:
                representatives.append(json.loads(line))
        
        assert len(representatives) == len(deduplicator.clusters)
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_generate_report(self, sample_jsonl_file):
        """Test report generation"""
        deduplicator = ContentDeduplicator()
        deduplicator.load_jsonl(sample_jsonl_file)
        deduplicator.cluster_and_deduplicate()
        
        report = deduplicator.generate_report()
        
        required_sections = [
            'processing_settings',
            'basic_statistics',
            'cluster_size_statistics',
            'language_distribution'
        ]
        
        for section in required_sections:
            assert section in report
        
        # Check basic statistics
        stats = report['basic_statistics']
        assert stats['original_content_count'] == len(deduplicator.content_items)
        assert stats['cluster_count'] == len(deduplicator.clusters)
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_invalid_file_handling(self):
        """Test handling of invalid input files"""
        deduplicator = ContentDeduplicator()
        
        with pytest.raises(ValueError):
            deduplicator.load_jsonl("non_existent_file.jsonl")
