@echo off
echo ========================================================================
echo 🚀 Starting LegalAI Pro - The World's Best AI-Powered Attorney Office Software
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Start backend
echo 📦 Starting Backend API...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -q -r requirements.txt

REM Start backend
echo Starting FastAPI server on http://localhost:8000
start /B python main.py

cd ..

REM Start frontend
echo.
echo 🎨 Starting Frontend...
cd frontend

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
)

REM Start frontend
echo Starting React app on http://localhost:3000
start /B npm run dev

cd ..

echo.
echo ========================================================================
echo ✅ LegalAI Pro is now running!
echo.
echo 📍 Frontend: http://localhost:3000
echo 📍 Backend API: http://localhost:8000
echo 📍 API Docs: http://localhost:8000/docs
echo.
echo 🔑 Demo Login Credentials:
echo    Email: demo@legalai.pro
echo    Password: demo123
echo.
echo Press any key to stop all services
echo ========================================================================
pause >nul

REM Stop services
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
echo 🛑 LegalAI Pro stopped