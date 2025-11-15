#!/bin/bash

echo "🚀 Starting iTechSmart MDM Deployment Agent..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Create network if it doesn't exist
docker network create itechsmart-network 2>/dev/null || true

# Start services
echo "📦 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker ps | grep -q itechsmart-mdm-agent; then
    echo "✅ iTechSmart MDM Deployment Agent is running!"
    echo ""
    echo "📍 Access Points:"
    echo "   - API: http://localhost:8200"
    echo "   - API Docs: http://localhost:8200/docs"
    echo "   - Health Check: http://localhost:8200/health"
    echo ""
    echo "📊 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop services:"
    echo "   docker-compose down"
else
    echo "❌ Failed to start iTechSmart MDM Deployment Agent"
    echo "📋 Check logs with: docker-compose logs"
    exit 1
fi
