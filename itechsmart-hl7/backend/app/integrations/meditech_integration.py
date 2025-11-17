"""
Meditech EMR Integration
Supports Meditech Expanse FHIR API and HL7 v2.x interfaces
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)


class MeditechIntegration:
    """
    Meditech EMR Integration
    Supports both FHIR API and HL7 v2.x messaging
    """

    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key")
        self.facility_id = config.get("facility_id")
        self.hl7_host = config.get("hl7_host")
        self.hl7_port = config.get("hl7_port", 2575)
        self.access_token = None
        self.token_expiry = None
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def authenticate(self) -> bool:
        """
        Authenticate with Meditech using API key
        Meditech uses custom authentication
        """
        try:
            token_url = f"{self.base_url}/auth/token"

            headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

            data = {"facility_id": self.facility_id, "grant_type": "api_key"}

            response = await self.http_client.post(
                token_url, headers=headers, json=data
            )
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

            logger.info("Meditech authentication successful")
            return True

        except Exception as e:
            logger.error(f"Meditech authentication failed: {e}")
            return False

    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or datetime.now() >= self.token_expiry:
            await self.authenticate()

    async def get_patient(self, patient_id: str) -> Optional[Dict]:
        """
        Retrieve patient demographics from Meditech
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/fhir/Patient/{patient_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
                "X-Facility-ID": self.facility_id,
            }

            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()

            patient_data = response.json()

            return {
                "id": patient_data.get("id"),
                "mrn": self._extract_identifier(patient_data, "MR"),
                "account_number": self._extract_identifier(patient_data, "AN"),
                "name": self._format_name(patient_data.get("name", [{}])[0]),
                "gender": patient_data.get("gender"),
                "birth_date": patient_data.get("birthDate"),
                "ssn": self._extract_identifier(patient_data, "SS"),
                "phone": self._extract_telecom(patient_data, "phone"),
                "email": self._extract_telecom(patient_data, "email"),
                "address": self._format_address(patient_data.get("address", [{}])[0]),
                "emergency_contact": self._extract_emergency_contact(patient_data),
                "raw_fhir": patient_data,
            }

        except Exception as e:
            logger.error(f"Failed to retrieve patient {patient_id}: {e}")
            return None

    async def search_patients(self, criteria: Dict[str, str]) -> List[Dict]:
        """
        Search for patients using various criteria
        Meditech supports: identifier, name, birthdate, gender, family, given
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/fhir/Patient"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
                "X-Facility-ID": self.facility_id,
            }

            response = await self.http_client.get(url, headers=headers, params=criteria)
            response.raise_for_status()

            bundle = response.json()
            patients = []

            if bundle.get("entry"):
                for entry in bundle["entry"]:
                    patient_data = entry.get("resource")
                    if patient_data:
                        patients.append(
                            {
                                "id": patient_data.get("id"),
                                "mrn": self._extract_identifier(patient_data, "MR"),
                                "name": self._format_name(
                                    patient_data.get("name", [{}])[0]
                                ),
                                "gender": patient_data.get("gender"),
                                "birth_date": patient_data.get("birthDate"),
                            }
                        )

            return patients

        except Exception as e:
            logger.error(f"Patient search failed: {e}")
            return []

    async def get_admissions(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient admissions (ADT data)
        Meditech-specific admission tracking
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/fhir/Encounter"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
                "X-Facility-ID": self.facility_id,
            }

            params = {"patient": patient_id, "class": "inpatient"}

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()

            bundle = response.json()
            admissions = []

            if bundle.get("entry"):
                for entry in bundle["entry"]:
                    encounter = entry.get("resource")
                    if encounter:
                        admissions.append(
                            {
                                "id": encounter.get("id"),
                                "status": encounter.get("status"),
                                "class": encounter.get("class", {}).get("code"),
                                "type": self._extract_encounter_type(encounter),
                                "admission_date": self._extract_period_start(encounter),
                                "discharge_date": self._extract_period_end(encounter),
                                "location": self._extract_location(encounter),
                                "attending_physician": self._extract_practitioner(
                                    encounter, "ATND"
                                ),
                                "admitting_physician": self._extract_practitioner(
                                    encounter, "ADM"
                                ),
                                "discharge_disposition": self._extract_discharge_disposition(
                                    encounter
                                ),
                            }
                        )

            return admissions

        except Exception as e:
            logger.error(f"Failed to retrieve admissions for patient {patient_id}: {e}")
            return []

    async def get_lab_results(
        self, patient_id: str, date_from: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve patient lab results
        Meditech lab interface
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/fhir/Observation"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
                "X-Facility-ID": self.facility_id,
            }

            params = {"patient": patient_id, "category": "laboratory"}

            if date_from:
                params["date"] = f"ge{date_from}"

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()

            bundle = response.json()
            lab_results = []

            if bundle.get("entry"):
                for entry in bundle["entry"]:
                    observation = entry.get("resource")
                    if observation:
                        lab_results.append(
                            {
                                "id": observation.get("id"),
                                "test_name": self._extract_code_display(
                                    observation.get("code")
                                ),
                                "test_code": self._extract_code_value(
                                    observation.get("code")
                                ),
                                "value": self._extract_observation_value(observation),
                                "unit": self._extract_observation_unit(observation),
                                "reference_range": self._extract_reference_range(
                                    observation
                                ),
                                "abnormal_flag": self._extract_abnormal_flag(
                                    observation
                                ),
                                "status": observation.get("status"),
                                "date": observation.get("effectiveDateTime"),
                                "performer": self._extract_performer(observation),
                            }
                        )

            return lab_results

        except Exception as e:
            logger.error(
                f"Failed to retrieve lab results for patient {patient_id}: {e}"
            )
            return []

    async def get_medications(self, patient_id: str) -> List[Dict]:
        """
        Retrieve patient medications
        Meditech pharmacy interface
        """
        await self._ensure_authenticated()

        try:
            url = f"{self.base_url}/api/fhir/MedicationRequest"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/fhir+json",
                "X-Facility-ID": self.facility_id,
            }

            params = {"patient": patient_id}

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()

            bundle = response.json()
            medications = []

            if bundle.get("entry"):
                for entry in bundle["entry"]:
                    med_request = entry.get("resource")
                    if med_request:
                        medications.append(
                            {
                                "id": med_request.get("id"),
                                "medication": self._extract_medication_name(
                                    med_request
                                ),
                                "dosage": self._extract_dosage_instruction(med_request),
                                "route": self._extract_route(med_request),
                                "frequency": self._extract_frequency(med_request),
                                "status": med_request.get("status"),
                                "intent": med_request.get("intent"),
                                "start_date": med_request.get("authoredOn"),
                                "prescriber": self._extract_requester(med_request),
                            }
                        )

            return medications

        except Exception as e:
            logger.error(
                f"Failed to retrieve medications for patient {patient_id}: {e}"
            )
            return []

    async def send_hl7_adt(self, message_type: str, patient_data: Dict) -> bool:
        """
        Send HL7 ADT message to Meditech
        Message types: A01 (Admit), A02 (Transfer), A03 (Discharge), A08 (Update)
        """
        try:
            # Build HL7 v2.x ADT message
            from ..core.hl7_parser import HL7Parser

            parser = HL7Parser()
            hl7_message = parser.build_adt_message(message_type, patient_data)

            # Send via TCP/IP to Meditech HL7 interface
            reader, writer = await asyncio.open_connection(self.hl7_host, self.hl7_port)

            # Wrap message with MLLP framing
            mllp_message = f"\x0b{hl7_message}\x1c\x0d".encode("utf-8")

            writer.write(mllp_message)
            await writer.drain()

            # Wait for ACK
            response = await reader.read(1024)

            writer.close()
            await writer.wait_closed()

            # Parse ACK
            ack_message = response.decode("utf-8").strip("\x0b\x1c\x0d")

            if "MSA|AA" in ack_message:
                logger.info(f"HL7 ADT {message_type} sent successfully")
                return True
            else:
                logger.error(f"HL7 ADT {message_type} rejected: {ack_message}")
                return False

        except Exception as e:
            logger.error(f"Failed to send HL7 ADT message: {e}")
            return False

    # Helper methods

    def _extract_identifier(self, patient_data: Dict, id_type: str) -> Optional[str]:
        """Extract specific identifier type"""
        identifiers = patient_data.get("identifier", [])
        for identifier in identifiers:
            if identifier.get("type", {}).get("coding", [{}])[0].get("code") == id_type:
                return identifier.get("value")
        return None

    def _format_name(self, name: Dict) -> Optional[str]:
        """Format patient name"""
        if not name:
            return None
        parts = []
        if name.get("given"):
            parts.extend(name["given"])
        if name.get("family"):
            parts.append(name["family"])
        return " ".join(parts) if parts else None

    def _extract_telecom(self, patient_data: Dict, system: str) -> Optional[str]:
        """Extract telecom value"""
        telecoms = patient_data.get("telecom", [])
        for telecom in telecoms:
            if telecom.get("system") == system:
                return telecom.get("value")
        return None

    def _format_address(self, address: Dict) -> Optional[Dict]:
        """Format patient address"""
        if not address:
            return None
        return {
            "line": address.get("line", []),
            "city": address.get("city"),
            "state": address.get("state"),
            "postal_code": address.get("postalCode"),
            "country": address.get("country"),
        }

    def _extract_emergency_contact(self, patient_data: Dict) -> Optional[Dict]:
        """Extract emergency contact information"""
        contacts = patient_data.get("contact", [])
        for contact in contacts:
            relationships = contact.get("relationship", [])
            for rel in relationships:
                if rel.get("coding", [{}])[0].get("code") == "C":
                    return {
                        "name": self._format_name(contact.get("name", {})),
                        "phone": self._extract_telecom(
                            {"telecom": contact.get("telecom", [])}, "phone"
                        ),
                        "relationship": rel.get("coding", [{}])[0].get("display"),
                    }
        return None

    def _extract_encounter_type(self, encounter: Dict) -> Optional[str]:
        """Extract encounter type"""
        types = encounter.get("type", [])
        if types:
            return types[0].get("coding", [{}])[0].get("display")
        return None

    def _extract_period_start(self, encounter: Dict) -> Optional[str]:
        """Extract encounter start date"""
        period = encounter.get("period", {})
        return period.get("start")

    def _extract_period_end(self, encounter: Dict) -> Optional[str]:
        """Extract encounter end date"""
        period = encounter.get("period", {})
        return period.get("end")

    def _extract_location(self, encounter: Dict) -> Optional[str]:
        """Extract encounter location"""
        locations = encounter.get("location", [])
        if locations:
            return locations[0].get("location", {}).get("display")
        return None

    def _extract_practitioner(self, encounter: Dict, role_code: str) -> Optional[str]:
        """Extract practitioner by role"""
        participants = encounter.get("participant", [])
        for participant in participants:
            types = participant.get("type", [])
            for type_concept in types:
                if type_concept.get("coding", [{}])[0].get("code") == role_code:
                    return participant.get("individual", {}).get("display")
        return None

    def _extract_discharge_disposition(self, encounter: Dict) -> Optional[str]:
        """Extract discharge disposition"""
        hospitalization = encounter.get("hospitalization", {})
        discharge_disp = hospitalization.get("dischargeDisposition", {})
        return discharge_disp.get("coding", [{}])[0].get("display")

    def _extract_code_display(self, code: Dict) -> Optional[str]:
        """Extract code display"""
        if code and code.get("coding"):
            return code["coding"][0].get("display")
        return None

    def _extract_code_value(self, code: Dict) -> Optional[str]:
        """Extract code value"""
        if code and code.get("coding"):
            return code["coding"][0].get("code")
        return None

    def _extract_observation_value(self, observation: Dict) -> Optional[Any]:
        """Extract observation value"""
        if "valueQuantity" in observation:
            return observation["valueQuantity"].get("value")
        elif "valueString" in observation:
            return observation["valueString"]
        elif "valueCodeableConcept" in observation:
            return self._extract_code_display(observation["valueCodeableConcept"])
        return None

    def _extract_observation_unit(self, observation: Dict) -> Optional[str]:
        """Extract observation unit"""
        if "valueQuantity" in observation:
            return observation["valueQuantity"].get("unit")
        return None

    def _extract_reference_range(self, observation: Dict) -> Optional[str]:
        """Extract reference range"""
        ref_ranges = observation.get("referenceRange", [])
        if ref_ranges:
            ref_range = ref_ranges[0]
            low = ref_range.get("low", {}).get("value")
            high = ref_range.get("high", {}).get("value")
            if low and high:
                return f"{low}-{high}"
        return None

    def _extract_abnormal_flag(self, observation: Dict) -> Optional[str]:
        """Extract abnormal flag"""
        interpretations = observation.get("interpretation", [])
        if interpretations:
            return interpretations[0].get("coding", [{}])[0].get("code")
        return None

    def _extract_performer(self, observation: Dict) -> Optional[str]:
        """Extract performer"""
        performers = observation.get("performer", [])
        if performers:
            return performers[0].get("display")
        return None

    def _extract_medication_name(self, med_request: Dict) -> Optional[str]:
        """Extract medication name"""
        med_concept = med_request.get("medicationCodeableConcept", {})
        return self._extract_code_display(med_concept)

    def _extract_dosage_instruction(self, med_request: Dict) -> Optional[str]:
        """Extract dosage instruction"""
        dosages = med_request.get("dosageInstruction", [])
        if dosages:
            return dosages[0].get("text")
        return None

    def _extract_route(self, med_request: Dict) -> Optional[str]:
        """Extract route"""
        dosages = med_request.get("dosageInstruction", [])
        if dosages:
            route = dosages[0].get("route", {})
            return self._extract_code_display(route)
        return None

    def _extract_frequency(self, med_request: Dict) -> Optional[str]:
        """Extract frequency"""
        dosages = med_request.get("dosageInstruction", [])
        if dosages:
            timing = dosages[0].get("timing", {})
            repeat = timing.get("repeat", {})
            frequency = repeat.get("frequency")
            period = repeat.get("period")
            period_unit = repeat.get("periodUnit")
            if frequency and period and period_unit:
                return f"{frequency} times per {period} {period_unit}"
        return None

    def _extract_requester(self, med_request: Dict) -> Optional[str]:
        """Extract requester"""
        requester = med_request.get("requester", {})
        return requester.get("display")

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
