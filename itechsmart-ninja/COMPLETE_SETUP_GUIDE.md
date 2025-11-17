# iTechSmart Ninja - Complete Setup & Usage Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Starting the System](#starting-the-system)
5. [Using Each Feature](#using-each-feature)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.11 or higher
- **Node.js**: 20.x or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB free space
- **Internet**: Stable internet connection required

### Required Software
- Python 3.11+
- Node.js 20.x
- npm (comes with Node.js)
- VS Code (latest version)
- Docker (optional, for containerized deployment)

---

## Installation

### Step 1: Clone or Extract the Project

```bash
# If you have the project as a zip file
unzip itechsmart-ninja.zip
cd itechsmart-ninja

# Or if cloning from git
git clone <repository-url>
cd itechsmart-ninja
```

### Step 2: Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Backend Dependencies Include:**
- FastAPI (web framework)
- Uvicorn (ASGI server)
- SQLAlchemy (database ORM)
- Pydantic (data validation)
- OpenAI, Anthropic, Google AI SDKs
- And 40+ other packages

### Step 3: Install VS Code Extension

```bash
# Navigate to VS Code extension directory
cd ../vscode-extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile
```

### Step 4: Install the Extension in VS Code

**Option A: Development Mode (Recommended for testing)**
1. Open VS Code
2. Press `F5` to open Extension Development Host
3. The extension will be loaded automatically

**Option B: Package and Install**
```bash
# Install vsce (VS Code Extension packager)
npm install -g @vscode/vsce

# Package the extension
vsce package

# Install the .vsix file in VS Code
# Go to Extensions → ... → Install from VSIX
```

---

## Configuration

### Step 1: Create Environment File

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

### Step 2: Configure API Keys

Edit the `.env` file and add your API keys:

```bash
# Database
DATABASE_URL=sqlite:///./itechsmart.db

# Security
SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Providers (Add the ones you want to use)

# OpenAI (Required for DALL-E and GPT models)
OPENAI_API_KEY=sk-your-openai-key-here

# Anthropic (Required for Claude models)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Google (Required for Gemini models)
GOOGLE_API_KEY=your-google-api-key-here

# DeepSeek (Optional)
DEEPSEEK_API_KEY=your-deepseek-key-here

# Mistral (Optional)
MISTRAL_API_KEY=your-mistral-key-here

# Cohere (Optional)
COHERE_API_KEY=your-cohere-key-here

# Replicate (Required for FLUX image generation)
REPLICATE_API_KEY=your-replicate-key-here

# Stability AI (Optional for Stable Diffusion)
STABILITY_API_KEY=your-stability-key-here

# GitHub (Required for GitHub integration)
GITHUB_TOKEN=ghp_your-github-token-here

# Web Search (Optional but recommended)
GOOGLE_SEARCH_API_KEY=your-google-search-key-here
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id-here
BING_SEARCH_API_KEY=your-bing-search-key-here
```

### Step 3: Get API Keys

#### OpenAI (Required)
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key and add to `.env`

#### Anthropic (Required)
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy and add to `.env`

#### Google AI (Required)
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and add to `.env`

#### Replicate (For Image Generation)
1. Go to https://replicate.com/account/api-tokens
2. Sign up or log in
3. Create a new token
4. Copy and add to `.env`

#### GitHub (For GitHub Integration)
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`, `read:org`
4. Generate and copy token
5. Add to `.env`

### Step 4: Initialize Database

```bash
# Make sure you're in the backend directory with venv activated
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run database initialization
python -c "from app.core.database import init_db; init_db()"
```

---

## Starting the System

### Step 1: Start the Backend Server

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend is Running:**
- Open browser: http://localhost:8000
- You should see: `{"message": "iTechSmart Ninja API"}`
- API Docs: http://localhost:8000/docs

### Step 2: Start VS Code with Extension

1. Open VS Code
2. Press `F5` to start Extension Development Host
3. Or if installed: Just open VS Code normally

### Step 3: Configure VS Code Extension

1. Open VS Code Settings (`Ctrl+,` or `Cmd+,`)
2. Search for "iTechSmart"
3. Configure:
   - **API URL**: `http://localhost:8000` (default)
   - **Default Agent**: Choose your preferred agent
   - **Auto Save**: Enable/disable
   - **Show Notifications**: Enable/disable

---

## Using Each Feature

### Feature 1: Enhanced Multi-AI Model Support

#### Via VS Code Command Palette

1. **Browse Available Models**
   ```
   Ctrl+Shift+P → iTechSmart: Browse AI Models
   ```
   - View all 42 available models
   - See provider, cost, and capabilities

2. **Select a Model**
   ```
   Ctrl+Shift+P → iTechSmart: Select AI Model
   ```
   - Choose from dropdown
   - Model is saved for future use

3. **Compare Models**
   ```
   Ctrl+Shift+P → iTechSmart: Compare AI Models
   ```
   - Select 2-4 models
   - View side-by-side comparison

4. **Get Recommendations**
   ```
   Ctrl+Shift+P → iTechSmart: Get Model Recommendations
   ```
   - Specify task type
   - Get AI-powered recommendations

5. **View Usage Statistics**
   ```
   Ctrl+Shift+P → iTechSmart: Show Model Usage Stats
   ```
   - See usage by model
   - View costs
   - Track performance

#### Via Terminal

1. **Open iTechSmart Terminal**
   ```
   Ctrl+Shift+I
   ```

2. **Available Commands**
   ```bash
   # List all models
   models

   # Select a model
   select-model

   # Compare models
   compare-models

   # Get recommendations
   recommend-model

   # View usage stats
   model-stats

   # Check provider status
   provider-status
   ```

#### Via API

```bash
# List all models
curl http://localhost:8000/api/models

# Get model details
curl http://localhost:8000/api/models/gpt-4o

# Compare models
curl -X POST http://localhost:8000/api/models/compare \
  -H "Content-Type: application/json" \
  -d '{"models": ["gpt-4o", "claude-3-opus", "gemini-pro"]}'

# Get recommendations
curl -X POST http://localhost:8000/api/models/recommend \
  -H "Content-Type: application/json" \
  -d '{"task_type": "code_generation", "budget": "medium"}'
```

---

### Feature 2: Deep Research with Citations

#### Via VS Code Command Palette

1. **Perform Deep Research**
   ```
   Ctrl+Shift+P → iTechSmart: Perform Deep Research
   ```
   - Enter your research query
   - Select citation style (APA, MLA, Chicago, Harvard, IEEE)
   - Wait for comprehensive report
   - Report opens in new editor

2. **Format Citation**
   ```
   Ctrl+Shift+P → iTechSmart: Format Citation
   ```
   - Enter source URL
   - Select citation style
   - Get formatted citation

3. **Check Source Credibility**
   ```
   Ctrl+Shift+P → iTechSmart: Check Source Credibility
   ```
   - Enter source URL
   - Get credibility score (0-100)
   - See detailed analysis

4. **View Citation Styles**
   ```
   Ctrl+Shift+P → iTechSmart: View Citation Styles
   ```
   - See all 5 supported styles
   - View examples

#### Via Terminal

```bash
# Open terminal
Ctrl+Shift+I

# Perform research
research "artificial intelligence trends 2025"

# Format citation
cite "https://example.com/article"

# Check credibility
credibility "https://example.com/article"

# View citation styles
citation-styles
```

#### Via API

```bash
# Perform deep research
curl -X POST http://localhost:8000/api/research/deep \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "artificial intelligence trends 2025",
    "citation_style": "apa",
    "max_sources": 10
  }'

# Format citation
curl -X POST http://localhost:8000/api/research/cite \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "style": "mla"
  }'

# Check credibility
curl -X POST http://localhost:8000/api/research/credibility \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

---

### Feature 3: Embedded Code Editors

#### Via VS Code Command Palette

1. **Monaco Code Editor**
   ```
   Ctrl+Shift+P → iTechSmart: Open Monaco Editor
   ```
   - Select language (20+ supported)
   - Start coding with IntelliSense
   - Syntax highlighting
   - Auto-completion

2. **Open File in Monaco**
   ```
   Ctrl+Shift+P → iTechSmart: Open File in Monaco
   ```
   - Select file from workspace
   - Edit with advanced features

3. **Image Editor**
   ```
   Ctrl+Shift+P → iTechSmart: Open Image Editor
   ```
   - Select image file
   - Draw, crop, resize
   - Add text and shapes
   - Save changes

4. **Website Builder**
   ```
   Ctrl+Shift+P → iTechSmart: Open Website Builder
   ```
   - Choose template (5 available)
   - Drag-and-drop interface
   - Live preview
   - Export HTML/CSS

5. **Markdown Editor**
   ```
   Ctrl+Shift+P → iTechSmart: Open Markdown Editor
   ```
   - Write markdown
   - Live preview
   - Word count
   - Export to HTML

6. **JSON Editor**
   ```
   Ctrl+Shift+P → iTechSmart: Open JSON Editor
   ```
   - Edit JSON with validation
   - Format and beautify
   - Convert to YAML

7. **YAML Editor**
   ```
   Ctrl+Shift+P → iTechSmart: Open YAML Editor
   ```
   - Edit YAML with validation
   - Format and beautify
   - Convert to JSON

#### Via Terminal

```bash
# Open terminal
Ctrl+Shift+I

# Open Monaco editor
monaco

# Open image editor
image-editor

# Open website builder
website-builder

# Open markdown editor
markdown-editor

# Open JSON editor
json-editor

# Open YAML editor
yaml-editor

# List active editors
editors
```

---

### Feature 4: GitHub Integration

#### Via VS Code Command Palette

1. **Set GitHub Token**
   ```
   Ctrl+Shift+P → iTechSmart: Set GitHub Token
   ```
   - Enter your GitHub personal access token
   - Token is stored securely

2. **List Repositories**
   ```
   Ctrl+Shift+P → iTechSmart: List GitHub Repositories
   ```
   - View all your repositories
   - See stars, forks, and status

3. **Create Repository**
   ```
   Ctrl+Shift+P → iTechSmart: Create GitHub Repository
   ```
   - Enter repository name
   - Set description
   - Choose public/private
   - Initialize with README

4. **Fork Repository**
   ```
   Ctrl+Shift+P → iTechSmart: Fork GitHub Repository
   ```
   - Enter repository to fork
   - Creates fork in your account

5. **List Pull Requests**
   ```
   Ctrl+Shift+P → iTechSmart: List Pull Requests
   ```
   - View open PRs
   - See status and reviews

6. **Create Pull Request**
   ```
   Ctrl+Shift+P → iTechSmart: Create Pull Request
   ```
   - Enter title and description
   - Select base and head branches
   - Create PR

7. **Review Pull Request**
   ```
   Ctrl+Shift+P → iTechSmart: Review Pull Request
   ```
   - Select PR to review
   - Add comments
   - Approve or request changes

8. **List Issues**
   ```
   Ctrl+Shift+P → iTechSmart: List GitHub Issues
   ```
   - View open issues
   - Filter by labels

9. **Create Issue**
   ```
   Ctrl+Shift+P → iTechSmart: Create GitHub Issue
   ```
   - Enter title and description
   - Add labels
   - Assign to users

10. **List Branches**
    ```
    Ctrl+Shift+P → iTechSmart: List GitHub Branches
    ```
    - View all branches
    - See latest commits

11. **Create Branch**
    ```
    Ctrl+Shift+P → iTechSmart: Create GitHub Branch
    ```
    - Enter branch name
    - Select source branch

12. **List Workflows**
    ```
    Ctrl+Shift+P → iTechSmart: List GitHub Workflows
    ```
    - View GitHub Actions workflows
    - See status and runs

13. **Trigger Workflow**
    ```
    Ctrl+Shift+P → iTechSmart: Trigger GitHub Workflow
    ```
    - Select workflow
    - Trigger manual run

#### Via Terminal

```bash
# Open terminal
Ctrl+Shift+I

# List repositories
gh-repos

# List pull requests
gh-prs

# List issues
gh-issues

# Create pull request
gh-create-pr

# Create issue
gh-create-issue
```

---

### Feature 5: Image Generation

#### Via VS Code Command Palette

1. **Generate Image from Text**
   ```
   Ctrl+Shift+P → iTechSmart: Generate Image from Text
   ```
   - Enter prompt (e.g., "A serene mountain landscape at sunset")
   - Select provider (FLUX, DALL-E, Stable Diffusion)
   - Choose size (512x512, 1024x1024, etc.)
   - Select style (photorealistic, artistic, etc.)
   - Wait 8-15 seconds
   - Image opens automatically

2. **Transform Image**
   ```
   Ctrl+Shift+P → iTechSmart: Transform Image
   ```
   - Select source image
   - Enter transformation prompt
   - Adjust strength (0.0-1.0)
   - View result

3. **Inpaint Image**
   ```
   Ctrl+Shift+P → iTechSmart: Inpaint Image
   ```
   - Select source image
   - Select mask image
   - Enter prompt for masked area
   - Generate result

4. **Create Image Variations**
   ```
   Ctrl+Shift+P → iTechSmart: Create Image Variations
   ```
   - Select source image
   - Choose number of variations (1-4)
   - View all variations

5. **Upscale Image**
   ```
   Ctrl+Shift+P → iTechSmart: Upscale Image
   ```
   - Select image to upscale
   - Choose scale factor (2x or 4x)
   - Wait for processing
   - View high-res result

6. **Remove Background**
   ```
   Ctrl+Shift+P → iTechSmart: Remove Image Background
   ```
   - Select image
   - Automatic background removal
   - Download PNG with transparency

7. **Enhance Face**
   ```
   Ctrl+Shift+P → iTechSmart: Enhance Face in Image
   ```
   - Select portrait image
   - Automatic face detection and enhancement
   - View enhanced result

8. **List Image Providers**
   ```
   Ctrl+Shift+P → iTechSmart: List Image Generation Providers
   ```
   - View all available providers
   - See capabilities and pricing

#### Via Terminal

```bash
# Open terminal
Ctrl+Shift+I

# Generate image
img-generate
# or
generate-image

# Transform image
img-transform
# or
transform-image

# Upscale image
img-upscale
# or
upscale-image

# Remove background
img-remove-bg
# or
remove-background

# List providers
img-providers
# or
list-image-providers
```

#### Via API

```bash
# Generate image
curl -X POST http://localhost:8000/api/image-generation/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "prompt": "A serene mountain landscape at sunset",
    "provider": "flux",
    "size": "1024x1024",
    "style": "photorealistic"
  }'

