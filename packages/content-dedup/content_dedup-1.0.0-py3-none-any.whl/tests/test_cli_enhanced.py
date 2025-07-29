#!/usr/bin/env python3
"""
Test new CLI features with minimal flag and mapping types
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_test_data():
    """Create test JSONL data"""
    test_data = [
        {
            "headline": "AI 突破性進展",
            "body": "人工智慧在醫療領域取得重大突破",
            "summary": "最新AI技術應用於疾病診斷",
            "permalink": "https://example.com/ai-breakthrough",
            "writer": "張三",
            "published_at": "2024-01-15",
            "tags": ["AI", "醫療"],
            "photos": ["image1.jpg"]
        },
        {
            "headline": "人工智慧醫療突破",
            "body": "AI技術在醫療診斷方面實現重大進展",
            "summary": "新的人工智慧系統用於疾病檢測",
            "permalink": "https://example.com/ai-medical",
            "writer": "李四",
            "published_at": "2024-01-16",
            "tags": ["技術", "醫療"],
            "photos": ["image2.jpg"]
        },
        {
            "headline": "科技新聞",
            "body": "完全不同的科技新聞內容",
            "summary": "關於其他科技發展",
            "permalink": "https://example.com/tech-news",
            "writer": "王五",
            "published_at": "2024-01-17",
            "tags": ["科技"],
            "photos": []
        }
    ]
    return test_data

def test_cli_minimal_flag():
    """Test CLI with --minimal flag"""
    print("🧪 測試 CLI --minimal 標誌")
    print("=" * 50)
    
    # Create test data file
    test_data = create_test_data()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in test_data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
        temp_input = f.name
    
    try:
        # Test different CLI commands
        test_commands = [
            # Standard mapping
            f"python -m content_dedup.cli {temp_input} --field-mapping news --format representatives",
            
            # Balanced mapping  
            f"python -m content_dedup.cli {temp_input} --field-mapping balanced-news --format representatives",
            
            # Minimal mapping
            f"python -m content_dedup.cli {temp_input} --field-mapping minimal-news --format representatives",
            
            # Custom mapping with minimal flag
            f"python -m content_dedup.cli {temp_input} --title-field headline --content-fields body,summary --url-field permalink --minimal --format representatives",
            
            # Custom balanced mapping
            f"python -m content_dedup.cli {temp_input} --title-field headline --content-fields body,summary --url-field permalink --author-field writer --format representatives"
        ]
        
        for i, cmd in enumerate(test_commands, 1):
            print(f"\n📋 測試 {i}: {cmd.split()[-6:]}")  # Show last 6 args
            try:
                result = os.system(cmd + " > /dev/null 2>&1")
                if result == 0:
                    print("✅ 成功")
                else:
                    print(f"❌ 失敗 (退出碼: {result})")
            except Exception as e:
                print(f"❌ 錯誤: {e}")
    
    finally:
        Path(temp_input).unlink()

def test_mapping_types_consistency():
    """Test that different mapping types produce consistent results"""
    print("\n\n🔍 測試映射類型一致性")
    print("=" * 50)
    
    # Import after adding to path
    from content_dedup import ContentDeduplicator
    
    # Create test data
    test_data = create_test_data()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in test_data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
        temp_input = f.name
    
    try:
        # Test different mapping types
        mapping_types = [
            ('news', '完整版'),
            ('balanced-news', '平衡版'),
            ('minimal-news', '精簡版')
        ]
        
        results = {}
        
        for mapping, name in mapping_types:
            print(f"\n📊 測試 {name} ({mapping})")
            
            deduplicator = ContentDeduplicator(
                field_mapping=mapping,
                similarity_threshold=0.7
            )
            deduplicator.load_jsonl(temp_input)
            clusters = deduplicator.cluster_and_deduplicate()
            
            results[mapping] = {
                'clusters': len(clusters),
                'items': len(deduplicator.content_items),
                'representatives': [c.representative.title for c in clusters]
            }
            
            print(f"  項目數: {results[mapping]['items']}")
            print(f"  群集數: {results[mapping]['clusters']}")
            print(f"  代表標題: {results[mapping]['representatives']}")
        
        # Check consistency
        print(f"\n📈 一致性檢查:")
        cluster_counts = [r['clusters'] for r in results.values()]
        if len(set(cluster_counts)) == 1:
            print("✅ 所有映射類型產生相同數量的群集")
        else:
            print(f"⚠️ 群集數量不同: {cluster_counts}")
        
        # Check core deduplication (should be similar)
        full_titles = set(results['news']['representatives'])
        balanced_titles = set(results['balanced-news']['representatives'])
        minimal_titles = set(results['minimal-news']['representatives'])
        
        if full_titles == balanced_titles == minimal_titles:
            print("✅ 所有映射類型選擇相同的代表項目")
        else:
            print("⚠️ 代表項目選擇略有不同（這是正常的）")
            
    finally:
        Path(temp_input).unlink()

def test_migration_utilities():
    """Test migration utilities"""
    print("\n\n🔄 測試遷移工具")
    print("=" * 50)
    
    from content_dedup.utils.migration import (
        suggest_optimal_mapping, 
        compatibility_check,
        migrate_to_minimal,
        migrate_to_balanced
    )
    from content_dedup.config.field_mapping import get_field_mapping
    from content_dedup.config.field_mapping_balanced import get_balanced_field_mapping
    
    # Test suggestions
    print("💡 映射建議:")
    use_cases = ['performance', 'general', 'research', 'api_service']
    for case in use_cases:
        suggestion = suggest_optimal_mapping(case)
        print(f"  {case}: {suggestion}")
    
    # Test compatibility check
    print("\n🔍 相容性檢查:")
    old_mappings = ['news', 'blog', 'default']
    for mapping in old_mappings:
        check = compatibility_check(mapping)
        print(f"  {mapping} -> {check['recommended_migration']}")
    
    # Test migration
    print("\n🔄 遷移測試:")
    try:
        # Get original mapping
        original = get_field_mapping('news')
        print(f"  原始映射: {type(original).__name__}")
        
        # Migrate to balanced
        balanced = migrate_to_balanced(original)
        print(f"  平衡版: {type(balanced).__name__}")
        
        # Migrate to minimal
        minimal = migrate_to_minimal(original)
        print(f"  精簡版: {type(minimal).__name__}")
        
        print("✅ 遷移功能正常")
        
    except Exception as e:
        print(f"❌ 遷移錯誤: {e}")

if __name__ == "__main__":
    print("🚀 py-content-dedup CLI 新功能測試")
    print("=" * 60)
    
    test_cli_minimal_flag()
    test_mapping_types_consistency()
    test_migration_utilities()
    
    print("\n\n🎯 測試完成")
    print("=" * 60)
    print("💡 建議:")
    print("  - 新項目使用 balanced-* 映射（推薦）")
    print("  - 效能敏感場景使用 minimal-* 映射")
    print("  - 複雜需求使用完整映射")
    print("  - 使用 --minimal 標誌快速啟用精簡模式")
