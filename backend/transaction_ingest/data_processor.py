"""
Data processing utilities for the FinLex platform
"""
import pandas as pd
import json
import csv
import os
from typing import Dict, List, Any, Optional
import sqlite3
import uuid
from datetime import datetime
import numpy as np

class DataProcessor:
    """Processor for different types of compliance data"""
    
    def __init__(self, db_path: str = "transactions.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create transactions table with the correct schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                amount REAL,
                date TEXT,
                type TEXT,
                description TEXT,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to native Python types"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        return obj
    
    def process_paysim_data(self, file_path: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Process Paysim1 transaction data
        
        Args:
            file_path: Path to the Paysim1.csv file
            limit: Maximum number of rows to process (for testing)
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Read the CSV file
            if limit is not None:
                df = pd.read_csv(file_path, nrows=limit)
            else:
                df = pd.read_csv(file_path)
            
            # Convert to the expected schema
            transactions = []
            for _, row in df.iterrows():
                transaction = {
                    'id': str(uuid.uuid4()),
                    'user_id': 'paysim_user',
                    'amount': float(row['amount']),
                    'date': datetime.now().isoformat(),  # In a real implementation, we'd use actual dates
                    'type': str(row['type']),
                    'description': f"{row['type']} transaction from {row['nameOrig']} to {row['nameDest']}",
                    'metadata': json.dumps({
                        'step': int(row['step']),
                        'nameOrig': str(row['nameOrig']),
                        'oldbalanceOrg': float(row['oldbalanceOrg']),
                        'newbalanceOrig': float(row['newbalanceOrig']),
                        'nameDest': str(row['nameDest']),
                        'oldbalanceDest': float(row['oldbalanceDest']),
                        'newbalanceDest': float(row['newbalanceDest']),
                        'isFraud': int(row['isFraud']),
                        'isFlaggedFraud': int(row['isFlaggedFraud'])
                    })
                }
                transactions.append(transaction)
            
            # Store in database with the correct schema
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert transactions one by one to match the schema
            for transaction in transactions:
                cursor.execute('''
                    INSERT OR REPLACE INTO transactions 
                    (id, user_id, amount, date, type, description, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction['id'],
                    transaction['user_id'],
                    transaction['amount'],
                    transaction['date'],
                    transaction['type'],
                    transaction['description'],
                    transaction['metadata']
                ))
            
            conn.commit()
            conn.close()
            
            # Generate statistics and convert numpy types
            stats = {
                'total_transactions': len(transactions),
                'fraudulent_transactions': int(df['isFraud'].sum()),
                'flagged_fraud_transactions': int(df['isFlaggedFraud'].sum()),
                'transaction_types': {k: int(v) for k, v in df['type'].value_counts().to_dict().items()},
                'total_amount': float(df['amount'].sum())
            }
            
            return {
                'success': True,
                'message': f'Successfully processed {len(transactions)} transactions',
                'statistics': self._convert_numpy_types(stats)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing Paysim data: {str(e)}'
            }
    
    def process_obliqa_data(self, file_path: str) -> Dict[str, Any]:
        """
        Process ObliQA regulatory question-answer data
        
        Args:
            file_path: Path to the ObliQA JSON file
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract questions and passages
            questions = []
            passages = []
            
            for item in data:
                questions.append({
                    'id': item.get('QuestionID'),
                    'question': item.get('Question'),
                    'passages': item.get('Passages', [])
                })
                
                # Collect all unique passages
                for passage in item.get('Passages', []):
                    if passage not in passages:
                        passages.append(passage)
            
            return {
                'success': True,
                'message': f'Successfully processed {len(questions)} questions',
                'statistics': {
                    'total_questions': len(questions),
                    'total_passages': len(passages)
                },
                'data': {
                    'questions': questions,
                    'passages': passages
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing ObliQA data: {str(e)}'
            }
    
    def process_c3pa_data(self, annotations_path: str, crawl_path: str) -> Dict[str, Any]:
        """
        Process C3PA privacy policy data
        
        Args:
            annotations_path: Path to the C3PA annotations CSV file
            crawl_path: Path to the C3PA crawl CSV file
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Process annotations
            annotations_df = pd.read_csv(annotations_path)
            
            # Process crawl data
            crawl_df = pd.read_csv(crawl_path)
            
            # Generate statistics and convert numpy types
            stats = {
                'total_annotations': len(annotations_df),
                'total_crawled_policies': len(crawl_df),
                'annotation_labels': {k: int(v) for k, v in annotations_df['Label'].value_counts().to_dict().items()} if 'Label' in annotations_df.columns else {}
            }
            
            return {
                'success': True,
                'message': f'Successfully processed C3PA data',
                'statistics': self._convert_numpy_types(stats)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing C3PA data: {str(e)}'
            }
    
    def get_transaction_stats(self) -> Dict[str, Any]:
        """Get statistics about processed transactions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM transactions")
            total_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_transactions': total_count,
                'fraudulent_transactions': 0,  # We don't have fraud data in this schema
                'transaction_types': {}  # We'll populate this if needed
            }
            
        except Exception as e:
            return {
                'error': f'Error getting transaction stats: {str(e)}'
            }

def main():
    """Main function to demonstrate data processing"""
    # Initialize processor
    processor = DataProcessor()
    
    # Process sample data if available
    data_dir = "data/raw"
    
    # Check if Paysim data exists
    paysim_path = os.path.join(data_dir, "paysim1.csv")
    if os.path.exists(paysim_path):
        print("Processing Paysim transaction data...")
        result = processor.process_paysim_data(paysim_path, limit=1000)  # Process only first 1000 rows for demo
        print(f"Result: {result['message']}")
        if result['success']:
            print(f"Statistics: {result['statistics']}")
    
    # Check if ObliQA data exists
    obliqa_dev_path = os.path.join(data_dir, "obliqa", "ObliQA_dev.json")
    if os.path.exists(obliqa_dev_path):
        print("\nProcessing ObliQA regulatory data...")
        result = processor.process_obliqa_data(obliqa_dev_path)
        print(f"Result: {result['message']}")
        if result['success']:
            print(f"Statistics: {result['statistics']}")
    
    print("\nCurrent transaction statistics:")
    stats = processor.get_transaction_stats()
    print(stats)

if __name__ == "__main__":
    main()