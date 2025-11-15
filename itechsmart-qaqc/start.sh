#!/bin/bash

echo "🚀 Starting iTechSmart QA/QC System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create network if it doesn't exist
echo "📡 Creating iTechSmart network..."
docker network create itechsmart-network 2>/dev/null || true

# Start services
echo "🔧 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
curl -s http://localhost:8300/health > /dev/null && echo "✅ Backend is healthy" || echo "⚠️  Backend is not responding"
curl -s http://localhost:3300 > /dev/null && echo "✅ Frontend is healthy" || echo "⚠️  Frontend is not responding"

echo ""
echo "✅ iTechSmart QA/QC System is running!"
echo ""
echo "📊 Access points:"
echo "   Frontend:  http://localhost:3300"
echo "   Backend:   http://localhost:8300"
echo "   API Docs:  http://localhost:8300/docs"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
echo ""