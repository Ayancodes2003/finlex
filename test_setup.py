#!/usr/bin/env python3
"""
Test script to verify the FinLex setup
"""
import subprocess
import sys
import time
import requests

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_docker_compose():
    """Test if docker-compose is available"""
    print("Testing Docker Compose availability...")
    success, stdout, stderr = run_command("docker-compose --version")
    if success:
        print(f"✓ Docker Compose is available: {stdout.strip()}")
        return True
    else:
        print(f"✗ Docker Compose is not available: {stderr}")
        return False

def test_docker_build():
    """Test if we can build the docker images"""
    print("Testing Docker build for API Gateway...")
    success, stdout, stderr = run_command("docker build -t finlex-api-gateway-test .", cwd="backend/api_gateway")
    if success:
        print("✓ Docker build successful for API Gateway")
        # Clean up test image
        run_command("docker rmi finlex-api-gateway-test")
        return True
    else:
        print(f"✗ Docker build failed for API Gateway: {stderr}")
        return False

def test_python_imports():
    """Test if required Python packages can be imported"""
    print("Testing Python package imports...")
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pandas",
        "redis",
        "jwt",
        "pytest"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {package}: {e}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def test_file_structure():
    """Test if required files and directories exist"""
    print("Testing file structure...")
    required_paths = [
        "backend/api_gateway/main.py",
        "backend/api_gateway/requirements.txt",
        "backend/api_gateway/Dockerfile",
        "backend/transaction_ingest/main.py",
        "backend/transaction_ingest/requirements.txt",
        "backend/transaction_ingest/Dockerfile",
        "backend/policy_extractor/main.py",
        "backend/compliance_matcher/main.py",
        "backend/rag_generator/main.py",
        "backend/vector_db/main.py",
        "frontend/index.html",
        "frontend/styles.css",
        "frontend/app.js",
        "docker-compose.yml",
        "nginx.conf",
        "docs/api.md",
        "docs/user-guide.md",
        "docs/developer-setup.md",
        "docs/deployment.md"
    ]
    
    missing_paths = []
    for path in required_paths:
        import os
        if not os.path.exists(path):
            print(f"✗ Missing path: {path}")
            missing_paths.append(path)
        else:
            print(f"✓ Found: {path}")
    
    return len(missing_paths) == 0

def main():
    """Main test function"""
    print("FinLex Setup Verification Script")
    print("=" * 40)
    
    tests = [
        test_file_structure,
        test_python_imports,
        test_docker_compose,
        test_docker_build
    ]
    
    results = []
    for test in tests:
        print()
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Your FinLex setup is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())