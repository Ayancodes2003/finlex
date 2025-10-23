from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import sqlite3
import os
import uuid
from datetime import datetime
import uvicorn
import sys
import json
import google.generativeai as genai

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor

# Import PyPDF2 for PDF processing
PDF_PROCESSING_AVAILABLE = False
try:
    import importlib
    PyPDF2 = importlib.import_module('PyPDF2')
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PyPDF2 = None
    print("Warning: PyPDF2 not installed. PDF processing will be disabled.")

app = FastAPI(title="Transaction Ingest Service", version="1.0.0")

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
DATABASE_URL = os.getenv("DATABASE_URL", "transactions.db")
conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
cursor = conn.cursor()

# Create transactions table
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

# Initialize data processor
data_processor = DataProcessor(DATABASE_URL)

class Transaction(BaseModel):
    id: str
    user_id: str
    amount: float
    date: str
    type: str
    description: str
    metadata: Optional[str] = None

class TransactionResponse(BaseModel):
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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "transaction_ingest", "timestamp": datetime.utcnow()}

# AI-powered transaction analysis using Gemini
def analyze_transaction_with_gemini(transaction_data):
    if not model:
        # Fallback to simple analysis if Gemini is not available
        return analyze_transaction_simple(transaction_data)
    
    try:
        # Create a prompt for the AI to analyze the transaction
        prompt = f"""
        Analyze the following financial transaction for potential compliance risks:
        
        TRANSACTION DATA:
        {json.dumps(transaction_data, indent=2)}
        
        Please provide:
        1. Risk score (0-100) indicating the likelihood of compliance issues
        2. Key risk factors identified in this transaction
        3. Specific recommendations for compliance review
        4. A concise summary of your analysis
        
        Respond in JSON format with the following structure:
        {{
            "risk_score": 75.5,
            "risk_factors": ["factor1", "factor2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "summary": "Concise summary of the analysis"
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
            return extract_transaction_info_from_text(response.text)
    
    except Exception as e:
        print(f"Error analyzing transaction with Gemini: {str(e)}")
        # Fallback to simple analysis
        return analyze_transaction_simple(transaction_data)

# Extract transaction information from text response
def extract_transaction_info_from_text(text):
    # Simple extraction logic - in a real implementation, this would be more sophisticated
    risk_score = 50.0  # Default risk score
    risk_factors = []
    recommendations = []
    summary = text[:200]  # First 200 characters as summary
    
    # Try to extract risk score from text
    import re
    score_match = re.search(r'\b\d{1,3}\b', text)
    if score_match:
        try:
            score = float(score_match.group())
            if 0 <= score <= 100:
                risk_score = score
        except ValueError:
            pass
    
    return {
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        "summary": summary
    }

# Simple transaction analysis (fallback)
def analyze_transaction_simple(transaction_data):
    # This is a placeholder for the actual AI processing
    # In a real implementation, this would use more sophisticated analysis
    risk_score = 0.0
    risk_factors = []
    recommendations = []
    
    # Simple rule-based analysis
    amount = transaction_data.get('amount', 0)
    transaction_type = transaction_data.get('type', '').lower()
    description = transaction_data.get('description', '').lower()
    
    if amount > 10000:
        risk_score += 30
        risk_factors.append("High value transaction")
        recommendations.append("Verify source of funds")
    
    if 'cash' in transaction_type:
        risk_score += 20
        risk_factors.append("Cash transaction")
        recommendations.append("Review for structuring patterns")
    
    if 'suspicious' in description:
        risk_score += 25
        risk_factors.append("Suspicious keywords in description")
        recommendations.append("Enhanced due diligence required")
    
    summary = f"Transaction analyzed with {len(risk_factors)} identified risk factors."
    
    return {
        "risk_score": min(risk_score, 100.0),
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        "summary": summary
    }

# Upload CSV file and parse transactions
@app.post("/upload")
async def upload_transactions(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    if file.filename.endswith('.csv'):
        return await process_csv_file(file)
    elif file.filename.endswith('.pdf'):
        return await process_pdf_file(file)
    else:
        raise HTTPException(status_code=400, detail="Only CSV and PDF files are allowed")

async def process_csv_file(file: UploadFile):
    """Process CSV file and extract transactions"""
    try:
        # Read CSV file
        contents = await file.read()
        from io import StringIO
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = ['amount', 'date', 'type', 'description']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")
        
        # Process transactions
        transactions = []
        for _, row in df.iterrows():
            transaction_id = str(uuid.uuid4())
            transaction = {
                'id': transaction_id,
                'user_id': 'default_user',  # In a real implementation, this would come from auth
                'amount': float(row['amount']),
                'date': str(row['date']),
                'type': str(row['type']),
                'description': str(row['description']),
                'metadata': str(row['metadata']) if 'metadata' in row else None
            }
            
            # Insert into database
            cursor.execute('''
                INSERT INTO transactions (id, user_id, amount, date, type, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction['id'],
                transaction['user_id'],
                transaction['amount'],
                transaction['date'],
                transaction['type'],
                transaction['description'],
                transaction['metadata']
            ))
            
            transactions.append(transaction)
        
        conn.commit()
        return {"message": f"Successfully processed {len(transactions)} transactions from CSV", "transactions": transactions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV file: {str(e)}")

async def process_pdf_file(file: UploadFile):
    """Process PDF file and extract transactions"""
    if not PDF_PROCESSING_AVAILABLE or not PyPDF2:
        raise HTTPException(status_code=500, detail="PDF processing is not available. PyPDF2 library is not installed.")
    
    try:
        # Read PDF file
        contents = await file.read()
        from io import BytesIO
        pdf_reader = PyPDF2.PdfReader(BytesIO(contents))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        # Process PDF text to extract transactions
        result = data_processor.process_pdf_transactions(text)
        
        if result['success']:
            return {"message": result['message'], "statistics": result['statistics']}
        else:
            raise HTTPException(status_code=500, detail=result['message'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {str(e)}")

# Process existing data files
@app.post("/process-data-files")
async def process_data_files():
    """Process the existing data files in the data/raw directory"""
    try:
        results = []
        
        # Process Paysim data if available
        paysim_path = "/app/data/raw/raw/paysim1.csv"  # Updated path
        if os.path.exists(paysim_path):
            result = data_processor.process_paysim_data(paysim_path, limit=1000)  # Limit for demo
            results.append({"file": "paysim1.csv", "result": result})
        
        # Process ObliQA data if available
        obliqa_paths = [
            "/app/data/raw/raw/obliqa/ObliQA_dev.json",  # Updated path
            "/app/data/raw/raw/obliqa/ObliQA_test.json",  # Updated path
            "/app/data/raw/raw/obliqa/ObliQA_train.json"  # Updated path
        ]
        
        for path in obliqa_paths:
            if os.path.exists(path):
                result = data_processor.process_obliqa_data(path)
                results.append({"file": os.path.basename(path), "result": result})
        
        return {
            "message": "Data processing completed",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data files: {str(e)}")

# Analyze a transaction
@app.post("/analyze/{transaction_id}", response_model=TransactionAnalysisResponse)
async def analyze_transaction(transaction_id: str):
    try:
        # Get transaction from database
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Create transaction data from row
        transaction_data = {
            'id': row[0],
            'user_id': row[1],
            'amount': row[2],
            'date': row[3],
            'type': row[4],
            'description': row[5],
            'metadata': row[6]
        }
        
        # Analyze transaction using AI
        analysis = analyze_transaction_with_gemini(transaction_data)
        
        return TransactionAnalysisResponse(
            risk_score=analysis["risk_score"],
            risk_factors=analysis["risk_factors"],
            recommendations=analysis["recommendations"],
            summary=analysis["summary"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing transaction: {str(e)}")

# Get all transactions
@app.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions():
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    
    transactions = []
    for row in rows:
        transaction = TransactionResponse(
            id=row[0],
            user_id=row[1],
            amount=row[2],
            date=row[3],
            type=row[4],
            description=row[5],
            metadata=row[6]
        )
        transactions.append(transaction)
    
    return transactions

# Get transaction by ID
@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction = TransactionResponse(
        id=row[0],
        user_id=row[1],
        amount=row[2],
        date=row[3],
        type=row[4],
        description=row[5],
        metadata=row[6]
    )
    
    return transaction

# Add a single transaction
@app.post("/transactions", response_model=TransactionResponse)
async def add_transaction(transaction: Transaction):
    try:
        cursor.execute('''
            INSERT INTO transactions (id, user_id, amount, date, type, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction.id,
            transaction.user_id,
            transaction.amount,
            transaction.date,
            transaction.type,
            transaction.description,
            transaction.metadata
        ))
        
        conn.commit()
        return transaction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding transaction: {str(e)}")

# Update a transaction
@app.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: str, transaction: Transaction):
    try:
        cursor.execute('''
            UPDATE transactions 
            SET user_id = ?, amount = ?, date = ?, type = ?, description = ?, metadata = ?
            WHERE id = ?
        ''', (
            transaction.user_id,
            transaction.amount,
            transaction.date,
            transaction.type,
            transaction.description,
            transaction.metadata,
            transaction_id
        ))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating transaction: {str(e)}")

# Delete a transaction
@app.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    try:
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return {"message": "Transaction deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting transaction: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)