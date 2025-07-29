"""
Data validation utilities.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional


def validate_input_file(file_path: str) -> bool:
    """
    Validate input JSONL file
    
    Args:
        file_path: Path to input file
        
    Returns:
        True if file is valid
    """
    logger = logging.getLogger(__name__)
    
    try:
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            logger.error(f"File does not exist: {file_path}")
            return False
        
        # Check if file is readable
        if not path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            return False
        
        # Check file extension
        if path.suffix.lower() not in ['.jsonl', '.json']:
            logger.warning(f"Unexpected file extension: {path.suffix}")
        
        # Try to read first few lines
        valid_lines = 0
        total_lines = 0
        
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                total_lines = line_num
                line = line.strip()
                if not line:
                    continue
                
                try:
                    json.loads(line)
                    valid_lines += 1
                except json.JSONDecodeError:
                    if line_num <= 10:  # Log first 10 errors
                        logger.warning(f"Invalid JSON at line {line_num}")
                
                # Check first 100 lines for quick validation
                if line_num >= 100:
                    break
        
        if valid_lines == 0:
            logger.error("No valid JSON lines found")
            return False
        
        validation_ratio = valid_lines / total_lines if total_lines > 0 else 0
        if validation_ratio < 0.5:
            logger.warning(f"Low validation ratio: {validation_ratio:.2%}")
        
        logger.info(f"File validation passed: {valid_lines}/{total_lines} valid lines")
        return True
        
    except Exception as e:
        logger.error(f"File validation failed: {e}")
        return False


def validate_content_item(data: Dict[str, Any]) -> bool:
    """
    Validate content item data structure
    
    Args:
        data: Content item data dictionary
        
    Returns:
        True if data is valid
    """
    required_fields = ['title', 'content_text', 'url']
    optional_fields = [
        'original_url', 'category', 'publish_time', 
        'author', 'images', 'fetch_time', 'language'
    ]
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False
        if not isinstance(data[field], str) or not data[field].strip():
            return False
    
    # Check optional fields types
    if 'category' in data and not isinstance(data['category'], list):
        return False
    
    if 'images' in data and not isinstance(data['images'], list):
        return False
    
    return True


def validate_cluster_data(clusters: List[Dict[str, Any]]) -> bool:
    """
    Validate cluster data structure
    
    Args:
        clusters: List of cluster dictionaries
        
    Returns:
        True if data is valid
    """
    for cluster in clusters:
        required_fields = ['cluster_id', 'representative', 'members']
        
        for field in required_fields:
            if field not in cluster:
                return False
        
        # Validate representative
        if not validate_content_item(cluster['representative']):
            return False
        
        # Validate members
        if not isinstance(cluster['members'], list):
            return False
        
        for member in cluster['members']:
            if not validate_content_item(member):
                return False
    
    return True
