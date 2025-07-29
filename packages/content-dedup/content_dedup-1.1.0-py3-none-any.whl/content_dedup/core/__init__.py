"""
Core components for content deduplication and clustering.
"""

from .deduplicator import ContentDeduplicator
from .models_flexible import FlexibleContentItem, FlexibleContentCluster, create_flexible_content_item
from .clustering import ClusteringEngine

__all__ = ["ContentDeduplicator", "FlexibleContentItem", "FlexibleContentCluster", "create_flexible_content_item", "ClusteringEngine"]
