"""
macOS DMG Creator
Creates professional DMG installers for iTechSmart products
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class MacDMGCreator:
    """Create macOS DMG installer"""
    
    def __init__(self, product_name: str, version: str):
        self.product_name = product_name
        self.version = version
        self.workspace = Path.cwd()
        self.dist_dir = self.workspace / "dist" / "macos" / product_name
        self.installer_dir = self.workspace / "installers" / "macos" / product_name
        self.app_name = self.get_app_name()
        
    def get_app_name(self) -> str:
        """Get formatted app name"""
        return self.product_name.replace("-", " ").title().replace(" ", "")
    
    def prepare_environment(self):
        """Prepare installer build environment"""
        print(f"Preparing DMG environment for {self.product_name}...")
        self.installer_dir.mkdir(parents=True, exist_ok=True)
    
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
            "company": "iTechSmart"
        }
    
    def create_dmg_template(self):
        """Create DMG template directory"""
        print("Creating DMG template...")
        
        template_dir = self.installer_dir / "dmg_template"
        if template_dir.exists():
            shutil.rmtree(template_dir)
        template_dir.mkdir(parents=True)
        
        # Copy application
        app_path = self.dist_dir / f"{self.app_name}.app"
        if not app_path.exists():
            raise FileNotFoundError(f"Application not found: {app_path}")
        
        shutil.copytree(app_path, template_dir / f"{self.app_name}.app")
        
        # Create Applications symlink
        applications_link = template_dir / "Applications"
        if not applications_link.exists():
            os.symlink("/Applications", applications_link)
        
        # Create README
        self.create_readme(template_dir)
        
        # Create .DS_Store for custom view (if available)
        self.create_ds_store(template_dir)
        
        print(f"✓ DMG template created: {template_dir}")
        return template_dir
    
    def create_readme(self, template_dir: Path):
        """Create README file for DMG"""
        metadata = self.get_product_metadata()
        
        readme_content = f"""
{metadata['name']} v{self.version}
{'=' * 60}

Installation Instructions:
1. Drag the {self.app_name}.app to the Applications folder
2. Launch from Applications or Spotlight
3. On first launch, you may need to allow the app in System Preferences > Security & Privacy

For support and documentation, visit:
https://itechsmart.com/support

{metadata['description']}

© 2025 {metadata['company']}. All rights reserved.
"""
        
        readme_file = template_dir / "README.txt"
        readme_file.write_text(readme_content)
        print(f"✓ README created")
    
    def create_ds_store(self, template_dir: Path):
        """Create .DS_Store for custom DMG appearance"""
        # This would require py-applescript or similar
        # For now, we'll skip custom appearance
        print("⚠ Custom DMG appearance skipped (requires additional tools)")
    
    def create_dmg(self, template_dir: Path):
        """Create the DMG file"""
        print("Creating DMG file...")
        
        metadata = self.get_product_metadata()
        dmg_name = f"{self.product_name}-{self.version}.dmg"
        dmg_path = self.installer_dir / dmg_name
        
        # Remove existing DMG
        if dmg_path.exists():
            dmg_path.unlink()
        
        try:
            # Create DMG using hdiutil
            subprocess.run([
                'hdiutil', 'create',
                '-volname', metadata['name'],
                '-srcfolder', str(template_dir),
                '-ov',
                '-format', 'UDZO',
                '-imagekey', 'zlib-level=9',
                str(dmg_path)
            ], check=True, capture_output=True)
            
            print(f"✓ DMG created: {dmg_path}")
            
            # Get DMG size
            size_mb = dmg_path.stat().st_size / (1024 * 1024)
            print(f"  Size: {size_mb:.2f} MB")
            
            return dmg_path
            
        except subprocess.CalledProcessError as e:
            print(f"✗ DMG creation failed: {e}")
            print(f"  stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
            raise
    
    def sign_dmg(self, dmg_path: Path):
        """Sign the DMG (if certificate available)"""
        print("⚠ DMG signing skipped (no certificate configured)")
    
    def notarize_dmg(self, dmg_path: Path):
        """Notarize the DMG with Apple (if credentials available)"""
        print("⚠ DMG notarization skipped (no credentials configured)")
    
    def create_checksum(self, dmg_path: Path):
        """Create SHA256 checksum file"""
        print("Creating checksum...")
        
        import hashlib
        
        sha256_hash = hashlib.sha256()
        with open(dmg_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        checksum = sha256_hash.hexdigest()
        checksum_file = dmg_path.with_suffix('.dmg.sha256')
        checksum_file.write_text(f"{checksum}  {dmg_path.name}\n")
        
        print(f"✓ Checksum created: {checksum_file}")
        print(f"  SHA256: {checksum}")
    
    def run(self):
        """Run the complete DMG creation process"""
        print("=" * 60)
        print(f"Creating macOS DMG: {self.product_name}")
        print(f"Version: {self.version}")
        print("=" * 60)
        
        try:
            self.prepare_environment()
            template_dir = self.create_dmg_template()
            dmg_path = self.create_dmg(template_dir)
            self.sign_dmg(dmg_path)
            self.notarize_dmg(dmg_path)
            self.create_checksum(dmg_path)
            
            # Cleanup template
            shutil.rmtree(template_dir)
            
            print("\n" + "=" * 60)
            print("✓ DMG CREATION SUCCESSFUL")
            print("=" * 60)
            print(f"Output: {dmg_path}")
            
            return True
            
        except Exception as e:
            print("\n" + "=" * 60)
            print("✗ DMG CREATION FAILED")
            print("=" * 60)
            print(f"Error: {e}")
            return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_macos_dmg.py <product_name> <version>")
        sys.exit(1)
    
    product_name = sys.argv[1]
    version = sys.argv[2]
    
    creator = MacDMGCreator(product_name, version)
    success = creator.run()
    
    sys.exit(0 if success else 1)