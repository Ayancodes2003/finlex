# FinLex API Documentation

## Overview

FinLex provides a comprehensive RESTful API for financial compliance auditing. The API is organized around microservices, each responsible for a specific domain of functionality.

## Base URL

All URLs referenced in the documentation have the following base:

```
http://localhost:8000/api
```

## Authentication

All API requests require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

To obtain a token, use the login endpoint:

```
POST /auth/login
```

## API Services

### 1. API Gateway Service (Port 8000)

Central routing service for all client requests.

#### Authentication Endpoints

- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

#### Proxy Endpoints

- `GET /transactions` - Get all transactions
- `POST /transactions` - Add a new transaction
- `GET /transactions/{id}` - Get a specific transaction
- `PUT /transactions/{id}` - Update a transaction
- `DELETE /transactions/{id}` - Delete a transaction

- `GET /policies` - Get all policies
- `POST /policies` - Add a new policy
- `GET /policies/{id}` - Get a specific policy
- `PUT /policies/{id}` - Update a policy
- `DELETE /policies/{id}` - Delete a policy

- `POST /compliance/scan` - Run compliance scan
- `GET /compliance/violations` - Get compliance violations

- `POST /reports/generate` - Generate compliance report
- `GET /reports` - Get all reports
- `GET /reports/{id}` - Get a specific report

### 2. Transaction Ingest Service (Port 8001)

Handles CSV parsing and transaction data management.

#### Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload CSV transaction data
- `GET /transactions` - Get all transactions
- `GET /transactions/{id}` - Get a specific transaction
- `POST /transactions` - Add a new transaction

### 3. Policy Extractor Service (Port 8002)

Manages policy documents and requirement extraction.

#### Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload policy document
- `GET /policies` - Get all policies
- `GET /policies/{id}` - Get a specific policy
- `POST /policies` - Add a new policy

### 4. Compliance Matcher Service (Port 8003)

Compares transactions against policy requirements.

#### Endpoints

- `GET /health` - Health check
- `POST /scan` - Run compliance scan
- `GET /violations` - Get all violations
- `GET /violations/{id}` - Get a specific violation
- `GET /violations/transaction/{transaction_id}` - Get violations for a transaction

### 5. RAG Generator Service (Port 8004)

Generates compliance reports using Retrieval-Augmented Generation.

#### Endpoints

- `GET /health` - Health check
- `POST /generate` - Generate compliance report
- `GET /reports` - Get all reports
- `GET /reports/{id}` - Get a specific report

### 6. Vector Database Service (Port 8010)

FAISS-based similarity search for policy requirements.

#### Endpoints

- `GET /health` - Health check
- `POST /embeddings` - Store an embedding
- `GET /embeddings/{id}` - Get an embedding
- `POST /similarity` - Find similar embeddings
- `DELETE /embeddings/{id}` - Delete an embedding

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a JSON object with an error message:

```json
{
  "detail": "Error description"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

## Versioning

The API is versioned through the URL path. Currently, version 1.0 is available.