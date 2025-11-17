# Desktop Launcher - Complete User Guide

**Version**: 1.0.0  
**Last Updated**: November 17, 2025  
**Product Type**: Desktop Application  
**Platforms**: Windows, macOS, Linux

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Core Features](#core-features)
5. [User Interface Guide](#user-interface-guide)
6. [Configuration](#configuration)
7. [Managing Applications](#managing-applications)
8. [System Monitoring](#system-monitoring)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)
11. [Advanced Topics](#advanced-topics)

---

## Introduction

### What is Desktop Launcher?

The iTechSmart Suite Desktop Launcher is a modern, cross-platform desktop application that serves as your central hub for managing and launching all iTechSmart Suite components. It provides a unified interface for accessing your entire suite of enterprise tools.

### Key Features

- 🚀 **Quick Launch** - One-click access to all iTechSmart Suite applications
- 🎨 **Modern UI** - Intuitive, user-friendly interface built with modern web technologies
- 🔄 **Auto Updates** - Automatic version management and updates
- 📊 **System Monitoring** - Real-time status monitoring of all services
- 🔐 **Secure Credentials** - Encrypted credential storage and management
- 🌐 **Multi-Platform** - Native support for Windows, macOS, and Linux
- 📱 **Responsive Design** - Adapts to different screen sizes and resolutions
- 🔔 **Notifications** - Stay informed about system events and updates

### System Requirements

#### Minimum Requirements
- **CPU**: Dual-core processor (2 GHz or faster)
- **RAM**: 4 GB
- **Storage**: 500 MB free space
- **OS**: 
  - Windows 10 or later (64-bit)
  - macOS 10.13 (High Sierra) or later
  - Linux (Ubuntu 18.04+, Fedora 32+, or equivalent)
- **Network**: Internet connection for updates and cloud features

#### Recommended Requirements
- **CPU**: Quad-core processor (2.5 GHz or faster)
- **RAM**: 8 GB or more
- **Storage**: 1 GB free space (SSD recommended)
- **Display**: 1920x1080 or higher resolution
- **Network**: Broadband internet connection

---

## Installation

### Windows Installation

#### Method 1: Using the Installer (Recommended)

1. **Download the Installer**
   - Visit [GitHub Releases](https://github.com/Iteksmart/iTechSmart/releases)
   - Download `iTechSmart-Setup-1.0.0.exe`

2. **Run the Installer**
   - Double-click the downloaded `.exe` file
   - If Windows SmartScreen appears, click "More info" → "Run anyway"
   - Follow the installation wizard:
     * Accept the license agreement
     * Choose installation directory (default: `C:\Program Files\iTechSmart`)
     * Select whether to create desktop shortcut
     * Click "Install"

3. **Launch the Application**
   - Find "iTechSmart Suite" in Start Menu
   - Or double-click the desktop shortcut (if created)

#### Method 2: Portable Version

1. Download the portable `.zip` file
2. Extract to your preferred location
3. Run `iTechSmart.exe` from the extracted folder

### macOS Installation

#### Method 1: Using DMG (Recommended)

1. **Download the DMG**
   - Visit [GitHub Releases](https://github.com/Iteksmart/iTechSmart/releases)
   - Download `iTechSmart-1.0.0.dmg` (Intel) or `iTechSmart-1.0.0-arm64.dmg` (Apple Silicon)

2. **Install the Application**
   - Double-click the downloaded `.dmg` file
   - Drag the iTechSmart icon to the Applications folder
   - Eject the DMG

3. **First Launch**
   - Open Applications folder
   - Right-click "iTechSmart Suite" → "Open"
   - Click "Open" in the security dialog (first launch only)

#### Troubleshooting macOS Security

If you see "iTechSmart Suite cannot be opened because it is from an unidentified developer":

```bash
# Remove quarantine attribute
xattr -cr /Applications/iTechSmart\ Suite.app
```

Or go to System Preferences → Security & Privacy → General → Click "Open Anyway"

### Linux Installation

#### Method 1: AppImage (Recommended)

1. **Download AppImage**
   - Visit [GitHub Releases](https://github.com/Iteksmart/iTechSmart/releases)
   - Download `iTechSmart-1.0.0.AppImage`

2. **Make it Executable**
   ```bash
   chmod +x iTechSmart-1.0.0.AppImage
   ```

3. **Run the Application**
   ```bash
   ./iTechSmart-1.0.0.AppImage
   ```

#### Method 2: System Integration

To integrate with your system menu:

```bash
# Create desktop entry
cat > ~/.local/share/applications/itechsmart.desktop << EOF
[Desktop Entry]
Name=iTechSmart Suite
Exec=/path/to/iTechSmart-1.0.0.AppImage
Icon=itechsmart
Type=Application
Categories=Utility;
EOF

# Update desktop database
update-desktop-database ~/.local/share/applications
```

---

## Getting Started

### First Launch

When you launch the Desktop Launcher for the first time:

1. **Welcome Screen**
   - You'll see a welcome screen introducing the application
   - Click "Get Started" to proceed

2. **License Configuration**
   - Enter your license server URL (e.g., `https://license.itechsmart.dev`)
   - Enter your organization API key
   - Click "Connect"

3. **Initial Setup**
   - The launcher will verify your license
   - Download available product configurations
   - Set up local preferences

4. **Dashboard**
   - You'll be taken to the main dashboard
   - All available products will be displayed
   - Products are organized by category

### Basic Navigation

The Desktop Launcher interface consists of several key areas:

1. **Top Bar**
   - Application title and logo
   - Search bar for finding products
   - User profile menu
   - Settings icon
   - Minimize/Maximize/Close buttons

2. **Sidebar** (Left)
   - Dashboard (Home)
   - All Products
   - Favorites
   - Recently Used
   - Categories
   - Settings

3. **Main Content Area**
   - Product cards/tiles
   - Status indicators
   - Quick action buttons
   - System notifications

4. **Status Bar** (Bottom)
   - Connection status
   - System health indicators
   - Update notifications
   - Quick stats

---

## Core Features

### 1. Quick Launch

**Launch any iTechSmart product with a single click:**

- Click on any product card in the dashboard
- Or use the search bar to find and launch products
- Or use keyboard shortcuts (see below)

**Keyboard Shortcuts:**
- `Ctrl/Cmd + K` - Open quick launcher
- `Ctrl/Cmd + F` - Focus search bar
- `Ctrl/Cmd + 1-9` - Launch favorite products 1-9
- `Ctrl/Cmd + R` - Refresh product list

### 2. Product Management

**Add to Favorites:**
1. Hover over a product card
2. Click the star icon
3. Product appears in "Favorites" section

**Remove from Favorites:**
1. Click the filled star icon on a favorited product
2. Or go to Favorites → Right-click → "Remove from Favorites"

**Product Information:**
- Click the info icon (ℹ️) on any product card
- View detailed information:
  * Product description
  * Version number
  * License status
  * System requirements
  * Documentation links

### 3. System Monitoring

**Real-time Status Monitoring:**

The launcher continuously monitors:
- Product availability
- Service health
- License validity
- System resources
- Network connectivity

**Status Indicators:**
- 🟢 Green - Service running and healthy
- 🟡 Yellow - Service degraded or warning
- 🔴 Red - Service down or error
- ⚪ Gray - Service not started

**View Detailed Status:**
1. Click on any status indicator
2. View detailed metrics:
   - Uptime
   - Response time
   - Resource usage
   - Recent errors
   - Performance graphs

### 4. Credential Management

**Secure Storage:**
- All credentials are encrypted locally
- Uses system keychain/credential manager
- Never stored in plain text

**Managing Credentials:**
1. Go to Settings → Credentials
2. View saved credentials for each product
3. Add new credentials:
   - Click "Add Credential"
   - Select product
   - Enter username/password or API key
   - Click "Save"
4. Edit or delete existing credentials

**Auto-Login:**
- Enable auto-login for frequently used products
- Credentials are automatically filled when launching
- Can be disabled per-product in settings

### 5. Automatic Updates

**Update Notifications:**
- Desktop Launcher checks for updates daily
- Notification appears when update is available
- Click "Update Now" or "Remind Me Later"

**Update Process:**
1. Click "Update Now"
2. Launcher downloads update in background
3. Prompt to restart application
4. Update is applied on restart
5. Changelog is displayed after update

**Update Settings:**
- Go to Settings → Updates
- Configure update preferences:
  * Automatic updates (recommended)
  * Check for updates manually
  * Update channel (stable/beta)
  * Download updates in background

---

## User Interface Guide

### Dashboard View

**Product Cards:**
Each product is displayed as a card showing:
- Product icon/logo
- Product name
- Brief description
- Status indicator
- Quick action buttons:
  * Launch
  * Favorite/Unfavorite
  * Info
  * Settings (for that product)

**Filtering and Sorting:**
- **Filter by Category**: Click category in sidebar
- **Filter by Status**: All / Running / Stopped / Error
- **Sort Options**:
  * Alphabetical (A-Z)
  * Recently Used
  * Most Used
  * Status

**View Modes:**
- Grid View (default) - Cards in a grid
- List View - Compact list with details
- Compact View - Minimal information

### Search Functionality

**Quick Search:**
1. Press `Ctrl/Cmd + K` or click search bar
2. Type product name or keyword
3. Results appear instantly
4. Use arrow keys to navigate
5. Press Enter to launch selected product

**Advanced Search:**
- Search by product name
- Search by category
- Search by tags
- Search by description keywords

### Settings Panel

**General Settings:**
- Theme (Light/Dark/Auto)
- Language
- Startup behavior
- Notification preferences
- Default view mode

**Product Settings:**
- Configure per-product preferences
- Set default launch options
- Manage product-specific credentials
- Configure product-specific shortcuts

**Advanced Settings:**
- License server configuration
- Network proxy settings
- Cache management
- Debug logging
- Performance tuning

---

## Configuration

### Environment Configuration

**License Server:**
```
License Server URL: https://license.itechsmart.dev
Organization ID: your-org-id
API Key: your-api-key
```

**Network Settings:**
- Proxy configuration (if behind corporate proxy)
- Timeout settings
- Retry policies
- Connection pooling

### Customization

**Themes:**
1. Go to Settings → Appearance
2. Choose theme:
   - Light Mode
   - Dark Mode
   - Auto (follows system)
   - Custom (create your own)

**Layout:**
- Customize sidebar position (left/right)
- Show/hide status bar
- Adjust card size
- Configure grid columns

**Shortcuts:**
1. Go to Settings → Keyboard Shortcuts
2. View all available shortcuts
3. Customize shortcuts:
   - Click on shortcut
   - Press new key combination
   - Click "Save"

---

## Managing Applications

### Starting Applications

**Method 1: Click to Launch**
1. Find the product in dashboard
2. Click the "Launch" button
3. Application opens in default browser or desktop app

**Method 2: Quick Launcher**
1. Press `Ctrl/Cmd + K`
2. Type product name
3. Press Enter

**Method 3: Favorites**
1. Add products to favorites
2. Use `Ctrl/Cmd + 1-9` to launch

### Stopping Applications

**For Web-Based Products:**
- Simply close the browser tab
- Or click "Stop" in the launcher (if available)

**For Desktop Products:**
- Close the application window
- Or right-click product → "Stop Service"

### Monitoring Application Status

**Status Dashboard:**
1. Go to Dashboard
2. View status indicators on each product
3. Click status indicator for details

**System Tray:**
- Launcher runs in system tray
- Right-click tray icon for quick menu:
  * View running applications
  * Stop all applications
  * Open dashboard
  * Exit launcher

---

## System Monitoring

### Health Checks

**Automatic Health Checks:**
- Launcher performs health checks every 30 seconds
- Checks service availability
- Monitors response times
- Detects errors and issues

**Manual Health Check:**
1. Go to Settings → System
2. Click "Run Health Check"
3. View results:
   - Service status
   - Network connectivity
   - License validity
   - System resources

### Performance Monitoring

**Resource Usage:**
- View CPU usage per product
- Monitor memory consumption
- Track network bandwidth
- Monitor disk I/O

**Performance Graphs:**
1. Click on any product
2. Go to "Performance" tab
3. View real-time graphs:
   - Response time
   - Request rate
   - Error rate
   - Resource usage

### Logs and Diagnostics

**Viewing Logs:**
1. Go to Settings → Logs
2. Select log level (Info/Warning/Error)
3. Filter by product or time range
4. Export logs for support

**Diagnostic Tools:**
- Network diagnostics
- License validation
- Configuration validation
- System compatibility check

---

## Troubleshooting

### Common Issues

#### Issue 1: Cannot Connect to License Server

**Symptoms:**
- "Connection failed" error
- Products not loading
- License validation fails

**Solutions:**

1. **Check Network Connection**
   ```bash
   # Test connectivity
   ping license.itechsmart.dev
   ```

2. **Verify License Server URL**
   - Go to Settings → License
   - Ensure URL is correct
   - Try accessing URL in browser

3. **Check Firewall**
   - Ensure port 443 (HTTPS) is open
   - Add exception for iTechSmart Suite
   - Check corporate proxy settings

4. **Verify Credentials**
   - Confirm API key is valid
   - Check organization ID
   - Contact administrator if needed

#### Issue 2: Application Won't Launch

**Symptoms:**
- Click launch but nothing happens
- Application crashes immediately
- Error message appears

**Solutions:**

1. **Check Application Status**
   - Verify service is running
   - Check status indicator
   - View error logs

2. **Clear Cache**
   ```bash
   # Settings → Advanced → Clear Cache
   ```

3. **Reinstall Application**
   - Uninstall Desktop Launcher
   - Download latest version
   - Reinstall

4. **Check System Requirements**
   - Verify OS compatibility
   - Ensure sufficient resources
   - Update system dependencies

#### Issue 3: Slow Performance

**Symptoms:**
- Launcher is slow to respond
- Products take long to launch
- UI is laggy

**Solutions:**

1. **Check System Resources**
   - Close unnecessary applications
   - Free up RAM
   - Check CPU usage

2. **Optimize Settings**
   - Reduce number of monitored products
   - Increase health check interval
   - Disable animations

3. **Clear Cache and Data**
   - Settings → Advanced → Clear Cache
   - Settings → Advanced → Reset Settings

4. **Update to Latest Version**
   - Check for updates
   - Install latest version

#### Issue 4: Auto-Update Fails

**Symptoms:**
- Update download fails
- Update installation fails
- Launcher won't restart after update

**Solutions:**

1. **Manual Update**
   - Download latest installer
   - Close launcher
   - Run installer
   - Restart launcher

2. **Check Permissions**
   - Ensure write permissions
   - Run as administrator (Windows)
   - Check disk space

3. **Disable Antivirus Temporarily**
   - Some antivirus software blocks updates
   - Add exception for iTechSmart
   - Re-enable after update

---

## FAQ

### General Questions

**Q: Is the Desktop Launcher free?**  
A: The Desktop Launcher itself is free. However, you need a valid license for the iTechSmart Suite products you want to access.

**Q: Can I use the launcher without an internet connection?**  
A: The launcher requires internet connection for initial setup and license validation. Some features work offline, but most products require connectivity.

**Q: How many products can I manage with the launcher?**  
A: The launcher can manage all 37 iTechSmart Suite products, depending on your license.

**Q: Can I customize the launcher appearance?**  
A: Yes! You can customize themes, layouts, and even create custom themes in Settings → Appearance.

### Installation Questions

**Q: Why does Windows SmartScreen block the installer?**  
A: This is normal for new applications. Click "More info" → "Run anyway" to proceed. The application is safe and digitally signed.

**Q: Can I install on multiple computers?**  
A: Yes, you can install the launcher on multiple computers. Your license determines how many concurrent users you can have.

**Q: How do I uninstall the launcher?**  
A: 
- **Windows**: Control Panel → Programs → Uninstall
- **macOS**: Drag app to Trash from Applications folder
- **Linux**: Delete the AppImage file

### Usage Questions

**Q: How do I add a new product?**  
A: Products are automatically discovered based on your license. If a product is missing, check your license or contact support.

**Q: Can I launch multiple products simultaneously?**  
A: Yes, you can launch as many products as your system resources allow.

**Q: How do I backup my settings?**  
A: Go to Settings → Advanced → Export Settings. Save the file to a safe location.

**Q: Can I use keyboard shortcuts?**  
A: Yes! Press `Ctrl/Cmd + ?` to view all available shortcuts.

### Technical Questions

**Q: Where are my credentials stored?**  
A: Credentials are encrypted and stored in your system's secure credential manager (Windows Credential Manager, macOS Keychain, or Linux Secret Service).

**Q: How often does the launcher check for updates?**  
A: By default, once per day. You can change this in Settings → Updates.

**Q: Can I run the launcher on a server?**  
A: The launcher is designed for desktop use. For server deployments, use Docker or Kubernetes configurations.

**Q: What data does the launcher collect?**  
A: The launcher only collects anonymous usage statistics (if enabled) and error reports to improve the product. No personal data is collected without consent.

---

## Advanced Topics

### Command Line Options

The launcher supports several command-line options:

```bash
# Launch with specific profile
iTechSmart --profile=production

# Enable debug logging
iTechSmart --debug

# Specify config file
iTechSmart --config=/path/to/config.json

# Launch in headless mode (no UI)
iTechSmart --headless

# Launch specific product
iTechSmart --launch=ninja

# Reset all settings
iTechSmart --reset
```

### Configuration Files

**Location:**
- **Windows**: `%APPDATA%\iTechSmart\config.json`
- **macOS**: `~/Library/Application Support/iTechSmart/config.json`
- **Linux**: `~/.config/iTechSmart/config.json`

**Example Configuration:**
```json
{
  "licenseServer": "https://license.itechsmart.dev",
  "organizationId": "your-org-id",
  "theme": "dark",
  "autoUpdate": true,
  "updateChannel": "stable",
  "healthCheckInterval": 30,
  "favorites": ["ninja", "supreme", "citadel"],
  "shortcuts": {
    "quickLaunch": "Ctrl+K",
    "search": "Ctrl+F"
  }
}
```

### API Integration

The launcher exposes a local API for automation:

```javascript
// Connect to launcher API
const launcher = require('itechsmart-launcher-api');

// Launch a product
launcher.launch('ninja');

// Get product status
const status = launcher.getStatus('ninja');

// Stop a product
launcher.stop('ninja');

// Get all products
const products = launcher.listProducts();
```

### Scripting and Automation

**PowerShell (Windows):**
```powershell
# Launch product
& "C:\Program Files\iTechSmart\iTechSmart.exe" --launch=ninja

# Get status
$status = & "C:\Program Files\iTechSmart\iTechSmart.exe" --status
```

**Bash (macOS/Linux):**
```bash
# Launch product
/Applications/iTechSmart\ Suite.app/Contents/MacOS/iTechSmart --launch=ninja

# Get status
status=$(/Applications/iTechSmart\ Suite.app/Contents/MacOS/iTechSmart --status)
```

### Building from Source

If you want to build the launcher from source:

```bash
# Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/desktop-launcher

# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build

# Package for your platform
npm run package:win    # Windows
npm run package:mac    # macOS
npm run package:linux  # Linux
```

---

## Additional Resources

### Documentation
- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Demo Setup**: [DEMO_SETUP.md](DEMO_SETUP.md)
- **Build Verification**: [BUILD_VERIFICATION.md](BUILD_VERIFICATION.md)

### Support
- **GitHub**: https://github.com/Iteksmart/iTechSmart
- **Issues**: https://github.com/Iteksmart/iTechSmart/issues
- **Discussions**: https://github.com/Iteksmart/iTechSmart/discussions
- **Email**: support@itechsmart.dev

### Community
- **Discord**: Join our community server
- **Twitter**: @iTechSmart
- **Blog**: https://blog.itechsmart.dev

---

## Version History

### Version 1.0.0 (Current)
- Initial release
- Multi-platform support (Windows, macOS, Linux)
- Quick launch functionality
- System monitoring
- Credential management
- Auto-update system
- Modern UI with dark/light themes

---

**Last Updated**: November 17, 2025  
**Document Version**: 1.0  
**Maintained by**: iTechSmart Inc

---

**End of User Guide**