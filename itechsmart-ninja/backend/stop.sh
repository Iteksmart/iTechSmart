#!/bin/bash

# iTechSmart Ninja - Stop Script

echo "🛑 Stopping iTechSmart Ninja Backend..."

# Stop Docker containers
docker-compose down

echo "✅ All services stopped."
echo ""
echo "💾 Data is preserved in Docker volumes."
echo "🗑️  To remove all data, run: docker-compose down -v"