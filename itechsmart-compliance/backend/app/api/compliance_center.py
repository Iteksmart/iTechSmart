"""
iTechSmart Compliance - Compliance Center API
Multi-framework compliance tracking endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..core.compliance_center import ComplianceCenterEngine
from ..models.models import ComplianceFramework, ControlStatus, EvidenceType, RiskLevel

router = APIRouter(prefix="/compliance-center", tags=["Compliance Center"])
engine = ComplianceCenterEngine()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class ControlStatusUpdate(BaseModel):
    status: ControlStatus
    notes: Optional[str] = None


class ControlAssignment(BaseModel):
    assigned_to: str


class EvidenceCreate(BaseModel):
    control_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    file_path: Optional[str] = None


class AssessmentCreate(BaseModel):
    framework: ComplianceFramework
    assessment_type: str
    scope: str


class ControlAssessment(BaseModel):
    control_id: str
    passed: bool
    notes: Optional[str] = None


class FindingCreate(BaseModel):
    assessment_id: str
    control_id: str
    severity: RiskLevel
    title: str
    description: str
    impact: Optional[str] = None
    recommendation: Optional[str] = None


class FindingResolve(BaseModel):
    resolution_notes: str


class PolicyCreate(BaseModel):
    title: str
    policy_type: str
    version: str
    description: Optional[str] = None


class ReportGenerate(BaseModel):
    framework: ComplianceFramework
    report_type: str


# ============================================================================
# CONTROL ENDPOINTS
# ============================================================================


@router.get("/controls")
async def get_controls(
    framework: Optional[ComplianceFramework] = Query(None),
    status: Optional[ControlStatus] = Query(None),
    category: Optional[str] = Query(None),
):
    """Get compliance controls with optional filters"""
    controls = list(engine.controls.values())

    if framework:
        controls = [c for c in controls if c.framework == framework]
    if status:
        controls = [c for c in controls if c.status == status]
    if category:
        controls = [c for c in controls if c.category == category]

    return {
        "total": len(controls),
        "controls": [
            {
                "control_id": c.control_id,
                "framework": c.framework.value,
                "control_number": c.control_number,
                "title": c.title,
                "description": c.description,
                "category": c.category,
                "domain": c.domain,
                "status": c.status.value,
                "assigned_to": c.assigned_to,
                "evidence_count": len(c.evidence_ids),
                "last_assessed": (
                    c.last_assessed.isoformat() if c.last_assessed else None
                ),
                "next_assessment": (
                    c.next_assessment.isoformat() if c.next_assessment else None
                ),
            }
            for c in controls
        ],
    }


@router.get("/controls/{control_id}")
async def get_control(control_id: str):
    """Get detailed control information"""
    if control_id not in engine.controls:
        raise HTTPException(status_code=404, detail="Control not found")

    control = engine.controls[control_id]

    # Get evidence
    evidence = [
        {
            "evidence_id": e.evidence_id,
            "evidence_type": e.evidence_type.value,
            "title": e.title,
            "collected_at": e.collected_at.isoformat(),
            "verified": e.verified_at is not None,
        }
        for e in [engine.evidence.get(eid) for eid in control.evidence_ids]
        if e is not None
    ]

    return {
        "control_id": control.control_id,
        "framework": control.framework.value,
        "control_number": control.control_number,
        "title": control.title,
        "description": control.description,
        "category": control.category,
        "domain": control.domain,
        "requirement": control.requirement,
        "status": control.status.value,
        "implementation_date": (
            control.implementation_date.isoformat()
            if control.implementation_date
            else None
        ),
        "assigned_to": control.assigned_to,
        "owner": control.owner,
        "evidence": evidence,
        "gap_analysis": control.gap_analysis,
        "remediation_plan": control.remediation_plan,
        "notes": control.notes,
        "last_assessed": (
            control.last_assessed.isoformat() if control.last_assessed else None
        ),
        "next_assessment": (
            control.next_assessment.isoformat() if control.next_assessment else None
        ),
    }


@router.put("/controls/{control_id}/status")
async def update_control_status(control_id: str, update: ControlStatusUpdate):
    """Update control implementation status"""
    result = engine.update_control_status(
        control_id=control_id,
        status=update.status,
        user="api_user",  # Should come from auth
        notes=update.notes,
    )

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.put("/controls/{control_id}/assign")
async def assign_control(control_id: str, assignment: ControlAssignment):
    """Assign control to a user"""
    result = engine.assign_control(
        control_id=control_id, assigned_to=assignment.assigned_to, user="api_user"
    )

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ============================================================================
# EVIDENCE ENDPOINTS
# ============================================================================


@router.post("/evidence")
async def add_evidence(evidence: EvidenceCreate):
    """Add evidence for a control"""
    result = engine.add_evidence(
        control_id=evidence.control_id,
        evidence_type=evidence.evidence_type,
        title=evidence.title,
        description=evidence.description,
        file_path=evidence.file_path,
        user="api_user",
    )

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/evidence/{evidence_id}")
async def get_evidence(evidence_id: str):
    """Get evidence details"""
    if evidence_id not in engine.evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    evidence = engine.evidence[evidence_id]

    return {
        "evidence_id": evidence.evidence_id,
        "control_id": evidence.control_id,
        "evidence_type": evidence.evidence_type.value,
        "title": evidence.title,
        "description": evidence.description,
        "file_path": evidence.file_path,
        "collected_by": evidence.collected_by,
        "collected_at": evidence.collected_at.isoformat(),
        "verified_by": evidence.verified_by,
        "verified_at": (
            evidence.verified_at.isoformat() if evidence.verified_at else None
        ),
        "expiration_date": (
            evidence.expiration_date.isoformat() if evidence.expiration_date else None
        ),
    }


@router.put("/evidence/{evidence_id}/verify")
async def verify_evidence(evidence_id: str):
    """Verify evidence"""
    result = engine.verify_evidence(evidence_id=evidence_id, user="api_user")

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ============================================================================
# ASSESSMENT ENDPOINTS
# ============================================================================


@router.post("/assessments")
async def create_assessment(assessment: AssessmentCreate):
    """Create new compliance assessment"""
    result = engine.create_assessment(
        framework=assessment.framework,
        assessment_type=assessment.assessment_type,
        assessor="api_user",
        scope=assessment.scope,
    )

    return result


@router.get("/assessments")
async def get_assessments(
    framework: Optional[ComplianceFramework] = Query(None),
    status: Optional[str] = Query(None),
):
    """Get compliance assessments"""
    assessments = list(engine.assessments.values())

    if framework:
        assessments = [a for a in assessments if a.framework == framework]
    if status:
        assessments = [a for a in assessments if a.status == status]

    return {
        "total": len(assessments),
        "assessments": [
            {
                "assessment_id": a.assessment_id,
                "framework": a.framework.value,
                "assessment_type": a.assessment_type,
                "assessor": a.assessor,
                "status": a.status,
                "started_at": a.started_at.isoformat(),
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
                "overall_score": a.overall_score,
                "controls_assessed": a.controls_assessed,
                "controls_passed": a.controls_passed,
                "controls_failed": a.controls_failed,
                "findings_count": a.findings_count,
            }
            for a in assessments
        ],
    }


@router.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Get assessment details"""
    if assessment_id not in engine.assessments:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment = engine.assessments[assessment_id]

    # Get findings
    findings = [
        {
            "finding_id": f.finding_id,
            "control_id": f.control_id,
            "severity": f.severity.value,
            "title": f.title,
            "status": f.status,
        }
        for f in engine.findings.values()
        if f.assessment_id == assessment_id
    ]

    return {
        "assessment_id": assessment.assessment_id,
        "framework": assessment.framework.value,
        "assessment_type": assessment.assessment_type,
        "assessor": assessment.assessor,
        "scope": assessment.scope,
        "status": assessment.status,
        "started_at": assessment.started_at.isoformat(),
        "completed_at": (
            assessment.completed_at.isoformat() if assessment.completed_at else None
        ),
        "overall_score": assessment.overall_score,
        "controls_assessed": assessment.controls_assessed,
        "controls_passed": assessment.controls_passed,
        "controls_failed": assessment.controls_failed,
        "controls_partial": assessment.controls_partial,
        "findings": findings,
        "critical_findings": assessment.critical_findings,
        "high_findings": assessment.high_findings,
        "medium_findings": assessment.medium_findings,
        "low_findings": assessment.low_findings,
    }


