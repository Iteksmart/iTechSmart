"""
HIPAA Compliance Framework
Ensures compliance with HIPAA regulations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HIPAAEventType(Enum):
    """HIPAA-relevant event types"""
    PHI_ACCESS = "phi_access"
    PHI_MODIFICATION = "phi_modification"
    PHI_DELETION = "phi_deletion"
    PHI_EXPORT = "phi_export"
    PHI_DISCLOSURE = "phi_disclosure"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SECURITY_INCIDENT = "security_incident"
    CONFIGURATION_CHANGE = "configuration_change"
    SYSTEM_ACCESS = "system_access"


class HIPAARiskLevel(Enum):
    """Risk levels for HIPAA events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HIPAACompliance:
    """
    HIPAA Compliance Manager
    Implements HIPAA Security Rule requirements
    """
    
    def __init__(self):
        self.compliance_checks = []
        self.violations = []
        self.access_logs = []
        
    # ========================================================================
    # Access Control (HIPAA § 164.312(a)(1))
    # ========================================================================
    
    def validate_access_control(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        user_roles: List[str]
    ) -> Dict[str, Any]:
        """
        Validate access control per HIPAA requirements
        
        HIPAA Requirement: Implement technical policies and procedures for
        electronic information systems that maintain electronic protected
        health information to allow access only to those persons or software
        programs that have been granted access rights.
        """
        result = {
            "allowed": False,
            "reason": "",
            "risk_level": HIPAARiskLevel.LOW.value,
            "requires_audit": True
        }
        
        # Check if accessing PHI
        is_phi_access = resource_type in ['patient', 'observation', 'medication', 'allergy']
        
        if is_phi_access:
            result["requires_audit"] = True
            result["risk_level"] = HIPAARiskLevel.MEDIUM.value
            
            # Verify user has appropriate role
            required_roles = self._get_required_roles(resource_type, action)
            has_permission = any(role in user_roles for role in required_roles)
            
            if has_permission:
                result["allowed"] = True
                result["reason"] = "User has required role for PHI access"
            else:
                result["allowed"] = False
                result["reason"] = "User lacks required role for PHI access"
                result["risk_level"] = HIPAARiskLevel.HIGH.value
                
                # Log potential violation
                self._log_access_violation(user_id, resource_type, resource_id, action)
        else:
            # Non-PHI access
            result["allowed"] = True
            result["requires_audit"] = False
        
        return result
    
    def _get_required_roles(self, resource_type: str, action: str) -> List[str]:
        """
        Get required roles for resource access
        """
        role_matrix = {
            'patient': {
                'read': ['admin', 'clinician', 'nurse', 'user'],
                'write': ['admin', 'clinician'],
                'delete': ['admin']
            },
            'observation': {
                'read': ['admin', 'clinician', 'nurse', 'user'],
                'write': ['admin', 'clinician', 'nurse'],
                'delete': ['admin']
            },
            'medication': {
                'read': ['admin', 'clinician', 'pharmacist', 'nurse'],
                'write': ['admin', 'clinician', 'pharmacist'],
                'delete': ['admin']
            }
        }
        
        return role_matrix.get(resource_type, {}).get(action, ['admin'])
    
    def _log_access_violation(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str
    ):
        """
        Log access violation
        """
        violation = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'violation_type': 'unauthorized_access_attempt'
        }
        
        self.violations.append(violation)
        logger.warning(f"HIPAA violation: Unauthorized access attempt by {user_id}")
    
    # ========================================================================
    # Audit Controls (HIPAA § 164.312(b))
    # ========================================================================
    
    def create_audit_log(
        self,
        event_type: HIPAAEventType,
        user_id: str,
        user_name: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        action: str = "",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        success: bool = True
    ) -> Dict[str, Any]:
        """
        Create HIPAA-compliant audit log entry
        
        HIPAA Requirement: Implement hardware, software, and/or procedural
        mechanisms that record and examine activity in information systems
        that contain or use electronic protected health information.
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type.value,
            'user_id': user_id,
            'user_name': user_name,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'patient_id': patient_id,
            'action': action,
            'details': details or {},
            'ip_address': ip_address,
            'success': success,
            'hipaa_compliant': True
        }
        
        self.access_logs.append(audit_entry)
        return audit_entry
    
    def get_audit_trail(
        self,
        patient_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[HIPAAEventType] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail with filters
        
        HIPAA Requirement: Maintain audit logs for at least 6 years
        """
        filtered_logs = self.access_logs
        
        if patient_id:
            filtered_logs = [log for log in filtered_logs if log.get('patient_id') == patient_id]
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.get('user_id') == user_id]
        
        if event_type:
            filtered_logs = [log for log in filtered_logs if log.get('event_type') == event_type.value]
        
        if start_date:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log['timestamp']) >= start_date
            ]
        
        if end_date:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log['timestamp']) <= end_date
            ]
        
        return filtered_logs
    
    # ========================================================================
    # Integrity Controls (HIPAA § 164.312(c)(1))
    # ========================================================================
    
    def verify_data_integrity(
        self,
        data: Dict[str, Any],
        checksum: Optional[str] = None
    ) -> bool:
        """
        Verify data integrity
        
        HIPAA Requirement: Implement policies and procedures to protect
        electronic protected health information from improper alteration
        or destruction.
        """
        import hashlib
        import json
        
        if checksum:
            # Verify against provided checksum
            data_str = json.dumps(data, sort_keys=True)
            calculated_checksum = hashlib.sha256(data_str.encode()).hexdigest()
            return calculated_checksum == checksum
        
        return True
    
    def generate_checksum(self, data: Dict[str, Any]) -> str:
        """
        Generate checksum for data integrity verification
        """
        import hashlib
        import json
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    # ========================================================================
    # Transmission Security (HIPAA § 164.312(e)(1))
    # ========================================================================
    
    def validate_transmission_security(
        self,
        protocol: str,
        encryption_enabled: bool
    ) -> Dict[str, Any]:
        """
        Validate transmission security
        
        HIPAA Requirement: Implement technical security measures to guard
        against unauthorized access to electronic protected health information
        that is being transmitted over an electronic communications network.
        """
        result = {
            "compliant": False,
            "issues": []
        }
        
        # Check for secure protocol
        if protocol.lower() not in ['https', 'tls', 'ssl', 'sftp']:
            result["issues"].append("Insecure transmission protocol")
        
        # Check for encryption
        if not encryption_enabled:
            result["issues"].append("Transmission encryption not enabled")
        
        result["compliant"] = len(result["issues"]) == 0
        
        return result
    
    # ========================================================================
    # Person or Entity Authentication (HIPAA § 164.312(d))
    # ========================================================================
    
    def validate_authentication(
        self,
        authentication_method: str,
        multi_factor_enabled: bool
    ) -> Dict[str, Any]:
        """
        Validate authentication mechanism
        
        HIPAA Requirement: Implement procedures to verify that a person or
        entity seeking access to electronic protected health information is
        the one claimed.
        """
        result = {
            "compliant": False,
            "recommendations": []
        }
        
        # Check authentication method
        strong_methods = ['jwt', 'oauth2', 'saml', 'certificate']
        if authentication_method.lower() not in strong_methods:
            result["recommendations"].append("Use stronger authentication method")
        
        # Check for multi-factor authentication
        if not multi_factor_enabled:
            result["recommendations"].append("Enable multi-factor authentication")
        
        result["compliant"] = len(result["recommendations"]) == 0
        
        return result
    
    # ========================================================================
    # Breach Notification
    # ========================================================================
    
    def detect_potential_breach(
        self,
        event_type: str,
        affected_records: int,
        unauthorized_access: bool,
        data_encrypted: bool
    ) -> Dict[str, Any]:
        """
        Detect potential HIPAA breach
        
        HIPAA Requirement: Notify affected individuals, HHS, and potentially
        media if breach affects 500+ individuals
        """
        breach_detected = False
        risk_level = HIPAARiskLevel.LOW
        notification_required = False
        
        # Determine if breach occurred
        if unauthorized_access and not data_encrypted:
            breach_detected = True
            
            if affected_records >= 500:
                risk_level = HIPAARiskLevel.CRITICAL
                notification_required = True
            elif affected_records >= 100:
                risk_level = HIPAARiskLevel.HIGH
                notification_required = True
            elif affected_records >= 10:
                risk_level = HIPAARiskLevel.MEDIUM
                notification_required = True
        
        return {
            "breach_detected": breach_detected,
            "risk_level": risk_level.value,
            "affected_records": affected_records,
            "notification_required": notification_required,
            "notification_deadline": (datetime.now() + timedelta(days=60)).isoformat() if notification_required else None,
            "actions_required": self._get_breach_actions(breach_detected, affected_records)
        }
    
    def _get_breach_actions(self, breach_detected: bool, affected_records: int) -> List[str]:
        """
        Get required actions for breach response
        """
        if not breach_detected:
            return []
        
        actions = [
            "Immediately contain the breach",
            "Document the breach details",
            "Assess the scope and impact",
            "Notify the Privacy Officer"
        ]
        
        if affected_records >= 500:
            actions.extend([
                "Notify HHS within 60 days",
                "Notify affected individuals within 60 days",
                "Notify prominent media outlets"
            ])
        elif affected_records >= 10:
            actions.extend([
                "Notify HHS within 60 days",
                "Notify affected individuals within 60 days"
            ])
        
        return actions
    
    # ========================================================================
    # Minimum Necessary Rule
    # ========================================================================
    
    def apply_minimum_necessary(
        self,
        data: Dict[str, Any],
        purpose: str,
        user_role: str
    ) -> Dict[str, Any]:
        """
        Apply minimum necessary rule to data
        
        HIPAA Requirement: When using or disclosing protected health
        information, make reasonable efforts to limit information to the
        minimum necessary to accomplish the intended purpose.
        """
        # Define minimum necessary fields by purpose and role
        field_sets = {
            'treatment': {
                'clinician': ['id', 'mrn', 'name', 'birth_date', 'gender', 'observations', 'medications', 'allergies'],
                'nurse': ['id', 'mrn', 'name', 'birth_date', 'observations', 'medications'],
                'pharmacist': ['id', 'mrn', 'name', 'medications', 'allergies']
            },
            'billing': {
                'billing_staff': ['id', 'mrn', 'name', 'birth_date', 'insurance']
            },
            'research': {
                'researcher': ['id', 'birth_date', 'gender', 'observations']  # De-identified
            }
        }
        
        allowed_fields = field_sets.get(purpose, {}).get(user_role, ['id'])
        
        # Filter data to minimum necessary
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        return filtered_data
    
    # ========================================================================
    # Compliance Reporting
    # ========================================================================
    
    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate HIPAA compliance report
        """
        # Get audit logs for period
        logs = self.get_audit_trail(start_date=start_date, end_date=end_date)
        
        # Calculate metrics
        total_access = len(logs)
        phi_access = len([log for log in logs if log.get('event_type') == HIPAAEventType.PHI_ACCESS.value])
        violations = len([log for log in logs if not log.get('success')])
        
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'metrics': {
                'total_access_events': total_access,
                'phi_access_events': phi_access,
                'violations': violations,
                'compliance_rate': ((total_access - violations) / total_access * 100) if total_access > 0 else 100
            },
            'violations': self.violations,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """
        Generate compliance recommendations
        """
        recommendations = []
        
        if len(self.violations) > 0:
            recommendations.append("Review and address access violations")
        
        if len(self.access_logs) > 10000:
            recommendations.append("Archive old audit logs to maintain performance")
        
        recommendations.append("Conduct regular security risk assessments")
        recommendations.append("Provide ongoing HIPAA training to staff")
        recommendations.append("Review and update security policies annually")
        
        return recommendations


# Global HIPAA compliance manager
hipaa_manager = HIPAACompliance()