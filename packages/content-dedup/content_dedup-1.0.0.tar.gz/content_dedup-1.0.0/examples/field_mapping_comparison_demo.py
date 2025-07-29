#!/usr/bin/env python3
"""
Complete demonstration of three field mapping approaches:
1. Full FieldMapping (comple        balanced_mapping = create_balanced_mapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink',
            category_field='tags',
            publish_time_field='published_at',
            content_separator=' | '
        )ionality)
2. Balanced FieldMapping (core + important fields)
3. Minimal FieldMapping (core fields only)
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
from content_dedup.config.field_mapping import create_custom_mapping
from content_dedup.config.field_mapping_balanced import create_balanced_mapping
from content_dedup.config.field_mapping_minimal import create_minimal_custom_mapping


def create_sample_data():
    """Create sample data for testing"""
    return [
        {
            "headline": "AI技術重大突破",
            "body": "人工智慧領域取得了前所未有的重大進展",
            "summary": "研究團隊開發出革命性的新算法",
            "permalink": "https://tech.example.com/ai-breakthrough-1",
            "writer": "資深科技記者",
            "tags": ["AI", "人工智慧", "科技突破"],
            "published_at": "2025/01/15 10:00:00",
            "images": ["ai_breakthrough.jpg", "algorithm_diagram.png"],
            "crawled_at": "2025/01/15 11:30:00"
        },
        {
            "headline": "機器學習新里程碑",
            "body": "機器學習技術達到新的里程碑",
            "summary": "科學家發現了改進學習效率的方法",
            "permalink": "https://tech.example.com/ml-milestone-1",
            "writer": "技術專家",
            "tags": ["機器學習", "科技", "創新"],
            "published_at": "2025/01/15 14:00:00",
            "images": ["ml_chart.jpg"],
            "crawled_at": "2025/01/15 15:00:00"
        },
        {
            "headline": "深度學習演算法優化",
            "body": "深度學習演算法獲得重要優化改進",
            "summary": "新的訓練方法提升了模型效能",
            "permalink": "https://tech.example.com/dl-optimization-1",
            "writer": "AI研究員",
            "tags": ["深度學習", "演算法", "優化"],
            "published_at": "2025/01/15 16:00:00",
            "images": ["neural_network.png", "performance_chart.jpg"],
            "crawled_at": "2025/01/15 17:00:00"
        }
    ]


def demo_mapping_comparison():
    """比較三種映射方式的效果"""
    print("🔍 欄位映射方式比較演示")
    print("=" * 60)
    
    # 創建測試資料
    sample_data = create_sample_data()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in sample_data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
        temp_file = f.name
    
    try:
        # 1. 完整版映射 (Full FieldMapping)
        print("\n📋 1. 完整版映射 (Full FieldMapping)")
        print("-" * 40)
        
        full_mapping = create_custom_mapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink',
            category_field='tags',
            publish_time_field='published_at',
            content_separator=' | '
        )
        
        deduplicator_full = ContentDeduplicator(
            similarity_threshold=0.7,
            field_mapping=full_mapping
        )
        deduplicator_full.load_jsonl(temp_file)
        clusters_full = deduplicator_full.cluster_and_deduplicate()
        
        print(f"✅ 載入 {len(deduplicator_full.content_items)} 項目")
        print(f"📊 產生 {len(clusters_full)} 個群集")
        print("📝 代表項目範例：")
        if clusters_full:
            rep = clusters_full[0].representative
            print(f"   標題: {rep.title}")
            print(f"   作者: {rep.author}")
            print(f"   分類: {rep.category}")
            print(f"   圖片: {len(rep.images)} 張")
            print(f"   發布時間: {rep.publish_time}")
        
        # 2. 平衡版映射 (Balanced FieldMapping) 
        print("\n⚖️ 2. 平衡版映射 (Balanced FieldMapping)")
        print("-" * 40)
        
        balanced_mapping = create_balanced_mapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink',
            author_field='writer',
            publish_time_field='published_at',
            content_separator=' | '
        )
        
        deduplicator_balanced = ContentDeduplicator(
            similarity_threshold=0.7,
            field_mapping=balanced_mapping
        )
        deduplicator_balanced.load_jsonl(temp_file)
        clusters_balanced = deduplicator_balanced.cluster_and_deduplicate()
        
        print(f"✅ 載入 {len(deduplicator_balanced.content_items)} 項目")
        print(f"📊 產生 {len(clusters_balanced)} 個群集")
        print("📝 代表項目範例：")
        if clusters_balanced:
            rep = clusters_balanced[0].representative
            print(f"   標題: {rep.title}")
            print(f"   作者: {rep.author}")
            print(f"   分類: {rep.category} (預設值)")
            print(f"   圖片: {len(rep.images)} 張 (預設值)")
            print(f"   發布時間: {rep.publish_time}")
        
        # 3. 精簡版映射 (Minimal FieldMapping)
        print("\n🎯 3. 精簡版映射 (Minimal FieldMapping)")
        print("-" * 40)
        
        minimal_mapping = create_minimal_custom_mapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            id_field='permalink',
            content_separator=' | '
        )
        
        deduplicator_minimal = ContentDeduplicator(
            similarity_threshold=0.7,
            field_mapping=minimal_mapping
        )
        deduplicator_minimal.load_jsonl(temp_file)
        clusters_minimal = deduplicator_minimal.cluster_and_deduplicate()
        
        print(f"✅ 載入 {len(deduplicator_minimal.content_items)} 項目")
        print(f"📊 產生 {len(clusters_minimal)} 個群集")
        print("📝 代表項目範例：")
        if clusters_minimal:
            rep = clusters_minimal[0].representative
            print(f"   標題: {rep.title}")
            print(f"   作者: {rep.author} (預設值)")
            print(f"   分類: {rep.category} (預設值)")
            print(f"   圖片: {len(rep.images)} 張 (預設值)")
            print(f"   發布時間: {rep.publish_time} (預設值)")
        
        # 4. 去重效果比較
        print("\n📈 4. 去重效果比較")
        print("-" * 40)
        print(f"完整版群集數: {len(clusters_full)}")
        print(f"平衡版群集數: {len(clusters_balanced)}")
        print(f"精簡版群集數: {len(clusters_minimal)}")
        
        # 核心去重功能應該相同
        if len(clusters_full) == len(clusters_balanced) == len(clusters_minimal):
            print("✅ 所有版本的去重效果一致")
        else:
            print("⚠️ 不同版本的去重效果有差異")
        
        # 5. 記憶體和配置複雜度比較
        print("\n💾 5. 配置複雜度比較")
        print("-" * 40)
        
        # 統計映射物件的屬性數量
        full_attrs = len([attr for attr in dir(full_mapping) if not attr.startswith('_') and not callable(getattr(full_mapping, attr))])
        balanced_attrs = len([attr for attr in dir(balanced_mapping) if not attr.startswith('_') and not callable(getattr(balanced_mapping, attr))])
        minimal_attrs = len([attr for attr in dir(minimal_mapping) if not attr.startswith('_') and not callable(getattr(minimal_mapping, attr))])
        
        print(f"完整版配置屬性: {full_attrs}")
        print(f"平衡版配置屬性: {balanced_attrs}")
        print(f"精簡版配置屬性: {minimal_attrs}")
        
        print(f"\n配置簡化效果:")
        print(f"  平衡版 vs 完整版: {(1 - balanced_attrs/full_attrs)*100:.1f}% 減少")
        print(f"  精簡版 vs 完整版: {(1 - minimal_attrs/full_attrs)*100:.1f}% 減少")
        
    finally:
        Path(temp_file).unlink()


def demo_predefined_mapping_types():
    """演示預定義映射的三種類型"""
    print("\n\n🗂️ 預定義映射類型演示")
    print("=" * 60)
    
    # 使用字串前綴指定映射類型
    mapping_examples = [
        ("news", "標準新聞格式"),
        ("balanced-news", "平衡版新聞格式"),
        ("minimal-news", "精簡版新聞格式"),
        ("blog", "標準部落格格式"),
        ("balanced-blog", "平衡版部落格格式"),
        ("minimal-blog", "精簡版部落格格式")
    ]
    
    for mapping_name, description in mapping_examples:
        print(f"\n📌 {description} ({mapping_name})")
        try:
            deduplicator = ContentDeduplicator(field_mapping=mapping_name)
            mapping = deduplicator.field_mapping
            print(f"   類型: {type(mapping).__name__}")
            print(f"   標題欄位: {mapping.title_field}")
            print(f"   內容欄位: {mapping.content_fields}")
            print(f"   ID欄位: {mapping.id_field}")
            
            # 檢查是否有額外欄位
            if hasattr(mapping, 'author_field'):
                print(f"   作者欄位: {mapping.author_field}")
            if hasattr(mapping, 'category_field'):
                print(f"   分類欄位: {mapping.category_field}")
                
        except ValueError as e:
            print(f"   ❌ 錯誤: {e}")


def demo_performance_comparison():
    """效能比較演示"""
    print("\n\n⚡ 效能比較演示")
    print("=" * 60)
    
    import time
    
    # 創建較大的測試資料集
    large_sample_data = []
    base_data = create_sample_data()
    
    for i in range(50):  # 創建 150 個項目
        for j, item in enumerate(base_data):
            new_item = item.copy()
            new_item['headline'] = f"{item['headline']} - 變體 {i}-{j}"
            new_item['permalink'] = f"{item['permalink']}-{i}-{j}"
            large_sample_data.append(new_item)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in large_sample_data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
        temp_file = f.name
    
    try:
        print(f"📊 測試資料: {len(large_sample_data)} 個項目")
        
        # 測試三種映射的處理時間
        mapping_types = [
            ("完整版", create_custom_mapping(
                title_field='headline',
                content_fields=['body', 'summary'],
                id_field='permalink',
                author_field='writer',
                category_field='tags',
                publish_time_field='published_at',
                images_field='images',
                fetch_time_field='crawled_at'
            )),
            ("平衡版", create_balanced_mapping(
                title_field='headline',
                content_fields=['body', 'summary'],
                id_field='permalink',
                author_field='writer',
                publish_time_field='published_at'
            )),
            ("精簡版", create_minimal_custom_mapping(
                title_field='headline',
                content_fields=['body', 'summary'],
                id_field='permalink'
            ))
        ]
        
        for name, mapping in mapping_types:
            start_time = time.time()
            
            deduplicator = ContentDeduplicator(
                similarity_threshold=0.8,
                field_mapping=mapping
            )
            deduplicator.load_jsonl(temp_file)
            clusters = deduplicator.cluster_and_deduplicate()
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"\n{name}映射:")
            print(f"   處理時間: {processing_time:.3f} 秒")
            print(f"   群集數量: {len(clusters)}")
            print(f"   記憶體項目: {len(deduplicator.content_items)}")
        
    finally:
        Path(temp_file).unlink()


if __name__ == "__main__":
    demo_mapping_comparison()
    demo_predefined_mapping_types()
    demo_performance_comparison()
    
    print("\n\n🎯 總結建議")
    print("=" * 60)
    print("💡 精簡版 (MinimalFieldMapping):")
    print("   ✅ 適用於: 效能敏感、大量資料處理、簡單去重需求")
    print("   ✅ 優點: 配置簡單、記憶體使用少、處理速度快")
    print("   ⚠️ 限制: 代表選擇品質較低、資料結構較簡單")
    
    print("\n⚖️ 平衡版 (BalancedFieldMapping):")
    print("   ✅ 適用於: 一般使用場景、需要較好代表選擇")
    print("   ✅ 優點: 平衡功能性與簡潔性、更好的代表選擇")
    print("   ⚠️ 限制: 比精簡版稍複雜")
    
    print("\n📋 完整版 (FieldMapping):")
    print("   ✅ 適用於: 複雜需求、完整資料結構、多樣化輸出")
    print("   ✅ 優點: 功能完整、資料結構豐富")
    print("   ⚠️ 限制: 配置複雜、記憶體使用較多")
    
    print("\n🚀 建議使用順序: 精簡版 → 平衡版 → 完整版")
    print("   根據實際需求選擇最適合的版本！")
