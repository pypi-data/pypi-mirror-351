"""
Balanced field mapping configuration - includes core fields plus important ones.
This version balances functionality with simplicity.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union


@dataclass
class BalancedFieldMapping:
    """Balanced configuration for mapping JSON fields to ContentItem attributes"""
    
    # Core required fields (essential for deduplication)
    title_field: Union[str, List[str]] = "title"
    content_fields: Union[str, List[str]] = "content_text"
    
    # Important fields (enhance deduplication quality)
    id_field: Union[str, List[str]] = "url"   # Important for exact duplicate detection
    category_field: str = "category"           # Improves clustering
    publish_time_field: str = "publish_time"  # Freshness consideration
    
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
        Map JSON data to ContentItem dictionary format (balanced version)
        
        Args:
            data: Input JSON data
            
        Returns:
            Dictionary compatible with ContentItem.from_dict()
            
        Raises:
            ValueError: If required fields are missing and ignore_missing_required is False
        """
        result = {}
        
        # Extract title (required)
        title = self.extract_field_value(data, self.title_field, self.title_separator, "")
        if not title and not self.ignore_missing_required:
            raise ValueError(f"Title field(s) {self.title_field} not found or empty")
        result['title'] = title
        
        # Extract content (required)
        content = self.extract_field_value(data, self.content_fields, self.content_separator, "")
        if not content and not self.ignore_missing_required:
            raise ValueError(f"Content field(s) {self.content_fields} not found or empty")
        result['content_text'] = content
        
        # Extract important fields
        id_value = self.extract_field_value(data, self.id_field, 
                                           default=self.default_values['url'])
        result['url'] = id_value
        result['original_url'] = id_value
        
        result['category'] = self.extract_field_value(data, self.category_field,
                                                    default=self.default_values['category'])
        result['publish_time'] = self.extract_field_value(data, self.publish_time_field,
                                                         default=self.default_values['publish_time'])
        
        # Set default values for non-essential fields
        result['author'] = ""
        result['images'] = []
        result['fetch_time'] = ""
        
        return result


# Predefined balanced field mappings
BALANCED_PREDEFINED_MAPPINGS = {
    'default': BalancedFieldMapping(),
    
    'news': BalancedFieldMapping(
        title_field="title",
        content_fields=["content", "body", "text"],
        id_field="url",
        category_field="category",
        publish_time_field="published_at"
    ),
    
    'blog': BalancedFieldMapping(
        title_field="title",
        content_fields=["content", "body"],
        id_field="permalink",
        category_field="category",
        publish_time_field="date"
    ),
    
    'social': BalancedFieldMapping(
        title_field=["title", "subject"],
        content_fields=["text", "content", "message"],
        id_field="link",
        category_field="tags",
        publish_time_field="timestamp"
    ),
    
    'academic': BalancedFieldMapping(
        title_field="title",
        content_fields=["abstract", "content"],
        id_field="doi",
        category_field="subject",
        publish_time_field="publication_date"
    ),
    
    'ecommerce': BalancedFieldMapping(
        title_field="name",
        content_fields=["description", "features"],
        id_field="product_url",
        category_field="category",
        publish_time_field="created_date"
    )
}


def get_balanced_field_mapping(mapping_name: str = 'default') -> BalancedFieldMapping:
    """
    Get predefined balanced field mapping by name
    
    Args:
        mapping_name: Name of predefined mapping
        
    Returns:
        BalancedFieldMapping instance
        
    Raises:
        ValueError: If mapping name not found
    """
    if mapping_name not in BALANCED_PREDEFINED_MAPPINGS:
        available = list(BALANCED_PREDEFINED_MAPPINGS.keys())
        raise ValueError(f"Unknown mapping '{mapping_name}'. Available: {available}")
    
    return BALANCED_PREDEFINED_MAPPINGS[mapping_name]


def create_balanced_mapping(**kwargs) -> BalancedFieldMapping:
    """
    Create balanced field mapping with keyword arguments
    
    Args:
        **kwargs: Field mapping parameters
        
    Returns:
        BalancedFieldMapping instance
    """
    return BalancedFieldMapping(**kwargs)


def convert_to_balanced(original_mapping) -> BalancedFieldMapping:
    """
    Convert a full FieldMapping to BalancedFieldMapping
    
    Args:
        original_mapping: Original FieldMapping instance
        
    Returns:
        BalancedFieldMapping instance with equivalent core functionality
    """
    return BalancedFieldMapping(
        title_field=original_mapping.title_field,
        content_fields=original_mapping.content_fields,
        id_field=original_mapping.id_field,
        category_field=original_mapping.category_field,
        publish_time_field=original_mapping.publish_time_field,
        content_separator=original_mapping.content_separator,
        default_values=original_mapping.default_values.copy(),
        ignore_missing_required=original_mapping.ignore_missing_required
    )
