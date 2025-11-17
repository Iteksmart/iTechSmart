"""
iTechSmart Compliance - Compliance Management Engine
Handles regulatory compliance tracking, auditing, and reporting
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""

    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    CCPA = "ccpa"
    NIST = "nist"


class ComplianceStatus(str, Enum):
    """Compliance status"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    NOT_APPLICABLE = "not_applicable"


class ControlStatus(str, Enum):
    """Control implementation status"""

    IMPLEMENTED = "implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    NOT_IMPLEMENTED = "not_implemented"
    PLANNED = "planned"


class ComplianceControl:
    """Represents a compliance control"""

    def __init__(
        self,
        control_id: str,
        framework: ComplianceFramework,
        control_number: str,
        title: str,
        description: str,
        category: str,
    ):
        self.control_id = control_id
        self.framework = framework
        self.control_number = control_number
        self.title = title
        self.description = description
        self.category = category
        self.status = ControlStatus.NOT_IMPLEMENTED
        self.evidence = []
        self.last_assessed = None
        self.next_assessment = None
        self.assigned_to = None
        self.notes = ""


class ComplianceAssessment:
    """Represents a compliance assessment"""

    def __init__(
        self, assessment_id: str, framework: ComplianceFramework, assessor: str
    ):
        self.assessment_id = assessment_id
        self.framework = framework
        self.assessor = assessor
        self.started_at = datetime.utcnow()
        self.completed_at = None
        self.status = "in_progress"
        self.findings = []
        self.score = 0
        self.controls_assessed = 0
        self.controls_passed = 0
        self.controls_failed = 0


class ComplianceFinding:
    """Represents a compliance finding"""

    def __init__(
        self, finding_id: str, control_id: str, severity: str, description: str
    ):
        self.finding_id = finding_id
        self.control_id = control_id
        self.severity = severity  # critical, high, medium, low
        self.description = description
        self.status = "open"
        self.remediation_plan = ""
        self.due_date = None
        self.assigned_to = None
        self.created_at = datetime.utcnow()
        self.resolved_at = None


