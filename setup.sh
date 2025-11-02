#!/bin/bash

# Dynamic Personal Finance Agent - Setup Script
# This script sets up both backend and frontend environments

echo "🚀 Setting up Dynamic Personal Finance Agent..."
echo "=================================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Setup Backend
echo ""
echo "🔧 Setting up Backend..."
echo "------------------------"

cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp sample.env .env
    echo "⚠️  Please edit backend/.env with your API keys!"
fi

cd ..

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend..."
echo "-------------------------"

cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

# Create startup scripts
echo ""
echo "📝 Creating startup scripts..."
echo "------------------------------"

# Create backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
python main.py
EOF

# Create frontend startup script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm run dev
EOF

# Create combined startup script
cat > start_all.sh << 'EOF'
#!/bin/bash
echo "Starting Dynamic Personal Finance Agent..."
echo "=========================================="

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend
echo "🚀 Starting Backend (Port 8000)..."
cd backend
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend (Port 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Services started successfully!"
echo "=================================="
echo "🔗 Frontend: http://localhost:5173"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
EOF

# Make scripts executable
chmod +x start_backend.sh
chmod +x start_frontend.sh
chmod +x start_all.sh

# Create Windows batch files
cat > start_backend.bat << 'EOF'
@echo off
cd backend
call venv\Scripts\activate
python main.py
pause
EOF

cat > start_frontend.bat << 'EOF'
@echo off
cd frontend
npm run dev
pause
EOF

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📋 Next Steps:"
echo "1. Edit backend/.env with your API keys (especially GROQ_API_KEY)"
echo "2. Run the application:"
echo "   • Option 1: ./start_all.sh (starts both backend and frontend)"
echo "   • Option 2: Run separately:"
echo "     - Backend: ./start_backend.sh (or start_backend.bat on Windows)"
echo "     - Frontend: ./start_frontend.sh (or start_frontend.bat on Windows)"
echo ""
echo "🔗 URLs:"
echo "   • Frontend: http://localhost:5173"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "📖 For detailed setup instructions, see SETUP_GUIDE.md"
echo ""
echo "⚠️  Required API Keys:"
echo "   • GROQ_API_KEY (required for LLM functionality)"
echo "   • ALPHA_VANTAGE_API_KEY (optional, for market data)"
echo "   • FINNHUB_API_KEY (optional, for financial data)"