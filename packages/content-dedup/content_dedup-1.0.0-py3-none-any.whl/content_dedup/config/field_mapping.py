"""
Field mapping configuration for flexible JSONL processing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union


@dataclass
class FieldMapping:
    """Configuration for mapping JSON fields to ContentItem attributes"""
    
    # Core required fields
    title_field: Union[str, List[str]] = "title"
    content_fields: Union[str, List[str]] = "content_text"
    
    # Optional fields with defaults
    id_field: Union[str, List[str]] = "url"  # Unique identifier for deduplication
    category_field: str = "category"
    publish_time_field: str = "publish_time"
    
    # Field concatenation settings
    content_separator: str = " "
    title_separator: str = " "
    
    # Default values for missing fields
    default_values: Dict[str, Any] = field(default_factory=lambda: {
        'url': '',
        'original_url': '',
        'category': [],
        'publish_time': '',
        'author': '',
        'images': [],
        'fetch_time': ''
    })
    
    # Whether to ignore missing required fields
    ignore_missing_required: bool = False
    
    def extract_field_value(self, data: Dict[str, Any], field_name: Union[str, List[str]], 
                          separator: str = " ", default: Any = None) -> Any:
        """
        Extract field value from JSON data with support for multiple fields
        
        Args:
            data: JSON data dictionary
            field_name: Single field name or list of field names
            separator: Separator for concatenating multiple fields
            default: Default value if field not found
            
        Returns:
            Extracted field value
        """
        if isinstance(field_name, str):
            return data.get(field_name, default)
        
        elif isinstance(field_name, list):
            values = []
            for fname in field_name:
                value = data.get(fname)
                if value is not None:
                    if isinstance(value, str):
                        values.append(value.strip())
                    elif isinstance(value, (list, tuple)):
                        values.extend([str(v).strip() for v in value if v])
                    else:
                        values.append(str(value).strip())
            
            if values:
                return separator.join(filter(None, values))
            return default
        
        return default
    
    def map_to_content_item_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map JSON data to ContentItem dictionary format
        
        Args:
            data: Input JSON data
            
        Returns:
            Dictionary compatible with ContentItem.from_dict()
            
        Raises:
            ValueError: If required fields are missing and ignore_missing_required is False
        """
        result = {}
        
        # Extract title
        title = self.extract_field_value(data, self.title_field, self.title_separator, "")
        if not title and not self.ignore_missing_required:
            raise ValueError(f"Title field(s) {self.title_field} not found or empty")
        result['title'] = title
        
        # Extract content
        content = self.extract_field_value(data, self.content_fields, self.content_separator, "")
        if not content and not self.ignore_missing_required:
            raise ValueError(f"Content field(s) {self.content_fields} not found or empty")
        result['content_text'] = content
        
        # Extract other fields with defaults
        id_value = self.extract_field_value(data, self.id_field, default=self.default_values['url'])
        result['url'] = id_value
        result['original_url'] = id_value  # Use same value for compatibility
        
        # Handle category (should be list)
        category_value = self.extract_field_value(data, self.category_field, 
                                                 default=self.default_values['category'])
        if isinstance(category_value, str):
            result['category'] = [category_value] if category_value else []
        elif isinstance(category_value, (list, tuple)):
            result['category'] = list(category_value)
        else:
            result['category'] = self.default_values['category']
        
        result['publish_time'] = self.extract_field_value(data, self.publish_time_field,
                                                         default=self.default_values['publish_time'])
        
        # Handle backward compatibility for fields that may still exist in data
        # but are not in the optimized field mapping
        result['author'] = data.get('author', self.default_values['author'])
        result['images'] = data.get('images', self.default_values['images'])
        result['fetch_time'] = data.get('fetch_time', self.default_values['fetch_time'])
        
        return result


# Predefined field mappings for common formats
PREDEFINED_MAPPINGS = {
    'default': FieldMapping(),
    
    'news': FieldMapping(
        title_field="title",
        content_fields=["content", "body", "text"],
        id_field=["url", "permalink"],
        publish_time_field="published_at",
        category_field="tags"
    ),
    
    'blog': FieldMapping(
        title_field="title",
        content_fields=["content", "body"],
        id_field=["permalink", "url"],
        publish_time_field="date",
        category_field="categories"
    ),
    
    'social': FieldMapping(
        title_field=["title", "subject"],
        content_fields=["text", "content", "message"],
        id_field=["link", "url", "post_id"],
        publish_time_field="timestamp"
    ),
    
    'academic': FieldMapping(
        title_field="title",
        content_fields=["abstract", "content"],
        id_field=["doi", "url"],
        publish_time_field="publication_date",
        category_field="subjects"
    ),
    
    'ecommerce': FieldMapping(
        title_field="name",
        content_fields=["description", "features"],
        id_field=["product_url", "sku", "id"],
        category_field="category"
    )
}


def get_field_mapping(mapping_name: str = 'default') -> FieldMapping:
    """
    Get predefined field mapping by name
    
    Args:
        mapping_name: Name of predefined mapping
        
    Returns:
        FieldMapping instance
        
    Raises:
        ValueError: If mapping name not found
    """
    if mapping_name not in PREDEFINED_MAPPINGS:
        available = list(PREDEFINED_MAPPINGS.keys())
        raise ValueError(f"Unknown mapping '{mapping_name}'. Available: {available}")
    
    return PREDEFINED_MAPPINGS[mapping_name]


def create_custom_mapping(**kwargs) -> FieldMapping:
    """
    Create custom field mapping with keyword arguments
    
    Args:
        **kwargs: Field mapping parameters
        
    Returns:
        FieldMapping instance
    """
    # Handle backward compatibility: map old field names to new ones
    if 'url_field' in kwargs:
        kwargs['id_field'] = kwargs.pop('url_field')
    if 'author_field' in kwargs:
        # For backward compatibility, map author_field to category_field
        kwargs['category_field'] = kwargs.pop('author_field')
    
    # Remove unsupported fields that may still be in test cases
    unsupported_fields = ['original_url_field', 'images_field', 'fetch_time_field']
    for field in unsupported_fields:
        kwargs.pop(field, None)
    
    return FieldMapping(**kwargs)