# Upscale image
curl -X POST http://localhost:8000/api/image-generation/upscale \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "image_path": "path/to/image.jpg",
    "scale_factor": 4
  }'

# Remove background
curl -X POST http://localhost:8000/api/image-generation/remove-background \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "image_path": "path/to/image.jpg"
  }'
```

---

## Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError` or import errors

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

**Problem**: `Port 8000 already in use`

**Solution**:
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001

# Or kill the process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### VS Code Extension Not Working

**Problem**: Commands not appearing in command palette

**Solution**:
1. Reload VS Code window (`Ctrl+Shift+P` → `Reload Window`)
2. Check extension is installed and enabled
3. Check for errors in Developer Tools (`Help` → `Toggle Developer Tools`)

**Problem**: "Cannot connect to backend"

**Solution**:
1. Verify backend is running: http://localhost:8000
2. Check API URL in VS Code settings
3. Check firewall settings

### API Key Issues

**Problem**: "Invalid API key" errors

**Solution**:
1. Verify API key is correct in `.env` file
2. Check for extra spaces or quotes
3. Ensure `.env` file is in `backend` directory
4. Restart backend server after changing `.env`

**Problem**: "Rate limit exceeded"

**Solution**:
1. Wait a few minutes
2. Check your API usage on provider's dashboard
3. Consider upgrading your API plan
4. Use a different provider temporarily

