#!/bin/bash

echo "🚀 Starting LegalAI Pro - The World's Best AI-Powered Attorney Office Software"
echo "=============================================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Start backend
echo "📦 Starting Backend API..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Start backend in background
echo "Starting FastAPI server on http://localhost:8000"
python main.py &
BACKEND_PID=$!

cd ..

# Start frontend
echo ""
echo "🎨 Starting Frontend..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Start frontend
echo "Starting React app on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "=============================================================================="
echo "✅ LegalAI Pro is now running!"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "🔑 Demo Login Credentials:"
echo "   Email: demo@legalai.pro"
echo "   Password: demo123"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=============================================================================="

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping LegalAI Pro...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait