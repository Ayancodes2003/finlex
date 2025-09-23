#!/usr/bin/env python3
"""
Integration test for the FinLex platform
"""
import subprocess
import time
import requests
import json

def start_services():
    """Start the Docker services"""
    print("Starting Docker services...")
    result = subprocess.run(
        ["docker-compose", "up", "-d"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error starting services: {result.stderr}")
        return False
    
    print("Services started successfully")
    return True

def wait_for_services():
    """Wait for services to be ready"""
    print("Waiting for services to be ready...")
    time.sleep(30)  # Give services time to start
    
    # Check if services are responding
    services = [
        ("API Gateway", "http://localhost:8000/health"),
        ("Transaction Ingest", "http://localhost:8001/health"),
        ("Policy Extractor", "http://localhost:8002/health"),
        ("Compliance Matcher", "http://localhost:8003/health"),
        ("RAG Generator", "http://localhost:8004/health"),
        ("Vector Database", "http://localhost:8010/health")
    ]
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {service_name} is ready")
            else:
                print(f"✗ {service_name} returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ {service_name} is not responding: {e}")
            return False
    
    return True

def test_api_endpoints():
    """Test API endpoints"""
    print("Testing API endpoints...")
    
    # Test health endpoints
    health_endpoints = [
        ("API Gateway", "http://localhost:8000/health"),
        ("Transaction Ingest", "http://localhost:8001/health"),
        ("Policy Extractor", "http://localhost:8002/health"),
        ("Compliance Matcher", "http://localhost:8003/health"),
        ("RAG Generator", "http://localhost:8004/health"),
        ("Vector Database", "http://localhost:8010/health")
    ]
    
    for service_name, url in health_endpoints:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print(f"✓ {service_name} health check passed")
                else:
                    print(f"✗ {service_name} health check failed: {data}")
            else:
                print(f"✗ {service_name} health check failed with status {response.status_code}")
        except Exception as e:
            print(f"✗ {service_name} health check failed: {e}")
    
    # Test transaction ingest data summary
    try:
        response = requests.get("http://localhost:8001/data-summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Transaction data summary retrieved: {data}")
        else:
            print(f"✗ Transaction data summary failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Transaction data summary failed: {e}")

def stop_services():
    """Stop the Docker services"""
    print("Stopping Docker services...")
    result = subprocess.run(
        ["docker-compose", "down"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error stopping services: {result.stderr}")
        return False
    
    print("Services stopped successfully")
    return True

def main():
    """Main integration test function"""
    print("FinLex Integration Test")
    print("=" * 30)
    
    # Start services
    if not start_services():
        return 1
    
    # Wait for services to be ready
    if not wait_for_services():
        stop_services()
        return 1
    
    # Test API endpoints
    test_api_endpoints()
    
    # Stop services
    stop_services()
    
    print("\nIntegration test completed!")
    return 0

if __name__ == "__main__":
    exit(main())