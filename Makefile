# Makefile untuk Metadata Curator Agent

.PHONY: help install dev-install test lint format type-check docs clean run-basic run-enhanced

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies with Poetry"
	@echo "  dev-install  - Install with development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  type-check   - Run type checking"
	@echo "  docs         - Build documentation"
	@echo "  clean        - Clean cache and build artifacts"
	@echo "  run-basic    - Run basic version"
	@echo "  run-enhanced - Run enhanced version"

# Installation
install:
	poetry install --no-dev

dev-install:
	poetry install
	poetry run pre-commit install

# Testing
test:
	poetry run pytest --cov=metadata_curator_agent --cov-report=html --cov-report=term

test-fast:
	poetry run pytest -x -v

# Code quality
lint:
	poetry run flake8 .
	poetry run bandit -r . -f json -o bandit-report.json || true

format:
	poetry run black .
	poetry run isort .

type-check:
	poetry run mypy .

# Documentation
docs:
	poetry run mkdocs build

docs-serve:
	poetry run mkdocs serve

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/

# Running applications
run-basic:
	poetry run streamlit run metadata_curator_agent.py

run-enhanced:
	poetry run streamlit run enhanced_app.py

# Development workflow
dev-setup: dev-install
	mkdir -p data exports logs tests
	cp .env.example .env 2>/dev/null || true

# CI/CD targets
ci-test: dev-install
	poetry run pytest --cov=metadata_curator_agent --cov-report=xml

ci-lint: dev-install
	poetry run black --check .
	poetry run flake8 .
	poetry run mypy .

# Update dependencies
update:
	poetry update
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# Build package
build:
	poetry build

# Security check
security:
	poetry run bandit -r . -f json -o bandit-report.json
	poetry run safety check

# All quality checks
check-all: format lint type-check test

# Development commands
dev: dev-setup
	@echo "Development environment ready!"
	@echo "Run 'make run-basic' or 'make run-enhanced' to start the application"
