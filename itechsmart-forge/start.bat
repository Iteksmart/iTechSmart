@echo off
REM iTechSmart Forge - Startup Script (Windows)

echo.
echo ========================================
echo  iTechSmart Forge - Starting...
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Create network if it doesn't exist
echo Creating iTechSmart network...
docker network create itechsmart-network 2>nul

REM Start services
echo Starting Docker containers...
docker-compose up -d

REM Wait for services
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo  iTechSmart Forge Started!
echo ========================================
echo.
echo Access Points:
echo   Backend API:  http://localhost:8320
echo   API Docs:     http://localhost:8320/docs
echo.
echo View logs:      docker-compose logs -f
echo Stop services:  docker-compose down
echo.
echo ========================================
echo.

pause