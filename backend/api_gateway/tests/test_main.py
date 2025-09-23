import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

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
    assert data["service"] == "api_gateway"

@patch('main.jwt.encode')
def test_login_success(mock_jwt_encode):
    """Test successful login"""
    mock_jwt_encode.return_value = "test_token"
    
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "password"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure():
    """Test failed login"""
    response = client.post("/auth/login", data={
        "username": "wrong",
        "password": "wrong"
    })
    
    assert response.status_code == 401

@patch('main.jwt.decode')
def test_logout(mock_jwt_decode):
    """Test logout functionality"""
    mock_jwt_decode.return_value = {"sub": "admin"}
    
    response = client.post("/auth/logout", 
                          data={"username": "admin"},
                          headers={"Authorization": "Bearer test_token"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out"

# Test proxy endpoints
@patch('main.jwt.decode')
def test_transaction_proxy(mock_jwt_decode):
    """Test transaction proxy endpoint"""
    mock_jwt_decode.return_value = {"sub": "admin"}
    
    response = client.get("/transactions",
                         headers={"Authorization": "Bearer test_token"})
    
    # Should return the proxy message
    assert response.status_code == 200
    data = response.json()
    assert "service_url" in data

@patch('main.jwt.decode')
def test_policy_proxy(mock_jwt_decode):
    """Test policy proxy endpoint"""
    mock_jwt_decode.return_value = {"sub": "admin"}
    
    response = client.get("/policies",
                         headers={"Authorization": "Bearer test_token"})
    
    # Should return the proxy message
    assert response.status_code == 200
    data = response.json()
    assert "service_url" in data

@patch('main.jwt.decode')
def test_compliance_proxy(mock_jwt_decode):
    """Test compliance proxy endpoint"""
    mock_jwt_decode.return_value = {"sub": "admin"}
    
    response = client.get("/compliance",
                         headers={"Authorization": "Bearer test_token"})
    
    # Should return the proxy message
    assert response.status_code == 200
    data = response.json()
    assert "service_url" in data

@patch('main.jwt.decode')
def test_rag_proxy(mock_jwt_decode):
    """Test RAG proxy endpoint"""
    mock_jwt_decode.return_value = {"sub": "admin"}
    
    response = client.get("/reports",
                         headers={"Authorization": "Bearer test_token"})
    
    # Should return the proxy message
    assert response.status_code == 200
    data = response.json()
    assert "service_url" in data

if __name__ == "__main__":
    pytest.main([__file__])