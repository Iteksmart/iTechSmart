@echo off
echo Starting iTechSmart QA/QC System...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create network if it doesn't exist
echo Creating iTechSmart network...
docker network create itechsmart-network 2>nul

REM Start services
echo Starting services...
docker-compose up -d

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo iTechSmart QA/QC System is running!
echo.
echo Access points:
echo    Frontend:  http://localhost:3300
echo    Backend:   http://localhost:8300
echo    API Docs:  http://localhost:8300/docs
echo.
echo To view logs:
echo    docker-compose logs -f
echo.
echo To stop:
echo    docker-compose down
echo.

pause