"""
Meditech Integration
Supports Meditech MAGIC, Expanse, and HL7 v2.x interfaces
"""

import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import socket

logger = logging.getLogger(__name__)


class MeditechIntegration:
    """
    Meditech EMR Integration
    Supports Meditech MAGIC, Expanse, FHIR, and HL7 v2.x
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Meditech integration

        Args:
            config: Configuration dictionary containing:
                - base_url: Meditech API base URL (for Expanse)
                - api_key: API key for authentication
                - hl7_host: HL7 interface host
                - hl7_port: HL7 interface port
                - facility_id: Meditech facility ID
                - version: Meditech version (MAGIC, Expanse)
        """
        self.config = config
        self.base_url = config.get("base_url", "").rstrip("/")
        self.api_key = config.get("api_key")
        self.hl7_host = config.get("hl7_host")
        self.hl7_port = config.get("hl7_port", 6661)
        self.facility_id = config.get("facility_id")
        self.version = config.get("version", "MAGIC")

        # Meditech-specific endpoints (for Expanse)
        if self.version == "Expanse":
            self.endpoints = {
                "patient": f"{self.base_url}/api/patient",
                "admission": f"{self.base_url}/api/admission",
                "order": f"{self.base_url}/api/order",
                "result": f"{self.base_url}/api/result",
                "medication": f"{self.base_url}/api/medication",
                "document": f"{self.base_url}/api/document",
            }

    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make authenticated request to Meditech API"""
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.api_key}"
        headers["Accept"] = "application/json"

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            return response

    # Patient Operations

    async def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Get patient by ID"""
        if self.version == "Expanse":
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
                logger.error(f"Error getting patient from Meditech: {str(e)}")
                return None
        else:
            # For MAGIC, use HL7 QRY message
            return await self._query_patient_hl7(patient_id)

    async def search_patients(self, **search_params) -> List[Dict]:
        """Search for patients"""
        if self.version == "Expanse":
            try:
                response = await self._make_request(
                    "GET", self.endpoints["patient"], params=search_params
                )

                if response.status_code == 200:
                    return response.json().get("patients", [])
                else:
                    logger.error(
                        f"Error searching patients: {response.status_code} - {response.text}"
                    )
                    return []

            except Exception as e:
                logger.error(f"Error searching patients in Meditech: {str(e)}")
                return []
        else:
            return []

    # Admission Operations

    async def get_admissions(self, patient_id: str) -> List[Dict]:
        """Get patient admissions"""
        if self.version == "Expanse":
            try:
                response = await self._make_request(
                    "GET",
                    self.endpoints["admission"],
                    params={"patient_id": patient_id},
                )

                if response.status_code == 200:
                    return response.json().get("admissions", [])
                else:
                    logger.error(
                        f"Error getting admissions: {response.status_code} - {response.text}"
                    )
                    return []

            except Exception as e:
                logger.error(f"Error getting admissions from Meditech: {str(e)}")
                return []
        else:
            return []

    # Order Operations

    async def get_orders(self, patient_id: str) -> List[Dict]:
        """Get patient orders"""
        if self.version == "Expanse":
            try:
                response = await self._make_request(
                    "GET", self.endpoints["order"], params={"patient_id": patient_id}
                )

                if response.status_code == 200:
                    return response.json().get("orders", [])
                else:
                    logger.error(
                        f"Error getting orders: {response.status_code} - {response.text}"
                    )
                    return []

            except Exception as e:
                logger.error(f"Error getting orders from Meditech: {str(e)}")
                return []
        else:
            return []

    async def create_order(self, order_data: Dict) -> Optional[Dict]:
        """Create new order"""
        if self.version == "Expanse":
            try:
                response = await self._make_request(
                    "POST", self.endpoints["order"], json=order_data
                )

                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(
                        f"Error creating order: {response.status_code} - {response.text}"
                    )
                    return None

            except Exception as e:
                logger.error(f"Error creating order in Meditech: {str(e)}")
                return None
        else:
            # For MAGIC, use HL7 ORM message
            return await self._send_order_hl7(order_data)

    # Result Operations

    async def get_results(
        self, patient_id: str, result_type: Optional[str] = None
    ) -> List[Dict]:
        """Get patient results (lab, radiology, etc.)"""
        if self.version == "Expanse":
            try:
                params = {"patient_id": patient_id}
                if result_type:
                    params["type"] = result_type

                response = await self._make_request(
                    "GET", self.endpoints["result"], params=params
                )

                if response.status_code == 200:
                    return response.json().get("results", [])
                else:
                    logger.error(
                        f"Error getting results: {response.status_code} - {response.text}"
                    )
                    return []

            except Exception as e:
                logger.error(f"Error getting results from Meditech: {str(e)}")
                return []
        else:
            return []

    async def get_lab_results(self, patient_id: str) -> List[Dict]:
        """Get patient lab results"""
        return await self.get_results(patient_id, result_type="laboratory")

    async def get_radiology_results(self, patient_id: str) -> List[Dict]:
        """Get patient radiology results"""
        return await self.get_results(patient_id, result_type="radiology")

    # Medication Operations

    async def get_medications(self, patient_id: str) -> List[Dict]:
        """Get patient medications"""
        if self.version == "Expanse":
            try:
                response = await self._make_request(
                    "GET",
                    self.endpoints["medication"],
                    params={"patient_id": patient_id},
                )

                if response.status_code == 200:
                    return response.json().get("medications", [])
                else:
                    logger.error(
                        f"Error getting medications: {response.status_code} - {response.text}"
                    )
                    return []

            except Exception as e:
                logger.error(f"Error getting medications from Meditech: {str(e)}")
                return []
        else:
            return []

    # Document Operations

    async def get_documents(self, patient_id: str) -> List[Dict]:
        """Get patient documents"""
        if self.version == "Expanse":
            try:
                response = await self._make_request(
                    "GET", self.endpoints["document"], params={"patient_id": patient_id}
                )

                if response.status_code == 200:
                    return response.json().get("documents", [])
                else:
                    logger.error(
                        f"Error getting documents: {response.status_code} - {response.text}"
                    )
                    return []

            except Exception as e:
                logger.error(f"Error getting documents from Meditech: {str(e)}")
                return []
        else:
            return []

    # HL7 Interface Operations (Primary for MAGIC)

    async def send_hl7_message(self, message: str) -> Optional[str]:
        """Send HL7 v2.x message to Meditech interface"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.hl7_host, self.hl7_port))

            # Send with MLLP framing
            mllp_message = f"\x0b{message}\x1c\x0d"
            sock.sendall(mllp_message.encode("utf-8"))

            # Receive ACK
            ack = sock.recv(4096).decode("utf-8")
            sock.close()

            ack = ack.strip("\x0b\x1c\x0d")

            logger.info("HL7 message sent successfully to Meditech")
            return ack

        except Exception as e:
            logger.error(f"Error sending HL7 message to Meditech: {str(e)}")
            return None

    async def _query_patient_hl7(self, patient_id: str) -> Optional[Dict]:
        """Query patient using HL7 QRY message"""
        qry_message = f"""MSH|^~\\&|ITECHSMART|FACILITY|MEDITECH|{self.facility_id}|{datetime.utcnow().strftime('%Y%m%d%H%M%S')}||QRY^A19|{datetime.utcnow().timestamp()}|P|2.5
