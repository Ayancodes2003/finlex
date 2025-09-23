#!/usr/bin/env python3
"""
Demo script for the FinLex platform
"""
import requests
import json
import time

def demo_platform():
    """Demonstrate the FinLex platform functionality"""
    print("FinLex Platform Demo")
    print("=" * 30)
    
    # 1. Check service health
    print("\n1. Checking service health...")
    services = [
        ("API Gateway", "http://localhost:18000/health"),
        ("Transaction Ingest", "http://localhost:18001/health"),
        ("Policy Extractor", "http://localhost:8002/health"),
        ("Compliance Matcher", "http://localhost:8003/health"),
        ("RAG Generator", "http://localhost:8004/health"),
        ("Vector Database", "http://localhost:8010/health")
    ]
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✓ {service_name} is healthy")
            else:
                print(f"  ✗ {service_name} returned status {response.status_code}")
        except Exception as e:
            print(f"  ✗ {service_name} is not responding: {e}")
    
    # 2. Get data summary
    print("\n2. Getting data summary...")
    try:
        response = requests.get("http://localhost:18001/data-summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("  Transaction Data Summary:")
            print(f"    Total transactions: {data['transaction_data']['total_transactions']}")
            print(f"    Fraudulent transactions: {data['transaction_data']['fraudulent_transactions']}")
            print(f"    Transaction types: {list(data['transaction_data']['transaction_types'].keys())}")
        else:
            print(f"  ✗ Failed to get data summary: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Failed to get data summary: {e}")
    
    # 3. Simulate compliance scan
    print("\n3. Simulating compliance scan...")
    try:
        # In a real implementation, this would trigger the compliance matcher service
        print("  Simulating compliance analysis of transactions...")
        time.sleep(2)  # Simulate processing time
        print("  ✓ Compliance scan completed")
        print("  Found 40 potential violations")
        print("  Risk levels: High (15), Medium (20), Low (5)")
    except Exception as e:
        print(f"  ✗ Compliance scan failed: {e}")
    
    # 4. Generate report
    print("\n4. Generating compliance report...")
    try:
        # In a real implementation, this would trigger the RAG generator service
        print("  Generating AI-powered compliance report...")
        time.sleep(2)  # Simulate processing time
        print("  ✓ Compliance report generated successfully")
        print("  Report includes:")
        print("    - Executive summary")
        print("    - Detailed violation analysis")
        print("    - Risk assessment")
        print("    - Recommendations")
    except Exception as e:
        print(f"  ✗ Report generation failed: {e}")
    
    print("\n" + "=" * 30)
    print("Demo completed successfully!")
    print("\nTo interact with the full platform:")
    print("1. Start all services: docker-compose up -d")
    print("2. Visit the web interface: http://localhost:3000")
    print("3. Log in and explore the dashboard")
    print("4. Upload additional data files")
    print("5. Run compliance scans")
    print("6. Generate reports")

if __name__ == "__main__":
    demo_platform()