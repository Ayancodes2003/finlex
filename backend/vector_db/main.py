from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime
import uvicorn
import numpy as np

# FAISS import with error handling
FAISS_AVAILABLE = False
faiss = None
try:
    import importlib
    faiss = importlib.import_module('faiss')
    FAISS_AVAILABLE = True
except ImportError:
    print("FAISS not available, using fallback implementation")

import google.generativeai as genai

app = FastAPI(title="Vector Database Service", version="1.0.0")

# Configure Gemini API for embeddings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Initialize the embedding model
    try:
        embedding_model = genai.embed_content
    except AttributeError:
        # Fallback for older versions
        embedding_model = None
else:
    embedding_model = None
    print("Warning: GEMINI_API_KEY not set. AI embeddings will be disabled.")

# In-memory storage for embeddings (in a real implementation, this would be FAISS)
embeddings_store = {}

class EmbeddingRequest(BaseModel):
    id: str
    text: str
    metadata: Optional[dict] = None

class SimilarityRequest(BaseModel):
    text: str
    k: int = 5  # Number of similar items to return

class SimilarityResponse(BaseModel):
    id: str
    similarity: float
    metadata: Optional[dict] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vector_db", "timestamp": datetime.utcnow()}

# Generate embeddings using Gemini
def generate_embeddings_with_gemini(text: str):
    if not embedding_model or not GEMINI_API_KEY:
        # Fallback to simple embedding generation
        return generate_simple_embeddings(text)
    
    try:
        # Generate embeddings using Gemini
        result = genai.embed_content(model="models/embedding-001", content=text)
        return result['embedding']
    except Exception as e:
        print(f"Error generating embeddings with Gemini: {str(e)}")
        # Fallback to simple embedding generation
        return generate_simple_embeddings(text)

# Simple embedding generation (fallback)
def generate_simple_embeddings(text: str):
    # This is a simple fallback that creates a fixed-size vector
    # In a real implementation, you would use a proper embedding model
    np.random.seed(hash(text) % (2**32))  # Seed based on text for consistency
    return np.random.rand(768).tolist()  # 768-dimensional vector (similar to many embedding models)

# Store an embedding
@app.post("/embeddings")
async def store_embedding(request: EmbeddingRequest):
    try:
        # Generate embeddings using AI
        vector = generate_embeddings_with_gemini(request.text)
        
        # In a real implementation with FAISS:
        # 1. Add the vector to the FAISS index
        # 2. Store metadata in a separate database
        
        # For this example, we'll store in memory
        embeddings_store[request.id] = {
            "vector": vector,
            "text": request.text,
            "metadata": request.metadata,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {"message": "Embedding stored successfully", "id": request.id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing embedding: {str(e)}")

# Get an embedding by ID
@app.get("/embeddings/{embedding_id}")
async def get_embedding(embedding_id: str):
    if embedding_id not in embeddings_store:
        raise HTTPException(status_code=404, detail="Embedding not found")
    
    return embeddings_store[embedding_id]

# Find similar embeddings
@app.post("/similarity", response_model=List[SimilarityResponse])
async def find_similar_embeddings(request: SimilarityRequest):
    try:
        if not embeddings_store:
            return []
        
        # Generate embedding for the query text
        query_vector = np.array(generate_embeddings_with_gemini(request.text))
        
        # Calculate similarities (cosine similarity)
        similarities = []
        for id, data in embeddings_store.items():
            stored_vector = np.array(data["vector"])
            
            # Calculate cosine similarity
            dot_product = np.dot(query_vector, stored_vector)
            norm_query = np.linalg.norm(query_vector)
            norm_stored = np.linalg.norm(stored_vector)
            
            if norm_query == 0 or norm_stored == 0:
                similarity = 0
            else:
                similarity = dot_product / (norm_query * norm_stored)
            
            similarities.append({
                "id": id,
                "similarity": float(similarity),
                "metadata": data.get("metadata")
            })
        
        # Sort by similarity (descending) and return top k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:request.k]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar embeddings: {str(e)}")

# Delete an embedding
@app.delete("/embeddings/{embedding_id}")
async def delete_embedding(embedding_id: str):
    if embedding_id not in embeddings_store:
        raise HTTPException(status_code=404, detail="Embedding not found")
    
    del embeddings_store[embedding_id]
    return {"message": "Embedding deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)