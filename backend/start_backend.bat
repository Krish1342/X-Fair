@echo off
REM Startup script for X-Fair Finance Backend

echo Starting X-Fair Finance Backend...
echo.

cd /d "%~dp0"

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy sample.env to .env and configure your API keys.
    pause
    exit /b 1
)

REM Run the server
python main.py

pause
