"""
End-to-End Encryption for iTechSmart Ninja
Implements encryption for data at rest and in transit
"""

import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import base64
import secrets
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(str, Enum):
    """Supported encryption algorithms"""
    AES_256 = "aes-256"
    RSA_2048 = "rsa-2048"
    RSA_4096 = "rsa-4096"


@dataclass
class EncryptionKey:
    """Encryption key information"""
    key_id: str
    algorithm: EncryptionAlgorithm
    created_at: datetime
    expires_at: Optional[datetime]
    user_id: str
    key_data: bytes
    public_key: Optional[bytes] = None


@dataclass
class EncryptedData:
    """Encrypted data container"""
    data: bytes
    algorithm: EncryptionAlgorithm
    key_id: str
    iv: Optional[bytes]
    timestamp: datetime


class EncryptionManager:
    """Manages encryption keys and operations"""
    
    def __init__(self):
        """Initialize encryption manager"""
        self.keys: Dict[str, EncryptionKey] = {}
        self.master_key = Fernet.generate_key()
        self.fernet = Fernet(self.master_key)
        logger.info("EncryptionManager initialized successfully")
    
    def generate_key(
        self,
        user_id: str,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256,
        expires_in_days: Optional[int] = None
    ) -> EncryptionKey:
        """Generate a new encryption key"""
        import uuid
        
        key_id = str(uuid.uuid4())
        created_at = datetime.now()
        expires_at = created_at + timedelta(days=expires_in_days) if expires_in_days else None
        
        if algorithm == EncryptionAlgorithm.AES_256:
            key_data = Fernet.generate_key()
            public_key = None
        elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            key_size = 2048 if algorithm == EncryptionAlgorithm.RSA_2048 else 4096
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_key = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            algorithm=algorithm,
            created_at=created_at,
            expires_at=expires_at,
            user_id=user_id,
            key_data=key_data,
            public_key=public_key
        )
        
        self.keys[key_id] = encryption_key
        logger.info(f"Generated {algorithm.value} key {key_id} for user {user_id}")
        
        return encryption_key
    
    def encrypt_data(
        self,
        data: bytes,
        key_id: str
    ) -> EncryptedData:
        """Encrypt data using specified key"""
        key = self.keys.get(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found")
        
        if key.expires_at and datetime.now() > key.expires_at:
            raise ValueError(f"Key {key_id} has expired")
        
        if key.algorithm == EncryptionAlgorithm.AES_256:
            fernet = Fernet(key.key_data)
            encrypted = fernet.encrypt(data)
            iv = None
        elif key.algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            private_key = serialization.load_pem_private_key(
                key.key_data,
                password=None,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            encrypted = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            iv = None
        else:
            raise ValueError(f"Unsupported algorithm: {key.algorithm}")
        
        return EncryptedData(
            data=encrypted,
            algorithm=key.algorithm,
            key_id=key_id,
            iv=iv,
            timestamp=datetime.now()
        )
    
    def decrypt_data(
        self,
        encrypted_data: EncryptedData
    ) -> bytes:
        """Decrypt data"""
        key = self.keys.get(encrypted_data.key_id)
        if not key:
            raise ValueError(f"Key {encrypted_data.key_id} not found")
        
        if encrypted_data.algorithm == EncryptionAlgorithm.AES_256:
            fernet = Fernet(key.key_data)
            decrypted = fernet.decrypt(encrypted_data.data)
        elif encrypted_data.algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            private_key = serialization.load_pem_private_key(
                key.key_data,
                password=None,
                backend=default_backend()
            )
            decrypted = private_key.decrypt(
                encrypted_data.data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        else:
            raise ValueError(f"Unsupported algorithm: {encrypted_data.algorithm}")
        
        return decrypted
    
    def encrypt_string(self, text: str, key_id: str) -> str:
        """Encrypt a string and return base64-encoded result"""
        encrypted = self.encrypt_data(text.encode(), key_id)
        return base64.b64encode(encrypted.data).decode()
    
    def decrypt_string(self, encrypted_text: str, key_id: str) -> str:
        """Decrypt a base64-encoded string"""
        encrypted_data = EncryptedData(
            data=base64.b64decode(encrypted_text),
            algorithm=self.keys[key_id].algorithm,
            key_id=key_id,
            iv=None,
            timestamp=datetime.now()
        )
        decrypted = self.decrypt_data(encrypted_data)
        return decrypted.decode()
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Hash a password using PBKDF2"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        return key, salt
    
    def verify_password(self, password: str, hashed: bytes, salt: bytes) -> bool:
        """Verify a password against its hash"""
        key, _ = self.hash_password(password, salt)
        return key == hashed
    
    def rotate_key(self, old_key_id: str, user_id: str) -> EncryptionKey:
        """Rotate an encryption key"""
        old_key = self.keys.get(old_key_id)
        if not old_key:
            raise ValueError(f"Key {old_key_id} not found")
        
        # Generate new key with same algorithm
        new_key = self.generate_key(user_id, old_key.algorithm)
        
        # Mark old key as expired
        old_key.expires_at = datetime.now()
        
        logger.info(f"Rotated key {old_key_id} to {new_key.key_id}")
        return new_key
    
    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Get encryption key by ID"""
        return self.keys.get(key_id)
    
    def delete_key(self, key_id: str) -> bool:
        """Delete an encryption key"""
        if key_id in self.keys:
            del self.keys[key_id]
            logger.info(f"Deleted key {key_id}")
            return True
        return False


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get or create global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager