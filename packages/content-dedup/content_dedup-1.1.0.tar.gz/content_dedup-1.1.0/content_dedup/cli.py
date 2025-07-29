#!/usr/bin/env python3
"""
Content Deduplication CLI Tool with stdin support
"""

import os
import argparse
import sys
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from .core.deduplicator import ContentDeduplicator
from .utils.progress import ProgressReporter
from .utils.io import JsonLinesReader, JsonWriter, OutputFormatter
from .utils.validators import validate_input_file, validate_content_item
from .config.field_mapping import FieldMapping, get_field_mapping, create_custom_mapping
from .config.field_mapping_balanced import create_balanced_mapping
from .config.field_mapping_minimal import create_minimal_custom_mapping


def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler (for progress and debug info)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
    else:
        # Default to stderr for logging (not stdout to avoid pipeline interference)
        file_handler = logging.StreamHandler(sys.stderr)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
    
    # Configure root logger
    logger = logging.getLogger('content_dedup')
    logger.setLevel(level)
    logger.addHandler(file_handler)
    
    return logger


def handle_stdin_input(logger: logging.Logger) -> str:
    """
    Handle stdin input by creating a temporary file
    
    Args:
        logger: Logger instance
        
    Returns:
        Path to temporary file containing stdin data
    """
    logger.info("Reading data from stdin...")
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.jsonl', prefix='content_dedup_stdin_')
    
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_file:
            line_count = 0
            for line in sys.stdin:
                line = line.strip()
                if line:
                    # Validate JSON line
                    try:
                        json.loads(line)
                        temp_file.write(line + '\n')
                        line_count += 1
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping invalid JSON line: {line[:50]}...")
                        continue
        
        logger.info(f"Read {line_count} lines from stdin")
        
        if line_count == 0:
            os.unlink(temp_path)
            raise ValueError("No valid JSON lines found in stdin")
        
        return temp_path
        
    except Exception as e:
        # Clean up on error
        try:
            os.unlink(temp_path)
        except:
            pass
        raise e


