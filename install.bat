@echo off
echo Installing Metadata Curator Agent dependencies...
echo.

echo Installing Python packages...
pip install -r requirements.txt

echo.
echo Setting up project structure...
if not exist "data" mkdir data
if not exist "exports" mkdir exports
if not exist "logs" mkdir logs

echo.
echo Creating environment file...
if not exist ".env" copy ".env.example" ".env"

echo.
echo Installation complete!
echo.
echo To run the application:
echo   streamlit run metadata_curator_agent.py
echo.
echo For enhanced version:
echo   streamlit run enhanced_app.py
echo.
echo Don't forget to:
echo 1. Get your Gemini API key from https://makersuite.google.com/app/apikey
echo 2. Enter the API key in the application sidebar
echo.
pause
