"""
Suite Installer Creator
Creates a unified installer for the complete iTechSmart Suite
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import List, Dict

class SuiteInstallerCreator:
    """Create unified suite installer"""
    
    def __init__(self, platform: str, version: str):
        self.platform = platform
        self.version = version
        self.workspace = Path.cwd()
        self.dist_dir = self.workspace / "dist" / platform
        self.suite_dir = self.workspace / "dist" / "suite" / platform
        self.products = self.discover_products()
        
    def discover_products(self) -> List[str]:
        """Discover all available products"""
        print("Discovering products...")
        
        products = []
        if self.dist_dir.exists():
            for item in self.dist_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    products.append(item.name)
        
        print(f"✓ Found {len(products)} products")
        return sorted(products)
    
    def prepare_environment(self):
        """Prepare suite installer environment"""
        print("Preparing suite installer environment...")
        self.suite_dir.mkdir(parents=True, exist_ok=True)
    
    def create_installer_structure(self):
        """Create installer directory structure"""
        print("Creating installer structure...")
        
        dirs = [
            self.suite_dir / "products",
            self.suite_dir / "installer",
            self.suite_dir / "resources",
            self.suite_dir / "config"
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def copy_products(self):
        """Copy all products to suite directory"""
        print("Copying products...")
        
        for product in self.products:
            src = self.dist_dir / product
            dst = self.suite_dir / "products" / product
            
            if src.exists():
                print(f"  Copying {product}...")
                shutil.copytree(src, dst, dirs_exist_ok=True)
        
        print(f"✓ Copied {len(self.products)} products")
    
    def create_product_manifest(self):
        """Create product manifest"""
        print("Creating product manifest...")
        
        manifest = {
            "suite_name": "iTechSmart Suite",
            "version": self.version,
            "platform": self.platform,
            "products": []
        }
        
        for product in self.products:
            product_info = self.get_product_info(product)
            manifest["products"].append(product_info)
        
        manifest_file = self.suite_dir / "config" / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✓ Manifest created: {manifest_file}")
    
    def get_product_info(self, product: str) -> Dict:
        """Get product information"""
        metadata_file = self.workspace / product / "metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        
        return {
            "id": product,
            "name": product.replace("-", " ").title(),
            "description": f"{product} - iTechSmart Suite",
            "version": self.version,
            "category": self.categorize_product(product)
        }
    
    def categorize_product(self, product: str) -> str:
        """Categorize product by name"""
        if "ai" in product.lower():
            return "AI & Machine Learning"
        elif "analytics" in product.lower():
            return "Analytics & Insights"
        elif "security" in product.lower() or "shield" in product.lower():
            return "Security & Compliance"
        elif "cloud" in product.lower():
            return "Cloud & Infrastructure"
        elif "data" in product.lower():
            return "Data Management"
        else:
            return "General Tools"
    
    def create_installer_script(self):
        """Create installer script"""
        print("Creating installer script...")
        
        if self.platform == "windows":
            self.create_windows_installer_script()
        elif self.platform == "macos":
            self.create_macos_installer_script()
        elif self.platform == "linux":
            self.create_linux_installer_script()
    
    def create_windows_installer_script(self):
        """Create Windows installer script"""
        script_content = f"""@echo off
REM iTechSmart Suite Installer
REM Version {self.version}

echo.
echo ========================================
echo  iTechSmart Suite Installer
echo  Version {self.version}
echo ========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This installer requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

REM Set installation directory
set "INSTALL_DIR=%ProgramFiles%\\iTechSmart Suite"

echo Installation directory: %INSTALL_DIR%
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy products
echo Installing products...
xcopy /E /I /Y "products" "%INSTALL_DIR%\\products"

REM Create shortcuts
echo Creating shortcuts...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\iTechSmart Suite.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\launcher.exe'; $Shortcut.Save()"

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo iTechSmart Suite has been installed to:
echo %INSTALL_DIR%
echo.
echo You can launch it from the Start Menu.
echo.

pause
"""
        
        script_file = self.suite_dir / "install.bat"
        script_file.write_text(script_content)
        print(f"✓ Windows installer script created")
    
    def create_macos_installer_script(self):
        """Create macOS installer script"""
        script_content = f"""#!/bin/bash
# iTechSmart Suite Installer
# Version {self.version}

echo ""
echo "========================================"
echo " iTechSmart Suite Installer"
echo " Version {self.version}"
echo "========================================"
echo ""

# Set installation directory
INSTALL_DIR="/Applications/iTechSmart Suite"

echo "Installation directory: $INSTALL_DIR"
echo ""

