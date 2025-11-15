"""
Access Control System
Role-Based Access Control (RBAC) for HIPAA compliance
"""

from typing import List, Dict, Optional, Set, Any
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Permission(Enum):
    """System permissions"""
    # Patient permissions
    PATIENT_READ = "patient:read"
    PATIENT_WRITE = "patient:write"
    PATIENT_DELETE = "patient:delete"
    PATIENT_EXPORT = "patient:export"
    
    # Observation permissions
    OBSERVATION_READ = "observation:read"
    OBSERVATION_WRITE = "observation:write"
    OBSERVATION_DELETE = "observation:delete"
    
    # Medication permissions
    MEDICATION_READ = "medication:read"
    MEDICATION_WRITE = "medication:write"
    MEDICATION_DELETE = "medication:delete"
    MEDICATION_PRESCRIBE = "medication:prescribe"
    
    # Allergy permissions
    ALLERGY_READ = "allergy:read"
    ALLERGY_WRITE = "allergy:write"
    ALLERGY_DELETE = "allergy:delete"
    
    # HL7 permissions
    HL7_READ = "hl7:read"
    HL7_SEND = "hl7:send"
    HL7_RECEIVE = "hl7:receive"
    
    # Connection permissions
    CONNECTION_READ = "connection:read"
    CONNECTION_WRITE = "connection:write"
    CONNECTION_DELETE = "connection:delete"
    CONNECTION_TEST = "connection:test"
    
    # Audit permissions
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    
    # System permissions
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"
    USER_MANAGE = "user:manage"


class Role(Enum):
    """System roles with associated permissions"""
    ADMIN = "admin"
    CLINICIAN = "clinician"
    NURSE = "nurse"
    PHARMACIST = "pharmacist"
    BILLING_STAFF = "billing_staff"
    RESEARCHER = "researcher"
    USER = "user"
    GUEST = "guest"


# Role-Permission mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Full system access
        Permission.PATIENT_READ,
        Permission.PATIENT_WRITE,
        Permission.PATIENT_DELETE,
        Permission.PATIENT_EXPORT,
        Permission.OBSERVATION_READ,
        Permission.OBSERVATION_WRITE,
        Permission.OBSERVATION_DELETE,
        Permission.MEDICATION_READ,
        Permission.MEDICATION_WRITE,
        Permission.MEDICATION_DELETE,
        Permission.MEDICATION_PRESCRIBE,
        Permission.ALLERGY_READ,
        Permission.ALLERGY_WRITE,
        Permission.ALLERGY_DELETE,
        Permission.HL7_READ,
        Permission.HL7_SEND,
        Permission.HL7_RECEIVE,
        Permission.CONNECTION_READ,
        Permission.CONNECTION_WRITE,
        Permission.CONNECTION_DELETE,
        Permission.CONNECTION_TEST,
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
        Permission.SYSTEM_ADMIN,
        Permission.SYSTEM_CONFIG,
        Permission.USER_MANAGE,
    },
    Role.CLINICIAN: {
        # Clinical access
        Permission.PATIENT_READ,
        Permission.PATIENT_WRITE,
        Permission.OBSERVATION_READ,
        Permission.OBSERVATION_WRITE,
        Permission.MEDICATION_READ,
        Permission.MEDICATION_WRITE,
        Permission.MEDICATION_PRESCRIBE,
        Permission.ALLERGY_READ,
        Permission.ALLERGY_WRITE,
        Permission.HL7_READ,
    },
    Role.NURSE: {
        # Nursing access
        Permission.PATIENT_READ,
        Permission.OBSERVATION_READ,
        Permission.OBSERVATION_WRITE,
        Permission.MEDICATION_READ,
        Permission.ALLERGY_READ,
        Permission.HL7_READ,
    },
    Role.PHARMACIST: {
        # Pharmacy access
        Permission.PATIENT_READ,
        Permission.MEDICATION_READ,
        Permission.MEDICATION_WRITE,
        Permission.ALLERGY_READ,
    },
    Role.BILLING_STAFF: {
        # Billing access (limited PHI)
        Permission.PATIENT_READ,
    },
    Role.RESEARCHER: {
        # Research access (de-identified data)
        Permission.PATIENT_READ,
        Permission.OBSERVATION_READ,
    },
    Role.USER: {
        # Basic user access
        Permission.PATIENT_READ,
        Permission.OBSERVATION_READ,
        Permission.MEDICATION_READ,
        Permission.ALLERGY_READ,
    },
    Role.GUEST: {
        # Minimal access
        Permission.PATIENT_READ,
    }
}


