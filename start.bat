@echo off
REM ============================================================================
REM Gun Del Sol - Master Launcher
REM ============================================================================
REM Starts all Gun Del Sol services:
REM   1. AutoHotkey interface (gun_del_sol.ahk)
REM   2. Flask REST API (localhost:5001)
REM   3. Next.js web dashboard (localhost:3000)
REM ============================================================================

echo ============================================================================
echo Gun Del Sol - Starting all services...
echo ============================================================================
echo.

REM Launch AutoHotkey script
echo [1/3] Starting AutoHotkey interface...
if exist "%~dp0gun_del_sol.ahk" (
    start "Gun Del Sol - AutoHotkey" "%~dp0gun_del_sol.ahk"
    echo       Started: gun_del_sol.ahk
) else (
    echo       WARNING: gun_del_sol.ahk not found
)
echo.

REM Launch Flask API
echo [2/3] Starting Flask REST API...
if exist "%~dp0start_monitor.bat" (
    start "Gun Del Sol - Flask API" /D "%~dp0" cmd /k start_monitor.bat
    echo       Started: Flask API (localhost:5001)
) else (
    echo       WARNING: start_monitor.bat not found
)
echo.

REM Launch Next.js web dashboard
echo [3/3] Starting Next.js web dashboard...
if exist "%~dp0..\gun-del-sol-web\launch_web.bat" (
    start "Gun Del Sol - Web Dashboard" /D "%~dp0..\gun-del-sol-web" cmd /k launch_web.bat
    echo       Started: Next.js Web (localhost:3000)
) else (
    echo       WARNING: ..\gun-del-sol-web\launch_web.bat not found
)
echo.

echo ============================================================================
echo All services started!
echo ============================================================================
echo.
echo AutoHotkey:  Running in background
echo Flask API:   http://localhost:5001
echo Next.js Web: http://localhost:3000
echo.
echo Close the individual windows to stop each service.
echo ============================================================================
echo.
pause
