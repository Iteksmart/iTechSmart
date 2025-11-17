# iTechSmart Agent Dockerfile
# Copyright © 2025 iTechSmart Inc. All rights reserved.

# Build stage
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git make gcc musl-dev

# Set working directory
WORKDIR /build

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build agent
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s -X main.version=1.0.0 -X main.buildDate=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    -o itechsmart-agent \
    cmd/agent/main.go

# Runtime stage
FROM alpine:latest

# Install runtime dependencies
RUN apk add --no-cache ca-certificates tzdata

# Create user
RUN addgroup -g 1000 itechsmart && \
    adduser -D -u 1000 -G itechsmart itechsmart

# Create directories
RUN mkdir -p /etc/itechsmart /var/log/itechsmart && \
    chown -R itechsmart:itechsmart /etc/itechsmart /var/log/itechsmart

# Copy binary from builder
COPY --from=builder /build/itechsmart-agent /usr/local/bin/

# Copy default config
COPY configs/agent.yaml /etc/itechsmart/

# Set permissions
RUN chmod +x /usr/local/bin/itechsmart-agent

# Switch to non-root user
USER itechsmart

# Set working directory
WORKDIR /home/itechsmart

# Expose ports (if needed)
# EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep itechsmart-agent || exit 1

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/itechsmart-agent"]

# Default command
CMD ["--config", "/etc/itechsmart/agent.yaml"]

# Labels
LABEL maintainer="iTechSmart Inc <support@itechsmart.dev>"
LABEL version="1.0.0"
LABEL description="iTechSmart Agent - System monitoring and management"
LABEL org.opencontainers.image.source="https://github.com/Iteksmart/iTechSmart"
LABEL org.opencontainers.image.vendor="iTechSmart Inc"
LABEL org.opencontainers.image.licenses="Proprietary"