@router.post("/assessments/{assessment_id}/assess-control")
async def assess_control(assessment_id: str, assessment: ControlAssessment):
    """Assess a control during an assessment"""
    result = engine.assess_control(
        assessment_id=assessment_id,
        control_id=assessment.control_id,
        passed=assessment.passed,
        notes=assessment.notes,
    )

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.post("/assessments/{assessment_id}/complete")
async def complete_assessment(assessment_id: str):
    """Complete an assessment"""
    result = engine.complete_assessment(assessment_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ============================================================================
# FINDING ENDPOINTS
# ============================================================================


@router.post("/findings")
async def create_finding(finding: FindingCreate):
    """Create compliance finding"""
    result = engine.create_finding(
        assessment_id=finding.assessment_id,
        control_id=finding.control_id,
        severity=finding.severity,
        title=finding.title,
        description=finding.description,
        user="api_user",
    )

    return result


@router.get("/findings")
async def get_findings(
    status: Optional[str] = Query(None), severity: Optional[RiskLevel] = Query(None)
):
    """Get compliance findings"""
    findings = list(engine.findings.values())

    if status:
        findings = [f for f in findings if f.status == status]
    if severity:
        findings = [f for f in findings if f.severity == severity]

    return {
        "total": len(findings),
        "findings": [
            {
                "finding_id": f.finding_id,
                "assessment_id": f.assessment_id,
                "control_id": f.control_id,
                "severity": f.severity.value,
                "title": f.title,
                "description": f.description,
                "status": f.status,
                "assigned_to": f.assigned_to,
                "due_date": f.due_date.isoformat() if f.due_date else None,
                "created_at": f.created_at.isoformat(),
            }
            for f in findings
        ],
    }


@router.get("/findings/{finding_id}")
async def get_finding(finding_id: str):
    """Get finding details"""
    if finding_id not in engine.findings:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding = engine.findings[finding_id]

    return {
        "finding_id": finding.finding_id,
        "assessment_id": finding.assessment_id,
        "control_id": finding.control_id,
        "severity": finding.severity.value,
        "title": finding.title,
        "description": finding.description,
        "impact": finding.impact,
        "recommendation": finding.recommendation,
        "remediation_plan": finding.remediation_plan,
        "status": finding.status,
        "assigned_to": finding.assigned_to,
        "due_date": finding.due_date.isoformat() if finding.due_date else None,
        "resolved_at": finding.resolved_at.isoformat() if finding.resolved_at else None,
        "resolved_by": finding.resolved_by,
        "resolution_notes": finding.resolution_notes,
        "created_at": finding.created_at.isoformat(),
    }


@router.put("/findings/{finding_id}/resolve")
async def resolve_finding(finding_id: str, resolve: FindingResolve):
    """Resolve a finding"""
    result = engine.resolve_finding(
        finding_id=finding_id,
        resolution_notes=resolve.resolution_notes,
        user="api_user",
    )

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================


@router.get("/dashboard/posture")
async def get_compliance_posture(framework: ComplianceFramework):
    """Get compliance posture for a framework"""
    return engine.get_compliance_posture(framework)


@router.get("/dashboard/gap-analysis")
async def get_gap_analysis(framework: ComplianceFramework):
    """Get gap analysis for a framework"""
    return engine.get_gap_analysis(framework)


@router.get("/dashboard/multi-framework")
async def get_multi_framework_view():
    """Get compliance status across all frameworks"""
    frameworks = [
        ComplianceFramework.SOC2,
        ComplianceFramework.ISO27001,
        ComplianceFramework.HIPAA,
        ComplianceFramework.GDPR,
        ComplianceFramework.PCI_DSS,
    ]

    results = []
    for framework in frameworks:
        posture = engine.get_compliance_posture(framework)
        results.append(posture)

    return {"frameworks": results, "generated_at": datetime.utcnow().isoformat()}


# ============================================================================
# REPORTING ENDPOINTS
# ============================================================================


@router.post("/reports/generate")
async def generate_report(report: ReportGenerate):
    """Generate compliance report"""
    result = engine.generate_compliance_report(
        framework=report.framework, report_type=report.report_type, user="api_user"
    )

    return result


@router.get("/reports")
async def get_reports(framework: Optional[ComplianceFramework] = Query(None)):
    """Get compliance reports"""
    reports = list(engine.reports.values())

    if framework:
        reports = [r for r in reports if r.framework == framework]

    return {
        "total": len(reports),
        "reports": [
            {
                "report_id": r.report_id,
                "report_type": r.report_type,
                "framework": r.framework.value,
                "compliance_score": r.compliance_score,
                "overall_status": r.overall_status.value if r.overall_status else None,
                "generated_at": r.generated_at.isoformat(),
                "generated_by": r.generated_by,
            }
            for r in reports
        ],
    }


@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Get report details"""
    if report_id not in engine.reports:
        raise HTTPException(status_code=404, detail="Report not found")

    report = engine.reports[report_id]

    return {
        "report_id": report.report_id,
        "report_type": report.report_type,
        "framework": report.framework.value,
        "title": report.title,
        "description": report.description,
        "period_start": (
            report.period_start.isoformat() if report.period_start else None
        ),
        "period_end": report.period_end.isoformat() if report.period_end else None,
        "overall_status": (
            report.overall_status.value if report.overall_status else None
        ),
        "compliance_score": report.compliance_score,
        "total_controls": report.total_controls,
        "compliant_controls": report.compliant_controls,
        "non_compliant_controls": report.non_compliant_controls,
        "findings_summary": report.findings_summary,
        "recommendations": report.recommendations,
        "generated_at": report.generated_at.isoformat(),
        "generated_by": report.generated_by,
    }


# ============================================================================
# POLICY ENDPOINTS
# ============================================================================


@router.post("/policies")
async def create_policy(policy: PolicyCreate):
    """Create new policy document"""
    result = engine.create_policy(
        title=policy.title,
        policy_type=policy.policy_type,
        version=policy.version,
        owner="api_user",
        user="api_user",
    )

    return result


@router.get("/policies")
async def get_policies(
    status: Optional[str] = Query(None), policy_type: Optional[str] = Query(None)
):
    """Get policy documents"""
    policies = list(engine.policies.values())

    if status:
        policies = [p for p in policies if p.status == status]
    if policy_type:
        policies = [p for p in policies if p.policy_type == policy_type]

    return {
        "total": len(policies),
        "policies": [
            {
                "policy_id": p.policy_id,
                "title": p.title,
                "policy_type": p.policy_type,
                "version": p.version,
                "status": p.status,
                "owner": p.owner,
                "effective_date": (
                    p.effective_date.isoformat() if p.effective_date else None
                ),
                "next_review_date": (
                    p.next_review_date.isoformat() if p.next_review_date else None
                ),
            }
            for p in policies
        ],
    }


@router.put("/policies/{policy_id}/approve")
async def approve_policy(policy_id: str):
    """Approve a policy"""
    result = engine.approve_policy(policy_id=policy_id, user="api_user")

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ============================================================================
# AUDIT TRAIL ENDPOINTS
# ============================================================================


@router.get("/audit-trail")
async def get_audit_trail(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    """Get audit trail entries"""
    trails = engine.get_audit_trail(
        entity_type=entity_type, entity_id=entity_id, limit=limit
    )

    return {"total": len(trails), "trails": trails}
