"""
HashiCorp Vault Integration - Manage Secrets and Protect Sensitive Data
Secure credential storage and retrieval using Vault
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import aiohttp
import json

from ..core.models import HostCredentials, Platform


class VaultIntegration:
    """Integration with HashiCorp Vault for secrets management"""
    
    def __init__(
        self,
        vault_url: str,
        token: Optional[str] = None,
        namespace: Optional[str] = None
    ):
        self.vault_url = vault_url.rstrip('/')
        self.token = token
        self.namespace = namespace
        self.logger = logging.getLogger(__name__)
        self.headers = self._build_headers()
    
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.token:
            headers['X-Vault-Token'] = self.token
        
        if self.namespace:
            headers['X-Vault-Namespace'] = self.namespace
        
        return headers
    
    async def authenticate_approle(
        self,
        role_id: str,
        secret_id: str
    ) -> bool:
        """Authenticate using AppRole"""
        
        payload = {
            'role_id': role_id,
            'secret_id': secret_id
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.vault_url}/v1/auth/approle/login",
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.token = data['auth']['client_token']
                        self.headers = self._build_headers()
                        self.logger.info("Authenticated with Vault using AppRole")
                        return True
                    else:
                        self.logger.error(f"Vault authentication failed: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Vault authentication error: {e}")
            return False
    
    async def read_secret(
        self,
        path: str,
        mount_point: str = "secret"
    ) -> Optional[Dict[str, Any]]:
        """Read secret from Vault"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.vault_url}/v1/{mount_point}/data/{path}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', {}).get('data', {})
                    elif response.status == 404:
                        self.logger.warning(f"Secret not found: {path}")
                        return None
                    else:
                        self.logger.error(f"Failed to read secret: {response.status}")
                        return None
        
        except Exception as e:
            self.logger.error(f"Error reading secret: {e}")
            return None
    
    async def write_secret(
        self,
        path: str,
        data: Dict[str, Any],
        mount_point: str = "secret"
    ) -> bool:
        """Write secret to Vault"""
        
        payload = {'data': data}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.vault_url}/v1/{mount_point}/data/{path}",
                    json=payload,
                    headers=self.headers
                ) as response:
                    if response.status in [200, 204]:
                        self.logger.info(f"Secret written: {path}")
                        return True
                    else:
                        self.logger.error(f"Failed to write secret: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error writing secret: {e}")
            return False
    
    async def delete_secret(
        self,
        path: str,
        mount_point: str = "secret"
    ) -> bool:
        """Delete secret from Vault"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.vault_url}/v1/{mount_point}/metadata/{path}",
                    headers=self.headers
                ) as response:
                    if response.status == 204:
                        self.logger.info(f"Secret deleted: {path}")
                        return True
                    else:
                        self.logger.error(f"Failed to delete secret: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error deleting secret: {e}")
            return False
    
    async def list_secrets(
        self,
        path: str = "",
        mount_point: str = "secret"
    ) -> List[str]:
        """List secrets at path"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    'LIST',
                    f"{self.vault_url}/v1/{mount_point}/metadata/{path}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', {}).get('keys', [])
                    else:
                        return []
        
        except Exception as e:
            self.logger.error(f"Error listing secrets: {e}")
            return []
    
    async def store_credentials(
        self,
        host: str,
        credentials: HostCredentials
    ) -> bool:
        """Store host credentials in Vault"""
        
        secret_data = {
            'host': credentials.host,
            'username': credentials.username,
            'password': credentials.password,
            'private_key': credentials.private_key,
            'port': credentials.port,
            'platform': credentials.platform.value,
            'domain': credentials.domain,
            'use_sudo': credentials.use_sudo
        }
        
        # Remove None values
        secret_data = {k: v for k, v in secret_data.items() if v is not None}
        
        return await self.write_secret(
            path=f"itechsmart/hosts/{host}",
            data=secret_data
        )
    
    async def retrieve_credentials(
        self,
        host: str
    ) -> Optional[HostCredentials]:
        """Retrieve host credentials from Vault"""
        
        secret_data = await self.read_secret(
            path=f"itechsmart/hosts/{host}"
        )
        
        if not secret_data:
            return None
        
        try:
            return HostCredentials(
                host=secret_data['host'],
                username=secret_data['username'],
                password=secret_data.get('password'),
                private_key=secret_data.get('private_key'),
                port=secret_data.get('port', 22),
                platform=Platform(secret_data.get('platform', 'linux')),
                domain=secret_data.get('domain'),
                use_sudo=secret_data.get('use_sudo', False)
            )
        
        except Exception as e:
            self.logger.error(f"Error parsing credentials: {e}")
            return None
    
    async def rotate_secret(
        self,
        path: str,
        mount_point: str = "secret"
    ) -> bool:
        """Rotate a secret (create new version)"""
        
        # Read current secret
        current = await self.read_secret(path, mount_point)
        
        if not current:
            return False
        
        # Write back (creates new version)
        return await self.write_secret(path, current, mount_point)
    
    async def create_policy(
        self,
        name: str,
        policy: str
    ) -> bool:
        """Create Vault policy"""
        
        payload = {'policy': policy}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.vault_url}/v1/sys/policy/{name}",
                    json=payload,
                    headers=self.headers
                ) as response:
                    if response.status == 204:
                        self.logger.info(f"Policy created: {name}")
                        return True
                    else:
                        self.logger.error(f"Failed to create policy: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error creating policy: {e}")
            return False
    
    async def enable_secrets_engine(
        self,
        path: str,
        engine_type: str = "kv-v2"
    ) -> bool:
        """Enable secrets engine"""
        
        payload = {
            'type': engine_type,
            'options': {'version': '2'} if engine_type == 'kv' else {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.vault_url}/v1/sys/mounts/{path}",
                    json=payload,
                    headers=self.headers
                ) as response:
                    if response.status == 204:
                        self.logger.info(f"Secrets engine enabled: {path}")
                        return True
                    else:
                        self.logger.error(f"Failed to enable secrets engine: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error enabling secrets engine: {e}")
            return False
    
    async def generate_dynamic_credentials(
        self,
        role: str,
        mount_point: str = "database"
    ) -> Optional[Dict[str, str]]:
        """Generate dynamic database credentials"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.vault_url}/v1/{mount_point}/creds/{role}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', {})
                    else:
                        self.logger.error(f"Failed to generate credentials: {response.status}")
                        return None
        
        except Exception as e:
            self.logger.error(f"Error generating credentials: {e}")
            return None
    
    async def renew_token(self, increment: int = 3600) -> bool:
        """Renew Vault token"""
        
        payload = {'increment': increment}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.vault_url}/v1/auth/token/renew-self",
                    json=payload,
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        self.logger.info("Token renewed")
                        return True
                    else:
                        self.logger.error(f"Failed to renew token: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error renewing token: {e}")
            return False