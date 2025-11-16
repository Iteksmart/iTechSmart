# Desktop Launcher - Build Instructions

## Prerequisites

- Node.js 20+
- npm or yarn
- Docker (for running products)

## Installation

```bash
cd desktop-launcher

# Install dependencies
npm install

# This will install:
# - Electron 28
# - React 18 + TypeScript
# - Vite 5
# - Tailwind CSS
# - Dockerode
# - All other dependencies
```

## Development

### Start Development Server

```bash
# Terminal 1: Start Vite dev server (React UI)
npm run dev

# Terminal 2: Start Electron (Desktop app)
npm start
```

The app will open with hot-reload enabled. Changes to React components will update automatically.

### Development Tips

- React DevTools work in development mode
- Console logs appear in terminal
- Use `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac) for DevTools
- Main process logs appear in terminal
- Renderer process logs appear in DevTools console

## Building

### Build TypeScript

```bash
# Build main process
npm run build:main

# Build renderer (React UI)
npm run build:renderer

# Build both
npm run build
```

### Package Installers

```bash
# Package for current platform
npm run package

# Package for specific platform
npm run package:win    # Windows (.exe, .msi)
npm run package:mac    # macOS (.dmg, .pkg)
npm run package:linux  # Linux (.deb, .rpm, .AppImage)

# Package for all platforms (requires platform-specific tools)
npm run package:all
```

## Build Output

After packaging, installers will be in the `release/` directory:

### Windows
```
release/
├── iTechSmart-Suite-Setup-1.0.0.exe  # NSIS installer
└── iTechSmart-Suite-1.0.0.msi        # MSI installer
```

### macOS
```
release/
├── iTechSmart-Suite-1.0.0.dmg        # DMG installer
├── iTechSmart-Suite-1.0.0.pkg        # PKG installer
└── iTechSmart-Suite-1.0.0.app        # Application bundle
```

### Linux
```
release/
├── itechsmart-suite_1.0.0_amd64.deb  # Debian package
├── itechsmart-suite-1.0.0.x86_64.rpm # RedHat package
└── iTechSmart-Suite-1.0.0.AppImage   # Universal AppImage
```

## Testing

### Manual Testing Checklist

#### 1. Docker Integration
- [ ] App detects Docker installation
- [ ] Shows warning if Docker not installed
- [ ] Can pull Docker images
- [ ] Can start containers
- [ ] Can stop containers
- [ ] Status updates correctly
- [ ] Can open products in browser

#### 2. License System
- [ ] Trial license activates automatically
- [ ] Can enter license key
- [ ] License validation works
- [ ] Product access based on tier
- [ ] Shows days remaining for trial
- [ ] Locked products show upgrade message

#### 3. User Interface
- [ ] Dashboard loads correctly
- [ ] Product cards display properly
- [ ] Search works
- [ ] Category filter works
- [ ] Sidebar navigation works
- [ ] Settings page shows system info
- [ ] License page shows current license

#### 4. System Integration
- [ ] System tray icon appears
- [ ] Tray menu works
- [ ] App minimizes to tray
- [ ] App restores from tray
- [ ] Auto-update check works
- [ ] App quits properly

### Automated Testing

```bash
# Run tests (when implemented)
npm test

# Run linting
npm run lint
```

## Platform-Specific Build Requirements

### Windows
- Windows 10/11
- No additional requirements (electron-builder handles everything)

### macOS
- macOS 10.15+
- Xcode Command Line Tools: `xcode-select --install`
- For code signing: Apple Developer account

### Linux
- Ubuntu 20.04+ or equivalent
- For .deb: `sudo apt-get install dpkg fakeroot`
- For .rpm: `sudo apt-get install rpm`
- For .AppImage: `sudo apt-get install libfuse2`

## Code Signing (Optional but Recommended)

### Windows
```bash
# Set environment variables
export CSC_LINK=/path/to/certificate.pfx
export CSC_KEY_PASSWORD=your_password

# Build with signing
npm run package:win
```

### macOS
```bash
# Set environment variables
export APPLE_ID=your@email.com
export APPLE_ID_PASSWORD=app-specific-password
export CSC_LINK=/path/to/certificate.p12
export CSC_KEY_PASSWORD=your_password

# Build with signing and notarization
npm run package:mac
```

## Troubleshooting

### Build Fails

**Problem**: TypeScript compilation errors
```bash
# Solution: Check tsconfig files
npm run build:main
npm run build:renderer
```

**Problem**: Missing dependencies
```bash
# Solution: Clean install
rm -rf node_modules package-lock.json
npm install
```

### Electron Won't Start

**Problem**: Main process crashes
```bash
# Solution: Check main process logs
npm start
# Look for errors in terminal
```

**Problem**: Renderer won't load
```bash
# Solution: Check Vite dev server
npm run dev
# Should start on http://localhost:5173
```

### Docker Integration Issues

**Problem**: Can't connect to Docker
```bash
# Solution: Verify Docker is running
docker ps

# Check Docker socket permissions (Linux)
sudo usermod -aG docker $USER
```

**Problem**: Can't pull images
```bash
# Solution: Check Docker Hub access
docker pull ghcr.io/iteksmart/itechsmart-ninja-backend:main
```

### Package Build Issues

**Problem**: electron-builder fails
```bash
# Solution: Update electron-builder
npm install electron-builder@latest --save-dev

# Clear cache
rm -rf ~/.electron
```

**Problem**: Icon errors
```bash
# Solution: Verify icon files exist
ls -la assets/icons/
# Should have: icon.png, icon.ico, icon.icns, tray-icon.png
```

## Performance Optimization

### Reduce Bundle Size
```bash
# Analyze bundle
npm run build
# Check dist/ directory size

# Optimize images
# Use smaller icons
# Remove unused dependencies
```

### Improve Startup Time
- Lazy load components
- Defer non-critical operations
- Use code splitting
- Optimize Docker operations

## Distribution

### GitHub Releases
```bash
# Tag version
git tag v1.0.0
git push origin v1.0.0

# electron-builder can auto-publish
npm run package -- --publish always
```

### Manual Distribution
1. Build installers for all platforms
2. Upload to file hosting (S3, CDN)
3. Create download page
4. Provide checksums (SHA256)

### Auto-Update Server
Configure in `src/main/update-manager.ts`:
```typescript
autoUpdater.setFeedURL({
  provider: 'github',
  owner: 'Iteksmart',
  repo: 'iTechSmart'
});
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Build Desktop Launcher

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
      
      - run: npm install
      - run: npm run build
      - run: npm run package
      
      - uses: actions/upload-artifact@v3
        with:
          name: installers-${{ matrix.os }}
          path: release/
```

## Support

For build issues:
- Check logs in terminal
- Review error messages
- Consult electron-builder docs: https://www.electron.build/
- GitHub Issues: https://github.com/Iteksmart/iTechSmart/issues

## Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Add icon assets (see assets/icons/README.md)
3. ✅ Test in development: `npm run dev` + `npm start`
4. ✅ Build installers: `npm run package`
5. ✅ Test installers on target platforms
6. ✅ Distribute to users!

**Current Status**: Ready to build once icons are added! 🚀