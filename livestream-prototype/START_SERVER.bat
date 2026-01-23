@echo off
echo =========================================
echo   LiveStream Prototype - Server Starter
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python detected
echo.

REM Navigate to backend directory
cd backend

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo =========================================
echo   Starting Backend Server...
echo =========================================
echo.
echo   Backend API: http://localhost:5000
echo   Backoffice:  Open ../backoffice/index.html
echo   Client:      Open ../client/index.html
echo.
echo   Press Ctrl+C to stop the server
echo.
echo =========================================
echo.

REM Start the server
python app.py

pause
