"""
CRM Integration Manager
Orchestrates multiple CRM integrations and unified data synchronization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type
from datetime import datetime, timedelta
from dataclasses import asdict
import json

from .base_crm import BaseCRMConnector, CRMContact, CRMOpportunity, CRMAccount
from .salesforce_connector import SalesforceConnector
from .hubspot_connector import HubSpotConnector
from .marketo_connector import MarketoConnector

class CRMIntegrationManager:
    """Manages multiple CRM integrations and unified data synchronization"""
    
    CONNECTOR_REGISTRY: Dict[str, Type[BaseCRMConnector]] = {
        'salesforce': SalesforceConnector,
        'hubspot': HubSpotConnector,
        'marketo': MarketoConnector,
    }
    
    def __init__(self, configs: Dict[str, Dict[str, Any]]):
        self.configs = configs
        self.connectors: Dict[str, BaseCRMConnector] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.last_sync_times: Dict[str, Optional[datetime]] = {}
        
    async def initialize_connectors(self):
        """Initialize all configured CRM connectors"""
        for crm_type, config in self.configs.items():
            if crm_type in self.CONNECTOR_REGISTRY:
                try:
                    connector_class = self.CONNECTOR_REGISTRY[crm_type]
                    connector = connector_class(config)
                    
                    if await connector.authenticate():
                        self.connectors[crm_type] = connector
                        self.logger.info(f"Successfully connected to {crm_type}")
                    else:
                        self.logger.error(f"Failed to authenticate with {crm_type}")
                        
                except Exception as e:
                    self.logger.error(f"Error initializing {crm_type}: {str(e)}")
            else:
                self.logger.warning(f"Unknown CRM type: {crm_type}")
                
    async def sync_all_crms(self, incremental: bool = True) -> Dict[str, Any]:
        """
        Sync all configured CRM systems
        Returns comprehensive sync report
        """
        if not self.connectors:
            await self.initialize_connectors()
            
        sync_report = {
            'timestamp': datetime.now().isoformat(),
            'sync_type': 'incremental' if incremental else 'full',
            'crm_results': {},
            'total_contacts': 0,
            'total_opportunities': 0,
            'total_accounts': 0,
            'errors': []
        }
        
        for crm_name, connector in self.connectors.items():
            try:
                self.logger.info(f"Starting sync for {crm_name}")
                
                # Get last sync time for incremental sync
                last_sync = self.last_sync_times.get(crm_name) if incremental else None
                
                # Sync data from CRM
                sync_result = await connector.sync_data(last_sync)
                
                # Merge data into unified format
                unified_data = await self._merge_crm_data(crm_name, sync_result)
                
                sync_report['crm_results'][crm_name] = {
                    'status': 'success',
                    'sync_result': sync_result,
                    'unified_data': unified_data
                }
                
                sync_report['total_contacts'] += sync_result.get('contacts', 0)
                sync_report['total_opportunities'] += sync_result.get('opportunities', 0)
                sync_report['total_accounts'] += sync_result.get('accounts', 0)
                
                # Update last sync time
                self.last_sync_times[crm_name] = datetime.now()
                
                self.logger.info(f"Successfully synced {crm_name}: {sync_result}")
                
            except Exception as e:
                error_msg = f"Sync failed for {crm_name}: {str(e)}"
                self.logger.error(error_msg)
                sync_report['errors'].append(error_msg)
                sync_report['crm_results'][crm_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                
        return sync_report
        
    async def get_unified_contacts(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get unified contacts from all CRM systems"""
        unified_contacts = []
        
        for crm_name, connector in self.connectors.items():
            try:
                contacts = await connector.get_contacts(limit=1000)
                for contact in contacts:
                    contact_data = asdict(contact)
                    contact_data['source_system'] = crm_name
                    unified_contacts.append(contact_data)
                    
            except Exception as e:
                self.logger.error(f"Error getting contacts from {crm_name}: {str(e)}")
                
        # Apply filters if provided
        if filters:
            unified_contacts = self._apply_filters(unified_contacts, filters)
            
        return unified_contacts
        
    async def get_unified_opportunities(self, contact_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get unified opportunities from all CRM systems"""
        unified_opportunities = []
        
        for crm_name, connector in self.connectors.items():
            try:
                opportunities = await connector.get_opportunities(contact_id)
                for opportunity in opportunities:
                    opp_data = asdict(opportunity)
                    opp_data['source_system'] = crm_name
                    unified_opportunities.append(opp_data)
                    
            except Exception as e:
                self.logger.error(f"Error getting opportunities from {crm_name}: {str(e)}")
                
        return unified_opportunities
        
    async def create_contact_in_all_crms(self, contact: CRMContact) -> Dict[str, Optional[str]]:
        """Create contact in all configured CRM systems"""
        results = {}
        
        for crm_name, connector in self.connectors.items():
            try:
                contact_id = await connector.create_contact(contact)
                results[crm_name] = contact_id
                self.logger.info(f"Created contact in {crm_name} with ID: {contact_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to create contact in {crm_name}: {str(e)}")
                results[crm_name] = None
                
        return results
        
    async def update_contact_in_all_crms(self, contact_id: str, data: Dict[str, Any]) -> Dict[str, bool]:
        """Update contact in all CRM systems"""
        results = {}
        
        for crm_name, connector in self.connectors.items():
            try:
                success = await connector.update_contact(contact_id, data)
                results[crm_name] = success
                self.logger.info(f"Updated contact in {crm_name}: {success}")
                
            except Exception as e:
                self.logger.error(f"Failed to update contact in {crm_name}: {str(e)}")
                results[crm_name] = False
                
        return results
        
    async def test_all_connections(self) -> Dict[str, bool]:
        """Test connection to all configured CRM systems"""
        results = {}
        
        for crm_name, connector in self.connectors.items():
            try:
                is_connected = await connector.test_connection()
                results[crm_name] = is_connected
                self.logger.info(f"Connection test for {crm_name}: {is_connected}")
                
            except Exception as e:
                self.logger.error(f"Connection test failed for {crm_name}: {str(e)}")
                results[crm_name] = False
                
        return results
        
    async def _merge_crm_data(self, crm_name: str, sync_result: Dict[str, int]) -> Dict[str, Any]:
        """Merge CRM data into unified format"""
        # This would integrate with the main CDP engine
        # For now, return basic merge info
        return {
            'crm_name': crm_name,
            'processed_records': sum(sync_result.values()),
            'merge_timestamp': datetime.now().isoformat()
        }
        
    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to data list"""
        filtered_data = data
        
        for field, value in filters.items():
            if field in filtered_data[0] if filtered_data else []:
                filtered_data = [item for item in filtered_data if item.get(field) == value]
                
        return filtered_data
        
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status for all CRM systems"""
        status = {
            'connected_crms': list(self.connectors.keys()),
            'last_sync_times': {
                crm: sync_time.isoformat() if sync_time else None
                for crm, sync_time in self.last_sync_times.items()
            },
            'connection_status': await self.test_all_connections(),
            'total_synced_records': {
                'contacts': 0,
                'opportunities': 0,
                'accounts': 0
            }
        }
        
        return status
        
    async def close_all_connections(self):
        """Close all CRM connections"""
        for crm_name, connector in self.connectors.items():
            try:
                await connector.close()
                self.logger.info(f"Closed connection to {crm_name}")
            except Exception as e:
                self.logger.error(f"Error closing connection to {crm_name}: {str(e)}")
                
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_connectors()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_all_connections()