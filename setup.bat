@echo off
echo 🚀 Setting up Dynamic Personal Finance Agent...
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ and try again.
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed

REM Setup Backend
echo.
echo 🔧 Setting up Backend...
echo ------------------------

cd backend

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy sample.env .env
    echo ⚠️  Please edit backend\.env with your API keys!
)

cd ..

REM Setup Frontend
echo.
echo 🎨 Setting up Frontend...
echo -------------------------

cd frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

cd ..

echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo 📋 Next Steps:
echo 1. Edit backend\.env with your API keys (especially GROQ_API_KEY)
echo 2. Run the application:
echo    • Backend: start_backend.bat
echo    • Frontend: start_frontend.bat
echo.
echo 🔗 URLs:
echo    • Frontend: http://localhost:5173
echo    • Backend API: http://localhost:8000
echo    • API Documentation: http://localhost:8000/docs
echo.
echo 📖 For detailed setup instructions, see SETUP_GUIDE.md
echo.
echo ⚠️  Required API Keys:
echo    • GROQ_API_KEY (required for LLM functionality)
echo    • ALPHA_VANTAGE_API_KEY (optional, for market data)
echo    • FINNHUB_API_KEY (optional, for financial data)
echo.
pause