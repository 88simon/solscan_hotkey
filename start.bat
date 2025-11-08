@echo off
title Gun Del Sol - Launcher
REM ============================================================================
REM Gun Del Sol - Master Launcher
REM ============================================================================
REM Starts all Gun Del Sol services:
REM   1. AutoHotkey action wheel (action_wheel.ahk)
REM   2. Flask REST API backend (localhost:5001) - JSON API only
REM   3. Next.js frontend dashboard (localhost:3000) - Main UI
REM ============================================================================

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

REM Launch Backend API
echo [2/3] Starting backend API...
if exist "%~dp0start_backend.bat" (
    start "Gun Del Sol - Backend" /D "%~dp0" cmd /k start_backend.bat
    echo       Started: Backend ^(localhost:5001^)
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
echo Backend REST API:   http://localhost:5001 ^(JSON API only^)
echo Frontend Dashboard: http://localhost:3000 ^(Main UI^)
echo.
echo NOTE: Access the dashboard at http://localhost:3000
echo       The backend is now a pure REST API with no HTML interface.
echo.
echo Close the individual windows to stop each service.
echo ============================================================================
echo.
pause