def cleanup_temp_file(file_path: str, logger: logging.Logger):
    """
    Clean up temporary file
    
    Args:
        file_path: Path to temporary file
        logger: Logger instance
    """
    try:
        if file_path and Path(file_path).exists():
            os.unlink(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up temporary file {file_path}: {e}")


def is_stdin_input(input_path: str) -> bool:
    """
    Check if input should be read from stdin
    
    Args:
        input_path: Input path argument
        
    Returns:
        True if should read from stdin
    """
    return input_path in ['-', '/dev/stdin', 'stdin']


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Intelligent content deduplication and clustering toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with auto language detection
  content-dedup input.jsonl --output results.json

  # Use recommended balanced mapping for news
  content-dedup input.jsonl --field-mapping balanced-news --output results.json

  # High performance minimal mapping
  content-dedup input.jsonl --field-mapping minimal-news --output results.json
  content-dedup input.jsonl --title-field headline --content-fields body --minimal

  # Read from stdin (pipeline usage)
  cat input.jsonl | content-dedup - --format representatives
  cat input.jsonl | content-dedup /dev/stdin --output clusters.json

  # Specify language and similarity threshold
  content-dedup input.jsonl --language zh --similarity 0.85 --output clusters.json

  # Custom field mapping (simplified)
  content-dedup input.jsonl --title-field headline --content-fields body,summary \\
    --id-field permalink --output results.json

  # Pipeline usage (output to stdout)
  content-dedup input.jsonl --format representatives | jq '.[] | .title'
  cat input.jsonl | content-dedup - --format representatives | jq '.[] | .title'

  # Save both clusters and representatives
  content-dedup input.jsonl --output clusters.json --representatives reps.jsonl

  # Verbose mode with progress logging
  content-dedup input.jsonl --output results.json --verbose --log-file progress.log
        """
    )
    
    # Input/Output arguments
    parser.add_argument(
        'input',
        type=str,
        help='Input JSONL file containing content items (use "-" or "/dev/stdin" for stdin)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (JSON format). If not specified, outputs to stdout'
    )
    
    parser.add_argument(
        '-r', '--representatives',
        type=str,
        help='Output file for representative items only (JSONL format)'
    )
    
    # Processing arguments
    parser.add_argument(
        '-l', '--language',
        type=str,
        choices=['auto', 'zh', 'en', 'mixed'],
        default='auto',
        help='Language mode (default: auto)'
    )
    
    parser.add_argument(
        '-s', '--similarity',
        type=float,
        default=0.8,
        help='Similarity threshold for clustering (default: 0.8)'
    )
    
    parser.add_argument(
        '-t', '--mixed-threshold',
        type=float,
        default=0.3,
        help='Mixed language detection threshold (default: 0.3)'
    )
    
    # Field mapping arguments
    parser.add_argument(
        '--field-mapping',
        type=str,
        default='default',
        help='Field mapping preset (default, news, blog, social, academic, ecommerce) '
             'with optional prefixes: balanced-* (recommended), minimal-* (performance), '
             'or full mapping (default: default)'
    )
    
    parser.add_argument(
        '--title-field',
        type=str,
        help='Custom title field name(s), comma-separated for multiple fields'
    )
    
    parser.add_argument(
        '--content-fields',
        type=str,
        help='Custom content field name(s), comma-separated for multiple fields'
    )
    
    parser.add_argument(
        '--id-field',
        type=str,
        help='Custom ID field name(s) for unique identification and deduplication'
    )
    
    parser.add_argument(
        '--category-field',
        type=str,
        help='Custom category field name'
    )
    
    parser.add_argument(
        '--content-separator',
        type=str,
        default=' ',
        help='Separator for joining multiple content fields (default: space)'
    )
    
    parser.add_argument(
        '--ignore-missing',
        action='store_true',
        help='Ignore missing required fields (title/content) instead of failing'
    )
    
    parser.add_argument(
        '--minimal',
        action='store_true',
        help='Use minimal field mapping (3 core fields only) for maximum performance'
    )
    
    # Output format arguments
    parser.add_argument(
        '--format',
        type=str,
        choices=['clusters', 'representatives', 'report'],
        default='clusters',
        help='Output format (default: clusters)'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )
    
    # Logging and debugging arguments
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file path (default: stderr)'
    )
    
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress reporting'
    )
    
    # Validation arguments
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate input file without processing'
    )
    
    # Stdin specific arguments
    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='Keep temporary file when reading from stdin (for debugging)'
    )
    
    return parser


def output_json(data: Any, output_path: Optional[str] = None, pretty: bool = False):
    """Output JSON data to file or stdout"""
    json_str = OutputFormatter.format_json(data, pretty=pretty)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_str)
    else:
        # Output to stdout for pipeline usage
        print(json_str)


def output_jsonl(items: list, output_path: str):
    """Output items as JSONL format"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in items:
            item_dict = item.to_dict() if hasattr(item, 'to_dict') else item
            json.dump(item_dict, f, ensure_ascii=False)
            f.write('\n')


def main():
    """Main CLI entry point"""
    import os  # Import here to avoid issues
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose, args.log_file)
    
    temp_file_path = None
    
    try:
        # Handle stdin input
        if is_stdin_input(args.input):
            if sys.stdin.isatty():
                logger.error("No data provided via stdin. Use a file path or pipe data to stdin.")
                sys.exit(1)
            
            temp_file_path = handle_stdin_input(logger)
            input_file = temp_file_path
            logger.info(f"Created temporary file: {temp_file_path}")
        else:
            input_file = args.input
            
            # Validate input file for regular files
            if not validate_input_file(input_file):
                logger.error(f"Invalid input file: {input_file}")
                sys.exit(1)
        
        if args.validate_only:
            logger.info("Input validation passed")
            return
        
        # Initialize progress reporter
        progress = ProgressReporter(logger, enable_progress=not args.no_progress)
        progress.start("Initializing content deduplicator...")
        
        # Setup field mapping
        field_mapping = None
        if any([args.title_field, args.content_fields, args.id_field, 
                args.category_field]):
            # Create custom field mapping from CLI arguments
            mapping_kwargs = {
                'content_separator': args.content_separator,
                'ignore_missing_required': args.ignore_missing
            }
            
            if args.title_field:
                titles = [f.strip() for f in args.title_field.split(',')]
                mapping_kwargs['title_field'] = titles if len(titles) > 1 else titles[0]
            
            if args.content_fields:
                contents = [f.strip() for f in args.content_fields.split(',')]
                mapping_kwargs['content_fields'] = contents if len(contents) > 1 else contents[0]
            
            if args.id_field:
                ids = [f.strip() for f in args.id_field.split(',')]
                mapping_kwargs['id_field'] = ids if len(ids) > 1 else ids[0]
                
            if args.category_field:
                mapping_kwargs['category_field'] = args.category_field
            
            # Choose mapping type based on --minimal flag
            if args.minimal:
                # Use minimal mapping (3 core fields only)
                minimal_kwargs = {k: v for k, v in mapping_kwargs.items() 
                                if k in ['title_field', 'content_fields', 'id_field', 
                                        'content_separator', 'ignore_missing_required']}
                field_mapping = create_minimal_custom_mapping(**minimal_kwargs)
                logger.info(f"Using custom minimal field mapping: title={minimal_kwargs.get('title_field', 'title')}, "
                           f"content={minimal_kwargs.get('content_fields', 'content_text')}")
            elif args.category_field or not args.minimal:
                # Use balanced mapping if category specified or default
                balanced_kwargs = {k: v for k, v in mapping_kwargs.items() 
                                 if k in ['title_field', 'content_fields', 'id_field', 'category_field', 
                                         'publish_time_field', 'content_separator', 'ignore_missing_required']}
                field_mapping = create_balanced_mapping(**balanced_kwargs)
                logger.info(f"Using custom balanced field mapping: title={balanced_kwargs.get('title_field', 'title')}, "
                           f"content={balanced_kwargs.get('content_fields', 'content_text')}")
            else:
                # Use full mapping for complex scenarios
                field_mapping = create_custom_mapping(**mapping_kwargs)
                logger.info(f"Using custom full field mapping: title={mapping_kwargs.get('title_field', 'title')}, "
                           f"content={mapping_kwargs.get('content_fields', 'content_text')}")
        else:
            # Use predefined mapping (supports prefixes like 'minimal-', 'balanced-')
            if args.minimal and not args.field_mapping.startswith(('minimal-', 'balanced-')):
                field_mapping = f"minimal-{args.field_mapping}"
            else:
                field_mapping = args.field_mapping
            logger.info(f"Using predefined field mapping: {field_mapping}")
        
        # Initialize deduplicator
        deduplicator = ContentDeduplicator(
            language=args.language,
            similarity_threshold=args.similarity,
            mixed_language_threshold=args.mixed_threshold,
            field_mapping=field_mapping
        )
        
        progress.update("Loading input data...")
        
        # Load input data
        deduplicator.load_jsonl(input_file)
        
        progress.update("Processing clusters...")
        
        # Process clustering
        clusters = deduplicator.cluster_and_deduplicate()
        
        progress.update("Generating output...")
        
        # Generate output based on format
        if args.format == 'clusters':
            output_data = {
                'metadata': {
                    'total_clusters': len(clusters),
                    'original_count': len(deduplicator.content_items),
                    'language_settings': args.language,
                    'similarity_threshold': args.similarity,
                    'compression_ratio': len(clusters) / len(deduplicator.content_items) if deduplicator.content_items else 0
                },
                'clusters': [cluster.to_dict() for cluster in clusters]
            }
            output_json(output_data, args.output, args.pretty)
            
        elif args.format == 'representatives':
            representatives = [cluster.representative.to_dict() for cluster in clusters]
            output_json(representatives, args.output, args.pretty)
            
        elif args.format == 'report':
            report = deduplicator.generate_report()
            output_json(report, args.output, args.pretty)
        
        # Output representatives to separate file if specified
        if args.representatives:
            representatives = [cluster.representative for cluster in clusters]
            output_jsonl(representatives, args.representatives)
            logger.info(f"Representatives saved to: {args.representatives}")
        
        progress.finish(f"Processing complete. Generated {len(clusters)} clusters from {len(deduplicator.content_items)} items.")
        
        # Log summary to stderr
        logger.info(f"Successfully processed {len(deduplicator.content_items)} items into {len(clusters)} clusters")
        
    except KeyboardInterrupt:
        logger.error("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if args.verbose:
            import traceback
            logger.debug(traceback.format_exc())
        sys.exit(1)
    finally:
        # Clean up temporary file unless --keep-temp is specified
        if temp_file_path and not args.keep_temp:
            cleanup_temp_file(temp_file_path, logger)


if __name__ == '__main__':
    main()
