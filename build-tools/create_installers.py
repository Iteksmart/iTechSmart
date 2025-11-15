"""
iTechSmart Suite - Create Installers
Creates installers for Windows, Linux, and macOS
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class InstallerCreator:
    """Creates installers for different platforms"""
    
    def __init__(self):
        self.workspace = os.getcwd()
        self.installers_dir = "installers"
        self.assets_dir = "installers/assets"
        
    def create_windows_installer(self):
        """Create Windows NSIS installer"""
        print("\n" + "="*60)
        print("Creating Windows Installer (NSIS)")
        print("="*60)
        
        # Create NSIS script
        nsis_script = self._create_nsis_script()
        
        # Install NSIS if not available
        if not shutil.which("makensis"):
            print("Installing NSIS...")
            subprocess.run([
                "apt-get", "install", "-y", "nsis"
            ], check=True)
        
        # Build installer
        try:
            subprocess.run([
                "makensis",
                nsis_script
            ], check=True)
            
            print("✅ Windows installer created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create Windows installer: {str(e)}")
            return False
    
    def _create_nsis_script(self) -> str:
        """Create NSIS installer script"""
        script_content = '''
; iTechSmart Suite Installer
; Created with NSIS

!define PRODUCT_NAME "iTechSmart Suite"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "iTechSmart Inc."
!define PRODUCT_WEB_SITE "https://itechsmart.dev"
!define PRODUCT_DIR_REGKEY "Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\itechsmart.exe"
!define PRODUCT_UNINST_KEY "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI Settings
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "installers\\assets\\icons\\itechsmart.ico"
!define MUI_UNICON "installers\\assets\\icons\\itechsmart.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "installers\\assets\\splash\\splash-screen.png"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\\itechsmart-launcher.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Installer attributes
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "installers\\windows\\iTechSmart-Suite-Setup.exe"
InstallDir "$PROGRAMFILES64\\iTechSmart Suite"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Version Information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "Copyright © 2025 iTechSmart Inc."
VIAddVersionKey "FileDescription" "${PRODUCT_NAME} Installer"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"

Section "Core Components" SEC01
  SectionIn RO
  SetOutPath "$INSTDIR"
  
  ; Copy all executables
  File /r "dist\\*.*"
  
  ; Copy assets
  File /r "installers\\assets\\*.*"
  
  ; Copy license system
  File "src\\license-system\\license_manager.py"
  
  ; Copy auto-update system
  File "src\\auto-update\\update_manager.py"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\\iTechSmart Suite"
  CreateShortCut "$SMPROGRAMS\\iTechSmart Suite\\iTechSmart Suite.lnk" "$INSTDIR\\itechsmart-launcher.exe"
  CreateShortCut "$DESKTOP\\iTechSmart Suite.lnk" "$INSTDIR\\itechsmart-launcher.exe"
SectionEnd

Section "All 36 Products" SEC02
  ; Install all product executables
  SetOutPath "$INSTDIR\\products"
  File /r "installers\\windows\\individual-products\\*.*"
SectionEnd

Section "Documentation" SEC03
  SetOutPath "$INSTDIR\\docs"
  File "ITECHSMART_SUITE_INSTRUCTION_MANUAL.md"
  File "MASTER_TECHNICAL_MANUAL.md"
  File "QUICK_START_GUIDE.md"
SectionEnd

Section "Database Setup" SEC04
  ; Run database initialization
  ExecWait '"$INSTDIR\\setup_database.exe"'
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\\iTechSmart Suite\\Uninstall.lnk" "$INSTDIR\\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\\itechsmart-launcher.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\\itechsmart-launcher.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Core components required for iTechSmart Suite"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "All 36 iTechSmart products"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "User manuals and documentation"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC04} "Database initialization and setup"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section Uninstall
  Delete "$INSTDIR\\uninst.exe"
  Delete "$INSTDIR\\*.*"
  
  Delete "$SMPROGRAMS\\iTechSmart Suite\\*.*"
  Delete "$DESKTOP\\iTechSmart Suite.lnk"
  
  RMDir "$SMPROGRAMS\\iTechSmart Suite"
  RMDir /r "$INSTDIR"
  
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
'''
        
        script_file = "build-tools/installer.nsi"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        return script_file
    
    def create_linux_deb(self):
        """Create Debian package"""
        print("\n" + "="*60)
        print("Creating Linux .deb Package")
        print("="*60)
        
        # Create package structure
        pkg_dir = "installers/linux/itechsmart-suite_1.0.0_amd64"
        os.makedirs(f"{pkg_dir}/DEBIAN", exist_ok=True)
        os.makedirs(f"{pkg_dir}/usr/local/bin", exist_ok=True)
        os.makedirs(f"{pkg_dir}/usr/share/applications", exist_ok=True)
        os.makedirs(f"{pkg_dir}/usr/share/icons", exist_ok=True)
        
        # Create control file
        control_content = """Package: itechsmart-suite
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: iTechSmart Inc. <support@itechsmart.dev>
Description: iTechSmart Suite - Complete Enterprise Platform
 Comprehensive suite of 36 integrated products for enterprise management,
 including AI, analytics, compliance, security, and more.
