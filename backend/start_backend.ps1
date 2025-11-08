# PowerShell startup script for X-Fair Finance Backend

Write-Host "Starting X-Fair Finance Backend..." -ForegroundColor Cyan
Write-Host ""

# Change to the script directory
Set-Location $PSScriptRoot

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy sample.env to .env and configure your API keys." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Using: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the server
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python main.py
