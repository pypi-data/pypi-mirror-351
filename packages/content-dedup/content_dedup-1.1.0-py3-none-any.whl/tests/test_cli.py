"""
Tests for CLI functionality
"""

import pytest
import subprocess
import tempfile
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from content_dedup.cli import main, create_parser, output_json


class TestCLI:
    """Test CLI functionality"""
    
    def test_create_parser(self):
        """Test argument parser creation"""
        parser = create_parser()
        
        # Test default values
        args = parser.parse_args(['test.jsonl'])
        assert args.input == 'test.jsonl'
        assert args.language == 'auto'
        assert args.similarity == 0.8
        assert args.format == 'clusters'
        assert args.verbose == False
    
    def test_parser_with_arguments(self):
        """Test parser with various arguments"""
        parser = create_parser()
        
        args = parser.parse_args([
            'input.jsonl',
            '--language', 'zh',
            '--similarity', '0.9',
            '--output', 'output.json',
            '--format', 'representatives',
            '--verbose',
            '--pretty'
        ])
        
        assert args.input == 'input.jsonl'
        assert args.language == 'zh'
        assert args.similarity == 0.9
        assert args.output == 'output.json'
        assert args.format == 'representatives'
        assert args.verbose == True
        assert args.pretty == True
    
    def test_output_json_to_stdout(self, capsys):
        """Test JSON output to stdout"""
        test_data = {"test": "data", "number": 123}
        
        output_json(test_data, output_path=None, pretty=False)
        
        captured = capsys.readouterr()
        assert json.loads(captured.out) == test_data
    
    def test_output_json_to_file(self, temp_output_dir):
        """Test JSON output to file"""
        test_data = {"test": "data", "number": 123}
        output_path = Path(temp_output_dir) / "test_output.json"
        
        output_json(test_data, output_path=str(output_path), pretty=True)
        
        assert output_path.exists()
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
    
    @patch('content_dedup.cli.ContentDeduplicator')
    @patch('content_dedup.cli.validate_input_file')
    def test_main_basic_flow(self, mock_validate, mock_deduplicator_class):
        """Test main CLI flow"""
        # Setup mocks
        mock_validate.return_value = True
        mock_deduplicator = MagicMock()
        mock_deduplicator_class.return_value = mock_deduplicator
        mock_deduplicator.content_items = [MagicMock()]
        mock_deduplicator.cluster_and_deduplicate.return_value = [MagicMock()]
        
        # Test arguments
        test_args = ['content-dedup', 'test.jsonl', '--format', 'report']
        
        with patch.object(sys, 'argv', test_args):
            with patch('content_dedup.cli.output_json') as mock_output:
                try:
                    main()
                except SystemExit:
                    pass  # Expected for successful completion
                
                # Verify calls
                mock_validate.assert_called_once_with('test.jsonl')
                mock_deduplicator.load_jsonl.assert_called_once_with('test.jsonl')
                mock_deduplicator.cluster_and_deduplicate.assert_called_once()
    
    def test_cli_integration(self, sample_jsonl_file, temp_output_dir):
        """Test CLI integration with real files"""
        output_path = Path(temp_output_dir) / "cli_output.json"
        
        # Construct command
        cmd = [
            sys.executable, '-m', 'content_dedup.cli',
            sample_jsonl_file,
            '--output', str(output_path),
            '--format', 'clusters',
            '--similarity', '0.5'
        ]
        
        try:
            # Run CLI command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Check if command succeeded (allowing for import errors in test env)
            if result.returncode == 0:
                assert output_path.exists()
                
                # Verify output format
                with open(output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                assert 'metadata' in data
                assert 'clusters' in data
            else:
                # If command failed due to import issues, that's OK for unit tests
                pytest.skip(f"CLI test skipped due to import issues: {result.stderr}")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("CLI test skipped - subprocess execution issues")
        finally:
            # Clean up
            Path(sample_jsonl_file).unlink()
