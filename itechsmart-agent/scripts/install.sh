#!/bin/bash
# iTechSmart Agent Installation Script
# Copyright © 2025 iTechSmart Inc. All rights reserved.

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
VERSION="1.0.0"
BINARY_NAME="itechsmart-agent"
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="/etc/itechsmart"
LOG_DIR="/var/log/itechsmart"
SERVICE_NAME="itechsmart-agent"

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case $ARCH in
    x86_64)
        ARCH="amd64"
        ;;
    aarch64|arm64)
        ARCH="arm64"
        ;;
    *)
        echo -e "${RED}Unsupported architecture: $ARCH${NC}"
        exit 1
        ;;
esac

# Parse arguments
API_KEY=""
ORGANIZATION=""
AGENT_NAME=$(hostname)

while [[ $# -gt 0 ]]; do
    case $1 in
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --organization)
            ORGANIZATION="$2"
            shift 2
            ;;
        --agent-name)
            AGENT_NAME="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}iTechSmart Agent Installation${NC}"
echo -e "${GREEN}Version: $VERSION${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check for API key
if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}API Key is required${NC}"
    read -p "Enter your iTechSmart API Key: " API_KEY
    if [ -z "$API_KEY" ]; then
        echo -e "${RED}API Key cannot be empty${NC}"
        exit 1
    fi
fi

# Download binary
echo -e "${GREEN}Downloading iTechSmart Agent...${NC}"
DOWNLOAD_URL="https://github.com/Iteksmart/iTechSmart/releases/download/v${VERSION}/${BINARY_NAME}-${OS}-${ARCH}"
if [ "$OS" = "darwin" ]; then
    DOWNLOAD_URL="https://github.com/Iteksmart/iTechSmart/releases/download/v${VERSION}/${BINARY_NAME}-darwin-${ARCH}"
fi

curl -L -o "/tmp/${BINARY_NAME}" "$DOWNLOAD_URL"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to download agent${NC}"
    exit 1
fi

# Install binary
echo -e "${GREEN}Installing agent...${NC}"
chmod +x "/tmp/${BINARY_NAME}"
mv "/tmp/${BINARY_NAME}" "${INSTALL_DIR}/${BINARY_NAME}"

# Create directories
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"

# Create configuration file
echo -e "${GREEN}Creating configuration...${NC}"
cat > "${CONFIG_DIR}/agent.yaml" << EOF
# iTechSmart Agent Configuration
agent_name: "${AGENT_NAME}"
organization: "${ORGANIZATION}"
server_url: "https://api.itechsmart.dev"
websocket_url: "wss://api.itechsmart.dev/agent/ws"
api_key: "${API_KEY}"

# Collection intervals (seconds)
system_metrics_interval: 60
security_check_interval: 3600
software_inventory_interval: 86400

# Features
enable_system_monitoring: true
enable_security_checks: true
enable_software_inventory: true
enable_remote_commands: true
enable_patch_management: true
enable_audit_logging: true

# Logging
log_level: "info"
log_file: "${LOG_DIR}/agent.log"

# Product integration
ninja_enabled: true
enterprise_enabled: true
EOF

# Install as service
echo -e "${GREEN}Installing as system service...${NC}"

if [ "$OS" = "linux" ]; then
    # Create systemd service
    cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=iTechSmart Agent
After=network.target

[Service]
Type=simple
User=root
ExecStart=${INSTALL_DIR}/${BINARY_NAME} --config ${CONFIG_DIR}/agent.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable ${SERVICE_NAME}
    systemctl start ${SERVICE_NAME}
    
    echo -e "${GREEN}Service installed and started${NC}"
    
elif [ "$OS" = "darwin" ]; then
    # Create launchd plist
    cat > "/Library/LaunchDaemons/com.itechsmart.agent.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.itechsmart.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>${INSTALL_DIR}/${BINARY_NAME}</string>
        <string>--config</string>
        <string>${CONFIG_DIR}/agent.yaml</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/agent.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/agent-error.log</string>
</dict>
</plist>
EOF

    # Load service
    launchctl load /Library/LaunchDaemons/com.itechsmart.agent.plist
    
    echo -e "${GREEN}Service installed and started${NC}"
fi

# Verify installation
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Agent installed to: ${INSTALL_DIR}/${BINARY_NAME}"
echo -e "Configuration: ${CONFIG_DIR}/agent.yaml"
echo -e "Logs: ${LOG_DIR}/agent.log"
echo ""
echo -e "Service status:"
if [ "$OS" = "linux" ]; then
    systemctl status ${SERVICE_NAME} --no-pager
elif [ "$OS" = "darwin" ]; then
    launchctl list | grep itechsmart
fi
echo ""
echo -e "${GREEN}The iTechSmart Agent is now monitoring your system!${NC}"
echo -e "View logs: tail -f ${LOG_DIR}/agent.log"
echo ""