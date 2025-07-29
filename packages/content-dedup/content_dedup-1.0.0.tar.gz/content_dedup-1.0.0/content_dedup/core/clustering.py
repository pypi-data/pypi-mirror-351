"""
Clustering algorithms for content deduplication.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher

from .models import ContentItem, ContentCluster
from ..processors.language import LanguageProcessor


class ClusteringEngine:
    """Core clustering engine for content deduplication"""
    
    def __init__(self, 
                 similarity_threshold: float = 0.8,
                 language_processor: LanguageProcessor = None):
        self.similarity_threshold = similarity_threshold
        self.lang_processor = language_processor or LanguageProcessor()
    
    def calculate_similarity_matrix(self, items: List[ContentItem]) -> np.ndarray:
        """
        Calculate similarity matrix for content items
        
        Args:
            items: List of content items
            
        Returns:
            Similarity matrix as numpy array
        """
        n = len(items)
        if n <= 1:
            return np.array([[1.0]] if n == 1 else [])
        
        # Prepare tokenized texts
        processed_texts = []
        for item in items:
            combined_text = f"{item.title} {item.content_text}"
            tokens = self.lang_processor.tokenize_mixed_text(combined_text)
            processed_text = ' '.join(tokens)
            processed_texts.append(processed_text)
        
        try:
            # Use TF-IDF for similarity calculation
            vectorizer = TfidfVectorizer(
                max_features=3000,
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95,
                token_pattern=r'\b\w+\b'
            )
            
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
        except Exception as e:
            print(f"TF-IDF failed, using fallback method: {e}")
            # Fallback to pairwise sequence similarity
            similarity_matrix = np.zeros((n, n))
            for i in range(n):
                similarity_matrix[i][i] = 1.0
                for j in range(i + 1, n):
                    sim = self._calculate_content_similarity(items[i], items[j])
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim
        
        return similarity_matrix
    
    def _calculate_content_similarity(self, item1: ContentItem, item2: ContentItem) -> float:
        """Calculate similarity between two content items"""
        # Title similarity
        title_sim = SequenceMatcher(None, item1.title, item2.title).ratio()
        
        # Content keywords similarity
        keywords1 = set(self.lang_processor.extract_keywords(
            f"{item1.title} {item1.content_text}", max_keywords=50
        ))
        keywords2 = set(self.lang_processor.extract_keywords(
            f"{item2.title} {item2.content_text}", max_keywords=50
        ))
        
        if len(keywords1.union(keywords2)) > 0:
            keyword_overlap = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2))
        else:
            keyword_overlap = 0
        
        # Length similarity
        len1, len2 = len(item1.content_text), len(item2.content_text)
        if max(len1, len2) > 0:
            length_sim = min(len1, len2) / max(len1, len2)
        else:
            length_sim = 1.0
        
        # Weighted combination
        similarity = (
            title_sim * 0.4 +
            keyword_overlap * 0.5 +
            length_sim * 0.1
        )
        
        return similarity
    
    def find_clusters(self, items: List[ContentItem]) -> List[List[int]]:
        """
        Find clusters using connected components algorithm
        
        Args:
            items: List of content items
            
        Returns:
            List of clusters, each containing indices of similar items
        """
        if len(items) <= 1:
            return [[i] for i in range(len(items))]
        
        similarity_matrix = self.calculate_similarity_matrix(items)
        
        # Build adjacency graph
        clusters = []
        visited = set()
        
        for i in range(len(items)):
            if i in visited:
                continue
            
            # Start new cluster with DFS
            cluster = []
            stack = [i]
            
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                
                visited.add(current)
                cluster.append(current)
                
                # Find similar items
                for j in range(len(items)):
                    if j not in visited and similarity_matrix[current][j] > self.similarity_threshold:
                        stack.append(j)
            
            clusters.append(cluster)
        
        return clusters
    
    def select_representative(self, cluster_items: List[ContentItem]) -> ContentItem:
        """
        Select the best representative for a cluster
        
        Args:
            cluster_items: Items in the cluster
            
        Returns:
            Best representative item
        """
        if len(cluster_items) == 1:
            return cluster_items[0]
        
        best_item = cluster_items[0]
        best_score = 0
        
        for item in cluster_items:
            score = self._calculate_quality_score(item, cluster_items)
            
            if score > best_score:
                best_score = score
                best_item = item
        
        return best_item
    
    def _calculate_quality_score(self, item: ContentItem, cluster_items: List[ContentItem]) -> float:
        """Calculate quality score for representative selection"""
        score = 0.0
        
        # Content length score (30%)
        content_length = len(item.content_text)
        if content_length > 1500:
            score += 30
        elif content_length > 800:
            score += 20
        elif content_length > 300:
            score += 10
        
        # Title quality score (20%)
        title_length = len(item.title)
        if 15 <= title_length <= 60:
            score += 20
        elif 10 <= title_length <= 80:
            score += 15
        
        # Image count score (10%)
        score += min(len(item.images) * 5, 15)
        
        # Source reliability score (20%)
        reliable_domains = [
            'twreporter.org', 'cna.com.tw', 'udn.com', 'chinatimes.com',
            'ltn.com.tw', 'ettoday.net', 'tvbs.com.tw', 'storm.mg',
            'gov.tw', 'edu.tw', 'org.tw'
        ]
        
        if any(domain in item.url for domain in reliable_domains):
            score += 20
        
        # Language consistency score (10%)
        dominant_lang = self._get_cluster_dominant_language(cluster_items)
        if item.language == dominant_lang:
            score += 10
        
        # Freshness score (10%)
        try:
            from datetime import datetime
            publish_time = datetime.strptime(item.publish_time, "%Y/%m/%d %H:%M:%S")
            now = datetime.now()
            hours_diff = (now - publish_time).total_seconds() / 3600
            
            if hours_diff <= 6:
                score += 10
            elif hours_diff <= 24:
                score += 8
            elif hours_diff <= 72:
                score += 5
        except:
            score += 5  # Default score
        
        return score
    
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
