"""
Base CRM Connector Class
Abstract base class for all CRM platform integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

@dataclass
class CRMContact:
    """Standardized contact data structure"""
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    lead_score: Optional[int] = None
    source: Optional[str] = None
    created_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    custom_fields: Optional[Dict[str, Any]] = None

@dataclass
class CRMOpportunity:
    """Standardized opportunity data structure"""
    id: str
    contact_id: str
    name: str
    stage: str
    value: Optional[float] = None
    probability: Optional[int] = None
    close_date: Optional[datetime] = None
    created_date: Optional[datetime] = None
    custom_fields: Optional[Dict[str, Any]] = None

@dataclass
class CRMAccount:
    """Standardized account data structure"""
    id: str
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    revenue: Optional[float] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    created_date: Optional[datetime] = None
    custom_fields: Optional[Dict[str, Any]] = None

class BaseCRMConnector(ABC):
    """Abstract base class for CRM connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.access_token = None
        self.refresh_token = None
        
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the CRM platform"""
        pass
        
    @abstractmethod
    async def get_contacts(self, limit: int = 100, offset: int = 0) -> List[CRMContact]:
        """Retrieve contacts from CRM"""
        pass
        
    @abstractmethod
    async def get_contact(self, contact_id: str) -> Optional[CRMContact]:
        """Retrieve a specific contact"""
        pass
        
    @abstractmethod
    async def update_contact(self, contact_id: str, data: Dict[str, Any]) -> bool:
        """Update a contact in CRM"""
        pass
        
    @abstractmethod
    async def create_contact(self, contact: CRMContact) -> str:
        """Create a new contact in CRM"""
        pass
        
    @abstractmethod
    async def get_opportunities(self, contact_id: Optional[str] = None) -> List[CRMOpportunity]:
        """Retrieve opportunities from CRM"""
        pass
        
    @abstractmethod
    async def get_accounts(self) -> List[CRMAccount]:
        """Retrieve accounts from CRM"""
        pass
        
    async def sync_data(self, last_sync: Optional[datetime] = None) -> Dict[str, int]:
        """
        Sync all data from CRM
        Returns summary of synced records
        """
        try:
            if not await self.authenticate():
                raise AuthenticationError("Failed to authenticate with CRM")
                
            contacts_synced = 0
            opportunities_synced = 0
            accounts_synced = 0
            
            # Sync contacts
            contacts = await self.get_contacts(limit=1000)
            for contact in contacts:
                # Process contact through CDP engine
                contacts_synced += 1
                
            # Sync opportunities
            opportunities = await self.get_opportunities()
            for opportunity in opportunities:
                # Process opportunity through CDP engine
                opportunities_synced += 1
                
            # Sync accounts
            accounts = await self.get_accounts()
            for account in accounts:
                # Process account through CDP engine
                accounts_synced += 1
                
            return {
                'contacts': contacts_synced,
                'opportunities': opportunities_synced,
                'accounts': accounts_synced
            }
            
        except Exception as e:
            self.logger.error(f"Sync failed: {str(e)}")
            raise
            
    async def test_connection(self) -> bool:
        """Test connection to CRM platform"""
        try:
            return await self.authenticate()
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False

class AuthenticationError(Exception):
    """Authentication failed error"""
    pass

class CRMConfigurationError(Exception):
    """CRM configuration error"""
    pass