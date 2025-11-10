@echo off
title Gun Del Sol - Backend
REM ============================================================================
REM Gun Del Sol - Backend REST API Launcher
REM ============================================================================
REM Starts the Flask REST API service (pure JSON API, no HTML dashboard)
REM Provides endpoints for token analysis, wallet tagging, and data management
REM Use the Next.js frontend at localhost:3000 for the user interface
REM ============================================================================

REM Kill any existing backend services (idempotent startup)
echo Checking for existing backend services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do (
    taskkill /F /PID %%a >nul 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5002') do (
    taskkill /F /PID %%a >nul 2>nul
)
echo Cleaned up any existing services.
echo.

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

REM Check if aiofiles is installed (async file I/O)
python -c "import aiofiles" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo aiofiles is not installed. Installing...
    echo.
    python -m pip install aiofiles
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install aiofiles
        echo Please manually run: pip install aiofiles
        echo.
        pause
        exit /b 1
    ) else (
        echo aiofiles installed successfully.
    )
)

REM Check if httpx is installed (async HTTP client)
python -c "import httpx" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo httpx is not installed. Installing...
    echo.
    python -m pip install httpx
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install httpx
        echo Please manually run: pip install httpx
        echo.
        pause
        exit /b 1
    ) else (
        echo httpx installed successfully.
    )
)

REM Check if aiosqlite is installed (async database)
python -c "import aiosqlite" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo aiosqlite is not installed. Installing...
    echo.
    python -m pip install aiosqlite
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install aiosqlite
        echo Please manually run: pip install aiosqlite
        echo.
        pause
        exit /b 1
    ) else (
        echo aiosqlite installed successfully.
    )
)

REM Check if orjson is installed (fast JSON serialization)
python -c "import orjson" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo orjson is not installed. Installing...
    echo.
    python -m pip install orjson
    echo.
    REM Verify installation succeeded
    python -c "import orjson" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install orjson
        echo Please manually run: pip install orjson
        echo.
        pause
        exit /b 1
    ) else (
        echo orjson installed successfully.
    )
)

REM Start the WebSocket server in background
echo.
echo Starting WebSocket notification server...
start "Gun Del Sol - WebSocket Server" python "%SCRIPT_DIR%websocket_server.py"
echo WebSocket server started on port 5002
timeout /t 2 /nobreak >nul

REM Start the FastAPI service in background (high-priority endpoints)
echo.
echo Starting FastAPI service (high-performance endpoints)...
start "Gun Del Sol - FastAPI" python -m uvicorn fastapi_main:app --port 5003 --app-dir "%SCRIPT_DIR%"
echo FastAPI server started on port 5003
timeout /t 2 /nobreak >nul

REM Start the Flask API service
echo.
echo Starting Gun Del Sol REST API Service...
echo.
echo Flask API (legacy):  http://localhost:5001
echo FastAPI (primary):  http://localhost:5003
echo WebSocket Server:   http://localhost:5002
echo Frontend Dashboard: http://localhost:3000
echo.
echo NOTE: Frontend uses FastAPI (port 5003) for better performance
echo       Flask API remains available for analysis jobs
echo.
python "%PYTHON_SCRIPT%"

REM If we get here, the service was stopped
echo.
echo Backend service stopped.
pause