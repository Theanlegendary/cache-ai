@echo off
REM Cache AI - Auto Setup & Run Script for Windows
REM This script installs dependencies and starts the API server automatically

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║            Cache AI - Auto Setup & Run                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not available
    pause
    exit /b 1
)

echo ✅ pip found

REM Create data directory if it doesn't exist
if not exist "data" (
    echo 📁 Creating data directory...
    mkdir data
)

REM Check if requirements are installed
echo.
echo 📦 Checking dependencies...
pip list | find "flask" >nul
if errorlevel 1 (
    echo 📥 Installing required packages...
    pip install flask flask-cors
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo ✅ Dependencies already installed
)

REM Start the API server
echo.
echo 🚀 Starting Cache AI API Server...
echo.
echo ════════════════════════════════════════════════════════════════
echo 📊 API Server Started!
echo 🌐 Dashboard:     http://localhost:5000
echo 🌐 Dashboard:     http://localhost:5000/dashboard
echo ════════════════════════════════════════════════════════════════
echo.
echo 📚 API Endpoints:
echo    POST   /api/sessions                - Create session
echo    GET    /api/sessions                - List sessions
echo    GET    /api/sessions/^<id^>            - Get session
echo    POST   /api/interactions            - Log interaction
echo    GET    /api/stats                   - Get statistics
echo    GET    /api/rate                    - Get rating (0-10)
echo    GET    /api/compare/^<provider^>      - Compare with provider
echo.
echo Press Ctrl+C to stop the server
echo ════════════════════════════════════════════════════════════════
echo.

timeout /t 2 /nobreak

REM Start Flask app
python api/app.py

pause
