"""
HIPAA Compliance Module
Ensures all operations comply with HIPAA regulations
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class PHIType(Enum):
    """Types of Protected Health Information"""
    NAME = "name"
    ADDRESS = "address"
    DATE = "date"
    PHONE = "phone"
    EMAIL = "email"
    SSN = "ssn"
    MRN = "mrn"
    ACCOUNT_NUMBER = "account_number"
    CERTIFICATE_NUMBER = "certificate_number"
    VEHICLE_ID = "vehicle_id"
    DEVICE_ID = "device_id"
    URL = "url"
    IP_ADDRESS = "ip_address"
    BIOMETRIC = "biometric"
    PHOTO = "photo"
    OTHER = "other"


class HIPAACompliance:
    """
    HIPAA compliance enforcement and utilities
    """
    
    def __init__(self):
        self.phi_identifiers = [
            'name', 'address', 'date', 'phone', 'fax', 'email', 'ssn',
            'mrn', 'account', 'certificate', 'vehicle', 'device', 'url',
            'ip', 'biometric', 'photo'
        ]
    
    def log_phi_access(self,
                      user_id: str,
                      action: str,
                      resource_type: str,
                      resource_id: str,
                      phi_types: List[PHIType],
                      justification: str,
                      ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Log PHI access for HIPAA audit trail
        
        Args:
            user_id: User accessing PHI
            action: Action performed (read, write, delete)
            resource_type: Type of resource (patient, note, message)
            resource_id: Resource identifier
            phi_types: Types of PHI accessed
            justification: Business justification for access
            ip_address: User's IP address
            
        Returns:
            Audit log entry
        """
        log_entry = {
            'log_id': f"AUDIT-{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'phi_types': [phi.value for phi in phi_types],
            'justification': justification,
            'ip_address': ip_address,
            'phi_accessed': True
        }
        
        # In production: store in database with 7-year retention
        logger.info(f"PHI Access Logged: {log_entry['log_id']}")
        
        return log_entry
    
    def de_identify_data(self, data: Dict[str, Any], method: str = 'hash') -> Dict[str, Any]:
        """
        De-identify PHI data
        
        Args:
            data: Data containing PHI
            method: De-identification method (hash, mask, remove)
            
        Returns:
            De-identified data
        """
        de_identified = data.copy()
        
        phi_fields = ['name', 'ssn', 'mrn', 'phone', 'email', 'address']
        
        for field in phi_fields:
            if field in de_identified:
                if method == 'hash':
                    de_identified[field] = self._hash_value(str(de_identified[field]))
                elif method == 'mask':
                    de_identified[field] = self._mask_value(str(de_identified[field]))
                elif method == 'remove':
                    del de_identified[field]
        
        return de_identified
    
    def _hash_value(self, value: str) -> str:
        """Hash value using SHA-256"""
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    
    def _mask_value(self, value: str) -> str:
        """Mask value (show first/last chars only)"""
        if len(value) <= 4:
            return '****'
        return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
    
    def validate_minimum_necessary(self,
                                   requested_fields: List[str],
                                   user_role: str,
                                   purpose: str) -> Dict[str, Any]:
        """
        Validate minimum necessary principle
        
        Args:
            requested_fields: Fields being requested
            user_role: Role of requesting user
            purpose: Purpose of data access
            
        Returns:
            Validation result with allowed fields
        """
        # Define role-based access rules
        role_permissions = {
            'physician': ['name', 'mrn', 'dob', 'gender', 'vitals', 'labs', 'medications', 'diagnoses', 'notes'],
            'nurse': ['name', 'mrn', 'dob', 'vitals', 'medications', 'allergies', 'care_plan'],
            'therapist': ['name', 'mrn', 'dob', 'therapy_notes', 'progress'],
            'billing': ['name', 'mrn', 'insurance', 'billing_codes'],
            'analyst': ['age', 'gender', 'diagnoses', 'outcomes']  # De-identified only
        }
        
        allowed_fields = role_permissions.get(user_role, [])
        approved_fields = [f for f in requested_fields if f in allowed_fields]
        denied_fields = [f for f in requested_fields if f not in allowed_fields]
        
        return {
            'approved': len(denied_fields) == 0,
            'approved_fields': approved_fields,
            'denied_fields': denied_fields,
            'justification_required': len(denied_fields) > 0
        }
    
    def check_breach_notification_required(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if breach notification is required
        
        Args:
            incident: Security incident details
            
        Returns:
            Breach notification assessment
        """
        # HIPAA breach notification criteria
        criteria = {
            'unauthorized_access': False,
            'phi_compromised': False,
            'affects_500_plus': False,
            'notification_required': False,
            'notification_deadline': None
        }
        
        # Check if PHI was accessed
        if incident.get('phi_accessed'):
            criteria['phi_compromised'] = True
        
        # Check if unauthorized
        if incident.get('unauthorized'):
            criteria['unauthorized_access'] = True
        
        # Check number of individuals affected
        affected_count = incident.get('affected_individuals', 0)
        if affected_count >= 500:
            criteria['affects_500_plus'] = True
        
        # Determine if notification required
        if criteria['unauthorized_access'] and criteria['phi_compromised']:
            criteria['notification_required'] = True
            
            # Calculate deadline (60 days for <500, immediate for 500+)
            if criteria['affects_500_plus']:
                criteria['notification_deadline'] = 'immediate'
            else:
                deadline = datetime.utcnow().timestamp() + (60 * 24 * 60 * 60)  # 60 days
                criteria['notification_deadline'] = datetime.fromtimestamp(deadline).isoformat()
        
        return criteria
    
    def generate_baa(self, 
                    covered_entity: Dict[str, str],
                    business_associate: Dict[str, str]) -> str:
        """
        Generate Business Associate Agreement
        
        Args:
            covered_entity: Covered entity information
            business_associate: Business associate information
            
        Returns:
            BAA document text
        """
        baa_template = f"""
BUSINESS ASSOCIATE AGREEMENT

This Business Associate Agreement ("Agreement") is entered into as of {datetime.utcnow().strftime('%B %d, %Y')}
between {covered_entity.get('name')} ("Covered Entity") and {business_associate.get('name')} ("Business Associate").

RECITALS

WHEREAS, Covered Entity is a healthcare provider subject to the Health Insurance Portability and Accountability Act of 1996 ("HIPAA");

WHEREAS, Business Associate provides services to Covered Entity that involve the use or disclosure of Protected Health Information ("PHI");

NOW, THEREFORE, in consideration of the mutual covenants and agreements herein contained, the parties agree as follows:

1. DEFINITIONS

1.1 "Protected Health Information" or "PHI" shall have the same meaning as set forth in 45 CFR § 160.103.

1.2 "Required by Law" shall have the same meaning as set forth in 45 CFR § 164.103.

1.3 "Secretary" means the Secretary of the Department of Health and Human Services.

2. OBLIGATIONS OF BUSINESS ASSOCIATE

2.1 Permitted Uses and Disclosures
Business Associate may use or disclose PHI only as permitted by this Agreement or as Required by Law.

2.2 Safeguards
Business Associate shall implement appropriate safeguards to prevent use or disclosure of PHI other than as provided for by this Agreement.

2.3 Reporting
Business Associate shall report to Covered Entity any use or disclosure of PHI not provided for by this Agreement within 5 business days of becoming aware of such use or disclosure.

2.4 Subcontractors
Business Associate shall ensure that any subcontractors that create, receive, maintain, or transmit PHI on behalf of Business Associate agree to the same restrictions and conditions that apply to Business Associate.

2.5 Access to PHI
Business Associate shall provide access to PHI in a Designated Record Set to Covered Entity or an Individual as required by 45 CFR § 164.524.

2.6 Amendment of PHI
Business Associate shall make any amendments to PHI in a Designated Record Set as directed by Covered Entity pursuant to 45 CFR § 164.526.

2.7 Accounting of Disclosures
Business Associate shall document disclosures of PHI and provide an accounting of disclosures to Covered Entity as required by 45 CFR § 164.528.

2.8 Availability of Books and Records
Business Associate shall make its internal practices, books, and records relating to the use and disclosure of PHI available to the Secretary for purposes of determining Covered Entity's compliance with HIPAA.

3. OBLIGATIONS OF COVERED ENTITY

3.1 Permissible Requests
Covered Entity shall not request Business Associate to use or disclose PHI in any manner that would not be permissible under HIPAA if done by Covered Entity.

3.2 Notice of Privacy Practices
Covered Entity shall provide Business Associate with any changes in, or revocation of, permission by an Individual to use or disclose PHI.

4. TERM AND TERMINATION

4.1 Term
This Agreement shall be effective as of the date first written above and shall terminate when all PHI provided by Covered Entity to Business Associate is destroyed or returned to Covered Entity.

4.2 Termination for Cause
Upon Covered Entity's knowledge of a material breach by Business Associate, Covered Entity shall either:
(a) Provide an opportunity for Business Associate to cure the breach and terminate if not cured; or
(b) Immediately terminate this Agreement if cure is not possible.

4.3 Effect of Termination
Upon termination, Business Associate shall return or destroy all PHI received from Covered Entity. If return or destruction is not feasible, Business Associate shall extend the protections of this Agreement to such PHI.

5. MISCELLANEOUS

5.1 Regulatory References
A reference in this Agreement to a section in HIPAA means the section as in effect or as amended.

5.2 Amendment
The parties agree to take such action as is necessary to amend this Agreement to comply with HIPAA and HITECH Act.

5.3 Interpretation
Any ambiguity in this Agreement shall be resolved in favor of a meaning that permits Covered Entity to comply with HIPAA.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

COVERED ENTITY:
{covered_entity.get('name')}

By: _________________________
Name: {covered_entity.get('signatory_name', '')}
Title: {covered_entity.get('signatory_title', '')}
Date: _________________________


BUSINESS ASSOCIATE:
{business_associate.get('name')}

By: _________________________
Name: {business_associate.get('signatory_name', '')}
Title: {business_associate.get('signatory_title', '')}
Date: _________________________
        """
        
        return baa_template
    
    def validate_consent(self, patient_id: str, purpose: str) -> bool:
        """
        Validate patient consent for data use
        
        Args:
            patient_id: Patient identifier
            purpose: Purpose of data use
            
        Returns:
            True if consent exists
        """
        # In production: check consent database
        # For now, assume consent exists
        return True
    
    def get_retention_period(self, data_type: str) -> int:
        """
        Get retention period for data type
        
        Args:
            data_type: Type of data
            
        Returns:
            Retention period in years
        """
        retention_periods = {
            'audit_logs': 7,
            'clinical_notes': 7,
            'hl7_messages': 7,
            'patient_records': 7,
            'incident_logs': 7,
            'access_logs': 7
        }
        
        return retention_periods.get(data_type, 7)  # Default 7 years


# Global HIPAA compliance instance
hipaa = HIPAACompliance()


# Example usage
if __name__ == "__main__":
    # Log PHI access
    log = hipaa.log_phi_access(
        user_id='DR001',
        action='read',
        resource_type='patient',
        resource_id='P123456',
        phi_types=[PHIType.NAME, PHIType.MRN, PHIType.DATE],
        justification='Patient care - reviewing medical history',
        ip_address='192.168.1.100'
    )
    
    print(f"PHI Access Logged: {log['log_id']}")
    
    # De-identify data
    patient_data = {
        'name': 'John Doe',
        'mrn': '123456',
        'ssn': '123-45-6789',
        'phone': '555-1234',
        'diagnosis': 'Hypertension'
    }
    
    de_identified = hipaa.de_identify_data(patient_data, method='hash')
    print(f"\nDe-identified data: {de_identified}")
    
    # Validate minimum necessary
    validation = hipaa.validate_minimum_necessary(
        requested_fields=['name', 'mrn', 'ssn', 'diagnosis'],
        user_role='nurse',
        purpose='medication administration'
    )
    
    print(f"\nMinimum necessary validation: {validation}")
    
    # Generate BAA
    baa = hipaa.generate_baa(
        covered_entity={
            'name': 'Sample Hospital',
            'signatory_name': 'John Smith',
            'signatory_title': 'CEO'
        },
        business_associate={
            'name': 'iTechSmart Inc.',
            'signatory_name': 'Jane Doe',
            'signatory_title': 'CEO'
        }
    )
    
    print(f"\nBAA Generated (first 500 chars):\n{baa[:500]}...")