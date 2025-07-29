"""
Field mapping usage examples for py-content-dedup
"""

from content_dedup import ContentDeduplicator
from content_dedup.config.field_mapping import create_custom_mapping, get_field_mapping

def example_1_predefined_mapping():
    """Example 1: Using predefined field mappings"""
    print("Example 1: Predefined mappings")
    
    # News format
    deduplicator = ContentDeduplicator(field_mapping='news')
    
    # Blog format  
    deduplicator = ContentDeduplicator(field_mapping='blog')
    
    # Social media format
    deduplicator = ContentDeduplicator(field_mapping='social')
    
    print("✓ Initialized with predefined mappings")


def example_2_custom_mapping():
    """Example 2: Custom field mapping for specific data format"""
    print("\nExample 2: Custom field mapping")
    
    # Custom mapping for a specific API format
    custom_mapping = create_custom_mapping(
        title_field='headline',  # Single field
        content_fields=['body', 'summary', 'excerpt'],  # Multiple fields combined
        id_field='permalink',
        author_field='writer',
        category_field='tags',
        content_separator=' | ',  # Custom separator
        ignore_missing_required=True  # Don't fail on missing fields
    )
    
    deduplicator = ContentDeduplicator(field_mapping=custom_mapping)
    print("✓ Created custom field mapping")


def example_3_runtime_mapping():
    """Example 3: Runtime field mapping configuration"""
    print("\nExample 3: Runtime configuration")
    
    # Get predefined mapping and modify it
    mapping = get_field_mapping('news')
    mapping.content_fields = ['content', 'description', 'body_text']
    mapping.content_separator = '\n\n'
    
    deduplicator = ContentDeduplicator(field_mapping=mapping)
    print("✓ Modified predefined mapping at runtime")


def example_4_complex_data():
    """Example 4: Complex data structure handling"""
    print("\nExample 4: Complex data handling")
    
    # Handle nested or complex data
    mapping = create_custom_mapping(
        title_field=['article_title', 'post_title', 'name'],
        content_fields=['article_body', 'content.text', 'description'],
        id_field='metadata.url',
        author_field='author.name',
        category_field='classifications',
        default_values={
            'url': 'unknown',
            'author': 'anonymous',
            'category': ['uncategorized']
        }
    )
    
    deduplicator = ContentDeduplicator(field_mapping=mapping)
    print("✓ Setup for complex data structures")


if __name__ == '__main__':
    example_1_predefined_mapping()
    example_2_custom_mapping() 
    example_3_runtime_mapping()
    example_4_complex_data()
    
    print("\n✅ All field mapping examples completed!")
    
    print("\nCLI Usage Examples:")
    print("1. Predefined mapping:")
    print("   content-dedup data.jsonl --field-mapping news")
    
    print("\n2. Custom field mapping:")
    print("   content-dedup data.jsonl --title-field headline --content-fields body,summary")
    
    print("\n3. Multiple content fields:")
    print("   content-dedup data.jsonl --content-fields description,content,text --content-separator ' | '")
    
    print("\n4. Ignore missing fields:")
    print("   content-dedup data.jsonl --ignore-missing --title-field title,name")
