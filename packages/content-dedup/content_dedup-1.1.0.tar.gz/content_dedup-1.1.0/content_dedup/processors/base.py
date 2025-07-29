"""
Base classes for text processors.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseProcessor(ABC):
    """Base class for text processors"""
    
    @abstractmethod
    def process(self, text: str) -> Any:
        """Process input text"""
        pass


class BaseTokenizer(ABC):
    """Base class for tokenizers"""
    
    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """Tokenize input text"""
        pass


class BaseLanguageDetector(ABC):
    """Base class for language detectors"""
    
    @abstractmethod
    def detect(self, text: str) -> Dict[str, float]:
        """Detect language distribution in text"""
        pass
