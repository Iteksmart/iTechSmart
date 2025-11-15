# iTechSmart Ninja - Quick Reference Card

## 🚀 Quick Start (5 Minutes)

### 1. Start Backend
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```
**Verify**: http://localhost:8000

### 2. Start VS Code
- Press `F5` (Development Mode)
- Or open VS Code normally (if installed)

### 3. Open Terminal
- Press `Ctrl+Shift+I`
- Type `help` to see all commands

---

## 📝 Essential Commands

### Terminal Commands (Ctrl+Shift+I)

```bash
# AI Models
models                    # List all 42 AI models
select-model             # Choose a model
model-stats              # View usage statistics

# Research
research "query"         # Deep research with citations
cite "url"              # Format citation
credibility "url"       # Check source credibility

# Code Editors
monaco                  # Open code editor
image-editor           # Edit images
website-builder        # Build websites
markdown-editor        # Edit markdown

# GitHub
gh-repos               # List repositories
gh-prs                 # List pull requests
gh-issues              # List issues
gh-create-pr           # Create pull request
gh-create-issue        # Create issue

# Image Generation
img-generate           # Generate image from text
img-transform          # Transform image
img-upscale            # Upscale image
img-remove-bg          # Remove background
img-providers          # List providers

# General
help                   # Show all commands
clear                  # Clear terminal
status                 # System status
```

---

## 🎯 VS Code Commands (Ctrl+Shift+P)

### AI Models
- `iTechSmart: Browse AI Models`
- `iTechSmart: Select AI Model`
- `iTechSmart: Compare AI Models`
- `iTechSmart: Get Model Recommendations`
- `iTechSmart: Show Model Usage Stats`

### Research
- `iTechSmart: Perform Deep Research`
- `iTechSmart: Format Citation`
- `iTechSmart: Check Source Credibility`
- `iTechSmart: View Citation Styles`

### Code Editors
- `iTechSmart: Open Monaco Editor`
- `iTechSmart: Open Image Editor`
- `iTechSmart: Open Website Builder`
- `iTechSmart: Open Markdown Editor`
- `iTechSmart: Open JSON Editor`
- `iTechSmart: Open YAML Editor`

### GitHub
- `iTechSmart: List GitHub Repositories`
- `iTechSmart: Create GitHub Repository`
- `iTechSmart: List Pull Requests`
- `iTechSmart: Create Pull Request`
- `iTechSmart: List GitHub Issues`
- `iTechSmart: Create GitHub Issue`

### Image Generation
- `iTechSmart: Generate Image from Text`
- `iTechSmart: Transform Image`
- `iTechSmart: Upscale Image`
- `iTechSmart: Remove Image Background`
- `iTechSmart: Enhance Face in Image`

---

## 🔑 Required API Keys

### Minimum (Core Features)
```bash
OPENAI_API_KEY=sk-...           # For GPT models & DALL-E
ANTHROPIC_API_KEY=sk-ant-...    # For Claude models
GOOGLE_API_KEY=...              # For Gemini models
```

### Optional (Extended Features)
```bash
REPLICATE_API_KEY=...           # For FLUX image generation
GITHUB_TOKEN=ghp_...            # For GitHub integration
GOOGLE_SEARCH_API_KEY=...       # For web search
```

**Get Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google: https://makersuite.google.com/app/apikey
- Replicate: https://replicate.com/account/api-tokens
- GitHub: https://github.com/settings/tokens

---

## 📊 Available Features

### ✅ Completed (5/15)
1. **42 AI Models** - GPT, Claude, Gemini, DeepSeek, Mistral, etc.
2. **Deep Research** - Multi-source search, 5 citation styles
3. **5 Code Editors** - Monaco, Image, Website, Markdown, JSON/YAML
4. **GitHub Integration** - Repos, PRs, Issues, Actions
5. **Image Generation** - FLUX, DALL-E, Stable Diffusion

### ⏳ Not Yet Implemented (10/15)
6. Advanced Data Visualization
7. Enhanced Document Processing
8. Concurrent VM Support
9. Scheduled Tasks
10. MCP Data Sources
11. Undo/Redo Actions
12. Video Generation
13. Advanced Debugging
14. Custom Workflows
15. Team Collaboration

---

## 🌐 Important URLs

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🐛 Quick Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Need 3.11+

# Reinstall dependencies
pip install -r requirements.txt

# Use different port
uvicorn app.main:app --reload --port 8001
```

### Extension Not Working
1. Reload VS Code: `Ctrl+Shift+P` → `Reload Window`
2. Check backend is running: http://localhost:8000
3. Check API URL in settings

### API Key Errors
1. Verify key in `.env` file
2. No extra spaces or quotes
3. Restart backend after changes

---

## 💡 Pro Tips

### Keyboard Shortcuts
- `Ctrl+Shift+I` - Open iTechSmart Terminal
- `Ctrl+Shift+P` - Command Palette
- `F5` - Start Extension Development

### Cost Optimization
- Use **FLUX Schnell** ($0.003/image) for quick iterations
- Use **Stable Diffusion** ($0.0025/image) for batch generation
- Use **GPT-4o-mini** for most coding tasks
- Use **Claude 3 Haiku** for fast responses

### Best Practices
1. Start with cheaper models, upgrade if needed
2. Use web search before deep research
3. Save editor sessions frequently
4. Check provider status before bulk operations
5. Monitor usage statistics regularly

---

## 📚 Documentation

- **Complete Setup**: `COMPLETE_SETUP_GUIDE.md`
- **Feature 1**: `FEATURE1_COMPLETE.md`
- **Feature 2**: `FEATURE2_COMPLETE.md`
- **Feature 3**: `FEATURE3_COMPLETE.md`
- **Feature 4**: `FEATURE4_COMPLETE.md`
- **Feature 5**: `FEATURE5_COMPLETE.md`
- **Overall Progress**: `OVERALL_PROGRESS.md`
- **Status Report**: `STATUS_REPORT.md`

---

## 🎯 Common Use Cases

### Generate Code
```bash
# Terminal
Ctrl+Shift+I
generate "Create a REST API endpoint for user login"
```

### Research Topic
```bash
# Terminal
research "latest AI trends 2024"
```

### Create Website
```bash
# Command Palette
Ctrl+Shift+P → iTechSmart: Open Website Builder
```

### Generate Image
```bash
# Terminal
img-generate
# Enter: "A serene mountain landscape at sunset"
```

### GitHub PR
```bash
# Terminal
gh-create-pr
```

---

## 📞 Support

### Check Logs
- Backend: `backend/logs/`
- VS Code: `Help` → `Toggle Developer Tools`

### Verify Installation
```bash
# Backend
curl http://localhost:8000/health

# Python packages
pip list | grep fastapi

# Node packages
npm list
```

---

**Quick Reference v1.0** | Last Updated: Week 2