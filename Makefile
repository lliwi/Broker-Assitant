.PHONY: help build up down restart logs shell test migrate format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker containers
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "Application started at http://localhost:5000"

down: ## Stop all services
	docker-compose down

restart: down up ## Restart all services

logs: ## Show logs (use 'make logs service=app' for specific service)
	@if [ -z "$(service)" ]; then \
		docker-compose logs -f; \
	else \
		docker-compose logs -f $(service); \
	fi

shell: ## Open shell in app container
	docker-compose exec app /bin/bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U insightflow -d insightflow

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

test: ## Run tests
	docker-compose exec app pytest -v --cov=app tests/

migrate: ## Create database migration
	docker-compose exec app flask db migrate -m "$(msg)"

upgrade: ## Apply database migrations
	docker-compose exec app flask db upgrade

format: ## Format code with black
	docker-compose exec app black app/ tests/

lint: ## Run linting
	docker-compose exec app flake8 app/ tests/

clean: ## Remove containers, volumes, and cache
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

init: ## Initialize application (first time setup)
	@echo "Creating .env file from example..."
	@cp -n .env.example .env || true
	@echo "Building containers..."
	@make build
	@echo "Starting services..."
	@make up
	@echo "Waiting for database..."
	@sleep 10
	@echo "Running migrations..."
	@docker-compose exec app flask db upgrade
	@echo ""
	@echo "Setup complete! Application running at http://localhost:5000"
	@echo "Don't forget to add your API keys to .env file"

dev: ## Start in development mode with live reload
	docker-compose up

stats: ## Show container stats
	docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
