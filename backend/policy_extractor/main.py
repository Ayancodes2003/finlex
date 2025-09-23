from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime
import uvicorn
import sqlite3
import json
import hashlib
import google.generativeai as genai

app = FastAPI(title="Policy Extractor Service", version="1.0.0")

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Initialize the model
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
else:
    model = None
    print("Warning: GEMINI_API_KEY not set. AI features will be disabled.")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "policies.db")
conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
cursor = conn.cursor()

# Create policies table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS policies (
        id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        jurisdiction TEXT,
        category TEXT,
        created_at TEXT,
        embeddings TEXT
    )
''')
conn.commit()

class Policy(BaseModel):
    id: str
    title: str
    content: str
    jurisdiction: str
    category: str
    created_at: str
    embeddings: Optional[str] = None

class PolicyResponse(BaseModel):
    id: str
    title: str
    content: str
    jurisdiction: str
    category: str
    created_at: str
    embeddings: Optional[str] = None

class PolicyAnalysisResponse(BaseModel):
    requirements: List[dict]
    risk_categories: List[str]
    compliance_guidelines: List[str]
    summary: str

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "policy_extractor", "timestamp": datetime.utcnow()}

# AI-powered policy analysis using Gemini
def analyze_policy_with_gemini(content: str):
    if not model:
        # Fallback to simple extraction if Gemini is not available
        return extract_policy_requirements_simple(content)
    
    try:
        # Create a prompt for the AI to analyze the policy
        prompt = f"""
        Analyze the following regulatory policy document and extract structured information:
        
        POLICY DOCUMENT:
        {content}
        
        Please provide:
        1. Key compliance requirements (as a list of specific requirements)
        2. Risk categories addressed by this policy
        3. Compliance guidelines for each requirement
        4. A concise summary of the policy
        
        Respond in JSON format with the following structure:
        {{
            "requirements": [
                {{
                    "id": "req_1",
                    "text": "Specific requirement text",
                    "risk_level": "low|medium|high"
                }}
            ],
            "risk_categories": ["category1", "category2"],
            "compliance_guidelines": ["guideline1", "guideline2"],
            "summary": "Concise summary of the policy"
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
            return extract_policy_info_from_text(response.text)
    
    except Exception as e:
        print(f"Error analyzing policy with Gemini: {str(e)}")
        # Fallback to simple extraction
        return extract_policy_requirements_simple(content)

# Extract policy information from text response
def extract_policy_info_from_text(text):
    # Simple extraction logic - in a real implementation, this would be more sophisticated
    requirements = []
    risk_categories = []
    compliance_guidelines = []
    summary = text[:200]  # First 200 characters as summary
    
    # Try to extract requirements from text
    sentences = text.split('.')
    for i, sentence in enumerate(sentences[:10]):  # First 10 sentences
        if 'must' in sentence.lower() or 'shall' in sentence.lower() or 'required' in sentence.lower():
            requirements.append({
                "id": f"req_{i}",
                "text": sentence.strip(),
                "risk_level": "medium" if "must" in sentence.lower() else "low"
            })
    
    return {
        "requirements": requirements,
        "risk_categories": risk_categories,
        "compliance_guidelines": compliance_guidelines,
        "summary": summary
    }

# Simple policy extraction (fallback)
def extract_policy_requirements_simple(content: str):
    # This is a placeholder for the actual AI processing
    # In a real implementation, this would call the Gemini API to extract requirements
    requirements = []
    # Simple extraction logic for demonstration
    sentences = content.split('.')
    for i, sentence in enumerate(sentences):
        if 'must' in sentence.lower() or 'shall' in sentence.lower() or 'required' in sentence.lower():
            requirements.append({
                "id": f"req_{i}",
                "text": sentence.strip(),
                "risk_level": "medium" if "must" in sentence.lower() else "low"
            })
    return {
        "requirements": requirements,
        "risk_categories": ["general"],
        "compliance_guidelines": ["Follow policy requirements"],
        "summary": content[:200] if len(content) > 200 else content
    }

# Simulated embedding generation (in a real implementation, this would use a model to generate embeddings)
def generate_embeddings(content: str):
    # This is a placeholder for the actual embedding generation
    # In a real implementation, this would use a model to generate embeddings
    # For now, we'll just return a simple hash of the content
    return hashlib.md5(content.encode()).hexdigest()

# Upload policy document
@app.post("/upload")
async def upload_policy(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    jurisdiction: str = "default",
    category: str = "general"
):
    if not file.filename or not file.filename.endswith(('.txt', '.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only TXT, PDF, or DOCX files are allowed")
    
    try:
        # Read file content
        content = (await file.read()).decode('utf-8')
        
        # Generate title if not provided
        if not title:
            title = file.filename.split('.')[0] if file.filename else "Untitled Policy"
        
        # Analyze policy using AI
        analysis = analyze_policy_with_gemini(content)
        
        # Generate embeddings for similarity search
        embeddings = generate_embeddings(content)
        
        # Create policy record
        policy_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        policy_data = {
            'id': policy_id,
            'title': title,
            'content': content,
            'jurisdiction': jurisdiction,
            'category': category,
            'created_at': created_at,
            'embeddings': embeddings
        }
        
        # Insert into database
        cursor.execute('''
            INSERT INTO policies (id, title, content, jurisdiction, category, created_at, embeddings)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            policy_data['id'],
            policy_data['title'],
            policy_data['content'],
            policy_data['jurisdiction'],
            policy_data['category'],
            policy_data['created_at'],
            policy_data['embeddings']
        ))
        
        conn.commit()
        
        return {
            "message": "Policy uploaded and processed successfully",
            "policy": policy_data,
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing policy: {str(e)}")

# Analyze existing policy
@app.post("/analyze/{policy_id}", response_model=PolicyAnalysisResponse)
async def analyze_policy(policy_id: str):
    try:
        # Get policy from database
        cursor.execute("SELECT * FROM policies WHERE id = ?", (policy_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Extract content from row
        content = row[2]  # Content is in the third column
        
        # Analyze policy using AI
        analysis = analyze_policy_with_gemini(content)
        
        return PolicyAnalysisResponse(
            requirements=analysis["requirements"],
            risk_categories=analysis["risk_categories"],
            compliance_guidelines=analysis["compliance_guidelines"],
            summary=analysis["summary"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing policy: {str(e)}")

# Get all policies
@app.get("/policies", response_model=List[PolicyResponse])
async def get_policies():
    cursor.execute("SELECT * FROM policies")
    rows = cursor.fetchall()
    
    policies = []
    for row in rows:
        policy = PolicyResponse(
            id=row[0],
            title=row[1],
            content=row[2],
            jurisdiction=row[3],
            category=row[4],
            created_at=row[5],
            embeddings=row[6]
        )
        policies.append(policy)
    
    return policies

# Get policy by ID
@app.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str):
    cursor.execute("SELECT * FROM policies WHERE id = ?", (policy_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    policy = PolicyResponse(
        id=row[0],
        title=row[1],
        content=row[2],
        jurisdiction=row[3],
        category=row[4],
        created_at=row[5],
        embeddings=row[6]
    )
    
    return policy

# Add a single policy
@app.post("/policies", response_model=PolicyResponse)
async def add_policy(policy: Policy):
    try:
        cursor.execute('''
            INSERT INTO policies (id, title, content, jurisdiction, category, created_at, embeddings)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            policy.id,
            policy.title,
            policy.content,
            policy.jurisdiction,
            policy.category,
            policy.created_at,
            policy.embeddings
        ))
        
        conn.commit()
        return policy
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding policy: {str(e)}")

# Update a policy
@app.put("/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(policy_id: str, policy: Policy):
    try:
        cursor.execute('''
            UPDATE policies 
            SET title = ?, content = ?, jurisdiction = ?, category = ?, created_at = ?, embeddings = ?
            WHERE id = ?
        ''', (
            policy.title,
            policy.content,
            policy.jurisdiction,
            policy.category,
            policy.created_at,
            policy.embeddings,
            policy_id
        ))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return policy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating policy: {str(e)}")

# Delete a policy
@app.delete("/policies/{policy_id}")
async def delete_policy(policy_id: str):
    try:
        cursor.execute("DELETE FROM policies WHERE id = ?", (policy_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return {"message": "Policy deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting policy: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)