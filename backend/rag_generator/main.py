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

app = FastAPI(title="RAG Generator Service", version="1.0.0")

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Initialize the model
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
else:
    model = None
    print("Warning: GEMINI_API_KEY not set. AI features will be disabled.")

# Database setup for reports
REPORTS_DATABASE_URL = os.getenv("REPORTS_DATABASE_URL", "reports.db")
conn = sqlite3.connect(REPORTS_DATABASE_URL, check_same_thread=False)
cursor = conn.cursor()

# Create reports table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        content TEXT,
        generated_at TEXT
    )
''')
conn.commit()

class Report(BaseModel):
    id: str
    user_id: str
    content: str
    generated_at: str

class ReportResponse(BaseModel):
    id: str
    user_id: str
    content: str
    generated_at: str

class GenerateReportRequest(BaseModel):
    violations_data: List[dict]
    transactions_data: List[dict]
    policies_data: List[dict]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag_generator", "timestamp": datetime.utcnow()}

# Enhanced report generation function using Gemini API
def generate_report_with_gemini(violations_data, transactions_data, policies_data):
    if not model:
        # Fallback to template-based generation if Gemini is not available
        return generate_report_template(violations_data, transactions_data, policies_data)
    
    try:
        # Create a prompt for the AI to generate a comprehensive compliance report
        prompt = f"""
        Generate a comprehensive financial compliance report based on the following data:
        
        TRANSACTION DATA:
        {json.dumps(transactions_data, indent=2)}
        
        POLICY DATA:
        {json.dumps(policies_data, indent=2)}
        
        VIOLATIONS DETECTED:
        {json.dumps(violations_data, indent=2)}
        
        Please provide:
        1. An executive summary of the compliance analysis
        2. Key findings with risk categorization
        3. Detailed analysis of each violation
        4. Specific recommendations for addressing violations
        5. Overall compliance score (0-100)
        6. Actionable insights for improving compliance
        
        Format the response as a professional compliance report with clear sections and actionable insights.
        """
        
        # Generate content using Gemini
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        print(f"Error generating report with Gemini: {str(e)}")
        # Fallback to template-based generation
        return generate_report_template(violations_data, transactions_data, policies_data)

# Template-based report generation (fallback)
def generate_report_template(violations_data, transactions_data, policies_data):
    report_content = f"""
# Compliance Report

## Executive Summary

This report summarizes the compliance analysis performed on {len(transactions_data)} transactions against {len(policies_data)} regulatory policies.

## Key Findings

- Total violations detected: {len(violations_data)}
- High-risk violations: {len([v for v in violations_data if v.get('risk_level') == 'high'])}
- Medium-risk violations: {len([v for v in violations_data if v.get('risk_level') == 'medium'])}
- Low-risk violations: {len([v for v in violations_data if v.get('risk_level') == 'low'])}

## Detailed Violations

"""
    
    for violation in violations_data:
        report_content += f"""
### Violation ID: {violation.get('id', 'N/A')}
- Transaction ID: {violation.get('transaction_id', 'N/A')}
- Policy: {violation.get('policy_id', 'N/A')}
- Risk Level: {violation.get('risk_level', 'N/A')}
- Description: {violation.get('description', 'N/A')}
- Recommendation: {violation.get('recommendation', 'N/A')}
"""
    
    report_content += f"""

## Recommendations

Based on the analysis, we recommend the following actions:
1. Review all high-risk violations immediately
2. Implement enhanced monitoring for similar transactions
3. Update policies as needed to address identified gaps
4. Provide additional training to staff on compliance procedures

Report generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
    
    return report_content

# Generate compliance report
@app.post("/generate")
async def generate_compliance_report(request: GenerateReportRequest):
    try:
        # Generate report using AI-enhanced RAG
        report_content = generate_report_with_gemini(
            request.violations_data,
            request.transactions_data,
            request.policies_data
        )
        
        # Save report to database
        report_id = str(uuid.uuid4())
        user_id = "default_user"  # In a real implementation, this would come from auth
        generated_at = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT INTO reports (id, user_id, content, generated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            report_id,
            user_id,
            report_content,
            generated_at
        ))
        
        conn.commit()
        
        return {
            "message": "Report generated successfully",
            "report_id": report_id,
            "content": report_content
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

# Get all reports
@app.get("/reports", response_model=List[ReportResponse])
async def get_reports():
    cursor.execute("SELECT * FROM reports")
    rows = cursor.fetchall()
    
    reports = []
    for row in rows:
        report = ReportResponse(
            id=row[0],
            user_id=row[1],
            content=row[2],
            generated_at=row[3]
        )
        reports.append(report)
    
    return reports

# Get report by ID
@app.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = ReportResponse(
        id=row[0],
        user_id=row[1],
        content=row[2],
        generated_at=row[3]
    )
    
    return report

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)