#!/usr/bin/env python3
"""
Script to generate production-ready Dockerfiles for all iTechSmart products.
Uses successful products as templates.
"""

import os
import sys
from pathlib import Path

# Backend Dockerfile template (based on itechsmart-ninja)
BACKEND_DOCKERFILE = """# Multi-stage build for iTechSmart {product_name} Backend
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    libpq5 \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# Vite Frontend Dockerfile template (based on itechsmart-hl7)
VITE_FRONTEND_DOCKERFILE = """# Multi-stage build for iTechSmart {product_name} Frontend (Vite)
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""

# Create React App Frontend Dockerfile template
CRA_FRONTEND_DOCKERFILE = """# Multi-stage build for iTechSmart {product_name} Frontend (Create React App)
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including react-scripts)
RUN npm install

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""

# Next.js Frontend Dockerfile template (based on passport/prooflink)
NEXTJS_FRONTEND_DOCKERFILE = """# Multi-stage build for iTechSmart {product_name} Frontend (Next.js)
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm install --production

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.* ./

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Start application
CMD ["npm", "start"]
"""

# nginx.conf for Vite/CRA frontends
NGINX_CONF = """server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # SPA routing - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
"""

# Product framework mapping
VITE_PRODUCTS = [
    "itechsmart-ai",
    "itechsmart-citadel",
    "itechsmart-connect",
    "itechsmart-copilot",
    "itechsmart-dataflow",
    "itechsmart-forge",
    "itechsmart-ledger",
    "itechsmart-marketplace",
    "itechsmart-mdm-agent",
    "itechsmart-notify",
    "itechsmart-qaqc",
    "itechsmart-sandbox",
    "itechsmart-supreme-plus",
    "itechsmart-thinktank",
    "itechsmart-vault",
    "itechsmart-workflow",
    "legalai-pro",
]

CRA_PRODUCTS = [
    "itechsmart-analytics",
    "itechsmart-cloud",
    "itechsmart-compliance",
    "itechsmart-customer-success",
    "itechsmart-data-platform",
    "itechsmart-devops",
    "itechsmart-mobile",
    "itechsmart-observatory",
    "itechsmart-port-manager",
    "itechsmart-pulse",
    "itechsmart-shield",
]

NEXTJS_PRODUCTS = [
    "itechsmart-enterprise",
    "itechsmart-hl7",
    "itechsmart-impactos",
    "itechsmart-ninja",
    "passport",
    "prooflink",
]


def create_backend_dockerfile(product_path: Path, product_name: str):
    """Create backend Dockerfile for a product."""
    dockerfile_path = product_path / "backend" / "Dockerfile.backend"
    
    if dockerfile_path.exists():
        print(f"  ⚠️  Backend Dockerfile already exists for {product_name}")
        return False
    
    content = BACKEND_DOCKERFILE.format(product_name=product_name)
    dockerfile_path.write_text(content)
    print(f"  ✅ Created backend Dockerfile for {product_name}")
    return True


def create_frontend_dockerfile(product_path: Path, product_name: str, framework: str):
    """Create frontend Dockerfile for a product based on framework."""
    dockerfile_path = product_path / "frontend" / "Dockerfile.frontend"
    nginx_conf_path = product_path / "frontend" / "nginx.conf"
    
    if dockerfile_path.exists():
        print(f"  ⚠️  Frontend Dockerfile already exists for {product_name}")
        return False
    
    # Select template based on framework
    if framework == "vite":
        content = VITE_FRONTEND_DOCKERFILE.format(product_name=product_name)
        needs_nginx = True
    elif framework == "cra":
        content = CRA_FRONTEND_DOCKERFILE.format(product_name=product_name)
        needs_nginx = True
    elif framework == "nextjs":
        content = NEXTJS_FRONTEND_DOCKERFILE.format(product_name=product_name)
        needs_nginx = False
    else:
        print(f"  ❌ Unknown framework: {framework}")
        return False
    
    dockerfile_path.write_text(content)
    print(f"  ✅ Created frontend Dockerfile for {product_name} ({framework})")
    
    # Create nginx.conf if needed
    if needs_nginx and not nginx_conf_path.exists():
        nginx_conf_path.write_text(NGINX_CONF)
        print(f"  ✅ Created nginx.conf for {product_name}")
    
    return True


def main():
    """Main function to generate Dockerfiles for all products."""
    repo_root = Path(__file__).parent.parent
    
    print("🚀 Generating Dockerfiles for all iTechSmart products...\n")
    
    stats = {
        "backend_created": 0,
        "frontend_created": 0,
        "backend_skipped": 0,
        "frontend_skipped": 0,
    }
    
    # Process Vite products
    print("📦 Processing Vite products...")
    for product in VITE_PRODUCTS:
        product_path = repo_root / product
        if not product_path.exists():
            print(f"  ⚠️  Product directory not found: {product}")
            continue
        
        print(f"\n{product}:")
        if create_backend_dockerfile(product_path, product):
            stats["backend_created"] += 1
        else:
            stats["backend_skipped"] += 1
        
        if create_frontend_dockerfile(product_path, product, "vite"):
            stats["frontend_created"] += 1
        else:
            stats["frontend_skipped"] += 1
    
    # Process CRA products
    print("\n\n📦 Processing Create React App products...")
    for product in CRA_PRODUCTS:
        product_path = repo_root / product
        if not product_path.exists():
            print(f"  ⚠️  Product directory not found: {product}")
            continue
        
        print(f"\n{product}:")
        if create_backend_dockerfile(product_path, product):
            stats["backend_created"] += 1
        else:
            stats["backend_skipped"] += 1
        
        if create_frontend_dockerfile(product_path, product, "cra"):
            stats["frontend_created"] += 1
        else:
            stats["frontend_skipped"] += 1
    
    # Process Next.js products (already have Dockerfiles, just report)
    print("\n\n📦 Checking Next.js products (should already have Dockerfiles)...")
    for product in NEXTJS_PRODUCTS:
        product_path = repo_root / product
        if not product_path.exists():
            print(f"  ⚠️  Product directory not found: {product}")
            continue
        
        print(f"\n{product}:")
        backend_exists = (product_path / "backend" / "Dockerfile.backend").exists()
        frontend_exists = (product_path / "frontend" / "Dockerfile.frontend").exists()
        
        if backend_exists:
            print(f"  ✅ Backend Dockerfile exists")
            stats["backend_skipped"] += 1
        else:
            print(f"  ❌ Backend Dockerfile missing!")
            if create_backend_dockerfile(product_path, product):
                stats["backend_created"] += 1
        
        if frontend_exists:
            print(f"  ✅ Frontend Dockerfile exists")
            stats["frontend_skipped"] += 1
        else:
            print(f"  ❌ Frontend Dockerfile missing!")
            if create_frontend_dockerfile(product_path, product, "nextjs"):
                stats["frontend_created"] += 1
    
    # Print summary
    print("\n\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Backend Dockerfiles created:  {stats['backend_created']}")
    print(f"Backend Dockerfiles skipped:  {stats['backend_skipped']}")
    print(f"Frontend Dockerfiles created: {stats['frontend_created']}")
    print(f"Frontend Dockerfiles skipped: {stats['frontend_skipped']}")
    print(f"\nTotal Dockerfiles created: {stats['backend_created'] + stats['frontend_created']}")
    print(f"Total products processed: {len(VITE_PRODUCTS) + len(CRA_PRODUCTS) + len(NEXTJS_PRODUCTS)}")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())