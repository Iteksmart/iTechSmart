"""
Epic Systems Integration
Supports Epic Interconnect, FHIR APIs, and HL7 v2.x interfaces
"""

import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import base64

logger = logging.getLogger(__name__)


class EpicIntegration:
    """
    Epic Systems EMR Integration
    Supports Epic Interconnect, FHIR R4, and HL7 v2.x
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Epic integration
        
        Args:
            config: Configuration dictionary containing:
                - base_url: Epic FHIR base URL
                - client_id: OAuth client ID
                - client_secret: OAuth client secret (for backend apps)
                - private_key: Private key for JWT authentication
                - hl7_host: HL7 interface host
                - hl7_port: HL7 interface port
        """
        self.config = config
        self.base_url = config.get('base_url', '').rstrip('/')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.private_key = config.get('private_key')
        self.hl7_host = config.get('hl7_host')
        self.hl7_port = config.get('hl7_port', 6661)
        
        self.access_token = None
        self.token_expiry = None
        
        # Epic-specific endpoints
        self.endpoints = {
            'token': f"{self.base_url}/oauth2/token",
            'patient': f"{self.base_url}/api/FHIR/R4/Patient",
            'observation': f"{self.base_url}/api/FHIR/R4/Observation",
            'condition': f"{self.base_url}/api/FHIR/R4/Condition",
            'medication': f"{self.base_url}/api/FHIR/R4/MedicationRequest",
            'appointment': f"{self.base_url}/api/FHIR/R4/Appointment",
            'encounter': f"{self.base_url}/api/FHIR/R4/Encounter",
            'procedure': f"{self.base_url}/api/FHIR/R4/Procedure",
            'diagnostic_report': f"{self.base_url}/api/FHIR/R4/DiagnosticReport",
            'document_reference': f"{self.base_url}/api/FHIR/R4/DocumentReference"
        }
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Epic using OAuth 2.0
        Supports both client credentials and JWT bearer token
        
        Returns:
            True if authentication successful
        """
        try:
            async with httpx.AsyncClient() as client:
                # Backend service authentication (client credentials)
                if self.client_secret:
                    auth_string = f"{self.client_id}:{self.client_secret}"
                    auth_bytes = auth_string.encode('ascii')
                    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                    
                    response = await client.post(
                        self.endpoints['token'],
                        headers={
                            'Authorization': f'Basic {auth_b64}',
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        data={
                            'grant_type': 'client_credentials',
                            'scope': 'system/*.read system/*.write'
                        }
                    )
                
                # JWT bearer token authentication (for apps)
                elif self.private_key:
                    # Create JWT assertion
                    jwt_token = self._create_jwt_assertion()
                    
                    response = await client.post(
                        self.endpoints['token'],
                        headers={
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        data={
                            'grant_type': 'client_credentials',
                            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                            'client_assertion': jwt_token,
                            'scope': 'system/*.read system/*.write'
                        }
                    )
                else:
                    logger.error("No authentication credentials provided")
                    return False
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data['access_token']
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expiry = datetime.utcnow().timestamp() + expires_in
                    
                    logger.info("Epic authentication successful")
                    return True
                else:
                    logger.error(f"Epic authentication failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error authenticating with Epic: {str(e)}")
            return False
    
    def _create_jwt_assertion(self) -> str:
        """Create JWT assertion for authentication"""
        import jwt
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        
        payload = {
            'iss': self.client_id,
            'sub': self.client_id,
            'aud': self.endpoints['token'],
            'jti': str(datetime.utcnow().timestamp()),
            'exp': now + timedelta(minutes=5),
            'iat': now
        }
        
        token = jwt.encode(payload, self.private_key, algorithm='RS384')
        return token
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or (self.token_expiry and datetime.utcnow().timestamp() >= self.token_expiry):
            await self.authenticate()
    
    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make authenticated request to Epic API"""
        await self._ensure_authenticated()
        
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        headers['Accept'] = 'application/fhir+json'
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            return response
    
    # Patient Operations
    
    async def get_patient(self, patient_id: str) -> Optional[Dict]:
        """
        Get patient by ID
        
        Args:
            patient_id: Epic patient ID or MRN
            
        Returns:
            Patient FHIR resource
        """
        try:
            response = await self._make_request('GET', f"{self.endpoints['patient']}/{patient_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting patient: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting patient from Epic: {str(e)}")
            return None
    
    async def search_patients(self, **search_params) -> List[Dict]:
        """
        Search for patients
        
        Args:
            **search_params: Search parameters (name, birthdate, identifier, etc.)
            
        Returns:
            List of patient FHIR resources
        """
        try:
            response = await self._make_request('GET', self.endpoints['patient'], params=search_params)
            
            if response.status_code == 200:
                bundle = response.json()
                return bundle.get('entry', [])
            else:
                logger.error(f"Error searching patients: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching patients in Epic: {str(e)}")
            return []
    
    async def create_patient(self, patient_data: Dict) -> Optional[Dict]:
        """
        Create new patient
        
        Args:
            patient_data: Patient FHIR resource
            
        Returns:
            Created patient resource
        """
        try:
            response = await self._make_request(
                'POST',
                self.endpoints['patient'],
                json=patient_data,
                headers={'Content-Type': 'application/fhir+json'}
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error creating patient: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating patient in Epic: {str(e)}")
            return None
    
    async def update_patient(self, patient_id: str, patient_data: Dict) -> Optional[Dict]:
        """
        Update existing patient
        
        Args:
            patient_id: Patient ID
            patient_data: Updated patient FHIR resource
            
        Returns:
            Updated patient resource
        """
        try:
            response = await self._make_request(
                'PUT',
                f"{self.endpoints['patient']}/{patient_id}",
                json=patient_data,
                headers={'Content-Type': 'application/fhir+json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error updating patient: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating patient in Epic: {str(e)}")
            return None
    
    # Observation Operations
    
    async def get_observations(self, patient_id: str, category: Optional[str] = None) -> List[Dict]:
        """
        Get patient observations (lab results, vitals, etc.)
        
        Args:
            patient_id: Patient ID
            category: Observation category (laboratory, vital-signs, etc.)
            
        Returns:
            List of observation FHIR resources
        """
        try:
            params = {'patient': patient_id}
            if category:
                params['category'] = category
            
            response = await self._make_request('GET', self.endpoints['observation'], params=params)
            
            if response.status_code == 200:
                bundle = response.json()
                return bundle.get('entry', [])
            else:
                logger.error(f"Error getting observations: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting observations from Epic: {str(e)}")
            return []
    
    async def create_observation(self, observation_data: Dict) -> Optional[Dict]:
        """
        Create new observation
        
        Args:
            observation_data: Observation FHIR resource
            
        Returns:
            Created observation resource
        """
        try:
            response = await self._make_request(
                'POST',
                self.endpoints['observation'],
                json=observation_data,
                headers={'Content-Type': 'application/fhir+json'}
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error creating observation: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating observation in Epic: {str(e)}")
            return None
    
    # Medication Operations
    
    async def get_medications(self, patient_id: str) -> List[Dict]:
        """
        Get patient medications
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of medication request FHIR resources
        """
        try:
            response = await self._make_request(
                'GET',
                self.endpoints['medication'],
                params={'patient': patient_id}
            )
            
            if response.status_code == 200:
                bundle = response.json()
                return bundle.get('entry', [])
            else:
                logger.error(f"Error getting medications: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting medications from Epic: {str(e)}")
            return []
    
    async def create_medication_order(self, medication_data: Dict) -> Optional[Dict]:
        """
        Create medication order
        
        Args:
            medication_data: MedicationRequest FHIR resource
            
        Returns:
            Created medication request resource
        """
        try:
            response = await self._make_request(
                'POST',
                self.endpoints['medication'],
                json=medication_data,
                headers={'Content-Type': 'application/fhir+json'}
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error creating medication order: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating medication order in Epic: {str(e)}")
            return None
    
    # Appointment Operations
    
    async def get_appointments(self, patient_id: str, start_date: Optional[str] = None) -> List[Dict]:
        """
        Get patient appointments
        
        Args:
            patient_id: Patient ID
            start_date: Start date for appointment search (YYYY-MM-DD)
            
        Returns:
            List of appointment FHIR resources
        """
        try:
            params = {'patient': patient_id}
            if start_date:
                params['date'] = f'ge{start_date}'
            
            response = await self._make_request('GET', self.endpoints['appointment'], params=params)
            
            if response.status_code == 200:
                bundle = response.json()
                return bundle.get('entry', [])
            else:
                logger.error(f"Error getting appointments: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting appointments from Epic: {str(e)}")
            return []
    
    async def create_appointment(self, appointment_data: Dict) -> Optional[Dict]:
        """
        Create appointment
        
        Args:
            appointment_data: Appointment FHIR resource
            
        Returns:
            Created appointment resource
        """
        try:
            response = await self._make_request(
                'POST',
                self.endpoints['appointment'],
                json=appointment_data,
                headers={'Content-Type': 'application/fhir+json'}
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error creating appointment: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating appointment in Epic: {str(e)}")
            return None
    
    # Document Operations
    
    async def get_clinical_notes(self, patient_id: str) -> List[Dict]:
        """
        Get patient clinical notes
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of document reference FHIR resources
        """
        try:
            response = await self._make_request(
                'GET',
                self.endpoints['document_reference'],
                params={'patient': patient_id, 'type': 'clinical-note'}
            )
            
            if response.status_code == 200:
                bundle = response.json()
                return bundle.get('entry', [])
            else:
                logger.error(f"Error getting clinical notes: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting clinical notes from Epic: {str(e)}")
            return []
    
    async def upload_clinical_note(self, note_data: Dict) -> Optional[Dict]:
        """
        Upload clinical note to Epic
        
        Args:
            note_data: DocumentReference FHIR resource with note content
            
        Returns:
            Created document reference resource
        """
        try:
            response = await self._make_request(
                'POST',
                self.endpoints['document_reference'],
                json=note_data,
                headers={'Content-Type': 'application/fhir+json'}
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error uploading clinical note: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading clinical note to Epic: {str(e)}")
            return None
    
    # HL7 Interface Operations
    
    async def send_hl7_message(self, message: str) -> Optional[str]:
        """
        Send HL7 v2.x message to Epic interface
        
        Args:
            message: HL7 v2.x message string
            
        Returns:
            ACK message if successful
        """
        try:
            import socket
            
            # Connect to Epic HL7 interface
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.hl7_host, self.hl7_port))
            
            # Send message with MLLP framing
            mllp_message = f"\x0b{message}\x1c\x0d"
            sock.sendall(mllp_message.encode('utf-8'))
            
            # Receive ACK
            ack = sock.recv(4096).decode('utf-8')
            sock.close()
            
            # Remove MLLP framing
            ack = ack.strip('\x0b\x1c\x0d')
            
            logger.info("HL7 message sent successfully to Epic")
            return ack
            
        except Exception as e:
            logger.error(f"Error sending HL7 message to Epic: {str(e)}")
            return None
    
    # Utility Methods
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Epic
        
        Returns:
            Connection test results
        """
        results = {
            'fhir_api': False,
            'hl7_interface': False,
            'authentication': False,
            'errors': []
        }
        
        # Test authentication
        try:
            auth_success = await self.authenticate()
            results['authentication'] = auth_success
            if not auth_success:
                results['errors'].append('Authentication failed')
        except Exception as e:
            results['errors'].append(f'Authentication error: {str(e)}')
        
        # Test FHIR API
        try:
            response = await self._make_request('GET', f"{self.base_url}/metadata")
            results['fhir_api'] = response.status_code == 200
            if response.status_code != 200:
                results['errors'].append(f'FHIR API error: {response.status_code}')
        except Exception as e:
            results['errors'].append(f'FHIR API error: {str(e)}')
        
        # Test HL7 interface
        if self.hl7_host:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.hl7_host, self.hl7_port))
                sock.close()
                results['hl7_interface'] = True
            except Exception as e:
                results['errors'].append(f'HL7 interface error: {str(e)}')
        
        return results


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Configure Epic integration
        config = {
            'base_url': 'https://fhir.epic.com/interconnect-fhir-oauth',
            'client_id': 'your-client-id',
            'client_secret': 'your-client-secret',
            'hl7_host': 'hl7.epic.hospital.org',
            'hl7_port': 6661
        }
        
        epic = EpicIntegration(config)
        
        # Test connection
        test_results = await epic.test_connection()
        print(f"Connection test: {json.dumps(test_results, indent=2)}")
        
        # Get patient
        patient = await epic.get_patient('patient-id')
        if patient:
            print(f"Patient: {json.dumps(patient, indent=2)}")
        
        # Get observations
        observations = await epic.get_observations('patient-id', category='laboratory')
        print(f"Found {len(observations)} lab results")
    
    asyncio.run(main())