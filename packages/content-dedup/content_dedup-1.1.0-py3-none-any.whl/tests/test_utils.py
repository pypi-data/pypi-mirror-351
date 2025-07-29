"""
Tests for utility functions
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock

from content_dedup.utils.io import JsonLinesReader, JsonWriter, OutputFormatter
from content_dedup.utils.validators import validate_input_file, validate_content_item
from content_dedup.utils.progress import ProgressReporter
import logging



class TestJsonLinesReader:
    """Test JsonLinesReader"""
    
    def test_read_valid_jsonl(self, sample_jsonl_file):
        """Test reading valid JSONL file"""
        reader = JsonLinesReader(sample_jsonl_file)
        
        items = list(reader.read())
        assert len(items) == 4
        assert all(isinstance(item, dict) for item in items)
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_read_invalid_file(self):
        """Test reading non-existent file"""
        reader = JsonLinesReader("non_existent.jsonl")
        
        with pytest.raises(FileNotFoundError):
            list(reader.read())
    
    def test_count_lines(self, sample_jsonl_file):
        """Test counting lines in JSONL file"""
        reader = JsonLinesReader(sample_jsonl_file)
        
        count = reader.count_lines()
        assert count == 4
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_read_with_invalid_json_lines(self):
        """Test reading JSONL with some invalid JSON lines"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
            f.write('{"valid": "json"}\n')
            f.write('invalid json line\n')
            f.write('{"another": "valid", "json": true}\n')
            temp_file = f.name
        
        reader = JsonLinesReader(temp_file)
        items = list(reader.read())
        
        # Should only get valid JSON lines
        assert len(items) == 2
        assert items[0]["valid"] == "json"
        assert items[1]["another"] == "valid"
        
        # Clean up
        Path(temp_file).unlink()


class TestJsonWriter:
    """Test JsonWriter"""
    
    def test_write_json(self, temp_output_dir):
        """Test writing JSON data"""
        test_data = {"test": "data", "numbers": [1, 2, 3]}
        output_path = Path(temp_output_dir) / "test.json"
        
        writer = JsonWriter(str(output_path), pretty=True)
        writer.write(test_data)
        
        assert output_path.exists()
        
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
    
    def test_write_lines(self, temp_output_dir):
        """Test writing JSONL data"""
        test_items = [
            {"id": 1, "text": "first"},
            {"id": 2, "text": "second"}
        ]
        output_path = Path(temp_output_dir) / "test.jsonl"
        
        writer = JsonWriter(str(output_path))
        writer.write_lines(test_items)
        
        assert output_path.exists()
        
        # Read back and verify
        reader = JsonLinesReader(str(output_path))
        loaded_items = list(reader.read())
        
        assert loaded_items == test_items


class TestOutputFormatter:
    """Test OutputFormatter"""
    
    def test_format_json_compact(self):
        """Test compact JSON formatting"""
        data = {"test": "data", "nested": {"key": "value"}}
        
        result = OutputFormatter.format_json(data, pretty=False)
        
        assert isinstance(result, str)
        assert '\n' not in result  # Should be compact
        assert json.loads(result) == data
    
    def test_format_json_pretty(self):
        """Test pretty JSON formatting"""
        data = {"test": "data", "nested": {"key": "value"}}
        
        result = OutputFormatter.format_json(data, pretty=True)
        
        assert isinstance(result, str)
        assert '\n' in result  # Should be formatted
        assert json.loads(result) == data
    
    def test_format_jsonl(self):
        """Test JSONL formatting"""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        
        result = OutputFormatter.format_jsonl(items)
        
        lines = result.strip().split('\n')
        assert len(lines) == 3
        
        for i, line in enumerate(lines):
            assert json.loads(line) == items[i]


class TestValidators:
    """Test validation functions"""
    
    def test_validate_input_file_valid(self, sample_jsonl_file):
        """Test validation of valid input file"""
        assert validate_input_file(sample_jsonl_file) == True
        
        # Clean up
        Path(sample_jsonl_file).unlink()
    
    def test_validate_input_file_invalid(self):
        """Test validation of invalid input file"""
        assert validate_input_file("non_existent.jsonl") == False
    
    def test_validate_input_file_empty(self):
        """Test validation of empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            temp_file = f.name
        
        assert validate_input_file(temp_file) == False
        
        # Clean up
        Path(temp_file).unlink()
    
    def test_validate_content_item_valid(self):
        """Test validation of valid content item"""
        valid_item = {
            "title": "Test Title",
            "content_text": "Test content",
            "url": "https://example.com/test",
            "category": ["test"],
            "author": "Test Author"
        }
        
        assert validate_content_item(valid_item) == True
    
    def test_validate_content_item_missing_required(self):
        """Test validation of content item missing required fields"""
        invalid_item = {
            "title": "Test Title",
            # Missing content_text and url
            "category": ["test"]
        }
        
        assert validate_content_item(invalid_item) == False
    
    def test_validate_content_item_wrong_types(self):
        """Test validation of content item with wrong types"""
        invalid_item = {
            "title": "Test Title",
            "content_text": "Test content",
            "url": "https://example.com/test",
            "category": "should be list not string"  # Wrong type
        }
        
        assert validate_content_item(invalid_item) == False


class TestProgressReporter:
    """Test ProgressReporter"""
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger for testing"""
        return MagicMock()
    
    def test_progress_reporter_enabled(self, mock_logger):
        """Test progress reporter when enabled"""
        reporter = ProgressReporter(mock_logger, enable_progress=True)
        
        reporter.start("Starting test")
        reporter.update("Processing")
        reporter.finish("Test complete")
        
        # Should have made logging calls
        assert mock_logger.info.call_count >= 3
    
    def test_progress_reporter_disabled(self, mock_logger):
        """Test progress reporter when disabled"""
        reporter = ProgressReporter(mock_logger, enable_progress=False)
        
        reporter.start("Starting test")
        reporter.update("Processing")
        reporter.finish("Test complete")
        
        # Should not have made any logging calls
        assert mock_logger.info.call_count == 0
    
    def test_progress_with_steps(self, mock_logger):
        """Test progress reporting with step counts"""
        reporter = ProgressReporter(mock_logger, enable_progress=True)
        
        reporter.start("Starting test")
        reporter.update("Processing item", step=5, total=10)
        reporter.finish("Test complete")
        
        # Should include step information in calls
        calls = mock_logger.info.call_args_list
        step_call = calls[1][0][0]  # Second call, first argument
        assert "5/10" in step_call
        assert "50.0%" in step_call
    
    def test_error_and_warning_logging(self, mock_logger):
        """Test error and warning logging"""
        reporter = ProgressReporter(mock_logger)
        
        reporter.log_error("Test error")
        reporter.log_warning("Test warning")
        
        mock_logger.error.assert_called_once()
        mock_logger.warning.assert_called_once()
        
        # Check emoji prefixes
        error_call = mock_logger.error.call_args[0][0]
        warning_call = mock_logger.warning.call_args[0][0]
        
        assert "❌" in error_call
        assert "⚠️" in warning_call
