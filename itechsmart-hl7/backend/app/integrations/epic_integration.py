"""
Epic EMR Integration
Supports Epic FHIR API and proprietary interfaces
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.encounter import Encounter

logger = logging.getLogger(__name__)


class EpicIntegration:
    """
    Epic EMR Integration using FHIR R4 API
    Supports: Patient demographics, observations, medications, encounters
    """

    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get("base_url")
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.access_token = None
        self.token_expiry = None
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def authenticate(self) -> bool:
        """
        Authenticate with Epic using OAuth 2.0
        Epic uses backend services authorization
        """
        try:
            # Epic OAuth 2.0 token endpoint
            token_url = f"{self.base_url}/oauth2/token"

            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "system/Patient.read system/Observation.read system/MedicationRequest.read",
            }

            response = await self.http_client.post(token_url, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

            logger.info("Epic authentication successful")
            return True

        except Exception as e:
            logger.error(f"Epic authentication failed: {e}")
            return False

    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or datetime.now() >= self.token_expiry:
            await self.authenticate()

    async def get_patient(self, patient_id: str) -> Optional[Dict]:
        """
        Retrieve patient demographics from Epic
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/FHIR/R4/Patient/{patient_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
            }

            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()

            patient_data = response.json()
            patient = Patient(**patient_data)

            # Convert to simplified format
            return {
                "id": patient.id,
                "mrn": self._extract_mrn(patient),
                "name": self._format_name(patient.name[0] if patient.name else None),
                "gender": patient.gender,
                "birth_date": str(patient.birthDate) if patient.birthDate else None,
                "phone": self._extract_phone(patient),
                "email": self._extract_email(patient),
                "address": self._format_address(
                    patient.address[0] if patient.address else None
                ),
                "raw_fhir": patient_data,
            }

        except Exception as e:
            logger.error(f"Failed to retrieve patient {patient_id}: {e}")
            return None

    async def search_patients(self, criteria: Dict[str, str]) -> List[Dict]:
        """
        Search for patients using various criteria
        Supports: name, birthdate, identifier, gender
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/FHIR/R4/Patient"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
            }

            response = await self.http_client.get(url, headers=headers, params=criteria)
            response.raise_for_status()

            bundle = response.json()
            patients = []

            if bundle.get("entry"):
                for entry in bundle["entry"]:
                    patient_data = entry.get("resource")
                    if patient_data:
                        patient = Patient(**patient_data)
                        patients.append(
                            {
                                "id": patient.id,
                                "mrn": self._extract_mrn(patient),
                                "name": self._format_name(
                                    patient.name[0] if patient.name else None
                                ),
                                "gender": patient.gender,
                                "birth_date": (
                                    str(patient.birthDate)
                                    if patient.birthDate
                                    else None
                                ),
                            }
                        )

            return patients

        except Exception as e:
            logger.error(f"Patient search failed: {e}")
            return []

    async def get_observations(
        self, patient_id: str, category: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve patient observations (vitals, labs, etc.)
        Categories: vital-signs, laboratory, social-history, etc.
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/FHIR/R4/Observation"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
            }

            params = {"patient": patient_id}
            if category:
                params["category"] = category

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()

            bundle = response.json()
            observations = []

            if bundle.get("entry"):
                for entry in bundle["entry"]:
                    obs_data = entry.get("resource")
                    if obs_data:
                        obs = Observation(**obs_data)
                        observations.append(
                            {
                                "id": obs.id,
                                "code": self._extract_code(obs.code),
                                "value": self._extract_value(obs),
                                "unit": self._extract_unit(obs),
                                "date": (
                                    str(obs.effectiveDateTime)
                                    if obs.effectiveDateTime
                                    else None
                                ),
                                "status": obs.status,
                                "category": category,
                            }
                        )

            return observations

        except Exception as e:
            logger.error(
                f"Failed to retrieve observations for patient {patient_id}: {e}"
            )
            return []

    async def get_medications(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient medications
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/FHIR/R4/MedicationRequest"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
            }

            params = {"patient": patient_id}

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()

            bundle = response.json()
            medications = []

            if bundle.get("entry"):
                for entry in bundle["entry"]:
                    med_data = entry.get("resource")
                    if med_data:
                        med = MedicationRequest(**med_data)
                        medications.append(
                            {
                                "id": med.id,
                                "medication": self._extract_medication_name(med),
                                "dosage": self._extract_dosage(med),
                                "status": med.status,
                                "intent": med.intent,
                                "authored_on": (
                                    str(med.authoredOn) if med.authoredOn else None
                                ),
                            }
                        )

            return medications

        except Exception as e:
            logger.error(
                f"Failed to retrieve medications for patient {patient_id}: {e}"
            )
            return []

    async def get_encounters(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient encounters (visits)
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/FHIR/R4/Encounter"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
            }

            params = {"patient": patient_id}

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()

            bundle = response.json()
            encounters = []

            if bundle.get("entry"):
                for entry in bundle["entry"]:
                    enc_data = entry.get("resource")
                    if enc_data:
                        enc = Encounter(**enc_data)
                        encounters.append(
                            {
                                "id": enc.id,
                                "status": enc.status,
                                "class": (
                                    enc.class_fhir.code if enc.class_fhir else None
                                ),
                                "type": self._extract_encounter_type(enc),
                                "period": self._extract_period(enc),
                                "reason": self._extract_reason(enc),
                            }
                        )

            return encounters

        except Exception as e:
            logger.error(f"Failed to retrieve encounters for patient {patient_id}: {e}")
            return []

    async def create_observation(
        self, patient_id: str, observation_data: Dict
    ) -> Optional[str]:
        """
        Create a new observation in Epic
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/FHIR/R4/Observation"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/fhir+json",
                "Accept": "application/fhir+json",
            }

            # Build FHIR Observation resource
            observation = {
                "resourceType": "Observation",
                "status": "final",
                "subject": {"reference": f"Patient/{patient_id}"},
                "code": observation_data.get("code"),
                "valueQuantity": observation_data.get("value"),
                "effectiveDateTime": observation_data.get(
                    "date", datetime.now().isoformat()
                ),
            }

            response = await self.http_client.post(
                url, headers=headers, json=observation
            )
            response.raise_for_status()

            result = response.json()
            return result.get("id")

        except Exception as e:
            logger.error(f"Failed to create observation: {e}")
            return None

    # Helper methods for data extraction

    def _extract_mrn(self, patient: Patient) -> Optional[str]:
        """Extract Medical Record Number from patient identifiers"""
        if patient.identifier:
            for identifier in patient.identifier:
                if identifier.type and identifier.type.coding:
                    for coding in identifier.type.coding:
                        if coding.code == "MR":
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
        return " ".join(parts) if parts else None

    def _extract_phone(self, patient: Patient) -> Optional[str]:
        """Extract phone number"""
        if patient.telecom:
            for contact in patient.telecom:
                if contact.system == "phone":
                    return contact.value
        return None

    def _extract_email(self, patient: Patient) -> Optional[str]:
        """Extract email address"""
        if patient.telecom:
            for contact in patient.telecom:
                if contact.system == "email":
                    return contact.value
        return None

    def _format_address(self, address) -> Optional[Dict]:
        """Format patient address"""
        if not address:
            return None
        return {
            "line": address.line if address.line else [],
            "city": address.city,
            "state": address.state,
            "postal_code": address.postalCode,
            "country": address.country,
        }

    def _extract_code(self, code) -> Optional[Dict]:
        """Extract code from CodeableConcept"""
        if code and code.coding:
            coding = code.coding[0]
            return {
                "system": coding.system,
                "code": coding.code,
                "display": coding.display,
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
        return None

    def _extract_unit(self, observation: Observation) -> Optional[str]:
        """Extract observation unit"""
        if observation.valueQuantity:
            return observation.valueQuantity.unit
        return None

    def _extract_medication_name(self, med: MedicationRequest) -> Optional[str]:
        """Extract medication name"""
        if med.medicationCodeableConcept and med.medicationCodeableConcept.coding:
            return med.medicationCodeableConcept.coding[0].display
        return None

    def _extract_dosage(self, med: MedicationRequest) -> Optional[str]:
        """Extract dosage instructions"""
        if med.dosageInstruction:
            dosage = med.dosageInstruction[0]
            if dosage.text:
                return dosage.text
        return None

    def _extract_encounter_type(self, encounter: Encounter) -> Optional[str]:
        """Extract encounter type"""
        if encounter.type:
            for type_concept in encounter.type:
                if type_concept.coding:
                    return type_concept.coding[0].display
        return None

    def _extract_period(self, encounter: Encounter) -> Optional[Dict]:
        """Extract encounter period"""
        if encounter.period:
            return {
                "start": (
                    str(encounter.period.start) if encounter.period.start else None
                ),
                "end": str(encounter.period.end) if encounter.period.end else None,
            }
        return None

    def _extract_reason(self, encounter: Encounter) -> Optional[str]:
        """Extract encounter reason"""
        if encounter.reasonCode:
            for reason in encounter.reasonCode:
                if reason.coding:
                    return reason.coding[0].display
        return None

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
