"""
Clinical Notes Manager
Unified manager for all clinical note types
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class NoteType(Enum):
    """Clinical note types"""

    SOAP = "soap"
    NURSING = "nursing"
    PROGRESS = "progress"
    CONSULT = "consult"
    DISCHARGE = "discharge"
    CASE_REPORT = "case_report"


class ClinicalNotesManager:
    """
    Unified manager for all clinical note types
    Supports SOAP, Nursing, Progress, Consult, Discharge, and Case Report notes
    """

    def __init__(self, ai_agent=None):
        """
        Initialize clinical notes manager

        Args:
            ai_agent: AI agent for note generation
        """
        self.ai_agent = ai_agent
        self.templates = self._load_all_templates()

    def _load_all_templates(self) -> Dict[str, Dict]:
        """Load all clinical note templates"""
        return {
            "soap": self._get_soap_templates(),
            "nursing": self._get_nursing_templates(),
            "progress": self._get_progress_templates(),
            "consult": self._get_consult_templates(),
            "discharge": self._get_discharge_templates(),
            "case_report": self._get_case_report_templates(),
        }

    def _get_soap_templates(self) -> Dict[str, str]:
        """SOAP note templates"""
        return {
            "standard": """
SOAP NOTE

Date: {date}
Patient: {patient_name} | MRN: {mrn} | DOB: {dob}
Provider: {provider_name}

SUBJECTIVE:
Chief Complaint: {chief_complaint}
{subjective_content}

OBJECTIVE:
Vitals: BP {bp}, HR {hr}, Temp {temp}, RR {rr}, O2 {o2_sat}
{objective_content}

ASSESSMENT:
{assessment_content}

PLAN:
{plan_content}

_________________________
{provider_name}
{signature_datetime}
            """
        }

    def _get_nursing_templates(self) -> Dict[str, str]:
        """Nursing note templates"""
        return {
            "standard": """
NURSING NOTE

Date/Time: {datetime}
Patient: {patient_name} | MRN: {mrn} | Room: {room}
Nurse: {nurse_name}

ASSESSMENT:
{assessment}

INTERVENTIONS:
{interventions}

PATIENT RESPONSE:
{response}

PLAN OF CARE:
{plan}

_________________________
{nurse_name}, RN
{signature_datetime}
            """,
            "shift": """
NURSING SHIFT NOTE

Shift: {shift} | Date: {date}
Patient: {patient_name} | MRN: {mrn} | Room: {room}
Nurse: {nurse_name}

PATIENT STATUS:
{status}

VITAL SIGNS:
{vitals}

INTAKE/OUTPUT:
{intake_output}

MEDICATIONS ADMINISTERED:
{medications}

PROCEDURES/TREATMENTS:
{procedures}

PATIENT/FAMILY EDUCATION:
{education}

PLAN FOR NEXT SHIFT:
{plan}

_________________________
{nurse_name}, RN
{signature_datetime}
            """,
        }

    def _get_progress_templates(self) -> Dict[str, str]:
        """Progress note templates"""
        return {
            "standard": """
PROGRESS NOTE

Date: {date}
Patient: {patient_name} | MRN: {mrn}
Provider: {provider_name}

INTERVAL HISTORY:
{interval_history}

CURRENT STATUS:
{current_status}

VITAL SIGNS:
{vitals}

PHYSICAL EXAMINATION:
{exam}

LABORATORY/STUDIES:
{labs}

ASSESSMENT/PLAN:
{assessment_plan}

_________________________
{provider_name}
{signature_datetime}
            """,
            "daily": """
DAILY PROGRESS NOTE

Hospital Day: {hospital_day} | Date: {date}
Patient: {patient_name} | MRN: {mrn}
Attending: {attending_name}

OVERNIGHT EVENTS:
{overnight_events}

SUBJECTIVE:
{subjective}

OBJECTIVE:
Vitals: {vitals}
Exam: {exam}
Labs: {labs}

ASSESSMENT/PLAN BY PROBLEM:
{problem_list}

_________________________
{provider_name}
{signature_datetime}
            """,
        }

    def _get_consult_templates(self) -> Dict[str, str]:
        """Consult note templates"""
        return {
            "standard": """
CONSULTATION NOTE

Date: {date}
Patient: {patient_name} | MRN: {mrn}
Requesting Provider: {requesting_provider}
Consulting Provider: {consulting_provider}
Specialty: {specialty}

