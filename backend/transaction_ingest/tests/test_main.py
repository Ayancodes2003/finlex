import pytest
from fastapi.testclient import TestClient
import sys
import os
import tempfile
import csv

# Add the parent directory to the path so we can import main
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "transaction_ingest"

def test_get_transactions_empty():
    """Test getting transactions when none exist"""
    response = client.get("/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_add_transaction():
    """Test adding a single transaction"""
    transaction_data = {
        "id": "test-123",
        "user_id": "user-1",
        "amount": 100.50,
        "date": "2023-01-01",
        "type": "deposit",
        "description": "Test deposit"
    }
    
    response = client.post("/transactions", json=transaction_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-123"
    assert data["amount"] == 100.50

def test_get_transaction_by_id():
    """Test getting a specific transaction"""
    # First add a transaction
    transaction_data = {
        "id": "test-456",
        "user_id": "user-1",
        "amount": 200.75,
        "date": "2023-01-02",
        "type": "withdrawal",
        "description": "Test withdrawal"
    }
    
    client.post("/transactions", json=transaction_data)
    
    # Then retrieve it
    response = client.get("/transactions/test-456")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-456"
    assert data["amount"] == 200.75

def test_get_transactions():
    """Test getting all transactions"""
    # Add a few transactions
    transactions = [
        {
            "id": "test-789",
            "user_id": "user-1",
            "amount": 300.00,
            "date": "2023-01-03",
            "type": "transfer",
            "description": "Test transfer 1"
        },
        {
            "id": "test-101",
            "user_id": "user-2",
            "amount": 400.25,
            "date": "2023-01-04",
            "type": "payment",
            "description": "Test payment"
        }
    ]
    
    for transaction in transactions:
        client.post("/transactions", json=transaction)
    
    # Get all transactions
    response = client.get("/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_upload_csv_success():
    """Test successful CSV upload"""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['amount', 'date', 'type', 'description'])
        writer.writerow([100.50, '2023-01-01', 'deposit', 'Test deposit'])
        writer.writerow([200.75, '2023-01-02', 'withdrawal', 'Test withdrawal'])
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            response = client.post(
                "/upload",
                files={"file": ("test.csv", f, "text/csv")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "Successfully processed" in data["message"]
    finally:
        os.unlink(temp_file_path)

def test_upload_csv_invalid_file():
    """Test uploading an invalid file type"""
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is not a CSV file")
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            response = client.post(
                "/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 400
    finally:
        os.unlink(temp_file_path)

def test_upload_csv_missing_columns():
    """Test uploading CSV with missing required columns"""
    # Create a temporary CSV file with missing columns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['amount', 'date'])  # Missing type and description
        writer.writerow([100.50, '2023-01-01'])
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            response = client.post(
                "/upload",
                files={"file": ("test.csv", f, "text/csv")}
            )
        
        assert response.status_code == 400
    finally:
        os.unlink(temp_file_path)

if __name__ == "__main__":
    pytest.main([__file__])