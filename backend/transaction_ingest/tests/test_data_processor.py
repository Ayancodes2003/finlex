"""
Tests for the data processor utilities
"""
import pytest
import pandas as pd
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from ..data_processor import DataProcessor

def test_init_db():
    """Test database initialization"""
    # Create processor with temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        tmp_db_path = tmp_file.name
    
    try:
        processor = DataProcessor(tmp_db_path)
        
        # Check that database file was created
        assert os.path.exists(tmp_db_path)
        
        # Check that transactions table exists
        import sqlite3
        conn = sqlite3.connect(tmp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'transactions'
        
    finally:
        # Clean up
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)

def test_process_paysim_data():
    """Test processing of Paysim data"""
    # Create sample CSV data
    csv_content = """step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud
1,PAYMENT,9839.64,C1231006815,170136.0,160296.36,M1979787155,0.0,0.0,0,0
1,PAYMENT,1864.28,C1666544295,21249.0,19384.72,M2044282225,0.0,0.0,0,0
1,TRANSFER,181.0,C1305486145,181.0,0.0,C553264065,0.0,0.0,1,0
1,CASH_OUT,181.0,C840083671,181.0,0.0,C38997010,21182.0,0.0,1,0"""

    # Create processor with temporary database
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as tmp_csv:
        tmp_csv.write(csv_content)
        tmp_csv_path = tmp_csv.name
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        tmp_db_path = tmp_db.name
    
    try:
        processor = DataProcessor(tmp_db_path)
        result = processor.process_paysim_data(tmp_csv_path)
        
        assert result['success'] == True
        assert 'Successfully processed 4 transactions' in result['message']
        assert result['statistics']['total_transactions'] == 4
        assert result['statistics']['fraudulent_transactions'] == 2
        
    finally:
        # Clean up
        for path in [tmp_csv_path, tmp_db_path]:
            if os.path.exists(path):
                os.unlink(path)

def test_process_obliqa_data():
    """Test processing of ObliQA data"""
    # Create sample JSON data
    json_content = [
        {
            "QuestionID": "test-123",
            "Question": "Test question?",
            "Passages": ["Test passage 1", "Test passage 2"]
        },
        {
            "QuestionID": "test-456",
            "Question": "Another test question?",
            "Passages": ["Test passage 3"]
        }
    ]

    # Create processor
    processor = DataProcessor()
    
    # Mock the file reading
    with patch('builtins.open', mock_open(read_data=json.dumps(json_content))):
        result = processor.process_obliqa_data('fake_path.json')
        
        assert result['success'] == True
        assert 'Successfully processed 2 questions' in result['message']
        assert result['statistics']['total_questions'] == 2
        assert result['statistics']['total_passages'] == 3

def test_get_transaction_stats():
    """Test getting transaction statistics"""
    # Create processor with temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        tmp_db_path = tmp_db.name
    
    try:
        processor = DataProcessor(tmp_db_path)
        
        # Initially should be empty
        stats = processor.get_transaction_stats()
        assert stats['total_transactions'] == 0
        assert stats['fraudulent_transactions'] == 0
        
    finally:
        # Clean up
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)

if __name__ == "__main__":
    pytest.main([__file__])