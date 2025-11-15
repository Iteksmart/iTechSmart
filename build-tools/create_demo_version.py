"""
Demo Version Creator
Creates demo/trial versions with feature restrictions
"""

import os
import sys
import shutil
import json
from pathlib import Path

class DemoVersionCreator:
    """Create demo versions with restrictions"""
    
    def __init__(self, product_name: str, platform: str, version: str):
        self.product_name = product_name
        self.platform = platform
        self.version = version
        self.workspace = Path.cwd()
        self.source_dir = self.workspace / "dist" / platform / product_name
        self.demo_dir = self.workspace / "dist" / "demo" / platform / product_name
        
    def prepare_environment(self):
        """Prepare demo build environment"""
        print(f"Preparing demo environment for {self.product_name} ({self.platform})...")
        self.demo_dir.mkdir(parents=True, exist_ok=True)
    
    def copy_base_files(self):
        """Copy base files from full version"""
        print("Copying base files...")
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")
        
        # Copy all files
        for item in self.source_dir.iterdir():
            dest = self.demo_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        
        print(f"✓ Files copied to: {self.demo_dir}")
    
    def create_demo_config(self):
        """Create demo configuration file"""
        print("Creating demo configuration...")
        
        demo_config = {
            "demo_mode": True,
            "trial_days": 30,
            "restrictions": {
                "max_users": 5,
                "max_projects": 10,
                "api_calls_per_day": 1000,
                "storage_gb": 10,
                "advanced_features": False,
                "export_enabled": False,
                "collaboration_enabled": False
            },
            "watermark": {
                "enabled": True,
                "text": "DEMO VERSION"
            },
            "nag_screen": {
                "enabled": True,
                "frequency": "daily",
                "message": "This is a demo version. Purchase a license to unlock all features."
            }
        }
        
        config_file = self.demo_dir / "demo_config.json"
        with open(config_file, 'w') as f:
            json.dump(demo_config, f, indent=2)
        
        print(f"✓ Demo config created: {config_file}")
    
    def inject_demo_license(self):
        """Inject demo license"""
        print("Injecting demo license...")
        
        # Import license manager
        sys.path.insert(0, str(self.workspace / "src" / "license-system"))
        try:
            from license_manager import LicenseManager
            
            manager = LicenseManager(str(self.demo_dir / "license.dat"))
            success, key, message = manager.create_trial_license()
            
            if success:
                print(f"✓ Demo license created: {message}")
            else:
                print(f"⚠ Demo license creation failed: {message}")
                
        except ImportError:
            print("⚠ License manager not available, skipping license injection")
    
    def rename_executables(self):
        """Rename executables to indicate demo version"""
        print("Renaming executables...")
        
        if self.platform == "windows":
            exe_file = self.demo_dir / f"{self.product_name}.exe"
            if exe_file.exists():
                demo_exe = self.demo_dir / f"{self.product_name}-demo.exe"
                exe_file.rename(demo_exe)
                print(f"✓ Renamed to: {demo_exe.name}")
        
        elif self.platform == "macos":
            app_dir = self.demo_dir / f"{self.product_name}.app"
            if app_dir.exists():
                demo_app = self.demo_dir / f"{self.product_name}-demo.app"
                app_dir.rename(demo_app)
                print(f"✓ Renamed to: {demo_app.name}")
        
        elif self.platform == "linux":
            binary_file = self.demo_dir / self.product_name
            if binary_file.exists():
                demo_binary = self.demo_dir / f"{self.product_name}-demo"
                binary_file.rename(demo_binary)
                print(f"✓ Renamed to: {demo_binary.name}")
    
    def create_readme(self):
        """Create demo README"""
        print("Creating demo README...")
        
        readme_content = f"""
{self.product_name.replace('-', ' ').title()} - DEMO VERSION
{'=' * 60}

This is a demo/trial version with the following restrictions:

LIMITATIONS:
- 30-day trial period
- Maximum 5 users
- Maximum 10 projects
- 1,000 API calls per day
- 10 GB storage limit
- Advanced features disabled
- Export functionality limited
- Collaboration features disabled
- Demo watermark on outputs

FULL VERSION BENEFITS:
- Unlimited trial period
- Unlimited users
- Unlimited projects
- Unlimited API calls
- Unlimited storage
- All advanced features
- Full export capabilities
- Complete collaboration tools
- No watermarks

To purchase a full license, visit:
https://itechsmart.com/pricing

For support:
https://itechsmart.com/support

© 2025 iTechSmart. All rights reserved.
"""
        
        readme_file = self.demo_dir / "README-DEMO.txt"
        readme_file.write_text(readme_content)
        print(f"✓ Demo README created: {readme_file}")
    
    def create_version_info(self):
        """Create version information file"""
        version_info = {
            "product": self.product_name,
            "version": f"{self.version}-demo",
            "type": "demo",
            "platform": self.platform,
            "restrictions": {
                "trial_days": 30,
                "max_users": 5,
                "max_projects": 10
            }
        }
        
        version_file = self.demo_dir / "version.json"
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
        
        print(f"✓ Version info created: {version_file}")
    
    def create_archive(self):
        """Create compressed archive of demo version"""
        print("Creating demo archive...")
        
        archive_name = f"{self.product_name}-{self.version}-demo-{self.platform}"
        archive_path = self.demo_dir.parent / archive_name
        
        # Create zip archive
        shutil.make_archive(
            str(archive_path),
            'zip',
            self.demo_dir
        )
        
        print(f"✓ Demo archive created: {archive_path}.zip")
    
    def run(self):
        """Run the complete demo creation process"""
        print("=" * 60)
        print(f"Creating Demo Version: {self.product_name}")
        print(f"Platform: {self.platform}")
        print(f"Version: {self.version}")
        print("=" * 60)
        
        try:
            self.prepare_environment()
            self.copy_base_files()
            self.create_demo_config()
            self.inject_demo_license()
            self.rename_executables()
            self.create_readme()
            self.create_version_info()
            self.create_archive()
            
            print("\n" + "=" * 60)
            print("✓ DEMO VERSION CREATION SUCCESSFUL")
            print("=" * 60)
            print(f"Output directory: {self.demo_dir}")
            
            return True
            
        except Exception as e:
            print("\n" + "=" * 60)
            print("✗ DEMO VERSION CREATION FAILED")
            print("=" * 60)
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_demo_version.py <product_name> <platform> <version>")
        sys.exit(1)
    
    product_name = sys.argv[1]
    platform = sys.argv[2]
    version = sys.argv[3]
    
    creator = DemoVersionCreator(product_name, platform, version)
    success = creator.run()
    
    sys.exit(0 if success else 1)