REASON FOR CONSULTATION:
{reason}

HISTORY OF PRESENT ILLNESS:
{hpi}

PAST MEDICAL HISTORY:
{pmh}

MEDICATIONS:
{medications}

ALLERGIES:
{allergies}

PHYSICAL EXAMINATION:
{exam}

DIAGNOSTIC STUDIES:
{studies}

IMPRESSION:
{impression}

RECOMMENDATIONS:
{recommendations}

Thank you for this consultation.

_________________________
{consulting_provider}
{specialty}
{signature_datetime}
            """
        }

    def _get_discharge_templates(self) -> Dict[str, str]:
        """Discharge summary templates"""
        return {
            "standard": """
DISCHARGE SUMMARY

Date of Admission: {admission_date}
Date of Discharge: {discharge_date}
Length of Stay: {los} days

Patient: {patient_name} | MRN: {mrn} | DOB: {dob}
Attending Physician: {attending_name}

ADMISSION DIAGNOSIS:
{admission_diagnosis}

DISCHARGE DIAGNOSIS:
{discharge_diagnosis}

HOSPITAL COURSE:
{hospital_course}

PROCEDURES PERFORMED:
{procedures}

DISCHARGE MEDICATIONS:
{discharge_medications}

DISCHARGE INSTRUCTIONS:
{discharge_instructions}

FOLLOW-UP:
{followup}

DISCHARGE CONDITION:
{discharge_condition}

DISCHARGE DISPOSITION:
{disposition}

_________________________
{attending_name}
{signature_datetime}
            """
        }

    def _get_case_report_templates(self) -> Dict[str, str]:
        """Clinical case report templates"""
        return {
            "standard": """
CLINICAL CASE REPORT

Title: {title}
Date: {date}
Authors: {authors}
Institution: {institution}

ABSTRACT:
{abstract}

INTRODUCTION:
{introduction}

CASE PRESENTATION:
Patient: {patient_demographics}
Chief Complaint: {chief_complaint}
History: {history}
Physical Examination: {exam}
Diagnostic Studies: {diagnostics}

DIFFERENTIAL DIAGNOSIS:
{differential}

TREATMENT:
{treatment}

OUTCOME:
{outcome}

DISCUSSION:
{discussion}

CONCLUSION:
{conclusion}

REFERENCES:
{references}

_________________________
{authors}
{signature_datetime}
            """
        }

    async def generate_note(
        self,
        note_type: NoteType,
        patient_data: Dict,
        clinical_data: Dict,
        provider_data: Optional[Dict] = None,
        template_name: str = "standard",
    ) -> Dict[str, Any]:
        """
        Generate any type of clinical note

        Args:
            note_type: Type of note to generate
            patient_data: Patient information
            clinical_data: Clinical data
            provider_data: Provider information
            template_name: Template to use

        Returns:
            Generated note with metadata
        """
        try:
            # Use AI if available
            if self.ai_agent:
                content = await self._generate_with_ai(
                    note_type, patient_data, clinical_data, provider_data
                )
            else:
                content = self._generate_from_template(
                    note_type, patient_data, clinical_data, provider_data, template_name
                )

            # Create note metadata
            note = {
                "note_id": f"{note_type.value.upper()}-{datetime.utcnow().timestamp()}",
                "note_type": note_type.value,
                "template_name": template_name,
                "patient_id": patient_data.get("id"),
                "patient_name": patient_data.get("name"),
                "mrn": patient_data.get("mrn"),
                "provider_name": provider_data.get("name") if provider_data else None,
                "provider_id": provider_data.get("id") if provider_data else None,
                "date_created": datetime.utcnow().isoformat(),
                "content": content,
                "status": "draft",
                "signed": False,
                "signature_datetime": None,
                "amendments": [],
            }

            return note

        except Exception as e:
            logger.error(f"Error generating {note_type.value} note: {str(e)}")
            raise

    async def _generate_with_ai(
        self,
        note_type: NoteType,
        patient_data: Dict,
        clinical_data: Dict,
        provider_data: Optional[Dict],
    ) -> str:
        """Generate note using AI"""

        note_descriptions = {
            NoteType.SOAP: "SOAP (Subjective, Objective, Assessment, Plan) note",
            NoteType.NURSING: "Nursing assessment and care note",
            NoteType.PROGRESS: "Progress note documenting patient status",
            NoteType.CONSULT: "Consultation note from specialist",
            NoteType.DISCHARGE: "Discharge summary with instructions",
            NoteType.CASE_REPORT: "Clinical case report for publication",
        }

        prompt = f"""
