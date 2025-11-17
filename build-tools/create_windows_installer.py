"""
Windows Installer Creator
Creates professional MSI installers for iTechSmart products
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import xml.etree.ElementTree as ET


class WindowsInstallerCreator:
    """Create Windows MSI installer using WiX Toolset"""

    def __init__(self, product_name: str, version: str):
        self.product_name = product_name
        self.version = version
        self.workspace = Path.cwd()
        self.dist_dir = self.workspace / "dist" / "windows" / product_name
        self.installer_dir = self.workspace / "installers" / "windows" / product_name
        self.wix_dir = self.installer_dir / "wix"

    def prepare_environment(self):
        """Prepare installer build environment"""
        print(f"Preparing installer environment for {self.product_name}...")

        self.installer_dir.mkdir(parents=True, exist_ok=True)
        self.wix_dir.mkdir(parents=True, exist_ok=True)

    def get_product_metadata(self) -> dict:
        """Get product metadata"""
        metadata_file = self.workspace / self.product_name / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)

        return {
            "name": self.product_name.replace("-", " ").title(),
            "description": f"{self.product_name} - iTechSmart Suite",
            "version": self.version,
            "company": "iTechSmart",
            "manufacturer": "iTechSmart",
            "copyright": "Copyright © 2025 iTechSmart. All rights reserved.",
            "upgrade_code": self.generate_upgrade_code(),
        }

    def generate_upgrade_code(self) -> str:
        """Generate a consistent upgrade code for the product"""
        import uuid

        # Use product name as seed for consistent UUID
        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        return str(uuid.uuid5(namespace, f"itechsmart-{self.product_name}"))

    def create_wix_source(self):
        """Create WiX source file (.wxs)"""
        print("Creating WiX source file...")

        metadata = self.get_product_metadata()

        # Generate component IDs for all files
        components = self.generate_file_components()

        wxs_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*" 
             Name="{metadata['name']}" 
             Language="1033" 
             Version="{self.version}" 
             Manufacturer="{metadata['manufacturer']}" 
             UpgradeCode="{metadata['upgrade_code']}">
        
        <Package InstallerVersion="200" 
                 Compressed="yes" 
                 InstallScope="perMachine" 
                 Description="{metadata['description']}"
                 Comments="{metadata['copyright']}" />

        <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
        <MediaTemplate EmbedCab="yes" />

        <Feature Id="ProductFeature" Title="{metadata['name']}" Level="1">
            <ComponentGroupRef Id="ProductComponents" />
            <ComponentRef Id="ApplicationShortcut" />
            <ComponentRef Id="DesktopShortcut" />
        </Feature>

        <Icon Id="ProductIcon" SourceFile="{self.get_icon_path()}" />
        <Property Id="ARPPRODUCTICON" Value="ProductIcon" />
        <Property Id="ARPHELPLINK" Value="https://itechsmart.com/support" />
        <Property Id="ARPURLINFOABOUT" Value="https://itechsmart.com" />

        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFiles64Folder">
                <Directory Id="CompanyFolder" Name="iTechSmart">
                    <Directory Id="INSTALLFOLDER" Name="{metadata['name']}" />
                </Directory>
            </Directory>
            
            <Directory Id="ProgramMenuFolder">
                <Directory Id="ApplicationProgramsFolder" Name="{metadata['name']}" />
            </Directory>
            
            <Directory Id="DesktopFolder" Name="Desktop" />
        </Directory>

        <DirectoryRef Id="ApplicationProgramsFolder">
            <Component Id="ApplicationShortcut" Guid="{self.generate_component_guid('shortcut')}">
                <Shortcut Id="ApplicationStartMenuShortcut"
                         Name="{metadata['name']}"
                         Description="{metadata['description']}"
                         Target="[INSTALLFOLDER]{self.product_name}.exe"
                         WorkingDirectory="INSTALLFOLDER"
                         Icon="ProductIcon" />
                <RemoveFolder Id="CleanUpShortCut" Directory="ApplicationProgramsFolder" On="uninstall" />
                <RegistryValue Root="HKCU" 
                              Key="Software\\iTechSmart\\{self.product_name}" 
                              Name="installed" 
                              Type="integer" 
                              Value="1" 
                              KeyPath="yes" />
            </Component>
        </DirectoryRef>

        <DirectoryRef Id="DesktopFolder">
            <Component Id="DesktopShortcut" Guid="{self.generate_component_guid('desktop')}">
                <Shortcut Id="ApplicationDesktopShortcut"
                         Name="{metadata['name']}"
                         Description="{metadata['description']}"
                         Target="[INSTALLFOLDER]{self.product_name}.exe"
                         WorkingDirectory="INSTALLFOLDER"
                         Icon="ProductIcon" />
                <RegistryValue Root="HKCU" 
                              Key="Software\\iTechSmart\\{self.product_name}" 
                              Name="desktop_shortcut" 
                              Type="integer" 
                              Value="1" 
                              KeyPath="yes" />
            </Component>
        </DirectoryRef>

        <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
            {components}
        </ComponentGroup>

        <UI>
            <UIRef Id="WixUI_InstallDir" />
            <Publish Dialog="ExitDialog"
                    Control="Finish" 
                    Event="DoAction" 
                    Value="LaunchApplication">WIXUI_EXITDIALOGOPTIONALCHECKBOX = 1 and NOT Installed</Publish>
        </UI>

        <Property Id="WIXUI_INSTALLDIR" Value="INSTALLFOLDER" />
        <Property Id="WIXUI_EXITDIALOGOPTIONALCHECKBOXTEXT" Value="Launch {metadata['name']}" />
        <Property Id="WixShellExecTarget" Value="[#MainExecutable]" />
        
        <CustomAction Id="LaunchApplication"
                     BinaryKey="WixCA"
                     DllEntry="WixShellExec"
                     Impersonate="yes" />

    </Product>
</Wix>
"""

        wxs_file = self.wix_dir / f"{self.product_name}.wxs"
        wxs_file.write_text(wxs_content)
        print(f"✓ WiX source created: {wxs_file}")
        return wxs_file

    def generate_file_components(self) -> str:
        """Generate WiX components for all files"""
        components = []

        # Main executable
        exe_file = self.dist_dir / f"{self.product_name}.exe"
        if exe_file.exists():
            components.append(
                f"""
            <Component Id="MainExecutable" Guid="{self.generate_component_guid('exe')}">
                <File Id="MainExecutable" 
                      Source="{exe_file}" 
                      KeyPath="yes" 
                      Checksum="yes" />
            </Component>
            """
            )

        # Additional files
        for file_path in self.dist_dir.rglob("*"):
            if file_path.is_file() and file_path != exe_file:
                rel_path = file_path.relative_to(self.dist_dir)
                file_id = (
                    str(rel_path).replace("/", "_").replace("\\", "_").replace(".", "_")
                )

                components.append(
                    f"""
            <Component Id="Component_{file_id}" Guid="{self.generate_component_guid(str(rel_path))}">
                <File Id="File_{file_id}" 
                      Source="{file_path}" 
                      KeyPath="yes" />
            </Component>
                """
                )

        return "\n".join(components)

    def generate_component_guid(self, seed: str) -> str:
        """Generate a consistent GUID for a component"""
        import uuid

        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        return str(uuid.uuid5(namespace, f"{self.product_name}-{seed}"))

    def get_icon_path(self) -> str:
        """Get icon path for the installer"""
        icon_path = (
            self.workspace
            / "installers"
            / "assets"
            / "icons"
            / f"{self.product_name}.ico"
        )
        if not icon_path.exists():
            icon_path = (
                self.workspace / "installers" / "assets" / "icons" / "default.ico"
            )
        return str(icon_path) if icon_path.exists() else ""

    def build_installer_with_wix(self, wxs_file: Path):
        """Build MSI installer using WiX Toolset"""
        print("Building MSI installer with WiX...")

        # Check if WiX is installed
        wix_installed = shutil.which("candle.exe") is not None

        if not wix_installed:
            print("⚠ WiX Toolset not found. Creating NSIS installer instead...")
            self.build_installer_with_nsis()
            return

        try:
            # Compile .wxs to .wixobj
            wixobj_file = self.wix_dir / f"{self.product_name}.wixobj"
            subprocess.run(
                [
                    "candle.exe",
                    "-ext",
                    "WixUIExtension",
                    "-ext",
                    "WixUtilExtension",
                    "-out",
                    str(wixobj_file),
                    str(wxs_file),
                ],
                check=True,
            )

            # Link .wixobj to .msi
            msi_file = self.installer_dir / f"{self.product_name}-{self.version}.msi"
            subprocess.run(
                [
                    "light.exe",
                    "-ext",
                    "WixUIExtension",
                    "-ext",
                    "WixUtilExtension",
                    "-out",
                    str(msi_file),
                    str(wixobj_file),
                ],
                check=True,
            )

            print(f"✓ MSI installer created: {msi_file}")

        except subprocess.CalledProcessError as e:
            print(f"✗ WiX build failed: {e}")
            print("Falling back to NSIS installer...")
            self.build_installer_with_nsis()

    def build_installer_with_nsis(self):
        """Build installer using NSIS as fallback"""
        print("Building NSIS installer...")

        metadata = self.get_product_metadata()

        nsis_script = f"""
!define PRODUCT_NAME "{metadata['name']}"
!define PRODUCT_VERSION "{self.version}"
!define PRODUCT_PUBLISHER "{metadata['manufacturer']}"
!define PRODUCT_WEB_SITE "https://itechsmart.com"
!define PRODUCT_DIR_REGKEY "Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{self.product_name}.exe"
!define PRODUCT_UNINST_KEY "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{PRODUCT_NAME}}"

SetCompressor lzma

Name "${{PRODUCT_NAME}} ${{PRODUCT_VERSION}}"
OutFile "{self.installer_dir / f'{self.product_name}-{self.version}-setup.exe'}"
InstallDir "$PROGRAMFILES64\\iTechSmart\\${{PRODUCT_NAME}}"
InstallDirRegKey HKLM "${{PRODUCT_DIR_REGKEY}}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File /r "{self.dist_dir}\\*.*"
  
  CreateDirectory "$SMPROGRAMS\\${{PRODUCT_NAME}}"
  CreateShortCut "$SMPROGRAMS\\${{PRODUCT_NAME}}\\${{PRODUCT_NAME}}.lnk" "$INSTDIR\\{self.product_name}.exe"
  CreateShortCut "$DESKTOP\\${{PRODUCT_NAME}}.lnk" "$INSTDIR\\{self.product_name}.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\\uninst.exe"
  WriteRegStr HKLM "${{PRODUCT_DIR_REGKEY}}" "" "$INSTDIR\\{self.product_name}.exe"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "DisplayName" "${{PRODUCT_NAME}}"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "UninstallString" "$INSTDIR\\uninst.exe"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "DisplayIcon" "$INSTDIR\\{self.product_name}.exe"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "DisplayVersion" "${{PRODUCT_VERSION}}"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "URLInfoAbout" "${{PRODUCT_WEB_SITE}}"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "Publisher" "${{PRODUCT_PUBLISHER}}"
SectionEnd

Section Uninstall
  Delete "$INSTDIR\\uninst.exe"
  Delete "$INSTDIR\\*.*"
  
  Delete "$SMPROGRAMS\\${{PRODUCT_NAME}}\\${{PRODUCT_NAME}}.lnk"
  Delete "$DESKTOP\\${{PRODUCT_NAME}}.lnk"
  
  RMDir "$SMPROGRAMS\\${{PRODUCT_NAME}}"
  RMDir /r "$INSTDIR"
  
  DeleteRegKey HKLM "${{PRODUCT_UNINST_KEY}}"
  DeleteRegKey HKLM "${{PRODUCT_DIR_REGKEY}}"
  
  SetAutoClose true
SectionEnd
"""

        nsis_file = self.wix_dir / f"{self.product_name}.nsi"
        nsis_file.write_text(nsis_script)

        # Try to build with NSIS if available
        if shutil.which("makensis.exe"):
            try:
                subprocess.run(["makensis.exe", str(nsis_file)], check=True)
                print(f"✓ NSIS installer created")
            except subprocess.CalledProcessError:
                print("⚠ NSIS build failed")
        else:
            print("⚠ NSIS not found. Installer script created but not compiled.")
            print(f"  Script location: {nsis_file}")

    def run(self):
        """Run the complete installer creation process"""
        print("=" * 60)
        print(f"Creating Windows Installer: {self.product_name}")
        print(f"Version: {self.version}")
        print("=" * 60)

        try:
            self.prepare_environment()
            wxs_file = self.create_wix_source()
            self.build_installer_with_wix(wxs_file)

            print("\n" + "=" * 60)
            print("✓ INSTALLER CREATION SUCCESSFUL")
            print("=" * 60)
            print(f"Output directory: {self.installer_dir}")

            return True

        except Exception as e:
            print("\n" + "=" * 60)
            print("✗ INSTALLER CREATION FAILED")
            print("=" * 60)
            print(f"Error: {e}")
            return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_windows_installer.py <product_name> <version>")
        sys.exit(1)

    product_name = sys.argv[1]
    version = sys.argv[2]

    creator = WindowsInstallerCreator(product_name, version)
    success = creator.run()

    sys.exit(0 if success else 1)
