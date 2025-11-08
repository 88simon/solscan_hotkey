@echo off
REM ============================================================================
REM Gun Del Sol - Monitor Service Launcher
REM ============================================================================
REM Starts the Flask REST API service that receives address registrations
REM ============================================================================

set SCRIPT_DIR=%~dp0monitor\
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

REM Start the API service
echo.
echo Starting Gun Del Sol API Service...
echo Flask API: http://localhost:5001
echo Next.js Web: http://localhost:3000
echo.
python "%PYTHON_SCRIPT%"

REM If we get here, the service was stopped
echo.
echo API service stopped.
pause
