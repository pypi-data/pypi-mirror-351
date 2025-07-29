"""
完整示範彈性架構的使用方式和優勢
"""

import json
import sys
from pathlib import Path

# 加入專案路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from content_dedup.core.models_flexible import FlexibleContentItem, create_flexible_content_item
from content_dedup.config.field_mapping import get_field_mapping


def demo_flexible_architecture():
    """示範彈性架構的完整功能"""
    print("🚀 彈性架構完整示範")
    print("=" * 80)
    
    # 模擬複雜的原始資料（12 個欄位）
    complex_original_data = {
        "title": "AI 革命：機器學習新突破",
        "content": "人工智慧領域迎來重大突破，新的深度學習演算法展現出驚人的性能提升",
        "summary": "研究團隊開發出革命性的機器學習算法",
        "url": "https://tech.example.com/ai-breakthrough-2025",
        "author": "張三博士",
        "published_at": "2025-01-15T10:30:00Z",
        "tags": ["AI", "機器學習", "科技突破"],
        "source_site": "TechDaily",
        "view_count": 25000,
        "external_id": "td_ai_2025_001",
        "metadata": {
            "editor": "李四",
            "department": "科技組",
            "priority": "高",
            "source_quality": "A+"
        },
        "social_metrics": {
            "likes": 1250,
            "shares": 380,
            "comments": 97
        }
    }
    
    print(f"📊 原始資料：{len(complex_original_data)} 個頂層欄位")
    print(f"   總欄位數（包含巢狀）：{count_all_fields(complex_original_data)} 個")
    print()
    
    # 取得欄位映射
    field_mapping = get_field_mapping('news')
    
    # 示範不同工作模式
    modes = ["minimal", "balanced", "full"]
    
    for mode in modes:
        print(f"🔧 工作模式：{mode.upper()}")
        print("-" * 50)
        
        # 建立彈性內容項目
        item = create_flexible_content_item(
            original_data=complex_original_data,
            field_mapping=field_mapping,
            work_mode=mode
        )
        
        print(f"   工作欄位：{len(item.working_fields)} 個")
        print(f"   原始欄位：{len(item.original_data)} 個（100% 保留）")
        
        # 展示工作欄位
        print("   工作欄位內容：")
        for field, value in item.working_fields.items():
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f"     {field}: {value}")
        
        # 記憶體使用分析
        memory_info = item.memory_footprint()
        print(f"   記憶體使用：{memory_info['total_bytes']} bytes")
        print(f"   額外負擔：{memory_info['overhead_ratio']:.1%}")
        print()


def demo_dynamic_field_access():
    """示範動態欄位存取"""
    print("🔍 動態欄位存取示範")
    print("=" * 80)
    
    # 建立測試資料
    original_data = {
        "title": "測試新聞",
        "content": "這是新聞內容",
        "url": "https://example.com/news",
        "source_site": "新聞網",
        "view_count": 5000,
        "editor_notes": "重要新聞",
        "custom_field": "自定義資料"
    }
    
    field_mapping = get_field_mapping('news')
    item = create_flexible_content_item(original_data, field_mapping, "minimal")
    
    print("1️⃣ 基本工作欄位存取：")
    print(f"   標題：{item.title}")
    print(f"   URL：{item.url}")
    print()
    
    print("2️⃣ 原始欄位存取（零損失）：")
    print(f"   來源網站：{item.get_original_field('source_site')}")
    print(f"   瀏覽次數：{item.get_original_field('view_count')}")
    print(f"   編輯備註：{item.get_original_field('editor_notes')}")
    print(f"   自定義欄位：{item.get_original_field('custom_field')}")
    print()
    
    print("3️⃣ 動態擴展工作欄位：")
    print(f"   擴展前工作欄位：{list(item.working_fields.keys())}")
    
    # 動態添加需要的欄位到工作集
    item.extend_working_fields(['source_site', 'view_count'])
    print(f"   擴展後工作欄位：{list(item.working_fields.keys())}")
    print(f"   現在可以直接存取：{item.get_working_field('view_count')}")
    print()


