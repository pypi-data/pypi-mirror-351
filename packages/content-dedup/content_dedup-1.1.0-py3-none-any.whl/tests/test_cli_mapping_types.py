"""
Test CLI support for different field mapping types
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from content_dedup.cli import main, create_parser


class TestCLIMappingTypes:
    """Test CLI functionality for different mapping types"""
    
    @pytest.fixture
    def sample_data_file(self):
        """Create a temporary JSONL file with sample data"""
        sample_data = [
            {
                "headline": "AI breakthrough in 2025",
                "body": "Artificial intelligence reaches new milestone",
                "summary": "Major AI advancement announced",
                "permalink": "https://example.com/ai-news",
                "writer": "John Doe",
                "published_at": "2025-01-15",
                "tags": ["AI", "Technology"]
            },
            {
                "headline": "Climate change update",
                "body": "New climate data shows concerning trends",
                "summary": "Climate report released",
                "permalink": "https://example.com/climate",
                "writer": "Jane Smith",
                "published_at": "2025-01-16",
                "tags": ["Climate", "Environment"]
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in sample_data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
            return f.name
    
    def test_parser_minimal_flag(self):
        """Test that --minimal flag is properly parsed"""
        parser = create_parser()
        
        # Test without minimal flag
        args = parser.parse_args(['test.jsonl'])
        assert not args.minimal
        
        # Test with minimal flag
        args = parser.parse_args(['test.jsonl', '--minimal'])
        assert args.minimal
    
    def test_parser_new_field_mapping_help(self):
        """Test that field mapping help includes new options"""
        parser = create_parser()
        
        # Get the field-mapping argument
        for action in parser._actions:
            if action.dest == 'field_mapping':
                help_text = action.help
                assert 'balanced-' in help_text
                assert 'minimal-' in help_text
                break
        else:
            pytest.fail("field_mapping argument not found")
    
    @patch('content_dedup.cli.ContentDeduplicator')
    def test_minimal_flag_with_custom_fields(self, mock_deduplicator_class, sample_data_file):
        """Test --minimal flag with custom field specification"""
        # Mock the deduplicator
        mock_deduplicator = mock_deduplicator_class.return_value
        mock_deduplicator.content_items = []
        mock_deduplicator.cluster_and_deduplicate.return_value = []
        mock_deduplicator.generate_report.return_value = {}
        
        # Test CLI arguments
        test_args = [
            sample_data_file,
            '--title-field', 'headline',
            '--content-fields', 'body,summary',
            '--id-field', 'permalink',
            '--minimal',
            '--output', '/dev/null'
        ]
        
        with patch('sys.argv', ['content-dedup'] + test_args):
            try:
                main()
            except SystemExit:
                pass  # Expected for successful completion
        
        # Verify ContentDeduplicator was called
        assert mock_deduplicator_class.called
        
        # Check that field_mapping parameter was passed
        call_args = mock_deduplicator_class.call_args
        assert 'field_mapping' in call_args.kwargs
        
        # The field mapping should be a MinimalFieldMapping instance
        field_mapping = call_args.kwargs['field_mapping']
        assert hasattr(field_mapping, 'title_field')
        assert hasattr(field_mapping, 'content_fields')
        assert hasattr(field_mapping, 'id_field')  # Changed from url_field
        
        # Should not have extra fields (for minimal mapping)
        assert not hasattr(field_mapping, 'category_field') or field_mapping.category_field is None
    
    @patch('content_dedup.cli.ContentDeduplicator')
    def test_predefined_mapping_with_minimal_prefix(self, mock_deduplicator_class, sample_data_file):
        """Test predefined mapping with minimal- prefix"""
        mock_deduplicator = mock_deduplicator_class.return_value
        mock_deduplicator.content_items = []
        mock_deduplicator.cluster_and_deduplicate.return_value = []
        
        test_args = [
            sample_data_file,
            '--field-mapping', 'minimal-news',
            '--output', '/dev/null'
        ]
        
        with patch('sys.argv', ['content-dedup'] + test_args):
            try:
                main()
            except SystemExit:
                pass
        
        # Verify the mapping was passed correctly
        call_args = mock_deduplicator_class.call_args
        field_mapping = call_args.kwargs['field_mapping']
        assert field_mapping == 'minimal-news'
    
    @patch('content_dedup.cli.ContentDeduplicator')
    def test_minimal_flag_converts_predefined_mapping(self, mock_deduplicator_class, sample_data_file):
        """Test that --minimal flag converts predefined mapping"""
        mock_deduplicator = mock_deduplicator_class.return_value
        mock_deduplicator.content_items = []
        mock_deduplicator.cluster_and_deduplicate.return_value = []
        
        test_args = [
            sample_data_file,
            '--field-mapping', 'news',
            '--minimal',
            '--output', '/dev/null'
        ]
        
        with patch('sys.argv', ['content-dedup'] + test_args):
            try:
                main()
            except SystemExit:
                pass
        
        # Verify the mapping was converted to minimal-news
        call_args = mock_deduplicator_class.call_args
        field_mapping = call_args.kwargs['field_mapping']
        assert field_mapping == 'minimal-news'

    @patch('content_dedup.cli.ContentDeduplicator')
    def test_balanced_mapping_with_category_field(self, mock_deduplicator_class, sample_data_file):
        """Test that category field creates balanced mapping"""
        mock_deduplicator = mock_deduplicator_class.return_value
        mock_deduplicator.content_items = []
        mock_deduplicator.cluster_and_deduplicate.return_value = []

        test_args = [
            sample_data_file,
            '--title-field', 'headline',
            '--content-fields', 'body',
            '--category-field', 'tags',
            '--output', '/dev/null'
        ]

        with patch('sys.argv', ['content-dedup'] + test_args):
            try:
                main()
            except SystemExit:
                pass

        # Should create balanced mapping when category field is specified
        call_args = mock_deduplicator_class.call_args
        field_mapping = call_args.kwargs['field_mapping']
        assert hasattr(field_mapping, 'category_field')
        assert field_mapping.category_field == 'tags'
    
    def test_cli_examples_in_help(self):
        """Test that CLI help contains updated examples"""
        parser = create_parser()
        help_text = parser.format_help()
        
        # Check for new examples
        assert 'balanced-news' in help_text
        assert 'minimal-news' in help_text
        assert '--minimal' in help_text
    
    def cleanup_temp_file(self, filepath):
        """Clean up temporary file"""
        try:
            os.unlink(filepath)
        except (OSError, FileNotFoundError):
            pass


class TestCLIMigrationFeatures:
    """Test CLI migration and compatibility features"""
    
    def test_backward_compatibility(self):
        """Test that old CLI usage still works"""
        parser = create_parser()
        
        # Old style arguments should still work
        old_style_args = [
            'test.jsonl',
            '--field-mapping', 'news',
            '--title-field', 'title',
            '--content-fields', 'content'
        ]
        
        args = parser.parse_args(old_style_args)
        assert args.field_mapping == 'news'
        assert args.title_field == 'title'
        assert args.content_fields == 'content'
    
    def test_new_style_arguments(self):
        """Test new style CLI arguments"""
        parser = create_parser()
        
        # New style with balanced prefix
        new_style_args = [
            'test.jsonl',
            '--field-mapping', 'balanced-news',
            '--output', 'results.json'
        ]
        
        args = parser.parse_args(new_style_args)
        assert args.field_mapping == 'balanced-news'
        assert args.output == 'results.json'
        
        # New style with minimal flag
        minimal_args = [
            'test.jsonl',
            '--title-field', 'headline',
            '--content-fields', 'body',
            '--minimal'
        ]
        
        args = parser.parse_args(minimal_args)
        assert args.minimal
        assert args.title_field == 'headline'
        assert args.content_fields == 'body'
