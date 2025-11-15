"""
Encryption Manager
Handles encryption/decryption of sensitive data
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data
    Uses Fernet (symmetric encryption) for data at rest
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption manager
        
        Args:
            master_key: Master encryption key (should be from environment variable)
        """
        self.master_key = master_key or os.getenv('ENCRYPTION_KEY')
        
        if not self.master_key:
            # Generate a new key if none provided (for development only)
            logger.warning("No encryption key provided, generating new key")
            self.master_key = Fernet.generate_key().decode()
        
        # Ensure key is bytes
        if isinstance(self.master_key, str):
            self.master_key = self.master_key.encode()
        
        self.fernet = Fernet(self.master_key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data
        
        Args:
            data: Plain text string to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        try:
            if not data:
                return data
            
            encrypted = self.fernet.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted string
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
            
        Returns:
            Decrypted plain text string
        """
        try:
            if not encrypted_data:
                return encrypted_data
            
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Encrypt dictionary data
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Encrypted JSON string
        """
        try:
            json_str = json.dumps(data)
            return self.encrypt(json_str)
        except Exception as e:
            logger.error(f"Dictionary encryption error: {e}")
            raise
    
    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt encrypted dictionary
        
        Args:
            encrypted_data: Encrypted JSON string
            
        Returns:
            Decrypted dictionary
        """
        try:
            json_str = self.decrypt(encrypted_data)
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Dictionary decryption error: {e}")
            raise
    
    def encrypt_field(self, data: Dict[str, Any], field: str) -> Dict[str, Any]:
        """
        Encrypt specific field in dictionary
        
        Args:
            data: Dictionary containing field to encrypt
            field: Field name to encrypt
            
        Returns:
            Dictionary with encrypted field
        """
        if field in data and data[field]:
            data[field] = self.encrypt(str(data[field]))
        return data
    
    def decrypt_field(self, data: Dict[str, Any], field: str) -> Dict[str, Any]:
        """
        Decrypt specific field in dictionary
        
        Args:
            data: Dictionary containing encrypted field
            field: Field name to decrypt
            
        Returns:
            Dictionary with decrypted field
        """
        if field in data and data[field]:
            data[field] = self.decrypt(data[field])
        return data
    
    def encrypt_multiple_fields(self, data: Dict[str, Any], fields: list) -> Dict[str, Any]:
        """
        Encrypt multiple fields in dictionary
        
        Args:
            data: Dictionary containing fields to encrypt
            fields: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        for field in fields:
            data = self.encrypt_field(data, field)
        return data
    
    def decrypt_multiple_fields(self, data: Dict[str, Any], fields: list) -> Dict[str, Any]:
        """
        Decrypt multiple fields in dictionary
        
        Args:
            data: Dictionary containing encrypted fields
            fields: List of field names to decrypt
            
        Returns:
            Dictionary with decrypted fields
        """
        for field in fields:
            data = self.decrypt_field(data, field)
        return data
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key
        
        Returns:
            Base64 encoded encryption key
        """
        return Fernet.generate_key().decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generated if not provided)
            
        Returns:
            Tuple of (key, salt)
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
        return key.decode(), base64.b64encode(salt).decode()
    
    def mask_sensitive_data(self, data: str, visible_chars: int = 4) -> str:
        """
        Mask sensitive data (e.g., SSN, credit card)
        
        Args:
            data: Data to mask
            visible_chars: Number of characters to leave visible
            
        Returns:
            Masked string
        """
        if not data or len(data) <= visible_chars:
            return data
        
        masked_length = len(data) - visible_chars
        return '*' * masked_length + data[-visible_chars:]
    
    def hash_data(self, data: str) -> str:
        """
        Create one-way hash of data (for comparison, not encryption)
        
        Args:
            data: Data to hash
            
        Returns:
            Hashed string
        """
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()


# Sensitive fields that should be encrypted
SENSITIVE_FIELDS = [
    'ssn',
    'password',
    'api_key',
    'client_secret',
    'access_token',
    'refresh_token',
    'credit_card',
    'bank_account'
]


class PHIEncryption:
    """
    Protected Health Information (PHI) encryption utilities
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def encrypt_phi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt all PHI fields in data
        
        Args:
            data: Dictionary containing PHI
            
        Returns:
            Dictionary with encrypted PHI
        """
        phi_fields = [
            'ssn',
            'phone_home',
            'phone_work',
            'phone_mobile',
            'email',
            'address_line1',
            'address_line2'
        ]
        
        return self.encryption_manager.encrypt_multiple_fields(data, phi_fields)
    
    def decrypt_phi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt all PHI fields in data
        
        Args:
            data: Dictionary containing encrypted PHI
            
        Returns:
            Dictionary with decrypted PHI
        """
        phi_fields = [
            'ssn',
            'phone_home',
            'phone_work',
            'phone_mobile',
            'email',
            'address_line1',
            'address_line2'
        ]
        
        return self.encryption_manager.decrypt_multiple_fields(data, phi_fields)
    
    def mask_phi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask PHI fields for display
        
        Args:
            data: Dictionary containing PHI
            
        Returns:
            Dictionary with masked PHI
        """
        masked_data = data.copy()
        
        if 'ssn' in masked_data and masked_data['ssn']:
            masked_data['ssn'] = self.encryption_manager.mask_sensitive_data(
                masked_data['ssn'], visible_chars=4
            )
        
        if 'phone_home' in masked_data and masked_data['phone_home']:
            masked_data['phone_home'] = self.encryption_manager.mask_sensitive_data(
                masked_data['phone_home'], visible_chars=4
            )
        
        if 'email' in masked_data and masked_data['email']:
            # Mask email: show first 2 chars and domain
            email = masked_data['email']
            if '@' in email:
                local, domain = email.split('@')
                masked_data['email'] = f"{local[:2]}***@{domain}"
        
        return masked_data


class ConnectionConfigEncryption:
    """
    EMR connection configuration encryption
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def encrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in connection config
        
        Args:
            config: Connection configuration
            
        Returns:
            Configuration with encrypted sensitive fields
        """
        sensitive_fields = [
            'client_secret',
            'api_key',
            'password',
            'access_token',
            'refresh_token'
        ]
        
        return self.encryption_manager.encrypt_multiple_fields(config, sensitive_fields)
    
    def decrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in connection config
        
        Args:
            config: Connection configuration with encrypted fields
            
        Returns:
            Configuration with decrypted sensitive fields
        """
        sensitive_fields = [
            'client_secret',
            'api_key',
            'password',
            'access_token',
            'refresh_token'
        ]
        
        return self.encryption_manager.decrypt_multiple_fields(config, sensitive_fields)


# Global encryption manager instance
encryption_manager = EncryptionManager()
phi_encryption = PHIEncryption(encryption_manager)
config_encryption = ConnectionConfigEncryption(encryption_manager)