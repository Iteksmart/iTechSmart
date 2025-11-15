#!/bin/bash

# Products to complete
declare -A PRODUCTS=(
    ["itechsmart-thinktank"]="8030:3030:Internal AI Development Platform"
    ["itechsmart-cloud"]="8020:3020:Multi-Cloud Management"
    ["itechsmart-devops"]="8021:3021:CI/CD Automation"
    ["itechsmart-mobile"]="8022:3022:Mobile Development Platform"
    ["itechsmart-ai"]="8023:3023:AI/ML Platform"
    ["itechsmart-compliance"]="8024:3024:Compliance Management"
    ["itechsmart-data-platform"]="8025:3025:Data Governance"
    ["itechsmart-customer-success"]="8026:3026:Customer Success Platform"
)

for product in "${!PRODUCTS[@]}"; do
    IFS=':' read -r backend_port frontend_port description <<< "${PRODUCTS[$product]}"
    
    echo "Processing: $product"
    
    # Create backend main.py if missing
    if [ ! -f "/workspace/$product/backend/main.py" ]; then
        echo "Creating backend/main.py for $product"
        mkdir -p "/workspace/$product/backend"
        cat > "/workspace/$product/backend/main.py" << EOF
"""
${product^} - Main Entry Point
$description
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ${product^}...")
    yield
    logger.info("Shutting down ${product^}...")

app = FastAPI(
    title="${product^}",
    description="$description - Part of iTechSmart Suite",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "${product^}",
        "version": "1.0.0",
        "description": "$description",
        "status": "operational",
        "suite": "iTechSmart Suite"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "${product^}", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=$backend_port)
EOF
    fi
    
    # Create docker-compose.yml if missing
    if [ ! -f "/workspace/$product/docker-compose.yml" ]; then
        echo "Creating docker-compose.yml for $product"
        cat > "/workspace/$product/docker-compose.yml" << EOF
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "$backend_port:$backend_port"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./backend:/app
      - ${product}-data:/app/data
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "$frontend_port:$frontend_port"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  ${product}-data:
EOF
    fi
    
    # Create backend Dockerfile if missing
    if [ ! -f "/workspace/$product/backend/Dockerfile" ]; then
        echo "Creating backend Dockerfile for $product"
        cat > "/workspace/$product/backend/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE PORT_PLACEHOLDER

CMD ["python", "main.py"]
EOF
        sed -i "s/PORT_PLACEHOLDER/$backend_port/" "/workspace/$product/backend/Dockerfile"
    fi
    
    # Create frontend Dockerfile if missing
    if [ ! -f "/workspace/$product/frontend/Dockerfile" ]; then
        echo "Creating frontend Dockerfile for $product"
        mkdir -p "/workspace/$product/frontend"
        cat > "/workspace/$product/frontend/Dockerfile" << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

RUN npm install -g serve

EXPOSE PORT_PLACEHOLDER

CMD ["serve", "-s", "dist", "-l", "PORT_PLACEHOLDER"]
EOF
        sed -i "s/PORT_PLACEHOLDER/$frontend_port/g" "/workspace/$product/frontend/Dockerfile"
    fi
    
    # Create docs directory
    mkdir -p "/workspace/$product/docs"
    
    echo "✓ Completed: $product"
    echo ""
done

echo "All products processed!"
