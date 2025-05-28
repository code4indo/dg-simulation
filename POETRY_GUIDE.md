# Poetry Installation and Usage Guide

## Installation

### 1. Install Poetry
```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -

# Alternative: via pip
pip install poetry
```

### 2. Verify Installation
```bash
poetry --version
```

## Project Setup

### 1. Install Dependencies
```bash
# Install all dependencies
poetry install

# Install only production dependencies
poetry install --no-dev

# Install with specific groups
poetry install --with dev,test
```

### 2. Activate Virtual Environment
```bash
# Activate shell
poetry shell

# Or run commands in environment
poetry run python metadata_curator_agent.py
poetry run streamlit run metadata_curator_agent.py
```

## Dependency Management

### Adding Dependencies
```bash
# Add production dependency
poetry add streamlit

# Add development dependency
poetry add --group dev pytest

# Add optional dependency
poetry add --optional jupyter
```

### Updating Dependencies
```bash
# Update all dependencies
poetry update

# Update specific package
poetry update streamlit

# Show outdated packages
poetry show --outdated
```

### Removing Dependencies
```bash
# Remove package
poetry remove package-name

# Remove from specific group
poetry remove --group dev pytest
```

## Development Commands

### Running the Application
```bash
# Basic version
poetry run streamlit run metadata_curator_agent.py

# Enhanced version
poetry run streamlit run enhanced_app.py

# Using script aliases
poetry run metadata-curator
poetry run enhanced-curator
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=metadata_curator_agent

# Run specific test file
poetry run pytest tests/test_metadata.py

# Run with markers
poetry run pytest -m "not slow"
```

### Code Quality
```bash
# Format code with Black
poetry run black .

# Lint with flake8
poetry run flake8

# Type checking with mypy
poetry run mypy .

# Run pre-commit hooks
poetry run pre-commit run --all-files
```

### Documentation
```bash
# Build documentation
poetry run mkdocs build

# Serve documentation locally
poetry run mkdocs serve
```

## Virtual Environment Management

### Environment Information
```bash
# Show environment info
poetry env info

# List environments
poetry env list

# Show path to environment
poetry env info --path
```

### Environment Operations
```bash
# Remove environment
poetry env remove python3.9

# Use specific Python version
poetry env use python3.9

# Use system Python
poetry env use system
```

## Building and Publishing

### Build Package
```bash
# Build distribution packages
poetry build

# Build only wheel
poetry build --format wheel

# Build only sdist
poetry build --format sdist
```

### Configuration
```bash
# Show configuration
poetry config --list

# Set PyPI credentials
poetry config pypi-token.pypi your-token

# Set custom repository
poetry config repositories.custom-repo https://custom.repo.com/simple/
```

## Lock File Management

### Working with poetry.lock
```bash
# Generate lock file
poetry lock

# Update lock file without installing
poetry lock --no-update

# Install from lock file
poetry install
```

### Export Requirements
```bash
# Export to requirements.txt
poetry export -f requirements.txt --output requirements.txt

# Export with development dependencies
poetry export -f requirements.txt --output requirements-dev.txt --with dev

# Export without hashes
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Useful Commands

### Check Project
```bash
# Check pyproject.toml validity
poetry check

# Show dependency tree
poetry show --tree

# Show specific package info
poetry show streamlit
```

### Scripts and Aliases
```bash
# Add custom scripts to pyproject.toml
[tool.poetry.scripts]
start = "metadata_curator_agent:main"
test = "pytest"
lint = "flake8"
```

## Best Practices

1. **Always use poetry.lock**: Commit the lock file for reproducible builds
2. **Group dependencies**: Use dependency groups for organization
3. **Pin versions**: Use caret constraints (^1.0.0) for flexibility
4. **Regular updates**: Keep dependencies updated for security
5. **Development setup**: Use pre-commit hooks for code quality

## Troubleshooting

### Common Issues
```bash
# Clear Poetry cache
poetry cache clear --all pypi

# Reset virtual environment
poetry env remove python
poetry install

# Fix SSL issues
poetry config certificates.custom-ca-bundle-path /path/to/certificate.pem

# Use system certificates
poetry config certificates.custom-ca-bundle-path false
```

### Environment Variables
```bash
# Set Poetry home directory
export POETRY_HOME=/custom/poetry/path

# Set virtual environment in project
export POETRY_VENV_IN_PROJECT=1

# Set custom cache directory
export POETRY_CACHE_DIR=/custom/cache/path
```
