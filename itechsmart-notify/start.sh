#!/bin/bash

set -e

echo "=========================================="
echo "iTechSmart Notify - Quick Start"
echo "=========================================="
echo ""

if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
echo ""

echo "🏗️  Building and starting services..."
echo ""

if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

echo ""
echo "⏳ Waiting for services to be healthy..."
echo ""

max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker-compose ps 2>/dev/null | grep -q "healthy" || docker compose ps 2>/dev/null | grep -q "healthy"; then
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done

echo ""
echo ""

echo "📊 Service Status:"
echo "===================="
if docker compose version &> /dev/null; then
    docker compose ps
else
    docker-compose ps
fi

echo ""
echo "=========================================="
echo "✅ iTechSmart Notify is now running!"
echo "=========================================="
echo ""
echo "🌐 Access the application:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   RabbitMQ:  http://localhost:15672"
echo ""
echo "🔐 Default credentials:"
echo "   Username: admin"
echo "   Password: password"
echo ""
echo "📝 Useful commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "=========================================="