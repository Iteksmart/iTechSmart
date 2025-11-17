"""
iTechSmart Compliance - Enhanced Database Models
Compliance Center with SOC2/ISO/HIPAA tracking
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""

    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"
    CCPA = "ccpa"
    NIST = "nist"
    FISMA = "fisma"


class ControlStatus(str, Enum):
    """Control implementation status"""

    IMPLEMENTED = "implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    NOT_IMPLEMENTED = "not_implemented"
    PLANNED = "planned"
    NOT_APPLICABLE = "not_applicable"


class ComplianceStatus(str, Enum):
    """Overall compliance status"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    NOT_ASSESSED = "not_assessed"


class EvidenceType(str, Enum):
    """Types of compliance evidence"""

    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    LOG_FILE = "log_file"
    POLICY = "policy"
    PROCEDURE = "procedure"
    AUDIT_REPORT = "audit_report"
    CERTIFICATE = "certificate"
    ATTESTATION = "attestation"


class RiskLevel(str, Enum):
    """Risk severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# ============================================================================
# COMPLIANCE CENTER MODELS
# ============================================================================


class ComplianceControl:
    """
    Represents a compliance control from any framework
    """

    def __init__(
        self,
        control_id: str,
        framework: ComplianceFramework,
        control_number: str,
        title: str,
        description: str,
        category: str,
        domain: str,
        requirement: str,
    ):
        self.control_id = control_id
        self.framework = framework
        self.control_number = control_number
        self.title = title
        self.description = description
        self.category = category
        self.domain = domain
        self.requirement = requirement
        self.status = ControlStatus.NOT_IMPLEMENTED
        self.implementation_date: Optional[datetime] = None
        self.last_assessed: Optional[datetime] = None
        self.next_assessment: Optional[datetime] = None
        self.assigned_to: Optional[str] = None
        self.owner: Optional[str] = None
        self.evidence_ids: List[str] = []
        self.gap_analysis: Optional[str] = None
        self.remediation_plan: Optional[str] = None
        self.notes: str = ""
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ComplianceEvidence:
    """
    Evidence supporting compliance control implementation
    """

    def __init__(
        self,
        evidence_id: str,
        control_id: str,
        evidence_type: EvidenceType,
        title: str,
        description: str,
        file_path: Optional[str] = None,
    ):
        self.evidence_id = evidence_id
        self.control_id = control_id
        self.evidence_type = evidence_type
        self.title = title
        self.description = description
        self.file_path = file_path
        self.file_size: Optional[int] = None
        self.file_hash: Optional[str] = None
        self.collected_by: Optional[str] = None
        self.collected_at = datetime.utcnow()
        self.verified_by: Optional[str] = None
        self.verified_at: Optional[datetime] = None
        self.expiration_date: Optional[datetime] = None
        self.metadata: dict = {}
        self.created_at = datetime.utcnow()


class ComplianceAssessment:
    """
    Compliance assessment/audit session
    """

    def __init__(
        self,
        assessment_id: str,
        framework: ComplianceFramework,
        assessment_type: str,
        assessor: str,
        scope: str,
    ):
        self.assessment_id = assessment_id
        self.framework = framework
        self.assessment_type = assessment_type  # internal, external, self
        self.assessor = assessor
        self.scope = scope
        self.started_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self.status = "in_progress"
        self.controls_assessed = 0
        self.controls_passed = 0
        self.controls_failed = 0
        self.controls_partial = 0
        self.overall_score: float = 0.0
        self.findings_count = 0
        self.critical_findings = 0
        self.high_findings = 0
        self.medium_findings = 0
        self.low_findings = 0
        self.report_path: Optional[str] = None
        self.notes: str = ""
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ComplianceFinding:
    """
    Compliance gap or issue identified during assessment
    """

    def __init__(
        self,
        finding_id: str,
        assessment_id: str,
        control_id: str,
        severity: RiskLevel,
        title: str,
        description: str,
    ):
        self.finding_id = finding_id
        self.assessment_id = assessment_id
        self.control_id = control_id
        self.severity = severity
        self.title = title
        self.description = description
        self.impact: Optional[str] = None
        self.recommendation: Optional[str] = None
        self.remediation_plan: Optional[str] = None
        self.status = "open"  # open, in_progress, resolved, accepted
        self.assigned_to: Optional[str] = None
        self.due_date: Optional[datetime] = None
        self.resolved_at: Optional[datetime] = None
        self.resolved_by: Optional[str] = None
        self.resolution_notes: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class PolicyDocument:
    """
    Organizational policy document
    """

    def __init__(
        self, policy_id: str, title: str, policy_type: str, version: str, owner: str
    ):
        self.policy_id = policy_id
        self.title = title
        self.policy_type = policy_type  # security, privacy, operational, etc.
        self.version = version
        self.owner = owner
        self.description: Optional[str] = None
        self.file_path: Optional[str] = None
        self.status = "draft"  # draft, review, approved, archived
        self.approved_by: Optional[str] = None
        self.approved_at: Optional[datetime] = None
        self.effective_date: Optional[datetime] = None
        self.review_date: Optional[datetime] = None
        self.next_review_date: Optional[datetime] = None
        self.related_frameworks: List[ComplianceFramework] = []
        self.related_controls: List[str] = []
        self.tags: List[str] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ComplianceReport:
    """
    Generated compliance report
    """

    def __init__(
        self,
        report_id: str,
        report_type: str,
        framework: ComplianceFramework,
        generated_by: str,
    ):
        self.report_id = report_id
        self.report_type = report_type  # assessment, gap_analysis, executive, audit
        self.framework = framework
        self.generated_by = generated_by
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.period_start: Optional[datetime] = None
        self.period_end: Optional[datetime] = None
        self.file_path: Optional[str] = None
        self.file_format = "pdf"  # pdf, html, docx
        self.overall_status: Optional[ComplianceStatus] = None
        self.compliance_score: float = 0.0
        self.total_controls = 0
        self.compliant_controls = 0
        self.non_compliant_controls = 0
        self.findings_summary: dict = {}
        self.recommendations: List[str] = []
        self.generated_at = datetime.utcnow()
        self.created_at = datetime.utcnow()


class AuditTrail:
    """
    Audit trail for compliance activities
    """

    def __init__(
        self, trail_id: str, entity_type: str, entity_id: str, action: str, user: str
    ):
        self.trail_id = trail_id
        self.entity_type = entity_type  # control, evidence, assessment, etc.
        self.entity_id = entity_id
        self.action = action  # created, updated, deleted, assessed, etc.
        self.user = user
        self.timestamp = datetime.utcnow()
        self.ip_address: Optional[str] = None
        self.user_agent: Optional[str] = None
        self.changes: dict = {}
        self.metadata: dict = {}


# ============================================================================
# FRAMEWORK-SPECIFIC MODELS
# ============================================================================


class SOC2Control(ComplianceControl):
    """
    SOC2-specific control with trust service criteria
    """

    def __init__(
        self,
        control_id: str,
        control_number: str,
        title: str,
        description: str,
        category: str,
        domain: str,
        requirement: str,
        trust_service_criteria: str,
    ):
        super().__init__(
            control_id=control_id,
            framework=ComplianceFramework.SOC2,
            control_number=control_number,
            title=title,
            description=description,
            category=category,
            domain=domain,
            requirement=requirement,
        )
        self.trust_service_criteria = trust_service_criteria  # CC, A, PI, C, P
        self.common_criteria_related: bool = False


class ISO27001Control(ComplianceControl):
    """
    ISO 27001-specific control
    """

    def __init__(
        self,
        control_id: str,
        control_number: str,
        title: str,
        description: str,
        category: str,
        domain: str,
        requirement: str,
        annex_section: str,
    ):
        super().__init__(
            control_id=control_id,
            framework=ComplianceFramework.ISO27001,
            control_number=control_number,
            title=title,
            description=description,
            category=category,
            domain=domain,
            requirement=requirement,
        )
        self.annex_section = annex_section  # A.5, A.6, etc.
        self.iso_clause: Optional[str] = None


class HIPAAControl(ComplianceControl):
    """
    HIPAA-specific control
    """

    def __init__(
        self,
        control_id: str,
        control_number: str,
        title: str,
        description: str,
        category: str,
        domain: str,
        requirement: str,
        safeguard_type: str,
    ):
        super().__init__(
            control_id=control_id,
            framework=ComplianceFramework.HIPAA,
            control_number=control_number,
            title=title,
            description=description,
            category=category,
            domain=domain,
            requirement=requirement,
        )
        self.safeguard_type = safeguard_type  # administrative, physical, technical
        self.is_required: bool = True
        self.is_addressable: bool = False
        self.phi_related: bool = True
