"""
Cerner EMR Integration
Supports Cerner FHIR API (now Oracle Health)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.condition import Condition
from fhir.resources.allergyintolerance import AllergyIntolerance

logger = logging.getLogger(__name__)


class CernerIntegration:
    """
    Cerner (Oracle Health) EMR Integration using FHIR DSTU2/R4 API
    Supports: Patient demographics, observations, conditions, allergies
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get('base_url')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.tenant_id = config.get('tenant_id')
        self.access_token = None
        self.token_expiry = None
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def authenticate(self) -> bool:
        """
        Authenticate with Cerner using OAuth 2.0
        Cerner uses system-level authorization
        """
        try:
            token_url = f"{self.base_url}/tenants/{self.tenant_id}/protocols/oauth2/profiles/smart-v1/token"
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'system/Patient.read system/Observation.read system/Condition.read'
            }
            
            response = await self.http_client.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Cerner authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Cerner authentication failed: {e}")
            return False
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or datetime.now() >= self.token_expiry:
            await self.authenticate()
    
    async def get_patient(self, patient_id: str) -> Optional[Dict]:
        """
        Retrieve patient demographics from Cerner
        """
        await self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/Patient/{patient_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/fhir+json'
            }
            
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            
            patient_data = response.json()
            patient = Patient(**patient_data)
            
            return {
                'id': patient.id,
                'mrn': self._extract_mrn(patient),
                'name': self._format_name(patient.name[0] if patient.name else None),
                'gender': patient.gender,
                'birth_date': str(patient.birthDate) if patient.birthDate else None,
                'phone': self._extract_phone(patient),
                'email': self._extract_email(patient),
                'address': self._format_address(patient.address[0] if patient.address else None),
                'marital_status': self._extract_marital_status(patient),
                'raw_fhir': patient_data
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve patient {patient_id}: {e}")
            return None
    
    async def search_patients(self, criteria: Dict[str, str]) -> List[Dict]:
        """
        Search for patients using various criteria
        Cerner supports: _id, identifier, name, birthdate, gender, phone, email
        """
        await self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/Patient"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/fhir+json'
            }
            
            response = await self.http_client.get(url, headers=headers, params=criteria)
            response.raise_for_status()
            
            bundle = response.json()
            patients = []
            
            if bundle.get('entry'):
                for entry in bundle['entry']:
                    patient_data = entry.get('resource')
                    if patient_data:
                        patient = Patient(**patient_data)
                        patients.append({
                            'id': patient.id,
                            'mrn': self._extract_mrn(patient),
                            'name': self._format_name(patient.name[0] if patient.name else None),
                            'gender': patient.gender,
                            'birth_date': str(patient.birthDate) if patient.birthDate else None
                        })
            
            return patients
            
        except Exception as e:
            logger.error(f"Patient search failed: {e}")
            return []
    
    async def get_observations(self, patient_id: str, category: Optional[str] = None) -> List[Dict]:
        """
        Retrieve patient observations (vitals, labs, etc.)
        Cerner categories: vital-signs, laboratory, social-history, exam, imaging, procedure
        """
        await self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/Observation"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/fhir+json'
            }
            
            params = {'patient': patient_id}
            if category:
                params['category'] = category
            
            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            bundle = response.json()
            observations = []
            
            if bundle.get('entry'):
                for entry in bundle['entry']:
                    obs_data = entry.get('resource')
                    if obs_data:
                        obs = Observation(**obs_data)
                        observations.append({
                            'id': obs.id,
                            'code': self._extract_code(obs.code),
                            'value': self._extract_value(obs),
                            'unit': self._extract_unit(obs),
                            'date': str(obs.effectiveDateTime) if obs.effectiveDateTime else None,
                            'status': obs.status,
                            'category': category,
                            'interpretation': self._extract_interpretation(obs)
                        })
            
            return observations
            
        except Exception as e:
            logger.error(f"Failed to retrieve observations for patient {patient_id}: {e}")
            return []
    
    async def get_conditions(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient conditions (diagnoses)
        """
        await self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/Condition"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/fhir+json'
            }
            
            params = {'patient': patient_id}
            
            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            bundle = response.json()
            conditions = []
            
            if bundle.get('entry'):
                for entry in bundle['entry']:
                    cond_data = entry.get('resource')
                    if cond_data:
                        cond = Condition(**cond_data)
                        conditions.append({
                            'id': cond.id,
                            'code': self._extract_code(cond.code),
                            'clinical_status': cond.clinicalStatus.coding[0].code if cond.clinicalStatus else None,
                            'verification_status': cond.verificationStatus.coding[0].code if cond.verificationStatus else None,
                            'severity': self._extract_severity(cond),
                            'onset_date': str(cond.onsetDateTime) if cond.onsetDateTime else None,
                            'recorded_date': str(cond.recordedDate) if cond.recordedDate else None
                        })
            
            return conditions
            
        except Exception as e:
            logger.error(f"Failed to retrieve conditions for patient {patient_id}: {e}")
            return []
    
    async def get_allergies(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient allergies and intolerances
        """
        await self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/AllergyIntolerance"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/fhir+json'
            }
            
            params = {'patient': patient_id}
            
            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            bundle = response.json()
            allergies = []
            
            if bundle.get('entry'):
                for entry in bundle['entry']:
                    allergy_data = entry.get('resource')
                    if allergy_data:
                        allergy = AllergyIntolerance(**allergy_data)
                        allergies.append({
                            'id': allergy.id,
                            'substance': self._extract_code(allergy.code),
                            'clinical_status': allergy.clinicalStatus.coding[0].code if allergy.clinicalStatus else None,
                            'verification_status': allergy.verificationStatus.coding[0].code if allergy.verificationStatus else None,
                            'type': allergy.type,
                            'category': allergy.category[0] if allergy.category else None,
                            'criticality': allergy.criticality,
                            'onset_date': str(allergy.onsetDateTime) if allergy.onsetDateTime else None,
                            'reactions': self._extract_reactions(allergy)
                        })
            
            return allergies
            
        except Exception as e:
            logger.error(f"Failed to retrieve allergies for patient {patient_id}: {e}")
            return []
    
    async def get_vital_signs(self, patient_id: str) -> Dict[str, List[Dict]]:
        """
        Retrieve patient vital signs organized by type
        Returns: blood_pressure, heart_rate, temperature, respiratory_rate, oxygen_saturation
        """
        await self._ensure_authenticated()
        
        vitals = {
            'blood_pressure': [],
            'heart_rate': [],
            'temperature': [],
            'respiratory_rate': [],
            'oxygen_saturation': []
        }
        
        try:
            observations = await self.get_observations(patient_id, category='vital-signs')
            
            for obs in observations:
                code = obs.get('code', {}).get('code', '')
                
                # Map LOINC codes to vital sign types
                if code in ['85354-9', '8480-6', '8462-4']:  # Blood pressure
                    vitals['blood_pressure'].append(obs)
                elif code in ['8867-4']:  # Heart rate
                    vitals['heart_rate'].append(obs)
                elif code in ['8310-5', '8331-1']:  # Temperature
                    vitals['temperature'].append(obs)
                elif code in ['9279-1']:  # Respiratory rate
                    vitals['respiratory_rate'].append(obs)
                elif code in ['2708-6', '59408-5']:  # Oxygen saturation
                    vitals['oxygen_saturation'].append(obs)
            
            return vitals
            
        except Exception as e:
            logger.error(f"Failed to retrieve vital signs for patient {patient_id}: {e}")
            return vitals
    
    # Helper methods
    
    def _extract_mrn(self, patient: Patient) -> Optional[str]:
        """Extract Medical Record Number"""
        if patient.identifier:
            for identifier in patient.identifier:
                if identifier.type and identifier.type.coding:
                    for coding in identifier.type.coding:
                        if coding.code == 'MR':
                            return identifier.value
        return None
    
    def _format_name(self, name) -> Optional[str]:
        """Format patient name"""
        if not name:
            return None
        parts = []
        if name.given:
            parts.extend(name.given)
        if name.family:
            parts.append(name.family)
        return ' '.join(parts) if parts else None
    
    def _extract_phone(self, patient: Patient) -> Optional[str]:
        """Extract phone number"""
        if patient.telecom:
            for contact in patient.telecom:
                if contact.system == 'phone':
                    return contact.value
        return None
    
    def _extract_email(self, patient: Patient) -> Optional[str]:
        """Extract email address"""
        if patient.telecom:
            for contact in patient.telecom:
                if contact.system == 'email':
                    return contact.value
        return None
    
    def _format_address(self, address) -> Optional[Dict]:
        """Format patient address"""
        if not address:
            return None
        return {
            'line': address.line if address.line else [],
            'city': address.city,
            'state': address.state,
            'postal_code': address.postalCode,
            'country': address.country
        }
    
    def _extract_marital_status(self, patient: Patient) -> Optional[str]:
        """Extract marital status"""
        if patient.maritalStatus and patient.maritalStatus.coding:
            return patient.maritalStatus.coding[0].display
        return None
    
    def _extract_code(self, code) -> Optional[Dict]:
        """Extract code from CodeableConcept"""
        if code and code.coding:
            coding = code.coding[0]
            return {
                'system': coding.system,
                'code': coding.code,
                'display': coding.display
            }
        return None
    
    def _extract_value(self, observation: Observation) -> Optional[Any]:
        """Extract observation value"""
        if observation.valueQuantity:
            return observation.valueQuantity.value
        elif observation.valueString:
            return observation.valueString
        elif observation.valueBoolean is not None:
            return observation.valueBoolean
        elif observation.valueCodeableConcept:
            return self._extract_code(observation.valueCodeableConcept)
        return None
    
    def _extract_unit(self, observation: Observation) -> Optional[str]:
        """Extract observation unit"""
        if observation.valueQuantity:
            return observation.valueQuantity.unit
        return None
    
    def _extract_interpretation(self, observation: Observation) -> Optional[str]:
        """Extract observation interpretation"""
        if observation.interpretation:
            for interp in observation.interpretation:
                if interp.coding:
                    return interp.coding[0].display
        return None
    
    def _extract_severity(self, condition: Condition) -> Optional[str]:
        """Extract condition severity"""
        if condition.severity and condition.severity.coding:
            return condition.severity.coding[0].display
        return None
    
    def _extract_reactions(self, allergy: AllergyIntolerance) -> List[Dict]:
        """Extract allergy reactions"""
        reactions = []
        if allergy.reaction:
            for reaction in allergy.reaction:
                reactions.append({
                    'manifestation': [self._extract_code(m) for m in reaction.manifestation] if reaction.manifestation else [],
                    'severity': reaction.severity,
                    'onset': str(reaction.onset) if reaction.onset else None
                })
        return reactions
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()