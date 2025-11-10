@echo off
title Gun Del Sol - Launcher
REM ============================================================================
REM Gun Del Sol - Master Launcher
REM ============================================================================
REM Starts all Gun Del Sol services:
REM   1. AutoHotkey action wheel (action_wheel.ahk)
REM   2. Flask REST API backend (localhost:5001) - JSON API only
REM   3. FastAPI WebSocket server (localhost:5002) - Real-time notifications
REM   4. Next.js frontend dashboard (localhost:3000) - Main UI
REM ============================================================================

REM Kill any existing services (idempotent startup)
echo Checking for existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /F /PID %%a >nul 2>nul
)
echo Cleaned up any existing services.
echo.

echo ============================================================================
echo Gun Del Sol - Starting all services...
echo ============================================================================
echo.

REM Launch AutoHotkey script
echo [1/3] Starting AutoHotkey action wheel...
if exist "%~dp0action_wheel.ahk" (
    start "Gun Del Sol - Action Wheel" "%~dp0action_wheel.ahk"
    echo       Started: action_wheel.ahk
) else (
    echo       WARNING: action_wheel.ahk not found
)
echo.

REM Launch Backend API (includes WebSocket server and FastAPI)
echo [2/3] Starting backend services...
if exist "%~dp0start_backend.bat" (
    start "Gun Del Sol - Backend" /D "%~dp0" cmd /k start_backend.bat
    echo       Started: Flask API ^(localhost:5001^) - Legacy/Analysis
    echo       Started: FastAPI ^(localhost:5003^) - Primary API
    echo       Started: WebSocket Server ^(localhost:5002^) - Notifications
) else (
    echo       WARNING: start_backend.bat not found
)
echo.

REM Launch Frontend
echo [3/3] Starting frontend...
if exist "%~dp0..\gun-del-sol-web\launch_web.bat" (
    start "Gun Del Sol - Frontend" /D "%~dp0..\gun-del-sol-web" cmd /k "title Gun Del Sol - Frontend && launch_web.bat"
    echo       Started: Frontend ^(localhost:3000^)
) else (
    echo       WARNING: ..\gun-del-sol-web\launch_web.bat not found
)
echo.

echo ============================================================================
echo All services started!
echo ============================================================================
echo.
echo Action Wheel:       Running in background
echo FastAPI ^(Primary^):  http://localhost:5003 ^(High-performance API^)
echo Flask API ^(Legacy^):  http://localhost:5001 ^(Analysis jobs^)
echo WebSocket Server:   http://localhost:5002 ^(Real-time notifications^)
echo Frontend Dashboard: http://localhost:3000 ^(Main UI^)
echo.
echo NOTE: Access the dashboard at http://localhost:3000
echo       FastAPI serves all frontend requests for better performance
echo       Flask API handles token analysis jobs
echo.
echo Close the individual windows to stop each service.
echo ============================================================================
echo.
pause
