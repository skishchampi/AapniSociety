# AapniSociety — developer commands
# Monorepo: backend/ (Django 5 + DRF), frontend/ (React + Vite PWA)

.DEFAULT_GOAL := help
BACKEND := backend
FRONTEND := frontend

.PHONY: help hooks up down migrate makemigrations seed test lint fmt install \
        backend-install backend-migrate backend-seed backend-test backend-lint \
        frontend-install frontend-test frontend-lint

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

hooks: ## Install the git pre-commit hook
	@cp scripts/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "pre-commit hook installed"

# ── Backend ────────────────────────────────────────────
backend-install: ## Install backend deps (uv)
	cd $(BACKEND) && uv sync

backend-migrate: ## Run backend migrations
	cd $(BACKEND) && uv run python manage.py migrate

makemigrations: ## Create new migrations
	cd $(BACKEND) && uv run python manage.py makemigrations

backend-seed: ## Seed development data
	cd $(BACKEND) && uv run python manage.py seed_dev

backend-test: ## Run backend tests
	cd $(BACKEND) && uv run pytest

backend-lint: ## Lint backend (ruff)
	cd $(BACKEND) && uv run ruff check .

# ── Frontend ───────────────────────────────────────────
frontend-install: ## Install frontend deps
	cd $(FRONTEND) && npm install

frontend-test: ## Run frontend tests
	cd $(FRONTEND) && npm run test -- --run

frontend-lint: ## Lint frontend
	cd $(FRONTEND) && npm run lint

# ── Aggregate ──────────────────────────────────────────
migrate: backend-migrate ## Run all migrations
seed: backend-seed ## Seed all dev data
test: backend-test frontend-test ## Run all test suites
lint: backend-lint frontend-lint ## Lint everything
install: backend-install frontend-install ## Install all deps

up: ## Start the local docker-compose stack
	docker compose -f infra/docker-compose.yml up --build

down: ## Stop the local docker-compose stack
	docker compose -f infra/docker-compose.yml down
