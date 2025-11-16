# 🍎 macOS Build Instructions

**Building the iTechSmart Suite Desktop Launcher for macOS**

---

## ⚠️ Important Note

**macOS installers MUST be built on a macOS system.** Cross-compilation from Linux or Windows is not supported by Apple's toolchain.

---

## 📋 Prerequisites

### System Requirements
- **macOS:** 10.13 (High Sierra) or later
- **Xcode Command Line Tools:** Required
- **Node.js:** Version 20.x or later
- **npm:** Latest version (comes with Node.js)
- **Disk Space:** At least 5GB free

### Installation Steps

#### 1. Install Xcode Command Line Tools
```bash
xcode-select --install
```

#### 2. Install Node.js
Download and install from: https://nodejs.org/
Or use Homebrew:
```bash
brew install node@20
```

#### 3. Verify Installation
```bash
# Check macOS version
sw_vers

# Check Xcode tools
xcode-select -p

# Check Node.js
node -v  # Should be v20.x or higher
npm -v
```

---

## 🚀 Building the macOS Installer

### Quick Build (Recommended)

1. **Clone the repository** (if not already done):
```bash
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/desktop-launcher
```

2. **Run the build script**:
```bash
./build-macos.sh
```

The script will:
- ✅ Check system requirements
- ✅ Install dependencies
- ✅ Build the application
- ✅ Create DMG installer
- ✅ Create PKG installer
- ✅ List all built files

### Manual Build

If you prefer to build manually:

```bash
# 1. Navigate to desktop-launcher directory
cd iTechSmart/desktop-launcher

# 2. Install dependencies
npm install

# 3. Build the application
npm run build

# 4. Build macOS installers
npm run package:mac
```

---

## 📦 Expected Output

After a successful build, you should have:

### DMG Installer
```
release/iTechSmart Suite-1.0.0.dmg
```
- **Type:** Disk Image
- **Size:** ~100-120 MB
- **Architectures:** x64 and arm64 (Universal)
- **Features:** Drag-and-drop installation

### PKG Installer
```
release/iTechSmart Suite-1.0.0.pkg
```
- **Type:** Package Installer
- **Size:** ~100-120 MB
- **Architectures:** x64 and arm64 (Universal)
- **Features:** Traditional installer wizard

### Unpacked Build
```
release/mac/iTechSmart Suite.app
```
- **Type:** Application Bundle
- **Use:** For testing before packaging

---

## 🔍 Verification

### Check Built Files
```bash
# List all built files
ls -lh release/

# Check DMG
ls -lh release/*.dmg

# Check PKG
ls -lh release/*.pkg

# Verify app bundle
ls -lh release/mac/
```

### Test the Application
```bash
# Open the app directly
open "release/mac/iTechSmart Suite.app"

# Or mount and test the DMG
open release/*.dmg
```

---

## 🔐 Code Signing (Optional)

For distribution outside the Mac App Store, you should sign your application.

### Prerequisites
- Apple Developer Account ($99/year)
- Developer ID Application certificate
- Developer ID Installer certificate

### Signing Process

1. **Get your signing identity**:
```bash
security find-identity -v -p codesigning
```

2. **Update package.json** with your identity:
```json
{
  "build": {
    "mac": {
      "identity": "Developer ID Application: Your Name (TEAM_ID)"
    }
  }
}
```

3. **Build with signing**:
```bash
npm run package:mac
```

### Notarization (Required for macOS 10.15+)

After signing, notarize with Apple:

```bash
# Submit for notarization
xcrun notarytool submit "release/iTechSmart Suite-1.0.0.dmg" \
  --apple-id "your@email.com" \
  --team-id "TEAM_ID" \
  --password "app-specific-password"

# Check status
xcrun notarytool info SUBMISSION_ID \
  --apple-id "your@email.com" \
  --team-id "TEAM_ID" \
  --password "app-specific-password"

# Staple the notarization
xcrun stapler staple "release/iTechSmart Suite-1.0.0.dmg"
```

---

## 🐛 Troubleshooting

### Build Fails

**Error: "xcode-select: error: tool 'xcodebuild' requires Xcode"**
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

**Error: "node: command not found"**
```bash
# Install Node.js
brew install node@20
# Or download from nodejs.org
```

