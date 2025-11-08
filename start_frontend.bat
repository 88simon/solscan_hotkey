@echo off
REM ============================================================================
REM Gun Del Sol - Frontend Only
REM ============================================================================
REM Starts only the Next.js frontend on localhost:3000
REM Useful for troubleshooting or when backend API is already running
REM ============================================================================

echo ============================================================================
echo Gun Del Sol - Starting Frontend...
echo ============================================================================
echo.

REM Check if launch_web.bat exists
if exist "%~dp0..\gun-del-sol-web\launch_web.bat" (
    echo Starting Next.js development server...
    echo.
    cd /d "%~dp0..\gun-del-sol-web"
    call launch_web.bat
) else (
    echo ERROR: Cannot find gun-del-sol-web\launch_web.bat
    echo Expected location: %~dp0..\gun-del-sol-web\launch_web.bat
    echo.
    pause
    exit /b 1
)
