"""
iTechSmart Compliance - Compliance Center Engine
Enhanced compliance tracking with SOC2/ISO/HIPAA support
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import json

from ..models.models import (
    ComplianceFramework,
    ComplianceControl,
    ComplianceEvidence,
    ComplianceAssessment,
    ComplianceFinding,
    PolicyDocument,
    ComplianceReport,
    AuditTrail,
    ControlStatus,
    ComplianceStatus,
    EvidenceType,
    RiskLevel,
    SOC2Control,
    ISO27001Control,
    HIPAAControl,
)


class ComplianceCenterEngine:
    """
    Enhanced compliance management engine with multi-framework support
    """

    def __init__(self):
        self.controls: Dict[str, ComplianceControl] = {}
        self.evidence: Dict[str, ComplianceEvidence] = {}
        self.assessments: Dict[str, ComplianceAssessment] = {}
        self.findings: Dict[str, ComplianceFinding] = {}
        self.policies: Dict[str, PolicyDocument] = {}
        self.reports: Dict[str, ComplianceReport] = {}
        self.audit_trails: List[AuditTrail] = []

        # Initialize framework control libraries
        self._initialize_soc2_controls()
        self._initialize_iso27001_controls()
        self._initialize_hipaa_controls()

    # ========================================================================
    # FRAMEWORK INITIALIZATION
    # ========================================================================

    def _initialize_soc2_controls(self):
        """Initialize SOC2 Type II control library"""
        soc2_controls = [
            # Common Criteria (CC) - Organization & Management
            {
                "control_number": "CC1.1",
                "title": "COSO Principle 1 - Demonstrates Commitment to Integrity and Ethical Values",
                "category": "Control Environment",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "The entity demonstrates a commitment to integrity and ethical values.",
            },
            {
                "control_number": "CC1.2",
                "title": "Board Independence and Oversight",
                "category": "Control Environment",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "The board of directors demonstrates independence from management.",
            },
            {
                "control_number": "CC2.1",
                "title": "Communication of Responsibilities",
                "category": "Communication and Information",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "The entity communicates internal control responsibilities.",
            },
            {
                "control_number": "CC3.1",
                "title": "Risk Assessment Process",
                "category": "Risk Assessment",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "The entity specifies objectives with sufficient clarity.",
            },
            {
                "control_number": "CC4.1",
                "title": "Monitoring Activities",
                "category": "Monitoring Activities",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "The entity selects, develops, and performs ongoing evaluations.",
            },
            {
                "control_number": "CC5.1",
                "title": "Control Activities",
                "category": "Control Activities",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "The entity selects and develops control activities.",
            },
            {
                "control_number": "CC6.1",
                "title": "Logical and Physical Access Controls",
                "category": "Logical and Physical Access",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "The entity implements logical access security software.",
            },
            {
                "control_number": "CC6.2",
                "title": "Access Control - Authentication",
                "category": "Logical and Physical Access",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "Prior to issuing system credentials, the entity registers and authorizes users.",
            },
            {
                "control_number": "CC7.1",
                "title": "System Operations",
                "category": "System Operations",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "The entity identifies, selects, and develops risk mitigation activities.",
            },
            {
                "control_number": "CC8.1",
                "title": "Change Management",
                "category": "Change Management",
                "domain": "Common Criteria",
                "trust_service_criteria": "CC",
                "description": "The entity authorizes, designs, develops, and tests changes.",
            },
            # Availability (A)
            {
                "control_number": "A1.1",
                "title": "Availability Commitments",
                "category": "Availability",
                "domain": "Availability",
                "trust_service_criteria": "A",
                "description": "The entity maintains availability commitments and system requirements.",
            },
            {
                "control_number": "A1.2",
                "title": "System Monitoring",
                "category": "Availability",
                "domain": "Availability",
                "trust_service_criteria": "A",
                "description": "The entity monitors system components for anomalies.",
            },
            # Confidentiality (C)
            {
                "control_number": "C1.1",
                "title": "Confidential Information Protection",
                "category": "Confidentiality",
                "domain": "Confidentiality",
                "trust_service_criteria": "C",
                "description": "The entity identifies and maintains confidential information.",
            },
            {
                "control_number": "C1.2",
                "title": "Confidential Information Disposal",
                "category": "Confidentiality",
                "domain": "Confidentiality",
                "trust_service_criteria": "C",
                "description": "The entity disposes of confidential information securely.",
            },
        ]

        for control_data in soc2_controls:
            control_id = (
                f"soc2_{control_data['control_number'].lower().replace('.', '_')}"
            )
            control = SOC2Control(
                control_id=control_id,
                control_number=control_data["control_number"],
                title=control_data["title"],
                description=control_data["description"],
                category=control_data["category"],
                domain=control_data["domain"],
                requirement="SOC 2 Type II",
                trust_service_criteria=control_data["trust_service_criteria"],
            )
            self.controls[control_id] = control

    def _initialize_iso27001_controls(self):
        """Initialize ISO 27001:2013 control library"""
        iso_controls = [
            # A.5 Information Security Policies
            {
                "control_number": "A.5.1.1",
                "title": "Policies for Information Security",
                "category": "Information Security Policies",
                "domain": "A.5",
                "annex_section": "A.5",
                "description": "A set of policies for information security shall be defined.",
            },
            {
                "control_number": "A.5.1.2",
                "title": "Review of Policies",
                "category": "Information Security Policies",
                "domain": "A.5",
                "annex_section": "A.5",
                "description": "Policies shall be reviewed at planned intervals.",
            },
            # A.6 Organization of Information Security
            {
                "control_number": "A.6.1.1",
                "title": "Information Security Roles and Responsibilities",
                "category": "Internal Organization",
                "domain": "A.6",
                "annex_section": "A.6",
                "description": "All information security responsibilities shall be defined.",
            },
            {
                "control_number": "A.6.1.2",
                "title": "Segregation of Duties",
                "category": "Internal Organization",
                "domain": "A.6",
                "annex_section": "A.6",
                "description": "Conflicting duties and areas of responsibility shall be segregated.",
            },
            # A.7 Human Resource Security
            {
                "control_number": "A.7.1.1",
                "title": "Screening",
                "category": "Prior to Employment",
                "domain": "A.7",
                "annex_section": "A.7",
                "description": "Background verification checks shall be carried out.",
            },
            {
                "control_number": "A.7.2.1",
                "title": "Management Responsibilities",
                "category": "During Employment",
                "domain": "A.7",
                "annex_section": "A.7",
                "description": "Management shall require employees to apply security.",
            },
            # A.8 Asset Management
            {
                "control_number": "A.8.1.1",
                "title": "Inventory of Assets",
                "category": "Responsibility for Assets",
                "domain": "A.8",
                "annex_section": "A.8",
                "description": "Assets associated with information shall be identified.",
            },
            {
                "control_number": "A.8.2.1",
                "title": "Classification of Information",
                "category": "Information Classification",
                "domain": "A.8",
                "annex_section": "A.8",
                "description": "Information shall be classified.",
            },
            # A.9 Access Control
            {
                "control_number": "A.9.1.1",
                "title": "Access Control Policy",
                "category": "Business Requirements",
                "domain": "A.9",
                "annex_section": "A.9",
                "description": "An access control policy shall be established.",
            },
            {
                "control_number": "A.9.2.1",
                "title": "User Registration and De-registration",
                "category": "User Access Management",
                "domain": "A.9",
                "annex_section": "A.9",
                "description": "A formal user registration process shall be implemented.",
            },
        ]

        for control_data in iso_controls:
            control_id = (
                f"iso_{control_data['control_number'].lower().replace('.', '_')}"
            )
            control = ISO27001Control(
                control_id=control_id,
                control_number=control_data["control_number"],
                title=control_data["title"],
                description=control_data["description"],
                category=control_data["category"],
                domain=control_data["domain"],
                requirement="ISO 27001:2013",
                annex_section=control_data["annex_section"],
            )
            self.controls[control_id] = control

    def _initialize_hipaa_controls(self):
        """Initialize HIPAA Security Rule controls"""
        hipaa_controls = [
            # Administrative Safeguards
            {
                "control_number": "164.308(a)(1)(i)",
                "title": "Security Management Process",
                "category": "Administrative Safeguards",
                "domain": "Administrative",
                "safeguard_type": "administrative",
                "is_required": True,
                "description": "Implement policies and procedures to prevent, detect, contain, and correct security violations.",
            },
            {
                "control_number": "164.308(a)(1)(ii)(A)",
                "title": "Risk Analysis",
                "category": "Administrative Safeguards",
                "domain": "Administrative",
                "safeguard_type": "administrative",
                "is_required": True,
                "description": "Conduct an accurate and thorough assessment of potential risks.",
            },
            {
                "control_number": "164.308(a)(3)(i)",
                "title": "Workforce Security",
                "category": "Administrative Safeguards",
                "domain": "Administrative",
                "safeguard_type": "administrative",
                "is_required": True,
                "description": "Implement policies and procedures to ensure workforce members have appropriate access.",
            },
            {
                "control_number": "164.308(a)(5)(i)",
                "title": "Security Awareness and Training",
                "category": "Administrative Safeguards",
                "domain": "Administrative",
                "safeguard_type": "administrative",
                "is_required": True,
                "description": "Implement security awareness and training program.",
            },
            # Physical Safeguards
            {
                "control_number": "164.310(a)(1)",
                "title": "Facility Access Controls",
                "category": "Physical Safeguards",
                "domain": "Physical",
                "safeguard_type": "physical",
                "is_required": True,
                "description": "Implement policies and procedures to limit physical access.",
            },
            {
                "control_number": "164.310(b)",
                "title": "Workstation Use",
                "category": "Physical Safeguards",
                "domain": "Physical",
                "safeguard_type": "physical",
                "is_required": True,
                "description": "Implement policies and procedures for workstation use.",
            },
            {
                "control_number": "164.310(d)(1)",
                "title": "Device and Media Controls",
                "category": "Physical Safeguards",
                "domain": "Physical",
                "safeguard_type": "physical",
                "is_required": True,
                "description": "Implement policies and procedures for electronic media.",
            },
            # Technical Safeguards
            {
                "control_number": "164.312(a)(1)",
                "title": "Access Control",
                "category": "Technical Safeguards",
                "domain": "Technical",
                "safeguard_type": "technical",
                "is_required": True,
                "description": "Implement technical policies and procedures for access.",
            },
            {
                "control_number": "164.312(b)",
                "title": "Audit Controls",
                "category": "Technical Safeguards",
                "domain": "Technical",
                "safeguard_type": "technical",
                "is_required": True,
                "description": "Implement hardware, software, and procedural mechanisms to record and examine activity.",
            },
            {
                "control_number": "164.312(c)(1)",
                "title": "Integrity",
                "category": "Technical Safeguards",
                "domain": "Technical",
                "safeguard_type": "technical",
                "is_required": True,
                "description": "Implement policies and procedures to protect ePHI from improper alteration.",
            },
            {
                "control_number": "164.312(d)",
                "title": "Person or Entity Authentication",
                "category": "Technical Safeguards",
                "domain": "Technical",
                "safeguard_type": "technical",
                "is_required": True,
                "description": "Implement procedures to verify person or entity seeking access.",
            },
            {
                "control_number": "164.312(e)(1)",
                "title": "Transmission Security",
                "category": "Technical Safeguards",
                "domain": "Technical",
                "safeguard_type": "technical",
                "is_required": True,
                "description": "Implement technical security measures to guard against unauthorized access.",
            },
        ]

        for control_data in hipaa_controls:
            control_id = f"hipaa_{control_data['control_number'].replace('(', '').replace(')', '').replace('.', '_')}"
            control = HIPAAControl(
                control_id=control_id,
                control_number=control_data["control_number"],
                title=control_data["title"],
                description=control_data["description"],
                category=control_data["category"],
                domain=control_data["domain"],
                requirement="HIPAA Security Rule",
                safeguard_type=control_data["safeguard_type"],
            )
            control.is_required = control_data["is_required"]
            self.controls[control_id] = control

    # ========================================================================
    # CONTROL MANAGEMENT
    # ========================================================================

    def get_controls_by_framework(
        self, framework: ComplianceFramework
    ) -> List[ComplianceControl]:
        """Get all controls for a specific framework"""
        return [c for c in self.controls.values() if c.framework == framework]

    def update_control_status(
        self,
        control_id: str,
        status: ControlStatus,
        user: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update control implementation status"""
        if control_id not in self.controls:
            return {"success": False, "error": "Control not found"}

        control = self.controls[control_id]
        old_status = control.status
        control.status = status
        control.updated_at = datetime.utcnow()

        if status == ControlStatus.IMPLEMENTED:
            control.implementation_date = datetime.utcnow()

        if notes:
            control.notes = notes

        # Create audit trail
        self._create_audit_trail(
            entity_type="control",
            entity_id=control_id,
            action="status_updated",
            user=user,
            changes={"old_status": old_status.value, "new_status": status.value},
        )

        return {
            "success": True,
            "control_id": control_id,
            "old_status": old_status.value,
            "new_status": status.value,
        }

    def assign_control(
        self, control_id: str, assigned_to: str, user: str
    ) -> Dict[str, Any]:
        """Assign control to a user"""
        if control_id not in self.controls:
            return {"success": False, "error": "Control not found"}

        control = self.controls[control_id]
        old_assignee = control.assigned_to
        control.assigned_to = assigned_to
        control.updated_at = datetime.utcnow()

        self._create_audit_trail(
            entity_type="control",
            entity_id=control_id,
            action="assigned",
            user=user,
            changes={"old_assignee": old_assignee, "new_assignee": assigned_to},
        )

        return {"success": True, "control_id": control_id, "assigned_to": assigned_to}

    # ========================================================================
    # EVIDENCE MANAGEMENT
    # ========================================================================

    def add_evidence(
        self,
        control_id: str,
        evidence_type: EvidenceType,
        title: str,
        description: str,
        file_path: Optional[str],
        user: str,
    ) -> Dict[str, Any]:
        """Add evidence for a control"""
        if control_id not in self.controls:
            return {"success": False, "error": "Control not found"}

        evidence_id = f"ev_{uuid4().hex[:12]}"
        evidence = ComplianceEvidence(
            evidence_id=evidence_id,
            control_id=control_id,
            evidence_type=evidence_type,
            title=title,
            description=description,
            file_path=file_path,
        )
        evidence.collected_by = user

        self.evidence[evidence_id] = evidence
        self.controls[control_id].evidence_ids.append(evidence_id)

        self._create_audit_trail(
            entity_type="evidence", entity_id=evidence_id, action="created", user=user
        )

        return {"success": True, "evidence_id": evidence_id}

    def verify_evidence(self, evidence_id: str, user: str) -> Dict[str, Any]:
        """Verify evidence"""
        if evidence_id not in self.evidence:
            return {"success": False, "error": "Evidence not found"}

        evidence = self.evidence[evidence_id]
        evidence.verified_by = user
        evidence.verified_at = datetime.utcnow()

        self._create_audit_trail(
            entity_type="evidence", entity_id=evidence_id, action="verified", user=user
        )

        return {"success": True, "evidence_id": evidence_id, "verified_by": user}

    # ========================================================================
    # ASSESSMENT MANAGEMENT
    # ========================================================================

    def create_assessment(
        self,
        framework: ComplianceFramework,
        assessment_type: str,
        assessor: str,
        scope: str,
    ) -> Dict[str, Any]:
        """Create new compliance assessment"""
        assessment_id = f"assess_{uuid4().hex[:12]}"
        assessment = ComplianceAssessment(
            assessment_id=assessment_id,
            framework=framework,
            assessment_type=assessment_type,
            assessor=assessor,
            scope=scope,
        )

        self.assessments[assessment_id] = assessment

        self._create_audit_trail(
            entity_type="assessment",
            entity_id=assessment_id,
            action="created",
            user=assessor,
        )

        return {"success": True, "assessment_id": assessment_id}

    def assess_control(
        self,
        assessment_id: str,
        control_id: str,
        passed: bool,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Assess a control during an assessment"""
        if assessment_id not in self.assessments:
            return {"success": False, "error": "Assessment not found"}
        if control_id not in self.controls:
            return {"success": False, "error": "Control not found"}

        assessment = self.assessments[assessment_id]
        control = self.controls[control_id]

        assessment.controls_assessed += 1
        if passed:
            assessment.controls_passed += 1
        else:
            assessment.controls_failed += 1

        control.last_assessed = datetime.utcnow()
        control.next_assessment = datetime.utcnow() + timedelta(days=90)

        # Calculate score
        if assessment.controls_assessed > 0:
            assessment.overall_score = (
                assessment.controls_passed / assessment.controls_assessed
            ) * 100

        return {
            "success": True,
            "assessment_id": assessment_id,
            "control_id": control_id,
            "passed": passed,
            "overall_score": assessment.overall_score,
        }

    def complete_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """Complete an assessment"""
        if assessment_id not in self.assessments:
            return {"success": False, "error": "Assessment not found"}

        assessment = self.assessments[assessment_id]
        assessment.completed_at = datetime.utcnow()
        assessment.status = "completed"

        self._create_audit_trail(
            entity_type="assessment",
            entity_id=assessment_id,
            action="completed",
            user=assessment.assessor,
        )

        return {
            "success": True,
            "assessment_id": assessment_id,
            "overall_score": assessment.overall_score,
            "controls_assessed": assessment.controls_assessed,
            "controls_passed": assessment.controls_passed,
            "controls_failed": assessment.controls_failed,
        }

    # ========================================================================
    # FINDING MANAGEMENT
    # ========================================================================

    def create_finding(
        self,
        assessment_id: str,
        control_id: str,
        severity: RiskLevel,
        title: str,
        description: str,
        user: str,
    ) -> Dict[str, Any]:
        """Create compliance finding"""
        finding_id = f"find_{uuid4().hex[:12]}"
        finding = ComplianceFinding(
            finding_id=finding_id,
            assessment_id=assessment_id,
            control_id=control_id,
            severity=severity,
            title=title,
            description=description,
        )

        self.findings[finding_id] = finding

        # Update assessment finding counts
        if assessment_id in self.assessments:
            assessment = self.assessments[assessment_id]
            assessment.findings_count += 1
            if severity == RiskLevel.CRITICAL:
                assessment.critical_findings += 1
            elif severity == RiskLevel.HIGH:
                assessment.high_findings += 1
            elif severity == RiskLevel.MEDIUM:
                assessment.medium_findings += 1
            elif severity == RiskLevel.LOW:
                assessment.low_findings += 1

        self._create_audit_trail(
            entity_type="finding", entity_id=finding_id, action="created", user=user
        )

        return {"success": True, "finding_id": finding_id}

    def resolve_finding(
        self, finding_id: str, resolution_notes: str, user: str
    ) -> Dict[str, Any]:
        """Resolve a compliance finding"""
        if finding_id not in self.findings:
            return {"success": False, "error": "Finding not found"}

        finding = self.findings[finding_id]
        finding.status = "resolved"
        finding.resolved_at = datetime.utcnow()
        finding.resolved_by = user
        finding.resolution_notes = resolution_notes

        self._create_audit_trail(
            entity_type="finding", entity_id=finding_id, action="resolved", user=user
        )

        return {"success": True, "finding_id": finding_id}

    # ========================================================================
    # COMPLIANCE DASHBOARD & REPORTING
    # ========================================================================

    def get_compliance_posture(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Get overall compliance posture for a framework"""
        controls = self.get_controls_by_framework(framework)

        total = len(controls)
        implemented = sum(1 for c in controls if c.status == ControlStatus.IMPLEMENTED)
        partial = sum(
            1 for c in controls if c.status == ControlStatus.PARTIALLY_IMPLEMENTED
        )
        not_implemented = sum(
            1 for c in controls if c.status == ControlStatus.NOT_IMPLEMENTED
        )
        planned = sum(1 for c in controls if c.status == ControlStatus.PLANNED)

        compliance_score = (implemented / total * 100) if total > 0 else 0

        # Determine overall status
        if compliance_score >= 95:
            status = ComplianceStatus.COMPLIANT
        elif compliance_score >= 70:
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        elif compliance_score >= 50:
            status = ComplianceStatus.UNDER_REVIEW
        else:
            status = ComplianceStatus.NON_COMPLIANT

        return {
            "framework": framework.value,
            "overall_status": status.value,
            "compliance_score": round(compliance_score, 2),
            "total_controls": total,
            "implemented": implemented,
            "partially_implemented": partial,
            "not_implemented": not_implemented,
            "planned": planned,
            "last_updated": datetime.utcnow().isoformat(),
        }

    def get_gap_analysis(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Perform gap analysis for a framework"""
        controls = self.get_controls_by_framework(framework)

        gaps = []
        for control in controls:
            if control.status in [
                ControlStatus.NOT_IMPLEMENTED,
                ControlStatus.PARTIALLY_IMPLEMENTED,
            ]:
                gaps.append(
                    {
                        "control_id": control.control_id,
                        "control_number": control.control_number,
                        "title": control.title,
                        "status": control.status.value,
                        "category": control.category,
                        "domain": control.domain,
                        "assigned_to": control.assigned_to,
                        "gap_analysis": control.gap_analysis,
                    }
                )

        return {
            "framework": framework.value,
            "total_gaps": len(gaps),
            "gaps": gaps,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def generate_compliance_report(
        self, framework: ComplianceFramework, report_type: str, user: str
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        report_id = f"report_{uuid4().hex[:12]}"
        report = ComplianceReport(
            report_id=report_id,
            report_type=report_type,
            framework=framework,
            generated_by=user,
        )

        # Get compliance posture
        posture = self.get_compliance_posture(framework)
        report.overall_status = ComplianceStatus(posture["overall_status"])
        report.compliance_score = posture["compliance_score"]
        report.total_controls = posture["total_controls"]
        report.compliant_controls = posture["implemented"]
        report.non_compliant_controls = posture["not_implemented"]

        # Get findings summary
        framework_findings = [
            f
            for f in self.findings.values()
            if self.controls.get(f.control_id, {}).framework == framework
        ]
        report.findings_summary = {
            "total": len(framework_findings),
            "critical": sum(
                1 for f in framework_findings if f.severity == RiskLevel.CRITICAL
            ),
            "high": sum(1 for f in framework_findings if f.severity == RiskLevel.HIGH),
            "medium": sum(
                1 for f in framework_findings if f.severity == RiskLevel.MEDIUM
            ),
            "low": sum(1 for f in framework_findings if f.severity == RiskLevel.LOW),
        }

        self.reports[report_id] = report

        return {
            "success": True,
            "report_id": report_id,
            "compliance_score": report.compliance_score,
            "overall_status": report.overall_status.value,
        }

    # ========================================================================
    # POLICY MANAGEMENT
    # ========================================================================

    def create_policy(
        self, title: str, policy_type: str, version: str, owner: str, user: str
    ) -> Dict[str, Any]:
        """Create new policy document"""
        policy_id = f"policy_{uuid4().hex[:12]}"
        policy = PolicyDocument(
            policy_id=policy_id,
            title=title,
            policy_type=policy_type,
            version=version,
            owner=owner,
        )

        self.policies[policy_id] = policy

        self._create_audit_trail(
            entity_type="policy", entity_id=policy_id, action="created", user=user
        )

        return {"success": True, "policy_id": policy_id}

    def approve_policy(self, policy_id: str, user: str) -> Dict[str, Any]:
        """Approve a policy"""
        if policy_id not in self.policies:
            return {"success": False, "error": "Policy not found"}

        policy = self.policies[policy_id]
        policy.status = "approved"
        policy.approved_by = user
        policy.approved_at = datetime.utcnow()
        policy.effective_date = datetime.utcnow()
        policy.next_review_date = datetime.utcnow() + timedelta(days=365)

        self._create_audit_trail(
            entity_type="policy", entity_id=policy_id, action="approved", user=user
        )

        return {"success": True, "policy_id": policy_id}

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _create_audit_trail(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        user: str,
        changes: Optional[Dict] = None,
    ):
        """Create audit trail entry"""
        trail_id = f"audit_{uuid4().hex[:12]}"
        trail = AuditTrail(
            trail_id=trail_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user=user,
        )
        if changes:
            trail.changes = changes

        self.audit_trails.append(trail)

    def get_audit_trail(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get audit trail entries"""
        trails = self.audit_trails

        if entity_type:
            trails = [t for t in trails if t.entity_type == entity_type]
        if entity_id:
            trails = [t for t in trails if t.entity_id == entity_id]

        trails = sorted(trails, key=lambda x: x.timestamp, reverse=True)[:limit]

        return [
            {
                "trail_id": t.trail_id,
                "entity_type": t.entity_type,
                "entity_id": t.entity_id,
                "action": t.action,
                "user": t.user,
                "timestamp": t.timestamp.isoformat(),
                "changes": t.changes,
            }
            for t in trails
        ]
