# iTechSmart Suite - Distribution Guide

## Overview

This guide covers how to distribute the built executables from the iTechSmart Suite to end users.

## Table of Contents

1. [Download Built Artifacts](#download-built-artifacts)
2. [Distribution Channels](#distribution-channels)
3. [File Organization](#file-organization)
4. [Installation Instructions](#installation-instructions)
5. [License Distribution](#license-distribution)
6. [Update Mechanism](#update-mechanism)
7. [Support Resources](#support-resources)

## Download Built Artifacts

### From GitHub Actions

After a successful build, artifacts are available in the Actions tab:

1. Go to **Actions** → Select the workflow run
2. Scroll to **Artifacts** section
3. Download the artifacts you need:
   - `windows-<product>-<version>` - Windows executables
   - `macos-<product>-<version>` - macOS applications
   - `linux-<product>-<version>` - Linux binaries
   - `suite-<platform>-<version>` - Complete suite installers

### From GitHub Releases

For tagged releases, artifacts are available on the Releases page:

1. Go to **Releases** → Select the version
2. Download from **Assets** section
3. All platforms and products available in one place

## Distribution Channels

### 1. GitHub Releases (Primary)

**Best for**: Public releases, version tracking

**URL**: https://github.com/Iteksmart/iTechSmart/releases

**Advantages**:
- Automatic from CI/CD
- Version history
- Download statistics
- Checksums included

### 2. Direct Download Links

**Best for**: Website integration, direct links

**Format**: 
```
https://github.com/Iteksmart/iTechSmart/releases/download/v1.0.0/<product>-1.0.0-<platform>.<ext>
```

**Example**:
```
https://github.com/Iteksmart/iTechSmart/releases/download/v1.0.0/itechsmart-supreme-1.0.0-windows.exe
```

### 3. Enterprise Portal

**Best for**: Licensed customers, private distribution

**Features**:
- License validation
- Customer-specific builds
- Usage tracking
- Support integration

### 4. Package Managers (Future)

**Planned support**:
- **Windows**: Chocolatey, Winget
- **macOS**: Homebrew
- **Linux**: apt, yum, snap

## File Organization

### Windows Distribution

```
itechsmart-suite-windows-1.0.0/
├── installers/
│   ├── itechsmart-supreme-1.0.0.msi
│   ├── itechsmart-ninja-1.0.0.msi
│   └── ... (all products)
├── executables/
│   ├── itechsmart-supreme.exe
│   ├── itechsmart-ninja.exe
│   └── ... (all products)
├── demo/
│   ├── itechsmart-supreme-demo.exe
│   └── ... (demo versions)
├── suite-installer.exe
├── README.txt
├── LICENSE.txt
└── checksums.sha256
```

### macOS Distribution

```
itechsmart-suite-macos-1.0.0/
├── installers/
│   ├── iTechSmartSupreme-1.0.0.dmg
│   ├── iTechSmartNinja-1.0.0.dmg
│   └── ... (all products)
├── applications/
│   ├── iTechSmartSupreme.app
│   ├── iTechSmartNinja.app
│   └── ... (all products)
├── demo/
│   ├── iTechSmartSupreme-demo.app
│   └── ... (demo versions)
├── suite-installer.dmg
├── README.txt
├── LICENSE.txt
└── checksums.sha256
```

### Linux Distribution

```
itechsmart-suite-linux-1.0.0/
├── deb/
│   ├── itechsmart-supreme_1.0.0_amd64.deb
│   └── ... (all products)
├── rpm/
│   ├── itechsmart-supreme-1.0.0.x86_64.rpm
│   └── ... (all products)
├── appimage/
│   ├── iTechSmartSupreme-1.0.0.AppImage
│   └── ... (all products)
├── binaries/
│   ├── itechsmart-supreme
│   └── ... (all products)
├── demo/
│   ├── itechsmart-supreme-demo
│   └── ... (demo versions)
├── install.sh
├── README.txt
├── LICENSE.txt
└── checksums.sha256
```

## Installation Instructions

### Windows

#### MSI Installer (Recommended)
```
1. Download the .msi file
2. Double-click to run
3. Follow the installation wizard
4. Launch from Start Menu
```

#### Standalone Executable
```
1. Download the .exe file
2. Run as Administrator (first time)
3. Accept license agreement
4. Application is ready to use
```

#### Suite Installer
```
1. Download suite-installer.exe
2. Run as Administrator
3. Select products to install
4. Configure installation options
5. Complete installation
```

### macOS

#### DMG Installer (Recommended)
```
1. Download the .dmg file
2. Open the DMG
3. Drag application to Applications folder
4. Launch from Applications
5. Allow in System Preferences > Security (first time)
```

#### Application Bundle
```
1. Download the .app file
2. Move to Applications folder
3. Right-click → Open (first time)
4. Application is ready to use
```

### Linux

#### DEB Package (Debian/Ubuntu)
```bash
# Download and install
sudo dpkg -i itechsmart-supreme_1.0.0_amd64.deb

# Install dependencies if needed
sudo apt-get install -f

# Launch
itechsmart-supreme
```

#### RPM Package (RedHat/Fedora)
```bash
# Download and install
sudo rpm -i itechsmart-supreme-1.0.0.x86_64.rpm

# Or with yum
sudo yum install itechsmart-supreme-1.0.0.x86_64.rpm

# Launch
itechsmart-supreme
```

#### AppImage (Universal)
```bash
# Download and make executable
chmod +x iTechSmartSupreme-1.0.0.AppImage

# Run
./iTechSmartSupreme-1.0.0.AppImage
```

#### Binary
```bash
# Download and make executable
chmod +x itechsmart-supreme

# Run
./itechsmart-supreme
```

## License Distribution

### Trial Licenses

**Automatic**: Demo versions include 30-day trial license

**Features**:
- 5 users maximum
- 10 projects maximum
- 1,000 API calls/day
- 10 GB storage
- Demo watermark

### Full Licenses

**Distribution Methods**:

1. **Email**: Send license key to customer
2. **Portal**: Customer downloads from portal
3. **Installer**: Embedded in custom installer

**Activation**:
```bash
# Command line
itechsmart-supreme --activate LICENSE-KEY-HERE

# Or through GUI
Settings → License → Enter License Key
```

### License Types

| Type | Users | Projects | API Calls | Storage | Support |
|------|-------|----------|-----------|---------|---------|
| Trial | 5 | 10 | 1K/day | 10 GB | Community |
| Basic | 25 | 50 | 10K/day | 100 GB | Email |
| Professional | 100 | 200 | 50K/day | 500 GB | Priority |
| Enterprise | 1000 | Unlimited | Unlimited | Unlimited | 24/7 |
| Unlimited | Unlimited | Unlimited | Unlimited | Unlimited | Dedicated |

## Update Mechanism

### Automatic Updates

**Default Behavior**:
- Check for updates on startup
- Download in background
- Prompt user to install
- Apply on next restart

**Configuration**:
```json
{
  "auto_update": {
    "enabled": true,
    "check_frequency": "daily",
    "download_automatically": true,
    "install_automatically": false
  }
}
```

### Manual Updates

**Check for updates**:
```bash
itechsmart-supreme --check-updates
```

**Download update**:
```bash
itechsmart-supreme --download-update
```

**Install update**:
```bash
itechsmart-supreme --install-update
```

### Update Server

**URL**: https://updates.itechsmart.dev

**Endpoints**:
- `/api/updates/<product>` - Check for updates
- `/api/download/<product>/<version>` - Download update
- `/api/changelog/<product>/<version>` - Get changelog

## Support Resources

### Documentation

- **User Guides**: https://itechsmart.dev/docs
- **API Documentation**: https://itechsmart.dev/api
- **Video Tutorials**: https://itechsmart.dev/tutorials
- **FAQ**: https://itechsmart.dev/faq

### Support Channels

- **Email**: support@itechsmart.dev
- **Portal**: https://itechsmart.dev/support
- **Community**: https://community.itechsmart.dev
- **GitHub Issues**: https://github.com/Iteksmart/iTechSmart/issues

### Installation Support

**Common Issues**:

1. **Windows SmartScreen Warning**
   - Click "More info" → "Run anyway"
   - Or: Code sign executables

2. **macOS Gatekeeper Blocking**
   - Right-click → Open (first time)
   - Or: System Preferences → Security → Allow

3. **Linux Permission Denied**
   - Run: `chmod +x <file>`
   - Or: Install via package manager

4. **Missing Dependencies**
   - Windows: Install Visual C++ Redistributable
   - macOS: Install Xcode Command Line Tools
   - Linux: Install via package manager

### Verification

**Verify checksums**:
```bash
# Windows (PowerShell)
Get-FileHash -Algorithm SHA256 itechsmart-supreme.exe

# macOS/Linux
shasum -a 256 itechsmart-supreme
```

**Compare with checksums.sha256 file**

## Distribution Checklist

### Pre-Distribution

- [ ] All builds successful
- [ ] Integration tests passed
- [ ] Checksums generated
- [ ] Release notes prepared
- [ ] Licenses generated
- [ ] Documentation updated

### Distribution

- [ ] Upload to GitHub Releases
- [ ] Update website download links
- [ ] Send notification emails
- [ ] Update documentation
- [ ] Post on social media
- [ ] Notify support team

### Post-Distribution

- [ ] Monitor download statistics
- [ ] Track installation issues
- [ ] Collect user feedback
- [ ] Monitor crash reports
- [ ] Plan next release

## Best Practices

### Security

1. **Code Signing**: Sign all executables
2. **Checksums**: Provide SHA256 checksums
3. **HTTPS**: Use HTTPS for all downloads
4. **Verification**: Document verification process

### User Experience

1. **Clear Instructions**: Provide step-by-step guides
2. **Multiple Formats**: Offer various installation methods
3. **Quick Start**: Include quick start guide
4. **Support**: Make support easily accessible

### Maintenance

1. **Version Control**: Track all distributed versions
2. **Update Path**: Ensure smooth update process
3. **Backward Compatibility**: Maintain compatibility
4. **Deprecation**: Plan deprecation carefully

## Metrics to Track

- Download counts per product
- Installation success rate
- Update adoption rate
- License activation rate
- Support ticket volume
- User satisfaction scores

## Contact

For distribution questions:
- **Email**: distribution@itechsmart.dev
- **Sales**: sales@itechsmart.dev
- **Support**: support@itechsmart.dev

---

© 2025 iTechSmart. All rights reserved.