from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import uuid
from datetime import datetime
import uvicorn
import json
import google.generativeai as genai

app = FastAPI(title="Compliance Matcher Service", version="1.0.0")

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Initialize the model
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
else:
    model = None
    print("Warning: GEMINI_API_KEY not set. AI features will be disabled.")

# Database setup for violations
VIOLATIONS_DATABASE_URL = os.getenv("VIOLATIONS_DATABASE_URL", "violations.db")
conn = sqlite3.connect(VIOLATIONS_DATABASE_URL, check_same_thread=False)
cursor = conn.cursor()

# Create violations table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS violations (
        id TEXT PRIMARY KEY,
        transaction_id TEXT,
        policy_id TEXT,
        risk_level TEXT,
        description TEXT,
        recommendation TEXT,
        created_at TEXT
    )
''')
conn.commit()

class Violation(BaseModel):
    id: str
    transaction_id: str
    policy_id: str
    risk_level: str
    description: str
    recommendation: str
    created_at: str

class ViolationResponse(BaseModel):
    id: str
    transaction_id: str
    policy_id: str
    risk_level: str
    description: str
    recommendation: str
    created_at: str

class ComplianceScanRequest(BaseModel):
    transactions: List[dict]
    policies: List[dict]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "compliance_matcher", "timestamp": datetime.utcnow()}

# AI-powered compliance checking function using Gemini
def check_compliance_with_ai(transaction_data, policy_data):
    if not model:
        # Fallback to rule-based checking if Gemini is not available
        return check_compliance_rule_based(transaction_data, policy_data)
    
    try:
        # Create a prompt for the AI to analyze compliance
        prompt = f"""
        Analyze the following financial transaction for compliance with the regulatory policy:
        
        TRANSACTION DATA:
        {json.dumps(transaction_data, indent=2)}
        
        POLICY REQUIREMENTS:
        {json.dumps(policy_data, indent=2)}
        
        Please determine if this transaction violates the policy and provide:
        1. Risk level (low, medium, high)
        2. Detailed description of the violation (if any)
        3. Specific recommendation for addressing the issue
        4. Confidence score (0-100) in your assessment
        
        Respond in JSON format with the following structure:
        {{
            "risk_level": "low|medium|high",
            "description": "Detailed description of findings",
            "recommendation": "Actionable recommendation",
            "confidence": 95
        }}
        """
        
        # Generate content using Gemini
        response = model.generate_content(prompt)
        
        # Try to parse the response as JSON
        try:
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # If parsing fails, extract information from text response
            return extract_compliance_info_from_text(response.text)
    
    except Exception as e:
        print(f"Error checking compliance with Gemini: {str(e)}")
        # Fallback to rule-based checking
        return check_compliance_rule_based(transaction_data, policy_data)

# Extract compliance information from text response
def extract_compliance_info_from_text(text):
    # Simple extraction logic - in a real implementation, this would be more sophisticated
    risk_level = "medium"  # Default
    description = text[:200]  # First 200 characters
    recommendation = "Review transaction manually"
    confidence = 70  # Default confidence
    
    # Try to extract risk level from text
    if "high" in text.lower():
        risk_level = "high"
    elif "low" in text.lower():
        risk_level = "low"
    
    return {
        "risk_level": risk_level,
        "description": description,
        "recommendation": recommendation,
        "confidence": confidence
    }

# Rule-based compliance checking (fallback)
def check_compliance_rule_based(transaction_data, policy_data):
    # This is a placeholder for the actual compliance checking logic
    # In a real implementation, this would use AI to compare transactions against policies
    violations = []
    
    # Simple rule-based checking for demonstration
    amount = transaction_data.get('amount', 0)
    transaction_type = transaction_data.get('type', '').lower()
    description = transaction_data.get('description', '').lower()
    
    # Example rules
    if amount > 10000 and 'cash' in transaction_type:
        violations.append({
            "risk_level": "high",
            "description": f"Large cash transaction (${amount}) exceeds threshold",
            "recommendation": "Verify source of funds and file SAR if necessary",
            "confidence": 90
        })
    
    if 'suspicious' in description:
        violations.append({
            "risk_level": "medium",
            "description": "Transaction description contains suspicious keywords",
            "recommendation": "Review transaction for potential fraud indicators",
            "confidence": 80
        })
    
    # If no violations found, return low risk
    if not violations:
        return {
            "risk_level": "low",
            "description": "No clear violations detected",
            "recommendation": "Continue monitoring",
            "confidence": 95
        }
    
    # Return the highest risk violation
    violations.sort(key=lambda x: {"low": 1, "medium": 2, "high": 3}[x["risk_level"]], reverse=True)
    return violations[0]

# Run compliance scan on transactions
@app.post("/scan")
async def run_compliance_scan(request: ComplianceScanRequest):
    try:
        # Check each transaction against each policy
        detected_violations = []
        for transaction in request.transactions:
            for policy in request.policies:
                compliance_result = check_compliance_with_ai(transaction, policy)
                
                violation_id = str(uuid.uuid4())
                created_at = datetime.utcnow().isoformat()
                
                violation = {
                    'id': violation_id,
                    'transaction_id': transaction['id'],
                    'policy_id': policy['id'],
                    'risk_level': compliance_result['risk_level'],
                    'description': compliance_result['description'],
                    'recommendation': compliance_result['recommendation'],
                    'created_at': created_at
                }
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO violations (id, transaction_id, policy_id, risk_level, description, recommendation, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    violation['id'],
                    violation['transaction_id'],
                    violation['policy_id'],
                    violation['risk_level'],
                    violation['description'],
                    violation['recommendation'],
                    violation['created_at']
                ))
                
                detected_violations.append(violation)
        
        conn.commit()
        
        return {
            "message": f"Compliance scan completed. Found {len(detected_violations)} violations.",
            "violations": detected_violations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during compliance scan: {str(e)}")

# Get all violations
@app.get("/violations", response_model=List[ViolationResponse])
async def get_violations():
    cursor.execute("SELECT * FROM violations")
    rows = cursor.fetchall()
    
    violations = []
    for row in rows:
        violation = ViolationResponse(
            id=row[0],
            transaction_id=row[1],
            policy_id=row[2],
            risk_level=row[3],
            description=row[4],
            recommendation=row[5],
            created_at=row[6]
        )
        violations.append(violation)
    
    return violations

# Get violation by ID
@app.get("/violations/{violation_id}", response_model=ViolationResponse)
async def get_violation(violation_id: str):
    cursor.execute("SELECT * FROM violations WHERE id = ?", (violation_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    violation = ViolationResponse(
        id=row[0],
        transaction_id=row[1],
        policy_id=row[2],
        risk_level=row[3],
        description=row[4],
        recommendation=row[5],
        created_at=row[6]
    )
    
    return violation

# Get violations by transaction ID
@app.get("/violations/transaction/{transaction_id}", response_model=List[ViolationResponse])
async def get_violations_by_transaction(transaction_id: str):
    cursor.execute("SELECT * FROM violations WHERE transaction_id = ?", (transaction_id,))
    rows = cursor.fetchall()
    
    violations = []
    for row in rows:
        violation = ViolationResponse(
            id=row[0],
            transaction_id=row[1],
            policy_id=row[2],
            risk_level=row[3],
            description=row[4],
            recommendation=row[5],
            created_at=row[6]
        )
        violations.append(violation)
    
    return violations

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)