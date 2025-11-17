# 🤖 iTechSmart Agent

**Version**: 1.0.0  
**Date**: November 17, 2025  
**Company**: iTechSmart Inc  
**Copyright**: © 2025 iTechSmart Inc. All rights reserved.

---

## 🎯 Overview

iTechSmart Agent is a lightweight, cross-platform system monitoring and management agent that communicates with the iTechSmart Cloud Platform. It provides real-time visibility and control over your IT infrastructure.

### Key Features

✅ **Real-time System Monitoring**
- CPU, Memory, Disk, Network metrics
- Process monitoring
- Performance tracking

✅ **Security & Compliance**
- Firewall status monitoring
- Antivirus status tracking
- Security event logging
- Compliance checks (password policy, encryption, updates)
- Failed login attempt tracking

✅ **Software Management**
- Complete software inventory
- License tracking and compliance
- Available updates detection
- Remote software installation/uninstallation
- Automated patch management

✅ **Failure Prediction** (NEW in v1.3.0)
- ML-based prediction models
- Historical data analysis
- Anomaly detection
- Proactive failure alerts
- Confidence scoring

✅ **Automated Remediation** (NEW in v1.3.0)
- Automatic issue resolution
- Configurable remediation rules
- Action execution engine
- Remediation history tracking
- Approval workflows

✅ **Capacity Planning** (NEW in v1.3.0)
- Resource forecasting
- Trend analysis
- Growth rate calculation
- Time-to-exhaustion estimates
- Capacity reports and recommendations

✅ **Remote Management**
- Remote command execution
- Script execution (PowerShell, Bash)
- File transfer (upload/download)
- System restart capability
- Diagnostics execution

✅ **Proactive Alerts**
- High CPU/Memory/Disk usage alerts
- Security compliance alerts
- Software update alerts
- Custom alert rules

✅ **Comprehensive Logging**
- All agent activities logged
- Audit trail for compliance
- Configurable log levels
- Log rotation and retention

✅ **Product Integration**
- iTechSmart Ninja integration
- iTechSmart Enterprise integration
- iTechSmart License Server integration

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                iTechSmart Cloud Platform                     │
│           (License Server, Ninja, Enterprise)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket (TLS 1.3)
                              │ Encrypted & Authenticated
                              │
┌─────────────────────────────────────────────────────────────┐
│                    iTechSmart Agent                          │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   System     │  │   Security   │  │   Software   │      │
│  │  Collector   │  │  Collector   │  │  Collector   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Communicator │  │   Executor   │  │    Logger    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Local System (Windows/macOS/Linux)              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- **Operating System**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+, RHEL 8+)
- **Architecture**: x86_64 (AMD64) or ARM64
- **Network**: Internet connectivity to iTechSmart Cloud Platform
- **Permissions**: Administrator/root privileges for installation

### Quick Install

#### Windows (PowerShell as Administrator)
```powershell
# Download and install
Invoke-WebRequest -Uri "https://downloads.itechsmart.dev/agent/windows/install.ps1" -OutFile "install.ps1"
.\install.ps1 -ApiKey "YOUR_API_KEY"
```

#### macOS/Linux
```bash
# Download and install
curl -fsSL https://downloads.itechsmart.dev/agent/install.sh | sudo bash -s -- --api-key YOUR_API_KEY
```

### Manual Installation

#### 1. Download Agent Binary

**Windows**:
```powershell
# Download from GitHub releases
Invoke-WebRequest -Uri "https://github.com/Iteksmart/iTechSmart/releases/download/v1.3.0/itechsmart-agent-windows-amd64.exe" -OutFile "itechsmart-agent.exe"
```

**macOS**:
```bash
# Download from GitHub releases
curl -L -o itechsmart-agent "https://github.com/Iteksmart/iTechSmart/releases/download/v1.3.0/itechsmart-agent-darwin-amd64"
chmod +x itechsmart-agent
```

**Linux**:
```bash
# Download from GitHub releases
curl -L -o itechsmart-agent "https://github.com/Iteksmart/iTechSmart/releases/download/v1.3.0/itechsmart-agent-linux-amd64"
chmod +x itechsmart-agent
```

#### 2. Create Configuration File

```bash
# Create config directory
sudo mkdir -p /etc/itechsmart

# Create configuration file
sudo nano /etc/itechsmart/agent.yaml
```

Add your configuration:
```yaml
agent_name: "my-server"
organization: "My Company"
server_url: "https://api.itechsmart.dev"
websocket_url: "wss://api.itechsmart.dev/agent/ws"
api_key: "YOUR_API_KEY_HERE"
```

#### 3. Install as Service

**Windows** (PowerShell as Administrator):
```powershell
# Install service
.\itechsmart-agent.exe install

# Start service
Start-Service iTechSmartAgent
```

