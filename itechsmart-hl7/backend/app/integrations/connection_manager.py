"""
EMR Connection Manager
Manages connections to multiple EMR systems and provides unified interface
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

from .epic_integration import EpicIntegration
from .cerner_integration import CernerIntegration
from .meditech_integration import MeditechIntegration
from .allscripts_integration import AllscriptsIntegration
from .generic_hl7_adapter import GenericHL7Adapter

logger = logging.getLogger(__name__)


class EMRType(Enum):
    """Supported EMR types"""
    EPIC = "epic"
    CERNER = "cerner"
    MEDITECH = "meditech"
    ALLSCRIPTS = "allscripts"
    GENERIC_HL7 = "generic_hl7"


class EMRConnectionManager:
    """
    Manages connections to multiple EMR systems
    Provides unified interface for all EMR operations
    """
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.connection_configs: Dict[str, Dict] = {}
        self.active_connections: Dict[str, bool] = {}
        
    async def add_connection(self, connection_id: str, emr_type: EMRType, config: Dict[str, Any]) -> bool:
        """
        Add a new EMR connection
        """
        try:
            # Create appropriate integration instance
            if emr_type == EMRType.EPIC:
                integration = EpicIntegration(config)
            elif emr_type == EMRType.CERNER:
                integration = CernerIntegration(config)
            elif emr_type == EMRType.MEDITECH:
                integration = MeditechIntegration(config)
            elif emr_type == EMRType.ALLSCRIPTS:
                integration = AllscriptsIntegration(config)
            elif emr_type == EMRType.GENERIC_HL7:
                integration = GenericHL7Adapter(config)
            else:
                logger.error(f"Unsupported EMR type: {emr_type}")
                return False
            
            # Test connection
            if hasattr(integration, 'authenticate'):
                success = await integration.authenticate()
                if not success:
                    logger.error(f"Failed to authenticate with {connection_id}")
                    return False
            
            # Store connection
            self.connections[connection_id] = integration
            self.connection_configs[connection_id] = {
                'emr_type': emr_type,
                'config': config
            }
            self.active_connections[connection_id] = True
            
            logger.info(f"Successfully added connection: {connection_id} ({emr_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add connection {connection_id}: {e}")
            return False
    
    async def remove_connection(self, connection_id: str) -> bool:
        """
        Remove an EMR connection
        """
        try:
            if connection_id in self.connections:
                integration = self.connections[connection_id]
                
                # Close connection if applicable
                if hasattr(integration, 'close'):
                    await integration.close()
                
                # Remove from tracking
                del self.connections[connection_id]
                del self.connection_configs[connection_id]
                del self.active_connections[connection_id]
                
                logger.info(f"Successfully removed connection: {connection_id}")
                return True
            else:
                logger.warning(f"Connection not found: {connection_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove connection {connection_id}: {e}")
            return False
    
    def get_connection(self, connection_id: str) -> Optional[Any]:
        """
        Get a specific EMR connection
        """
        return self.connections.get(connection_id)
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """
        List all configured connections
        """
        connections = []
        for conn_id, config in self.connection_configs.items():
            connections.append({
                'id': conn_id,
                'emr_type': config['emr_type'].value,
                'active': self.active_connections.get(conn_id, False)
            })
        return connections
    
    async def test_connection(self, connection_id: str) -> bool:
        """
        Test if a connection is working
        """
        try:
            integration = self.connections.get(connection_id)
            if not integration:
                return False
            
            # Try to authenticate
            if hasattr(integration, 'authenticate'):
                return await integration.authenticate()
            
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed for {connection_id}: {e}")
            return False
    
    async def get_patient(self, connection_id: str, patient_id: str) -> Optional[Dict]:
        """
        Get patient from specific EMR connection
        """
        try:
            integration = self.connections.get(connection_id)
            if not integration:
                logger.error(f"Connection not found: {connection_id}")
                return None
            
            if hasattr(integration, 'get_patient'):
                return await integration.get_patient(patient_id)
            
            logger.error(f"get_patient not supported for connection: {connection_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get patient from {connection_id}: {e}")
            return None
    
    async def search_patients(self, connection_id: str, criteria: Dict[str, str]) -> List[Dict]:
        """
        Search patients in specific EMR connection
        """
        try:
            integration = self.connections.get(connection_id)
            if not integration:
                logger.error(f"Connection not found: {connection_id}")
                return []
            
            if hasattr(integration, 'search_patients'):
                return await integration.search_patients(criteria)
            
            logger.error(f"search_patients not supported for connection: {connection_id}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to search patients in {connection_id}: {e}")
            return []
    
    async def get_observations(self, connection_id: str, patient_id: str, category: Optional[str] = None) -> List[Dict]:
        """
        Get patient observations from specific EMR connection
        """
        try:
            integration = self.connections.get(connection_id)
            if not integration:
                logger.error(f"Connection not found: {connection_id}")
                return []
            
            if hasattr(integration, 'get_observations'):
                return await integration.get_observations(patient_id, category)
            
            logger.error(f"get_observations not supported for connection: {connection_id}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get observations from {connection_id}: {e}")
            return []
    
    async def get_medications(self, connection_id: str, patient_id: str) -> List[Dict]:
        """
        Get patient medications from specific EMR connection
        """
        try:
            integration = self.connections.get(connection_id)
            if not integration:
                logger.error(f"Connection not found: {connection_id}")
                return []
            
            if hasattr(integration, 'get_medications'):
                return await integration.get_medications(patient_id)
            
            logger.error(f"get_medications not supported for connection: {connection_id}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get medications from {connection_id}: {e}")
            return []
    
    async def get_allergies(self, connection_id: str, patient_id: str) -> List[Dict]:
        """
        Get patient allergies from specific EMR connection
        """
        try:
            integration = self.connections.get(connection_id)
            if not integration:
                logger.error(f"Connection not found: {connection_id}")
                return []
            
            if hasattr(integration, 'get_allergies'):
                return await integration.get_allergies(patient_id)
            
            logger.error(f"get_allergies not supported for connection: {connection_id}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get allergies from {connection_id}: {e}")
            return []
    
    async def aggregate_patient_data(self, patient_identifiers: Dict[str, str]) -> Dict[str, Any]:
        """
        Aggregate patient data from multiple EMR systems
        patient_identifiers: {connection_id: patient_id}
        """
        aggregated_data = {
            'demographics': None,
            'observations': [],
            'medications': [],
            'allergies': [],
            'conditions': [],
            'encounters': [],
            'sources': []
        }
        
        tasks = []
        
        for connection_id, patient_id in patient_identifiers.items():
            # Get patient demographics
            tasks.append(self._fetch_patient_data(connection_id, patient_id, aggregated_data))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return aggregated_data
    
    async def _fetch_patient_data(self, connection_id: str, patient_id: str, aggregated_data: Dict):
        """
        Fetch all patient data from a single connection
        """
        try:
            integration = self.connections.get(connection_id)
            if not integration:
                return
            
            # Get demographics
            if not aggregated_data['demographics'] and hasattr(integration, 'get_patient'):
                demographics = await integration.get_patient(patient_id)
                if demographics:
                    aggregated_data['demographics'] = demographics
                    aggregated_data['sources'].append(connection_id)
            
            # Get observations
            if hasattr(integration, 'get_observations'):
                observations = await integration.get_observations(patient_id)
                for obs in observations:
                    obs['source'] = connection_id
                    aggregated_data['observations'].append(obs)
            
            # Get medications
            if hasattr(integration, 'get_medications'):
                medications = await integration.get_medications(patient_id)
                for med in medications:
                    med['source'] = connection_id
                    aggregated_data['medications'].append(med)
            
            # Get allergies
            if hasattr(integration, 'get_allergies'):
                allergies = await integration.get_allergies(patient_id)
                for allergy in allergies:
                    allergy['source'] = connection_id
                    aggregated_data['allergies'].append(allergy)
            
            # Get conditions (if supported)
            if hasattr(integration, 'get_conditions'):
                conditions = await integration.get_conditions(patient_id)
                for condition in conditions:
                    condition['source'] = connection_id
                    aggregated_data['conditions'].append(condition)
            
            # Get encounters (if supported)
            if hasattr(integration, 'get_encounters'):
                encounters = await integration.get_encounters(patient_id)
                for encounter in encounters:
                    encounter['source'] = connection_id
                    aggregated_data['encounters'].append(encounter)
            
        except Exception as e:
            logger.error(f"Failed to fetch patient data from {connection_id}: {e}")
    
    async def send_hl7_message(self, connection_id: str, message: str) -> Optional[str]:
        """
        Send HL7 message through specific connection
        """
        try:
            integration = self.connections.get(connection_id)
            if not integration:
                logger.error(f"Connection not found: {connection_id}")
                return None
            
            if hasattr(integration, 'send_message'):
                return await integration.send_message(message)
            
            logger.error(f"send_message not supported for connection: {connection_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to send HL7 message through {connection_id}: {e}")
            return None
    
    async def close_all_connections(self):
        """
        Close all EMR connections
        """
        for connection_id in list(self.connections.keys()):
            await self.remove_connection(connection_id)
        
        logger.info("All connections closed")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about all connections
        """
        return {
            'total_connections': len(self.connections),
            'active_connections': sum(1 for active in self.active_connections.values() if active),
            'connections_by_type': self._count_by_type(),
            'connection_list': self.list_connections()
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """
        Count connections by EMR type
        """
        counts = {}
        for config in self.connection_configs.values():
            emr_type = config['emr_type'].value
            counts[emr_type] = counts.get(emr_type, 0) + 1
        return counts