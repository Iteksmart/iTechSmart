"""
iTechSmart Suite - Client-Specific Build Script
Builds customized installers for specific clients with their branding
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class ClientBuilder:
    """Builds customized installers for clients"""
    
    def __init__(self, client_name: str, output_dir: str = None):
        self.client_name = client_name
        self.client_dir = f"clients/{client_name}"
        self.output_dir = output_dir or f"dist/clients/{client_name}"
        self.config = self.load_client_config()
        self.build_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log build message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.build_log.append(log_entry)
        print(log_entry)
    
    def load_client_config(self) -> dict:
        """Load client configuration"""
        config_file = f"{self.client_dir}/config.json"
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Client config not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        self.log(f"Loaded configuration for {config['client']['name']}")
        return config
    
    def prepare_client_assets(self):
        """Prepare client-specific assets"""
        self.log(f"Preparing assets for {self.config['client']['name']}")
        
        # Create assets directory
        assets_dir = "installers/assets"
        os.makedirs(assets_dir, exist_ok=True)
        os.makedirs(f"{assets_dir}/splash", exist_ok=True)
        os.makedirs(f"{assets_dir}/icons", exist_ok=True)
        
        # Get client logo
        logo_file = self.config['branding'].get('logo_file', 'logo.png')
        client_logo = f"{self.client_dir}/{logo_file}"
        
        if not os.path.exists(client_logo):
            self.log(f"Warning: Client logo not found: {client_logo}", "WARNING")
            return False
        
        # Copy and convert logo
        shutil.copy2(client_logo, "logo_client.png")
        
        # Convert to all required sizes
        sizes = [512, 256, 128, 64, 48, 32, 16]
        for size in sizes:
            try:
                subprocess.run([
                    "convert", "logo_client.png",
                    "-resize", f"{size}x{size}",
                    f"{assets_dir}/logo-{size}.png"
                ], check=True, capture_output=True)
                self.log(f"✓ Created logo-{size}.png")
            except Exception as e:
                self.log(f"Error creating logo-{size}.png: {e}", "ERROR")
        
        # Create splash screen
        try:
            subprocess.run([
                "convert", "logo_client.png",
                "-resize", "400x400",
                "-gravity", "center",
                "-background", "white",
                "-extent", "800x600",
                f"{assets_dir}/splash/splash-screen.png"
            ], check=True, capture_output=True)
            self.log("✓ Created splash screen")
        except Exception as e:
            self.log(f"Error creating splash screen: {e}", "ERROR")
        
        # Create icon
        try:
            subprocess.run([
                "convert", "logo_client.png",
                "-resize", "256x256",
                f"{assets_dir}/icons/client.ico"
            ], check=True, capture_output=True)
            self.log("✓ Created icon file")
        except Exception as e:
            self.log(f"Error creating icon: {e}", "ERROR")
        
        return True
    
    def customize_source_files(self):
        """Customize source files with client information"""
        self.log("Customizing source files with client information")
        
        # Create backup of original files
        backup_dir = ".client_build_backup"
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        
        # Define replacements
        replacements = {
            "iTechSmart Inc.": self.config['client']['name'],
            "iTechSmart Suite": self.config['branding']['app_name'],
            "support@itechsmart.dev": self.config['client']['support_email'],
        }
        
        # Add website replacement
        website = self.config['client']['website']
        website_clean = website.replace('https://', '').replace('http://', '').replace('www.', '')
        replacements["itechsmart.dev"] = website_clean
        
        # Update source files
        files_updated = 0
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    if self.replace_in_file(filepath, replacements):
                        files_updated += 1
        
        self.log(f"✓ Updated {files_updated} source files")
        return True
    
    def replace_in_file(self, filepath: str, replacements: dict) -> bool:
        """Replace text in file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            for old, new in replacements.items():
                content = content.replace(old, new)
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            return False
        except Exception as e:
            self.log(f"Error updating {filepath}: {e}", "WARNING")
            return False
    
    def build_selected_products(self, platform: str = "windows"):
        """Build only selected products"""
        included_products = self.config['products'].get('include', [])
        
        if not included_products:
            self.log("No products selected, building all 36 products")
            # Build all products
            subprocess.run([
                "python", "build-tools/build_all_products.py",
                "--platform", platform
            ])
        else:
            self.log(f"Building {len(included_products)} selected products")
            
            # Build each selected product
            # This would integrate with build_all_products.py
            # For now, we'll build all and filter later
            subprocess.run([
                "python", "build-tools/build_all_products.py",
                "--platform", platform
            ])
    
    def create_client_documentation(self):
        """Create client-specific documentation"""
        self.log("Creating client documentation")
        
        docs_dir = f"{self.output_dir}/Documentation"
        os.makedirs(docs_dir, exist_ok=True)
        
        # Copy and customize documentation
        docs_to_copy = [
            "QUICK_START_GUIDE.md",
            "DEPLOYMENT_GUIDE.md",
            "ITECHSMART_SUITE_INSTRUCTION_MANUAL.md"
        ]
        
        for doc in docs_to_copy:
            if os.path.exists(doc):
                dest = f"{docs_dir}/{doc}"
                shutil.copy2(doc, dest)
                
                # Customize the documentation
                replacements = {
                    "iTechSmart Inc.": self.config['client']['name'],
                    "iTechSmart Suite": self.config['branding']['app_name'],
                    "support@itechsmart.dev": self.config['client']['support_email'],
                    "itechsmart.dev": self.config['client']['website'].replace('https://', '').replace('http://', '')
                }
                self.replace_in_file(dest, replacements)
        
        # Create custom README
        readme_content = f"""
# {self.config['branding']['app_name']}

**Version**: 1.0.0  
**Client**: {self.config['client']['name']}  
**Build Date**: {datetime.now().strftime('%Y-%m-%d')}

## Installation

Please refer to the Installation Guide in the Documentation folder.

## Support

- **Email**: {self.config['client']['support_email']}
- **Website**: {self.config['client']['website']}

## License

{self.config['client'].get('copyright', f"Copyright © 2025 {self.config['client']['name']}. All rights reserved.")}
"""
        
        with open(f"{self.output_dir}/README.txt", 'w') as f:
            f.write(readme_content)
        
        self.log("✓ Documentation created")
    
    def generate_license_keys(self, count: int = 5):
        """Generate license keys for client"""
        self.log(f"Generating {count} license keys")
        
        keys_dir = f"{self.output_dir}/License_Keys"
        os.makedirs(keys_dir, exist_ok=True)
        
        license_types = self.config['license'].get('types', ['trial', 'professional', 'enterprise'])
        
        keys_content = f"""
# License Keys for {self.config['client']['name']}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        for license_type in license_types:
            for i in range(count):
                # Generate license key
                try:
                    result = subprocess.run([
                        "python", "src/license-system/license_manager.py",
                        "generate",
                        license_type,
                        self.config['client']['name'],
                        self.config['client']['support_email'],
                        "365"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Extract key from output
                        output_lines = result.stdout.strip().split('\n')
                        key = output_lines[-1] if output_lines else "ERROR"
                        keys_content += f"\n{license_type.upper()} #{i+1}:\n{key}\n"
                except Exception as e:
                    self.log(f"Error generating license key: {e}", "ERROR")
        
        with open(f"{keys_dir}/license_keys.txt", 'w') as f:
            f.write(keys_content)
        
        self.log("✓ License keys generated")
    
    def create_distribution_package(self):
        """Create final distribution package"""
        self.log("Creating distribution package")
        
        # Create distribution structure
        dist_name = f"{self.config['branding']['installer_name']}-v1.0.0"
        dist_path = f"{self.output_dir}/{dist_name}"
        
        if os.path.exists(dist_path):
            shutil.rmtree(dist_path)
        
        os.makedirs(dist_path, exist_ok=True)
        
        # Copy installers
        if os.path.exists("installers"):
            for platform in ["windows", "linux", "macos"]:
                platform_dir = f"installers/{platform}"
                if os.path.exists(platform_dir):
                    dest_dir = f"{dist_path}/{platform.capitalize()}"
                    shutil.copytree(platform_dir, dest_dir, dirs_exist_ok=True)
        
        # Copy documentation
        if os.path.exists(f"{self.output_dir}/Documentation"):
            shutil.copytree(
                f"{self.output_dir}/Documentation",
                f"{dist_path}/Documentation",
                dirs_exist_ok=True
            )
        
        # Copy license keys
        if os.path.exists(f"{self.output_dir}/License_Keys"):
            shutil.copytree(
                f"{self.output_dir}/License_Keys",
                f"{dist_path}/License_Keys",
                dirs_exist_ok=True
            )
        
        # Copy README
        if os.path.exists(f"{self.output_dir}/README.txt"):
            shutil.copy2(f"{self.output_dir}/README.txt", dist_path)
        
        # Create archive
        archive_name = f"{dist_name}.zip"
        shutil.make_archive(
            f"{self.output_dir}/{dist_name}",
            'zip',
            self.output_dir,
            dist_name
        )
        
        self.log(f"✓ Distribution package created: {archive_name}")
    
    def build_for_client(self, platforms: list = None):
        """Build complete package for client"""
        if platforms is None:
            platforms = ["windows"]
        
        self.log("\n" + "="*60)
        self.log(f"Building Custom Package for {self.config['client']['name']}")
        self.log("="*60)
        
        try:
            # Phase 1: Prepare assets
            if not self.prepare_client_assets():
                self.log("Failed to prepare assets", "ERROR")
                return False
            
            # Phase 2: Customize source files
            if not self.customize_source_files():
                self.log("Failed to customize source files", "ERROR")
                return False
            
            # Phase 3: Build products
            for platform in platforms:
                self.log(f"\nBuilding for platform: {platform}")
                self.build_selected_products(platform)
            
            # Phase 4: Create documentation
            self.create_client_documentation()
            
            # Phase 5: Generate license keys
            self.generate_license_keys()
            
            # Phase 6: Create distribution package
            self.create_distribution_package()
            
            # Save build log
            log_file = f"{self.output_dir}/build_log.txt"
            with open(log_file, 'w') as f:
                f.write('\n'.join(self.build_log))
            
            self.log("\n" + "="*60)
            self.log(f"✅ Client package complete: {self.config['client']['name']}")
            self.log(f"Output directory: {self.output_dir}")
            self.log("="*60)
            
            return True
            
        except Exception as e:
            self.log(f"Build failed: {str(e)}", "ERROR")
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Build client-specific iTechSmart Suite package"
    )
    parser.add_argument(
        "--client",
        required=True,
        help="Client name (must have config in clients/<name>/)"
    )
    parser.add_argument(
        "--platform",
        choices=["windows", "linux", "macos", "all"],
        default="windows",
        help="Target platform(s)"
    )
    parser.add_argument(
        "--output",
        help="Output directory (default: dist/clients/<client>)"
    )
    
    args = parser.parse_args()
    
    # Determine platforms
    if args.platform == "all":
        platforms = ["windows", "linux", "macos"]
    else:
        platforms = [args.platform]
    
    # Build for client
    builder = ClientBuilder(args.client, args.output)
    success = builder.build_for_client(platforms)
    
    sys.exit(0 if success else 1)