**macOS**:
```bash
# Copy binary
sudo cp itechsmart-agent /usr/local/bin/

# Create launchd plist
sudo nano /Library/LaunchDaemons/com.itechsmart.agent.plist
```

Add:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.itechsmart.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/itechsmart-agent</string>
        <string>--config</string>
        <string>/etc/itechsmart/agent.yaml</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
# Load service
sudo launchctl load /Library/LaunchDaemons/com.itechsmart.agent.plist
```

**Linux (systemd)**:
```bash
# Copy binary
sudo cp itechsmart-agent /usr/local/bin/

# Create systemd service
sudo nano /etc/systemd/system/itechsmart-agent.service
```

Add:
```ini
[Unit]
Description=iTechSmart Agent
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/itechsmart-agent --config /etc/itechsmart/agent.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable itechsmart-agent
sudo systemctl start itechsmart-agent
```

---

## ⚙️ Configuration

### Configuration File Location

- **Windows**: `C:\ProgramData\iTechSmart\agent.yaml`
- **macOS**: `/etc/itechsmart/agent.yaml`
- **Linux**: `/etc/itechsmart/agent.yaml`

### Configuration Options

```yaml
# Agent identification
agent_id: ""              # Auto-generated if not set
agent_name: "my-server"   # Friendly name
organization: "My Org"    # Organization name

# Server configuration
server_url: "https://api.itechsmart.dev"
websocket_url: "wss://api.itechsmart.dev/agent/ws"
api_key: "YOUR_API_KEY"   # Required

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

# Logging
log_level: "info"
log_file: "/var/log/itechsmart/agent.log"

# Product integration
ninja_enabled: true
enterprise_enabled: true
```

### Environment Variables

You can also configure the agent using environment variables:

```bash
export ITECHSMART_API_KEY="your-api-key"
export ITECHSMART_SERVER_URL="https://api.itechsmart.dev"
export ITECHSMART_LOG_LEVEL="debug"
```

---

## 🚀 Usage

### Command Line Interface

```bash
# Start agent (foreground)
itechsmart-agent

# Start with custom config
itechsmart-agent --config /path/to/config.yaml

# Show version
itechsmart-agent version

# Check status
itechsmart-agent status

# Install as service
itechsmart-agent install

# Uninstall service
itechsmart-agent uninstall
```

### Service Management

**Windows**:
```powershell
# Start service
Start-Service iTechSmartAgent

# Stop service
Stop-Service iTechSmartAgent

# Restart service
Restart-Service iTechSmartAgent

# Check status
Get-Service iTechSmartAgent
```

**macOS**:
```bash
# Start service
sudo launchctl start com.itechsmart.agent

# Stop service
sudo launchctl stop com.itechsmart.agent

# Check status
sudo launchctl list | grep itechsmart
```

**Linux**:
```bash
# Start service
sudo systemctl start itechsmart-agent

# Stop service
sudo systemctl stop itechsmart-agent

# Restart service
sudo systemctl restart itechsmart-agent

# Check status
sudo systemctl status itechsmart-agent

# View logs
sudo journalctl -u itechsmart-agent -f
```

---

## 📊 Monitoring

### Metrics Collected

#### System Metrics (every 60 seconds)
- CPU usage (overall and per-core)
- Memory usage (RAM and swap)
- Disk usage (all partitions)
- Network I/O (all interfaces)
- System uptime
- Process count

#### Security Metrics (every hour)
- Firewall status
- Antivirus status
- System update status
- Open ports
- Active users
- Failed login attempts
- Compliance checks

#### Software Inventory (daily)
- Installed software list
- Software versions
- Available updates
- License information

### Alerts

The agent automatically sends alerts for:
- High CPU usage (>90%)
- High memory usage (>90%)
- Low disk space (>90% full)
- Firewall disabled
- Antivirus disabled
- Failed compliance checks
- Available critical/security updates

---

## 🔒 Security

### Communication Security
- **TLS 1.3**: All communication encrypted
- **Certificate Pinning**: Prevents MITM attacks
- **API Key Authentication**: Secure agent authentication
- **WebSocket Secure (WSS)**: Real-time encrypted communication

### Data Security
- **Data Minimization**: Only necessary data collected
- **No PII Collection**: Personal information excluded
- **Secure Storage**: Sensitive data encrypted at rest
- **Audit Logging**: All actions logged

### Permissions
- **Least Privilege**: Minimal permissions required
- **Sandboxing**: Limited system access
- **Code Signing**: Binaries are signed
- **Integrity Checks**: Agent integrity verified

---

## 🔧 Troubleshooting

### Agent Won't Start

**Check logs**:
```bash
# Linux/macOS
tail -f /var/log/itechsmart/agent.log

