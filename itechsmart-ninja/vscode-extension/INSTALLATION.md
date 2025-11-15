# iTechSmart Ninja VS Code Extension - Installation Guide

## Prerequisites

### 1. Backend Setup
The VS Code extension requires the iTechSmart Ninja backend to be running.

```bash
# Navigate to backend directory
cd itechsmart-ninja/backend

# Start backend services
./start.sh

# Verify backend is running
curl http://localhost:8000/health
```

### 2. System Requirements
- VS Code 1.80.0 or higher
- Node.js 20.x or higher
- npm 9.x or higher

## Installation Methods

### Method 1: Install from VSIX (Recommended)

1. **Build the extension**
```bash
cd itechsmart-ninja/vscode-extension
npm install
npm run compile
npm run package
```

2. **Install in VS Code**
- Open VS Code
- Press `Ctrl+Shift+X` (Extensions)
- Click "..." menu → "Install from VSIX"
- Select `itechsmart-ninja-vscode-1.0.0.vsix`

### Method 2: Development Mode

1. **Open extension in VS Code**
```bash
cd itechsmart-ninja/vscode-extension
code .
```

2. **Install dependencies**
```bash
npm install
```

3. **Compile TypeScript**
```bash
npm run compile
```

4. **Run extension**
- Press `F5` in VS Code
- New VS Code window opens with extension loaded

### Method 3: Manual Installation

1. **Build extension**
```bash
cd itechsmart-ninja/vscode-extension
npm install
npm run compile
```

2. **Copy to extensions folder**

**Windows:**
```bash
xcopy /E /I out "%USERPROFILE%\.vscode\extensions\itechsmart-ninja-vscode-1.0.0"
```

**macOS/Linux:**
```bash
cp -r out ~/.vscode/extensions/itechsmart-ninja-vscode-1.0.0
```

3. **Reload VS Code**
- Press `Ctrl+Shift+P`
- Type "Reload Window"

## Configuration

### 1. Configure Backend URL

Open VS Code Settings (`Ctrl+,`):

```json
{
  "itechsmart.apiUrl": "http://localhost:8000"
}
```

Or use Settings UI:
1. Open Settings (`Ctrl+,`)
2. Search for "iTechSmart"
3. Set "Api Url" to your backend URL

### 2. Login

**Option A: Command Palette**
1. Press `Ctrl+Shift+P`
2. Type "iTechSmart: Login"
3. Enter email and password

**Option B: Welcome Prompt**
- Extension shows welcome message on first launch
- Click "Login" button
- Enter credentials

### 3. Verify Installation

1. **Open AI Terminal**
   - Press `Ctrl+Shift+I`
   - Terminal should open with welcome message

2. **Test Command**
   ```bash
   $ status
   ```
   Should show system status

3. **Check Sidebar**
   - Click iTechSmart icon in Activity Bar
   - Should see Tasks, Agents, and Files views

## Build Commands

### Compile TypeScript
```bash
npm run compile
```

### Watch Mode (Auto-compile)
```bash
npm run watch
```

### Package Extension
```bash
npm run package
```
Creates `itechsmart-ninja-vscode-1.0.0.vsix`

### Run Tests
```bash
npm test
```

### Lint Code
```bash
npm run lint
```

## Troubleshooting

### Extension Not Loading

**Check Extension Status:**
1. Press `Ctrl+Shift+P`
2. Type "Developer: Show Running Extensions"
3. Look for "iTechSmart Ninja"

**View Extension Logs:**
1. Press `Ctrl+Shift+P`
2. Type "Developer: Open Extension Logs Folder"
3. Find iTechSmart Ninja logs

### Cannot Connect to Backend

**Verify Backend:**
```bash
curl http://localhost:8000/health
```

**Check Settings:**
1. Open Settings (`Ctrl+,`)
2. Search "itechsmart.apiUrl"
3. Verify URL is correct

**Check Firewall:**
- Ensure port 8000 is not blocked
- Try disabling firewall temporarily

### Authentication Issues

**Clear Stored Credentials:**
1. Press `Ctrl+Shift+P`
2. Type "iTechSmart: Logout"
3. Login again

**Check Backend Logs:**
```bash
cd itechsmart-ninja/backend
docker-compose logs -f backend
```

### Terminal Not Opening

**Reload Window:**
1. Press `Ctrl+Shift+P`
2. Type "Reload Window"

**Reinstall Extension:**
1. Uninstall extension
2. Reload VS Code
3. Reinstall extension

### Commands Not Working

**Verify Login:**
```bash
# In AI Terminal
$ whoami
```

**Check API Connection:**
```bash
# In AI Terminal
$ status
```

**View Output Panel:**
1. Press `Ctrl+Shift+U`
2. Select "iTechSmart Ninja" from dropdown

## Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd itechsmart-ninja/vscode-extension
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Open in VS Code
```bash
code .
```

### 4. Start Development
```bash
# Terminal 1: Watch mode
npm run watch

# Terminal 2: Run extension (Press F5 in VS Code)
```

### 5. Make Changes
- Edit TypeScript files in `src/`
- Extension auto-reloads in debug window

### 6. Test Changes
```bash
npm test
```

### 7. Build for Production
```bash
npm run compile
npm run package
```

## Publishing (For Maintainers)

### 1. Update Version
```bash
npm version patch  # or minor, major
```

### 2. Update CHANGELOG.md
Add release notes

### 3. Build Extension
```bash
npm run package
```

### 4. Publish to VS Code Marketplace
```bash
vsce publish
```

### 5. Create GitHub Release
- Tag version
- Upload VSIX file
- Add release notes

## Uninstallation

### Method 1: VS Code UI
1. Open Extensions (`Ctrl+Shift+X`)
2. Find "iTechSmart Ninja"
3. Click "Uninstall"

### Method 2: Command Line
```bash
code --uninstall-extension itechsmart.itechsmart-ninja-vscode
```

### Method 3: Manual
Delete extension folder:

**Windows:**
```bash
rmdir /S "%USERPROFILE%\.vscode\extensions\itechsmart-ninja-vscode-1.0.0"
```

**macOS/Linux:**
```bash
rm -rf ~/.vscode/extensions/itechsmart-ninja-vscode-1.0.0
```

## Support

- **Documentation**: [README.md](README.md)
- **Backend Setup**: [Backend README](../backend/README.md)
- **Issues**: GitHub Issues
- **Email**: support@itechsmart.ninja

## Next Steps

After installation:
1. ✅ Configure backend URL
2. ✅ Login with credentials
3. ✅ Open AI Terminal (`Ctrl+Shift+I`)
4. ✅ Try `help` command
5. ✅ Generate your first code!

---

**Happy coding with AI assistance!** 🚀