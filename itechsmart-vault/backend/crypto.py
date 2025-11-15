"""
iTechSmart Vault - Cryptography Module
Handles encryption, decryption, and key management
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
import secrets


class CryptoService:
    """
    Cryptography service for encrypting and decrypting secrets
    """
    
    def __init__(self, master_key: bytes = None):
        """
        Initialize crypto service with master key
        """
        if master_key is None:
            # Generate or load master key from environment
            master_key_str = os.getenv("VAULT_MASTER_KEY")
            if master_key_str:
                self.master_key = base64.urlsafe_b64decode(master_key_str)
            else:
                # Generate new master key (should be stored securely)
                self.master_key = Fernet.generate_key()
        else:
            self.master_key = master_key
        
        self.fernet = Fernet(self.master_key)
    
    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypt plaintext string
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Encrypted bytes
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        return self.fernet.encrypt(plaintext)
    
    def decrypt(self, ciphertext: bytes) -> str:
        """
        Decrypt ciphertext
        
        Args:
            ciphertext: Encrypted bytes
            
        Returns:
            Decrypted string
        """
        decrypted = self.fernet.decrypt(ciphertext)
        return decrypted.decode('utf-8')
    
    def generate_key(self) -> str:
        """
        Generate a new encryption key
        
        Returns:
            Base64 encoded key
        """
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode('utf-8')
    
    def derive_key(self, password: str, salt: bytes = None) -> tuple:
        """
        Derive encryption key from password
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generated if not provided)
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def generate_token(self, length: int = 32) -> str:
        """
        Generate a secure random token
        
        Args:
            length: Length of token in bytes
            
        Returns:
            URL-safe token string
        """
        return secrets.token_urlsafe(length)
    
    def hash_api_key(self, api_key: str) -> str:
        """
        Hash API key for storage
        
        Args:
            api_key: API key to hash
            
        Returns:
            Hashed API key
        """
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(api_key.encode())
        return base64.b64encode(digest.finalize()).decode('utf-8')
    
    def generate_api_key(self) -> tuple:
        """
        Generate a new API key
        
        Returns:
            Tuple of (api_key, key_hash, key_prefix)
        """
        api_key = f"vault_{self.generate_token(32)}"
        key_hash = self.hash_api_key(api_key)
        key_prefix = api_key[:12]  # First 12 chars for identification
        return api_key, key_hash, key_prefix


# Global crypto service instance
crypto_service = CryptoService()