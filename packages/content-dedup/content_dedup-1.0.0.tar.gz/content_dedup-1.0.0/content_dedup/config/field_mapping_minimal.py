"""
Minimal field mapping configuration focusing on essential deduplication fields.
This is a simplified version that includes only the most critical fields.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union


@dataclass
class MinimalFieldMapping:
    """Minimal configuration for mapping JSON fields to ContentItem attributes"""
    
    # Core required fields (essential for deduplication)
    title_field: Union[str, List[str]] = "title"
    content_fields: Union[str, List[str]] = "content_text"
    
    # ID field (important for exact duplicate detection)
    id_field: Union[str, List[str]] = "url"
    
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
        Map JSON data to ContentItem dictionary format (minimal version)
        
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
        
        # Extract ID (important for duplicate detection)
        id_value = self.extract_field_value(data, self.id_field, 
                                           default=self.default_values['url'])
        result['url'] = id_value
        result['original_url'] = id_value
        # Set default values for all other fields
        result['category'] = self.default_values['category']
        result['publish_time'] = self.default_values['publish_time']
        result['author'] = self.default_values['author']
        result['images'] = self.default_values['images']
        result['fetch_time'] = self.default_values['fetch_time']
        
        return result


# Predefined minimal field mappings
MINIMAL_PREDEFINED_MAPPINGS = {
    'default': MinimalFieldMapping(),
    
    'news': MinimalFieldMapping(
        title_field="title",
        content_fields=["content", "body", "text"],
        id_field="url"
    ),
    
    'blog': MinimalFieldMapping(
        title_field="title",
        content_fields=["content", "body"],
        id_field="permalink"
    ),
    
    'social': MinimalFieldMapping(
        title_field=["title", "subject"],
        content_fields=["text", "content", "message"],
        id_field="link"
    ),
    
    'academic': MinimalFieldMapping(
        title_field="title",
        content_fields=["abstract", "content"],
        id_field="doi"
    ),
    
    'ecommerce': MinimalFieldMapping(
        title_field="name",
        content_fields=["description", "features"],
        id_field="product_url"
    )
}


def get_minimal_field_mapping(mapping_name: str = 'default') -> MinimalFieldMapping:
    """
    Get predefined minimal field mapping by name
    
    Args:
        mapping_name: Name of predefined mapping
        
    Returns:
        MinimalFieldMapping instance
        
    Raises:
        ValueError: If mapping name not found
    """
    if mapping_name not in MINIMAL_PREDEFINED_MAPPINGS:
        available = list(MINIMAL_PREDEFINED_MAPPINGS.keys())
        raise ValueError(f"Unknown mapping '{mapping_name}'. Available: {available}")
    
    return MINIMAL_PREDEFINED_MAPPINGS[mapping_name]


def create_minimal_custom_mapping(**kwargs) -> MinimalFieldMapping:
    """
    Create custom minimal field mapping with keyword arguments
    
    Args:
        **kwargs: Field mapping parameters
        
    Returns:
        MinimalFieldMapping instance
    """
    # Handle backward compatibility for old parameter names
    if 'url_field' in kwargs:
        kwargs['id_field'] = kwargs.pop('url_field')
    
    # Remove parameters that don't exist in minimal mapping
    removed_params = ['author_field', 'images_field', 'fetch_time_field', 'original_url_field']
    for param in removed_params:
        kwargs.pop(param, None)
    
    return MinimalFieldMapping(**kwargs)


# Migration utilities
def convert_to_minimal(full_mapping) -> MinimalFieldMapping:
    """
    Convert a full FieldMapping to MinimalFieldMapping
    
    Args:
        full_mapping: Original FieldMapping instance
        
    Returns:
        MinimalFieldMapping instance with essential fields only
    """
    return MinimalFieldMapping(
        title_field=full_mapping.title_field,
        content_fields=full_mapping.content_fields,
        id_field=full_mapping.id_field,  # Changed from url_field to id_field
        content_separator=full_mapping.content_separator,
        title_separator=getattr(full_mapping, 'title_separator', ' '),
        default_values=full_mapping.default_values.copy(),
        ignore_missing_required=full_mapping.ignore_missing_required
    )
