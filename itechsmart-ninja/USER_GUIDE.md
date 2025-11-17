# iTechSmart Ninja - Complete User Guide

**Version**: 1.0.0  
**Last Updated**: November 17, 2025  
**Product Type**: Personal AI Agent Platform

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Core Features](#core-features)
4. [AI & Intelligence](#ai--intelligence)
5. [Development & Execution](#development--execution)
6. [Data & Files](#data--files)
7. [Automation & Workflow](#automation--workflow)
8. [Integration & Communication](#integration--communication)
9. [Security & Privacy](#security--privacy)
10. [Advanced Usage](#advanced-usage)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## Introduction

### What is iTechSmart Ninja?

iTechSmart Ninja is a comprehensive personal AI agent platform designed for the founder of iTechSmart Inc. It provides 25 powerful features for AI-powered automation, development, research, and productivity enhancement.

### Key Benefits

- **AI-Powered**: 5 specialized AI agents for different tasks
- **Development Tools**: Sandbox environments, VMs, terminal access
- **Automation**: Workflow automation with triggers and actions
- **Integration**: 17+ third-party integrations
- **Security**: End-to-end encryption and privacy controls

### System Requirements

**Minimum**:
- CPU: 4 cores
- RAM: 8 GB
- Storage: 20 GB
- OS: Linux, macOS, or Windows with Docker

**Recommended**:
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: 50+ GB SSD
- Network: 100 Mbps+

---

## Getting Started

### Installation

#### Step 1: Prerequisites

Install Docker and Docker Compose:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# macOS
brew install docker docker-compose

# Windows
# Download Docker Desktop from docker.com
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/itechsmart-ninja
```

#### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables**:
```env
# Database
DATABASE_URL=postgresql://ninja:password@postgres:5432/ninja_db

# Redis
REDIS_URL=redis://redis:6379/0

# API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### Step 4: Launch Platform

```bash
# Quick start script
./QUICK_START.sh

# Or manually
docker-compose up -d
```

#### Step 5: Create Founder Account

```bash
# Run account creation script
docker exec -it ninja-backend python scripts/create_founder.py

# Follow prompts to set:
# - Email
# - Password
# - Full name
```

#### Step 6: Access Platform

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000/admin

### First Login

1. Navigate to http://localhost:3000
2. Click "Sign In"
3. Enter your founder credentials
4. You'll be redirected to the dashboard

---

## Core Features

### Dashboard Overview

The main dashboard provides:

- **Quick Actions**: Common tasks and shortcuts
- **Recent Activity**: Latest actions and events
- **System Status**: Health of all services
- **Active Tasks**: Running background jobs
- **Notifications**: Important alerts

### Navigation

- **Home**: Dashboard and overview
- **AI Agents**: Access specialized agents
- **Sandbox**: Development environments
- **Files**: File management
- **Workflows**: Automation builder
- **Integrations**: Third-party connections
- **Settings**: Configuration and preferences

---

## AI & Intelligence

### 1. Specialized AI Agents

iTechSmart Ninja includes 5 specialized AI agents:

#### Coder Agent 💻

**Purpose**: Code generation, debugging, and optimization

**How to Use**:
1. Navigate to AI Agents → Coder
2. Describe your coding task
3. Select programming language
4. Click "Generate Code"

**Example**:
```
Task: "Create a Python function to calculate Fibonacci numbers"
Language: Python
Output: Complete function with tests
```

**Features**:
- Code generation in 20+ languages
- Bug detection and fixing
- Code optimization suggestions
- Documentation generation
- Unit test creation

#### Researcher Agent 🔍

**Purpose**: Information gathering and analysis

**How to Use**:
1. Navigate to AI Agents → Researcher
2. Enter research topic
3. Select depth level (quick, standard, deep)
4. Click "Start Research"

**Example**:
```
Topic: "Latest trends in AI automation"
Depth: Deep
Output: Comprehensive report with sources
```

**Features**:
- Web search and scraping
- Academic paper analysis
- Data synthesis
- Citation management
- Report generation

#### Writer Agent ✍️

**Purpose**: Content creation and editing

**How to Use**:
1. Navigate to AI Agents → Writer
2. Select content type (article, email, report)
3. Provide topic and requirements
4. Click "Generate Content"

**Example**:
```
Type: Blog Post
Topic: "Benefits of AI in Business"
Length: 1000 words
Tone: Professional
Output: Complete article with SEO optimization
```

**Features**:
- Multiple content types
- Tone and style customization
- SEO optimization
- Grammar and spell checking
- Plagiarism detection

#### Analyst Agent 📊

**Purpose**: Data analysis and visualization

**How to Use**:
1. Navigate to AI Agents → Analyst
2. Upload data file or connect data source
3. Select analysis type
4. Click "Analyze"

**Example**:
```
Data: sales_data.csv
Analysis: Trend analysis
Output: Charts, insights, recommendations
```

**Features**:
- Statistical analysis
- Data visualization
- Predictive modeling
- Anomaly detection
- Report generation

#### Debugger Agent 🐛

**Purpose**: Code debugging and error resolution

**How to Use**:
1. Navigate to AI Agents → Debugger
2. Paste error message or code
3. Provide context
4. Click "Debug"

**Example**:
```
Error: "TypeError: 'NoneType' object is not subscriptable"
Code: [paste your code]
Output: Root cause analysis and fix
```

**Features**:
- Error analysis
- Root cause identification
- Fix suggestions
- Code review
- Performance profiling

### 2. Vision Analysis 👁️

**Purpose**: Image and visual content analysis

**Capabilities**:
- OCR (Optical Character Recognition)
- Object detection
- Diagram analysis
- Visual Q&A
- Image classification

**How to Use**:

#### OCR Example
```bash
# Upload image
POST /api/vision/ocr
{
  "image": "base64_encoded_image",
  "language": "en"
}

# Response
{
  "text": "Extracted text from image",
  "confidence": 0.98
}
```

#### Visual Q&A Example
```bash
# Ask question about image
POST /api/vision/qa
{
  "image": "base64_encoded_image",
  "question": "What objects are in this image?"
}

# Response
{
  "answer": "A laptop, coffee mug, and notebook",
  "confidence": 0.95
}
```

### 3. Knowledge Graph 🕸️

**Purpose**: Entity relationship mapping and analysis

**Features**:
- Entity extraction
- Relationship mapping
- Path finding
- Clustering
- Graph visualization

**How to Use**:

1. **Create Knowledge Graph**:
```python
# Add entities
POST /api/knowledge/entities
{
  "name": "Python",
  "type": "Programming Language",
  "properties": {
    "creator": "Guido van Rossum",
    "year": 1991
  }
}

# Add relationships
POST /api/knowledge/relationships
{
  "from": "Python",
  "to": "Django",
  "type": "framework"
}
```

2. **Query Graph**:
```python
# Find relationships
GET /api/knowledge/path?from=Python&to=Web Development

# Response
{
  "path": ["Python", "Django", "Web Development"],
  "relationships": ["framework", "used_for"]
}
```

### 4. Task Memory & Context 🧠

**Purpose**: Maintain conversation context and task history

**Features**:
- Infinite context window
- Semantic search
- Task history
- Context switching
- Memory persistence

**How to Use**:

```python
# Store context
POST /api/memory/context
{
  "task_id": "task_123",
  "context": "Working on Python web scraper",
  "metadata": {
    "language": "Python",
    "framework": "BeautifulSoup"
  }
}

# Retrieve context
GET /api/memory/context/task_123

# Search memory
POST /api/memory/search
{
  "query": "web scraping",
  "limit": 10
}
```

### 5. Asynchronous Tasks ⚡

**Purpose**: Background task processing

**Features**:
- Priority queue
- Task scheduling
- Progress tracking
- Error handling
- Result caching

**How to Use**:

```python
# Create async task
POST /api/tasks/async
{
  "type": "data_processing",
  "priority": "high",
  "params": {
    "file": "large_dataset.csv",
    "operation": "analysis"
  }
}

# Response
{
  "task_id": "async_task_456",
  "status": "queued",
  "estimated_time": "5 minutes"
}

# Check status
GET /api/tasks/async_task_456

# Response
{
  "status": "processing",
  "progress": 45,
  "eta": "2 minutes"
}
```

---

## Development & Execution

### 6. Sandbox Environments 🏖️

**Purpose**: Isolated code execution environments

**Supported Languages** (9):
1. Python
2. JavaScript/Node.js
3. Java
4. C++
5. Go
6. Rust
7. Ruby
8. PHP
9. Shell/Bash

**How to Use**:

1. **Create Sandbox**:
```python
POST /api/sandbox/create
{
  "language": "python",
  "version": "3.11",
  "timeout": 30
}

# Response
{
  "sandbox_id": "sb_789",
  "status": "ready"
}
```

2. **Execute Code**:
```python
POST /api/sandbox/sb_789/execute
{
  "code": "print('Hello, World!')",
  "stdin": ""
}

# Response
{
  "stdout": "Hello, World!\n",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.05
}
```

3. **Install Packages**:
```python
POST /api/sandbox/sb_789/install
{
  "packages": ["requests", "pandas"]
}
```

### 7. Virtual Machines ☁️

**Purpose**: Full VM provisioning and management

**Supported Providers** (6):
1. AWS EC2
2. Google Cloud Compute
3. Azure VMs
4. DigitalOcean Droplets
5. Linode
6. Vultr

**How to Use**:

1. **Create VM**:
```python
POST /api/vms/create
{
  "provider": "aws",
  "instance_type": "t3.medium",
  "os": "ubuntu-22.04",
  "region": "us-east-1"
}

# Response
{
  "vm_id": "vm_101",
  "ip_address": "54.123.45.67",
  "status": "provisioning"
}
```

2. **Connect to VM**:
```bash
# SSH access
ssh -i ~/.ssh/ninja_key ubuntu@54.123.45.67

# Or use web terminal
GET /api/vms/vm_101/terminal
```

3. **Manage VM**:
```python
# Start
POST /api/vms/vm_101/start

# Stop
POST /api/vms/vm_101/stop

# Delete
DELETE /api/vms/vm_101
```

### 8. Terminal Access 💻

**Purpose**: Full shell access with WebSocket support

**Features**:
- Multiple terminal sessions
- Command history
- Tab completion
- File upload/download
- Session persistence

**How to Use**:

1. **Web Terminal**:
   - Navigate to Development → Terminal
   - Click "New Terminal"
   - Start typing commands

2. **WebSocket Connection**:
```javascript
// Connect to terminal
const ws = new WebSocket('ws://localhost:8000/ws/terminal');

// Send command
ws.send(JSON.stringify({
  type: 'command',
  data: 'ls -la'
}));

// Receive output
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log(response.output);
};
```

### 9. Application Hosting 🚀

**Purpose**: Deploy and host applications

**Features**:
- Container orchestration
- Auto-scaling
- Load balancing
- SSL certificates
- Custom domains

**How to Use**:

1. **Deploy Application**:
```python
POST /api/hosting/deploy
{
  "name": "my-app",
  "type": "docker",
  "image": "nginx:latest",
  "port": 80,
  "replicas": 3
}

# Response
{
  "app_id": "app_202",
  "url": "https://my-app.ninja.itechsmart.dev",
  "status": "deploying"
}
```

2. **Scale Application**:
```python
POST /api/hosting/app_202/scale
{
  "replicas": 5
}
```

3. **View Logs**:
```python
GET /api/hosting/app_202/logs?tail=100
```

### 10. Plugin Ecosystem 🔌

**Purpose**: Extend functionality with plugins

**Features**:
- Plugin marketplace
- Version management
- Dependency resolution
- Auto-updates
- Sandboxed execution

**How to Use**:

1. **Browse Plugins**:
```python
GET /api/plugins/marketplace

# Response
{
  "plugins": [
    {
      "id": "plugin_301",
      "name": "Advanced Analytics",
      "version": "1.2.0",
      "rating": 4.8
    }
  ]
}
```

2. **Install Plugin**:
```python
POST /api/plugins/install
{
  "plugin_id": "plugin_301"
}
```

3. **Use Plugin**:
```python
POST /api/plugins/plugin_301/execute
{
  "action": "analyze",
  "params": {
    "data": "..."
  }
}
```

---

## Data & Files

### 11. File Upload & Parsing 📁

**Supported Formats** (15+):
- Documents: PDF, DOCX, TXT, MD
- Spreadsheets: XLSX, CSV, XLS
- Images: JPG, PNG, GIF, SVG
- Code: PY, JS, JAVA, CPP
- Archives: ZIP, TAR, GZ

**How to Use**:

1. **Upload File**:
```python
POST /api/files/upload
Content-Type: multipart/form-data

file: [binary data]
```

2. **Parse File**:
```python
POST /api/files/parse
{
  "file_id": "file_401",
  "extract_text": true,
  "extract_metadata": true
}

# Response
{
  "text": "Extracted content...",
  "metadata": {
    "pages": 10,
    "author": "John Doe",
    "created": "2025-01-01"
  }
}
```

3. **Search Files**:
```python
POST /api/files/search
{
  "query": "machine learning",
  "file_types": ["pdf", "docx"]
}
```

### 12. Image Editing 🎨

**Filters** (8):
- Grayscale
- Sepia
- Blur
- Sharpen
- Edge Detection
- Emboss
- Vintage
- HDR

**Enhancements** (4):
- Brightness
- Contrast
- Saturation
- Hue

**How to Use**:

```python
POST /api/images/edit
{
  "image_id": "img_501",
  "operations": [
    {
      "type": "filter",
      "name": "sharpen",
      "intensity": 0.8
    },
    {
      "type": "enhance",
      "name": "brightness",
      "value": 1.2
    }
  ]
}

# Response
{
  "edited_image_id": "img_502",
  "url": "/files/img_502.jpg"
}
```

### 13. Performance Analytics 📊

**Metrics Tracked**:
- API response times
- Database query performance
- Memory usage
- CPU utilization
- Network I/O
- Error rates

**How to Use**:

1. **View Dashboard**:
   - Navigate to Analytics → Performance
   - View real-time metrics
   - Set up alerts

2. **Query Metrics**:
```python
GET /api/analytics/metrics?
  metric=api_response_time&
  start=2025-01-01&
  end=2025-01-31

# Response
{
  "data": [
    {"timestamp": "2025-01-01T00:00:00Z", "value": 45.2},
    {"timestamp": "2025-01-01T01:00:00Z", "value": 42.8}
  ],
  "average": 44.0,
  "p95": 67.3
}
```

---

## Automation & Workflow

### 14. Workflow Automation 🔄

**Triggers** (5):
1. Schedule (cron)
2. Webhook
3. File upload
4. Email received
5. Manual

**Actions** (10):
1. Run code
2. Send email
3. Create file
4. Call API
5. Execute command
6. Send notification
7. Update database
8. Transform data
9. Generate report
10. Trigger another workflow

**How to Use**:

1. **Create Workflow**:
```python
POST /api/workflows/create
{
  "name": "Daily Report Generator",
  "trigger": {
    "type": "schedule",
    "cron": "0 9 * * *"
  },
  "actions": [
    {
      "type": "run_code",
      "language": "python",
      "code": "# Generate report code"
    },
    {
      "type": "send_email",
      "to": "founder@itechsmart.com",
      "subject": "Daily Report",
      "body": "{{report_output}}"
    }
  ]
}
```

2. **Test Workflow**:
```python
POST /api/workflows/wf_601/test
```

3. **Enable Workflow**:
```python
POST /api/workflows/wf_601/enable
```

### 15. Calendar & Scheduling 📅

**Features**:
- Event creation
- Recurring events
- Availability checking
- Reminders
- Integration with Google Calendar

**How to Use**:

```python
# Create event
POST /api/calendar/events
{
  "title": "Team Meeting",
  "start": "2025-01-15T10:00:00Z",
  "end": "2025-01-15T11:00:00Z",
  "recurring": "weekly",
  "reminders": [15, 60]
}

# Check availability
GET /api/calendar/availability?
  start=2025-01-15T09:00:00Z&
  end=2025-01-15T17:00:00Z
```

### 16. Action History ⏮️

**Features**:
- Undo/redo operations
- State snapshots
- Rollback capability
- Audit trail
- Version history

**How to Use**:

```python
# View history
GET /api/history?limit=50

# Undo last action
POST /api/history/undo

# Redo action
POST /api/history/redo

# Rollback to specific point
POST /api/history/rollback
{
  "snapshot_id": "snap_701"
}
```

---

## Integration & Communication

### 17. Google Drive 💾

**Features**:
- File sync
- Bidirectional sync
- Real-time updates
- Folder management
- Sharing controls

**Setup**:

1. **Connect Account**:
   - Navigate to Integrations → Google Drive
   - Click "Connect"
   - Authorize access

2. **Configure Sync**:
```python
POST /api/integrations/gdrive/sync
{
  "folder": "/Ninja Files",
  "direction": "bidirectional",
  "auto_sync": true
}
```

### 18. Slack 💬

**Features**:
- Send messages
- Receive notifications
- Slash commands
- Bot integration
- Channel management

**Setup**:

1. **Connect Workspace**:
   - Navigate to Integrations → Slack
   - Click "Add to Slack"
   - Authorize

2. **Send Message**:
```python
POST /api/integrations/slack/message
{
  "channel": "#general",
  "text": "Task completed successfully!"
}
```

3. **Create Slash Command**:
```python
POST /api/integrations/slack/commands
{
  "command": "/ninja",
  "description": "Execute Ninja commands",
  "url": "https://ninja.itechsmart.dev/api/slack/commands"
}
```

### 19. Chat & Collaboration 💭

**Features**:
- Real-time messaging
- Thread support
- File sharing
- @mentions
- Reactions

**How to Use**:

1. **Web Interface**:
   - Navigate to Chat
   - Select or create channel
   - Start messaging

2. **API**:
```python
# Send message
POST /api/chat/messages
{
  "channel_id": "ch_801",
  "text": "Hello team!",
  "thread_id": null
}

# WebSocket for real-time
ws://localhost:8000/ws/chat/ch_801
```

### 20. GitHub Integration 🐙

**Features**:
- Repository management
- Code commits
- Pull requests
- Issue tracking
- Webhooks

**Setup**:

1. **Connect Account**:
   - Navigate to Integrations → GitHub
   - Click "Connect"
   - Authorize

2. **Create Repository**:
```python
POST /api/integrations/github/repos
{
  "name": "my-project",
  "private": true,
  "description": "My awesome project"
}
```

3. **Commit Code**:
```python
POST /api/integrations/github/repos/my-project/commits
{
  "message": "Initial commit",
  "files": [
    {
      "path": "README.md",
      "content": "# My Project"
    }
  ]
}
```

### 21. Additional Integrations (12)

1. **Jira** - Project management
2. **Gmail** - Email automation
3. **Trello** - Task boards
4. **Asana** - Team collaboration
5. **Notion** - Documentation
6. **Dropbox** - File storage
7. **OneDrive** - Microsoft cloud
8. **Zoom** - Video conferencing
9. **Calendar** - Scheduling
10. **Twitter** - Social media
11. **LinkedIn** - Professional network
12. **Stripe** - Payment processing

---

## Security & Privacy

### 22. Data Privacy Controls 🔒

**GDPR Compliance**:
- Data export
- Data deletion
- Consent management
- Privacy policy
- Cookie controls

**How to Use**:

```python
# Export user data
POST /api/privacy/export
{
  "user_id": "user_901",
  "format": "json"
}

# Delete user data
DELETE /api/privacy/user/user_901

# Manage consent
POST /api/privacy/consent
{
  "user_id": "user_901",
  "analytics": true,
  "marketing": false
}
```

### 23. End-to-End Encryption 🔐

**Encryption Standards**:
- AES-256 for data at rest
- RSA-2048/4096 for key exchange
- TLS 1.3 for data in transit

**Features**:
- Automatic encryption
- Key management
- Secure key storage
- Encrypted backups

**How to Use**:

```python
# Encrypt data
POST /api/encryption/encrypt
{
  "data": "sensitive information",
  "algorithm": "AES-256"
}

# Response
{
  "encrypted_data": "base64_encrypted_string",
  "key_id": "key_1001"
}

# Decrypt data
POST /api/encryption/decrypt
{
  "encrypted_data": "base64_encrypted_string",
  "key_id": "key_1001"
}
```

### 24. Multi-Tenant Workspaces 🏢

**Features** (Simplified for single-user):
- Resource isolation
- Separate databases
- Independent configurations
- Workspace switching

**How to Use**:

```python
# Create workspace
POST /api/workspaces/create
{
  "name": "Personal",
  "description": "My personal workspace"
}

# Switch workspace
POST /api/workspaces/switch
{
  "workspace_id": "ws_1101"
}
```

### 25. Advanced Security 🛡️

**Features**:
- Rate limiting
- Audit logs
- Access control
- IP whitelisting
- 2FA/MFA

**How to Use**:

1. **Enable 2FA**:
   - Navigate to Settings → Security
   - Click "Enable 2FA"
   - Scan QR code with authenticator app

2. **View Audit Logs**:
```python
GET /api/security/audit?
  start=2025-01-01&
  end=2025-01-31&
  action=login
```

3. **Configure Rate Limits**:
```python
POST /api/security/rate-limits
{
  "endpoint": "/api/*",
  "limit": 100,
  "window": "1m"
}
```

---

## Advanced Usage

### API Authentication

All API requests require authentication:

```bash
# Get access token
POST /api/auth/login
{
  "email": "founder@itechsmart.com",
  "password": "your-password"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}

# Use token in requests
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  http://localhost:8000/api/agents/coder
```

### Batch Operations

Execute multiple operations in one request:

```python
POST /api/batch
{
  "operations": [
    {
      "method": "POST",
      "path": "/api/files/upload",
      "body": {...}
    },
    {
      "method": "POST",
      "path": "/api/files/parse",
      "body": {...}
    }
  ]
}
```

### Webhooks

Set up webhooks for event notifications:

```python
POST /api/webhooks/create
{
  "url": "https://your-server.com/webhook",
  "events": ["task.completed", "file.uploaded"],
  "secret": "your-webhook-secret"
}
```

---

## Troubleshooting

### Common Issues

#### 1. Cannot Connect to Database

**Symptoms**: Error connecting to PostgreSQL

**Solution**:
```bash
# Check if database is running
docker ps | grep postgres

# Restart database
docker-compose restart postgres

# Check logs
docker logs ninja-postgres
```

#### 2. API Returns 401 Unauthorized

**Symptoms**: Authentication errors

**Solution**:
```bash
# Verify token is valid
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/auth/verify

# Get new token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"founder@itechsmart.com","password":"your-password"}'
```

#### 3. Slow Performance

**Symptoms**: API requests taking too long

**Solution**:
```bash
# Check resource usage
docker stats

# Scale services
docker-compose up -d --scale backend=3

# Clear cache
curl -X POST http://localhost:8000/api/cache/clear
```

#### 4. File Upload Fails

**Symptoms**: Cannot upload files

**Solution**:
```bash
# Check file size limits
# Edit docker-compose.yml
environment:
  - MAX_FILE_SIZE=100MB

# Restart services
docker-compose restart
```

### Getting Help

- **Documentation**: http://localhost:8000/docs
- **Logs**: `docker-compose logs -f`
- **Support**: support@itechsmart.com
- **GitHub Issues**: https://github.com/Iteksmart/iTechSmart/issues

---

## FAQ

### General Questions

**Q: Is iTechSmart Ninja open source?**  
A: No, it's proprietary software for the founder of iTechSmart Inc.

**Q: Can I use it for commercial purposes?**  
A: Yes, as the founder, you have full commercial rights.

**Q: What's the difference between Ninja and other iTechSmart products?**  
A: Ninja is a personal AI agent platform, while other products are enterprise solutions.

### Technical Questions

**Q: What databases are supported?**  
A: PostgreSQL 15+ is required. Redis is used for caching.

**Q: Can I run it without Docker?**  
A: Yes, but Docker is recommended for easier deployment.

**Q: How do I backup my data?**  
A: Use the backup script: `./scripts/backup.sh`

**Q: Can I customize the AI agents?**  
A: Yes, agents can be customized through the API and configuration files.

### Security Questions

**Q: Is my data encrypted?**  
A: Yes, all data is encrypted at rest (AES-256) and in transit (TLS 1.3).

**Q: Where is data stored?**  
A: Data is stored in your PostgreSQL database and file storage.

**Q: Can I export my data?**  
A: Yes, use the data export feature in Settings → Privacy.

---

## Appendix

### API Endpoints Summary

| Category | Endpoints | Count |
|----------|-----------|-------|
| AI Agents | /api/agents/* | 25 |
| Sandbox | /api/sandbox/* | 15 |
| Files | /api/files/* | 20 |
| Workflows | /api/workflows/* | 18 |
| Integrations | /api/integrations/* | 50 |
| Security | /api/security/* | 12 |
| **Total** | | **290+** |

### Environment Variables Reference

```env
# Core
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=your-secret-key

# AI
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASSWORD=your-password

# Storage
STORAGE_TYPE=local|s3|gcs
STORAGE_PATH=/data/files

# Security
JWT_SECRET=your-jwt-secret
JWT_EXPIRATION=3600
ENABLE_2FA=true

# Performance
MAX_WORKERS=4
CACHE_TTL=3600
RATE_LIMIT=100
```

### Docker Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Scale service
docker-compose up -d --scale backend=3

# Execute command
docker exec -it ninja-backend python manage.py

# Backup database
docker exec ninja-postgres pg_dump -U ninja ninja_db > backup.sql

# Restore database
docker exec -i ninja-postgres psql -U ninja ninja_db < backup.sql
```

---

**End of User Guide**

For the latest updates and API documentation, visit:
- API Docs: http://localhost:8000/docs
- GitHub: https://github.com/Iteksmart/iTechSmart
- Support: support@itechsmart.com