def demo_flexible_output_modes():
    """示範彈性輸出模式"""
    print("📤 彈性輸出模式示範")
    print("=" * 80)
    
    original_data = {
        "title": "輸出測試新聞",
        "content": "測試不同輸出模式",
        "url": "https://example.com/output-test",
        "author": "測試作者",
        "tags": ["測試"],
        "extra_info": "額外資訊",
        "metrics": {"views": 1000}
    }
    
    field_mapping = get_field_mapping('news') 
    item = create_flexible_content_item(original_data, field_mapping, "balanced")
    
    output_modes = [
        ("working", "只輸出工作欄位"),
        ("original", "只輸出原始資料"),
        ("compatible", "向後相容模式"),
        ("both", "輸出兩者")
    ]
    
    for mode, description in output_modes:
        print(f"🔸 {mode.upper()} 模式 - {description}：")
        output = item.to_dict(mode=mode, include_metadata=True)
        
        if mode == "both":
            print(f"   工作欄位數：{len(output.get('working_fields', {}))}")
            print(f"   原始欄位數：{len(output.get('original_data', {}))}")
        else:
            print(f"   輸出欄位數：{len([k for k in output.keys() if not k.startswith('_')])}")
        
        if '_metadata' in output:
            meta = output['_metadata']
            print(f"   中繼資料：工作欄位 {meta['working_field_count']} / 原始欄位 {meta['original_field_count']}")
        print()


def demo_memory_efficiency():
    """示範記憶體效率對比"""
    print("💾 記憶體效率對比")
    print("=" * 80)
    
    # 建立大型資料集模擬
    large_original_data = {
        f"field_{i}": f"value_{i}" * 10  # 模擬較大的欄位值
        for i in range(20)  # 20 個欄位
    }
    
    # 核心欄位
    large_original_data.update({
        "title": "大型資料測試",
        "content_text": "這是一個大型資料的測試內容" * 20,
        "url": "https://example.com/large-data-test"
    })
    
    field_mapping = get_field_mapping('default')
    
    # 不同模式的記憶體使用
    modes = ["minimal", "balanced", "full"]
    
    print("記憶體使用對比（單一項目）：")
    for mode in modes:
        item = create_flexible_content_item(large_original_data, field_mapping, mode)
        memory_info = item.memory_footprint()
        
        print(f"   {mode.upper():<8}: "
              f"總計 {memory_info['total_bytes']:>6} bytes, "
              f"工作欄位 {memory_info['working_fields_bytes']:>4} bytes, "
              f"負擔 {memory_info['overhead_ratio']:>5.1%}")
    
    print()
    
    # 大規模資料集估算
    print("大規模資料集記憶體估算：")
    dataset_sizes = [1000, 10000, 100000]
    
    for size in dataset_sizes:
        minimal_item = create_flexible_content_item(large_original_data, field_mapping, "minimal")
        single_item_memory = minimal_item.memory_footprint()['total_bytes']
        total_memory_mb = (size * single_item_memory) / 1024 / 1024
        
        print(f"   {size:>6,} 筆記錄：約 {total_memory_mb:.1f} MB")


def demo_backward_compatibility():
    """示範向後相容性"""
    print("🔄 向後相容性示範")
    print("=" * 80)
    
    original_data = {
        "title": "相容性測試",
        "content": "測試與原始 ContentItem 的相容性",
        "url": "https://example.com/compatibility"
    }
    
    field_mapping = get_field_mapping('news')
    flexible_item = create_flexible_content_item(original_data, field_mapping, "full")
    
    # 產生相容模式輸出
    compatible_output = flexible_item.to_dict(mode="compatible")
    
    print("✅ 相容模式輸出（模擬原始 ContentItem 格式）：")
    expected_fields = [
        'title', 'content_text', 'url', 'original_url', 
        'category', 'publish_time', 'author', 'images', 
        'fetch_time', 'language'
    ]
    
    for field in expected_fields:
        value = compatible_output.get(field, "❌ MISSING")
        print(f"   {field:<15}: {value}")
    
    print(f"\n✅ 所有必要欄位都存在：{all(field in compatible_output for field in expected_fields)}")


def count_all_fields(data, prefix=""):
    """遞歸計算所有欄位數量（包含巢狀）"""
    count = 0
    for key, value in data.items():
        count += 1
        if isinstance(value, dict):
            count += count_all_fields(value, f"{prefix}{key}.")
    return count


if __name__ == "__main__":
    demo_flexible_architecture()
    demo_dynamic_field_access()
    demo_flexible_output_modes()
    demo_memory_efficiency()
    demo_backward_compatibility()
    
    print("\n🎉 彈性架構示範完成！")
    print("\n💡 彈性架構的主要優勢：")
    print("   ✅ 零資料丟失：完整保留原始資料")
    print("   ✅ 記憶體彈性：只載入需要的工作欄位")
    print("   ✅ 動態擴展：隨時可以添加更多工作欄位")
    print("   ✅ 多種輸出：支援不同的輸出格式需求")
    print("   ✅ 向後相容：完全相容現有 API")
    print("   ✅ 彈性配置：支援 minimal/balanced/full 三種工作模式")
