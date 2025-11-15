@echo off
echo Starting iTechSmart MDM Deployment Agent...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo docker-compose is not installed. Please install docker-compose first.
    pause
    exit /b 1
)

REM Create network if it doesn't exist
docker network create itechsmart-network 2>nul

REM Start services
echo Starting services with Docker Compose...
docker-compose up -d

echo.
echo ✅ iTechSmart MDM Deployment Agent started successfully!
echo.
echo Access points:
echo   - Backend API: http://localhost:8200
echo   - API Documentation: http://localhost:8200/docs
echo   - Health Check: http://localhost:8200/health
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.
pause
