"""
Domain Administrator Account Manager
Manage domain admin accounts for executing remediation commands in Windows environments
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime, timedelta
import secrets
import string
import hashlib

try:
    import winrm
    from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
    HAS_AD_LIBS = True
except ImportError:
    HAS_AD_LIBS = False


class AccountType(Enum):
    """Domain account types"""
    SERVICE_ACCOUNT = "service"
    ADMIN_ACCOUNT = "admin"
    TEMPORARY_ACCOUNT = "temporary"
    REMEDIATION_ACCOUNT = "remediation"


class DomainAdminManager:
    """
    Manage domain administrator accounts for remediation
    
    Features:
    - Create temporary admin accounts
    - Rotate credentials automatically
    - Least privilege access
    - Audit logging
    - Auto-cleanup of temporary accounts
    - Secure credential storage
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.active_accounts = {}
        self.account_history = []
        
        # Domain controller connection
        self.dc_host = config.get('domain_controller')
        self.domain = config.get('domain')
        self.admin_username = config.get('admin_username')
        self.admin_password = config.get('admin_password')
        
        # LDAP connection
        self.ldap_connection = None
        
        if not HAS_AD_LIBS:
            self.logger.warning("Active Directory libraries not installed")
    
    async def connect_domain(self) -> bool:
        """Connect to Active Directory domain"""
        
        if not HAS_AD_LIBS:
            self.logger.error("AD libraries not available")
            return False
        
        try:
            self.logger.info(f"Connecting to domain controller: {self.dc_host}")
            
            # Create LDAP server
            server = Server(self.dc_host, get_info=ALL)
            
            # Create connection
            self.ldap_connection = Connection(
                server,
                user=f"{self.domain}\\{self.admin_username}",
                password=self.admin_password,
                auto_bind=True
            )
            
            self.logger.info("✅ Connected to Active Directory")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to AD: {e}")
            return False
    
    async def create_remediation_account(
        self,
        purpose: str,
        permissions: List[str],
        duration_hours: int = 24,
        auto_rotate: bool = True
    ) -> Dict[str, Any]:
        """
        Create a temporary remediation account
        
        Args:
            purpose: Purpose of the account
            permissions: List of required permissions
            duration_hours: Account lifetime in hours
            auto_rotate: Auto-rotate credentials
        
        Returns:
            Account details including username and password
        """
        
        self.logger.info(f"🔐 Creating remediation account for: {purpose}")
        
        # Generate account details
        account_id = secrets.token_hex(8)
        username = f"itechsmart_remediation_{account_id[:8]}"
        password = self._generate_secure_password()
        
        account = {
            'id': account_id,
            'username': username,
            'password': password,
            'domain': self.domain,
            'type': AccountType.REMEDIATION_ACCOUNT.value,
            'purpose': purpose,
            'permissions': permissions,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=duration_hours),
            'auto_rotate': auto_rotate,
            'rotation_count': 0,
            'last_used': None,
            'usage_count': 0
        }
        
        try:
            # Create account in Active Directory
            if self.ldap_connection:
                await self._create_ad_account(account)
            else:
                self.logger.warning("No AD connection - account created locally only")
            
            # Add to active accounts
            self.active_accounts[account_id] = account
            
            self.logger.info(f"✅ Remediation account created: {username}")
            
            return {
                'account_id': account_id,
                'username': username,
                'password': password,
                'domain': self.domain,
                'full_username': f"{self.domain}\\{username}",
                'expires_at': account['expires_at'].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create remediation account: {e}")
            raise
    
    async def _create_ad_account(self, account: Dict[str, Any]):
        """Create account in Active Directory"""
        
        if not self.ldap_connection:
            return
        
        # Build DN (Distinguished Name)
        ou = self.config.get('remediation_ou', 'OU=ServiceAccounts')
        dn = f"CN={account['username']},{ou},DC={self.domain.replace('.', ',DC=')}"
        
        # Account attributes
        attributes = {
            'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
            'cn': account['username'],
            'sAMAccountName': account['username'],
            'userPrincipalName': f"{account['username']}@{self.domain}",
            'displayName': f"iTechSmart Remediation - {account['purpose']}",
            'description': f"Temporary remediation account - Expires: {account['expires_at']}",
            'userAccountControl': 512,  # Normal account
        }
        
        try:
            # Add user to AD
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.ldap_connection.add(dn, attributes=attributes)
            )
            
            # Set password
            await self._set_ad_password(dn, account['password'])
            
            # Add to required groups
            await self._add_to_groups(dn, account['permissions'])
            
            self.logger.info(f"Account created in AD: {account['username']}")
            
        except Exception as e:
            self.logger.error(f"Failed to create AD account: {e}")
            raise
    
    async def _set_ad_password(self, dn: str, password: str):
        """Set password for AD account"""
        
        if not self.ldap_connection:
            return
        
        # Encode password for AD
        password_value = f'"{password}"'.encode('utf-16-le')
        
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.ldap_connection.modify(
                dn,
                {'unicodePwd': [(MODIFY_REPLACE, [password_value])]}
            )
        )
    
    async def _add_to_groups(self, dn: str, permissions: List[str]):
        """Add account to required AD groups"""
        
        if not self.ldap_connection:
            return
        
        # Map permissions to AD groups
        group_map = {
            'server_admin': 'CN=Server Operators,CN=Builtin,DC=domain,DC=com',
            'backup_operator': 'CN=Backup Operators,CN=Builtin,DC=domain,DC=com',
            'network_admin': 'CN=Network Configuration Operators,CN=Builtin,DC=domain,DC=com',
        }
        
        for permission in permissions:
            group_dn = group_map.get(permission)
            if group_dn:
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.ldap_connection.modify(
                            group_dn,
                            {'member': [(MODIFY_REPLACE, [dn])]}
                        )
                    )
                except Exception as e:
                    self.logger.error(f"Failed to add to group {permission}: {e}")
    
    def _generate_secure_password(self, length: int = 32) -> str:
        """Generate a secure random password"""
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one of each type
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill the rest
        all_chars = lowercase + uppercase + digits + special
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Shuffle
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return ''.join(password_list)
    
    async def rotate_credentials(self, account_id: str) -> Dict[str, str]:
        """Rotate account credentials"""
        
        if account_id not in self.active_accounts:
            raise ValueError(f"Account {account_id} not found")
        
        account = self.active_accounts[account_id]
        
        self.logger.info(f"🔄 Rotating credentials for: {account['username']}")
        
        # Generate new password
        new_password = self._generate_secure_password()
        
        # Update in AD
        if self.ldap_connection:
            ou = self.config.get('remediation_ou', 'OU=ServiceAccounts')
            dn = f"CN={account['username']},{ou},DC={self.domain.replace('.', ',DC=')}"
            await self._set_ad_password(dn, new_password)
        
        # Update account
        old_password = account['password']
        account['password'] = new_password
        account['rotation_count'] += 1
        account['last_rotated'] = datetime.now()
        
        self.logger.info(f"✅ Credentials rotated for: {account['username']}")
        
        return {
            'username': account['username'],
            'new_password': new_password,
            'rotation_count': account['rotation_count']
        }
    
    async def delete_account(self, account_id: str) -> bool:
        """Delete a remediation account"""
        
        if account_id not in self.active_accounts:
            self.logger.error(f"Account {account_id} not found")
            return False
        
        account = self.active_accounts[account_id]
        
        self.logger.info(f"🗑️  Deleting account: {account['username']}")
        
        try:
            # Delete from AD
            if self.ldap_connection:
                ou = self.config.get('remediation_ou', 'OU=ServiceAccounts')
                dn = f"CN={account['username']},{ou},DC={self.domain.replace('.', ',DC=')}"
                
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.ldap_connection.delete(dn)
                )
            
            # Move to history
            account['deleted_at'] = datetime.now()
            self.account_history.append(account)
            
            # Remove from active
            del self.active_accounts[account_id]
            
            self.logger.info(f"✅ Account deleted: {account['username']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete account: {e}")
            return False
    
    async def get_account_credentials(self, account_id: str) -> Optional[Dict[str, str]]:
        """Get credentials for an account"""
        
        if account_id not in self.active_accounts:
            return None
        
        account = self.active_accounts[account_id]
        
        # Update usage tracking
        account['last_used'] = datetime.now()
        account['usage_count'] += 1
        
        return {
            'username': account['username'],
            'password': account['password'],
            'domain': account['domain'],
            'full_username': f"{account['domain']}\\{account['username']}"
        }
    
    async def verify_account_access(
        self,
        account_id: str,
        target_host: str
    ) -> bool:
        """Verify account can access target host"""
        
        credentials = await self.get_account_credentials(account_id)
        
        if not credentials:
            return False
        
        try:
            # Test WinRM connection
            session = winrm.Session(
                f'http://{target_host}:5985/wsman',
                auth=(credentials['full_username'], credentials['password'])
            )
            
            # Try simple command
            result = session.run_cmd('whoami')
            
            return result.status_code == 0
            
        except Exception as e:
            self.logger.error(f"Access verification failed: {e}")
            return False
    
    async def cleanup_expired_accounts(self):
        """Clean up expired accounts"""
        
        current_time = datetime.now()
        expired_accounts = []
        
        for account_id, account in self.active_accounts.items():
            if current_time >= account['expires_at']:
                expired_accounts.append(account_id)
        
        for account_id in expired_accounts:
            self.logger.info(f"⏰ Auto-deleting expired account: {account_id}")
            await self.delete_account(account_id)
    
    async def auto_rotate_accounts(self):
        """Auto-rotate credentials for accounts with auto_rotate enabled"""
        
        for account_id, account in self.active_accounts.items():
            if account.get('auto_rotate', False):
                # Rotate every 12 hours
                last_rotated = account.get('last_rotated', account['created_at'])
                if datetime.now() - last_rotated >= timedelta(hours=12):
                    await self.rotate_credentials(account_id)
    
    def get_active_accounts(self) -> List[Dict[str, Any]]:
        """Get list of active accounts"""
        
        # Return without passwords
        return [
            {
                'id': acc['id'],
                'username': acc['username'],
                'domain': acc['domain'],
                'type': acc['type'],
                'purpose': acc['purpose'],
                'created_at': acc['created_at'].isoformat(),
                'expires_at': acc['expires_at'].isoformat(),
                'usage_count': acc['usage_count'],
                'rotation_count': acc['rotation_count']
            }
            for acc in self.active_accounts.values()
        ]
    
    def get_account_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get account history"""
        return self.account_history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get account management statistics"""
        
        total_usage = sum(acc['usage_count'] for acc in self.active_accounts.values())
        total_rotations = sum(acc['rotation_count'] for acc in self.active_accounts.values())
        
        return {
            'active_accounts': len(self.active_accounts),
            'total_created': len(self.account_history) + len(self.active_accounts),
            'total_deleted': len(self.account_history),
            'total_usage': total_usage,
            'total_rotations': total_rotations,
            'avg_usage_per_account': total_usage / len(self.active_accounts) if self.active_accounts else 0
        }