class Policy:
    """Represents a compliance policy"""

    def __init__(
        self, policy_id: str, title: str, framework: ComplianceFramework, content: str
    ):
        self.policy_id = policy_id
        self.title = title
        self.framework = framework
        self.content = content
        self.version = "1.0"
        self.status = "draft"
        self.approved_by = None
        self.approved_at = None
        self.effective_date = None
        self.review_date = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ComplianceEngine:
    """Main compliance management engine"""

    def __init__(self):
        self.controls: Dict[str, ComplianceControl] = {}
        self.assessments: Dict[str, ComplianceAssessment] = {}
        self.findings: Dict[str, ComplianceFinding] = {}
        self.policies: Dict[str, Policy] = {}
        self._initialize_controls()

    def _initialize_controls(self):
        """Initialize standard compliance controls"""
        # HIPAA Controls
        hipaa_controls = [
            (
                "164.308(a)(1)",
                "Security Management Process",
                "Administrative Safeguards",
            ),
            ("164.308(a)(3)", "Workforce Security", "Administrative Safeguards"),
            (
                "164.308(a)(4)",
                "Information Access Management",
                "Administrative Safeguards",
            ),
            ("164.310(a)(1)", "Facility Access Controls", "Physical Safeguards"),
            ("164.312(a)(1)", "Access Control", "Technical Safeguards"),
            ("164.312(b)", "Audit Controls", "Technical Safeguards"),
            ("164.312(c)(1)", "Integrity", "Technical Safeguards"),
            ("164.312(d)", "Person or Entity Authentication", "Technical Safeguards"),
            ("164.312(e)(1)", "Transmission Security", "Technical Safeguards"),
        ]

        for control_num, title, category in hipaa_controls:
            control_id = str(uuid4())
            control = ComplianceControl(
                control_id=control_id,
                framework=ComplianceFramework.HIPAA,
                control_number=control_num,
                title=title,
                description=f"HIPAA {control_num}: {title}",
                category=category,
            )
            self.controls[control_id] = control

        # GDPR Controls
        gdpr_controls = [
            ("Art. 5", "Principles of Processing", "Data Protection Principles"),
            ("Art. 6", "Lawfulness of Processing", "Legal Basis"),
            ("Art. 7", "Conditions for Consent", "Consent"),
            ("Art. 15", "Right of Access", "Data Subject Rights"),
            ("Art. 17", "Right to Erasure", "Data Subject Rights"),
            ("Art. 25", "Data Protection by Design", "Privacy by Design"),
            ("Art. 32", "Security of Processing", "Security Measures"),
            ("Art. 33", "Breach Notification", "Incident Response"),
        ]

        for control_num, title, category in gdpr_controls:
            control_id = str(uuid4())
            control = ComplianceControl(
                control_id=control_id,
                framework=ComplianceFramework.GDPR,
                control_number=control_num,
                title=title,
                description=f"GDPR {control_num}: {title}",
                category=category,
            )
            self.controls[control_id] = control

        # SOC 2 Controls
        soc2_controls = [
            ("CC1.1", "Control Environment", "Common Criteria"),
            ("CC2.1", "Communication and Information", "Common Criteria"),
            ("CC3.1", "Risk Assessment", "Common Criteria"),
            ("CC6.1", "Logical Access", "Common Criteria"),
            ("CC7.1", "System Operations", "Common Criteria"),
            ("CC8.1", "Change Management", "Common Criteria"),
        ]

        for control_num, title, category in soc2_controls:
            control_id = str(uuid4())
            control = ComplianceControl(
                control_id=control_id,
                framework=ComplianceFramework.SOC2,
                control_number=control_num,
                title=title,
                description=f"SOC 2 {control_num}: {title}",
                category=category,
            )
            self.controls[control_id] = control

    # Control Management
    def get_controls(
        self,
        framework: Optional[ComplianceFramework] = None,
        status: Optional[ControlStatus] = None,
    ) -> List[Dict[str, Any]]:
        """Get compliance controls"""
        controls = list(self.controls.values())

        if framework:
            controls = [c for c in controls if c.framework == framework]

        if status:
            controls = [c for c in controls if c.status == status]

        return [
            {
                "control_id": c.control_id,
                "framework": c.framework.value,
                "control_number": c.control_number,
                "title": c.title,
                "description": c.description,
                "category": c.category,
                "status": c.status.value,
                "last_assessed": (
                    c.last_assessed.isoformat() if c.last_assessed else None
                ),
                "assigned_to": c.assigned_to,
            }
            for c in controls
        ]

    def update_control_status(
        self,
        control_id: str,
        status: ControlStatus,
        evidence: List[str] = None,
        notes: str = None,
    ) -> bool:
        """Update control implementation status"""
        control = self.controls.get(control_id)
        if not control:
            return False

        control.status = status
        control.last_assessed = datetime.utcnow()

        if evidence:
            control.evidence.extend(evidence)

        if notes:
            control.notes = notes

        return True

    # Assessment Management
    def create_assessment(self, framework: ComplianceFramework, assessor: str) -> str:
        """Create a new compliance assessment"""
        assessment_id = str(uuid4())

        assessment = ComplianceAssessment(
            assessment_id=assessment_id, framework=framework, assessor=assessor
        )

        self.assessments[assessment_id] = assessment
        return assessment_id

    def conduct_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """Conduct compliance assessment"""
        assessment = self.assessments.get(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Get controls for this framework
        framework_controls = [
            c for c in self.controls.values() if c.framework == assessment.framework
        ]

        assessment.controls_assessed = len(framework_controls)

        # Assess each control
        for control in framework_controls:
            if control.status == ControlStatus.IMPLEMENTED:
                assessment.controls_passed += 1
            else:
                assessment.controls_failed += 1

                # Create finding
                finding_id = str(uuid4())
                finding = ComplianceFinding(
                    finding_id=finding_id,
                    control_id=control.control_id,
                    severity=(
                        "high"
                        if control.status == ControlStatus.NOT_IMPLEMENTED
                        else "medium"
                    ),
                    description=f"Control {control.control_number} not fully implemented",
                )
                self.findings[finding_id] = finding
                assessment.findings.append(finding_id)

        # Calculate score
        if assessment.controls_assessed > 0:
            assessment.score = int(
                (assessment.controls_passed / assessment.controls_assessed) * 100
            )

        assessment.completed_at = datetime.utcnow()
        assessment.status = "completed"

        return {
            "assessment_id": assessment_id,
            "framework": assessment.framework.value,
            "score": assessment.score,
            "controls_assessed": assessment.controls_assessed,
            "controls_passed": assessment.controls_passed,
            "controls_failed": assessment.controls_failed,
            "findings_count": len(assessment.findings),
            "status": assessment.status,
        }

    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment details"""
        assessment = self.assessments.get(assessment_id)
        if not assessment:
            return None

        return {
            "assessment_id": assessment.assessment_id,
            "framework": assessment.framework.value,
            "assessor": assessment.assessor,
            "started_at": assessment.started_at.isoformat(),
            "completed_at": (
                assessment.completed_at.isoformat() if assessment.completed_at else None
            ),
            "status": assessment.status,
            "score": assessment.score,
            "controls_assessed": assessment.controls_assessed,
            "controls_passed": assessment.controls_passed,
            "controls_failed": assessment.controls_failed,
            "findings": assessment.findings,
        }

    # Finding Management
    def get_findings(
        self, severity: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get compliance findings"""
        findings = list(self.findings.values())

        if severity:
            findings = [f for f in findings if f.severity == severity]

        if status:
            findings = [f for f in findings if f.status == status]

        return [
            {
                "finding_id": f.finding_id,
                "control_id": f.control_id,
                "severity": f.severity,
                "description": f.description,
                "status": f.status,
                "remediation_plan": f.remediation_plan,
                "due_date": f.due_date.isoformat() if f.due_date else None,
                "assigned_to": f.assigned_to,
                "created_at": f.created_at.isoformat(),
            }
            for f in findings
        ]

    def resolve_finding(self, finding_id: str, resolution_notes: str) -> bool:
        """Resolve a compliance finding"""
        finding = self.findings.get(finding_id)
        if not finding:
            return False

        finding.status = "resolved"
        finding.resolved_at = datetime.utcnow()
        finding.remediation_plan = resolution_notes

        return True

    # Policy Management
    def create_policy(
        self, title: str, framework: ComplianceFramework, content: str
    ) -> str:
        """Create a compliance policy"""
        policy_id = str(uuid4())

        policy = Policy(
            policy_id=policy_id, title=title, framework=framework, content=content
        )

        self.policies[policy_id] = policy
        return policy_id

    def approve_policy(self, policy_id: str, approver: str) -> bool:
        """Approve a policy"""
        policy = self.policies.get(policy_id)
        if not policy:
            return False

        policy.status = "approved"
        policy.approved_by = approver
        policy.approved_at = datetime.utcnow()
        policy.effective_date = datetime.utcnow()
        policy.review_date = datetime.utcnow() + timedelta(days=365)

        return True

    def get_policies(
        self,
        framework: Optional[ComplianceFramework] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get policies"""
        policies = list(self.policies.values())

        if framework:
            policies = [p for p in policies if p.framework == framework]

        if status:
            policies = [p for p in policies if p.status == status]

        return [
            {
                "policy_id": p.policy_id,
                "title": p.title,
                "framework": p.framework.value,
                "version": p.version,
                "status": p.status,
                "approved_by": p.approved_by,
                "effective_date": (
                    p.effective_date.isoformat() if p.effective_date else None
                ),
                "review_date": p.review_date.isoformat() if p.review_date else None,
            }
            for p in policies
        ]

    # Compliance Dashboard
    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        total_controls = len(self.controls)
        implemented = len(
            [c for c in self.controls.values() if c.status == ControlStatus.IMPLEMENTED]
        )

        by_framework = {}
        for framework in ComplianceFramework:
            framework_controls = [
                c for c in self.controls.values() if c.framework == framework
            ]
            framework_implemented = len(
                [c for c in framework_controls if c.status == ControlStatus.IMPLEMENTED]
            )

            if len(framework_controls) > 0:
                compliance_score = int(
                    (framework_implemented / len(framework_controls)) * 100
                )
            else:
                compliance_score = 0

            by_framework[framework.value] = {
                "total_controls": len(framework_controls),
                "implemented": framework_implemented,
                "compliance_score": compliance_score,
            }

        open_findings = len([f for f in self.findings.values() if f.status == "open"])
        critical_findings = len(
            [
                f
                for f in self.findings.values()
                if f.severity == "critical" and f.status == "open"
            ]
        )

        return {
            "overall_compliance": (
                int((implemented / total_controls * 100)) if total_controls > 0 else 0
            ),
            "total_controls": total_controls,
            "implemented_controls": implemented,
            "by_framework": by_framework,
            "open_findings": open_findings,
            "critical_findings": critical_findings,
            "total_policies": len(self.policies),
            "approved_policies": len(
                [p for p in self.policies.values() if p.status == "approved"]
            ),
        }


# Global compliance engine instance
compliance_engine = ComplianceEngine()
