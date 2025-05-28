#!/bin/bash

echo "Setting up Poetry for Metadata Curator Agent..."
echo

echo "Checking if Poetry is installed..."
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing Poetry..."
    echo
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    echo "Adding Poetry to PATH..."
    export PATH="$HOME/.local/bin:$PATH"
    
    echo "Please restart your shell or run: source ~/.bashrc"
    echo "Then run this script again."
    exit 1
fi

echo "Poetry found! Setting up project..."
echo

echo "Installing dependencies with Poetry..."
poetry install

echo
echo "Setting up pre-commit hooks..."
poetry run pre-commit install

echo
echo "Creating project directories..."
mkdir -p data exports logs tests

echo
echo "Creating environment file..."
if [ ! -f ".env" ]; then
    cp ".env.example" ".env"
fi

echo
echo "Poetry setup complete!"
echo
echo "Available commands:"
echo "  poetry run streamlit run metadata_curator_agent.py"
echo "  poetry run streamlit run enhanced_app.py"
echo "  poetry run pytest (for testing)"
echo "  poetry run black . (for code formatting)"
echo "  poetry run flake8 (for linting)"
echo
echo "Don't forget to:"
echo "1. Get your Gemini API key from https://makersuite.google.com/app/apikey"
echo "2. Enter the API key in the application sidebar"
echo
