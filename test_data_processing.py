#!/usr/bin/env python3
"""
Test script to verify data processing
"""
import requests
import json

def test_data_processing():
    """Test that data processing worked correctly"""
    print("Testing Data Processing")
    print("=" * 30)
    
    # Test transaction ingest service
    try:
        response = requests.get("http://localhost:18001/health", timeout=5)
        if response.status_code == 200:
            print("✓ Transaction Ingest Service is running")
        else:
            print(f"✗ Transaction Ingest Service returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Transaction Ingest Service is not responding: {e}")
    
    # Test data summary endpoint
    try:
        response = requests.get("http://localhost:18001/data-summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ Data summary endpoint is working")
            print(f"  Total transactions: {data.get('transaction_data', {}).get('total_transactions', 'N/A')}")
            print(f"  Fraudulent transactions: {data.get('transaction_data', {}).get('fraudulent_transactions', 'N/A')}")
        else:
            print(f"✗ Data summary endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Data summary endpoint failed: {e}")
    
    # Test transactions endpoint
    try:
        response = requests.get("http://localhost:18001/transactions", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ Transactions endpoint is working")
            print(f"  Number of transactions in database: {len(data)}")
        else:
            print(f"✗ Transactions endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Transactions endpoint failed: {e}")

if __name__ == "__main__":
    test_data_processing()