# Check for sudo privileges
if [ "$EUID" -ne 0 ]; then
    echo "This installer requires administrator privileges."
    echo "Please run with sudo."
    exit 1
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy products
echo "Installing products..."
cp -R products/* "$INSTALL_DIR/"

# Set permissions
chmod -R 755 "$INSTALL_DIR"

echo ""
echo "========================================"
echo " Installation Complete!"
echo "========================================"
echo ""
echo "iTechSmart Suite has been installed to:"
echo "$INSTALL_DIR"
echo ""
echo "You can launch it from Applications."
echo ""
"""
        
        script_file = self.suite_dir / "install.sh"
        script_file.write_text(script_content)
        os.chmod(script_file, 0o755)
        print(f"✓ macOS installer script created")
    
    def create_linux_installer_script(self):
        """Create Linux installer script"""
        script_content = f"""#!/bin/bash
# iTechSmart Suite Installer
# Version {self.version}

echo ""
echo "========================================"
echo " iTechSmart Suite Installer"
echo " Version {self.version}"
echo "========================================"
echo ""

# Set installation directory
INSTALL_DIR="/opt/itechsmart-suite"

echo "Installation directory: $INSTALL_DIR"
echo ""

# Check for sudo privileges
if [ "$EUID" -ne 0 ]; then
    echo "This installer requires root privileges."
    echo "Please run with sudo."
    exit 1
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy products
echo "Installing products..."
cp -R products/* "$INSTALL_DIR/"

# Create symlinks in /usr/local/bin
echo "Creating symlinks..."
for product in "$INSTALL_DIR"/*; do
    if [ -d "$product" ]; then
        product_name=$(basename "$product")
        if [ -f "$product/$product_name" ]; then
            ln -sf "$product/$product_name" "/usr/local/bin/$product_name"
        fi
    fi
done

# Set permissions
chmod -R 755 "$INSTALL_DIR"

# Create desktop entries
echo "Creating desktop entries..."
mkdir -p /usr/share/applications
for desktop in "$INSTALL_DIR"/*/*.desktop; do
    if [ -f "$desktop" ]; then
        cp "$desktop" /usr/share/applications/
    fi
done

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications
fi

echo ""
echo "========================================"
echo " Installation Complete!"
echo "========================================"
echo ""
echo "iTechSmart Suite has been installed to:"
echo "$INSTALL_DIR"
echo ""
echo "You can launch products from your application menu"
echo "or by running their names in the terminal."
echo ""
"""
        
        script_file = self.suite_dir / "install.sh"
        script_file.write_text(script_content)
        os.chmod(script_file, 0o755)
        print(f"✓ Linux installer script created")
    
    def create_readme(self):
        """Create suite README"""
        print("Creating README...")
        
        readme_content = f"""
iTechSmart Suite v{self.version}
{'=' * 60}

COMPLETE PRODUCT SUITE

This package contains the complete iTechSmart Suite with all products:

INCLUDED PRODUCTS:
"""
        
        for product in self.products:
            product_info = self.get_product_info(product)
            readme_content += f"\n- {product_info['name']}"
            readme_content += f"\n  {product_info['description']}\n"
        
        readme_content += f"""

INSTALLATION:

{self.get_platform_instructions()}

SYSTEM REQUIREMENTS:
- Operating System: {self.get_os_requirements()}
- RAM: 8 GB minimum, 16 GB recommended
- Disk Space: 10 GB minimum
- Internet connection for activation

LICENSE:
Each product requires a valid license key. Trial licenses are available
for 30 days. Visit https://itechsmart.com/pricing for licensing options.

SUPPORT:
- Documentation: https://itechsmart.com/docs
- Support Portal: https://itechsmart.com/support
- Email: support@itechsmart.com

© 2025 iTechSmart. All rights reserved.
"""
        
        readme_file = self.suite_dir / "README.txt"
        readme_file.write_text(readme_content)
        print(f"✓ README created: {readme_file}")
    
    def get_platform_instructions(self) -> str:
        """Get platform-specific installation instructions"""
        if self.platform == "windows":
            return """
Windows:
1. Run install.bat as Administrator
2. Follow the on-screen instructions
3. Launch from Start Menu
"""
        elif self.platform == "macos":
            return """
macOS:
1. Open Terminal
2. Run: sudo ./install.sh
3. Enter your password when prompted
4. Launch from Applications folder
"""
        elif self.platform == "linux":
            return """
Linux:
1. Open Terminal
2. Run: sudo ./install.sh
3. Enter your password when prompted
4. Launch from application menu or terminal
"""
        return ""
    
    def get_os_requirements(self) -> str:
        """Get OS requirements"""
        if self.platform == "windows":
            return "Windows 10 or later (64-bit)"
        elif self.platform == "macos":
            return "macOS 10.13 or later"
        elif self.platform == "linux":
            return "Ubuntu 20.04+, Debian 11+, or compatible"
        return "Unknown"
    
    def create_archive(self):
        """Create compressed archive"""
        print("Creating suite archive...")
        
        archive_name = f"itechsmart-suite-{self.version}-{self.platform}"
        archive_path = self.suite_dir.parent / archive_name
        
        shutil.make_archive(
            str(archive_path),
            'zip',
            self.suite_dir
        )
        
        print(f"✓ Suite archive created: {archive_path}.zip")
    
    def run(self):
        """Run the complete suite installer creation process"""
        print("=" * 60)
        print(f"Creating Suite Installer")
        print(f"Platform: {self.platform}")
        print(f"Version: {self.version}")
        print(f"Products: {len(self.products)}")
        print("=" * 60)
        
        try:
            self.prepare_environment()
            self.create_installer_structure()
            self.copy_products()
            self.create_product_manifest()
            self.create_installer_script()
            self.create_readme()
            self.create_archive()
            
            print("\n" + "=" * 60)
            print("✓ SUITE INSTALLER CREATION SUCCESSFUL")
            print("=" * 60)
            print(f"Output directory: {self.suite_dir}")
            
            return True
            
        except Exception as e:
            print("\n" + "=" * 60)
            print("✗ SUITE INSTALLER CREATION FAILED")
            print("=" * 60)
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_suite_installer.py <platform> <version>")
        sys.exit(1)
    
    platform = sys.argv[1]
    version = sys.argv[2]
    
    creator = SuiteInstallerCreator(platform, version)
    success = creator.run()
    
    sys.exit(0 if success else 1)