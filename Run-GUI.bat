@echo off
TITLE Coolify Multi-VPS Fleet GUI HUD
COLOR 0B
CLS

cd /d "%~dp0"

echo ================================================================================
echo   LAUNCHING COOLIFY MULTI-VPS FLEET VISUAL GUI HUD (PORTABLE)
echo   Local URL: http://127.0.0.1:8450
echo ================================================================================

python gui\server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] GUI server exited with code %ERRORLEVEL%.
    pause
)
