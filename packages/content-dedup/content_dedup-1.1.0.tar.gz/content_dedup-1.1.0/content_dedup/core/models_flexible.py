"""
Flexible data model with original data preservation and dynamic field usage.
基於使用者需求的全彈性架構設計。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set, Union


@dataclass
class FlexibleContentItem:
    """
    彈性內容項目 - 保留原始資料並動態使用所需欄位
    
    設計理念：
    1. 完整保留原始資料
    2. 只提取當前工作所需的欄位
    3. 支援任意欄位組合
    4. 零資料丟失
    """
    
    # 原始完整資料
    original_data: Dict[str, Any] = field(default_factory=dict)
    
    # 當前工作使用的欄位（從原始資料提取）
    working_fields: Dict[str, Any] = field(default_factory=dict)
    
    # 欄位映射配置（記錄哪些原始欄位映射到哪些工作欄位）
    field_mapping_info: Dict[str, str] = field(default_factory=dict)
    
    # 語言資訊（計算後的中繼資料）
    language: Optional[str] = None
    
    def __post_init__(self):
        """確保必要的工作欄位存在"""
        required_fields = {'title', 'content_text', 'url'}
        missing_fields = required_fields - set(self.working_fields.keys())
        
        if missing_fields:
            # 如果工作欄位缺失，嘗試從原始資料中補充預設值
            for field_name in missing_fields:
                self.working_fields[field_name] = ""
    
    @classmethod
    def from_raw_data(cls, 
                     original_data: Dict[str, Any], 
                     field_mapping,
                     required_fields: Optional[List[str]] = None) -> "FlexibleContentItem":
        """
        從原始資料建立彈性內容項目
        
        Args:
            original_data: 完整的原始 JSON 資料
            field_mapping: 欄位映射配置
            required_fields: 此次工作需要的欄位（如 ['title', 'content_text', 'url']）
        """
        if required_fields is None:
            required_fields = ['title', 'content_text', 'url']
        
        # 使用欄位映射提取工作欄位
        mapped_data = field_mapping.map_to_content_item_dict(original_data)
        
        # 只保留所需的工作欄位
        working_fields = {
            field: mapped_data.get(field, "")
            for field in required_fields
        }
        
        # 建立欄位映射資訊記錄
        mapping_info = {}
        if hasattr(field_mapping, 'title_field'):
            mapping_info['title'] = str(field_mapping.title_field)
        if hasattr(field_mapping, 'content_fields'):
            mapping_info['content_text'] = str(field_mapping.content_fields)
        if hasattr(field_mapping, 'id_field'):
            mapping_info['url'] = str(field_mapping.id_field)
        
        return cls(
            original_data=original_data.copy(),  # 完整保留
            working_fields=working_fields,       # 只保留工作需要的
            field_mapping_info=mapping_info
        )
    
    @classmethod
    def from_minimal_fields(cls, title: str, content_text: str, url: str, **kwargs) -> "FlexibleContentItem":
        """
        從最小欄位集建立（用於測試或簡單使用情況）
        """
        working_fields = {
            'title': title,
            'content_text': content_text,
            'url': url
        }
        working_fields.update(kwargs)
        
        return cls(
            original_data=working_fields.copy(),
            working_fields=working_fields
        )
    
    # 屬性存取器 - 提供便利的存取方式
    @property
    def title(self) -> str:
        """標題"""
        return self.working_fields.get('title', '')
    
    @property
    def content_text(self) -> str:
        """內容文字"""
        return self.working_fields.get('content_text', '')
    
    @property
    def url(self) -> str:
        """URL"""
        return self.working_fields.get('url', '')
    
    def get_working_field(self, field_name: str, default=None):
        """取得工作欄位值"""
        return self.working_fields.get(field_name, default)
    
    def get_original_field(self, field_name: str, default=None):
        """取得原始欄位值"""
        return self.original_data.get(field_name, default)
    
    def set_working_field(self, field_name: str, value: Any):
        """設定工作欄位值"""
        self.working_fields[field_name] = value
    
    def get_all_original_fields(self) -> Dict[str, Any]:
        """取得所有原始欄位"""
        return self.original_data.copy()
    
    def get_working_fields(self) -> Dict[str, Any]:
        """取得當前工作欄位"""
        return self.working_fields.copy()
    
    def extend_working_fields(self, additional_fields: List[str]):
        """
        擴展工作欄位 - 從原始資料中提取更多欄位到工作集
        
        Args:
            additional_fields: 需要新增到工作集的欄位名稱
        """
        for field_name in additional_fields:
            if field_name in self.original_data and field_name not in self.working_fields:
                self.working_fields[field_name] = self.original_data[field_name]
    
    def to_dict(self, 
               mode: str = "working", 
               include_metadata: bool = False) -> Dict[str, Any]:
        """
        轉換為字典格式
        
        Args:
            mode: 輸出模式
                - "working": 只輸出工作欄位
                - "original": 只輸出原始資料  
                - "both": 輸出兩者
                - "compatible": 相容模式（模擬原 ContentItem 格式）
            include_metadata: 是否包含中繼資料（欄位映射資訊等）
        """
        if mode == "working":
            result = self.working_fields.copy()
            if self.language:
                result['language'] = self.language
                
        elif mode == "original":
            result = self.original_data.copy()
            
        elif mode == "both":
            result = {
                'working_fields': self.working_fields.copy(),
                'original_data': self.original_data.copy()
            }
            if self.language:
                result['language'] = self.language
                
        elif mode == "compatible":
            # 向後相容模式 - 模擬原始 ContentItem 的 9 個欄位
            result = {
                'title': self.title,
                'content_text': self.content_text,
                'url': self.url,
                'original_url': self.get_working_field('original_url', self.url),
                'category': self.get_working_field('category', []),
                'publish_time': self.get_working_field('publish_time', ''),
                'author': self.get_working_field('author', ''),
                'images': self.get_working_field('images', []),
                'fetch_time': self.get_working_field('fetch_time', ''),
                'language': self.language
            }
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        if include_metadata:
            result['_metadata'] = {
                'field_mapping_info': self.field_mapping_info,
                'working_field_count': len(self.working_fields),
                'original_field_count': len(self.original_data)
            }
        
        return result
    
    def memory_footprint(self) -> Dict[str, int]:
        """估算記憶體使用量"""
        import sys
        
        original_size = sys.getsizeof(str(self.original_data))
        working_size = sys.getsizeof(str(self.working_fields))
        
        return {
            'original_data_bytes': original_size,
            'working_fields_bytes': working_size,
            'total_bytes': original_size + working_size,
            'overhead_ratio': working_size / original_size if original_size > 0 else 0
        }
    
    def __repr__(self) -> str:
        """字串表示"""
        working_count = len(self.working_fields)
        original_count = len(self.original_data)
        return f"FlexibleContentItem(working_fields={working_count}, original_fields={original_count})"


@dataclass
class FlexibleContentCluster:
    """彈性內容分群"""
    representative: FlexibleContentItem
    members: List[FlexibleContentItem]
    cluster_id: str
    dominant_language: str
    language_distribution: Dict[str, float] = field(default_factory=dict)
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self, output_mode: str = "working", include_metadata: bool = False) -> Dict[str, Any]:
        """
        轉換為字典格式
        
        Args:
            output_mode: 成員項目的輸出模式（傳遞給 FlexibleContentItem.to_dict）
            include_metadata: 是否包含中繼資料
        """
        result = {
            'cluster_id': self.cluster_id,
            'representative': self.representative.to_dict(output_mode, include_metadata),
            'members': [item.to_dict(output_mode, include_metadata) for item in self.members],
            'member_count': len(self.members),
            'dominant_language': self.dominant_language,
            'language_distribution': self.language_distribution,
            'similarity_scores': self.similarity_scores
        }
        
        if include_metadata:
            result['_cluster_metadata'] = {
                'avg_original_fields': sum(len(item.original_data) for item in self.members) / len(self.members),
                'avg_working_fields': sum(len(item.working_fields) for item in self.members) / len(self.members)
            }
        
        return result
    
    @property
    def size(self) -> int:
        """取得分群大小"""
        return len(self.members)
    
    def is_mixed_language(self, threshold: float = 0.3) -> bool:
        """檢查是否為混合語言分群"""
        if not self.language_distribution:
            return False
        
        sorted_langs = sorted(self.language_distribution.values(), reverse=True)
        return len(sorted_langs) >= 2 and sorted_langs[1] > threshold


# 工廠函數
def create_flexible_content_item(original_data: Dict[str, Any], 
                               field_mapping,
                               work_mode: str = "minimal") -> FlexibleContentItem:
    """
    建立彈性內容項目的工廠函數
    
    Args:
        original_data: 原始資料
        field_mapping: 欄位映射配置
        work_mode: 工作模式
            - "minimal": 只使用核心欄位 (title, content_text, url)
            - "balanced": 使用重要欄位 (+ category, publish_time)  
            - "full": 使用所有映射欄位
    """
    field_sets = {
        "minimal": ['title', 'content_text', 'url'],
        "balanced": ['title', 'content_text', 'url', 'category', 'publish_time'],
        "full": ['title', 'content_text', 'url', 'original_url', 'category', 
                'publish_time', 'author', 'images', 'fetch_time']
    }
    
    required_fields = field_sets.get(work_mode, field_sets["minimal"])
    
    return FlexibleContentItem.from_raw_data(
        original_data=original_data,
        field_mapping=field_mapping,
        required_fields=required_fields
    )