### Image Generation Issues

**Problem**: "Generation failed"

**Solution**:
1. Check API key is configured for the provider
2. Verify you have credits/quota remaining
3. Try a different provider
4. Check prompt doesn't violate content policy

**Problem**: Images not opening

**Solution**:
1. Check file was saved successfully
2. Verify file path in response
3. Try opening manually from file system
4. Check disk space

---

## API Reference

### Authentication

All API requests require authentication using JWT tokens.

**Get Token:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'
```

**Use Token:**
```bash
curl http://localhost:8000/api/endpoint \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### API Endpoints Summary

#### Models API
- `GET /api/models` - List all models
- `GET /api/models/{model_id}` - Get model details
- `POST /api/models/compare` - Compare models
- `POST /api/models/recommend` - Get recommendations
- `GET /api/models/usage` - Get usage statistics

#### Research API
- `POST /api/research/deep` - Perform deep research
- `POST /api/research/cite` - Format citation
- `POST /api/research/credibility` - Check credibility
- `GET /api/research/styles` - List citation styles

#### Editors API
- `POST /api/editors/monaco/create` - Create Monaco session
- `POST /api/editors/image/create` - Create image editor session
- `POST /api/editors/website/create` - Create website builder session
- `GET /api/editors/sessions` - List active sessions

