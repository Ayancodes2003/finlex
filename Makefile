# Makefile for FinLex development tasks

# Variables
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = finlex

# Default target
.PHONY: help
help:
	@echo "FinLex Development Commands"
	@echo "=========================="
	@echo "help            - Show this help message"
	@echo "setup           - Set up the development environment"
	@echo "start           - Start all services"
	@echo "stop            - Stop all services"
	@echo "restart         - Restart all services"
	@echo "logs            - View service logs"
	@echo "test            - Run all tests"
	@echo "test-api-gateway - Run API Gateway tests"
	@echo "test-transaction - Run Transaction Ingest tests"
	@echo "clean           - Remove all containers and volumes"
	@echo "build           - Build all Docker images"
	@echo "docs            - Generate documentation"

# Setup development environment
.PHONY: setup
setup:
	pip install -r requirements.txt
	docker-compose pull

# Start all services
.PHONY: start
start:
	docker-compose up -d

# Stop all services
.PHONY: stop
stop:
	docker-compose down

# Restart all services
.PHONY: restart
restart:
	docker-compose down
	docker-compose up -d

# View service logs
.PHONY: logs
logs:
	docker-compose logs -f

# Run all tests
.PHONY: test
test:
	docker-compose exec api-gateway pytest
	docker-compose exec transaction-ingest pytest

# Run API Gateway tests
.PHONY: test-api-gateway
test-api-gateway:
	docker-compose exec api-gateway pytest

# Run Transaction Ingest tests
.PHONY: test-transaction
test-transaction:
	docker-compose exec transaction-ingest pytest

# Remove all containers and volumes
.PHONY: clean
clean:
	docker-compose down -v --remove-orphans

# Build all Docker images
.PHONY: build
build:
	docker-compose build

# Generate documentation
.PHONY: docs
docs:
	@echo "Documentation is available in the docs/ directory"
	@echo "API documentation: docs/api.md"
	@echo "User guide: docs/user-guide.md"
	@echo "Developer setup: docs/developer-setup.md"
	@echo "Deployment guide: docs/deployment.md"

# Verify setup
.PHONY: verify
verify:
	python test_setup.py