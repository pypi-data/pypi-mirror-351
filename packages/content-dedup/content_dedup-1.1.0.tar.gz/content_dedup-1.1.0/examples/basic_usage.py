"""
Basic usage example for py-content-dedup
"""

from content_dedup import ContentDeduplicator

def main():
    # Initialize deduplicator with auto language detection
    deduplicator = ContentDeduplicator(
        language='auto',
        similarity_threshold=0.8
    )
    
    # Load data
    deduplicator.load_jsonl('sample_data/news_sample.jsonl')
    
    # Perform clustering
    clusters = deduplicator.cluster_and_deduplicate()
    
    # Save results
    deduplicator.save_results('output/clusters.json', format='clusters')
    deduplicator.save_results('output/representatives.jsonl', format='representatives')
    
    # Generate report
    report = deduplicator.generate_report()
    print(f"Processed {report['basic_statistics']['original_content_count']} items")
    print(f"Generated {report['basic_statistics']['cluster_count']} clusters")
    print(f"Compression ratio: {report['basic_statistics']['compression_ratio']}")

if __name__ == '__main__':
    main()
