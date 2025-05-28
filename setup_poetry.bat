@echo off
echo Setting up Poetry for Metadata Curator Agent...
echo.

echo Checking if Poetry is installed...
poetry --version >nul 2>&1
if errorlevel 1 (
    echo Poetry not found. Installing Poetry...
    echo.
    echo Please run this command to install Poetry:
    echo (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing^).Content ^| py -
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo Poetry found! Setting up project...
echo.

echo Installing dependencies with Poetry...
poetry install

echo.
echo Setting up pre-commit hooks...
poetry run pre-commit install

echo.
echo Creating project directories...
if not exist "data" mkdir data
if not exist "exports" mkdir exports
if not exist "logs" mkdir logs
if not exist "tests" mkdir tests

echo.
echo Creating environment file...
if not exist ".env" copy ".env.example" ".env"

echo.
echo Poetry setup complete!
echo.
echo Available commands:
echo   poetry run streamlit run metadata_curator_agent.py
echo   poetry run streamlit run enhanced_app.py
echo   poetry run pytest (for testing)
echo   poetry run black . (for code formatting)
echo   poetry run flake8 (for linting)
echo.
echo Don't forget to:
echo 1. Get your Gemini API key from https://makersuite.google.com/app/apikey
echo 2. Enter the API key in the application sidebar
echo.
pause
