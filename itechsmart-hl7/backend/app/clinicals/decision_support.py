"""
Clinical Decision Support System
Evidence-based clinical recommendations and guidelines
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GuidelineCategory(str, Enum):
    """Clinical guideline categories"""

    ANTIBIOTIC_STEWARDSHIP = "antibiotic_stewardship"
    VENOUS_THROMBOEMBOLISM = "venous_thromboembolism"
    PAIN_MANAGEMENT = "pain_management"
    DIABETES_MANAGEMENT = "diabetes_management"
    HYPERTENSION = "hypertension"
    HEART_FAILURE = "heart_failure"
    SEPSIS = "sepsis"
    STROKE = "stroke"
    COPD = "copd"
    ASTHMA = "asthma"


class RecommendationStrength(str, Enum):
    """Strength of clinical recommendations"""

    STRONG = "strong"  # Strong evidence, clear benefit
    MODERATE = "moderate"  # Moderate evidence
    WEAK = "weak"  # Limited evidence
    EXPERT_OPINION = "expert_opinion"  # Based on expert consensus


class ClinicalRecommendation:
    """Clinical decision support recommendation"""

    def __init__(
        self,
        recommendation_id: str,
        category: GuidelineCategory,
        title: str,
        description: str,
        strength: RecommendationStrength,
        evidence_level: str,
        actions: List[str],
        contraindications: List[str],
        monitoring: List[str],
        references: List[str],
    ):
        self.recommendation_id = recommendation_id
        self.category = category
        self.title = title
        self.description = description
        self.strength = strength
        self.evidence_level = evidence_level
        self.actions = actions
        self.contraindications = contraindications
        self.monitoring = monitoring
        self.references = references
        self.generated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "recommendation_id": self.recommendation_id,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "strength": self.strength.value,
            "evidence_level": self.evidence_level,
            "actions": self.actions,
            "contraindications": self.contraindications,
            "monitoring": self.monitoring,
            "references": self.references,
            "generated_at": self.generated_at.isoformat(),
        }


class ClinicalDecisionSupport:
    """
    Clinical Decision Support System
    Provides evidence-based clinical recommendations
    """

    def __init__(self):
        self.guidelines: Dict[GuidelineCategory, List[ClinicalRecommendation]] = {}
        self._load_guidelines()

    def _load_guidelines(self):
        """Load clinical guidelines"""

        # VTE Prophylaxis Guidelines
        vte_guidelines = [
            ClinicalRecommendation(
                "VTE_001",
                GuidelineCategory.VENOUS_THROMBOEMBOLISM,
                "VTE Prophylaxis for Medical Patients",
                "Pharmacologic VTE prophylaxis recommended for hospitalized medical patients at increased risk",
                RecommendationStrength.STRONG,
                "Grade 1B",
                [
                    "Assess VTE risk using validated tool (Padua Score, IMPROVE)",
                    "If high risk: Enoxaparin 40mg SC daily OR Heparin 5000 units SC TID",
                    "If renal impairment (CrCl <30): Heparin 5000 units SC BID-TID",
                    "Continue until patient fully mobile or at discharge",
                ],
                [
                    "Active bleeding",
                    "Platelet count <50,000",
                    "Recent neurosurgery or spinal procedure",
                    "Severe bleeding risk",
                ],
                [
                    "Monitor for signs of bleeding",
                    "Check platelet count if on heparin >5 days (HIT screening)",
                    "Assess mobility status daily",
                ],
                ["CHEST Guidelines 2012", "ACCP VTE Prevention"],
            ),
            ClinicalRecommendation(
                "VTE_002",
                GuidelineCategory.VENOUS_THROMBOEMBOLISM,
                "VTE Prophylaxis for Surgical Patients",
                "Extended duration prophylaxis for high-risk surgical patients",
                RecommendationStrength.STRONG,
                "Grade 1A",
                [
                    "Major surgery: Start prophylaxis preoperatively or within 24h postop",
                    "Enoxaparin 40mg SC daily OR Heparin 5000 units SC TID",
                    "Consider mechanical prophylaxis (SCDs) in addition",
                    "Extend prophylaxis 28-35 days for cancer surgery, major orthopedic",
                ],
                [
                    "Active bleeding",
                    "Epidural catheter in place (wait 12h after enoxaparin)",
                    "Severe thrombocytopenia",
                ],
                [
                    "Monitor surgical site for bleeding",
                    "Assess for DVT/PE symptoms",
                    "Remove mechanical devices when ambulatory",
                ],
                ["ACCP Guidelines", "ASCO VTE Guidelines"],
            ),
        ]

        # Antibiotic Stewardship
        abx_guidelines = [
            ClinicalRecommendation(
                "ABX_001",
                GuidelineCategory.ANTIBIOTIC_STEWARDSHIP,
                "Community-Acquired Pneumonia Treatment",
                "Empiric antibiotic selection for CAP based on severity",
                RecommendationStrength.STRONG,
                "Grade A",
                [
                    "Outpatient, no comorbidities: Amoxicillin 1g TID OR Doxycycline 100mg BID",
                    "Outpatient with comorbidities: Amoxicillin-clavulanate + Macrolide OR Respiratory fluoroquinolone",
                    "Hospitalized non-ICU: Ceftriaxone 1-2g daily + Azithromycin 500mg daily",
                    "ICU: Ceftriaxone 2g daily + Azithromycin 500mg daily (or respiratory FQ)",
                    "Duration: 5-7 days if clinical improvement",
                ],
                [
                    "Adjust for local resistance patterns",
                    "MRSA risk: Add vancomycin or linezolid",
                    "Pseudomonas risk: Use anti-pseudomonal beta-lactam",
                ],
                [
                    "Clinical improvement by day 3-5",
                    "Procalcitonin to guide duration",
                    "De-escalate based on culture results",
                    "Assess for complications (empyema, abscess)",
                ],
                ["IDSA/ATS CAP Guidelines 2019"],
            ),
            ClinicalRecommendation(
                "ABX_002",
                GuidelineCategory.ANTIBIOTIC_STEWARDSHIP,
                "Urinary Tract Infection Treatment",
                "Antibiotic selection for uncomplicated and complicated UTI",
                RecommendationStrength.STRONG,
                "Grade A",
                [
                    "Uncomplicated cystitis: Nitrofurantoin 100mg BID x 5 days OR TMP-SMX DS BID x 3 days",
                    "Complicated UTI: Ciprofloxacin 500mg BID x 7 days OR Ceftriaxone 1g daily",
                    "Pyelonephritis: Ciprofloxacin 500mg BID x 7 days OR Ceftriaxone 1-2g daily",
                    "Avoid fluoroquinolones if possible (FDA warning)",
                ],
                [
                    "Adjust based on local resistance patterns",
                    "Pregnancy: Use beta-lactams (avoid fluoroquinolones, TMP-SMX in 1st trimester)",
                    "Catheter-associated: Remove/replace catheter if possible",
                ],
                [
                    "Clinical improvement within 48-72 hours",
                    "Repeat urinalysis if no improvement",
                    "Blood cultures if pyelonephritis or sepsis",
                ],
                ["IDSA UTI Guidelines"],
            ),
        ]

        # Diabetes Management
        diabetes_guidelines = [
            ClinicalRecommendation(
                "DM_001",
                GuidelineCategory.DIABETES_MANAGEMENT,
                "Type 2 Diabetes Initial Management",
                "Evidence-based approach to T2DM management",
                RecommendationStrength.STRONG,
                "Grade A",
                [
                    "Lifestyle modification: Diet, exercise, weight loss",
                    "Metformin 500-1000mg BID (start low, titrate up)",
                    "Target HbA1c <7% for most patients",
                    "If HbA1c >9% or symptomatic: Consider dual therapy initially",
                    "ASCVD or CKD: Add SGLT2i or GLP-1 RA regardless of HbA1c",
                ],
                [
                    "Metformin contraindications: eGFR <30, lactic acidosis risk",
                    "Adjust targets for elderly, limited life expectancy",
                    "Avoid hypoglycemia in high-risk patients",
                ],
                [
                    "HbA1c every 3 months until at goal, then every 6 months",
                    "Annual: Microalbuminuria, lipids, eye exam, foot exam",
                    "Monitor renal function on metformin",
                    "Self-monitoring blood glucose as appropriate",
                ],
                ["ADA Standards of Care 2024", "AACE Guidelines"],
            ),
            ClinicalRecommendation(
                "DM_002",
                GuidelineCategory.DIABETES_MANAGEMENT,
                "Inpatient Hyperglycemia Management",
                "Blood glucose management for hospitalized patients",
                RecommendationStrength.STRONG,
                "Grade A",
                [
                    "Target glucose: 140-180 mg/dL for most patients",
                    "Use insulin for persistent hyperglycemia >180 mg/dL",
                    "Basal-bolus insulin preferred over sliding scale alone",
                    "Hold metformin on admission (lactic acidosis risk)",
                    "Hold SGLT2i (DKA risk)",
                ],
                [
                    "Avoid tight control (<110 mg/dL) - increases hypoglycemia",
                    "Adjust targets for critically ill, end-of-life",
                    "NPO patients: Hold prandial insulin, continue basal at 50-80%",
                ],
                [
                    "Check glucose before meals and bedtime (or q4-6h if NPO)",
                    "Monitor for hypoglycemia (<70 mg/dL)",
                    "Adjust insulin doses daily based on patterns",
                ],
                ["ADA Hospital Guidelines", "Endocrine Society"],
            ),
        ]

        # Hypertension Management
        htn_guidelines = [
            ClinicalRecommendation(
                "HTN_001",
                GuidelineCategory.HYPERTENSION,
                "Hypertension Initial Treatment",
                "First-line antihypertensive therapy",
                RecommendationStrength.STRONG,
                "Grade A",
                [
                    "Target BP <130/80 for most patients",
                    "First-line: Thiazide diuretic, ACEi, ARB, or CCB",
                    "Black patients: Thiazide or CCB preferred initially",
                    "CKD with proteinuria: ACEi or ARB",
                    "Start 2 drugs if BP >20/10 above goal",
                ],
                [
                    "ACEi/ARB: Avoid in pregnancy, bilateral renal artery stenosis",
                    "Thiazides: Caution with gout",
                    "Beta-blockers: Not first-line unless specific indication",
                ],
                [
                    "BP check in 1 month after starting therapy",
                    "Titrate every 2-4 weeks until at goal",
                    "Home BP monitoring encouraged",
                    "Annual: Electrolytes, creatinine",
                ],
                ["ACC/AHA 2017 Guidelines", "JNC 8"],
            )
        ]

        # Heart Failure Management
        hf_guidelines = [
            ClinicalRecommendation(
                "HF_001",
                GuidelineCategory.HEART_FAILURE,
                "Heart Failure with Reduced Ejection Fraction (HFrEF)",
                "Guideline-directed medical therapy for HFrEF",
                RecommendationStrength.STRONG,
                "Grade A",
                [
                    "Quadruple therapy: ACEi/ARB/ARNI + Beta-blocker + MRA + SGLT2i",
                    "ACEi: Lisinopril 10-40mg daily OR ARB: Losartan 50-100mg daily",
                    "Beta-blocker: Carvedilol 25mg BID OR Metoprolol succinate 200mg daily",
                    "MRA: Spironolactone 25-50mg daily (if K+ <5.0, Cr <2.5)",
                    "SGLT2i: Dapagliflozin 10mg daily OR Empagliflozin 10mg daily",
                    "Diuretics: Furosemide as needed for volume management",
                ],
                [
                    "ACEi/ARB: Avoid if K+ >5.5, Cr >3.0, bilateral RAS",
                    "Beta-blocker: Avoid in decompensated HF, severe bradycardia",
                    "MRA: Avoid if K+ >5.0, severe renal impairment",
                ],
                [
                    "Electrolytes and renal function 1-2 weeks after starting ACEi/ARB/MRA",
                    "Repeat echo in 3-6 months to assess response",
                    "Daily weights, report gain >2-3 lbs",
                    "Symptoms: dyspnea, edema, exercise tolerance",
                ],
                ["ACC/AHA/HFSA 2022 Guidelines"],
            )
        ]

        # Sepsis Management
        sepsis_guidelines = [
            ClinicalRecommendation(
                "SEPSIS_001",
                GuidelineCategory.SEPSIS,
                "Sepsis and Septic Shock Management",
                "Surviving Sepsis Campaign bundle",
                RecommendationStrength.STRONG,
                "Grade A",
                [
                    "Hour 1 Bundle:",
                    "1. Measure lactate, remeasure if >2 mmol/L",
                    "2. Obtain blood cultures before antibiotics",
                    "3. Administer broad-spectrum antibiotics",
                    "4. Fluid resuscitation: 30 mL/kg crystalloid for hypotension/lactate ≥4",
                    "5. Vasopressors if hypotensive during/after fluid resuscitation (target MAP ≥65)",
                    "Antibiotics: Vancomycin + Piperacillin-tazobactam OR Cefepime + Metronidazole",
                ],
                [
                    "Adjust antibiotics based on source and local resistance",
                    "De-escalate based on cultures and clinical improvement",
                    "Avoid excessive fluid in ARDS or cardiogenic shock",
                ],
                [
                    "Lactate clearance (repeat q2-4h until normalized)",
                    "Urine output (target >0.5 mL/kg/hr)",
                    "Mental status, vital signs q15-30min",
                    "Reassess volume status frequently",
                ],
                ["Surviving Sepsis Campaign 2021"],
            )
        ]

        # Pain Management
        pain_guidelines = [
            ClinicalRecommendation(
                "PAIN_001",
                GuidelineCategory.PAIN_MANAGEMENT,
                "Acute Pain Management",
                "Multimodal analgesia approach",
                RecommendationStrength.STRONG,
                "Grade B",
                [
                    "Multimodal approach: Combine non-opioid + opioid if needed",
                    "First-line: Acetaminophen 1000mg q6h (max 4g/day)",
                    "Add NSAID if not contraindicated: Ibuprofen 400-600mg q6h",
                    "Opioids only if inadequate response to non-opioids",
                    "If opioid needed: Start with lowest effective dose",
                    "Reassess pain regularly (q4h or more frequently)",
                ],
                [
                    "NSAIDs: Avoid in renal impairment, GI bleeding, anticoagulation",
                    "Acetaminophen: Max 3g/day if liver disease",
                    "Opioids: Caution in elderly, respiratory disease, substance use disorder",
                ],
                [
                    "Pain scores q4h",
                    "Sedation level if on opioids",
                    "Bowel regimen if on opioids >24h",
                    "Reassess need for opioids daily",
                ],
                ["CDC Opioid Guidelines", "AAPM"],
            )
        ]

        # Store guidelines
        self.guidelines[GuidelineCategory.VENOUS_THROMBOEMBOLISM] = vte_guidelines
        self.guidelines[GuidelineCategory.ANTIBIOTIC_STEWARDSHIP] = abx_guidelines
        self.guidelines[GuidelineCategory.DIABETES_MANAGEMENT] = diabetes_guidelines
        self.guidelines[GuidelineCategory.HYPERTENSION] = htn_guidelines
        self.guidelines[GuidelineCategory.HEART_FAILURE] = hf_guidelines
        self.guidelines[GuidelineCategory.SEPSIS] = sepsis_guidelines
        self.guidelines[GuidelineCategory.PAIN_MANAGEMENT] = pain_guidelines

        total_guidelines = sum(len(g) for g in self.guidelines.values())
        logger.info(
            f"Loaded {total_guidelines} clinical guidelines across {len(self.guidelines)} categories"
        )

    def get_recommendations(
        self, category: GuidelineCategory
    ) -> List[ClinicalRecommendation]:
        """Get recommendations for a category"""
        return self.guidelines.get(category, [])

    def get_vte_prophylaxis_recommendation(
        self, patient_type: str, risk_factors: List[str]
    ) -> Optional[ClinicalRecommendation]:
        """Get VTE prophylaxis recommendation"""
        vte_recs = self.guidelines.get(GuidelineCategory.VENOUS_THROMBOEMBOLISM, [])

        if patient_type == "medical":
            return vte_recs[0] if vte_recs else None
        elif patient_type == "surgical":
            return vte_recs[1] if len(vte_recs) > 1 else None

        return None

    def get_antibiotic_recommendation(
        self, infection_type: str, severity: str
    ) -> Optional[ClinicalRecommendation]:
        """Get antibiotic recommendation"""
        abx_recs = self.guidelines.get(GuidelineCategory.ANTIBIOTIC_STEWARDSHIP, [])

        if infection_type.lower() in ["pneumonia", "cap"]:
            return abx_recs[0] if abx_recs else None
        elif infection_type.lower() in ["uti", "urinary"]:
            return abx_recs[1] if len(abx_recs) > 1 else None

        return None

    def get_diabetes_recommendation(
        self, setting: str, hba1c: Optional[float] = None
    ) -> Optional[ClinicalRecommendation]:
        """Get diabetes management recommendation"""
        dm_recs = self.guidelines.get(GuidelineCategory.DIABETES_MANAGEMENT, [])

        if setting == "outpatient":
            return dm_recs[0] if dm_recs else None
        elif setting == "inpatient":
            return dm_recs[1] if len(dm_recs) > 1 else None

        return None

    def search_guidelines(self, query: str) -> List[ClinicalRecommendation]:
        """Search guidelines by keyword"""
        results = []
        query_lower = query.lower()

        for category_recs in self.guidelines.values():
            for rec in category_recs:
                if (
                    query_lower in rec.title.lower()
                    or query_lower in rec.description.lower()
                    or any(query_lower in action.lower() for action in rec.actions)
                ):
                    results.append(rec)

        return results

    def get_all_categories(self) -> List[str]:
        """Get all guideline categories"""
        return [cat.value for cat in self.guidelines.keys()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get decision support statistics"""
        return {
            "total_categories": len(self.guidelines),
            "total_guidelines": sum(len(g) for g in self.guidelines.values()),
            "categories": {
                cat.value: len(recs) for cat, recs in self.guidelines.items()
            },
        }


# Global decision support instance
decision_support = ClinicalDecisionSupport()
