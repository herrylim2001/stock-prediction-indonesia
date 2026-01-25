.PHONY: help dev dev-db backend frontend build docker-up docker-down clean

# Default target
help:
	@echo "Whitelabel Streaming Platform - Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start all services for development"
	@echo "  make dev-db       - Start only database services (postgres, redis)"
	@echo "  make backend      - Run backend in development mode"
	@echo "  make frontend     - Run frontend in development mode"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start all services with Docker"
	@echo "  make docker-down  - Stop all Docker services"
	@echo "  make docker-build - Build Docker images"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make migrate      - Run database migrations"

# Development
dev-db:
	docker-compose -f docker-compose.dev.yml up -d postgres redis
	@echo "Database services started. PostgreSQL: localhost:5432, Redis: localhost:6379"

backend:
	cd backend && go run ./cmd/api

frontend:
	cd frontend && npm run dev

dev: dev-db
	@echo "Starting backend and frontend..."
	@make -j2 backend frontend

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database
migrate:
	cd backend && go run ./cmd/api migrate

# Utilities
clean:
	rm -rf backend/main
	rm -rf frontend/.next
	rm -rf frontend/node_modules

# Install dependencies
install:
	cd backend && go mod download
	cd frontend && npm install

# Format code
fmt:
	cd backend && go fmt ./...
	cd frontend && npm run lint -- --fix

# Run tests
test:
	cd backend && go test ./...
	cd frontend && npm test
