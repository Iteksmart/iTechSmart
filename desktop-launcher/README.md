# iTechSmart Suite Desktop Launcher

A modern, cross-platform desktop application for managing and launching iTechSmart Suite components.

![Build Status](https://github.com/Iteksmart/iTechSmart/actions/workflows/build-all-platforms.yml/badge.svg)
![macOS Build](https://github.com/Iteksmart/iTechSmart/actions/workflows/build-macos.yml/badge.svg)

## Features

- 🚀 Quick launch for all iTechSmart Suite applications
- 🎨 Modern, intuitive user interface
- 🔄 Automatic updates and version management
- 📊 System status monitoring
- 🔐 Secure credential management
- 🌐 Multi-platform support (Windows, macOS, Linux)

## Installation

### Download Pre-built Installers

Visit the [Releases](https://github.com/Iteksmart/iTechSmart/releases) page to download the latest installer for your platform:

- **Windows**: `iTechSmart-Setup-x.x.x.exe`
- **macOS**: `iTechSmart-x.x.x.dmg` or `iTechSmart-x.x.x.pkg`
- **Linux**: `iTechSmart-x.x.x.AppImage`

### Build from Source

#### Prerequisites
- Node.js 20.x or higher
- npm or yarn

#### Building

```bash
# Install dependencies
npm install

# Build the application
npm run build

# Package for your platform
npm run package:win    # Windows
npm run package:mac    # macOS
npm run package:linux  # Linux
```

## Automated Builds

This project uses GitHub Actions for automated builds across all platforms:

- **Automatic Builds**: Triggered on every push to main branch
- **Release Builds**: Triggered when version tags are pushed
- **Artifacts**: Available for download from the Actions tab
- **Multi-Platform**: Windows, macOS, and Linux built in parallel

### Triggering a Build

#### Automatic (on push)
```bash
git push origin main
```

#### Manual Trigger
1. Go to the repository on GitHub
2. Click "Actions" tab
3. Select "Build All Platforms" workflow
4. Click "Run workflow"

#### Creating a Release
```bash
# Tag the version
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push the tag
git push origin v1.0.0
```

This will automatically:
- Build installers for all platforms
- Create a GitHub release
- Attach all installers to the release

## Development

### Project Structure

```
desktop-launcher/
├── src/              # Source code
├── assets/           # Icons and resources
├── release/          # Built installers
├── package.json      # Project configuration
└── electron.vite.config.ts  # Build configuration
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build the application
- `npm run preview` - Preview the built application
- `npm run package:win` - Build Windows installer
- `npm run package:mac` - Build macOS installer
- `npm run package:linux` - Build Linux installer

### Development Workflow

1. Make your changes in the `src/` directory
2. Test with `npm run dev`
3. Build with `npm run build`
4. Package with platform-specific commands
5. Test the installer on target platform

## Platform-Specific Notes

### Windows
- Requires Wine on Linux for cross-compilation
- Produces `.exe` installer
- Supports auto-updates

### macOS
- Requires macOS system for building (or GitHub Actions)
- Produces `.dmg` and `.pkg` installers
- Requires code signing for distribution
- Supports auto-updates

### Linux
- Produces `.AppImage` (portable)
- No installation required
- Works on most Linux distributions

## Configuration

The launcher can be configured through:
- Settings UI in the application
- Configuration file at `~/.itechsmart/config.json`
- Environment variables

## Troubleshooting

### Build Issues

**Windows Build Fails on Linux**
- Install Wine: See `.github/workflows/build-all-platforms.yml` for setup

**macOS Build Fails**
- Use GitHub Actions for macOS builds
- Or build on an actual macOS system

**Dependencies Not Installing**
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall

### Runtime Issues

**Application Won't Start**
- Check system requirements
- Verify all dependencies are installed
- Check logs in `~/.itechsmart/logs/`

**Auto-Update Fails**
- Check internet connection
- Verify GitHub releases are accessible
- Check application permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Documentation: [GitHub Wiki](https://github.com/Iteksmart/iTechSmart/wiki)
- Issues: [GitHub Issues](https://github.com/Iteksmart/iTechSmart/issues)
- Discussions: [GitHub Discussions](https://github.com/Iteksmart/iTechSmart/discussions)

## Acknowledgments

Built with:
- [Electron](https://www.electronjs.org/)
- [Vite](https://vitejs.dev/)
- [electron-builder](https://www.electron.build/)
- [GitHub Actions](https://github.com/features/actions)