"""
Allscripts EMR Integration
Supports Allscripts Unity API and HL7 interfaces
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import json

logger = logging.getLogger(__name__)


class AllscriptsIntegration:
    """
    Allscripts EMR Integration
    Supports Unity API and HL7 v2.x messaging
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get('base_url')
        self.app_name = config.get('app_name')
        self.app_username = config.get('app_username')
        self.app_password = config.get('app_password')
        self.access_token = None
        self.token_expiry = None
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def authenticate(self) -> bool:
        """
        Authenticate with Allscripts using GetToken
        Allscripts uses custom Unity API authentication
        """
        try:
            url = f"{self.base_url}/Unity/UnityService.svc/json/GetToken"
            
            payload = {
                "Action": "GetToken",
                "AppUserID": self.app_username,
                "Appname": self.app_name,
                "PatientID": "",
                "Token": "",
                "Parameter1": self.app_username,
                "Parameter2": self.app_password,
                "Parameter3": self.app_name,
                "Parameter4": "",
                "Parameter5": "",
                "Parameter6": "",
                "data": ""
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result.get('GetTokenResult')
            self.token_expiry = datetime.now() + timedelta(hours=8)  # Allscripts tokens last 8 hours
            
            logger.info("Allscripts authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Allscripts authentication failed: {e}")
            return False
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or datetime.now() >= self.token_expiry:
            await self.authenticate()
    
    async def _make_magic_call(self, action: str, parameters: List[str], data: str = "") -> Optional[Any]:
        """
        Make a MagicJson call to Allscripts Unity API
        """
        await self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/Unity/UnityService.svc/json/MagicJson"
            
            # Pad parameters to 6 elements
            while len(parameters) < 6:
                parameters.append("")
            
            payload = {
                "Action": action,
                "AppUserID": self.app_username,
                "Appname": self.app_name,
                "PatientID": "",
                "Token": self.access_token,
                "Parameter1": parameters[0],
                "Parameter2": parameters[1],
                "Parameter3": parameters[2],
                "Parameter4": parameters[3],
                "Parameter5": parameters[4],
                "Parameter6": parameters[5],
                "data": data
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get('MagicJsonResult')
            
        except Exception as e:
            logger.error(f"MagicJson call failed for action {action}: {e}")
            return None
    
    async def get_patient(self, patient_id: str) -> Optional[Dict]:
        """
        Retrieve patient demographics from Allscripts
        """
        try:
            result = await self._make_magic_call(
                action="GetPatient",
                parameters=[patient_id, "", "", "", "", ""]
            )
            
            if result and len(result) > 0:
                patient_data = result[0]
                return {
                    'id': patient_data.get('ID'),
                    'mrn': patient_data.get('PatientID'),
                    'first_name': patient_data.get('FirstName'),
                    'last_name': patient_data.get('LastName'),
                    'middle_name': patient_data.get('MiddleName'),
                    'name': f"{patient_data.get('FirstName', '')} {patient_data.get('MiddleName', '')} {patient_data.get('LastName', '')}".strip(),
                    'gender': patient_data.get('Sex'),
                    'birth_date': patient_data.get('DOB'),
                    'ssn': patient_data.get('SSN'),
                    'phone_home': patient_data.get('HomePhone'),
                    'phone_work': patient_data.get('WorkPhone'),
                    'phone_mobile': patient_data.get('MobilePhone'),
                    'email': patient_data.get('EmailAddress'),
                    'address': {
                        'street': patient_data.get('Address1'),
                        'street2': patient_data.get('Address2'),
                        'city': patient_data.get('City'),
                        'state': patient_data.get('State'),
                        'zip': patient_data.get('Zip'),
                        'country': patient_data.get('Country')
                    },
                    'marital_status': patient_data.get('MaritalStatus'),
                    'race': patient_data.get('Race'),
                    'ethnicity': patient_data.get('Ethnicity'),
                    'language': patient_data.get('Language'),
                    'raw_data': patient_data
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve patient {patient_id}: {e}")
            return None
    
    async def search_patients(self, criteria: Dict[str, str]) -> List[Dict]:
        """
        Search for patients using various criteria
        """
        try:
            # Build search parameters
            last_name = criteria.get('last_name', '')
            first_name = criteria.get('first_name', '')
            dob = criteria.get('birth_date', '')
            ssn = criteria.get('ssn', '')
            
            result = await self._make_magic_call(
                action="SearchPatients",
                parameters=[last_name, first_name, dob, ssn, "", ""]
            )
            
            patients = []
            if result:
                for patient_data in result:
                    patients.append({
                        'id': patient_data.get('ID'),
                        'mrn': patient_data.get('PatientID'),
                        'name': f"{patient_data.get('FirstName', '')} {patient_data.get('LastName', '')}".strip(),
                        'gender': patient_data.get('Sex'),
                        'birth_date': patient_data.get('DOB')
                    })
            
            return patients
            
        except Exception as e:
            logger.error(f"Patient search failed: {e}")
            return []
    
    async def get_encounters(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient encounters
        """
        try:
            result = await self._make_magic_call(
                action="GetEncounter",
                parameters=[patient_id, "", "", "", "", ""]
            )
            
            encounters = []
            if result:
                for encounter_data in result:
                    encounters.append({
                        'id': encounter_data.get('EncounterID'),
                        'patient_id': patient_id,
                        'date': encounter_data.get('EncounterDate'),
                        'type': encounter_data.get('EncounterType'),
                        'location': encounter_data.get('Location'),
                        'provider': encounter_data.get('Provider'),
                        'chief_complaint': encounter_data.get('ChiefComplaint'),
                        'status': encounter_data.get('Status')
                    })
            
            return encounters
            
        except Exception as e:
            logger.error(f"Failed to retrieve encounters for patient {patient_id}: {e}")
            return []
    
    async def get_problems(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient problem list
        """
        try:
            result = await self._make_magic_call(
                action="GetProblems",
                parameters=[patient_id, "", "", "", "", ""]
            )
            
            problems = []
            if result:
                for problem_data in result:
                    problems.append({
                        'id': problem_data.get('ProblemID'),
                        'patient_id': patient_id,
                        'description': problem_data.get('Description'),
                        'icd10_code': problem_data.get('ICD10Code'),
                        'snomed_code': problem_data.get('SNOMEDCode'),
                        'onset_date': problem_data.get('OnsetDate'),
                        'status': problem_data.get('Status'),
                        'severity': problem_data.get('Severity')
                    })
            
            return problems
            
        except Exception as e:
            logger.error(f"Failed to retrieve problems for patient {patient_id}: {e}")
            return []
    
    async def get_medications(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient medications
        """
        try:
            result = await self._make_magic_call(
                action="GetMedications",
                parameters=[patient_id, "", "", "", "", ""]
            )
            
            medications = []
            if result:
                for med_data in result:
                    medications.append({
                        'id': med_data.get('MedicationID'),
                        'patient_id': patient_id,
                        'name': med_data.get('DrugName'),
                        'generic_name': med_data.get('GenericName'),
                        'strength': med_data.get('Strength'),
                        'dosage': med_data.get('Dosage'),
                        'route': med_data.get('Route'),
                        'frequency': med_data.get('Frequency'),
                        'start_date': med_data.get('StartDate'),
                        'end_date': med_data.get('EndDate'),
                        'status': med_data.get('Status'),
                        'prescriber': med_data.get('Prescriber'),
                        'pharmacy': med_data.get('Pharmacy')
                    })
            
            return medications
            
        except Exception as e:
            logger.error(f"Failed to retrieve medications for patient {patient_id}: {e}")
            return []
    
    async def get_allergies(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient allergies
        """
        try:
            result = await self._make_magic_call(
                action="GetAllergies",
                parameters=[patient_id, "", "", "", "", ""]
            )
            
            allergies = []
            if result:
                for allergy_data in result:
                    allergies.append({
                        'id': allergy_data.get('AllergyID'),
                        'patient_id': patient_id,
                        'allergen': allergy_data.get('Allergen'),
                        'reaction': allergy_data.get('Reaction'),
                        'severity': allergy_data.get('Severity'),
                        'onset_date': allergy_data.get('OnsetDate'),
                        'status': allergy_data.get('Status'),
                        'notes': allergy_data.get('Notes')
                    })
            
            return allergies
            
        except Exception as e:
            logger.error(f"Failed to retrieve allergies for patient {patient_id}: {e}")
            return []
    
    async def get_lab_results(self, patient_id: str, date_from: Optional[str] = None) -> List[Dict]:
        """
        Retrieve patient lab results
        """
        try:
            result = await self._make_magic_call(
                action="GetLabResults",
                parameters=[patient_id, date_from or "", "", "", "", ""]
            )
            
            lab_results = []
            if result:
                for lab_data in result:
                    lab_results.append({
                        'id': lab_data.get('ResultID'),
                        'patient_id': patient_id,
                        'test_name': lab_data.get('TestName'),
                        'test_code': lab_data.get('TestCode'),
                        'value': lab_data.get('Value'),
                        'unit': lab_data.get('Unit'),
                        'reference_range': lab_data.get('ReferenceRange'),
                        'abnormal_flag': lab_data.get('AbnormalFlag'),
                        'status': lab_data.get('Status'),
                        'date': lab_data.get('ResultDate'),
                        'ordering_provider': lab_data.get('OrderingProvider'),
                        'performing_lab': lab_data.get('PerformingLab')
                    })
            
            return lab_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve lab results for patient {patient_id}: {e}")
            return []
    
    async def get_vitals(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient vital signs
        """
        try:
            result = await self._make_magic_call(
                action="GetVitals",
                parameters=[patient_id, "", "", "", "", ""]
            )
            
            vitals = []
            if result:
                for vital_data in result:
                    vitals.append({
                        'id': vital_data.get('VitalID'),
                        'patient_id': patient_id,
                        'date': vital_data.get('VitalDate'),
                        'blood_pressure_systolic': vital_data.get('BPSystolic'),
                        'blood_pressure_diastolic': vital_data.get('BPDiastolic'),
                        'heart_rate': vital_data.get('HeartRate'),
                        'temperature': vital_data.get('Temperature'),
                        'temperature_unit': vital_data.get('TempUnit'),
                        'respiratory_rate': vital_data.get('RespiratoryRate'),
                        'oxygen_saturation': vital_data.get('OxygenSaturation'),
                        'height': vital_data.get('Height'),
                        'height_unit': vital_data.get('HeightUnit'),
                        'weight': vital_data.get('Weight'),
                        'weight_unit': vital_data.get('WeightUnit'),
                        'bmi': vital_data.get('BMI')
                    })
            
            return vitals
            
        except Exception as e:
            logger.error(f"Failed to retrieve vitals for patient {patient_id}: {e}")
            return []
    
    async def get_immunizations(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient immunizations
        """
        try:
            result = await self._make_magic_call(
                action="GetImmunizations",
                parameters=[patient_id, "", "", "", "", ""]
            )
            
            immunizations = []
            if result:
                for imm_data in result:
                    immunizations.append({
                        'id': imm_data.get('ImmunizationID'),
                        'patient_id': patient_id,
                        'vaccine': imm_data.get('Vaccine'),
                        'cvx_code': imm_data.get('CVXCode'),
                        'date_administered': imm_data.get('DateAdministered'),
                        'dose': imm_data.get('Dose'),
                        'route': imm_data.get('Route'),
                        'site': imm_data.get('Site'),
                        'lot_number': imm_data.get('LotNumber'),
                        'manufacturer': imm_data.get('Manufacturer'),
                        'administered_by': imm_data.get('AdministeredBy')
                    })
            
            return immunizations
            
        except Exception as e:
            logger.error(f"Failed to retrieve immunizations for patient {patient_id}: {e}")
            return []
    
    async def save_document(self, patient_id: str, document_data: Dict) -> Optional[str]:
        """
        Save a document to patient chart
        """
        try:
            # Build document XML
            doc_xml = f"""
            <Document>
                <PatientID>{patient_id}</PatientID>
                <DocumentType>{document_data.get('type', 'Clinical Note')}</DocumentType>
                <Title>{document_data.get('title', '')}</Title>
                <Content>{document_data.get('content', '')}</Content>
                <Author>{document_data.get('author', '')}</Author>
                <Date>{document_data.get('date', datetime.now().isoformat())}</Date>
            </Document>
            """
            
            result = await self._make_magic_call(
                action="SaveDocument",
                parameters=[patient_id, "", "", "", "", ""],
                data=doc_xml
            )
            
            if result:
                return result.get('DocumentID')
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to save document for patient {patient_id}: {e}")
            return None
    
    async def get_ccda(self, patient_id: str) -> Optional[str]:
        """
        Retrieve patient C-CDA (Consolidated Clinical Document Architecture)
        """
        try:
            result = await self._make_magic_call(
                action="GetCCDA",
                parameters=[patient_id, "", "", "", "", ""]
            )
            
            if result:
                return result.get('CCDADocument')
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve C-CDA for patient {patient_id}: {e}")
            return None
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()