QRD|{datetime.utcnow().strftime('%Y%m%d%H%M%S')}|R|I|{patient_id}|||RD|{patient_id}|DEM||"""

        ack = await self.send_hl7_message(qry_message)

        if ack and "AA" in ack:
            # Parse response (would need full HL7 parser)
            return {"success": True, "ack": ack}
        return None

    async def _send_order_hl7(self, order_data: Dict) -> Optional[Dict]:
        """Send order using HL7 ORM message"""
        patient_id = order_data.get("patient_id")
        order_type = order_data.get("order_type")

        orm_message = f"""MSH|^~\\&|ITECHSMART|FACILITY|MEDITECH|{self.facility_id}|{datetime.utcnow().strftime('%Y%m%d%H%M%S')}||ORM^O01|{datetime.utcnow().timestamp()}|P|2.5
PID|1||{patient_id}
ORC|NW|{datetime.utcnow().timestamp()}||||||{datetime.utcnow().strftime('%Y%m%d%H%M%S')}
OBR|1||{datetime.utcnow().timestamp()}|{order_type}"""

        ack = await self.send_hl7_message(orm_message)

        if ack and "AA" in ack:
            return {"success": True, "ack": ack}
        return None

    async def send_adt_message(
        self, event_type: str, patient_data: Dict
    ) -> Optional[str]:
        """
        Send ADT (Admit/Discharge/Transfer) message

        Args:
            event_type: ADT event (A01=Admit, A03=Discharge, A08=Update)
            patient_data: Patient information
        """
        patient_id = patient_data.get("patient_id")
        patient_name = patient_data.get("name", "DOE^JOHN")

        adt_message = f"""MSH|^~\\&|ITECHSMART|FACILITY|MEDITECH|{self.facility_id}|{datetime.utcnow().strftime('%Y%m%d%H%M%S')}||ADT^{event_type}|{datetime.utcnow().timestamp()}|P|2.5
