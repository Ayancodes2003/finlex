from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import Response
import uvicorn
import logging
import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import redis
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_gateway")
app = FastAPI(title="API Gateway Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = "HS256"

# Redis for session management
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 16379)),
    db=0,
    decode_responses=True
)

# JWT token validation
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api_gateway", "timestamp": datetime.utcnow()}

# User authentication endpoints
@app.post("/auth/login")
async def login(username: str, password: str):
    # In a real implementation, verify credentials against database
    # This is a simplified example
    if username == "admin" and password == "password":
        # Create JWT token
        expire = datetime.utcnow() + timedelta(minutes=30)
        token_data = {
            "sub": username,
            "exp": expire,
            "role": "admin"
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        # Store session in Redis
        session_key = f"session:{username}"
        session_data = {
            "username": username,
            "role": "admin",
            "login_time": datetime.utcnow().isoformat()
        }
        redis_client.setex(session_key, 1800, json.dumps(session_data))  # 30 minutes expiry
        
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/logout")
async def logout(username: str, payload: dict = Depends(verify_token)):
    # Remove session from Redis
    session_key = f"session:{username}"
    redis_client.delete(session_key)
    return {"message": "Successfully logged out"}

# Proxy endpoints for other services
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:8001")
POLICY_SERVICE_URL = os.getenv("POLICY_SERVICE_URL", "http://localhost:8002")
COMPLIANCE_SERVICE_URL = os.getenv("COMPLIANCE_SERVICE_URL", "http://localhost:8003")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8004")

# Transaction service proxy - Public access
@app.get("/transactions")
async def get_transactions():
    # In a real implementation, proxy requests to the transaction service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.get(f"{TRANSACTION_SERVICE_URL}/transactions")
        return response.json()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")

@app.post("/transactions")
async def create_transaction(transaction: dict):
    # In a real implementation, proxy requests to the transaction service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.post(f"{TRANSACTION_SERVICE_URL}/transactions", json=transaction)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating transaction: {str(e)}")

@app.post("/upload")
async def upload_transactions(request: Request):
    # Proxy the file upload request to the transaction service
    import httpx
    try:
        # Forward the entire request to the transaction service
        async with httpx.AsyncClient() as client:
            # Get the raw request body and headers
            body = await request.body()
            headers = dict(request.headers)
            
            # Remove content-length header to let httpx recalculate it
            headers.pop('content-length', None)
            
            # Forward to transaction service
            response = await client.post(
                f"{TRANSACTION_SERVICE_URL}/upload",
                content=body,
                headers=headers
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading transactions: {str(e)}")

# Policy service proxy - Public access for policies
@app.get("/policies")
async def get_policies():
    # In a real implementation, proxy requests to the policy service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.get(f"{POLICY_SERVICE_URL}/policies")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching policies: {str(e)}")

@app.post("/policies")
async def create_policy(policy: dict):
    # In a real implementation, proxy requests to the policy service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.post(f"{POLICY_SERVICE_URL}/policies", json=policy)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating policy: {str(e)}")

@app.get("/policies/{policy_id}")
async def get_policy(policy_id: str):
    # In a real implementation, proxy requests to the policy service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.get(f"{POLICY_SERVICE_URL}/policies/{policy_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Policy not found")
        return response.json()
    except HTTPException as http_exc:
        logger.warning(f"HTTP Exception: {http_exc.detail}")
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching policy: {str(e)}")

@app.delete("/policies/{policy_id}")
async def delete_policy(policy_id: str):
    # In a real implementation, proxy requests to the policy service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.delete(f"{POLICY_SERVICE_URL}/policies/{policy_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Policy not found")
        return {"message": "Policy deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting policy: {str(e)}")

# Compliance service proxy - Public access
@app.post("/compliance/scan")
async def run_compliance_scan(scan_request: dict):
    # In a real implementation, proxy requests to the compliance service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.post(f"{COMPLIANCE_SERVICE_URL}/scan", json=scan_request)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running compliance scan: {str(e)}")

@app.get("/compliance/violations")
async def get_violations():
    # In a real implementation, proxy requests to the compliance service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.get(f"{COMPLIANCE_SERVICE_URL}/violations")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching violations: {str(e)}")

@app.get("/compliance/violations/{violation_id}")
async def get_violation(violation_id: str):
    # In a real implementation, proxy requests to the compliance service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.get(f"{COMPLIANCE_SERVICE_URL}/violations/{violation_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Violation not found")
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching violation: {str(e)}")

# RAG service proxy - Public access
@app.post("/reports/generate")
async def generate_report(report_request: dict):
    # In a real implementation, proxy requests to the RAG service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.post(f"{RAG_SERVICE_URL}/generate", json=report_request)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/reports")
async def get_reports():
    # In a real implementation, proxy requests to the RAG service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.get(f"{RAG_SERVICE_URL}/reports")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")

@app.get("/reports/{report_id}")
async def get_report(report_id: str):
    # In a real implementation, proxy requests to the RAG service
    # This is a placeholder that returns a direct response for testing
    import requests
    try:
        response = requests.get(f"{RAG_SERVICE_URL}/reports/{report_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Report not found")
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching report: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
