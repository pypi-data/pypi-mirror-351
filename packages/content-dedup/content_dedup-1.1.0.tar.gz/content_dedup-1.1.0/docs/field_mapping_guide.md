# Field Mapping 使用指南

## 概述

`py-content-dedup` 的欄位映射功能讓您可以處理各種不同格式的 JSONL 資料，而不需要預先轉換資料格式。

## 核心功能

### 1. 預定義映射

內建支援常見的資料格式：

- `default`: 標準格式
- `news`: 新聞資料
- `blog`: 部落格資料  
- `social`: 社群媒體資料
- `academic`: 學術論文資料
- `ecommerce`: 電商產品資料

### 2. 自訂映射

可以指定任意欄位名稱和組合：

- 單一欄位映射：`title_field='headline'`
- 多欄位合併：`content_fields=['body', 'summary', 'description']`
- 自訂分隔符：`content_separator=' | '`
- 容錯處理：`ignore_missing_required=True`

### 3. CLI 支援

命令列直接指定欄位映射，無需程式碼修改。

## 使用方式

### Python API

```python
from content_dedup import ContentDeduplicator
from content_dedup.config.field_mapping import create_custom_mapping

# 方法 1: 使用預定義映射
deduplicator = ContentDeduplicator(field_mapping='news')

# 方法 2: 建立自訂映射
custom_mapping = create_custom_mapping(
    title_field='headline',
    content_fields=['body', 'summary'],
    url_field='permalink',
    content_separator=' | '
)
deduplicator = ContentDeduplicator(field_mapping=custom_mapping)
```

### CLI 命令

```bash
# 使用預定義映射
content-dedup data.jsonl --field-mapping news

# 自訂欄位映射
content-dedup data.jsonl \
  --title-field headline \
  --content-fields body,summary \
  --content-separator ' | '

# 容錯處理
content-dedup data.jsonl \
  --title-field title,name \
  --ignore-missing
```

## 資料格式範例

### 標準格式
```json
{
  "title": "文章標題",
  "content_text": "文章內容",
  "url": "https://example.com",
  "author": "作者"
}
```

### 新聞格式 (需要映射)
```json
{
  "headline": "新聞標題",
  "body": "新聞內容",
  "summary": "新聞摘要",
  "permalink": "https://news.com/article",
  "writer": "記者"
}
```

### 社群媒體格式 (需要映射)
```json
{
  "username": "用戶名",
  "message": "貼文內容",
  "post_url": "https://social.com/post/123",
  "timestamp": "2025-05-27T10:00:00Z"
}
```

## 進階用法

### 多欄位合併

當您有多個相關欄位需要合併為內容時：

```python
mapping = create_custom_mapping(
    content_fields=['description', 'details', 'specifications'],
    content_separator='\n\n'  # 使用換行分隔
)
```

### 容錯處理

當資料品質不一致時：

```python
mapping = create_custom_mapping(
    title_field=['title', 'name', 'subject'],  # 嘗試多個可能的欄位
    ignore_missing_required=True,  # 不因缺少必要欄位而失敗
    default_values={
        'author': '未知作者',
        'url': 'https://unknown.com'
    }
)
```

### 混合格式處理

處理包含多種格式的資料：

```python
flexible_mapping = create_custom_mapping(
    title_field=['headline', 'title', 'subject', 'name'],
    content_fields=['body', 'content', 'text', 'message', 'description'],
    url_field=['url', 'link', 'permalink', 'post_url'],
    author_field=['author', 'writer', 'username', 'creator']
)
```

## 最佳實踐

1. **先檢視資料結構**：了解您的 JSONL 資料包含哪些欄位
2. **選擇合適的映射**：優先使用預定義映射，需要時建立自訂映射
3. **測試小樣本**：在處理大量資料前先測試映射配置
4. **考慮容錯性**：對於資料品質不一致的情況，啟用容錯選項
5. **記錄映射配置**：將成功的映射配置保存供未來使用

## 常見問題

**Q: 如何處理巢狀 JSON 結構？**
A: 目前版本支援一層結構，巢狀結構需要預處理。

**Q: 可以動態修改映射嗎？**
A: 可以，映射物件的屬性可以在運行時修改。

**Q: 如何處理多語言欄位名稱？**
A: 欄位映射支援任何 Unicode 字串作為欄位名稱。

**Q: 映射失敗時會發生什麼？**
A: 預設會拋出錯誤，可設定 `ignore_missing_required=True` 來跳過問題資料。