EVN|{event_type}|{datetime.utcnow().strftime('%Y%m%d%H%M%S')}
PID|1||{patient_id}||{patient_name}"""

        return await self.send_hl7_message(adt_message)

    async def send_result_message(self, result_data: Dict) -> Optional[str]:
        """
        Send ORU (Observation Result) message

        Args:
            result_data: Result information
        """
        patient_id = result_data.get("patient_id")
        observation_id = result_data.get("observation_id")
        observation_value = result_data.get("value")

        oru_message = f"""MSH|^~\\&|ITECHSMART|FACILITY|MEDITECH|{self.facility_id}|{datetime.utcnow().strftime('%Y%m%d%H%M%S')}||ORU^R01|{datetime.utcnow().timestamp()}|P|2.5
PID|1||{patient_id}
OBR|1||{datetime.utcnow().timestamp()}|{observation_id}
OBX|1|ST|{observation_id}||{observation_value}"""

        return await self.send_hl7_message(oru_message)

    # Utility Methods

    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Meditech"""
        results = {
            "api": False,
            "hl7_interface": False,
            "version": self.version,
            "errors": [],
        }

        # Test API (for Expanse)
        if self.version == "Expanse" and self.base_url:
            try:
                response = await self._make_request(
                    "GET", f"{self.base_url}/api/health"
                )
                results["api"] = response.status_code == 200
                if response.status_code != 200:
                    results["errors"].append(f"API error: {response.status_code}")
            except Exception as e:
                results["errors"].append(f"API error: {str(e)}")

        # Test HL7 interface
        if self.hl7_host:
            try:
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
        # MAGIC configuration (HL7 only)
        magic_config = {
            "hl7_host": "hl7.meditech.hospital.org",
            "hl7_port": 6661,
            "facility_id": "HOSPITAL01",
            "version": "MAGIC",
        }

        # Expanse configuration (API + HL7)
        expanse_config = {
            "base_url": "https://api.meditech.hospital.org",
            "api_key": "your-api-key",
            "hl7_host": "hl7.meditech.hospital.org",
            "hl7_port": 6661,
            "facility_id": "HOSPITAL01",
            "version": "Expanse",
        }

        meditech = MeditechIntegration(magic_config)

        # Test connection
        test_results = await meditech.test_connection()
        print(f"Connection test: {json.dumps(test_results, indent=2)}")

        # Send ADT message
        adt_ack = await meditech.send_adt_message(
            "A01", {"patient_id": "123456", "name": "DOE^JOHN^A"}
        )
        print(f"ADT ACK: {adt_ack}")

    asyncio.run(main())