#### GitHub API
- `GET /api/github/repos` - List repositories
- `POST /api/github/repos` - Create repository
- `GET /api/github/repos/{owner}/{repo}/pulls` - List PRs
- `POST /api/github/repos/{owner}/{repo}/pulls` - Create PR
- `GET /api/github/repos/{owner}/{repo}/issues` - List issues
- `POST /api/github/repos/{owner}/{repo}/issues` - Create issue

#### Image Generation API
- `POST /api/image-generation/generate` - Generate image
- `POST /api/image-generation/transform` - Transform image
- `POST /api/image-generation/upscale` - Upscale image
- `POST /api/image-generation/remove-background` - Remove background
- `GET /api/image-generation/providers` - List providers

**Full API Documentation**: http://localhost:8000/docs

---

## Next Steps

### Learn More
- Read feature-specific documentation in the `docs` folder
- Check out example workflows in `DEMO_SCENARIOS.md`
- Review API documentation at http://localhost:8000/docs

### Get Help
- Check troubleshooting section above
- Review backend logs in `backend/logs/`
- Check VS Code Developer Tools for extension errors

### Provide Feedback
- Report issues
- Suggest improvements
- Share your use cases

---

**Congratulations! You're now ready to use iTechSmart Ninja!** 🎉

Start with simple tasks and gradually explore more advanced features. Happy coding!