**Error: "Cannot find module"**
```bash
# Clean and reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Build Succeeds but App Won't Open

**Error: "App is damaged and can't be opened"**
- This happens with unsigned apps on macOS 10.15+
- Solution: Sign and notarize the app, or:
```bash
# Remove quarantine attribute (for testing only)
xattr -cr "iTechSmart Suite.app"
```

**Error: "App can't be opened because Apple cannot check it"**
- Right-click the app and select "Open"
- Click "Open" in the dialog
- Or disable Gatekeeper temporarily (not recommended):
```bash
sudo spctl --master-disable
```

### DMG Won't Mount

**Error: "Resource busy"**
```bash
# Unmount any existing mounts
hdiutil detach /Volumes/iTechSmart\ Suite
# Try mounting again
open release/*.dmg
```

---

## 📊 Build Statistics

### Expected Build Time
- **First build:** 5-10 minutes (includes dependency download)
- **Subsequent builds:** 2-5 minutes
- **With signing:** Add 1-2 minutes
- **With notarization:** Add 5-15 minutes (Apple's servers)

### Expected File Sizes
- **DMG:** ~100-120 MB
- **PKG:** ~100-120 MB
- **Unpacked .app:** ~200-250 MB

### Supported Architectures
- **x64 (Intel):** ✅ Supported
- **arm64 (Apple Silicon):** ✅ Supported
- **Universal Binary:** ✅ Both architectures in one file

---

## 🎯 Distribution

### For Testing
1. Build without signing
2. Share DMG or PKG with testers
3. Testers may need to right-click and "Open"

### For Production
1. Build with code signing
2. Notarize with Apple
3. Distribute via:
   - Direct download from website
   - GitHub releases
   - Mac App Store (requires additional steps)
   - Homebrew Cask

---

## 📝 Build Configuration

The build configuration is in `package.json`:

```json
{
  "build": {
    "mac": {
      "category": "public.app-category.developer-tools",
      "icon": "assets/icons/icon.icns",
      "target": [
        {
          "target": "dmg",
          "arch": ["x64", "arm64"]
        },
        {
          "target": "pkg",
          "arch": ["x64", "arm64"]
        }
      ],
      "hardenedRuntime": true,
      "gatekeeperAssess": false
    }
  }
}
```

### Customization Options

**Change app category:**
```json
"category": "public.app-category.business"
```

**Build only DMG:**
```json
"target": ["dmg"]
```

**Build only for Apple Silicon:**
```json
"arch": ["arm64"]
```

---

## 🆘 Getting Help

### Resources
- **Electron Builder Docs:** https://www.electron.build/
- **Apple Developer:** https://developer.apple.com/
- **Node.js:** https://nodejs.org/

### Support
- **GitHub Issues:** https://github.com/Iteksmart/iTechSmart/issues
- **Email:** support@itechsmart.com
- **Documentation:** Check repository README files

---

## ✅ Checklist

Before building:
- [ ] Running on macOS 10.13 or later
- [ ] Xcode Command Line Tools installed
- [ ] Node.js 20.x or later installed
- [ ] Repository cloned
- [ ] In desktop-launcher directory

After building:
- [ ] DMG file created
- [ ] PKG file created
- [ ] App opens without errors
- [ ] All features work correctly
- [ ] Ready for distribution

---

## 🎉 Success!

Once you've successfully built the macOS installers, you'll have:

✅ **DMG Installer** - Drag-and-drop installation  
✅ **PKG Installer** - Traditional installer  
✅ **Universal Binary** - Works on Intel and Apple Silicon  
✅ **Production Ready** - Ready to distribute  

---

## 📞 Next Steps

After building:

1. **Test the installers** on different macOS versions
2. **Sign the app** (if distributing publicly)
3. **Notarize with Apple** (required for macOS 10.15+)
4. **Upload to GitHub** as release assets
5. **Update documentation** with download links
6. **Announce to users** that macOS version is available

---

**🍎 Ready to build for macOS! Follow these instructions on a Mac system. 🚀**

---

**Last Updated:** December 21, 2024  
**Version:** 1.0.0  
**Status:** Ready for macOS Build  
**Script:** build-macos.sh