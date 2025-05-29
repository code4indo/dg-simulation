#!/bin/bash

echo "Installing Metadata Curator Agent dependencies..."
echo

echo "Installing Python packages..."
pip install -r requirements.txt

echo
echo "Setting up project structure..."
mkdir -p data exports logs

echo
echo "Creating environment file..."
if [ ! -f ".env" ]; then
    cp ".env.example" ".env"
fi

echo
echo "Installation complete!"
echo
echo "To run the application:"
echo "  streamlit run metadata_curator_agent.py"
echo
echo "For enhanced version:"
echo "  streamlit run enhanced_app.py"
echo
echo "Don't forget to:"
echo "1. Get your Gemini API key from https://makersuite.google.com/app/apikey"
echo "2. Enter the API key in the application sidebar"
echo
