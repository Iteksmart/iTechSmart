"""
Auto-Update System
Handles automatic updates for iTechSmart products
"""

import os
import sys
import json
import hashlib
import requests
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

class AutoUpdater:
    """Automatic update system for iTechSmart products"""
    
    def __init__(self, product_name: str, current_version: str):
        self.product_name = product_name
        self.current_version = current_version
        self.update_server = "https://updates.itechsmart.com"
        self.update_dir = Path.home() / ".itechsmart" / "updates"
        self.update_dir.mkdir(parents=True, exist_ok=True)
        
    def check_for_updates(self) -> Tuple[bool, Optional[Dict]]:
        """Check if updates are available"""
        try:
            response = requests.get(
                f"{self.update_server}/api/updates/{self.product_name}",
                params={"current_version": self.current_version},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("update_available"):
                    return True, data.get("update_info")
                else:
                    return False, None
            else:
                return False, None
                
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return False, None
    
    def download_update(self, update_info: Dict) -> Optional[Path]:
        """Download update package"""
        try:
            download_url = update_info.get("download_url")
            version = update_info.get("version")
            checksum = update_info.get("checksum")
            
            print(f"Downloading update {version}...")
            
            # Download file
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            # Save to temp file
            update_file = self.update_dir / f"{self.product_name}-{version}.update"
            
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify checksum
            if not self.verify_checksum(update_file, checksum):
                print("Checksum verification failed!")
                update_file.unlink()
                return None
            
            print(f"Update downloaded: {update_file}")
            return update_file
            
        except Exception as e:
            print(f"Error downloading update: {e}")
            return None
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        actual_checksum = sha256_hash.hexdigest()
        return actual_checksum == expected_checksum
    
    def apply_update(self, update_file: Path) -> bool:
        """Apply the update"""
        try:
            print("Applying update...")
            
            # Extract update package
            extract_dir = self.update_dir / "extract"
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir()
            
            # Unzip update
            shutil.unpack_archive(update_file, extract_dir)
            
            # Run update script
            update_script = extract_dir / "update.py"
            if update_script.exists():
                subprocess.run([sys.executable, str(update_script)], check=True)
            else:
                # Manual update process
                self.manual_update(extract_dir)
            
            print("Update applied successfully!")
            return True
            
        except Exception as e:
            print(f"Error applying update: {e}")
            return False
    
    def manual_update(self, extract_dir: Path):
        """Manually apply update by replacing files"""
        # Get current installation directory
        install_dir = Path(sys.executable).parent
        
        # Backup current installation
        backup_dir = self.update_dir / f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copytree(install_dir, backup_dir)
        
        # Copy new files
        for item in extract_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(extract_dir)
                dest = install_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
    
    def schedule_update(self, update_file: Path):
        """Schedule update for next restart"""
        update_info = {
            "update_file": str(update_file),
            "scheduled_at": datetime.now().isoformat(),
            "product": self.product_name
        }
        
        schedule_file = self.update_dir / "scheduled_update.json"
        with open(schedule_file, 'w') as f:
            json.dump(update_info, f, indent=2)
        
        print("Update scheduled for next restart")
    
    def check_scheduled_updates(self):
        """Check and apply scheduled updates"""
        schedule_file = self.update_dir / "scheduled_update.json"
        
        if schedule_file.exists():
            try:
                with open(schedule_file) as f:
                    update_info = json.load(f)
                
                update_file = Path(update_info["update_file"])
                
                if update_file.exists():
                    print("Applying scheduled update...")
                    if self.apply_update(update_file):
                        schedule_file.unlink()
                        update_file.unlink()
                        return True
                else:
                    schedule_file.unlink()
                    
            except Exception as e:
                print(f"Error applying scheduled update: {e}")
        
        return False
    
    def auto_update(self, silent: bool = False) -> bool:
        """Perform automatic update check and installation"""
        print(f"Checking for updates for {self.product_name}...")
        
        # Check for updates
        has_update, update_info = self.check_for_updates()
        
        if not has_update:
            if not silent:
                print("No updates available")
            return False
        
        print(f"Update available: {update_info.get('version')}")
        print(f"Release notes: {update_info.get('release_notes')}")
        
        # Download update
        update_file = self.download_update(update_info)
        
        if not update_file:
            print("Failed to download update")
            return False
        
        # Apply or schedule update
        if silent:
            self.schedule_update(update_file)
        else:
            response = input("Apply update now? (y/n): ")
            if response.lower() == 'y':
                return self.apply_update(update_file)
            else:
                self.schedule_update(update_file)
        
        return True
    
    def get_update_history(self) -> list:
        """Get update history"""
        history_file = self.update_dir / "update_history.json"
        
        if history_file.exists():
            with open(history_file) as f:
                return json.load(f)
        
        return []
    
    def record_update(self, version: str, success: bool):
        """Record update in history"""
        history = self.get_update_history()
        
        history.append({
            "product": self.product_name,
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "success": success
        })
        
        history_file = self.update_dir / "update_history.json"
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python auto_updater.py <product_name> <current_version>")
        sys.exit(1)
    
    product_name = sys.argv[1]
    current_version = sys.argv[2]
    
    updater = AutoUpdater(product_name, current_version)
    
    # Check for scheduled updates first
    updater.check_scheduled_updates()
    
    # Check for new updates
    updater.auto_update()