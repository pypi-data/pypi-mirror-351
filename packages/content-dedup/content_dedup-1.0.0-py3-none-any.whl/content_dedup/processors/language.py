"""
Language processing utilities for multilingual content.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from collections import Counter

# Optional dependencies
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

from .base import BaseProcessor


class LanguageProcessor(BaseProcessor):
    """Multilingual text processor with support for mixed-language content"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Chinese stopwords
        self.chinese_stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', 
            '都', '一', '一個', '上', '也', '很', '到', '說', '要', '去', 
            '你', '會', '著', '沒有', '看', '好', '自己', '這', '那', '它',
            '他', '她', '們', '這個', '那個', '什麼', '怎麼', '為什麼', 
            '但是', '因為', '所以', '而且', '或者', '如果', '雖然', '然而'
        }
        
        # English stopwords
        self.english_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 
            'she', 'it', 'we', 'they', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 
            'should', 'may', 'might', 'must', 'can', 'shall'
        }
        
        # Initialize jieba if available
        if JIEBA_AVAILABLE:
            jieba.initialize()
            self.logger.info("Jieba initialized for Chinese text processing")
        else:
            self.logger.warning("Jieba not available, using fallback for Chinese text")
        
        # Initialize NLTK if available
        if NLTK_AVAILABLE:
            try:
                # Download required NLTK data if not present
                import nltk
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                self.logger.info("NLTK initialized for English text processing")
            except Exception as e:
                self.logger.warning(f"NLTK initialization failed: {e}")
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process text and return comprehensive analysis
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing language info and processed tokens
        """
        lang_dist = self.detect_language(text)
        dominant_lang = self.get_dominant_language(text)
        is_mixed = self.is_mixed_language(text)
        tokens = self.tokenize_mixed_text(text)
        keywords = self.extract_keywords(text)
        
        return {
            'language_distribution': lang_dist,
            'dominant_language': dominant_lang,
            'is_mixed_language': is_mixed,
            'tokens': tokens,
            'keywords': keywords,
            'token_count': len(tokens),
            'keyword_count': len(keywords)
        }
    
    def detect_language(self, text: str) -> Dict[str, float]:
        """
        Detect language distribution in text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with language codes and their probabilities
        """
        if not text or len(text.strip()) < 3:
            return {'unknown': 1.0}
        
        # Character-based detection
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text))
        korean_chars = len(re.findall(r'[\uac00-\ud7af]', text))
        
        total_chars = chinese_chars + english_chars + japanese_chars + korean_chars
        
        if total_chars == 0:
            return {'unknown': 1.0}
        
        lang_dist = {}
        if chinese_chars > 0:
            lang_dist['zh'] = chinese_chars / total_chars
        if english_chars > 0:
            lang_dist['en'] = english_chars / total_chars
        if japanese_chars > 0:
            lang_dist['ja'] = japanese_chars / total_chars
        if korean_chars > 0:
            lang_dist['ko'] = korean_chars / total_chars
        
        # Use langdetect as supplementary detection
        if LANGDETECT_AVAILABLE and len(text) > 20:
            try:
                detected_langs = detect_langs(text)
                for lang_obj in detected_langs[:3]:  # Top 3 detected languages
                    lang_code = lang_obj.lang
                    confidence = lang_obj.prob
                    
                    if lang_code in lang_dist:
                        # Weighted average with character-based detection
                        lang_dist[lang_code] = (lang_dist[lang_code] + confidence) / 2
                    elif confidence > 0.2:  # Add high-confidence languages
                        lang_dist[lang_code] = confidence * 0.3
            except Exception as e:
                self.logger.debug(f"Language detection failed: {e}")
        
        # Normalize probabilities
        total_prob = sum(lang_dist.values())
        if total_prob > 0:
            lang_dist = {k: v / total_prob for k, v in lang_dist.items()}
        
        return lang_dist if lang_dist else {'unknown': 1.0}
    
    def get_dominant_language(self, text: str) -> str:
        """Get the dominant language in text"""
        lang_dist = self.detect_language(text)
        return max(lang_dist.items(), key=lambda x: x[1])[0]
    
    def is_mixed_language(self, text: str, threshold: float = 0.3) -> bool:
        """
        Check if text contains mixed languages
        
        Args:
            text: Input text
            threshold: Minimum proportion for secondary language
            
        Returns:
            True if text is mixed-language
        """
        lang_dist = self.detect_language(text)
        sorted_langs = sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)
        return len(sorted_langs) >= 2 and sorted_langs[1][1] > threshold
    
    def clean_and_normalize_text(self, text: str) -> str:
        """
        Clean and normalize text (language-agnostic)
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive punctuation but keep some structure
        text = re.sub(r'[^\w\s\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', ' ', text)
        
        # Clean extra whitespace
        text = text.strip()
        
        return text
    
    def tokenize_mixed_text(self, text: str) -> List[str]:
        """
        Tokenize mixed-language text (Chinese-English friendly)
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Clean text first
        cleaned_text = self.clean_and_normalize_text(text)
        
        tokens = []
        
        # Split text into segments by language
        segments = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+|\d+|[\u3040-\u309f\u30a0-\u30ff]+|[\uac00-\ud7af]+', cleaned_text)
        
        for segment in segments:
            if re.match(r'[\u4e00-\u9fff]+', segment):
                # Chinese text: use jieba if available
                if JIEBA_AVAILABLE:
                    chinese_tokens = jieba.lcut(segment)
                    # Filter stopwords and single characters
                    chinese_tokens = [
                        token for token in chinese_tokens 
                        if len(token) > 1 and token not in self.chinese_stopwords
                    ]
                    tokens.extend(chinese_tokens)
                else:
                    # Fallback: character-based tokenization
                    tokens.extend([char for char in segment if len(char.strip()) > 0])
            
            elif re.match(r'[a-zA-Z]+', segment):
                # English text: word-based tokenization
                if len(segment) > 2 and segment.lower() not in self.english_stopwords:
                    tokens.append(segment.lower())
            
            elif re.match(r'\d+', segment):
                # Numbers: keep if meaningful
                if len(segment) > 1:
                    tokens.append(segment)
            
            elif re.match(r'[\u3040-\u309f\u30a0-\u30ff]+', segment):
                # Japanese text: basic segmentation
                if len(segment) > 1:
                    tokens.append(segment)
            
            elif re.match(r'[\uac00-\ud7af]+', segment):
                # Korean text: basic segmentation
                if len(segment) > 1:
                    tokens.append(segment)
        
        return tokens
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """
        Extract keywords from text (language-agnostic)
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords sorted by frequency
        """
        tokens = self.tokenize_mixed_text(text)
        
        # Filter tokens by length and quality
        quality_tokens = [
            token for token in tokens 
            if len(token) >= 2 and not token.isdigit()
        ]
        
        # Count frequency
        word_freq = Counter(quality_tokens)
        
        # Return most common keywords
        return [word for word, freq in word_freq.most_common(max_keywords)]
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get comprehensive text statistics
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with various text statistics
        """
        tokens = self.tokenize_mixed_text(text)
        lang_dist = self.detect_language(text)
        
        # Character counts
        char_counts = {
            'total': len(text),
            'chinese': len(re.findall(r'[\u4e00-\u9fff]', text)),
            'english': len(re.findall(r'[a-zA-Z]', text)),
            'digits': len(re.findall(r'\d', text)),
            'punctuation': len(re.findall(r'[^\w\s\u4e00-\u9fff]', text))
        }
        
        return {
            'char_counts': char_counts,
            'token_count': len(tokens),
            'unique_tokens': len(set(tokens)),
            'language_distribution': lang_dist,
            'is_mixed_language': self.is_mixed_language(text),
            'dominant_language': self.get_dominant_language(text)
        }