Generate a professional {note_descriptions[note_type]}.

Patient Information:
- Name: {patient_data.get('name')}
- Age: {patient_data.get('age')}
- Gender: {patient_data.get('gender')}
- MRN: {patient_data.get('mrn')}

Clinical Information:
{json.dumps(clinical_data, indent=2)}

Provider: {provider_data.get('name') if provider_data else 'N/A'}

Generate a complete, professional clinical note following standard medical documentation practices.
Use appropriate medical terminology and ensure all required sections are included.
"""

        # Generate using AI agent
        content = await self.ai_agent.generate_clinical_note(
            note_type=note_type.value,
            patient_data=patient_data,
            clinical_data=clinical_data,
        )

        return content

    def _generate_from_template(
        self,
        note_type: NoteType,
        patient_data: Dict,
        clinical_data: Dict,
        provider_data: Optional[Dict],
        template_name: str,
    ) -> str:
        """Generate note from template"""

        templates = self.templates.get(note_type.value, {})
        template = templates.get(
            template_name, list(templates.values())[0] if templates else ""
        )

        # Prepare common template data
        template_data = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "datetime": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "patient_name": patient_data.get("name", "Unknown"),
            "mrn": patient_data.get("mrn", "N/A"),
            "dob": patient_data.get("dob", "N/A"),
            "provider_name": (
                provider_data.get("name", "Unknown") if provider_data else "Unknown"
            ),
            "signature_datetime": "",
        }

        # Add clinical data
        template_data.update(clinical_data)

        # Fill template
        try:
            content = template.format(**template_data)
        except KeyError as e:
            logger.warning(f"Missing template key: {e}")
            content = template

        return content

    async def generate_soap_note(
        self, patient_data: Dict, clinical_data: Dict, provider_data: Dict
    ) -> Dict:
        """Generate SOAP note"""
        return await self.generate_note(
            NoteType.SOAP, patient_data, clinical_data, provider_data
        )

    async def generate_nursing_note(
        self, patient_data: Dict, clinical_data: Dict, nurse_data: Dict
    ) -> Dict:
        """Generate nursing note"""
        return await self.generate_note(
            NoteType.NURSING, patient_data, clinical_data, nurse_data
        )

    async def generate_progress_note(
        self, patient_data: Dict, clinical_data: Dict, provider_data: Dict
    ) -> Dict:
        """Generate progress note"""
        return await self.generate_note(
            NoteType.PROGRESS, patient_data, clinical_data, provider_data
        )

    async def generate_consult_note(
        self, patient_data: Dict, clinical_data: Dict, provider_data: Dict
    ) -> Dict:
        """Generate consult note"""
        return await self.generate_note(
            NoteType.CONSULT, patient_data, clinical_data, provider_data
        )

    async def generate_discharge_summary(
        self, patient_data: Dict, clinical_data: Dict, provider_data: Dict
    ) -> Dict:
        """Generate discharge summary"""
        return await self.generate_note(
            NoteType.DISCHARGE, patient_data, clinical_data, provider_data
        )

    async def generate_case_report(
        self, patient_data: Dict, clinical_data: Dict, author_data: Dict
    ) -> Dict:
        """Generate clinical case report"""
        return await self.generate_note(
            NoteType.CASE_REPORT, patient_data, clinical_data, author_data
        )

    async def voice_to_note(
        self,
        audio_file: str,
        note_type: NoteType,
        patient_data: Dict,
        provider_data: Dict,
    ) -> Dict[str, Any]:
        """
        Convert voice recording to clinical note

        Args:
            audio_file: Path to audio file
            note_type: Type of note to generate
            patient_data: Patient information
            provider_data: Provider information

        Returns:
            Generated note from voice
        """
        try:
            # Transcribe audio (would use Whisper or similar)
            transcription = await self._transcribe_audio(audio_file)

            # Extract clinical data from transcription
            clinical_data = await self._extract_clinical_data(transcription, note_type)

            # Generate note
            note = await self.generate_note(
                note_type, patient_data, clinical_data, provider_data
            )

            note["source"] = "voice"
            note["transcription"] = transcription

            return note

        except Exception as e:
            logger.error(f"Error converting voice to note: {str(e)}")
            raise

    async def _transcribe_audio(self, audio_file: str) -> str:
        """Transcribe audio file to text"""
        # In production, use OpenAI Whisper or similar
        # For now, return placeholder
        return "Transcribed audio content would appear here..."

    async def _extract_clinical_data(
        self, transcription: str, note_type: NoteType
    ) -> Dict:
        """Extract structured clinical data from transcription"""
        if self.ai_agent:
            prompt = f"""
