"""
Input/Output utilities.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Iterator, Optional


class JsonLinesReader:
    """JSONL file reader with error handling"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.logger = logging.getLogger(__name__)
    
    def read(self) -> Iterator[Dict[str, Any]]:
        """
        Read JSONL file line by line
        
        Yields:
            Dictionary for each valid JSON line
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Skipping invalid JSON at line {line_num}: {e}")
                    continue
    
    def count_lines(self) -> int:
        """Count total number of valid JSON lines"""
        count = 0
        for _ in self.read():
            count += 1
        return count


class JsonWriter:
    """JSON file writer with formatting options"""
    
    def __init__(self, file_path: str, pretty: bool = False):
        self.file_path = Path(file_path)
        self.pretty = pretty
        self.logger = logging.getLogger(__name__)
    
    def write(self, data: Any) -> None:
        """
        Write data as JSON
        
        Args:
            data: Data to write
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                if self.pretty:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        except Exception as e:
            self.logger.error(f"Failed to write JSON to {self.file_path}: {e}")
            raise
    
    def write_lines(self, items: List[Any]) -> None:
        """
        Write items as JSONL
        
        Args:
            items: List of items to write
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                for item in items:
                    json.dump(item, f, ensure_ascii=False)
                    f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write JSONL to {self.file_path}: {e}")
            raise


class OutputFormatter:
    """Format output for different purposes"""
    
    @staticmethod
    def format_json(data: Any, pretty: bool = False) -> str:
        """Format data as JSON string"""
        if pretty:
            return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    
    @staticmethod
    def format_jsonl(items: List[Any]) -> str:
        """Format items as JSONL string"""
        lines = []
        for item in items:
            lines.append(json.dumps(item, ensure_ascii=False))
        return '\n'.join(lines)
