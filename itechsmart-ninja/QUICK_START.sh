#!/bin/bash

# iTechSmart Ninja - Quick Start Script for Founder
# This script sets up and launches your personal AI agent platform

set -e

echo "🚀 iTechSmart Ninja - Founder Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env file with your API keys and settings"
    echo "   Run: nano .env"
    echo ""
    read -p "Press Enter after you've configured .env file..."
fi

echo "🔧 Starting iTechSmart Ninja platform..."
echo ""

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

# Check service health
echo ""
echo "🔍 Checking service health..."

if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
else
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Display service URLs
echo ""
echo "🎉 iTechSmart Ninja is ready!"
echo "=============================="
echo ""
echo "📱 Access your platform:"
echo "   Frontend:  http://localhost:3000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   API:       http://localhost:8000"
echo ""
echo "🔐 First-time setup:"
echo "   1. Create your founder account:"
echo "      docker exec -it ninja-backend python scripts/create_founder.py"
echo ""
echo "   2. Login at http://localhost:3000"
echo ""
echo "📊 Useful commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop platform: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "📖 Full documentation: FOUNDER_SETUP.md"
echo ""
echo "Happy building! 🚀"