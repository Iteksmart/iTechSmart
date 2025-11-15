#!/usr/bin/env python3
"""
Generate Test Data for iTechSmart HL7
Creates realistic test data for development and testing
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid


class TestDataGenerator:
    """Generate realistic test data for iTechSmart HL7"""
    
    def __init__(self):
        self.first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer",
            "Michael", "Linda", "William", "Elizabeth", "David", "Barbara",
            "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah",
            "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
            "Jackson", "Martin", "Lee", "Thompson", "White", "Harris"
        ]
        
        self.diagnoses = [
            {"code": "I10", "display": "Essential (primary) hypertension"},
            {"code": "E11.9", "display": "Type 2 diabetes mellitus without complications"},
            {"code": "J44.9", "display": "Chronic obstructive pulmonary disease, unspecified"},
            {"code": "I50.9", "display": "Heart failure, unspecified"},
            {"code": "N18.3", "display": "Chronic kidney disease, stage 3"},
            {"code": "J18.9", "display": "Pneumonia, unspecified organism"},
            {"code": "A41.9", "display": "Sepsis, unspecified organism"},
            {"code": "I21.9", "display": "Acute myocardial infarction, unspecified"},
            {"code": "I63.9", "display": "Cerebral infarction, unspecified"},
            {"code": "K92.2", "display": "Gastrointestinal hemorrhage, unspecified"}
        ]
        
        self.medications = [
            {"name": "Lisinopril", "dose": "10mg", "frequency": "daily"},
            {"name": "Metformin", "dose": "500mg", "frequency": "twice daily"},
            {"name": "Atorvastatin", "dose": "20mg", "frequency": "daily"},
            {"name": "Aspirin", "dose": "81mg", "frequency": "daily"},
            {"name": "Omeprazole", "dose": "20mg", "frequency": "daily"},
            {"name": "Levothyroxine", "dose": "50mcg", "frequency": "daily"},
            {"name": "Amlodipine", "dose": "5mg", "frequency": "daily"},
            {"name": "Metoprolol", "dose": "25mg", "frequency": "twice daily"},
            {"name": "Furosemide", "dose": "40mg", "frequency": "daily"},
            {"name": "Warfarin", "dose": "5mg", "frequency": "daily"}
        ]
        
        self.allergies = [
            "Penicillin", "Sulfa drugs", "Aspirin", "Codeine",
            "Morphine", "Latex", "Iodine", "Shellfish"
        ]
    
    def generate_mrn(self) -> str:
        """Generate a Medical Record Number"""
        return f"MRN-{random.randint(100000, 999999)}"
    
    def generate_patient(self) -> Dict[str, Any]:
        """Generate a single patient"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        
        # Generate date of birth (18-90 years old)
        age = random.randint(18, 90)
        dob = datetime.now() - timedelta(days=age*365 + random.randint(0, 365))
        
        patient = {
            "id": str(uuid.uuid4()),
            "mrn": self.generate_mrn(),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "age": age,
            "gender": random.choice(["male", "female"]),
            "contact": {
                "phone": f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "address": {
                    "street": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar'])} St",
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                    "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                    "zip": f"{random.randint(10000, 99999)}"
                }
            },
            "insurance": {
                "provider": random.choice(["Blue Cross", "Aetna", "UnitedHealthcare", "Cigna", "Medicare"]),
                "policy_number": f"POL-{random.randint(100000, 999999)}",
                "group_number": f"GRP-{random.randint(1000, 9999)}"
            }
        }
        
        return patient
    
    def generate_vital_signs(self, patient_id: str) -> Dict[str, Any]:
        """Generate vital signs for a patient"""
        return {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "blood_pressure": f"{random.randint(90, 180)}/{random.randint(60, 110)}",
            "systolic_bp": random.randint(90, 180),
            "diastolic_bp": random.randint(60, 110),
            "heart_rate": random.randint(60, 120),
            "respiratory_rate": random.randint(12, 24),
            "temperature": round(random.uniform(36.0, 39.0), 1),
            "oxygen_saturation": random.randint(88, 100),
            "weight_kg": round(random.uniform(50, 120), 1),
            "height_cm": random.randint(150, 200),
            "bmi": round(random.uniform(18.5, 35.0), 1)
        }
    
    def generate_lab_results(self, patient_id: str) -> List[Dict[str, Any]]:
        """Generate laboratory results"""
        labs = [
            {"name": "WBC", "value": round(random.uniform(4.0, 15.0), 1), "unit": "K/μL", "reference": "4.0-11.0"},
            {"name": "Hemoglobin", "value": round(random.uniform(10.0, 18.0), 1), "unit": "g/dL", "reference": "12.0-16.0"},
            {"name": "Platelets", "value": random.randint(100, 400), "unit": "K/μL", "reference": "150-400"},
            {"name": "Sodium", "value": random.randint(130, 150), "unit": "mmol/L", "reference": "135-145"},
            {"name": "Potassium", "value": round(random.uniform(3.0, 6.0), 1), "unit": "mmol/L", "reference": "3.5-5.0"},
            {"name": "Creatinine", "value": round(random.uniform(0.5, 3.0), 2), "unit": "mg/dL", "reference": "0.6-1.2"},
            {"name": "Glucose", "value": random.randint(70, 300), "unit": "mg/dL", "reference": "70-100"},
            {"name": "Lactate", "value": round(random.uniform(0.5, 5.0), 1), "unit": "mmol/L", "reference": "0.5-2.0"},
            {"name": "Troponin", "value": round(random.uniform(0.0, 2.0), 3), "unit": "ng/mL", "reference": "<0.04"},
            {"name": "BNP", "value": random.randint(0, 1000), "unit": "pg/mL", "reference": "<100"}
        ]
        
        results = []
        for lab in labs:
            results.append({
                "id": str(uuid.uuid4()),
                "patient_id": patient_id,
                "timestamp": datetime.now().isoformat(),
                "test_name": lab["name"],
                "value": lab["value"],
                "unit": lab["unit"],
                "reference_range": lab["reference"],
                "status": "final"
            })
        
        return results
    
    def generate_medications(self, patient_id: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate medication list"""
        selected_meds = random.sample(self.medications, min(count, len(self.medications)))
        
        medications = []
        for med in selected_meds:
            medications.append({
                "id": str(uuid.uuid4()),
                "patient_id": patient_id,
                "medication_name": med["name"],
                "dose": med["dose"],
                "frequency": med["frequency"],
                "route": random.choice(["oral", "IV", "subcutaneous", "topical"]),
                "start_date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
                "prescriber": f"Dr. {random.choice(self.last_names)}",
                "status": "active"
            })
        
        return medications
    
    def generate_allergies(self, patient_id: str) -> List[Dict[str, Any]]:
        """Generate allergy list"""
        num_allergies = random.randint(0, 3)
        if num_allergies == 0:
            return []
        
        selected_allergies = random.sample(self.allergies, num_allergies)
        
        allergies = []
        for allergy in selected_allergies:
            allergies.append({
                "id": str(uuid.uuid4()),
                "patient_id": patient_id,
                "allergen": allergy,
                "reaction": random.choice(["Rash", "Anaphylaxis", "Hives", "Swelling", "Nausea"]),
                "severity": random.choice(["mild", "moderate", "severe"]),
                "onset_date": (datetime.now() - timedelta(days=random.randint(365, 3650))).strftime("%Y-%m-%d")
            })
        
        return allergies
    
    def generate_diagnoses(self, patient_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """Generate diagnosis list"""
        selected_dx = random.sample(self.diagnoses, min(count, len(self.diagnoses)))
        
        diagnoses = []
        for dx in selected_dx:
            diagnoses.append({
                "id": str(uuid.uuid4()),
                "patient_id": patient_id,
                "code": dx["code"],
                "display": dx["display"],
                "onset_date": (datetime.now() - timedelta(days=random.randint(1, 1825))).strftime("%Y-%m-%d"),
                "status": random.choice(["active", "resolved", "chronic"]),
                "diagnosed_by": f"Dr. {random.choice(self.last_names)}"
            })
        
        return diagnoses
    
    def generate_complete_patient_record(self) -> Dict[str, Any]:
        """Generate a complete patient record with all data"""
        patient = self.generate_patient()
        patient_id = patient["id"]
        
        return {
            "patient": patient,
            "vital_signs": self.generate_vital_signs(patient_id),
            "lab_results": self.generate_lab_results(patient_id),
            "medications": self.generate_medications(patient_id),
            "allergies": self.generate_allergies(patient_id),
            "diagnoses": self.generate_diagnoses(patient_id)
        }
    
    def generate_hl7_message(self, patient: Dict[str, Any]) -> str:
        """Generate an HL7 v2.x ADT message"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        hl7_message = f"""MSH|^~\\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|{timestamp}||ADT^A01|{uuid.uuid4().hex[:10]}|P|2.5
EVN|A01|{timestamp}
PID|1||{patient['mrn']}||{patient['last_name']}^{patient['first_name']}||{patient['date_of_birth'].replace('-', '')}|{patient['gender'][0].upper()}|||{patient['contact']['address']['street']}^^{patient['contact']['address']['city']}^{patient['contact']['address']['state']}^{patient['contact']['address']['zip']}||{patient['contact']['phone']}||||||{patient['insurance']['policy_number']}
PV1|1|I|ICU^101^01||||123456^DOE^JOHN^A^^^MD||||||||||ADM|||||||||||||||||||||||||{timestamp}"""
        
        return hl7_message
    
    def generate_fhir_patient(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a FHIR R4 Patient resource"""
        return {
            "resourceType": "Patient",
            "id": patient["id"],
            "identifier": [
                {
                    "system": "http://hospital.example.org/mrn",
                    "value": patient["mrn"]
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": patient["last_name"],
                    "given": [patient["first_name"]]
                }
            ],
            "gender": patient["gender"],
            "birthDate": patient["date_of_birth"],
            "address": [
                {
                    "use": "home",
                    "line": [patient["contact"]["address"]["street"]],
                    "city": patient["contact"]["address"]["city"],
                    "state": patient["contact"]["address"]["state"],
                    "postalCode": patient["contact"]["address"]["zip"]
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": patient["contact"]["phone"],
                    "use": "mobile"
                },
                {
                    "system": "email",
                    "value": patient["contact"]["email"]
                }
            ]
        }


def main():
    """Generate test data and save to files"""
    generator = TestDataGenerator()
    
    print("🏥 iTechSmart HL7 Test Data Generator")
    print("=" * 50)
    
    # Generate patients
    num_patients = 50
    print(f"\n📊 Generating {num_patients} patient records...")
    
    all_data = {
        "patients": [],
        "vital_signs": [],
        "lab_results": [],
        "medications": [],
        "allergies": [],
        "diagnoses": [],
        "hl7_messages": [],
        "fhir_resources": []
    }
    
    for i in range(num_patients):
        record = generator.generate_complete_patient_record()
        
        all_data["patients"].append(record["patient"])
        all_data["vital_signs"].append(record["vital_signs"])
        all_data["lab_results"].extend(record["lab_results"])
        all_data["medications"].extend(record["medications"])
        all_data["allergies"].extend(record["allergies"])
        all_data["diagnoses"].extend(record["diagnoses"])
        
        # Generate HL7 message
        hl7_msg = generator.generate_hl7_message(record["patient"])
        all_data["hl7_messages"].append({
            "patient_id": record["patient"]["id"],
            "message": hl7_msg
        })
        
        # Generate FHIR resource
        fhir_patient = generator.generate_fhir_patient(record["patient"])
        all_data["fhir_resources"].append(fhir_patient)
        
        if (i + 1) % 10 == 0:
            print(f"  ✓ Generated {i + 1}/{num_patients} patients")
    
    # Save to files
    print("\n💾 Saving test data to files...")
    
    with open("test_data_complete.json", "w") as f:
        json.dump(all_data, f, indent=2)
    print("  ✓ Saved: test_data_complete.json")
    
    with open("test_data_patients.json", "w") as f:
        json.dump(all_data["patients"], f, indent=2)
    print("  ✓ Saved: test_data_patients.json")
    
    with open("test_data_hl7_messages.txt", "w") as f:
        for msg in all_data["hl7_messages"]:
            f.write(f"# Patient ID: {msg['patient_id']}\n")
            f.write(msg["message"])
            f.write("\n\n" + "=" * 80 + "\n\n")
    print("  ✓ Saved: test_data_hl7_messages.txt")
    
    with open("test_data_fhir_bundle.json", "w") as f:
        fhir_bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {"resource": resource} for resource in all_data["fhir_resources"]
            ]
        }
        json.dump(fhir_bundle, f, indent=2)
    print("  ✓ Saved: test_data_fhir_bundle.json")
    
    # Statistics
    print("\n📈 Test Data Statistics:")
    print(f"  • Patients: {len(all_data['patients'])}")
    print(f"  • Vital Signs: {len(all_data['vital_signs'])}")
    print(f"  • Lab Results: {len(all_data['lab_results'])}")
    print(f"  • Medications: {len(all_data['medications'])}")
    print(f"  • Allergies: {len(all_data['allergies'])}")
    print(f"  • Diagnoses: {len(all_data['diagnoses'])}")
    print(f"  • HL7 Messages: {len(all_data['hl7_messages'])}")
    print(f"  • FHIR Resources: {len(all_data['fhir_resources'])}")
    
    print("\n✅ Test data generation complete!")
    print("\n📁 Generated Files:")
    print("  • test_data_complete.json - All data in one file")
    print("  • test_data_patients.json - Patient demographics only")
    print("  • test_data_hl7_messages.txt - HL7 v2.x messages")
    print("  • test_data_fhir_bundle.json - FHIR R4 bundle")


if __name__ == "__main__":
    main()