# Windows
Get-Content C:\ProgramData\iTechSmart\logs\agent.log -Tail 50 -Wait
```

**Common issues**:
1. Missing API key
2. Network connectivity
3. Firewall blocking
4. Insufficient permissions

### Agent Not Connecting

**Test connectivity**:
```bash
# Test WebSocket endpoint
curl -I https://api.itechsmart.dev/health

# Check DNS resolution
nslookup api.itechsmart.dev

# Check firewall
# Ensure outbound HTTPS (443) is allowed
```

### High Resource Usage

**Check configuration**:
```yaml
# Increase collection intervals
system_metrics_interval: 300  # 5 minutes instead of 1
security_check_interval: 7200  # 2 hours instead of 1
```

### Logs

**View logs**:
```bash
# Linux
sudo tail -f /var/log/itechsmart/agent.log

# macOS
sudo tail -f /var/log/itechsmart/agent.log

# Windows (PowerShell)
Get-Content C:\ProgramData\iTechSmart\logs\agent.log -Tail 50 -Wait
```

**Increase log verbosity**:
```yaml
log_level: "debug"
```

---

## 🔄 Updates

### Automatic Updates

The agent can update itself automatically when new versions are available:

```yaml
enable_auto_update: true
update_channel: "stable"  # stable, beta, dev
```

### Manual Update

**Windows**:
```powershell
# Stop service
Stop-Service iTechSmartAgent

# Download new version
Invoke-WebRequest -Uri "https://downloads.itechsmart.dev/agent/windows/latest.exe" -OutFile "itechsmart-agent.exe"

# Start service
Start-Service iTechSmartAgent
```

**macOS/Linux**:
```bash
# Stop service
sudo systemctl stop itechsmart-agent

# Download new version
curl -L -o /usr/local/bin/itechsmart-agent "https://downloads.itechsmart.dev/agent/linux/latest"
chmod +x /usr/local/bin/itechsmart-agent

# Start service
sudo systemctl start itechsmart-agent
```

---

## 🛠️ Development

### Building from Source

#### Prerequisites
- Go 1.21 or later
- Git

#### Build

```bash
# Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/itechsmart-agent

# Install dependencies
go mod download

# Build for current platform
go build -o itechsmart-agent cmd/agent/main.go

# Build for all platforms
make build-all
```

#### Cross-Compilation

```bash
# Windows
GOOS=windows GOARCH=amd64 go build -o itechsmart-agent.exe cmd/agent/main.go

# macOS
GOOS=darwin GOARCH=amd64 go build -o itechsmart-agent-darwin cmd/agent/main.go

# Linux
GOOS=linux GOARCH=amd64 go build -o itechsmart-agent-linux cmd/agent/main.go
```

---

## 📞 Support

### Documentation
- **User Guide**: https://docs.itechsmart.dev/agent
- **API Documentation**: https://docs.itechsmart.dev/api
- **GitHub**: https://github.com/Iteksmart/iTechSmart

### Contact
- **Email**: support@itechsmart.dev
- **Enterprise Support**: enterprise@itechsmart.dev
- **GitHub Issues**: https://github.com/Iteksmart/iTechSmart/issues

### Community
- **Discussions**: https://github.com/Iteksmart/iTechSmart/discussions
- **Slack**: https://itechsmart.slack.com

---

## 📄 License

Copyright © 2025 iTechSmart Inc. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, modification, distribution, or use is strictly prohibited.

---

## 🎯 Roadmap

### Version 1.1 (Q1 2026)
- [ ] Enhanced AI-powered anomaly detection
- [ ] Predictive maintenance alerts
- [ ] Custom script library
- [ ] Advanced reporting

### Version 1.2 (Q2 2026)
- [ ] Container monitoring (Docker, Kubernetes)
- [ ] Cloud resource monitoring (AWS, Azure, GCP)
- [ ] Application performance monitoring
- [ ] Custom dashboards

### Version 2.0 (Q3 2026)
- [ ] Machine learning insights
- [ ] Auto-remediation
- [ ] Advanced automation workflows
- [ ] Multi-tenant support

---

**© 2025 iTechSmart Inc. All rights reserved.**  
**Founder & CEO**: DJuane Jackson  
**Website**: https://itechsmart.dev

**The iTechSmart Agent - Intelligent System Management** 🤖
## 🤖 Agent Integration

This product integrates with the iTechSmart Agent monitoring system through the License Server. The agent system provides:

- Real-time system monitoring
- Performance metrics collection
- Security status tracking
- Automated alerting

### Configuration

Set the License Server URL in your environment:

```bash
LICENSE_SERVER_URL=http://localhost:3000
```

The product will automatically connect to the License Server to access agent data and monitoring capabilities.

