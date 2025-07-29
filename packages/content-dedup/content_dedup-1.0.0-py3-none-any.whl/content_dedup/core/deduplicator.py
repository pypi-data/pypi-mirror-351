"""
Main content deduplication engine.
"""

import json
import hashlib
import logging
from typing import List, Dict, Any, Union, Optional
from pathlib import Path

from .models import ContentItem, ContentCluster
from .clustering import ClusteringEngine
from ..processors.language import LanguageProcessor
from ..utils.validators import validate_input_file
from ..config.field_mapping import FieldMapping, get_field_mapping


class ContentDeduplicator:
    """Main content deduplication engine"""
    
    def __init__(self, 
                 language: Union[str, None] = 'auto',
                 similarity_threshold: float = 0.8,
                 mixed_language_threshold: float = 0.3,
                 field_mapping: Union[str, Any, None] = None):
        """
        Initialize content deduplicator
        
        Args:
            language: Language setting ('auto', 'zh', 'en', 'mixed', None)
            similarity_threshold: Similarity threshold for clustering
            mixed_language_threshold: Mixed language detection threshold
            field_mapping: Field mapping configuration (string name, mapping object, or None for default)
                          Supports prefixes: 'minimal-', 'balanced-' for different mapping types
        """
        self.language = language
        self.similarity_threshold = similarity_threshold
        self.mixed_language_threshold = mixed_language_threshold
        
        # Setup field mapping with support for different types
        if field_mapping is None:
            self.field_mapping = get_field_mapping('default')
        elif isinstance(field_mapping, str):
            # Support prefixed mapping names: 'minimal-news', 'balanced-blog', etc.
            if field_mapping.startswith('minimal-'):
                from ..config.field_mapping_minimal import get_minimal_field_mapping
                mapping_name = field_mapping[8:]  # Remove 'minimal-' prefix
                self.field_mapping = get_minimal_field_mapping(mapping_name)
            elif field_mapping.startswith('balanced-'):
                from ..config.field_mapping_balanced import get_balanced_field_mapping
                mapping_name = field_mapping[9:]  # Remove 'balanced-' prefix
                self.field_mapping = get_balanced_field_mapping(mapping_name)
            else:
                # Default to full mapping
                self.field_mapping = get_field_mapping(field_mapping)
        else:
            # Accept any mapping object
            self.field_mapping = field_mapping
        
        self.content_items: List[ContentItem] = []
        self.clusters: List[ContentCluster] = []
        
        # Initialize components
        self.lang_processor = LanguageProcessor()
        self.clustering_engine = ClusteringEngine(
            similarity_threshold=similarity_threshold,
            language_processor=self.lang_processor
        )
        
        # Statistics
        self.language_stats: Dict[str, int] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def load_jsonl(self, file_path: str) -> None:
        """
        Load content items from JSONL file
        
        Args:
            file_path: Path to JSONL file
        """
        if not validate_input_file(file_path):
            raise ValueError(f"Invalid input file: {file_path}")
        
        self.content_items = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    # Use field mapping to create ContentItem
                    item = ContentItem.from_raw_dict(data, self.field_mapping)
                    
                    # Auto-detect language if needed
                    if self.language == 'auto':
                        combined_text = f"{item.title} {item.content_text}"
                        item.language = self.lang_processor.get_dominant_language(combined_text)
                    else:
                        item.language = self.language
                    
                    self.content_items.append(item)
                    
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Skipping invalid JSON at line {line_num}: {e}")
                except Exception as e:
                    self.logger.warning(f"Skipping line {line_num} due to error: {e}")
        
        # Update language statistics
        self._update_language_stats()
        
        self.logger.info(f"Loaded {len(self.content_items)} content items")
        self.logger.info(f"Language distribution: {self.language_stats}")
    
    def _update_language_stats(self) -> None:
        """Update language statistics"""
        self.language_stats = {}
        for item in self.content_items:
            lang = item.language or 'unknown'
            self.language_stats[lang] = self.language_stats.get(lang, 0) + 1
    
    def exact_duplicate_check(self) -> List[ContentItem]:
        """
        Remove exact duplicates based on URL and title hash
        
        Returns:
            List of unique content items
        """
        seen_urls = set()
        seen_title_hashes = set()
        unique_items = []
        
        for item in self.content_items:
            # URL deduplication
            if item.url in seen_urls or item.original_url in seen_urls:
                continue
            
            # Title hash deduplication
            title_hash = hashlib.md5(item.title.encode('utf-8')).hexdigest()
            if title_hash in seen_title_hashes:
                continue
            
            seen_urls.add(item.url)
            seen_urls.add(item.original_url)
            seen_title_hashes.add(title_hash)
            unique_items.append(item)
        
        self.logger.info(f"Exact duplicate check: {len(self.content_items)} -> {len(unique_items)}")
        return unique_items
    
    def cluster_and_deduplicate(self) -> List[ContentCluster]:
        """
        Perform clustering and deduplication
        
        Returns:
            List of content clusters
        """
        self.logger.info("Starting content clustering and deduplication...")
        self.logger.info(f"Language setting: {self.language}")
        self.logger.info(f"Original content count: {len(self.content_items)}")
        
        # Step 1: Remove exact duplicates
        unique_items = self.exact_duplicate_check()
        
        # Step 2: Perform clustering
        cluster_indices = self.clustering_engine.find_clusters(unique_items)
        
        # Step 3: Create content clusters
        clusters = []
        for i, cluster_idx_list in enumerate(cluster_indices):
            cluster_items = [unique_items[idx] for idx in cluster_idx_list]
            
            # Select representative
            representative = self.clustering_engine.select_representative(cluster_items)
            
            # Calculate language information
            dominant_language = self._get_cluster_dominant_language(cluster_items)
            language_distribution = self._get_cluster_language_distribution(cluster_items)
            
            # Create cluster
            cluster = ContentCluster(
                representative=representative,
                members=cluster_items,
                cluster_id=f"cluster_{i:04d}",
                dominant_language=dominant_language,
                language_distribution=language_distribution
            )
            clusters.append(cluster)
        
        self.clusters = clusters
        
        # Log results
        single_clusters = len([c for c in clusters if len(c.members) == 1])
        multi_clusters = len([c for c in clusters if len(c.members) > 1])
        
        self.logger.info(f"Clustering complete: {len(self.content_items)} -> {len(unique_items)} -> {len(clusters)} clusters")
        self.logger.info(f"Single-item clusters: {single_clusters}")
        self.logger.info(f"Multi-item clusters: {multi_clusters}")
        
        return clusters
    
    def _get_cluster_dominant_language(self, cluster_items: List[ContentItem]) -> str:
        """Get dominant language of cluster"""
        lang_count = {}
        for item in cluster_items:
            lang = item.language or 'unknown'
            lang_count[lang] = lang_count.get(lang, 0) + 1
        
        if not lang_count:
            return 'unknown'
        
        return max(lang_count.items(), key=lambda x: x[1])[0]
    
    def _get_cluster_language_distribution(self, cluster_items: List[ContentItem]) -> Dict[str, float]:
        """Get language distribution of cluster"""
        lang_count = {}
        total = len(cluster_items)
        
        for item in cluster_items:
            lang = item.language or 'unknown'
            lang_count[lang] = lang_count.get(lang, 0) + 1
        
        return {lang: count / total for lang, count in lang_count.items()}
    
    def get_representatives(self) -> List[ContentItem]:
        """Get all cluster representatives"""
        return [cluster.representative for cluster in self.clusters]
    
    def get_all_clusters(self) -> List[ContentCluster]:
        """Get all content clusters"""
        return self.clusters
    
    def save_results(self, output_path: str, format: str = 'clusters') -> None:
        """
        Save results to file
        
        Args:
            output_path: Output file path
            format: Output format ('clusters', 'representatives', 'report')
        """
        if format == 'clusters':
            self._save_clusters(output_path)
        elif format == 'representatives':
            self._save_representatives(output_path)
        elif format == 'report':
            self._save_report(output_path)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _save_clusters(self, output_path: str) -> None:
        """Save complete cluster information"""
        result = {
            'metadata': {
                'total_clusters': len(self.clusters),
                'original_count': len(self.content_items),
                'language_settings': self.language,
                'language_stats': self.language_stats,
                'similarity_threshold': self.similarity_threshold,
                'compression_ratio': len(self.clusters) / len(self.content_items) if self.content_items else 0
            },
            'clusters': [cluster.to_dict() for cluster in self.clusters]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Clusters saved to: {output_path}")
    
    def _save_representatives(self, output_path: str) -> None:
        """Save representative items only"""
        representatives = [cluster.representative.to_dict() for cluster in self.clusters]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in representatives:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        
        self.logger.info(f"Representatives saved to: {output_path}")
    
    def _save_report(self, output_path: str) -> None:
        """Save detailed report"""
        report = self.generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Report saved to: {output_path}")
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate detailed processing report
        
        Returns:
            Comprehensive report dictionary
        """
        if not self.clusters:
            return {}
        
        representatives = self.get_representatives()
        cluster_sizes = [len(cluster.members) for cluster in self.clusters]
        
        # Language distribution analysis
        lang_distribution = {}
        for cluster in self.clusters:
            lang = cluster.dominant_language
            lang_distribution[lang] = lang_distribution.get(lang, 0) + 1
        
        # Mixed language clusters
        mixed_clusters = []
        for cluster in self.clusters:
            if cluster.is_mixed_language(self.mixed_language_threshold):
                mixed_clusters.append({
                    'cluster_id': cluster.cluster_id,
                    'member_count': len(cluster.members),
                    'language_distribution': cluster.language_distribution,
                    'representative_title': cluster.representative.title[:50] + "..."
                })
        
        # Large clusters analysis
        large_clusters = sorted(
            [c for c in self.clusters if len(c.members) >= 3],
            key=lambda x: len(x.members),
            reverse=True
        )
        
        large_cluster_details = []
        for cluster in large_clusters[:10]:  # Top 10 largest clusters
            large_cluster_details.append({
                "cluster_id": cluster.cluster_id,
                "member_count": len(cluster.members),
                "dominant_language": cluster.dominant_language,
                "language_distribution": cluster.language_distribution,
                "representative_title": cluster.representative.title[:50] + "...",
                "member_titles": [item.title[:30] + "..." for item in cluster.members[:3]]
            })
        
        try:
            import numpy as np
            avg_cluster_size = f"{np.mean(cluster_sizes):.2f}" if cluster_sizes else "0"
        except ImportError:
            avg_cluster_size = f"{sum(cluster_sizes) / len(cluster_sizes):.2f}" if cluster_sizes else "0"
        
        report = {
            "processing_settings": {
                "language_mode": self.language,
                "similarity_threshold": self.similarity_threshold,
                "mixed_language_threshold": self.mixed_language_threshold
            },
            "basic_statistics": {
                "original_content_count": len(self.content_items),
                "cluster_count": len(self.clusters),
                "representative_count": len(representatives),
                "compression_ratio": f"{((len(self.content_items) - len(representatives)) / len(self.content_items) * 100):.2f}%"
            },
            "cluster_size_statistics": {
                "largest_cluster": max(cluster_sizes) if cluster_sizes else 0,
                "average_cluster_size": avg_cluster_size,
                "single_item_clusters": len([s for s in cluster_sizes if s == 1]),
                "multi_item_clusters": len([s for s in cluster_sizes if s > 1])
            },
            "language_distribution": {
                "original_language_stats": self.language_stats,
                "cluster_language_distribution": lang_distribution,
                "mixed_language_cluster_count": len(mixed_clusters)
            },
            "mixed_language_clusters": mixed_clusters[:5],  # Top 5
            "large_clusters": large_cluster_details
        }
        
        return report
