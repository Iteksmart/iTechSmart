# iTechSmart Suite - Production Deployment Guide

## Overview

This guide covers the complete deployment process for iTechSmart Suite, including building executables, creating installers, and distributing to end users.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Build System Architecture](#build-system-architecture)
3. [GitHub Actions Workflow](#github-actions-workflow)
4. [Manual Build Process](#manual-build-process)
5. [Testing](#testing)
6. [Distribution](#distribution)
7. [License Management](#license-management)
8. [Auto-Update System](#auto-update-system)

## Prerequisites

### Development Environment

- **Python 3.11+**
- **Node.js 20+**
- **Git**
- **Docker** (for containerized products)

### Platform-Specific Tools

#### Windows
- Visual Studio Build Tools
- WiX Toolset (for MSI installers)
- NSIS (alternative installer)

#### macOS
- Xcode Command Line Tools
- create-dmg utility

#### Linux
- build-essential
- dpkg-dev (for DEB packages)
- rpm-build (for RPM packages)
- appimagetool (for AppImage)

## Build System Architecture

### Directory Structure

```
iTechSmart/
├── build-tools/                    # Build scripts
│   ├── build_windows_exe.py       # Windows executable builder
│   ├── build_macos_app.py         # macOS application builder
│   ├── build_linux_binary.py      # Linux binary builder
│   ├── create_windows_installer.py # Windows installer creator
│   ├── create_macos_dmg.py        # macOS DMG creator
│   ├── create_linux_packages.py   # Linux package creator
│   ├── create_demo_version.py     # Demo version creator
│   ├── create_suite_installer.py  # Suite installer creator
│   └── generate_release_notes.py  # Release notes generator
├── src/
│   ├── license-system/            # License management
│   ├── auto-update/               # Auto-update system
│   ├── launcher/                  # Product launcher
│   ├── crash-reporting/           # Crash reporting
│   └── telemetry/                 # Usage telemetry
├── electron-installer/            # Web-based installer
├── installers/                    # Generated installers
├── dist/                          # Built executables
└── .github/workflows/             # CI/CD workflows
```

## GitHub Actions Workflow

### Automated Builds

The repository includes a comprehensive GitHub Actions workflow that automatically builds all products for all platforms.

#### Trigger Events

- **Push to main/develop** → Full build
- **Tag push (v*)** → Release build
- **Pull request** → Test build
- **Manual dispatch** → Custom build

#### Using GitHub Actions

##### Automatic Build on Push

```bash
git add .
git commit -m "Update products"
git push origin main
```

##### Creating a Release

```bash
# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Build all products for all platforms
# 2. Create demo versions
# 3. Create suite installers
# 4. Run tests
# 5. Create GitHub release with all artifacts
```

## Manual Build Process

### Building Individual Products

#### Windows

```bash
cd iTechSmart
python build-tools/build_windows_exe.py <product-name> <version>
python build-tools/create_windows_installer.py <product-name> <version>
```

#### macOS

```bash
cd iTechSmart
python build-tools/build_macos_app.py <product-name> <version>
python build-tools/create_macos_dmg.py <product-name> <version>
```

#### Linux

```bash
cd iTechSmart
python build-tools/build_linux_binary.py <product-name> <version>
python build-tools/create_linux_packages.py <product-name> <version>
```

## Testing

### Running Integration Tests

```bash
cd iTechSmart
python integration-tests/test_executables.py <platform> <version>
```

## License Management

### Generating License Keys

```bash
cd iTechSmart/src/license-system
python license_manager.py generate <type> <name> <email> [days]
```

## Auto-Update System

### Update Process

1. **Check** - Application checks for updates on startup
2. **Download** - Update package downloaded and verified
3. **Apply** - Update applied immediately or scheduled
4. **Verify** - New version validated and confirmed

## Support

- **Documentation**: https://itechsmart.dev/docs
- **Support Portal**: https://itechsmart.dev/support
- **Email**: support@itechsmart.dev

© 2025 iTechSmart. All rights reserved.