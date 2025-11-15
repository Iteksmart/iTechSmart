"""
Secure credential management with encryption
"""

import logging
from typing import Dict, Optional, List
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

from ..core.models import HostCredentials, Platform


class CredentialManager:
    """Manage and encrypt host credentials"""
    
    def __init__(self, master_password: str, storage_path: str = "credentials.enc"):
        self.logger = logging.getLogger(__name__)
        self.storage_path = storage_path
        self.credentials_cache: Dict[str, HostCredentials] = {}
        
        # Derive encryption key from master password
        self.cipher = self._create_cipher(master_password)
        
        # Load existing credentials
        self.load_credentials()
    
    def _create_cipher(self, password: str) -> Fernet:
        """Create Fernet cipher from password"""
        # Use PBKDF2 to derive key from password
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'itechsmart_supreme_salt',  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def add_credentials(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        private_key: Optional[str] = None,
        port: int = 22,
        platform: Platform = Platform.LINUX,
        domain: Optional[str] = None,
        use_sudo: bool = False
    ) -> HostCredentials:
        """Add credentials for a host"""
        
        credentials = HostCredentials(
            host=host,
            username=username,
            password=password,
            private_key=private_key,
            port=port,
            platform=platform,
            domain=domain,
            use_sudo=use_sudo
        )
        
        self.credentials_cache[host] = credentials
        self.save_credentials()
        
        self.logger.info(f"Added credentials for host: {host}")
        
        return credentials
    
    def get_credentials(self, host: str) -> Optional[HostCredentials]:
        """Get credentials for a host"""
        return self.credentials_cache.get(host)
    
    def remove_credentials(self, host: str) -> bool:
        """Remove credentials for a host"""
        if host in self.credentials_cache:
            del self.credentials_cache[host]
            self.save_credentials()
            self.logger.info(f"Removed credentials for host: {host}")
            return True
        return False
    
    def list_hosts(self) -> List[str]:
        """List all hosts with stored credentials"""
        return list(self.credentials_cache.keys())
    
    def save_credentials(self):
        """Save credentials to encrypted file"""
        try:
            # Convert credentials to dict
            data = {}
            for host, creds in self.credentials_cache.items():
                data[host] = {
                    'host': creds.host,
                    'username': creds.username,
                    'password': creds.password,
                    'private_key': creds.private_key,
                    'port': creds.port,
                    'platform': creds.platform.value,
                    'domain': creds.domain,
                    'use_sudo': creds.use_sudo
                }
            
            # Encrypt and save
            json_data = json.dumps(data)
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            with open(self.storage_path, 'wb') as f:
                f.write(encrypted_data)
            
            self.logger.debug("Credentials saved successfully")
        
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
    
    def load_credentials(self):
        """Load credentials from encrypted file"""
        if not os.path.exists(self.storage_path):
            self.logger.info("No existing credentials file found")
            return
        
        try:
            # Read and decrypt
            with open(self.storage_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())
            
            # Convert to HostCredentials objects
            for host, creds_dict in data.items():
                self.credentials_cache[host] = HostCredentials(
                    host=creds_dict['host'],
                    username=creds_dict['username'],
                    password=creds_dict.get('password'),
                    private_key=creds_dict.get('private_key'),
                    port=creds_dict.get('port', 22),
                    platform=Platform(creds_dict.get('platform', 'linux')),
                    domain=creds_dict.get('domain'),
                    use_sudo=creds_dict.get('use_sudo', False)
                )
            
            self.logger.info(f"Loaded credentials for {len(self.credentials_cache)} hosts")
        
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
    
    def update_credentials(
        self,
        host: str,
        **kwargs
    ) -> Optional[HostCredentials]:
        """Update credentials for a host"""
        
        if host not in self.credentials_cache:
            self.logger.warning(f"No credentials found for host: {host}")
            return None
        
        creds = self.credentials_cache[host]
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(creds, key):
                setattr(creds, key, value)
        
        self.save_credentials()
        self.logger.info(f"Updated credentials for host: {host}")
        
        return creds


class VaultIntegration:
    """Integration with HashiCorp Vault or similar secret managers"""
    
    def __init__(self, vault_url: str, vault_token: str):
        self.vault_url = vault_url
        self.vault_token = vault_token
        self.logger = logging.getLogger(__name__)
    
    async def get_credentials(self, path: str) -> Dict[str, str]:
        """Get credentials from Vault"""
        # Implementation for Vault integration
        # This is a placeholder - implement based on your Vault setup
        pass
    
    async def store_credentials(self, path: str, credentials: Dict[str, str]):
        """Store credentials in Vault"""
        # Implementation for Vault integration
        pass