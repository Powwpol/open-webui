.PHONY: help build build-gpu build-slim up down logs clean prune test

# Pulsai Makefile
# Quick commands for Docker operations

help: ## Show this help message
	@echo "Pulsai Docker Commands"
	@echo "======================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Build commands
build: ## Build Pulsai images (CPU)
	./build-pulsai.sh --tag latest

build-gpu: ## Build Pulsai images with GPU support
	./build-pulsai.sh --cuda --tag latest

build-slim: ## Build slim version (no embedding models)
	./build-pulsai.sh --slim --tag latest

build-clean: ## Build without cache (clean build)
	./build-pulsai.sh --no-cache --tag latest

# Docker Compose commands
up: ## Start all services
	docker-compose -f docker-compose.pulsai.yaml up -d

down: ## Stop all services
	docker-compose -f docker-compose.pulsai.yaml down

restart: ## Restart all services
	docker-compose -f docker-compose.pulsai.yaml restart

logs: ## View logs (all services)
	docker-compose -f docker-compose.pulsai.yaml logs -f

logs-backend: ## View backend logs
	docker-compose -f docker-compose.pulsai.yaml logs -f pulsai-backend

logs-mcp: ## View MCP server logs
	docker-compose -f docker-compose.pulsai.yaml logs -f pulsai-mcp

# Service management
start-backend: ## Start only backend service
	docker-compose -f docker-compose.pulsai.yaml up -d pulsai-backend

start-mcp: ## Start only MCP server
	docker-compose -f docker-compose.pulsai.yaml up -d pulsai-mcp

stop-backend: ## Stop backend service
	docker-compose -f docker-compose.pulsai.yaml stop pulsai-backend

stop-mcp: ## Stop MCP server
	docker-compose -f docker-compose.pulsai.yaml stop pulsai-mcp

# Health checks
health: ## Check health of all services
	@echo "Backend:"; curl -s http://localhost:8080/health | jq || echo "❌ Backend not responding"
	@echo "MCP:"; curl -s http://localhost:8001/health | jq || echo "❌ MCP not responding"
	@echo "Redis:"; docker-compose -f docker-compose.pulsai.yaml exec -T pulsai-redis redis-cli ping || echo "❌ Redis not responding"

# Cleanup commands
clean: ## Stop services and remove containers
	docker-compose -f docker-compose.pulsai.yaml down

clean-volumes: ## Stop services and remove volumes (⚠️ deletes data)
	docker-compose -f docker-compose.pulsai.yaml down -v

prune: ## Remove unused Docker resources
	docker system prune -f

prune-all: ## Remove all unused Docker resources (⚠️ including images)
	docker system prune -af

# Development commands
dev-backend: ## Run backend in development mode
	cd backend && bash start.sh

dev-frontend: ## Run frontend in development mode
	npm run dev

# Database commands
db-migrate: ## Run database migrations
	docker-compose -f docker-compose.pulsai.yaml exec pulsai-backend bash -c "cd /app/backend && alembic upgrade head"

db-shell: ## Open database shell
	docker-compose -f docker-compose.pulsai.yaml exec pulsai-backend sqlite3 /app/backend/data/webui.db

# Backup commands
backup: ## Backup Pulsai data
	@mkdir -p backups
	@echo "Backing up data..."
	docker run --rm -v pulsai-data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/pulsai-data-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "✓ Backup complete: backups/pulsai-data-$(shell date +%Y%m%d-%H%M%S).tar.gz"

restore: ## Restore Pulsai data (usage: make restore FILE=backup.tar.gz)
	@if [ -z "$(FILE)" ]; then echo "Usage: make restore FILE=backup.tar.gz"; exit 1; fi
	@echo "⚠️  This will overwrite current data. Press Ctrl+C to cancel, Enter to continue..."; read
	docker run --rm -v pulsai-data:/data -v $(PWD)/backups:/backup alpine tar xzf /backup/$(FILE) -C /data
	@echo "✓ Restore complete"

# Ollama commands
ollama-pull: ## Pull Ollama model (usage: make ollama-pull MODEL=llama2)
	@if [ -z "$(MODEL)" ]; then echo "Usage: make ollama-pull MODEL=llama2"; exit 1; fi
	docker-compose -f docker-compose.pulsai.yaml exec pulsai-ollama ollama pull $(MODEL)

ollama-list: ## List Ollama models
	docker-compose -f docker-compose.pulsai.yaml exec pulsai-ollama ollama list

# Testing
test: ## Run tests
	@echo "Running tests..."
	docker-compose -f docker-compose.pulsai.yaml exec pulsai-backend pytest
	@echo "✓ Tests complete"

# Status
status: ## Show status of all services
	docker-compose -f docker-compose.pulsai.yaml ps

stats: ## Show resource usage
	docker stats

# Quick start
quickstart: build up logs ## Build, start, and show logs

# Update
update: ## Pull latest changes and rebuild
	git pull
	./build-pulsai.sh --tag latest
	docker-compose -f docker-compose.pulsai.yaml up -d
	@echo "✓ Update complete"
