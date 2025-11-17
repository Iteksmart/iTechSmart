# iTechSmart Agent Makefile
# Copyright © 2025 iTechSmart Inc. All rights reserved.

# Variables
BINARY_NAME=itechsmart-agent
VERSION=1.0.0
BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT=$(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
LDFLAGS=-ldflags "-X main.version=$(VERSION) -X main.buildDate=$(BUILD_DATE) -X main.gitCommit=$(GIT_COMMIT)"

# Go parameters
GOCMD=go
GOBUILD=$(GOCMD) build
GOCLEAN=$(GOCMD) clean
GOTEST=$(GOCMD) test
GOGET=$(GOCMD) get
GOMOD=$(GOCMD) mod

# Build directories
BUILD_DIR=build
DIST_DIR=dist

# Platforms
PLATFORMS=windows linux darwin
ARCHITECTURES=amd64 arm64

.PHONY: all build clean test deps build-all install uninstall

# Default target
all: clean deps test build

# Build for current platform
build:
	@echo "Building $(BINARY_NAME) v$(VERSION)..."
	@mkdir -p $(BUILD_DIR)
	$(GOBUILD) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME) cmd/agent/main.go
	@echo "Build complete: $(BUILD_DIR)/$(BINARY_NAME)"

# Build for all platforms
build-all: clean deps
	@echo "Building for all platforms..."
	@mkdir -p $(DIST_DIR)
	@for platform in $(PLATFORMS); do \
		for arch in $(ARCHITECTURES); do \
			output_name=$(BINARY_NAME)-$$platform-$$arch; \
			if [ $$platform = "windows" ]; then \
				output_name=$$output_name.exe; \
			fi; \
			echo "Building $$output_name..."; \
			GOOS=$$platform GOARCH=$$arch $(GOBUILD) $(LDFLAGS) -o $(DIST_DIR)/$$output_name cmd/agent/main.go; \
		done \
	done
	@echo "All builds complete in $(DIST_DIR)/"

# Clean build artifacts
clean:
	@echo "Cleaning..."
	@rm -rf $(BUILD_DIR) $(DIST_DIR)
	$(GOCLEAN)
	@echo "Clean complete"

# Run tests
test:
	@echo "Running tests..."
	$(GOTEST) -v -race -coverprofile=coverage.out ./...
	@echo "Tests complete"

# Download dependencies
deps:
	@echo "Downloading dependencies..."
	$(GOMOD) download
	$(GOMOD) tidy
	@echo "Dependencies downloaded"

# Install agent (requires root/admin)
install: build
	@echo "Installing $(BINARY_NAME)..."
	@if [ "$$(uname)" = "Darwin" ] || [ "$$(uname)" = "Linux" ]; then \
		sudo cp $(BUILD_DIR)/$(BINARY_NAME) /usr/local/bin/; \
		sudo chmod +x /usr/local/bin/$(BINARY_NAME); \
		sudo mkdir -p /etc/itechsmart; \
		sudo mkdir -p /var/log/itechsmart; \
		if [ ! -f /etc/itechsmart/agent.yaml ]; then \
			sudo cp configs/agent.yaml /etc/itechsmart/; \
		fi; \
		echo "Installed to /usr/local/bin/$(BINARY_NAME)"; \
	else \
		echo "Manual installation required on Windows"; \
	fi

# Uninstall agent (requires root/admin)
uninstall:
	@echo "Uninstalling $(BINARY_NAME)..."
	@if [ "$$(uname)" = "Darwin" ] || [ "$$(uname)" = "Linux" ]; then \
		sudo rm -f /usr/local/bin/$(BINARY_NAME); \
		echo "Uninstalled from /usr/local/bin/$(BINARY_NAME)"; \
		echo "Config files remain in /etc/itechsmart/"; \
	else \
		echo "Manual uninstallation required on Windows"; \
	fi

# Run agent (development)
run:
	@echo "Running $(BINARY_NAME)..."
	$(GOBUILD) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME) cmd/agent/main.go
	$(BUILD_DIR)/$(BINARY_NAME) --config configs/agent.yaml

# Format code
fmt:
	@echo "Formatting code..."
	$(GOCMD) fmt ./...

# Lint code
lint:
	@echo "Linting code..."
	@if command -v golangci-lint >/dev/null 2>&1; then \
		golangci-lint run ./...; \
	else \
		echo "golangci-lint not installed. Install with: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"; \
	fi

# Generate code coverage report
coverage:
	@echo "Generating coverage report..."
	$(GOTEST) -coverprofile=coverage.out ./...
	$(GOCMD) tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

# Build Docker image
docker-build:
	@echo "Building Docker image..."
	docker build -t itechsmart/agent:$(VERSION) .
	docker tag itechsmart/agent:$(VERSION) itechsmart/agent:latest
	@echo "Docker image built: itechsmart/agent:$(VERSION)"

# Push Docker image
docker-push:
	@echo "Pushing Docker image..."
	docker push itechsmart/agent:$(VERSION)
	docker push itechsmart/agent:latest
	@echo "Docker image pushed"

# Create release packages
release: build-all
	@echo "Creating release packages..."
	@mkdir -p $(DIST_DIR)/packages
	@for platform in $(PLATFORMS); do \
		for arch in $(ARCHITECTURES); do \
			binary_name=$(BINARY_NAME)-$$platform-$$arch; \
			if [ $$platform = "windows" ]; then \
				binary_name=$$binary_name.exe; \
			fi; \
			package_name=$(BINARY_NAME)-$(VERSION)-$$platform-$$arch; \
			if [ $$platform = "windows" ]; then \
				zip -j $(DIST_DIR)/packages/$$package_name.zip $(DIST_DIR)/$$binary_name configs/agent.yaml README.md; \
			else \
				tar -czf $(DIST_DIR)/packages/$$package_name.tar.gz -C $(DIST_DIR) $$binary_name -C ../configs agent.yaml -C .. README.md; \
			fi; \
		done \
	done
	@echo "Release packages created in $(DIST_DIR)/packages/"

# Show help
help:
	@echo "iTechSmart Agent Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all          - Clean, download deps, test, and build"
	@echo "  build        - Build for current platform"
	@echo "  build-all    - Build for all platforms"
	@echo "  clean        - Remove build artifacts"
	@echo "  test         - Run tests"
	@echo "  deps         - Download dependencies"
	@echo "  install      - Install agent (requires root/admin)"
	@echo "  uninstall    - Uninstall agent (requires root/admin)"
	@echo "  run          - Build and run agent"
	@echo "  fmt          - Format code"
	@echo "  lint         - Lint code"
	@echo "  coverage     - Generate coverage report"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-push  - Push Docker image"
	@echo "  release      - Create release packages"
	@echo "  help         - Show this help message"