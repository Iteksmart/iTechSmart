#!/bin/bash

# iTechSmart Sentinel - Startup Script (Linux/Mac)

echo "🚀 Starting iTechSmart Sentinel..."
echo ""

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
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service health..."
echo ""

# Check backend
if curl -s http://localhost:8310/health > /dev/null; then
    echo "✅ Backend API is running at http://localhost:8310"
else
    echo "⚠️  Backend API is not responding yet..."
fi

# Check frontend
if curl -s http://localhost:3310 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:3310"
else
    echo "⚠️  Frontend is not responding yet..."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 iTechSmart Sentinel is starting up!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Access Points:"
echo "   Frontend:        http://localhost:3310"
echo "   Backend API:     http://localhost:8310"
echo "   API Docs:        http://localhost:8310/docs"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"