"""
Tests for ClusteringEngine
"""

import pytest
import numpy as np
from content_dedup.core.clustering import ClusteringEngine
from content_dedup.processors.language import LanguageProcessor


class TestClusteringEngine:
    """Test ClusteringEngine functionality"""
    
    @pytest.fixture
    def clustering_engine(self):
        """Create ClusteringEngine instance"""
        return ClusteringEngine(similarity_threshold=0.7)
    
    def test_clustering_engine_initialization(self, clustering_engine):
        """Test clustering engine initialization"""
        assert clustering_engine.similarity_threshold == 0.7
        assert isinstance(clustering_engine.lang_processor, LanguageProcessor)
    
    def test_calculate_similarity_matrix(self, clustering_engine, sample_content_items):
        """Test similarity matrix calculation"""
        # Use first 3 items for testing
        items = sample_content_items[:3]
        similarity_matrix = clustering_engine.calculate_similarity_matrix(items)
        
        assert similarity_matrix.shape == (3, 3)
        # Diagonal should be 1.0 (self-similarity)
        np.testing.assert_array_almost_equal(np.diag(similarity_matrix), [1.0, 1.0, 1.0])
        # Matrix should be symmetric
        np.testing.assert_array_almost_equal(similarity_matrix, similarity_matrix.T)
    
    def test_calculate_content_similarity(self, clustering_engine, sample_content_items):
        """Test content similarity calculation between two items"""
        item1 = sample_content_items[0]  # AI article in Chinese
        item2 = sample_content_items[1]  # Similar AI article in English
        item3 = sample_content_items[3]  # Sports article in Chinese
        
        sim_similar = clustering_engine._calculate_content_similarity(item1, item2)
        sim_different = clustering_engine._calculate_content_similarity(item1, item3)
        
        assert 0 <= sim_similar <= 1
        assert 0 <= sim_different <= 1
        
        # 測試自身相似度應該很高
        sim_identical = clustering_engine._calculate_content_similarity(item1, item1)
        assert sim_identical > 0.9
 
    def test_find_clusters(self, clustering_engine, sample_content_items):
        """Test cluster finding"""
        clusters = clustering_engine.find_clusters(sample_content_items)
        
        assert len(clusters) > 0
        # All items should be assigned to a cluster
        total_items = sum(len(cluster) for cluster in clusters)
        assert total_items == len(sample_content_items)
        
        # No empty clusters
        assert all(len(cluster) > 0 for cluster in clusters)
    
    def test_select_representative(self, clustering_engine, sample_content_items):
        """Test representative selection"""
        # Test with single item
        single_item = [sample_content_items[0]]
        representative = clustering_engine.select_representative(single_item)
        assert representative == sample_content_items[0]
        
        # Test with multiple items
        multiple_items = sample_content_items[:3]
        representative = clustering_engine.select_representative(multiple_items)
        assert representative in multiple_items
    
    def test_quality_score_calculation(self, clustering_engine, sample_content_items):
        """Test quality score calculation"""
        item = sample_content_items[0]
        cluster_items = sample_content_items[:2]
        
        score = clustering_engine._calculate_quality_score(item, cluster_items)
        assert isinstance(score, float)
        assert score >= 0
    
    def test_cluster_language_methods(self, clustering_engine, sample_content_items):
        """Test cluster language detection methods"""
        cluster_items = sample_content_items[:3]
        
        dominant_lang = clustering_engine._get_cluster_dominant_language(cluster_items)
        lang_dist = clustering_engine._get_cluster_language_distribution(cluster_items)
        
        assert isinstance(dominant_lang, str)
        assert isinstance(lang_dist, dict)
        assert abs(sum(lang_dist.values()) - 1.0) < 0.01  # Should sum to 1.0
