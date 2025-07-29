"""
py-content-dedup: Intelligent content deduplication and clustering toolkit

This package provides tools for deduplicating and clustering content items
with support for multiple languages and mixed-language content.
"""

__version__ = "1.1.0"
__author__ = "changyy"
__email__ = "changyy.csie@gmail.com"

from .core.deduplicator import ContentDeduplicator
from .core.models_flexible import FlexibleContentItem, FlexibleContentCluster, create_flexible_content_item
from .processors.language import LanguageProcessor

__all__ = [
    "ContentDeduplicator",
    "FlexibleContentItem", 
    "FlexibleContentCluster",
    "create_flexible_content_item",
    "LanguageProcessor",
]
