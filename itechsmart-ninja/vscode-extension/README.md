# iTechSmart Ninja - VS Code Extension

AI-powered autonomous agent assistant for VS Code with integrated terminal.

## Features

### 🖥️ Integrated AI Terminal
- Full-featured terminal interface within VS Code
- Execute AI commands directly from the terminal
- Command history navigation (↑/↓ arrows)
- Real-time progress tracking
- Beautiful terminal UI with syntax highlighting

### 🤖 AI Agents
- **Researcher**: Web search, fact-checking, citations
- **Coder**: Code generation, execution, debugging
- **Writer**: Documentation, articles, tutorials
- **Analyst**: Data analysis, visualizations, insights
- **Debugger**: Error analysis, root cause identification, fixes

### 📋 Task Management
- Create and monitor tasks from VS Code
- View task progress in real-time
- Task history and details
- Cancel running tasks

### 🎨 Context Menu Integration
- Right-click on code to:
  - Explain selected code
  - Refactor code
  - Debug code
  - Generate tests

### 📁 File Management
- Upload files to iTechSmart
- View uploaded files
- Download files

### 🔐 Secure Authentication
- Secure token storage
- Automatic token refresh
- Multi-user support

## Installation

### Prerequisites
- VS Code 1.80.0 or higher
- iTechSmart Ninja backend running (see backend README)

### Install from VSIX
1. Download the latest `.vsix` file
2. Open VS Code
3. Go to Extensions (Ctrl+Shift+X)
4. Click "..." menu → "Install from VSIX"
5. Select the downloaded file

### Install from Source
```bash
cd vscode-extension
npm install
npm run compile
```

## Quick Start

### 1. Configure API URL
Open VS Code Settings (Ctrl+,) and search for "iTechSmart":
- Set `itechsmart.apiUrl` to your backend URL (default: `http://localhost:8000`)

### 2. Login
- Press `Ctrl+Shift+P`
- Type "iTechSmart: Login"
- Enter your credentials

### 3. Open AI Terminal
- Press `Ctrl+Shift+I` (or `Cmd+Shift+I` on Mac)
- Or: `Ctrl+Shift+P` → "iTechSmart: Open AI Terminal"

### 4. Start Using AI Commands
```bash
# Generate code
$ generate Create a REST API endpoint for user authentication

# Research a topic
$ research Latest AI trends in 2025

# Analyze data
$ analyze sales_data.csv

# Debug code
$ debug function calculateTotal() { return x + y }

# Get help
$ help
```

## Terminal Commands

### AI Commands
- `generate <description>` - Generate code from description
- `research <query>` - Research a topic
- `analyze <data>` - Analyze data
- `debug <code>` - Debug code
- `explain <code>` - Explain code

### Task Management
- `tasks` - List all tasks
- `task <id>` - View task details

### Information
- `agents` - List available AI agents
- `files` - List uploaded files
- `status` - Show system status
- `whoami` - Show current user

### Terminal
- `help` - Show help message
- `clear` - Clear terminal

## Keyboard Shortcuts

- `Ctrl+Shift+I` - Open AI Terminal
- `Ctrl+Shift+G` - Generate Code
- `↑/↓` - Navigate command history
- `Ctrl+L` - Clear terminal
- `Ctrl+C` - Cancel current operation

## Context Menu Commands

Right-click on selected code:
- **Explain Code** - Get detailed explanation
- **Refactor Code** - Improve code quality
- **Debug Code** - Find and fix errors

## Sidebar Views

### Tasks View
- See all your tasks
- Click to view details
- Real-time status updates

### Agents View
- Browse available AI agents
- View capabilities
- See example tasks

### Files View
- View uploaded files
- File size and type
- Upload date

## Configuration

### Settings
- `itechsmart.apiUrl` - Backend API URL (default: `http://localhost:8000`)
- `itechsmart.apiKey` - API key (optional)
- `itechsmart.defaultAgent` - Default AI agent (default: `coder`)
- `itechsmart.autoSave` - Auto-save generated code (default: `true`)
- `itechsmart.showNotifications` - Show task notifications (default: `true`)

### Example settings.json
```json
{
  "itechsmart.apiUrl": "http://localhost:8000",
  "itechsmart.defaultAgent": "coder",
  "itechsmart.autoSave": true,
  "itechsmart.showNotifications": true
}
```

## Usage Examples

### Generate Code
1. Open AI Terminal (`Ctrl+Shift+I`)
2. Type: `generate Create a function to validate email addresses`
3. Wait for code generation
4. Code is automatically inserted at cursor position

### Research Topic
1. Open AI Terminal
2. Type: `research Quantum computing applications`
3. View research results with citations

### Debug Code
1. Select code with error
2. Right-click → "iTechSmart: Debug Code"
3. View error analysis and suggested fix

### Explain Code
1. Select code
2. Right-click → "iTechSmart: Explain Code"
3. View detailed explanation in new panel

## Troubleshooting

### Cannot connect to backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check `itechsmart.apiUrl` setting
- Ensure no firewall blocking

### Authentication failed
- Verify credentials
- Check backend logs
- Try re-login: `Ctrl+Shift+P` → "iTechSmart: Login"

### Terminal not responding
- Close and reopen terminal
- Check backend status
- Restart VS Code

### Commands not working
- Ensure you're logged in
- Check API connection
- View Output panel for errors

## Development

### Build from Source
```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode
npm run watch

# Package extension
npm run package
```

### Run Tests
```bash
npm test
```

### Debug Extension
1. Open in VS Code
2. Press F5
3. New VS Code window opens with extension loaded

## Support

- **Documentation**: [Backend README](../backend/README.md)
- **Issues**: GitHub Issues
- **Email**: support@itechsmart.ninja

## Changelog

### Version 1.0.0
- Initial release
- Integrated AI terminal
- Multi-agent support
- Task management
- Context menu integration
- Sidebar views
- Secure authentication

## License

MIT License - see LICENSE file for details

## Credits

Built with ❤️ by the iTechSmart Ninja team

---

**Enjoy coding with AI assistance!** 🚀