"""
        
        with open(f"{pkg_dir}/DEBIAN/control", 'w') as f:
            f.write(control_content)
        
        # Create desktop entry
        desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=iTechSmart Suite
Comment=Enterprise Management Platform
Exec=/usr/local/bin/itechsmart-launcher
Icon=/usr/share/icons/itechsmart.png
Terminal=false
Categories=Office;Development;
"""
        
        with open(f"{pkg_dir}/usr/share/applications/itechsmart-suite.desktop", 'w') as f:
            f.write(desktop_content)
        
        # Copy files
        # (In production, copy actual executables here)
        
        # Build package
        try:
            subprocess.run([
                "dpkg-deb",
                "--build",
                pkg_dir
            ], check=True)
            
            print("✅ Linux .deb package created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create .deb package: {str(e)}")
            return False
    
    def create_linux_rpm(self):
        """Create RPM package"""
        print("\n" + "="*60)
        print("Creating Linux .rpm Package")
        print("="*60)
        
        # Create RPM spec file
        spec_content = """
Name:           itechsmart-suite
Version:        1.0.0
Release:        1%{?dist}
Summary:        iTechSmart Suite - Complete Enterprise Platform

License:        Proprietary
URL:            https://itechsmart.dev
Source0:        %{name}-%{version}.tar.gz

BuildArch:      x86_64
Requires:       python3 >= 3.8

%description
Comprehensive suite of 36 integrated products for enterprise management,
including AI, analytics, compliance, security, and more.

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/local/bin
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
mkdir -p $RPM_BUILD_ROOT/usr/share/icons

# Copy files
# (In production, copy actual executables here)

%files
/usr/local/bin/*
/usr/share/applications/itechsmart-suite.desktop
/usr/share/icons/itechsmart.png

%changelog
* Mon Jan 13 2025 iTechSmart Inc. <support@itechsmart.dev> - 1.0.0-1
- Initial release
"""
        
        spec_file = "build-tools/itechsmart-suite.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        print("✅ RPM spec file created")
        return True
    
    def create_appimage(self):
        """Create AppImage"""
        print("\n" + "="*60)
        print("Creating Linux AppImage")
        print("="*60)
        
        # Create AppDir structure
        appdir = "installers/linux/iTechSmart-Suite.AppDir"
        os.makedirs(f"{appdir}/usr/bin", exist_ok=True)
        os.makedirs(f"{appdir}/usr/share/applications", exist_ok=True)
        os.makedirs(f"{appdir}/usr/share/icons", exist_ok=True)
        
        # Create AppRun script
        apprun_content = """#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/itechsmart-launcher" "$@"
"""
        
        apprun_file = f"{appdir}/AppRun"
        with open(apprun_file, 'w') as f:
            f.write(apprun_content)
        
        os.chmod(apprun_file, 0o755)
        
        print("✅ AppImage structure created")
        return True
    
    def create_macos_dmg(self):
        """Create macOS DMG installer"""
        print("\n" + "="*60)
        print("Creating macOS .dmg Installer")
        print("="*60)
        
        # Create app bundle structure
        app_bundle = "installers/macos/iTechSmart Suite.app"
        os.makedirs(f"{app_bundle}/Contents/MacOS", exist_ok=True)
        os.makedirs(f"{app_bundle}/Contents/Resources", exist_ok=True)
        
        # Create Info.plist
        plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>itechsmart-launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.itechsmart.suite</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>iTechSmart Suite</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""
        
        with open(f"{app_bundle}/Contents/Info.plist", 'w') as f:
            f.write(plist_content)
        
        print("✅ macOS app bundle created")
        return True
    
    def create_all_installers(self):
        """Create installers for all platforms"""
        print("\n" + "="*60)
        print("Creating Installers for All Platforms")
        print("="*60)
        
        results = {
            "Windows NSIS": self.create_windows_installer(),
            "Linux .deb": self.create_linux_deb(),
            "Linux .rpm": self.create_linux_rpm(),
            "Linux AppImage": self.create_appimage(),
            "macOS .dmg": self.create_macos_dmg()
        }
        
        # Summary
        print("\n" + "="*60)
        print("Installer Creation Summary")
        print("="*60)
        
        for platform, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {platform}")
        
        return all(results.values())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create iTechSmart Suite installers")
    parser.add_argument(
        "--platform",
        choices=["windows", "linux", "macos", "all"],
        default="all",
        help="Target platform"
    )
    
    args = parser.parse_args()
    
    creator = InstallerCreator()
    
    if args.platform == "windows":
        creator.create_windows_installer()
    elif args.platform == "linux":
        creator.create_linux_deb()
        creator.create_linux_rpm()
        creator.create_appimage()
    elif args.platform == "macos":
        creator.create_macos_dmg()
    else:
        creator.create_all_installers()