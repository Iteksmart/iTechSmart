# Multi-stage build for FitSnap.AI Frontend (Expo Web)

# Stage 1: Dependencies
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application code
COPY frontend/ .

# Build for web
RUN npx expo export:web

# Stage 3: Runner
FROM node:20-alpine AS runner

WORKDIR /app

# Install serve
RUN npm install -g serve

# Copy built application
COPY --from=builder /app/web-build ./web-build

# Expose port
EXPOSE 19006

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:19006 || exit 1

# Serve the app
CMD ["serve", "web-build", "-p", "19006"]