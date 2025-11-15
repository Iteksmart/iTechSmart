"""
iTechSmart Vault - Secrets & Configuration Management
Encrypted secrets storage, dynamic secrets, and certificate management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4
import hashlib
import base64


class SecretType(str, Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    CERTIFICATE = "certificate"
    API_KEY = "api_key"


class Secret:
    def __init__(self, secret_id: str, path: str, secret_type: SecretType):
        self.secret_id = secret_id
        self.path = path
        self.secret_type = secret_type
        self.value = ""
        self.encrypted_value = ""
        self.version = 1
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.expires_at = None
        self.rotation_enabled = False
        self.rotation_period_days = 90
        self.access_count = 0
        self.last_accessed = None


class AccessPolicy:
    def __init__(self, policy_id: str, name: str, paths: List[str], permissions: List[str]):
        self.policy_id = policy_id
        self.name = name
        self.paths = paths
        self.permissions = permissions  # read, write, delete
        self.principals = []
        self.is_active = True


class VaultEngine:
    def __init__(self):
        self.secrets: Dict[str, Secret] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.encryption_key = "vault_master_key_" + uuid4().hex
    
    def _encrypt(self, value: str) -> str:
        """Encrypt secret value"""
        # Simplified encryption (in production, use proper encryption)
        encrypted = base64.b64encode(
            hashlib.sha256((value + self.encryption_key).encode()).digest()
        ).decode()
        return encrypted
    
    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt secret value"""
        # Simplified decryption
        return encrypted_value  # In production, properly decrypt
    
    def store_secret(self, path: str, value: str, secret_type: SecretType = SecretType.STATIC) -> str:
        """Store a secret"""
        secret_id = str(uuid4())
        secret = Secret(secret_id, path, secret_type)
        secret.value = value
        secret.encrypted_value = self._encrypt(value)
        
        self.secrets[secret_id] = secret
        
        self._audit("store_secret", {
            "secret_id": secret_id,
            "path": path,
            "type": secret_type.value
        })
        
        return secret_id
    
    def get_secret(self, path: str, requester: str) -> Optional[str]:
        """Retrieve a secret"""
        secret = next((s for s in self.secrets.values() if s.path == path), None)
        
        if not secret:
            return None
        
        # Check if expired
        if secret.expires_at and datetime.utcnow() > secret.expires_at:
            return None
        
        secret.access_count += 1
        secret.last_accessed = datetime.utcnow()
        
        self._audit("get_secret", {
            "path": path,
            "requester": requester
        })
        
        return secret.value
    
    def rotate_secret(self, secret_id: str, new_value: str) -> bool:
        """Rotate a secret"""
        secret = self.secrets.get(secret_id)
        if not secret:
            return False
        
        secret.value = new_value
        secret.encrypted_value = self._encrypt(new_value)
        secret.version += 1
        secret.updated_at = datetime.utcnow()
        
        self._audit("rotate_secret", {
            "secret_id": secret_id,
            "new_version": secret.version
        })
        
        return True
    
    def generate_dynamic_secret(self, path: str, ttl_hours: int = 24) -> Dict[str, Any]:
        """Generate a dynamic secret with TTL"""
        secret_id = str(uuid4())
        secret = Secret(secret_id, path, SecretType.DYNAMIC)
        
        # Generate dynamic credentials
        username = f"user_{uuid4().hex[:8]}"
        password = uuid4().hex
        
        secret.value = f"{username}:{password}"
        secret.encrypted_value = self._encrypt(secret.value)
        secret.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        self.secrets[secret_id] = secret
        
        return {
            "secret_id": secret_id,
            "username": username,
            "password": password,
            "expires_at": secret.expires_at.isoformat()
        }
    
    def create_policy(self, name: str, paths: List[str], permissions: List[str]) -> str:
        """Create access policy"""
        policy_id = str(uuid4())
        policy = AccessPolicy(policy_id, name, paths, permissions)
        self.policies[policy_id] = policy
        return policy_id
    
    def check_access(self, principal: str, path: str, permission: str) -> bool:
        """Check if principal has access"""
        for policy in self.policies.values():
            if not policy.is_active:
                continue
            
            if principal in policy.principals:
                if any(p in path for p in policy.paths):
                    if permission in policy.permissions:
                        return True
        
        return False
    
    def _audit(self, action: str, details: Dict[str, Any]):
        """Audit log entry"""
        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details
        })
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log"""
        return self.audit_log[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        total_secrets = len(self.secrets)
        dynamic_secrets = len([s for s in self.secrets.values() if s.secret_type == SecretType.DYNAMIC])
        expired = len([s for s in self.secrets.values() if s.expires_at and datetime.utcnow() > s.expires_at])
        
        return {
            "total_secrets": total_secrets,
            "static_secrets": total_secrets - dynamic_secrets,
            "dynamic_secrets": dynamic_secrets,
            "expired_secrets": expired,
            "total_policies": len(self.policies),
            "audit_entries": len(self.audit_log)
        }


vault_engine = VaultEngine()