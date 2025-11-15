"""
iTechSmart Suite - Auto-Update System
Handles automatic updates, version checking, and patch management
"""

import os
import json
import hashlib
import requests
import zipfile
import shutil
from datetime import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path
import subprocess
import platform

class UpdateManager:
    """Manages automatic updates for iTechSmart Suite"""
    
    # Update server URL (replace with actual server)
    UPDATE_SERVER = "https://updates.itechsmart.dev/api/v1"
    
    # Current version
    CURRENT_VERSION = "1.0.0"
    
    def __init__(self, install_dir: str = None):
        self.install_dir = install_dir or os.getcwd()
        self.update_cache_dir = os.path.join(self.install_dir, ".updates")
        self.version_file = os.path.join(self.install_dir, "version.json")
        self.update_log = os.path.join(self.install_dir, "update.log")
        
        # Create cache directory
        os.makedirs(self.update_cache_dir, exist_ok=True)
    
    def get_current_version(self) -> str:
        """Get current installed version"""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    return data.get("version", self.CURRENT_VERSION)
            except:
                pass
        return self.CURRENT_VERSION
    
    def check_for_updates(self) -> Tuple[bool, Optional[Dict]]:
        """
        Check if updates are available
        Returns: (has_update, update_info)
        """
        try:
            current_version = self.get_current_version()
            
            # Request update information from server
            response = requests.get(
                f"{self.UPDATE_SERVER}/check",
                params={
                    "current_version": current_version,
                    "platform": platform.system(),
                    "arch": platform.machine()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                update_info = response.json()
                
                if update_info.get("has_update"):
                    return True, update_info
                else:
                    return False, None
            else:
                self._log(f"Update check failed: HTTP {response.status_code}")
                return False, None
                
        except Exception as e:
            self._log(f"Error checking for updates: {str(e)}")
            return False, None
    
    def download_update(self, update_info: Dict) -> Tuple[bool, str]:
        """
        Download update package
        Returns: (success, file_path)
        """
        try:
            download_url = update_info.get("download_url")
            version = update_info.get("version")
            checksum = update_info.get("checksum")
            
            if not download_url:
                return False, "No download URL provided"
            
            # Download file
            self._log(f"Downloading update {version}...")
            
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Save to cache
            update_file = os.path.join(
                self.update_cache_dir,
                f"update_{version}.zip"
            )
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress callback could be added here
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self._log(f"Download progress: {progress:.1f}%")
            
            # Verify checksum
            if checksum:
                file_checksum = self._calculate_checksum(update_file)
                if file_checksum != checksum:
                    os.remove(update_file)
                    return False, "Checksum verification failed"
            
            self._log(f"Update downloaded successfully: {update_file}")
            return True, update_file
            
        except Exception as e:
            self._log(f"Error downloading update: {str(e)}")
            return False, str(e)
    
    def install_update(self, update_file: str, update_info: Dict) -> Tuple[bool, str]:
        """
        Install downloaded update
        Returns: (success, message)
        """
        try:
            self._log(f"Installing update from {update_file}...")
            
            # Create backup
            backup_dir = os.path.join(self.update_cache_dir, "backup")
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            self._log("Creating backup...")
            self._create_backup(backup_dir)
            
            # Extract update
            self._log("Extracting update files...")
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(self.install_dir)
            
            # Run post-install script if exists
            post_install_script = os.path.join(self.install_dir, "post_install.py")
            if os.path.exists(post_install_script):
                self._log("Running post-install script...")
                subprocess.run([
                    "python",
                    post_install_script
                ], check=True)
            
            # Update version file
            self._update_version_file(update_info)
            
            self._log(f"Update installed successfully: {update_info.get('version')}")
            return True, "Update installed successfully"
            
        except Exception as e:
            self._log(f"Error installing update: {str(e)}")
            
            # Restore backup
            self._log("Restoring backup...")
            self._restore_backup(backup_dir)
            
            return False, f"Update failed: {str(e)}"
    
    def rollback_update(self) -> Tuple[bool, str]:
        """Rollback to previous version"""
        try:
            backup_dir = os.path.join(self.update_cache_dir, "backup")
            
            if not os.path.exists(backup_dir):
                return False, "No backup found"
            
            self._log("Rolling back to previous version...")
            self._restore_backup(backup_dir)
            
            self._log("Rollback completed successfully")
            return True, "Rollback completed successfully"
            
        except Exception as e:
            self._log(f"Error during rollback: {str(e)}")
            return False, f"Rollback failed: {str(e)}"
    
    def auto_update(self, force: bool = False) -> Tuple[bool, str]:
        """
        Perform automatic update check and installation
        Returns: (success, message)
        """
        try:
            # Check for updates
            self._log("Checking for updates...")
            has_update, update_info = self.check_for_updates()
            
            if not has_update:
                return True, "No updates available"
            
            # Check if update is critical
            is_critical = update_info.get("critical", False)
            
            if not force and not is_critical:
                return True, f"Update available: {update_info.get('version')} (not critical)"
            
            # Download update
            success, result = self.download_update(update_info)
            if not success:
                return False, f"Download failed: {result}"
            
            update_file = result
            
            # Install update
            success, message = self.install_update(update_file, update_info)
            
            # Clean up
            if os.path.exists(update_file):
                os.remove(update_file)
            
            return success, message
            
        except Exception as e:
            self._log(f"Auto-update error: {str(e)}")
            return False, f"Auto-update failed: {str(e)}"
    
    def get_update_history(self) -> list:
        """Get update history"""
        history = []
        
        if os.path.exists(self.update_log):
            try:
                with open(self.update_log, 'r') as f:
                    for line in f:
                        if line.strip():
                            history.append(line.strip())
            except:
                pass
        
        return history
    
    def _create_backup(self, backup_dir: str):
        """Create backup of current installation"""
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup critical files
        critical_files = [
            "version.json",
            "config.json",
            "license.dat"
        ]
        
        for file in critical_files:
            src = os.path.join(self.install_dir, file)
            if os.path.exists(src):
                dst = os.path.join(backup_dir, file)
                shutil.copy2(src, dst)
    
    def _restore_backup(self, backup_dir: str):
        """Restore from backup"""
        if not os.path.exists(backup_dir):
            raise Exception("Backup directory not found")
        
        for file in os.listdir(backup_dir):
            src = os.path.join(backup_dir, file)
            dst = os.path.join(self.install_dir, file)
            shutil.copy2(src, dst)
    
    def _update_version_file(self, update_info: Dict):
        """Update version file with new version info"""
        version_data = {
            "version": update_info.get("version"),
            "updated_at": datetime.now().isoformat(),
            "previous_version": self.get_current_version(),
            "update_info": update_info
        }
        
        with open(self.version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _log(self, message: str):
        """Log message to update log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        print(log_message)
        
        with open(self.update_log, 'a') as f:
            f.write(log_message + "\n")


# CLI interface for update management
if __name__ == "__main__":
    import sys
    
    manager = UpdateManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_manager.py check")
        print("  python update_manager.py update [--force]")
        print("  python update_manager.py rollback")
        print("  python update_manager.py version")
        print("  python update_manager.py history")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        has_update, update_info = manager.check_for_updates()
        if has_update:
            print(f"Update available: {update_info.get('version')}")
            print(f"Release notes: {update_info.get('release_notes')}")
        else:
            print("No updates available")
    
    elif command == "update":
        force = "--force" in sys.argv
        success, message = manager.auto_update(force=force)
        print(message)
        sys.exit(0 if success else 1)
    
    elif command == "rollback":
        success, message = manager.rollback_update()
        print(message)
        sys.exit(0 if success else 1)
    
    elif command == "version":
        version = manager.get_current_version()
        print(f"Current version: {version}")
    
    elif command == "history":
        history = manager.get_update_history()
        print("Update History:")
        for entry in history:
            print(f"  {entry}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)