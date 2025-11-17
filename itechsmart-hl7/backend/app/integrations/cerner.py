"""
Cerner (Oracle Health) Integration
Supports Cerner Millennium APIs and HL7 v2.x interfaces
"""

import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import base64

logger = logging.getLogger(__name__)


class CernerIntegration:
    """
    Cerner (Oracle Health) EMR Integration
    Supports Cerner Millennium APIs, FHIR R4, and HL7 v2.x
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Cerner integration

        Args:
            config: Configuration dictionary containing:
                - base_url: Cerner FHIR base URL
                - client_id: OAuth client ID
                - client_secret: OAuth client secret
                - tenant_id: Cerner tenant ID
                - hl7_host: HL7 interface host
                - hl7_port: HL7 interface port
        """
        self.config = config
        self.base_url = config.get("base_url", "").rstrip("/")
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.tenant_id = config.get("tenant_id")
        self.hl7_host = config.get("hl7_host")
        self.hl7_port = config.get("hl7_port", 6661)

        self.access_token = None
        self.token_expiry = None

        # Cerner-specific endpoints
        self.endpoints = {
            "token": f"{self.base_url}/tenants/{self.tenant_id}/protocols/oauth2/profiles/smart-v1/token",
            "patient": f"{self.base_url}/Patient",
            "observation": f"{self.base_url}/Observation",
            "condition": f"{self.base_url}/Condition",
            "medication": f"{self.base_url}/MedicationRequest",
            "appointment": f"{self.base_url}/Appointment",
            "encounter": f"{self.base_url}/Encounter",
            "procedure": f"{self.base_url}/Procedure",
            "diagnostic_report": f"{self.base_url}/DiagnosticReport",
            "document_reference": f"{self.base_url}/DocumentReference",
            "allergy": f"{self.base_url}/AllergyIntolerance",
            "immunization": f"{self.base_url}/Immunization",
        }

    async def authenticate(self) -> bool:
        """
        Authenticate with Cerner using OAuth 2.0

        Returns:
            True if authentication successful
        """
        try:
            async with httpx.AsyncClient() as client:
                # Client credentials flow
                auth_string = f"{self.client_id}:{self.client_secret}"
                auth_bytes = auth_string.encode("ascii")
                auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

                response = await client.post(
                    self.endpoints["token"],
                    headers={
                        "Authorization": f"Basic {auth_b64}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "grant_type": "client_credentials",
                        "scope": "system/Patient.read system/Observation.read system/Condition.read system/MedicationRequest.read",
                    },
                )

                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expiry = datetime.utcnow().timestamp() + expires_in

                    logger.info("Cerner authentication successful")
                    return True
                else:
                    logger.error(
                        f"Cerner authentication failed: {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error authenticating with Cerner: {str(e)}")
            return False

    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or (
            self.token_expiry and datetime.utcnow().timestamp() >= self.token_expiry
        ):
            await self.authenticate()

    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make authenticated request to Cerner API"""
        await self._ensure_authenticated()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Accept"] = "application/fhir+json"

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            return response

    # Patient Operations

    async def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Get patient by ID"""
        try:
            response = await self._make_request(
                "GET", f"{self.endpoints['patient']}/{patient_id}"
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Error getting patient: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Error getting patient from Cerner: {str(e)}")
            return None

    async def search_patients(self, **search_params) -> List[Dict]:
        """Search for patients"""
        try:
            response = await self._make_request(
                "GET", self.endpoints["patient"], params=search_params
            )

            if response.status_code == 200:
                bundle = response.json()
                return bundle.get("entry", [])
            else:
                logger.error(
                    f"Error searching patients: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Error searching patients in Cerner: {str(e)}")
            return []

    # Observation Operations

    async def get_observations(
        self, patient_id: str, category: Optional[str] = None
    ) -> List[Dict]:
        """Get patient observations"""
        try:
            params = {"patient": patient_id}
            if category:
                params["category"] = category

            response = await self._make_request(
                "GET", self.endpoints["observation"], params=params
            )

            if response.status_code == 200:
                bundle = response.json()
                return bundle.get("entry", [])
            else:
                logger.error(
                    f"Error getting observations: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Error getting observations from Cerner: {str(e)}")
            return []

    async def get_vital_signs(self, patient_id: str) -> List[Dict]:
        """Get patient vital signs"""
        return await self.get_observations(patient_id, category="vital-signs")

    async def get_lab_results(self, patient_id: str) -> List[Dict]:
        """Get patient lab results"""
        return await self.get_observations(patient_id, category="laboratory")

    # Condition Operations

    async def get_conditions(self, patient_id: str) -> List[Dict]:
        """Get patient conditions/diagnoses"""
        try:
            response = await self._make_request(
                "GET", self.endpoints["condition"], params={"patient": patient_id}
            )

            if response.status_code == 200:
                bundle = response.json()
                return bundle.get("entry", [])
            else:
                logger.error(
                    f"Error getting conditions: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Error getting conditions from Cerner: {str(e)}")
            return []

    # Medication Operations

    async def get_medications(
        self, patient_id: str, status: Optional[str] = None
    ) -> List[Dict]:
        """Get patient medications"""
        try:
            params = {"patient": patient_id}
            if status:
                params["status"] = status

            response = await self._make_request(
                "GET", self.endpoints["medication"], params=params
            )

            if response.status_code == 200:
                bundle = response.json()
                return bundle.get("entry", [])
            else:
                logger.error(
                    f"Error getting medications: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Error getting medications from Cerner: {str(e)}")
            return []

    async def get_active_medications(self, patient_id: str) -> List[Dict]:
        """Get patient's active medications"""
        return await self.get_medications(patient_id, status="active")

    # Allergy Operations

    async def get_allergies(self, patient_id: str) -> List[Dict]:
        """Get patient allergies"""
        try:
            response = await self._make_request(
                "GET", self.endpoints["allergy"], params={"patient": patient_id}
            )

            if response.status_code == 200:
                bundle = response.json()
                return bundle.get("entry", [])
            else:
                logger.error(
                    f"Error getting allergies: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Error getting allergies from Cerner: {str(e)}")
            return []

    # Immunization Operations

    async def get_immunizations(self, patient_id: str) -> List[Dict]:
        """Get patient immunizations"""
        try:
            response = await self._make_request(
                "GET", self.endpoints["immunization"], params={"patient": patient_id}
            )

            if response.status_code == 200:
                bundle = response.json()
                return bundle.get("entry", [])
            else:
                logger.error(
                    f"Error getting immunizations: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Error getting immunizations from Cerner: {str(e)}")
            return []

    # Encounter Operations

    async def get_encounters(self, patient_id: str) -> List[Dict]:
        """Get patient encounters"""
        try:
            response = await self._make_request(
                "GET", self.endpoints["encounter"], params={"patient": patient_id}
            )

            if response.status_code == 200:
                bundle = response.json()
                return bundle.get("entry", [])
            else:
                logger.error(
                    f"Error getting encounters: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Error getting encounters from Cerner: {str(e)}")
            return []

    # Document Operations

    async def get_clinical_notes(self, patient_id: str) -> List[Dict]:
        """Get patient clinical notes"""
        try:
            response = await self._make_request(
                "GET",
                self.endpoints["document_reference"],
                params={"patient": patient_id},
            )

            if response.status_code == 200:
                bundle = response.json()
                return bundle.get("entry", [])
            else:
                logger.error(
                    f"Error getting clinical notes: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Error getting clinical notes from Cerner: {str(e)}")
            return []

    # Comprehensive Patient Summary

    async def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive patient summary

        Args:
            patient_id: Patient ID

        Returns:
            Complete patient summary with all clinical data
        """
        summary = {
            "patient": None,
            "demographics": {},
            "vital_signs": [],
            "lab_results": [],
            "conditions": [],
            "medications": [],
            "allergies": [],
            "immunizations": [],
            "encounters": [],
            "clinical_notes": [],
        }

        try:
            # Get patient demographics
            patient = await self.get_patient(patient_id)
            if patient:
                summary["patient"] = patient
                summary["demographics"] = self._extract_demographics(patient)

            # Get vital signs
            summary["vital_signs"] = await self.get_vital_signs(patient_id)

            # Get lab results
            summary["lab_results"] = await self.get_lab_results(patient_id)

            # Get conditions
            summary["conditions"] = await self.get_conditions(patient_id)

            # Get medications
            summary["medications"] = await self.get_active_medications(patient_id)

            # Get allergies
            summary["allergies"] = await self.get_allergies(patient_id)

            # Get immunizations
            summary["immunizations"] = await self.get_immunizations(patient_id)

            # Get encounters
            summary["encounters"] = await self.get_encounters(patient_id)

            # Get clinical notes
            summary["clinical_notes"] = await self.get_clinical_notes(patient_id)

            return summary

        except Exception as e:
            logger.error(f"Error getting patient summary: {str(e)}")
            return summary

    def _extract_demographics(self, patient: Dict) -> Dict[str, Any]:
        """Extract demographics from patient resource"""
        demographics = {}

        try:
            # Name
            if patient.get("name"):
                name = patient["name"][0]
                demographics["name"] = {
                    "family": name.get("family", ""),
                    "given": name.get("given", []),
                    "full": f"{' '.join(name.get('given', []))} {name.get('family', '')}",
                }

            # Gender
            demographics["gender"] = patient.get("gender", "")

            # Birth date
            demographics["birth_date"] = patient.get("birthDate", "")

            # Address
            if patient.get("address"):
                address = patient["address"][0]
                demographics["address"] = {
                    "line": address.get("line", []),
                    "city": address.get("city", ""),
                    "state": address.get("state", ""),
                    "postal_code": address.get("postalCode", ""),
                    "country": address.get("country", ""),
                }

            # Phone
            if patient.get("telecom"):
                phones = [t for t in patient["telecom"] if t.get("system") == "phone"]
                if phones:
                    demographics["phone"] = phones[0].get("value", "")

            # MRN
            if patient.get("identifier"):
                mrns = [
                    i
                    for i in patient["identifier"]
                    if i.get("type", {}).get("text") == "MRN"
                ]
                if mrns:
                    demographics["mrn"] = mrns[0].get("value", "")

        except Exception as e:
            logger.error(f"Error extracting demographics: {str(e)}")

        return demographics

    # HL7 Interface Operations

    async def send_hl7_message(self, message: str) -> Optional[str]:
        """Send HL7 v2.x message to Cerner interface"""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.hl7_host, self.hl7_port))

            # Send with MLLP framing
            mllp_message = f"\x0b{message}\x1c\x0d"
            sock.sendall(mllp_message.encode("utf-8"))

            # Receive ACK
            ack = sock.recv(4096).decode("utf-8")
            sock.close()

            ack = ack.strip("\x0b\x1c\x0d")

            logger.info("HL7 message sent successfully to Cerner")
            return ack

        except Exception as e:
            logger.error(f"Error sending HL7 message to Cerner: {str(e)}")
            return None

    # Utility Methods

    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Cerner"""
        results = {
            "fhir_api": False,
            "hl7_interface": False,
            "authentication": False,
            "errors": [],
        }

        # Test authentication
        try:
            auth_success = await self.authenticate()
            results["authentication"] = auth_success
            if not auth_success:
                results["errors"].append("Authentication failed")
        except Exception as e:
            results["errors"].append(f"Authentication error: {str(e)}")

        # Test FHIR API
        try:
            response = await self._make_request("GET", f"{self.base_url}/metadata")
            results["fhir_api"] = response.status_code == 200
            if response.status_code != 200:
                results["errors"].append(f"FHIR API error: {response.status_code}")
        except Exception as e:
            results["errors"].append(f"FHIR API error: {str(e)}")

        # Test HL7 interface
        if self.hl7_host:
            try:
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.hl7_host, self.hl7_port))
                sock.close()
                results["hl7_interface"] = True
            except Exception as e:
                results["errors"].append(f"HL7 interface error: {str(e)}")

        return results


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        config = {
            "base_url": "https://fhir-myrecord.cerner.com/r4/tenant-id",
            "client_id": "your-client-id",
            "client_secret": "your-client-secret",
            "tenant_id": "your-tenant-id",
            "hl7_host": "hl7.cerner.hospital.org",
            "hl7_port": 6661,
        }

        cerner = CernerIntegration(config)

        # Test connection
        test_results = await cerner.test_connection()
        print(f"Connection test: {json.dumps(test_results, indent=2)}")

        # Get patient summary
        summary = await cerner.get_patient_summary("patient-id")
        print(f"Patient summary: {json.dumps(summary, indent=2)}")

    asyncio.run(main())