Extract structured clinical data from this transcription for a {note_type.value} note:

{transcription}

Return JSON with appropriate fields for the note type.
"""
            # Use AI to extract structured data
            result = await self.ai_agent.analyze(prompt)
            return result
        else:
            return {"transcription": transcription}

    async def batch_generate_notes(self, note_requests: List[Dict]) -> List[Dict]:
        """
        Generate multiple notes in batch

        Args:
            note_requests: List of note generation requests

        Returns:
            List of generated notes
        """
        notes = []

        for request in note_requests:
            try:
                note = await self.generate_note(
                    NoteType(request["note_type"]),
                    request["patient_data"],
                    request["clinical_data"],
                    request.get("provider_data"),
                )
                notes.append(note)
            except Exception as e:
                logger.error(f"Error generating note in batch: {str(e)}")
                notes.append({"error": str(e), "request": request})

        return notes

    def get_note_templates(self, note_type: NoteType) -> List[str]:
        """Get available templates for note type"""
        templates = self.templates.get(note_type.value, {})
        return list(templates.keys())

    def validate_note(self, note_type: NoteType, content: str) -> Dict[str, Any]:
        """Validate note completeness"""
        required_sections = {
            NoteType.SOAP: ["SUBJECTIVE", "OBJECTIVE", "ASSESSMENT", "PLAN"],
            NoteType.NURSING: ["ASSESSMENT", "INTERVENTIONS", "RESPONSE", "PLAN"],
            NoteType.PROGRESS: ["INTERVAL HISTORY", "CURRENT STATUS", "ASSESSMENT"],
            NoteType.CONSULT: ["REASON", "IMPRESSION", "RECOMMENDATIONS"],
            NoteType.DISCHARGE: [
                "ADMISSION DIAGNOSIS",
                "DISCHARGE DIAGNOSIS",
                "HOSPITAL COURSE",
                "DISCHARGE MEDICATIONS",
            ],
            NoteType.CASE_REPORT: [
                "ABSTRACT",
                "CASE PRESENTATION",
                "DISCUSSION",
                "CONCLUSION",
            ],
        }

        required = required_sections.get(note_type, [])
        missing = [section for section in required if section not in content]

        return {
            "valid": len(missing) == 0,
            "missing_sections": missing,
            "completeness": (
                (len(required) - len(missing)) / len(required) * 100
                if required
                else 100
            ),
        }


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        manager = ClinicalNotesManager()

        patient_data = {
            "id": "P123456",
            "name": "John Doe",
            "age": 45,
            "gender": "M",
            "mrn": "123456",
            "dob": "1979-01-15",
        }

        # Generate SOAP note
        soap_note = await manager.generate_soap_note(
            patient_data,
            {
                "chief_complaint": "Chest pain",
                "subjective_content": "Patient reports acute chest pain...",
                "bp": "140/90",
                "hr": 88,
                "temp": 98.6,
                "rr": 16,
                "o2_sat": 98,
                "objective_content": "Alert and oriented...",
                "assessment_content": "Acute chest pain, rule out ACS",
                "plan_content": "EKG, troponin, cardiology consult",
            },
            {"name": "Dr. Jane Smith", "id": "DR001"},
        )

        print("SOAP Note:")
        print(soap_note["content"])

        # Generate nursing note
        nursing_note = await manager.generate_nursing_note(
            patient_data,
            {
                "assessment": "Patient resting comfortably",
                "interventions": "Administered medications as ordered",
                "response": "Patient tolerated well",
                "plan": "Continue current care plan",
            },
            {"name": "Sarah Johnson, RN", "id": "RN001"},
        )

        print("\n\nNursing Note:")
        print(nursing_note["content"])

    asyncio.run(main())
