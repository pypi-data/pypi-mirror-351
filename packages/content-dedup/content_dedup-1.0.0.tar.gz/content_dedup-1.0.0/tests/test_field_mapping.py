"""
Tests for field mapping functionality
"""

import pytest
import json
from content_dedup.config.field_mapping import FieldMapping, get_field_mapping, create_custom_mapping
from content_dedup.core.models import ContentItem


class TestFieldMapping:
    """Test field mapping functionality"""
    
    def test_default_mapping(self):
        """Test default field mapping"""
        mapping = get_field_mapping('default')
        
        data = {
            'title': 'Test Title',
            'content_text': 'Test Content',
            'url': 'https://example.com',
            'author': 'Test Author'
        }
        
        result = mapping.map_to_content_item_dict(data)
        assert result['title'] == 'Test Title'
        assert result['content_text'] == 'Test Content'
        assert result['url'] == 'https://example.com'
        assert result['author'] == 'Test Author'
    
    def test_single_field_extraction(self):
        """Test single field extraction"""
        mapping = FieldMapping()
        
        data = {'title': 'Single Title'}
        result = mapping.extract_field_value(data, 'title')
        assert result == 'Single Title'
        
        # Test missing field
        result = mapping.extract_field_value(data, 'missing_field', default='default_value')
        assert result == 'default_value'
    
    def test_multiple_field_extraction(self):
        """Test multiple field extraction and concatenation"""
        mapping = FieldMapping()
        
        data = {
            'title1': 'First Title',
            'title2': 'Second Title',
            'content': 'Main content',
            'description': 'Description text'
        }
        
        # Test multiple title fields
        result = mapping.extract_field_value(data, ['title1', 'title2'], separator=' | ')
        assert result == 'First Title | Second Title'
        
        # Test multiple content fields
        result = mapping.extract_field_value(data, ['content', 'description'], separator='\n')
        assert result == 'Main content\nDescription text'
        
        # Test partial matches
        result = mapping.extract_field_value(data, ['missing', 'title1'], separator=' ')
        assert result == 'First Title'
    
    def test_custom_mapping_creation(self):
        """Test custom field mapping creation"""
        mapping = create_custom_mapping(
            title_field=['headline', 'subject'],
            content_fields=['body', 'text', 'content'],
            url_field='permalink',
            content_separator=' | ',
            ignore_missing_required=True
        )
        
        data = {
            'headline': 'News Headline',
            'body': 'News body',
            'text': 'Additional text',
            'permalink': 'https://news.example.com/1'
        }
        
        result = mapping.map_to_content_item_dict(data)
        assert result['title'] == 'News Headline'
        assert result['content_text'] == 'News body | Additional text'
        assert result['url'] == 'https://news.example.com/1'
    
    def test_predefined_mappings(self):
        """Test all predefined mappings"""
        mappings = ['default', 'news', 'blog', 'social', 'academic', 'ecommerce']
        
        for mapping_name in mappings:
            mapping = get_field_mapping(mapping_name)
            assert isinstance(mapping, FieldMapping)
    
    def test_content_item_from_raw_dict(self):
        """Test ContentItem creation from raw dictionary"""
        mapping = create_custom_mapping(
            title_field='headline',
            content_fields=['body', 'summary'],
            url_field='link'
        )
        
        data = {
            'headline': 'Test Article',
            'body': 'Article body',
            'summary': 'Article summary',
            'link': 'https://example.com/article'
        }
        
        item = ContentItem.from_raw_dict(data, mapping)
        assert item.title == 'Test Article'
        assert item.content_text == 'Article body Article summary'
        assert item.url == 'https://example.com/article'
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        mapping = FieldMapping(ignore_missing_required=False)
        
        # Missing title should raise error
        data = {'content_text': 'Content only'}
        with pytest.raises(ValueError, match="Title field"):
            mapping.map_to_content_item_dict(data)
        
        # Missing content should raise error
        data = {'title': 'Title only'}
        with pytest.raises(ValueError, match="Content field"):
            mapping.map_to_content_item_dict(data)
    
    def test_ignore_missing_fields(self):
        """Test ignoring missing required fields"""
        mapping = FieldMapping(ignore_missing_required=True)
        
        data = {'some_field': 'some_value'}
        result = mapping.map_to_content_item_dict(data)
        
        assert result['title'] == ''
        assert result['content_text'] == ''
        assert result['url'] == ''
    
    def test_list_field_handling(self):
        """Test handling of list fields"""
        mapping = FieldMapping()
        
        data = {
            'title': 'Test Title',
            'content_text': 'Test Content',
            'category': ['tech', 'news'],
            'images': ['img1.jpg', 'img2.jpg']
        }
        
        result = mapping.map_to_content_item_dict(data)
        assert result['category'] == ['tech', 'news']
        assert result['images'] == ['img1.jpg', 'img2.jpg']
        
        # Test string to list conversion
        data['category'] = 'single_category'
        result = mapping.map_to_content_item_dict(data)
        assert result['category'] == ['single_category']
    
    def test_complex_field_mapping(self):
        """Test complex field mapping scenarios"""
        mapping = create_custom_mapping(
            title_field=['article_title', 'post_title', 'name'],
            content_fields=['body', 'description', 'content'],
            content_separator='\n\n',
            default_values={
                'url': 'https://default.com',
                'original_url': '',
                'category': [],
                'publish_time': '',
                'author': 'Unknown Author',
                'images': [],
                'fetch_time': ''
            }
        )
        
        # Test with partial data
        data = {
            'post_title': 'Blog Post',
            'description': 'Post description',
            'content': 'Full content'
        }
        
        result = mapping.map_to_content_item_dict(data)
        assert result['title'] == 'Blog Post'
        assert result['content_text'] == 'Post description\n\nFull content'
        assert result['url'] == 'https://default.com'
        assert result['author'] == 'Unknown Author'