class AccessControl:
    """
    Role-Based Access Control (RBAC) system
    """
    
    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS
        self.access_logs = []
    
    def has_permission(
        self,
        user_roles: List[str],
        required_permission: Permission
    ) -> bool:
        """
        Check if user has required permission
        
        Args:
            user_roles: List of user's roles
            required_permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        for role_str in user_roles:
            try:
                role = Role(role_str)
                permissions = self.role_permissions.get(role, set())
                if required_permission in permissions:
                    return True
            except ValueError:
                logger.warning(f"Invalid role: {role_str}")
                continue
        
        return False
    
    def has_any_permission(
        self,
        user_roles: List[str],
        required_permissions: List[Permission]
    ) -> bool:
        """
        Check if user has any of the required permissions
        """
        return any(
            self.has_permission(user_roles, perm)
            for perm in required_permissions
        )
    
    def has_all_permissions(
        self,
        user_roles: List[str],
        required_permissions: List[Permission]
    ) -> bool:
        """
        Check if user has all required permissions
        """
        return all(
            self.has_permission(user_roles, perm)
            for perm in required_permissions
        )
    
    def get_user_permissions(self, user_roles: List[str]) -> Set[Permission]:
        """
        Get all permissions for user based on roles
        """
        permissions = set()
        
        for role_str in user_roles:
            try:
                role = Role(role_str)
                permissions.update(self.role_permissions.get(role, set()))
            except ValueError:
                logger.warning(f"Invalid role: {role_str}")
                continue
        
        return permissions
    
    def check_resource_access(
        self,
        user_roles: List[str],
        resource_type: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Check if user can access resource with specific action
        
        Args:
            user_roles: User's roles
            resource_type: Type of resource (patient, observation, etc.)
            action: Action to perform (read, write, delete)
            
        Returns:
            Dictionary with access decision and details
        """
        # Map resource and action to permission
        permission_map = {
            'patient': {
                'read': Permission.PATIENT_READ,
                'write': Permission.PATIENT_WRITE,
                'delete': Permission.PATIENT_DELETE,
                'export': Permission.PATIENT_EXPORT,
            },
            'observation': {
                'read': Permission.OBSERVATION_READ,
                'write': Permission.OBSERVATION_WRITE,
                'delete': Permission.OBSERVATION_DELETE,
            },
            'medication': {
                'read': Permission.MEDICATION_READ,
                'write': Permission.MEDICATION_WRITE,
                'delete': Permission.MEDICATION_DELETE,
                'prescribe': Permission.MEDICATION_PRESCRIBE,
            },
            'allergy': {
                'read': Permission.ALLERGY_READ,
                'write': Permission.ALLERGY_WRITE,
                'delete': Permission.ALLERGY_DELETE,
            },
            'hl7': {
                'read': Permission.HL7_READ,
                'send': Permission.HL7_SEND,
                'receive': Permission.HL7_RECEIVE,
            },
            'connection': {
                'read': Permission.CONNECTION_READ,
                'write': Permission.CONNECTION_WRITE,
                'delete': Permission.CONNECTION_DELETE,
                'test': Permission.CONNECTION_TEST,
            },
            'audit': {
                'read': Permission.AUDIT_READ,
                'export': Permission.AUDIT_EXPORT,
            }
        }
        
        required_permission = permission_map.get(resource_type, {}).get(action)
        
        if not required_permission:
            return {
                'allowed': False,
                'reason': f'Unknown resource type or action: {resource_type}:{action}'
            }
        
        has_access = self.has_permission(user_roles, required_permission)
        
        result = {
            'allowed': has_access,
            'resource_type': resource_type,
            'action': action,
            'required_permission': required_permission.value,
            'user_roles': user_roles,
            'timestamp': datetime.now().isoformat()
        }
        
        if has_access:
            result['reason'] = 'User has required permission'
        else:
            result['reason'] = 'User lacks required permission'
        
        # Log access attempt
        self._log_access_attempt(result)
        
        return result
    
    def _log_access_attempt(self, access_result: Dict[str, Any]):
        """
        Log access attempt for audit trail
        """
        self.access_logs.append(access_result)
    
    def get_access_logs(
        self,
        user_roles: Optional[List[str]] = None,
        resource_type: Optional[str] = None,
        allowed_only: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get access logs with optional filters
        """
        logs = self.access_logs
        
        if user_roles:
            logs = [log for log in logs if any(role in log.get('user_roles', []) for role in user_roles)]
        
        if resource_type:
            logs = [log for log in logs if log.get('resource_type') == resource_type]
        
        if allowed_only is not None:
            logs = [log for log in logs if log.get('allowed') == allowed_only]
        
        return logs
    
    def add_role_permission(self, role: Role, permission: Permission):
        """
        Add permission to role (for dynamic permission management)
        """
        if role not in self.role_permissions:
            self.role_permissions[role] = set()
        
        self.role_permissions[role].add(permission)
        logger.info(f"Added permission {permission.value} to role {role.value}")
    
    def remove_role_permission(self, role: Role, permission: Permission):
        """
        Remove permission from role
        """
        if role in self.role_permissions:
            self.role_permissions[role].discard(permission)
            logger.info(f"Removed permission {permission.value} from role {role.value}")
    
    def create_custom_role(
        self,
        role_name: str,
        permissions: Set[Permission]
    ) -> Role:
        """
        Create custom role with specific permissions
        """
        # This would typically integrate with a database
        # For now, we'll just add to the in-memory mapping
        custom_role = Role(role_name)
        self.role_permissions[custom_role] = permissions
        
        logger.info(f"Created custom role: {role_name} with {len(permissions)} permissions")
        return custom_role


class ContextualAccessControl:
    """
    Context-aware access control
    Considers additional factors beyond roles
    """
    
    def __init__(self, access_control: AccessControl):
        self.access_control = access_control
    
    def check_contextual_access(
        self,
        user_roles: List[str],
        resource_type: str,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check access with additional context
        
        Context may include:
        - time_of_day: Access restrictions by time
        - location: IP-based location restrictions
        - patient_relationship: User's relationship to patient
        - emergency: Emergency access override
        """
        # First check basic RBAC
        basic_access = self.access_control.check_resource_access(
            user_roles,
            resource_type,
            action
        )
        
        if not basic_access['allowed']:
            return basic_access
        
        # Apply contextual rules
        contextual_checks = []
        
        # Time-based access
        if 'time_of_day' in context:
            time_check = self._check_time_restriction(context['time_of_day'])
            contextual_checks.append(time_check)
        
        # Location-based access
        if 'location' in context:
            location_check = self._check_location_restriction(context['location'])
            contextual_checks.append(location_check)
        
        # Emergency override
        if context.get('emergency', False):
            return {
                'allowed': True,
                'reason': 'Emergency access override',
                'emergency': True,
                'requires_justification': True
            }
        
        # Check if all contextual checks passed
        all_passed = all(check['allowed'] for check in contextual_checks)
        
        result = basic_access.copy()
        result['contextual_checks'] = contextual_checks
        result['allowed'] = all_passed
        
        if not all_passed:
            failed_checks = [check for check in contextual_checks if not check['allowed']]
            result['reason'] = f"Contextual restrictions: {', '.join(c['reason'] for c in failed_checks)}"
        
        return result
    
    def _check_time_restriction(self, time_of_day: str) -> Dict[str, bool]:
        """
        Check time-based access restrictions
        """
        # Example: Restrict certain operations to business hours
        hour = datetime.now().hour
        
        if 8 <= hour <= 18:  # Business hours
            return {'allowed': True, 'reason': 'Within business hours'}
        else:
            return {'allowed': False, 'reason': 'Outside business hours'}
    
    def _check_location_restriction(self, location: str) -> Dict[str, bool]:
        """
        Check location-based access restrictions
        """
        # Example: Restrict access from certain locations
        allowed_locations = ['internal_network', 'vpn', 'trusted_ip']
        
        if location in allowed_locations:
            return {'allowed': True, 'reason': 'Trusted location'}
        else:
            return {'allowed': False, 'reason': 'Untrusted location'}


# Global access control instance
access_control = AccessControl()
contextual_access_control = ContextualAccessControl(access_control)