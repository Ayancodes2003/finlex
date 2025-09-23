#!/usr/bin/env python3
"""
Status script for the FinLex platform
"""
import subprocess
import json

def show_status():
    """Show the status of all services"""
    print("FinLex Platform Status")
    print("=" * 30)
    
    # Get Docker Compose status
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Parse JSON output
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:  # Check if there's output
                print("Running Services:")
                for line in lines:
                    if line.strip():
                        try:
                            service = json.loads(line)
                            print(f"  - {service.get('Service', 'Unknown')}: {service.get('Status', 'Unknown')}")
                        except json.JSONDecodeError:
                            print(f"  - {line}")
            else:
                print("No services are currently running")
        else:
            print("Error getting service status")
            print(result.stderr)
            
    except FileNotFoundError:
        print("Docker Compose not found. Please install Docker Desktop.")
    except Exception as e:
        print(f"Error checking service status: {e}")
    
    print("\nService URLs:")
    print("  Frontend (Nginx): http://localhost:13000")
    print("  API Gateway: http://localhost:18000")
    print("  Transaction Ingest: http://localhost:18001")
    print("  Policy Extractor: http://localhost:8002")
    print("  Compliance Matcher: http://localhost:8003")
    print("  RAG Generator: http://localhost:8004")
    print("  Vector Database: http://localhost:8010")

if __name__ == "__main__":
    show_status()