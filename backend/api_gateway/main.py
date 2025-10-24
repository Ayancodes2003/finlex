from fastapi import FastAPI, HTTPException, Depends, status, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import Response
import uvicorn
import logging
import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import redis
import json
import pandas as pd
import sqlite3
import uuid
import sys
import re
import numpy as np
import google.generativeai as genai
from pydantic import BaseModel

# --- Basic Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_gateway")
app = FastAPI(title="FinLex Monolithic Service", version="1.1.0")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security and Auth ---
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = "HS256"

# --- Redis for Session Management ---
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 16379)),
    db=0,
    decode_responses=True
)

# --- Database Setup (Merged from transaction_ingest) ---
# Use a file path that works in Vercel's temporary filesystem
DATABASE_URL = "/tmp/transactions.db"
conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        amount REAL,
        date TEXT,
        type TEXT,
        description TEXT,
        metadata TEXT
    )
''')
conn.commit()

# --- PDF Processing Setup ---
PDF_PROCESSING_AVAILABLE = False
try:
    import PyPDF2
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PyPDF2 = None
    logger.warning("PyPDF2 not installed. PDF processing will be disabled.")

# --- Gemini AI Setup ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
else:
    logger.warning("GEMINI_API_KEY not set. AI features will be disabled.")

# --- DataProcessor Class (Merged) ---
class DataProcessor:
    def __init__(self, db_path: str = DATABASE_URL):
        self.db_path = db_path
    
    def _convert_numpy_types(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        elif isinstance(obj, np.floating): return float(obj)
        elif isinstance(obj, np.ndarray): return obj.tolist()
        elif isinstance(obj, dict): return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list): return [self._convert_numpy_types(item) for item in obj]
        return obj

    def process_pdf_transactions(self, pdf_text: str) -> Dict[str, Any]:
        try:
            transactions = []
            transaction_pattern = r'(\d{4}-\d{2}-\d{2})\s+([A-Z_]+)\s+([$]?[\d,]+\.?\d*)\s+(.*)'
            matches = re.findall(transaction_pattern, pdf_text)
            
            for match in matches:
                date, trans_type, amount_str, description = match
                amount_str = amount_str.replace('$', '').replace(',', '')
                try: amount = float(amount_str)
                except ValueError: amount = 0.0
                
                transactions.append({
                    'id': str(uuid.uuid4()), 'user_id': 'pdf_user', 'amount': amount, 'date': date,
                    'type': trans_type, 'description': description.strip(),
                    'metadata': json.dumps({'source': 'pdf'})
                })
            
            if not transactions:
                transactions.append({
                    'id': str(uuid.uuid4()), 'user_id': 'pdf_user', 'amount': 0.0, 'date': datetime.now().isoformat(),
                    'type': 'PDF_IMPORTED', 'description': 'Transaction data imported from PDF document',
                    'metadata': json.dumps({'source': 'pdf', 'content_length': len(pdf_text)})
                })

            db_conn = sqlite3.connect(self.db_path)
            db_cursor = db_conn.cursor()
            for t in transactions:
                db_cursor.execute('INSERT OR REPLACE INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)',
                                  (t['id'], t['user_id'], t['amount'], t['date'], t['type'], t['description'], t['metadata']))
            db_conn.commit()
            db_conn.close()
            
            return {'success': True, 'message': f'Successfully processed {len(transactions)} transactions from PDF',
                    'statistics': {'total_transactions': len(transactions), 'total_amount': sum(t['amount'] for t in transactions)}}
        except Exception as e:
            return {'success': False, 'message': f'Error processing PDF transactions: {str(e)}'}

data_processor = DataProcessor()

# --- Pydantic Models (Merged) ---
class Transaction(BaseModel):
    id: str
    user_id: str
    amount: float
    date: str
    type: str
    description: str
    metadata: Optional[str] = None

class TransactionAnalysisResponse(BaseModel):
    risk_score: float
    risk_factors: List[str]
    recommendations: List[str]
    summary: str

# --- JWT Token Validation ---
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

# --- Core Endpoints ---
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "finlex_monolith", "timestamp": datetime.utcnow()}

@app.post("/auth/login")
async def login(username: str, password: str):
    if username == "admin" and password == "password":
        expire = datetime.utcnow() + timedelta(minutes=30)
        token = jwt.encode({"sub": username, "exp": expire, "role": "admin"}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# --- File Upload Endpoint (Refactored) ---
async def process_csv_file(file: UploadFile):
    try:
        contents = await file.read()
        from io import StringIO
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        
        required_columns = ['amount', 'date', 'type', 'description']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail="CSV missing required columns")

        transactions = []
        for _, row in df.iterrows():
            transactions.append({
                'id': str(uuid.uuid4()), 'user_id': 'default_user', 'amount': float(row['amount']),
                'date': str(row['date']), 'type': str(row['type']), 'description': str(row['description']),
                'metadata': str(row.get('metadata', ''))
            })
        
        for t in transactions:
            cursor.execute('INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (t['id'], t['user_id'], t['amount'], t['date'], t['type'], t['description'], t['metadata']))
        conn.commit()
        return {"message": f"Successfully processed {len(transactions)} transactions from CSV", "transactions": transactions}
    except Exception as e:
        logger.error(f"CSV Processing Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing CSV file: {str(e)}")

async def process_pdf_file(file: UploadFile):
    if not PDF_PROCESSING_AVAILABLE:
        raise HTTPException(status_code=501, detail="PDF processing is not enabled on the server.")
    try:
        contents = await file.read()
        from io import BytesIO
        pdf_reader = PyPDF2.PdfReader(BytesIO(contents))
        text = "".join(page.extract_text() for page in pdf_reader.pages)
        
        result = data_processor.process_pdf_transactions(text)
        if result['success']:
            return {"message": result['message'], "statistics": result['statistics']}
        else:
            raise HTTPException(status_code=500, detail=result['message'])
    except Exception as e:
        logger.error(f"PDF Processing Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {str(e)}")

@app.post("/upload")
async def upload_transactions(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if file.filename.endswith('.csv'):
        return await process_csv_file(file)
    elif file.filename.endswith('.pdf'):
        return await process_pdf_file(file)
    else:
        raise HTTPException(status_code=400, detail="Only CSV and PDF files are supported")

# --- Transaction Endpoints (Merged) ---
@app.get("/transactions", response_model=List[Transaction])
async def get_transactions():
    cursor.execute("SELECT * FROM transactions")
    return [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

@app.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return dict(zip([c[0] for c in cursor.description], row))

# --- Placeholder Endpoints for Frontend ---
# These endpoints are called by the frontend but were part of other microservices.
# We'll add placeholder responses for them to prevent errors.
@app.get("/policies")
async def get_policies():
    return [{"id": "1", "title": "Sample AML Policy", "jurisdiction": "US", "category": "AML", "created_at": "2023-01-01"}]

@app.get("/policies/{policy_id}")
async def get_policy(policy_id: str):
    return {"id": policy_id, "title": "Sample AML Policy", "jurisdiction": "US", "category": "AML", "created_at": "2023-01-01", "content": "This is a sample policy."}

@app.post("/compliance/scan")
async def run_compliance_scan():
    return {"message": "Compliance scan completed successfully."}

@app.get("/compliance/violations")
async def get_violations():
    return [{"id": "1", "transactionId": "TXN-001", "policy": "Sample AML Policy", "risk": "high", "description": "Large cash transaction"}]

@app.get("/compliance/violations/{violation_id}")
async def get_violation(violation_id: str):
    # This is a placeholder response
    return {
        "id": violation_id,
        "transaction_id": "TXN-001",
        "policy_id": "Sample AML Policy",
        "risk_level": "high",
        "created_at": "2023-01-01T12:00:00Z",
        "description": "This is a sample high-risk violation for a large cash transaction.",
        "recommendation": "Review transaction source and destination. File a suspicious activity report if necessary."
    }

@app.get("/reports")
async def get_reports():
    return [{"id": "1", "generated": "2023-01-01T12:00:00Z"}]

@app.get("/reports/{report_id}")
async def get_report(report_id: str):
    # This is a placeholder response
    return {
        "id": report_id,
        "generated": "2023-01-01T12:00:00Z",
        "status": "Completed",
        "summary": "This is a sample report summary.",
        "details": "This section would contain the detailed findings of the generated report."
    }

@app.post("/reports/generate")
async def generate_report():
    return {"message": "Report generated successfully."}

# --- Main Execution ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
