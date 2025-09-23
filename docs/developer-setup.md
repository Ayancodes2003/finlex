# Developer Setup Guide

## Prerequisites

Before setting up the development environment, ensure you have the following installed:

- Docker and Docker Compose
- Python 3.9 or higher
- Node.js and npm (for frontend development)
- Git

## Project Structure

```
finlex/
├── backend/
│   ├── api_gateway/
│   ├── transaction_ingest/
│   ├── policy_extractor/
│   ├── compliance_matcher/
│   ├── rag_generator/
│   └── vector_db/
├── frontend/
├── docs/
├── init-scripts/
├── docker-compose.yml
└── nginx.conf
```

## Setting Up the Development Environment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd finlex
```

### 2. Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# API Gateway
SECRET_KEY=your_secret_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=postgresql://finlex_user:finlex_password@localhost:5432/finlex
REDIS_URL=redis://localhost:6379/0

# Service URLs
TRANSACTION_SERVICE_URL=http://localhost:8001
POLICY_SERVICE_URL=http://localhost:8002
COMPLIANCE_SERVICE_URL=http://localhost:8003
RAG_SERVICE_URL=http://localhost:8004
```

### 3. Start Services with Docker Compose

```bash
docker-compose up --build
```

This will start all services:
- API Gateway: http://localhost:8000
- Transaction Ingest: http://localhost:8001
- Policy Extractor: http://localhost:8002
- Compliance Matcher: http://localhost:8003
- RAG Generator: http://localhost:8004
- Vector Database: http://localhost:8010
- Redis: http://localhost:6379
- PostgreSQL: http://localhost:5432
- Frontend: http://localhost:3000

### 4. Access the Application

Open your browser and navigate to http://localhost:3000

## Working with Individual Services

### Running Services Locally

To run a service locally for development:

1. Navigate to the service directory:
   ```bash
   cd backend/api_gateway
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the service:
   ```bash
   python main.py
   ```

### Service Ports

- API Gateway: 8000
- Transaction Ingest: 8001
- Policy Extractor: 8002
- Compliance Matcher: 8003
- RAG Generator: 8004
- Vector Database: 8010

## Database Setup

### PostgreSQL

The application uses PostgreSQL for persistent storage. When running with Docker Compose, the database is automatically initialized with the schema from `init-scripts/init.sql`.

To connect to the database directly:
```bash
docker-compose exec postgres psql -U finlex_user -d finlex
```

### Redis

Redis is used for caching and session management. To connect to Redis:
```bash
docker-compose exec redis redis-cli
```

## Testing

### Unit Tests

Each service includes unit tests. To run tests for a service:

1. Navigate to the service directory
2. Activate the virtual environment
3. Run tests:
   ```bash
   python -m pytest tests/
   ```

### Integration Tests

Integration tests verify service interactions. To run integration tests:

```bash
docker-compose -f docker-compose.test.yml up --build
```

## Code Quality

### Linting

All Python code follows PEP8 standards. To lint the code:

```bash
flake8 .
```

### Formatting

Code is formatted using Black:

```bash
black .
```

## API Documentation

API documentation is available through Swagger UI when running the services:

- API Gateway: http://localhost:8000/docs
- Transaction Ingest: http://localhost:8001/docs
- Policy Extractor: http://localhost:8002/docs
- Compliance Matcher: http://localhost:8003/docs
- RAG Generator: http://localhost:8004/docs
- Vector Database: http://localhost:8010/docs

## Contributing

### Branching Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `hotfix/*` - Hotfix branches

### Commit Messages

Follow conventional commit messages:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

### Pull Requests

1. Create a feature branch from `develop`
2. Make your changes
3. Write tests if applicable
4. Update documentation if needed
5. Create a pull request to `develop`

## Deployment

### Production Deployment

For production deployment, refer to the [Deployment Guide](deployment.md).

## Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker logs:
   ```bash
   docker-compose logs <service-name>
   ```

2. **Database connection issues**: Verify environment variables and database status

3. **Port conflicts**: Ensure required ports are available

### Getting Help

For issues not covered in this guide, consult:
- Team members
- Project documentation
- Online resources for the technologies used