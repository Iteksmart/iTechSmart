#!/bin/bash

# iTechSmart Ninja - Startup Script

echo "🚀 Starting iTechSmart Ninja Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your configuration."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads deployments logs

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start services with Docker Compose
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Show logs
echo ""
echo "✅ iTechSmart Ninja is starting!"
echo ""
echo "📊 Service URLs:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo ""
echo "📝 View logs with: docker-compose logs -f"
echo "🛑 Stop services with: docker-compose down"
echo ""
echo "🔐 Default Admin Credentials:"
echo "   Email: admin@itechsmart.ninja"
echo "   Password: admin123"
echo ""
echo "⚠️  Remember to change the admin password after first login!"