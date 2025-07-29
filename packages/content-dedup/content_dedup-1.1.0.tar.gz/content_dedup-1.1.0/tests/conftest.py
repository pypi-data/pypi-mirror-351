"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from typing import List, Dict, Any

from content_dedup.core.models_flexible import FlexibleContentItem, create_flexible_content_item
from content_dedup.config.field_mapping import get_field_mapping


@pytest.fixture
def sample_content_items() -> List[FlexibleContentItem]:
    """Fixture providing sample content items for testing"""
    field_mapping = get_field_mapping('news')
    
    sample_data = [
        {
            "title": "AI技術突破：新演算法提升效率",
            "content": "人工智能領域迎來重大突破，新的深度學習演算法在多項測試中展現出色表現，相較於傳統方法提升了50%的處理速度。",
            "url": "https://example.com/ai-breakthrough",
            "tags": ["科技", "AI"],
            "published_at": "2025/01/15 10:00:00",
            "author": "科技記者",
            "images": ["https://example.com/image1.jpg"],
            "fetch_time": "2025/01/15 11:00:00"
        },
        {
            "title": "Machine Learning Algorithm Shows Promise",
            "content": "A new machine learning algorithm has demonstrated significant improvements in efficiency, showing 50% better performance than traditional methods in various tests.",
            "url": "https://example.com/ml-algorithm",
            "tags": ["technology", "AI"],
            "published_at": "2025/01/15 11:00:00",
            "author": "Tech Reporter",
            "images": ["https://example.com/image2.jpg"],
            "fetch_time": "2025/01/15 12:00:00"
        },
        {
            "title": "Similar AI Tech Article",
            "content": "Another article about AI technology breakthrough and new algorithms with improved efficiency in deep learning applications.",
            "url": "https://example.com/similar-ai",
            "tags": ["technology"],
            "published_at": "2025/01/15 12:00:00",
            "author": "Another Reporter",
            "images": [],
            "fetch_time": "2025/01/15 13:00:00"
        },
        {
            "title": "完全不同的新聞：體育賽事報導",
            "content": "今日體育新聞報導，籃球比賽結果出爐，主隊以98:87的比分擊敗客隊，取得本賽季第十場勝利。",
            "url": "https://example.com/sports-news",
            "tags": ["體育"],
            "published_at": "2025/01/15 13:00:00",
            "author": "體育記者",
            "images": ["https://example.com/sports.jpg"],
            "fetch_time": "2025/01/15 14:00:00"
        }
    ]
    
    items = []
    for data in sample_data:
        item = FlexibleContentItem.from_raw_data(
            original_data=data,
            field_mapping=field_mapping,
            required_fields=['title', 'content_text', 'url']
        )
        # Auto-detect language for test items
        combined_text = f"{item.title} {item.content_text}"
        if any(ord(char) > 127 for char in combined_text[:100]):
            item.language = 'zh'
        else:
            item.language = 'en'
        items.append(item)
    
    return items


@pytest.fixture
def sample_jsonl_file(sample_content_items) -> str:
    """Create a temporary JSONL file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
        for item in sample_content_items:
            json.dump(item.to_dict(), f, ensure_ascii=False)
            f.write('\n')
        
        return f.name


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for output files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mixed_language_content_items() -> List[FlexibleContentItem]:
    """Fixture for mixed language content testing"""
    field_mapping = get_field_mapping('news')
    
    sample_data = [
        {
            "title": "AI人工智能技術 breakthrough in machine learning",
            "content": "這是一個關於AI technology的混合語言文章，討論了machine learning和deep learning的最新發展trends。",
            "url": "https://example.com/mixed-ai",
            "tags": ["tech", "科技"],
            "published_at": "2025/01/15 14:00:00",
            "author": "Mixed Author",
            "images": [],
            "fetch_time": "2025/01/15 15:00:00"
        },
        {
            "title": "Technology trends 科技趨勢分析",
            "content": "Analysis of current technology trends including AI, machine learning, and 區塊鏈 blockchain applications in various industries.",
            "url": "https://example.com/tech-trends",
            "tags": ["technology"],
            "published_at": "2025/01/15 15:00:00",
            "author": "Trend Analyst",
            "images": [],
            "fetch_time": "2025/01/15 16:00:00"
        }
    ]
    
    items = []
    for data in sample_data:
        item = FlexibleContentItem.from_raw_data(
            original_data=data,
            field_mapping=field_mapping,
            required_fields=['title', 'content_text', 'url']
        )
        # Set mixed language
        item.language = 'mixed'
        items.append(item)
    
    return items
