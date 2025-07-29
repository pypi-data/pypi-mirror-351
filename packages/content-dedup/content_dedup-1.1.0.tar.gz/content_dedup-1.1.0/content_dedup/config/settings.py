"""
Configuration settings for content deduplication.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class ProcessingSettings:
    """Settings for text processing"""
    language: str = 'auto'
    similarity_threshold: float = 0.8
    mixed_language_threshold: float = 0.3
    max_features: int = 3000
    ngram_range: tuple = (1, 2)


@dataclass
class ClusteringSettings:
    """Settings for clustering algorithm"""
    min_cluster_size: int = 1
    max_cluster_size: int = 100
    use_tfidf: bool = True
    tfidf_max_df: float = 0.95
    tfidf_min_df: float = 1
    tfidf_ngram_range: tuple = (1, 2)


@dataclass
class OutputSettings:
    """Settings for output formatting"""
    pretty_print: bool = False
    include_metadata: bool = True
    max_cluster_size_in_report: int = 10


@dataclass
class Settings:
    """Main settings container"""
    processing: ProcessingSettings = field(default_factory=ProcessingSettings)
    clustering: ClusteringSettings = field(default_factory=ClusteringSettings)
    output: OutputSettings = field(default_factory=OutputSettings)


def get_default_settings() -> Settings:
    """Get default settings configuration"""
    return Settings()


def load_settings_from_dict(config_dict: Dict[str, Any]) -> Settings:
    """
    Load settings from dictionary
    
    Args:
        config_dict: Configuration dictionary
        
    Returns:
        Settings object
    """
    settings = Settings()
    
    if 'processing' in config_dict:
        proc_config = config_dict['processing']
        settings.processing = ProcessingSettings(**proc_config)
    
    if 'clustering' in config_dict:
        cluster_config = config_dict['clustering']
        settings.clustering = ClusteringSettings(**cluster_config)
    
    if 'output' in config_dict:
        output_config = config_dict['output']
        settings.output = OutputSettings(**output_config)
    
    return settings
