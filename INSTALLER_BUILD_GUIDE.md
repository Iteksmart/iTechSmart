# iTechSmart Suite - Complete Installer & Executable Build Guide

**Version**: 1.0.0  
**Date**: January 13, 2025  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Build Components](#build-components)
4. [Quick Start](#quick-start)
5. [Detailed Build Process](#detailed-build-process)
6. [Platform-Specific Instructions](#platform-specific-instructions)
7. [Security Features](#security-features)
8. [Testing](#testing)
9. [Distribution](#distribution)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This guide covers the complete process of building encrypted executables and installers for the iTechSmart Suite, including:

- ✅ **36 Individual Product Executables** - Standalone encrypted executables
- ✅ **Full Suite Installer** - Complete installation package
- ✅ **Enterprise Deployment Package** - Silent install with centralized config
- ✅ **Demo/Trial Version** - 30-day trial with feature limitations
- ✅ **Multi-Platform Support** - Windows, Linux, macOS
- ✅ **Advanced Security** - PyArmor encryption + Cython compilation
- ✅ **License Management** - Built-in license key system
- ✅ **Auto-Update** - Automatic update checking and installation
- ✅ **Telemetry & Analytics** - Usage tracking and performance metrics
- ✅ **Crash Reporting** - Automatic crash detection and reporting

---

## 🔧 Prerequisites

### Required Software

```bash
# Python 3.11+
python --version

# Build tools
pip install pyinstaller pyarmor cython wheel setuptools twine cryptography pynacl

# Image processing
apt-get install imagemagick

# Windows installer (NSIS)
apt-get install nsis

# Linux packaging
apt-get install dpkg-dev rpm build-essential

# macOS (if building on macOS)
brew install create-dmg
```

### Required Files

- ✅ Logo file: `logo itechsmart.JPG`
- ✅ All 36 product source directories
- ✅ License system code
- ✅ Auto-update system code
- ✅ Telemetry system code
- ✅ Crash reporting system code

---

## 📦 Build Components

### 1. License System (`src/license-system/`)
- `license_manager.py` - License validation and management
- Supports: Trial, Basic, Professional, Enterprise, Unlimited
- 30-day trial period
- Machine-locked activation
- Feature restrictions by license type

### 2. Auto-Update System (`src/auto-update/`)
- `update_manager.py` - Automatic update checking and installation
- Version checking
- Secure download with checksum verification
- Automatic rollback on failure
- Background update checking

### 3. Telemetry System (`src/telemetry/`)
- `telemetry_manager.py` - Usage tracking and analytics
- Event tracking
- Performance metrics
- System resource monitoring
- Anonymous or identified tracking

### 4. Crash Reporting (`src/crash-reporting/`)
- `crash_reporter.py` - Crash detection and reporting
- Automatic crash detection
- Stack trace collection
- System information gathering
- Crash report submission

### 5. Main Launcher (`src/launcher/`)
- `itechsmart_launcher.py` - Central launcher application
- Product management
- License checking
- Update management
- GUI interface

---

## 🚀 Quick Start

### One-Command Build (All Platforms)

```bash
# Build everything
python build-tools/master_build.py --all

# Build specific platform
python build-tools/master_build.py --platform windows
python build-tools/master_build.py --platform linux
python build-tools/master_build.py --platform macos
```

### Step-by-Step Build

```bash
# 1. Prepare assets
python build-tools/prepare_assets.py

# 2. Build all 36 products
python build-tools/build_all_products.py --platform windows

# 3. Create installers
python build-tools/create_installers.py --platform windows

# 4. Package for distribution
python build-tools/package_distribution.py
```

---

## 🔨 Detailed Build Process

### Phase 1: Asset Preparation

```bash
# Convert logo to all required formats
python build-tools/prepare_assets.py

# Output:
# - installers/assets/logo-512.png
# - installers/assets/logo-256.png
# - installers/assets/logo-128.png
# - installers/assets/logo-64.png
# - installers/assets/logo-48.png
# - installers/assets/logo-32.png
# - installers/assets/logo-16.png
# - installers/assets/splash/splash-screen.png
# - installers/assets/icons/itechsmart.ico
```

### Phase 2: Code Encryption

```bash
# Encrypt all product code with PyArmor
for product in products:
    pyarmor gen -O ${product}_encrypted -r ${product}

# Apply Cython compilation for maximum protection
cythonize -i *.py
```

### Phase 3: Executable Building

```bash
# Build individual products
python build-tools/build_all_products.py

# Output:
# - dist/itechsmart-enterprise.exe
# - dist/itechsmart-ninja.exe
# - ... (all 36 products)
```

### Phase 4: Installer Creation

```bash
# Create platform-specific installers
python build-tools/create_installers.py --platform all

# Output:
# Windows:
# - installers/windows/iTechSmart-Suite-Setup.exe
# - installers/windows/iTechSmart-Suite-Enterprise.msi
# - installers/windows/iTechSmart-Suite-Trial.exe

# Linux:
# - installers/linux/itechsmart-suite_1.0.0_amd64.deb
# - installers/linux/itechsmart-suite-1.0.0-1.x86_64.rpm
# - installers/linux/iTechSmart-Suite.AppImage

# macOS:
# - installers/macos/iTechSmart-Suite.dmg
# - installers/macos/iTechSmart-Suite.pkg
```

---

## 🖥️ Platform-Specific Instructions

### Windows

#### NSIS Installer
```bash
# Install NSIS
apt-get install nsis

# Build installer
makensis build-tools/installer.nsi

# Output: installers/windows/iTechSmart-Suite-Setup.exe
```

#### MSI Installer (Enterprise)
```bash
# Install WiX Toolset
# Create MSI with silent install support
candle installer.wxs
light installer.wixobj -out iTechSmart-Suite-Enterprise.msi
```

### Linux

#### Debian Package (.deb)
```bash
# Build .deb package
dpkg-deb --build installers/linux/itechsmart-suite_1.0.0_amd64

# Install
sudo dpkg -i itechsmart-suite_1.0.0_amd64.deb
```

#### RPM Package
```bash
# Build RPM
rpmbuild -ba build-tools/itechsmart-suite.spec

# Install
sudo rpm -i itechsmart-suite-1.0.0-1.x86_64.rpm
```

#### AppImage
```bash
# Create AppImage
appimagetool installers/linux/iTechSmart-Suite.AppDir

# Run
chmod +x iTechSmart-Suite.AppImage
./iTechSmart-Suite.AppImage
```

### macOS

#### DMG Installer
```bash
# Create DMG
create-dmg \
  --volname "iTechSmart Suite" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  iTechSmart-Suite.dmg \
  "installers/macos/iTechSmart Suite.app"
```

#### PKG Installer
```bash
# Create PKG
pkgbuild --root "installers/macos/iTechSmart Suite.app" \
         --identifier com.itechsmart.suite \
         --version 1.0.0 \
         iTechSmart-Suite.pkg
```

---

## 🔒 Security Features

### 1. Code Encryption (PyArmor)

```bash
# Encrypt with PyArmor
pyarmor gen -O encrypted_output -r source_directory

# Features:
# - Bytecode obfuscation
# - Runtime encryption
# - Anti-debugging
# - Anti-tampering
```

### 2. Cython Compilation

```bash
# Compile to C extensions
cythonize -i module.py

# Features:
# - Native code compilation
# - Performance improvement
# - Source code protection
```

### 3. License Validation

```python
# License checking on startup
license_manager = LicenseManager()
is_valid, license_data, message = license_manager.load_license()

if not is_valid:
    # Offer trial or request activation
    pass
```

### 4. Machine Locking

```python
# License tied to machine ID
machine_id = get_machine_id()  # Based on MAC + hostname
license_data["machine_id"] = machine_id
```

---

## 🧪 Testing

### Test Individual Executables

```bash
# Test each product
./dist/itechsmart-enterprise.exe
./dist/itechsmart-ninja.exe
# ... test all 36 products
```

### Test Installers

```bash
# Windows
iTechSmart-Suite-Setup.exe /S  # Silent install

# Linux
sudo dpkg -i itechsmart-suite_1.0.0_amd64.deb

# macOS
open iTechSmart-Suite.dmg
```

### Test License System

```bash
# Generate test license
python src/license-system/license_manager.py generate trial "Test User" "test@example.com" 30

# Activate license
python src/license-system/license_manager.py activate <license_key>

# Check status
python src/license-system/license_manager.py info
```

### Test Auto-Update

```bash
# Check for updates
python src/auto-update/update_manager.py check

# Test update
python src/auto-update/update_manager.py update --force
```

---

## 📤 Distribution

### File Structure

```
iTechSmart-Suite-v1.0.0/
├── Windows/
│   ├── iTechSmart-Suite-Setup.exe (Full installer)
│   ├── iTechSmart-Suite-Enterprise.msi (Enterprise silent install)
│   └── iTechSmart-Suite-Trial.exe (30-day trial)
├── Linux/
│   ├── itechsmart-suite_1.0.0_amd64.deb
│   ├── itechsmart-suite-1.0.0-1.x86_64.rpm
│   └── iTechSmart-Suite.AppImage
├── macOS/
│   ├── iTechSmart-Suite.dmg
│   └── iTechSmart-Suite.pkg
├── Documentation/
│   ├── INSTALLATION_GUIDE.md
│   ├── USER_MANUAL.md
│   ├── LICENSE_GUIDE.md
│   └── QUICK_START.md
└── README.txt
```

### Checksums

```bash
# Generate checksums for all installers
sha256sum installers/*/* > SHA256SUMS.txt

# Verify
sha256sum -c SHA256SUMS.txt
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. PyInstaller Build Fails

```bash
# Solution: Install missing dependencies
pip install -r requirements.txt

# Clear cache
pyinstaller --clean your_spec.spec
```

#### 2. PyArmor Encryption Fails

```bash
# Solution: Update PyArmor
pip install --upgrade pyarmor

# Check license
pyarmor --version
```

#### 3. NSIS Installer Fails

```bash
# Solution: Check NSIS installation
makensis /VERSION

# Verify paths in .nsi script
```

#### 4. License Activation Fails

```bash
# Solution: Check machine ID
python -c "from license_manager import LicenseManager; print(LicenseManager()._get_machine_id())"

# Regenerate license for correct machine
```

---

## 📞 Support

For build issues or questions:

- **Email**: support@itechsmart.dev
- **Website**: https://itechsmart.dev/support
- **Documentation**: https://docs.itechsmart.dev

---

## 📄 License

Copyright © 2025 iTechSmart Inc. All rights reserved.

---

**Build Date**: January 13, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready