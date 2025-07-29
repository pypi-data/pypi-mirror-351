"""
Similarity calculation utilities.
"""

import numpy as np
from typing import List, Tuple, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher

from .language import LanguageProcessor


class SimilarityCalculator:
    """Calculate similarity between text content"""
    
    def __init__(self, language_processor: LanguageProcessor = None):
        self.lang_processor = language_processor or LanguageProcessor()
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        
        Args:
            text1, text2: Input texts
            
        Returns:
            Similarity score (0-1)
        """
        # Tokenize both texts
        tokens1 = self.lang_processor.tokenize_mixed_text(text1)
        tokens2 = self.lang_processor.tokenize_mixed_text(text2)
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Calculate token-based similarity
        set1, set2 = set(tokens1), set(tokens2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        
        # Calculate sequence similarity
        seq_similarity = SequenceMatcher(None, text1, text2).ratio()
        
        # Combine similarities
        combined_similarity = (jaccard_similarity * 0.7 + seq_similarity * 0.3)
        
        return combined_similarity
    
    def calculate_tfidf_similarity(self, texts: List[str]) -> np.ndarray:
        """
        Calculate TF-IDF based similarity matrix
        
        Args:
            texts: List of texts
            
        Returns:
            Similarity matrix
        """
        if len(texts) < 2:
            return np.array([[1.0]] if texts else [])
        
        # Preprocess texts
        processed_texts = []
        for text in texts:
            tokens = self.lang_processor.tokenize_mixed_text(text)
            processed_texts.append(' '.join(tokens))
        
        # Calculate TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=3000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
        except ValueError:
            # Fallback to pairwise comparison
            n = len(texts)
            similarity_matrix = np.zeros((n, n))
            for i in range(n):
                similarity_matrix[i][i] = 1.0
                for j in range(i + 1, n):
                    sim = self.calculate_text_similarity(texts[i], texts[j])
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim
        
        return similarity_matrix
