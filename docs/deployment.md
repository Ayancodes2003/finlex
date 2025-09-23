# Deployment Guide

## Overview

This guide provides instructions for deploying the FinLex financial compliance auditing platform in various environments.

## Prerequisites

- Docker and Docker Compose installed on the target system
- At least 8GB RAM and 20GB free disk space
- Internet access for pulling Docker images
- Domain name (for production deployment)

## Environment Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Security
SECRET_KEY=your_production_secret_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=postgresql://finlex_user:finlex_password@postgres:5432/finlex
REDIS_URL=redis://redis:6379/0

# Service URLs
API_BASE_URL=https://your-domain.com/api
TRANSACTION_SERVICE_URL=http://transaction-ingest:8001
POLICY_SERVICE_URL=http://policy-extractor:8002
COMPLIANCE_SERVICE_URL=http://compliance-matcher:8003
RAG_SERVICE_URL=http://rag-generator:8004

# HTTPS (for production)
SSL_CERTIFICATE=/etc/ssl/certs/your_cert.pem
SSL_CERTIFICATE_KEY=/etc/ssl/private/your_key.pem
```

## Development Deployment

For local development and testing:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd finlex
   ```

2. Start services:
   ```bash
   docker-compose up --build
   ```

3. Access the application at http://localhost:3000

## Production Deployment

### 1. Server Setup

Provision a server with:
- Ubuntu 20.04 LTS or newer
- Docker and Docker Compose installed
- Firewall configured to allow ports 80 and 443

### 2. SSL Certificate

Obtain an SSL certificate using Let's Encrypt:

```bash
sudo apt-get update
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com
```

### 3. Configuration

1. Copy the repository to the server:
   ```bash
   scp -r finlex user@your-server:/opt/finlex
   ```

2. Update the `.env` file with production values

3. Modify `docker-compose.yml` for production:
   - Remove port mappings for internal services
   - Add SSL configuration for Nginx
   - Configure resource limits

### 4. Start Services

```bash
cd /opt/finlex
docker-compose up -d --build
```

### 5. Verify Deployment

Check service status:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f
```

Access the application at https://your-domain.com

## Kubernetes Deployment (Optional)

For large-scale deployments, you can use Kubernetes:

### 1. Create Kubernetes Manifests

Create YAML files for each service:

```yaml
# api-gateway-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: your-registry/finlex-api-gateway:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: finlex-config
```

### 2. Deploy to Kubernetes

```bash
kubectl apply -f k8s-manifests/
```

## Monitoring and Logging

### Centralized Logging

All services output logs to stdout/stderr, which Docker captures. For centralized logging:

1. Configure Docker logging driver:
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

2. Use ELK stack or similar for log aggregation

### Health Checks

Each service exposes a `/health` endpoint for monitoring:

- API Gateway: http://localhost:8000/health
- Transaction Ingest: http://localhost:8001/health
- Policy Extractor: http://localhost:8002/health
- Compliance Matcher: http://localhost:8003/health
- RAG Generator: http://localhost:8004/health
- Vector Database: http://localhost:8010/health

### Performance Monitoring

Monitor key metrics:
- Response times
- Error rates
- Resource utilization (CPU, memory, disk)
- Database performance

## Backup and Recovery

### Database Backup

PostgreSQL data is persisted in a Docker volume. To backup:

```bash
docker-compose exec postgres pg_dump -U finlex_user finlex > backup.sql
```

### Restore Database

```bash
docker-compose exec -T postgres psql -U finlex_user finlex < backup.sql
```

### Configuration Backup

Regularly backup:
- `.env` file
- `docker-compose.yml`
- SSL certificates
- Custom configurations

## Scaling

### Horizontal Scaling

Most services can be scaled horizontally:

```bash
docker-compose up -d --scale api-gateway=3
```

### Resource Limits

Configure resource limits in `docker-compose.yml`:

```yaml
services:
  api-gateway:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Security Considerations

### Network Security

- Use internal Docker networks
- Restrict external access to necessary ports only
- Implement firewall rules

### Data Security

- Encrypt data in transit with HTTPS
- Encrypt sensitive data at rest
- Regularly update dependencies

### Access Control

- Use strong authentication
- Implement role-based access control
- Regularly rotate secrets

## Maintenance

### Updates

To update the application:

1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart services:
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

### Monitoring

Regularly check:
- Service health
- Disk space
- Memory usage
- Log files for errors

## Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker logs and resource limits
2. **Database connection failures**: Verify database credentials and network connectivity
3. **Performance issues**: Monitor resource usage and scale as needed
4. **SSL certificate errors**: Verify certificate paths and permissions

### Support

For issues not covered in this guide, consult:
- Docker documentation
- Kubernetes documentation (if applicable)
- Community forums for the technologies used