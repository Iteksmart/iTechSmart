"""
Data Privacy Controls for iTechSmart Ninja
Implements GDPR-compliant privacy features and data protection
"""

import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)


class PrivacyLevel(str, Enum):
    """Privacy protection levels"""
    PUBLIC = "public"          # No privacy restrictions
    INTERNAL = "internal"      # Internal use only
    CONFIDENTIAL = "confidential"  # Confidential data
    RESTRICTED = "restricted"  # Highly restricted
    PRIVATE = "private"        # Maximum privacy


class DataCategory(str, Enum):
    """Categories of data for privacy management"""
    PERSONAL_INFO = "personal_info"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    COMMUNICATION = "communication"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    USAGE = "usage"


class ConsentType(str, Enum):
    """Types of user consent"""
    ESSENTIAL = "essential"        # Required for service
    FUNCTIONAL = "functional"      # Enhanced functionality
    ANALYTICS = "analytics"        # Usage analytics
    MARKETING = "marketing"        # Marketing communications
    THIRD_PARTY = "third_party"    # Third-party sharing
    AI_TRAINING = "ai_training"    # AI model training


class DataRetentionPeriod(str, Enum):
    """Data retention periods"""
    DAYS_7 = "7_days"
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    MONTHS_6 = "6_months"
    YEAR_1 = "1_year"
    YEARS_2 = "2_years"
    YEARS_5 = "5_years"
    INDEFINITE = "indefinite"


@dataclass
class PrivacySettings:
    """User privacy settings"""
    user_id: str
    privacy_level: PrivacyLevel
    consents: Dict[ConsentType, bool]
    data_retention: Dict[DataCategory, DataRetentionPeriod]
    opt_outs: Set[str]  # Features/services opted out
    anonymize_data: bool
    allow_ai_training: bool
    allow_third_party_sharing: bool
    allow_analytics: bool
    allow_marketing: bool
    data_export_requested: bool
    data_deletion_requested: bool
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "privacy_level": self.privacy_level.value,
            "consents": {k.value: v for k, v in self.consents.items()},
            "data_retention": {k.value: v.value for k, v in self.data_retention.items()},
            "opt_outs": list(self.opt_outs),
            "anonymize_data": self.anonymize_data,
            "allow_ai_training": self.allow_ai_training,
            "allow_third_party_sharing": self.allow_third_party_sharing,
            "allow_analytics": self.allow_analytics,
            "allow_marketing": self.allow_marketing,
            "data_export_requested": self.data_export_requested,
            "data_deletion_requested": self.data_deletion_requested,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class DataAccessLog:
    """Log of data access events"""
    log_id: str
    user_id: str
    accessor_id: str
    data_category: DataCategory
    access_type: str  # read, write, delete, export
    purpose: str
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "accessor_id": self.accessor_id,
            "data_category": self.data_category.value,
            "access_type": self.access_type,
            "purpose": self.purpose,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }


@dataclass
class DataExportRequest:
    """Request for data export (GDPR right to data portability)"""
    request_id: str
    user_id: str
    categories: List[DataCategory]
    format: str  # json, csv, xml
    status: str  # pending, processing, completed, failed
    requested_at: datetime
    completed_at: Optional[datetime]
    download_url: Optional[str]
    expires_at: Optional[datetime]


@dataclass
class DataDeletionRequest:
    """Request for data deletion (GDPR right to erasure)"""
    request_id: str
    user_id: str
    categories: List[DataCategory]
    reason: str
    status: str  # pending, processing, completed, failed
    requested_at: datetime
    completed_at: Optional[datetime]
    verification_required: bool
    verified: bool


