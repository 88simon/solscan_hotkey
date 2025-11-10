@echo off
title Gun Del Sol - Backend
REM ============================================================================
REM Gun Del Sol - Backend REST API Launcher
REM ============================================================================
REM Starts the Flask REST API service (pure JSON API, no HTML dashboard)
REM Provides endpoints for token analysis, wallet tagging, and data management
REM Use the Next.js frontend at localhost:3000 for the user interface
REM ============================================================================

set SCRIPT_DIR=%~dp0backend\
set PYTHON_SCRIPT=%SCRIPT_DIR%api_service.py

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: Cannot find api_service.py
    echo Expected location: %PYTHON_SCRIPT%
    echo.
    pause
    exit /b 1
)

REM Check if Flask and flask-cors are installed
python -c "import flask" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Flask is not installed. Installing dependencies...
    echo.
    python -m pip install -r "%SCRIPT_DIR%requirements.txt"
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install dependencies
        echo Please manually run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

python -c "import flask_cors" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo flask-cors is not installed. Installing dependencies...
    echo.
    python -m pip install -r "%SCRIPT_DIR%requirements.txt"
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install flask-cors
        echo Please manually run: pip install flask-cors
        echo.
        pause
        exit /b 1
    ) else (
        echo Dependencies installed successfully.
        echo.
    )
)

REM Check if FastAPI is installed
python -c "import fastapi" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo FastAPI is not installed. Installing dependencies...
    echo.
    python -m pip install fastapi uvicorn[standard]
    echo.
    REM Check if FastAPI installed successfully (ignore pip warnings)
    python -c "import fastapi" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install FastAPI
        echo Please manually run: pip install fastapi uvicorn[standard]
        echo.
        pause
        exit /b 1
    ) else (
        echo FastAPI installed successfully.
    )
)

REM Start the WebSocket server in background
echo.
echo Starting WebSocket notification server...
start "Gun Del Sol - WebSocket Server" /MIN python "%SCRIPT_DIR%websocket_server.py"
echo WebSocket server started on port 5002
timeout /t 2 /nobreak >nul

REM Start the Flask API service
echo.
echo Starting Gun Del Sol REST API Service...
echo.
echo Backend REST API:  http://localhost:5001
echo WebSocket Server:  http://localhost:5002
echo Frontend Dashboard: http://localhost:3000
echo.
echo NOTE: Backend is now a pure REST API (no HTML dashboard)
echo       Use the Next.js frontend at localhost:3000 for the UI
echo.
python "%PYTHON_SCRIPT%"

REM If we get here, the service was stopped
echo.
echo Backend service stopped.
pause