#!/usr/bin/env python3
"""
Script to process the raw data files for the FinLex platform
"""
import os
import sys
from backend.transaction_ingest.data_processor import DataProcessor

def main():
    """Main function to process all available data files"""
    print("FinLex Data Processing Script")
    print("=" * 40)
    
    # Initialize data processor
    processor = DataProcessor("finlex_data.db")
    
    # Define data paths
    data_dir = "data/raw"
    results = []
    
    # Process Paysim data if available
    paysim_path = os.path.join(data_dir, "paysim1.csv")
    if os.path.exists(paysim_path):
        print(f"Processing Paysim transaction data from {paysim_path}...")
        result = processor.process_paysim_data(paysim_path, limit=5000)  # Limit for performance
        results.append({"file": "paysim1.csv", "result": result})
        print(f"  Result: {result['message']}")
        if result['success'] and 'statistics' in result:
            stats = result['statistics']
            print(f"  Total transactions: {stats['total_transactions']}")
            print(f"  Fraudulent transactions: {stats['fraudulent_transactions']}")
    
    # Process ObliQA data if available
    obliqa_dir = os.path.join(data_dir, "obliqa")
    obliqa_files = ["ObliQA_dev.json", "ObliQA_test.json", "ObliQA_train.json"]
    
    for filename in obliqa_files:
        filepath = os.path.join(obliqa_dir, filename)
        if os.path.exists(filepath):
            print(f"Processing ObliQA data from {filepath}...")
            result = processor.process_obliqa_data(filepath)
            results.append({"file": filename, "result": result})
            print(f"  Result: {result['message']}")
            if result['success'] and 'statistics' in result:
                stats = result['statistics']
                print(f"  Total questions: {stats['total_questions']}")
                print(f"  Total passages: {stats['total_passages']}")
    
    # Process C3PA data if available
    c3pa_dir = os.path.join(data_dir, "c3pa")
    c3pa_annotations_dir = os.path.join(c3pa_dir, "Annotations", "DB")
    c3pa_crawl_dir = os.path.join(c3pa_dir, "Crawl", "DB")
    
    # Check if directories exist
    if os.path.exists(c3pa_annotations_dir) and os.path.exists(c3pa_crawl_dir):
        # Get the first annotation and crawl files
        annotation_files = [f for f in os.listdir(c3pa_annotations_dir) if f.endswith('.csv')]
        crawl_files = [f for f in os.listdir(c3pa_crawl_dir) if f.endswith('.csv')]
        
        if annotation_files and crawl_files:
            annotation_path = os.path.join(c3pa_annotations_dir, annotation_files[0])
            crawl_path = os.path.join(c3pa_crawl_dir, crawl_files[0])
            
            print(f"Processing C3PA data...")
            print(f"  Annotations: {annotation_path}")
            print(f"  Crawl data: {crawl_path}")
            
            result = processor.process_c3pa_data(annotation_path, crawl_path)
            results.append({"file": "c3pa_data", "result": result})
            print(f"  Result: {result['message']}")
            if result['success'] and 'statistics' in result:
                stats = result['statistics']
                print(f"  Total annotations: {stats.get('total_annotations', 'N/A')}")
                print(f"  Total crawled policies: {stats.get('total_crawled_policies', 'N/A')}")
    
    # Print summary
    print("\n" + "=" * 40)
    print("Processing Summary:")
    successful = sum(1 for r in results if r['result']['success'])
    total = len(results)
    print(f"Successfully processed: {successful}/{total} files")
    
    if successful > 0:
        print("\nTransaction Statistics:")
        stats = processor.get_transaction_stats()
        if 'error' not in stats:
            print(f"  Total transactions: {stats['total_transactions']}")
            print(f"  Fraudulent transactions: {stats['fraudulent_transactions']}")
            print(f"  Transaction types: {stats['transaction_types']}")
        else:
            print(f"  Error getting stats: {stats['error']}")
    
    print("\nData processing complete!")

if __name__ == "__main__":
    main()