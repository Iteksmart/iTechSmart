# iTechSmart Suite - Quick Reference Card

**Version**: 1.0.0 | **Date**: January 13, 2025

---

## 🚀 Quick Build Commands

```bash
# Build everything for all platforms
python build-tools/master_build.py --all

# Build for specific platform
python build-tools/master_build.py --platform windows
python build-tools/master_build.py --platform linux
python build-tools/master_build.py --platform macos

# Build only products
python build-tools/build_all_products.py --platform windows

# Create only installers
python build-tools/create_installers.py --platform windows
```

---

## 🔑 License Management

```bash
# Generate license
python src/license-system/license_manager.py generate \
  enterprise "Company Name" "email@company.com" 365

# Activate license
python src/license-system/license_manager.py activate <key>

# Create trial
python src/license-system/license_manager.py trial

# Check status
python src/license-system/license_manager.py info
```

---

## 🔄 Auto-Update

```bash
# Check for updates
python src/auto-update/update_manager.py check

# Install updates
python src/auto-update/update_manager.py update

# Force update
python src/auto-update/update_manager.py update --force

# Rollback
python src/auto-update/update_manager.py rollback
```

---

## 📊 Telemetry

```bash
# Enable
python src/telemetry/telemetry_manager.py enable

# Disable
python src/telemetry/telemetry_manager.py disable

# Status
python src/telemetry/telemetry_manager.py status
```

---

## 🐛 Crash Reporting

```bash
# List crashes
python src/crash-reporting/crash_reporter.py list

# Clear crashes
python src/crash-reporting/crash_reporter.py clear
```

---

## 📦 Installation

### Windows
```bash
iTechSmart-Suite-Setup.exe
# or silent:
iTechSmart-Suite-Enterprise.msi /quiet
```

### Linux
```bash
# Debian/Ubuntu
sudo dpkg -i itechsmart-suite_1.0.0_amd64.deb

# Red Hat/CentOS
sudo rpm -i itechsmart-suite-1.0.0-1.x86_64.rpm

# AppImage
chmod +x iTechSmart-Suite.AppImage && ./iTechSmart-Suite.AppImage
```

### macOS
```bash
open iTechSmart-Suite.dmg
# or
sudo installer -pkg iTechSmart-Suite.pkg -target /
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `build-tools/master_build.py` | Main build orchestrator |
| `build-tools/build_all_products.py` | Build all 36 products |
| `build-tools/create_installers.py` | Create installers |
| `src/license-system/license_manager.py` | License management |
| `src/auto-update/update_manager.py` | Auto-update system |
| `src/telemetry/telemetry_manager.py` | Telemetry tracking |
| `src/crash-reporting/crash_reporter.py` | Crash reporting |
| `src/launcher/itechsmart_launcher.py` | Main launcher GUI |

---

## 🎯 License Types

| Type | Users | Duration | Support |
|------|-------|----------|---------|
| Trial | 5 | 30 days | Community |
| Basic | 25 | Perpetual | Email |
| Professional | 100 | Perpetual | Priority |
| Enterprise | 1,000 | Perpetual | 24/7 |
| Unlimited | ∞ | Perpetual | Dedicated |

---

## 📞 Support

- **Email**: support@itechsmart.dev
- **Website**: https://itechsmart.dev
- **Docs**: https://docs.itechsmart.dev

---

## ✅ Build Checklist

- [ ] Run `python build-tools/master_build.py --all`
- [ ] Test installers on all platforms
- [ ] Generate license keys
- [ ] Test license activation
- [ ] Test auto-update
- [ ] Verify checksums
- [ ] Package for distribution
- [ ] Upload to distribution server

---

**Copyright © 2025 iTechSmart Inc.**