#!/usr/bin/env python3
"""
Complete demonstration of field mapping functionality
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from content_dedup import ContentDeduplicator
from content_dedup.config.field_mapping import create_custom_mapping, get_field_mapping


def demo_standard_format():
    """Demo 1: Standard format (no field mapping needed)"""
    print("🔍 Demo 1: Standard JSONL format")
    print("=" * 50)
    
    deduplicator = ContentDeduplicator(
        language='auto',
        similarity_threshold=0.8
    )
    
    # Load standard format
    sample_file = project_root / "examples/sample_data/standard_format.jsonl"
    if sample_file.exists():
        deduplicator.load_jsonl(str(sample_file))
        print(f"✅ Loaded {len(deduplicator.content_items)} items using default mapping")
        
        for i, item in enumerate(deduplicator.content_items[:2]):
            print(f"   Item {i+1}: '{item.title}' by {item.author}")
    else:
        print("❌ Standard format sample file not found")
    
    print()


def demo_custom_field_mapping():
    """Demo 2: Custom field mapping for news format"""
    print("🔍 Demo 2: Custom field mapping for news data")
    print("=" * 50)
    
    # Create custom mapping for news format
    news_mapping = create_custom_mapping(
        title_field='headline',
        content_fields=['body', 'summary'],  # Combine body and summary
        id_field='permalink',
        category_field='tags',
        content_separator=' | ',  # Custom separator
        ignore_missing_required=True
    )
    
    deduplicator = ContentDeduplicator(
        language='auto',
        similarity_threshold=0.7,  # Lower threshold to catch similar content
        field_mapping=news_mapping
    )
    
    # Create sample data for this demo
    sample_data = [
        {
            "headline": "科技突破：AI 技術新進展", 
            "body": "人工智慧領域取得重大突破", 
            "summary": "研究團隊開發出新的機器學習算法",
            "permalink": "https://tech.example.com/ai-breakthrough",
            "writer": "科技記者",
            "tags": ["AI", "科技", "突破"]
        },
        {
            "headline": "科技創新：機器學習新發現", 
            "body": "機器學習技術獲得新的進展", 
            "summary": "科學家發現了改進的學習方法",
            "permalink": "https://tech.example.com/ml-innovation",
            "writer": "技術專家",
            "tags": ["機器學習", "科技", "創新"]
        }
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in sample_data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
        temp_file = f.name
    
    try:
        deduplicator.load_jsonl(temp_file)
        print(f"✅ Loaded {len(deduplicator.content_items)} items using custom news mapping")
        
        for i, item in enumerate(deduplicator.content_items):
            print(f"   Item {i+1}: '{item.title}' by {item.author}")
            print(f"   Content: '{item.content_text[:50]}...'")
            print(f"   Categories: {item.category}")
        
        # Perform clustering
        clusters = deduplicator.cluster_and_deduplicate()
        print(f"✅ Generated {len(clusters)} clusters from similar content")
        
    finally:
        os.unlink(temp_file)
    
    print()


def demo_mixed_format_handling():
    """Demo 3: Handling mixed data formats"""
    print("🔍 Demo 3: Mixed data formats with multiple field mappings")
    print("=" * 50)
    
    # Sample mixed data with different structures
    mixed_data = [
        # News format
        {
            "headline": "新聞標題1", 
            "body": "新聞內容1", 
            "permalink": "https://news.example.com/1",
            "writer": "記者A"
        },
        # Blog format  
        {
            "post_title": "部落格標題", 
            "content": "部落格內容", 
            "blog_url": "https://blog.example.com/1",
            "blogger": "部落客"
        },
        # Social format
        {
            "username": "用戶", 
            "message": "社群訊息內容", 
            "post_url": "https://social.example.com/1"
        }
    ]
    
    # Strategy 1: Use flexible mapping to handle all formats
    flexible_mapping = create_custom_mapping(
        title_field=['headline', 'post_title', 'username'],  # Multiple possible title fields
        content_fields=['body', 'content', 'message'],       # Multiple possible content fields
        id_field=['permalink', 'blog_url', 'post_url'],     # Multiple possible URL fields
        content_separator=' ',
        ignore_missing_required=True
    )
    
    deduplicator = ContentDeduplicator(field_mapping=flexible_mapping)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in mixed_data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
        temp_file = f.name
    
    try:
        deduplicator.load_jsonl(temp_file)
        print(f"✅ Loaded {len(deduplicator.content_items)} mixed format items")
        
        for i, item in enumerate(deduplicator.content_items):
            print(f"   Item {i+1}: '{item.title}' by {item.author}")
            print(f"   URL: {item.url}")
        
    finally:
        os.unlink(temp_file)
    
    print()


def demo_predefined_mappings():
    """Demo 4: Using predefined mappings"""
    print("🔍 Demo 4: Predefined mapping presets")
    print("=" * 50)
    
    mappings = ['news', 'blog', 'social', 'academic', 'ecommerce']
    
    for mapping_name in mappings:
        try:
            mapping = get_field_mapping(mapping_name)
            print(f"✅ {mapping_name.capitalize()} mapping:")
            print(f"   Title field(s): {mapping.title_field}")
            print(f"   Content field(s): {mapping.content_fields}")
            print(f"   URL field: {mapping.id_field}")
            print(f"   Author field: {mapping.author_field}")
        except Exception as e:
            print(f"❌ Error loading {mapping_name} mapping: {e}")
    
    print()


def demo_cli_usage():
    """Demo 5: CLI usage examples"""
    print("🔍 Demo 5: CLI usage examples")
    print("=" * 50)
    
    examples = [
        {
            "desc": "Using predefined news mapping",
            "cmd": "content-dedup data.jsonl --field-mapping news --output results.json"
        },
        {
            "desc": "Custom title and content fields",
            "cmd": "content-dedup data.jsonl --title-field headline --content-fields body,summary --output results.json"
        },
        {
            "desc": "Multiple content fields with custom separator",
            "cmd": "content-dedup data.jsonl --content-fields description,content,text --content-separator ' | ' --output results.json"
        },
        {
            "desc": "Ignore missing required fields",
            "cmd": "content-dedup data.jsonl --ignore-missing --title-field title,name --output results.json"
        },
        {
            "desc": "Pipeline usage with custom mapping",
            "cmd": "cat mixed_data.jsonl | content-dedup - --field-mapping social --format representatives"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['desc']}:")
        print(f"   {example['cmd']}")
        print()


def main():
    """Run all demonstrations"""
    print("🚀 py-content-dedup Field Mapping Demonstration")
    print("=" * 60)
    print()
    
    # Run demonstrations
    demo_standard_format()
    demo_custom_field_mapping()
    demo_mixed_format_handling()
    demo_predefined_mappings()
    demo_cli_usage()
    
    print("✨ All demonstrations completed!")
    print("\n📚 Key Features Demonstrated:")
    print("  ✅ Standard JSONL format support")
    print("  ✅ Custom field mapping creation")
    print("  ✅ Multiple field concatenation")
    print("  ✅ Mixed data format handling")
    print("  ✅ Predefined mapping presets")
    print("  ✅ CLI parameter customization")
    print("  ✅ Flexible error handling")


if __name__ == '__main__':
    main()