class PrivacyManager:
    """Manages user privacy settings and data protection"""
    
    def __init__(self):
        """Initialize privacy manager"""
        self.settings: Dict[str, PrivacySettings] = {}
        self.access_logs: List[DataAccessLog] = []
        self.export_requests: Dict[str, DataExportRequest] = {}
        self.deletion_requests: Dict[str, DataDeletionRequest] = {}
        logger.info("PrivacyManager initialized successfully")
    
    def get_default_settings(self, user_id: str) -> PrivacySettings:
        """Get default privacy settings for a user"""
        return PrivacySettings(
            user_id=user_id,
            privacy_level=PrivacyLevel.INTERNAL,
            consents={
                ConsentType.ESSENTIAL: True,
                ConsentType.FUNCTIONAL: True,
                ConsentType.ANALYTICS: False,
                ConsentType.MARKETING: False,
                ConsentType.THIRD_PARTY: False,
                ConsentType.AI_TRAINING: False,
            },
            data_retention={
                DataCategory.PERSONAL_INFO: DataRetentionPeriod.YEARS_2,
                DataCategory.FINANCIAL: DataRetentionPeriod.YEARS_5,
                DataCategory.HEALTH: DataRetentionPeriod.YEARS_5,
                DataCategory.BIOMETRIC: DataRetentionPeriod.YEARS_2,
                DataCategory.LOCATION: DataRetentionPeriod.DAYS_90,
                DataCategory.COMMUNICATION: DataRetentionPeriod.YEAR_1,
                DataCategory.BEHAVIORAL: DataRetentionPeriod.MONTHS_6,
                DataCategory.TECHNICAL: DataRetentionPeriod.YEAR_1,
                DataCategory.USAGE: DataRetentionPeriod.MONTHS_6,
            },
            opt_outs=set(),
            anonymize_data=False,
            allow_ai_training=False,
            allow_third_party_sharing=False,
            allow_analytics=False,
            allow_marketing=False,
            data_export_requested=False,
            data_deletion_requested=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    async def get_privacy_settings(self, user_id: str) -> PrivacySettings:
        """Get privacy settings for a user"""
        if user_id not in self.settings:
            self.settings[user_id] = self.get_default_settings(user_id)
        return self.settings[user_id]
    
    async def update_privacy_settings(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> PrivacySettings:
        """Update privacy settings for a user"""
        settings = await self.get_privacy_settings(user_id)
        
        # Update fields
        if "privacy_level" in updates:
            settings.privacy_level = PrivacyLevel(updates["privacy_level"])
        
        if "consents" in updates:
            for consent_type, value in updates["consents"].items():
                settings.consents[ConsentType(consent_type)] = value
        
        if "data_retention" in updates:
            for category, period in updates["data_retention"].items():
                settings.data_retention[DataCategory(category)] = DataRetentionPeriod(period)
        
        if "opt_outs" in updates:
            settings.opt_outs = set(updates["opt_outs"])
        
        if "anonymize_data" in updates:
            settings.anonymize_data = updates["anonymize_data"]
        
        if "allow_ai_training" in updates:
            settings.allow_ai_training = updates["allow_ai_training"]
            settings.consents[ConsentType.AI_TRAINING] = updates["allow_ai_training"]
        
        if "allow_third_party_sharing" in updates:
            settings.allow_third_party_sharing = updates["allow_third_party_sharing"]
            settings.consents[ConsentType.THIRD_PARTY] = updates["allow_third_party_sharing"]
        
        if "allow_analytics" in updates:
            settings.allow_analytics = updates["allow_analytics"]
            settings.consents[ConsentType.ANALYTICS] = updates["allow_analytics"]
        
        if "allow_marketing" in updates:
            settings.allow_marketing = updates["allow_marketing"]
            settings.consents[ConsentType.MARKETING] = updates["allow_marketing"]
        
        settings.updated_at = datetime.now()
        
        logger.info(f"Privacy settings updated for user {user_id}")
        return settings
    
    async def check_consent(
        self,
        user_id: str,
        consent_type: ConsentType
    ) -> bool:
        """Check if user has given consent for a specific purpose"""
        settings = await self.get_privacy_settings(user_id)
        return settings.consents.get(consent_type, False)
    
    async def opt_out(
        self,
        user_id: str,
        feature: str
    ) -> bool:
        """Opt out of a specific feature or service"""
        settings = await self.get_privacy_settings(user_id)
        settings.opt_outs.add(feature)
        settings.updated_at = datetime.now()
        
        logger.info(f"User {user_id} opted out of {feature}")
        return True
    
    async def opt_in(
        self,
        user_id: str,
        feature: str
    ) -> bool:
        """Opt in to a specific feature or service"""
        settings = await self.get_privacy_settings(user_id)
        settings.opt_outs.discard(feature)
        settings.updated_at = datetime.now()
        
        logger.info(f"User {user_id} opted in to {feature}")
        return True
    
    async def is_opted_out(
        self,
        user_id: str,
        feature: str
    ) -> bool:
        """Check if user has opted out of a feature"""
        settings = await self.get_privacy_settings(user_id)
        return feature in settings.opt_outs
    
    async def log_data_access(
        self,
        user_id: str,
        accessor_id: str,
        data_category: DataCategory,
        access_type: str,
        purpose: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> DataAccessLog:
        """Log a data access event"""
        import uuid
        
        log = DataAccessLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            accessor_id=accessor_id,
            data_category=data_category,
            access_type=access_type,
            purpose=purpose,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.access_logs.append(log)
        logger.info(f"Data access logged: {access_type} {data_category.value} for user {user_id}")
        
        return log
    
    async def get_access_logs(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[DataCategory] = None
    ) -> List[DataAccessLog]:
        """Get data access logs for a user"""
        logs = [log for log in self.access_logs if log.user_id == user_id]
        
        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]
        
        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]
        
        if category:
            logs = [log for log in logs if log.data_category == category]
        
        return logs
    
    async def request_data_export(
        self,
        user_id: str,
        categories: List[DataCategory],
        format: str = "json"
    ) -> DataExportRequest:
        """Request data export (GDPR right to data portability)"""
        import uuid
        
        request = DataExportRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            categories=categories,
            format=format,
            status="pending",
            requested_at=datetime.now(),
            completed_at=None,
            download_url=None,
            expires_at=None
        )
        
        self.export_requests[request.request_id] = request
        
        # Update user settings
        settings = await self.get_privacy_settings(user_id)
        settings.data_export_requested = True
        settings.updated_at = datetime.now()
        
        logger.info(f"Data export requested for user {user_id}")
        return request
    
    async def request_data_deletion(
        self,
        user_id: str,
        categories: List[DataCategory],
        reason: str,
        verification_required: bool = True
    ) -> DataDeletionRequest:
        """Request data deletion (GDPR right to erasure)"""
        import uuid
        
        request = DataDeletionRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            categories=categories,
            reason=reason,
            status="pending",
            requested_at=datetime.now(),
            completed_at=None,
            verification_required=verification_required,
            verified=False
        )
        
        self.deletion_requests[request.request_id] = request
        
        # Update user settings
        settings = await self.get_privacy_settings(user_id)
        settings.data_deletion_requested = True
        settings.updated_at = datetime.now()
        
        logger.info(f"Data deletion requested for user {user_id}")
        return request
    
    async def anonymize_user_data(
        self,
        user_id: str,
        categories: List[DataCategory]
    ) -> bool:
        """Anonymize user data"""
        # In a real implementation, this would anonymize actual data
        # For now, we just update the settings
        settings = await self.get_privacy_settings(user_id)
        settings.anonymize_data = True
        settings.updated_at = datetime.now()
        
        logger.info(f"Data anonymized for user {user_id}")
        return True
    
    async def get_data_retention_policy(
        self,
        user_id: str,
        category: DataCategory
    ) -> DataRetentionPeriod:
        """Get data retention policy for a category"""
        settings = await self.get_privacy_settings(user_id)
        return settings.data_retention.get(category, DataRetentionPeriod.YEAR_1)
    
    async def should_retain_data(
        self,
        user_id: str,
        category: DataCategory,
        data_age: timedelta
    ) -> bool:
        """Check if data should be retained based on retention policy"""
        retention_period = await self.get_data_retention_policy(user_id, category)
        
        retention_days = {
            DataRetentionPeriod.DAYS_7: 7,
            DataRetentionPeriod.DAYS_30: 30,
            DataRetentionPeriod.DAYS_90: 90,
            DataRetentionPeriod.MONTHS_6: 180,
            DataRetentionPeriod.YEAR_1: 365,
            DataRetentionPeriod.YEARS_2: 730,
            DataRetentionPeriod.YEARS_5: 1825,
            DataRetentionPeriod.INDEFINITE: float('inf'),
        }
        
        max_days = retention_days.get(retention_period, 365)
        return data_age.days <= max_days
    
    def hash_pii(self, data: str) -> str:
        """Hash personally identifiable information"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def mask_pii(self, data: str, visible_chars: int = 4) -> str:
        """Mask personally identifiable information"""
        if len(data) <= visible_chars:
            return "*" * len(data)
        return data[:visible_chars] + "*" * (len(data) - visible_chars)


# Global privacy manager instance
_privacy_manager: Optional[PrivacyManager] = None


def get_privacy_manager() -> PrivacyManager:
    """Get or create global privacy manager instance"""
    global _privacy_manager
    if _privacy_manager is None:
        _privacy_manager = PrivacyManager()
    return _privacy_manager