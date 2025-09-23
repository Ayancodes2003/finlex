#!/usr/bin/env python3
"""
Final verification script for the FinLex platform
"""
import requests
import subprocess
import json

def verify_platform():
    """Verify that the FinLex platform is working correctly"""
    print("FinLex Platform - Final Verification")
    print("=" * 40)
    
    # Check if Docker services are running
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            running_services = len([line for line in lines if line.strip()])
            print(f"✅ Docker services are running ({running_services} services)")
        else:
            print("❌ Docker services are not running")
            return False
            
    except FileNotFoundError:
        print("❌ Docker Compose not found")
        return False
    except Exception as e:
        print(f"❌ Error checking Docker services: {e}")
        return False
    
    # Check frontend accessibility
    try:
        response = requests.get("http://localhost:13000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend is not accessible: {e}")
        return False
    
    # Check backend services
    services = [
        ("API Gateway", "http://localhost:18000/health"),
        ("Transaction Ingest", "http://localhost:18001/health"),
        ("Policy Extractor", "http://localhost:8002/health"),
        ("Compliance Matcher", "http://localhost:8003/health"),
        ("RAG Generator", "http://localhost:8004/health"),
        ("Vector Database", "http://localhost:8010/health")
    ]
    
    all_services_healthy = True
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} is healthy")
            else:
                print(f"❌ {service_name} returned status {response.status_code}")
                all_services_healthy = False
        except Exception as e:
            print(f"❌ {service_name} is not responding: {e}")
            all_services_healthy = False
    
    if not all_services_healthy:
        return False
    
    # Check data processing
    try:
        response = requests.get("http://localhost:18001/data-summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_transactions = data.get('transaction_data', {}).get('total_transactions', 0)
            print(f"✅ Data processing working (Total transactions: {total_transactions})")
        else:
            print(f"❌ Data processing endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data processing endpoint failed: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 FINLEX PLATFORM VERIFICATION COMPLETE")
    print("✅ All services are running correctly")
    print("✅ Frontend is accessible at http://localhost:13000")
    print("✅ All backend services are healthy")
    print("✅ Data processing is working")
    print("\nNext steps:")
    print("1. Visit http://localhost:13000 to use the platform")
    print("2. Integrate Google's Gemini AI for full AI capabilities")
    print("3. Configure production database and security settings")
    
    return True

if __name__ == "__main__":
    verify_platform()