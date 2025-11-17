"""
iTechSmart Citadel - Configuration Management
Sovereign Digital Infrastructure Platform

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "iTechSmart Citadel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://citadel:citadel@localhost:5435/citadel"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/5")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "citadel-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Post-Quantum Cryptography
    PQC_ENABLED: bool = os.getenv("PQC_ENABLED", "true").lower() == "true"
    PQC_ALGORITHM: str = os.getenv("PQC_ALGORITHM", "CRYSTALS-Kyber")
    KEY_ROTATION_DAYS: int = int(os.getenv("KEY_ROTATION_DAYS", "90"))

    # SIEM/XDR
    SIEM_ENABLED: bool = os.getenv("SIEM_ENABLED", "true").lower() == "true"
    XDR_ENABLED: bool = os.getenv("XDR_ENABLED", "true").lower() == "true"
    ALERT_RETENTION_DAYS: int = int(os.getenv("ALERT_RETENTION_DAYS", "365"))

    # Threat Intelligence
    THREAT_INTEL_ENABLED: bool = (
        os.getenv("THREAT_INTEL_ENABLED", "true").lower() == "true"
    )
    THREAT_FEED_UPDATE_INTERVAL: int = int(
        os.getenv("THREAT_FEED_UPDATE_INTERVAL", "3600")
    )

    # Compliance
    COMPLIANCE_FRAMEWORKS: list = [
        "HIPAA",
        "PCI-DSS",
        "SOC2",
        "ISO27001",
        "NIST",
        "GDPR",
    ]
    COMPLIANCE_SCAN_INTERVAL: int = int(os.getenv("COMPLIANCE_SCAN_INTERVAL", "86400"))

    # Zero Trust
    ZERO_TRUST_ENABLED: bool = os.getenv("ZERO_TRUST_ENABLED", "true").lower() == "true"
    MFA_REQUIRED: bool = os.getenv("MFA_REQUIRED", "true").lower() == "true"
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "15"))

    # Network Security
    IDS_ENABLED: bool = os.getenv("IDS_ENABLED", "true").lower() == "true"
    IPS_ENABLED: bool = os.getenv("IPS_ENABLED", "true").lower() == "true"
    DPI_ENABLED: bool = os.getenv("DPI_ENABLED", "true").lower() == "true"

    # Backup & Recovery
    IMMUTABLE_BACKUP_ENABLED: bool = (
        os.getenv("IMMUTABLE_BACKUP_ENABLED", "true").lower() == "true"
    )
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "90"))
    BACKUP_ENCRYPTION: bool = os.getenv("BACKUP_ENCRYPTION", "true").lower() == "true"

    # Hardware Security
    HSM_ENABLED: bool = os.getenv("HSM_ENABLED", "false").lower() == "true"
    TPM_ENABLED: bool = os.getenv("TPM_ENABLED", "true").lower() == "true"
    SECURE_BOOT_ENABLED: bool = (
        os.getenv("SECURE_BOOT_ENABLED", "true").lower() == "true"
    )

    # Monitoring
    METRICS_RETENTION_DAYS: int = int(os.getenv("METRICS_RETENTION_DAYS", "90"))
    LOG_RETENTION_DAYS: int = int(os.getenv("LOG_RETENTION_DAYS", "365"))

    # iTechSmart Hub Integration
    HUB_URL: str = os.getenv("HUB_URL", "http://localhost:8000")
    HUB_API_KEY: Optional[str] = os.getenv("HUB_API_KEY")

    # iTechSmart Shield Integration
    SHIELD_URL: str = os.getenv("SHIELD_URL", "http://localhost:8018")
    SHIELD_API_KEY: Optional[str] = os.getenv("SHIELD_API_KEY")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/citadel.log")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Security event types
SECURITY_EVENT_TYPES = {
    "intrusion": {
        "severity": "critical",
        "auto_response": True,
        "actions": ["isolate", "block", "alert"],
    },
    "malware": {
        "severity": "critical",
        "auto_response": True,
        "actions": ["quarantine", "scan", "alert"],
    },
    "anomaly": {
        "severity": "high",
        "auto_response": False,
        "actions": ["investigate", "monitor"],
    },
    "unauthorized_access": {
        "severity": "high",
        "auto_response": True,
        "actions": ["block", "alert", "audit"],
    },
    "data_exfiltration": {
        "severity": "critical",
        "auto_response": True,
        "actions": ["block", "isolate", "alert"],
    },
    "policy_violation": {
        "severity": "medium",
        "auto_response": False,
        "actions": ["alert", "audit"],
    },
}

# Threat intelligence indicator types
INDICATOR_TYPES = [
    "ip",
    "domain",
    "url",
    "hash_md5",
    "hash_sha1",
    "hash_sha256",
    "email",
    "file_path",
    "registry_key",
    "mutex",
]

# Compliance frameworks
COMPLIANCE_FRAMEWORKS_CONFIG = {
    "HIPAA": {
        "name": "Health Insurance Portability and Accountability Act",
        "requirements": [
            "Access Control",
            "Audit Controls",
            "Integrity Controls",
            "Transmission Security",
            "Encryption",
        ],
    },
    "PCI-DSS": {
        "name": "Payment Card Industry Data Security Standard",
        "requirements": [
            "Firewall Configuration",
            "Password Protection",
            "Data Encryption",
            "Antivirus Software",
            "Access Control",
        ],
    },
    "SOC2": {
        "name": "Service Organization Control 2",
        "requirements": [
            "Security",
            "Availability",
            "Processing Integrity",
            "Confidentiality",
            "Privacy",
        ],
    },
    "ISO27001": {
        "name": "Information Security Management",
        "requirements": [
            "Risk Assessment",
            "Security Policy",
            "Asset Management",
            "Access Control",
            "Cryptography",
        ],
    },
    "NIST": {
        "name": "NIST Cybersecurity Framework",
        "requirements": ["Identify", "Protect", "Detect", "Respond", "Recover"],
    },
    "GDPR": {
        "name": "General Data Protection Regulation",
        "requirements": [
            "Data Protection",
            "Privacy by Design",
            "Data Breach Notification",
            "Right to Erasure",
            "Data Portability",
        ],
    },
}

# Post-quantum cryptography algorithms
PQC_ALGORITHMS = {
    "CRYSTALS-Kyber": {
        "type": "key_encapsulation",
        "security_level": "high",
        "key_size": 1568,
    },
    "CRYSTALS-Dilithium": {
        "type": "digital_signature",
        "security_level": "high",
        "signature_size": 2420,
    },
    "FALCON": {
        "type": "digital_signature",
        "security_level": "high",
        "signature_size": 666,
    },
    "SPHINCS+": {
        "type": "digital_signature",
        "security_level": "high",
        "signature_size": 7856,
    },
}

# Security control types
SECURITY_CONTROL_TYPES = [
    "firewall",
    "ids",
    "ips",
    "waf",
    "dlp",
    "encryption",
    "mfa",
    "siem",
    "edr",
    "xdr",
]

# Incident response actions
INCIDENT_RESPONSE_ACTIONS = {
    "isolate": {
        "description": "Isolate affected system from network",
        "severity": "critical",
        "automated": True,
    },
    "block": {
        "description": "Block malicious IP/domain",
        "severity": "high",
        "automated": True,
    },
    "quarantine": {
        "description": "Quarantine malicious file",
        "severity": "high",
        "automated": True,
    },
    "investigate": {
        "description": "Initiate investigation",
        "severity": "medium",
        "automated": False,
    },
    "remediate": {
        "description": "Apply remediation",
        "severity": "medium",
        "automated": True,
    },
    "alert": {
        "description": "Send alert notification",
        "severity": "all",
        "automated": True,
    },
}
