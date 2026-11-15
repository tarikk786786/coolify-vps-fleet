@echo off
TITLE Coolify Multi-VPS Fleet Manager
COLOR 0B
CLS

:: 100% Self-Contained Portable Launcher
:: Can be run from ANY directory, drive, or machine without hardcoded paths
cd /d "%~dp0"

echo ================================================================================
echo   COOLIFY MULTI-VPS FLEET MANAGER & UNIVERSAL MOVER
echo   Portable Directory: %CD%
echo ================================================================================

python launcher.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Launcher exited with error code %ERRORLEVEL%.
    pause
)
