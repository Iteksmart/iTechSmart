"""
HL7 Message Parser
Supports HL7 v2.x, v3, and FHIR message parsing
"""

import hl7
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation

logger = logging.getLogger(__name__)


class HL7Parser:
    """
    Comprehensive HL7 message parser supporting multiple versions
    """

    def __init__(self):
        self.supported_versions = [
            "2.1",
            "2.2",
            "2.3",
            "2.4",
            "2.5",
            "2.6",
            "2.7",
            "2.8",
        ]
        self.message_types = {
            "ADT": "Admit/Discharge/Transfer",
            "ORM": "Order Message",
            "ORU": "Observation Result",
            "SIU": "Scheduling Information",
            "DFT": "Detailed Financial Transaction",
            "MDM": "Medical Document Management",
            "RDE": "Pharmacy/Treatment Encoded Order",
            "RAS": "Pharmacy/Treatment Administration",
            "BAR": "Add/Change Billing Account",
            "DG1": "Diagnosis",
        }

    def parse_hl7_v2(self, message: str) -> Dict[str, Any]:
        """
        Parse HL7 v2.x message

        Args:
            message: Raw HL7 v2.x message string

        Returns:
            Parsed message dictionary
        """
        try:
            # Parse message
            parsed = hl7.parse(message)

            # Extract MSH (Message Header)
            msh = parsed.segment("MSH")

            result = {
                "version": "v2.x",
                "message_type": self._get_message_type(msh),
                "message_control_id": str(msh[10]) if len(msh) > 10 else None,
                "timestamp": (
                    self._parse_hl7_datetime(str(msh[7])) if len(msh) > 7 else None
                ),
                "sending_application": str(msh[3]) if len(msh) > 3 else None,
                "sending_facility": str(msh[4]) if len(msh) > 4 else None,
                "receiving_application": str(msh[5]) if len(msh) > 5 else None,
                "receiving_facility": str(msh[6]) if len(msh) > 6 else None,
                "segments": {},
                "raw_message": message,
            }

            # Parse all segments
            for segment in parsed:
                segment_name = str(segment[0])

                if segment_name == "MSH":
                    continue  # Already parsed
                elif segment_name == "PID":
                    result["segments"]["patient"] = self._parse_pid(segment)
                elif segment_name == "PV1":
                    result["segments"]["visit"] = self._parse_pv1(segment)
                elif segment_name == "OBR":
                    result["segments"]["observation_request"] = self._parse_obr(segment)
                elif segment_name == "OBX":
                    if "observations" not in result["segments"]:
                        result["segments"]["observations"] = []
                    result["segments"]["observations"].append(self._parse_obx(segment))
                elif segment_name == "ORC":
                    result["segments"]["order_control"] = self._parse_orc(segment)
                elif segment_name == "DG1":
                    if "diagnoses" not in result["segments"]:
                        result["segments"]["diagnoses"] = []
                    result["segments"]["diagnoses"].append(self._parse_dg1(segment))
                else:
                    # Generic segment parsing
                    result["segments"][segment_name.lower()] = (
                        self._parse_generic_segment(segment)
                    )

            return result

        except Exception as e:
            logger.error(f"Error parsing HL7 v2 message: {str(e)}")
            raise ValueError(f"Invalid HL7 v2 message: {str(e)}")

    def parse_fhir(self, resource_json: str) -> Dict[str, Any]:
        """
        Parse FHIR resource (JSON)

        Args:
            resource_json: FHIR resource in JSON format

        Returns:
            Parsed resource dictionary
        """
        try:
            resource_dict = json.loads(resource_json)
            resource_type = resource_dict.get("resourceType")

            result = {
                "version": "FHIR",
                "resource_type": resource_type,
                "id": resource_dict.get("id"),
                "data": resource_dict,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Parse specific resource types
            if resource_type == "Patient":
                patient = Patient(**resource_dict)
                result["parsed"] = self._parse_fhir_patient(patient)
            elif resource_type == "Observation":
                observation = Observation(**resource_dict)
                result["parsed"] = self._parse_fhir_observation(observation)

            return result

        except Exception as e:
            logger.error(f"Error parsing FHIR resource: {str(e)}")
            raise ValueError(f"Invalid FHIR resource: {str(e)}")

    def _get_message_type(self, msh) -> str:
        """Extract message type from MSH segment"""
        try:
            msg_type = str(msh[9])
            if "^" in msg_type:
                return msg_type.split("^")[0]
            return msg_type
        except:
            return "UNKNOWN"

    def _parse_hl7_datetime(self, dt_string: str) -> Optional[str]:
        """Parse HL7 datetime format (YYYYMMDDHHMMSS)"""
        try:
            if len(dt_string) >= 8:
                year = dt_string[0:4]
                month = dt_string[4:6]
                day = dt_string[6:8]
                hour = dt_string[8:10] if len(dt_string) >= 10 else "00"
                minute = dt_string[10:12] if len(dt_string) >= 12 else "00"
                second = dt_string[12:14] if len(dt_string) >= 14 else "00"

                return f"{year}-{month}-{day}T{hour}:{minute}:{second}"
        except:
            pass
        return None

    def _parse_pid(self, segment) -> Dict[str, Any]:
        """Parse PID (Patient Identification) segment"""
        return {
            "patient_id": str(segment[3]) if len(segment) > 3 else None,
            "patient_name": (
                self._parse_name(str(segment[5])) if len(segment) > 5 else None
            ),
            "date_of_birth": (
                self._parse_hl7_datetime(str(segment[7])) if len(segment) > 7 else None
            ),
            "gender": str(segment[8]) if len(segment) > 8 else None,
            "race": str(segment[10]) if len(segment) > 10 else None,
            "address": (
                self._parse_address(str(segment[11])) if len(segment) > 11 else None
            ),
            "phone": str(segment[13]) if len(segment) > 13 else None,
            "marital_status": str(segment[16]) if len(segment) > 16 else None,
            "ssn": str(segment[19]) if len(segment) > 19 else None,
        }

    def _parse_pv1(self, segment) -> Dict[str, Any]:
        """Parse PV1 (Patient Visit) segment"""
        return {
            "patient_class": str(segment[2]) if len(segment) > 2 else None,
            "assigned_location": str(segment[3]) if len(segment) > 3 else None,
            "admission_type": str(segment[4]) if len(segment) > 4 else None,
            "attending_doctor": (
                self._parse_name(str(segment[7])) if len(segment) > 7 else None
            ),
            "referring_doctor": (
                self._parse_name(str(segment[8])) if len(segment) > 8 else None
            ),
            "hospital_service": str(segment[10]) if len(segment) > 10 else None,
            "admit_datetime": (
                self._parse_hl7_datetime(str(segment[44]))
                if len(segment) > 44
                else None
            ),
            "discharge_datetime": (
                self._parse_hl7_datetime(str(segment[45]))
                if len(segment) > 45
                else None
            ),
        }

    def _parse_obr(self, segment) -> Dict[str, Any]:
        """Parse OBR (Observation Request) segment"""
        return {
            "set_id": str(segment[1]) if len(segment) > 1 else None,
            "placer_order_number": str(segment[2]) if len(segment) > 2 else None,
            "filler_order_number": str(segment[3]) if len(segment) > 3 else None,
            "universal_service_id": str(segment[4]) if len(segment) > 4 else None,
            "observation_datetime": (
                self._parse_hl7_datetime(str(segment[7])) if len(segment) > 7 else None
            ),
            "ordering_provider": (
                self._parse_name(str(segment[16])) if len(segment) > 16 else None
            ),
            "result_status": str(segment[25]) if len(segment) > 25 else None,
        }

    def _parse_obx(self, segment) -> Dict[str, Any]:
        """Parse OBX (Observation Result) segment"""
        return {
            "set_id": str(segment[1]) if len(segment) > 1 else None,
            "value_type": str(segment[2]) if len(segment) > 2 else None,
            "observation_identifier": str(segment[3]) if len(segment) > 3 else None,
            "observation_sub_id": str(segment[4]) if len(segment) > 4 else None,
            "observation_value": str(segment[5]) if len(segment) > 5 else None,
            "units": str(segment[6]) if len(segment) > 6 else None,
            "reference_range": str(segment[7]) if len(segment) > 7 else None,
            "abnormal_flags": str(segment[8]) if len(segment) > 8 else None,
            "observation_result_status": (
                str(segment[11]) if len(segment) > 11 else None
            ),
            "observation_datetime": (
                self._parse_hl7_datetime(str(segment[14]))
                if len(segment) > 14
                else None
            ),
        }

    def _parse_orc(self, segment) -> Dict[str, Any]:
        """Parse ORC (Common Order) segment"""
        return {
            "order_control": str(segment[1]) if len(segment) > 1 else None,
            "placer_order_number": str(segment[2]) if len(segment) > 2 else None,
            "filler_order_number": str(segment[3]) if len(segment) > 3 else None,
            "order_status": str(segment[5]) if len(segment) > 5 else None,
            "transaction_datetime": (
                self._parse_hl7_datetime(str(segment[9])) if len(segment) > 9 else None
            ),
            "ordering_provider": (
                self._parse_name(str(segment[12])) if len(segment) > 12 else None
            ),
        }

    def _parse_dg1(self, segment) -> Dict[str, Any]:
        """Parse DG1 (Diagnosis) segment"""
        return {
            "set_id": str(segment[1]) if len(segment) > 1 else None,
            "diagnosis_coding_method": str(segment[2]) if len(segment) > 2 else None,
            "diagnosis_code": str(segment[3]) if len(segment) > 3 else None,
            "diagnosis_description": str(segment[4]) if len(segment) > 4 else None,
            "diagnosis_datetime": (
                self._parse_hl7_datetime(str(segment[5])) if len(segment) > 5 else None
            ),
            "diagnosis_type": str(segment[6]) if len(segment) > 6 else None,
        }

    def _parse_generic_segment(self, segment) -> List[str]:
        """Parse any segment generically"""
        return [str(field) for field in segment]

    def _parse_name(self, name_string: str) -> Dict[str, str]:
        """Parse HL7 name format (Last^First^Middle^Suffix^Prefix)"""
        parts = name_string.split("^")
        return {
            "family": parts[0] if len(parts) > 0 else "",
            "given": parts[1] if len(parts) > 1 else "",
            "middle": parts[2] if len(parts) > 2 else "",
            "suffix": parts[3] if len(parts) > 3 else "",
            "prefix": parts[4] if len(parts) > 4 else "",
        }

    def _parse_address(self, address_string: str) -> Dict[str, str]:
        """Parse HL7 address format"""
        parts = address_string.split("^")
        return {
            "street": parts[0] if len(parts) > 0 else "",
            "other": parts[1] if len(parts) > 1 else "",
            "city": parts[2] if len(parts) > 2 else "",
            "state": parts[3] if len(parts) > 3 else "",
            "zip": parts[4] if len(parts) > 4 else "",
            "country": parts[5] if len(parts) > 5 else "",
        }

    def _parse_fhir_patient(self, patient: Patient) -> Dict[str, Any]:
        """Parse FHIR Patient resource"""
        result = {
            "id": patient.id,
            "identifier": [],
            "name": [],
            "gender": patient.gender,
            "birth_date": str(patient.birthDate) if patient.birthDate else None,
            "address": [],
            "telecom": [],
        }

        # Parse identifiers
        if patient.identifier:
            for identifier in patient.identifier:
                result["identifier"].append(
                    {"system": identifier.system, "value": identifier.value}
                )

        # Parse names
        if patient.name:
            for name in patient.name:
                result["name"].append(
                    {"family": name.family, "given": name.given, "use": name.use}
                )

        # Parse addresses
        if patient.address:
            for address in patient.address:
                result["address"].append(
                    {
                        "line": address.line,
                        "city": address.city,
                        "state": address.state,
                        "postal_code": address.postalCode,
                        "country": address.country,
                    }
                )

        # Parse telecom
        if patient.telecom:
            for telecom in patient.telecom:
                result["telecom"].append(
                    {
                        "system": telecom.system,
                        "value": telecom.value,
                        "use": telecom.use,
                    }
                )

        return result

    def _parse_fhir_observation(self, observation: Observation) -> Dict[str, Any]:
        """Parse FHIR Observation resource"""
        result = {
            "id": observation.id,
            "status": observation.status,
            "code": None,
            "subject": None,
            "effective_datetime": None,
            "value": None,
            "interpretation": None,
        }

        # Parse code
        if observation.code:
            result["code"] = {
                "coding": (
                    [
                        {
                            "system": coding.system,
                            "code": coding.code,
                            "display": coding.display,
                        }
                        for coding in observation.code.coding
                    ]
                    if observation.code.coding
                    else []
                ),
                "text": observation.code.text,
            }

        # Parse subject
        if observation.subject:
            result["subject"] = {
                "reference": observation.subject.reference,
                "display": observation.subject.display,
            }

        # Parse effective datetime
        if observation.effectiveDateTime:
            result["effective_datetime"] = str(observation.effectiveDateTime)

        # Parse value
        if hasattr(observation, "valueQuantity") and observation.valueQuantity:
            result["value"] = {
                "value": observation.valueQuantity.value,
                "unit": observation.valueQuantity.unit,
                "system": observation.valueQuantity.system,
                "code": observation.valueQuantity.code,
            }
        elif hasattr(observation, "valueString") and observation.valueString:
            result["value"] = observation.valueString

        return result

    def validate_message(self, message: str, version: str = "v2") -> Dict[str, Any]:
        """
        Validate HL7 message structure

        Args:
            message: Raw HL7 message
            version: HL7 version ('v2' or 'fhir')

        Returns:
            Validation result with errors if any
        """
        errors = []
        warnings = []

        try:
            if version == "v2":
                parsed = hl7.parse(message)

                # Check for MSH segment
                try:
                    msh = parsed.segment("MSH")
                    if not msh:
                        errors.append("Missing MSH (Message Header) segment")
                except:
                    errors.append("Invalid or missing MSH segment")

                # Check message structure
                if len(parsed) < 2:
                    warnings.append("Message has very few segments")

                # Check for required fields in MSH
                if len(msh) < 12:
                    warnings.append("MSH segment missing some standard fields")

            elif version == "fhir":
                resource = json.loads(message)
                if "resourceType" not in resource:
                    errors.append("Missing resourceType in FHIR resource")

            return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": warnings,
            }

    def generate_ack(self, original_message: str, ack_code: str = "AA") -> str:
        """
        Generate HL7 ACK (Acknowledgment) message

        Args:
            original_message: Original HL7 message
            ack_code: ACK code (AA=Application Accept, AE=Application Error, AR=Application Reject)

        Returns:
            ACK message string
        """
        try:
            parsed = hl7.parse(original_message)
            msh = parsed.segment("MSH")

            # Create ACK message
            ack_msh = [
                "MSH",
                "|",
                "^~\\&",
                str(msh[5]),  # Receiving app becomes sending app
                str(msh[6]),  # Receiving facility becomes sending facility
                str(msh[3]),  # Sending app becomes receiving app
                str(msh[4]),  # Sending facility becomes receiving facility
                datetime.utcnow().strftime("%Y%m%d%H%M%S"),
                "",
                "ACK",
                str(msh[10]),  # Same message control ID
                "P",
                "2.5",
            ]

            msa = [
                "MSA",
                ack_code,
                str(msh[10]),  # Message control ID
                (
                    "Message received successfully"
                    if ack_code == "AA"
                    else "Message processing error"
                ),
            ]

            ack_message = "|".join(ack_msh) + "\r" + "|".join(msa) + "\r"
            return ack_message

        except Exception as e:
            logger.error(f"Error generating ACK: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    parser = HL7Parser()

    # Example HL7 v2 message
    sample_message = """MSH|^~\\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20250120120000||ADT^A01|MSG00001|P|2.5
EVN|A01|20250120120000
PID|1||123456789^^^MRN||DOE^JOHN^A||19800101|M|||123 MAIN ST^^CITY^ST^12345||555-1234|||S||987654321
PV1|1|I|ICU^101^01||||12345^SMITH^JANE^A^^^MD|||MED||||1|||12345^SMITH^JANE^A^^^MD|IP|V123456|||||||||||||||||||||||||20250120120000"""

    # Parse message
    result = parser.parse_hl7_v2(sample_message)
    print(json.dumps(result, indent=2))

    # Validate message
    validation = parser.validate_message(sample_message)
    print(f"\nValidation: {validation}")

    # Generate ACK
    ack = parser.generate_ack(sample_message)
    print(f"\nACK Message:\n{ack}")
