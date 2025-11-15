"""
AI Clinical Insights
ML-powered clinical analysis and predictions
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
import random

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class InsightType(str, Enum):
    """Types of clinical insights"""
    RISK_PREDICTION = "risk_prediction"
    DIAGNOSIS_SUGGESTION = "diagnosis_suggestion"
    TREATMENT_RECOMMENDATION = "treatment_recommendation"
    LAB_INTERPRETATION = "lab_interpretation"
    TREND_ANALYSIS = "trend_analysis"
    READMISSION_RISK = "readmission_risk"
    DETERIORATION_WARNING = "deterioration_warning"


class ClinicalInsight:
    """Clinical insight with AI analysis"""
    
    def __init__(
        self,
        insight_id: str,
        insight_type: InsightType,
        title: str,
        description: str,
        risk_level: RiskLevel,
        confidence: float,
        evidence: List[str],
        recommendations: List[str],
        references: List[str] = None
    ):
        self.insight_id = insight_id
        self.insight_type = insight_type
        self.title = title
        self.description = description
        self.risk_level = risk_level
        self.confidence = confidence  # 0.0 to 1.0
        self.evidence = evidence
        self.recommendations = recommendations
        self.references = references or []
        self.generated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'insight_id': self.insight_id,
            'insight_type': self.insight_type.value,
            'title': self.title,
            'description': self.description,
            'risk_level': self.risk_level.value,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'recommendations': self.recommendations,
            'references': self.references,
            'generated_at': self.generated_at.isoformat()
        }


class ClinicalAIInsights:
    """
    AI Clinical Insights Engine
    Provides ML-powered clinical analysis and predictions
    """
    
    def __init__(self):
        self.insights_cache: Dict[str, List[ClinicalInsight]] = {}
    
    def predict_sepsis_risk(
        self,
        patient_id: str,
        vital_signs: Dict[str, float],
        lab_results: Dict[str, float]
    ) -> ClinicalInsight:
        """Predict sepsis risk using qSOFA and SIRS criteria"""
        
        # qSOFA Score (Quick Sequential Organ Failure Assessment)
        qsofa_score = 0
        evidence = []
        
        # Respiratory rate >= 22
        if vital_signs.get('respiratory_rate', 0) >= 22:
            qsofa_score += 1
            evidence.append(f"Elevated respiratory rate: {vital_signs['respiratory_rate']} breaths/min (≥22)")
        
        # Altered mentation (GCS < 15)
        if vital_signs.get('gcs', 15) < 15:
            qsofa_score += 1
            evidence.append(f"Altered mental status: GCS {vital_signs['gcs']} (<15)")
        
        # Systolic BP <= 100
        if vital_signs.get('systolic_bp', 120) <= 100:
            qsofa_score += 1
            evidence.append(f"Hypotension: SBP {vital_signs['systolic_bp']} mmHg (≤100)")
        
        # SIRS Criteria
        sirs_score = 0
        
        # Temperature
        temp = vital_signs.get('temperature', 37.0)
        if temp > 38.0 or temp < 36.0:
            sirs_score += 1
            evidence.append(f"Abnormal temperature: {temp}°C")
        
        # Heart rate > 90
        if vital_signs.get('heart_rate', 70) > 90:
            sirs_score += 1
            evidence.append(f"Tachycardia: {vital_signs['heart_rate']} bpm (>90)")
        
        # WBC
        wbc = lab_results.get('wbc', 7.0)
        if wbc > 12.0 or wbc < 4.0:
            sirs_score += 1
            evidence.append(f"Abnormal WBC: {wbc} K/μL")
        
        # Lactate
        lactate = lab_results.get('lactate', 1.0)
        if lactate > 2.0:
            evidence.append(f"Elevated lactate: {lactate} mmol/L (>2.0)")
        
        # Determine risk level
        if qsofa_score >= 2 or (sirs_score >= 2 and lactate > 4.0):
            risk_level = RiskLevel.CRITICAL
            confidence = 0.85
            recommendations = [
                "IMMEDIATE: Activate sepsis protocol",
                "Obtain blood cultures before antibiotics",
                "Administer broad-spectrum antibiotics within 1 hour",
                "Initiate fluid resuscitation (30 mL/kg crystalloid)",
                "Consider ICU admission",
                "Monitor lactate clearance"
            ]
        elif qsofa_score >= 1 or sirs_score >= 2:
            risk_level = RiskLevel.HIGH
            confidence = 0.75
            recommendations = [
                "Close monitoring required",
                "Consider sepsis workup (cultures, lactate)",
                "Reassess in 1-2 hours",
                "Prepare for possible antibiotic initiation",
                "Monitor vital signs every 1 hour"
            ]
        else:
            risk_level = RiskLevel.LOW
            confidence = 0.90
            recommendations = [
                "Continue standard monitoring",
                "Reassess if clinical status changes",
                "Monitor vital signs per protocol"
            ]
        
        return ClinicalInsight(
            f"SEPSIS_RISK_{patient_id}_{datetime.utcnow().timestamp()}",
            InsightType.RISK_PREDICTION,
            "Sepsis Risk Assessment",
            f"qSOFA Score: {qsofa_score}/3, SIRS Score: {sirs_score}/4",
            risk_level,
            confidence,
            evidence,
            recommendations,
            ["Surviving Sepsis Campaign 2021", "qSOFA Validation Study"]
        )
    
    def predict_readmission_risk(
        self,
        patient_id: str,
        age: int,
        comorbidities: List[str],
        length_of_stay: int,
        previous_admissions: int
    ) -> ClinicalInsight:
        """Predict 30-day readmission risk"""
        
        risk_score = 0
        evidence = []
        
        # Age factor
        if age >= 65:
            risk_score += 2
            evidence.append(f"Age {age} years (≥65 increases risk)")
        
        # Comorbidities
        high_risk_conditions = ['heart_failure', 'copd', 'diabetes', 'renal_failure']
        comorbidity_count = sum(1 for c in comorbidities if c in high_risk_conditions)
        risk_score += comorbidity_count
        if comorbidity_count > 0:
            evidence.append(f"{comorbidity_count} high-risk comorbidities present")
        
        # Length of stay
        if length_of_stay > 7:
            risk_score += 1
            evidence.append(f"Extended length of stay: {length_of_stay} days")
        
        # Previous admissions
        if previous_admissions >= 2:
            risk_score += 2
            evidence.append(f"Multiple recent admissions: {previous_admissions} in past year")
        
        # Determine risk level
        if risk_score >= 5:
            risk_level = RiskLevel.HIGH
            confidence = 0.78
            recommendations = [
                "Schedule follow-up within 7 days of discharge",
                "Arrange home health services",
                "Medication reconciliation and education",
                "Provide written discharge instructions",
                "Consider transitional care program",
                "Ensure patient has primary care provider"
            ]
        elif risk_score >= 3:
            risk_level = RiskLevel.MODERATE
            confidence = 0.72
            recommendations = [
                "Schedule follow-up within 14 days",
                "Provide discharge education",
                "Medication reconciliation",
                "Consider post-discharge phone call"
            ]
        else:
            risk_level = RiskLevel.LOW
            confidence = 0.85
            recommendations = [
                "Standard discharge planning",
                "Schedule routine follow-up",
                "Provide discharge instructions"
            ]
        
        return ClinicalInsight(
            f"READMIT_RISK_{patient_id}_{datetime.utcnow().timestamp()}",
            InsightType.READMISSION_RISK,
            "30-Day Readmission Risk",
            f"Risk Score: {risk_score}/10",
            risk_level,
            confidence,
            evidence,
            recommendations,
            ["HOSPITAL Score", "LACE Index"]
        )
    
    def analyze_lab_trends(
        self,
        patient_id: str,
        lab_name: str,
        values: List[Dict[str, Any]]
    ) -> ClinicalInsight:
        """Analyze laboratory value trends"""
        
        if len(values) < 2:
            return None
        
        # Sort by timestamp
        sorted_values = sorted(values, key=lambda x: x['timestamp'])
        
        # Calculate trend
        first_value = sorted_values[0]['value']
        last_value = sorted_values[-1]['value']
        change = last_value - first_value
        percent_change = (change / first_value * 100) if first_value != 0 else 0
        
        evidence = [
            f"Initial value: {first_value}",
            f"Current value: {last_value}",
            f"Change: {change:+.2f} ({percent_change:+.1f}%)",
            f"Number of measurements: {len(values)}"
        ]
        
        # Lab-specific analysis
        if lab_name.lower() == 'creatinine':
            if last_value > 1.5 and change > 0.3:
                risk_level = RiskLevel.HIGH
                recommendations = [
                    "Acute kidney injury suspected",
                    "Review nephrotoxic medications",
                    "Ensure adequate hydration",
                    "Consider nephrology consultation if worsening",
                    "Monitor urine output"
                ]
            elif change > 0.2:
                risk_level = RiskLevel.MODERATE
                recommendations = [
                    "Monitor renal function closely",
                    "Review medication dosing",
                    "Ensure adequate hydration"
                ]
            else:
                risk_level = RiskLevel.LOW
                recommendations = ["Continue routine monitoring"]
        
        elif lab_name.lower() == 'potassium':
            if last_value > 5.5:
                risk_level = RiskLevel.CRITICAL
                recommendations = [
                    "URGENT: Severe hyperkalemia",
                    "Obtain ECG immediately",
                    "Consider calcium gluconate if ECG changes",
                    "Administer insulin/glucose or albuterol",
                    "Review potassium sources and medications"
                ]
            elif last_value < 3.0:
                risk_level = RiskLevel.HIGH
                recommendations = [
                    "Severe hypokalemia",
                    "Obtain ECG",
                    "Potassium replacement needed",
                    "Monitor for arrhythmias"
                ]
            else:
                risk_level = RiskLevel.LOW
                recommendations = ["Continue routine monitoring"]
        
        elif lab_name.lower() == 'hemoglobin':
            if last_value < 7.0:
                risk_level = RiskLevel.CRITICAL
                recommendations = [
                    "Severe anemia - consider transfusion",
                    "Assess for active bleeding",
                    "Type and cross match",
                    "Investigate cause of anemia"
                ]
            elif last_value < 9.0:
                risk_level = RiskLevel.HIGH
                recommendations = [
                    "Moderate anemia",
                    "Investigate cause",
                    "Consider iron studies",
                    "May need transfusion if symptomatic"
                ]
            else:
                risk_level = RiskLevel.LOW
                recommendations = ["Continue routine monitoring"]
        
        else:
            risk_level = RiskLevel.LOW
            recommendations = ["Continue monitoring trend"]
        
        confidence = 0.80 if len(values) >= 3 else 0.65
        
        return ClinicalInsight(
            f"LAB_TREND_{lab_name}_{patient_id}_{datetime.utcnow().timestamp()}",
            InsightType.TREND_ANALYSIS,
            f"{lab_name} Trend Analysis",
            f"Trending {'up' if change > 0 else 'down'} by {abs(percent_change):.1f}%",
            risk_level,
            confidence,
            evidence,
            recommendations,
            ["Clinical Laboratory Standards"]
        )
    
    def detect_deterioration(
        self,
        patient_id: str,
        vital_signs_history: List[Dict[str, Any]]
    ) -> Optional[ClinicalInsight]:
        """Detect patient deterioration using Modified Early Warning Score (MEWS)"""
        
        if not vital_signs_history:
            return None
        
        latest_vitals = vital_signs_history[-1]
        
        # Calculate MEWS
        mews_score = 0
        evidence = []
        
        # Respiratory rate
        rr = latest_vitals.get('respiratory_rate', 15)
        if rr < 9:
            mews_score += 2
            evidence.append(f"Bradypnea: RR {rr} (<9)")
        elif rr >= 30:
            mews_score += 3
            evidence.append(f"Tachypnea: RR {rr} (≥30)")
        elif rr >= 21:
            mews_score += 2
            evidence.append(f"Elevated RR: {rr} (21-29)")
        
        # Heart rate
        hr = latest_vitals.get('heart_rate', 75)
        if hr < 40:
            mews_score += 2
            evidence.append(f"Bradycardia: HR {hr} (<40)")
        elif hr >= 130:
            mews_score += 3
            evidence.append(f"Severe tachycardia: HR {hr} (≥130)")
        elif hr >= 111:
            mews_score += 2
            evidence.append(f"Tachycardia: HR {hr} (111-129)")
        
        # Systolic BP
        sbp = latest_vitals.get('systolic_bp', 120)
        if sbp < 70:
            mews_score += 3
            evidence.append(f"Severe hypotension: SBP {sbp} (<70)")
        elif sbp < 81:
            mews_score += 2
            evidence.append(f"Hypotension: SBP {sbp} (71-80)")
        elif sbp >= 200:
            mews_score += 2
            evidence.append(f"Severe hypertension: SBP {sbp} (≥200)")
        
        # Temperature
        temp = latest_vitals.get('temperature', 37.0)
        if temp < 35.0:
            mews_score += 2
            evidence.append(f"Hypothermia: {temp}°C (<35)")
        elif temp >= 38.5:
            mews_score += 2
            evidence.append(f"Fever: {temp}°C (≥38.5)")
        
        # Level of consciousness
        avpu = latest_vitals.get('avpu', 'A')  # A=Alert, V=Voice, P=Pain, U=Unresponsive
        if avpu == 'U':
            mews_score += 3
            evidence.append("Unresponsive (AVPU: U)")
        elif avpu == 'P':
            mews_score += 2
            evidence.append("Responds to pain only (AVPU: P)")
        elif avpu == 'V':
            mews_score += 1
            evidence.append("Responds to voice only (AVPU: V)")
        
        # Determine risk level
        if mews_score >= 5:
            risk_level = RiskLevel.CRITICAL
            confidence = 0.88
            recommendations = [
                "URGENT: Patient deteriorating",
                "Notify physician immediately",
                "Consider rapid response team activation",
                "Increase monitoring frequency to every 15 minutes",
                "Prepare for possible ICU transfer",
                "Reassess MEWS in 30 minutes"
            ]
        elif mews_score >= 3:
            risk_level = RiskLevel.HIGH
            confidence = 0.82
            recommendations = [
                "Increased monitoring required",
                "Notify physician",
                "Increase vital signs frequency to every 1 hour",
                "Reassess MEWS in 1 hour",
                "Consider additional interventions"
            ]
        elif mews_score >= 1:
            risk_level = RiskLevel.MODERATE
            confidence = 0.75
            recommendations = [
                "Continue close monitoring",
                "Reassess in 2-4 hours",
                "Document changes"
            ]
        else:
            return None  # No deterioration detected
        
        return ClinicalInsight(
            f"DETERIORATION_{patient_id}_{datetime.utcnow().timestamp()}",
            InsightType.DETERIORATION_WARNING,
            "Patient Deterioration Warning",
            f"Modified Early Warning Score (MEWS): {mews_score}",
            risk_level,
            confidence,
            evidence,
            recommendations,
            ["MEWS Guidelines", "Rapid Response Criteria"]
        )
    
    def suggest_diagnosis(
        self,
        patient_id: str,
        symptoms: List[str],
        vital_signs: Dict[str, float],
        lab_results: Dict[str, float]
    ) -> List[ClinicalInsight]:
        """Suggest possible diagnoses based on clinical presentation"""
        
        insights = []
        
        # Pneumonia detection
        if ('cough' in symptoms or 'dyspnea' in symptoms) and \
           vital_signs.get('temperature', 37.0) > 38.0 and \
           lab_results.get('wbc', 7.0) > 11.0:
            
            insights.append(ClinicalInsight(
                f"DX_PNEUMONIA_{patient_id}",
                InsightType.DIAGNOSIS_SUGGESTION,
                "Possible Pneumonia",
                "Clinical presentation consistent with pneumonia",
                RiskLevel.MODERATE,
                0.72,
                [
                    "Respiratory symptoms present",
                    f"Fever: {vital_signs.get('temperature')}°C",
                    f"Elevated WBC: {lab_results.get('wbc')} K/μL"
                ],
                [
                    "Obtain chest X-ray",
                    "Consider sputum culture",
                    "Assess oxygenation (SpO2, ABG if indicated)",
                    "Consider empiric antibiotics if confirmed"
                ],
                ["CAP Guidelines", "IDSA/ATS"]
            ))
        
        # Heart failure detection
        if ('dyspnea' in symptoms or 'edema' in symptoms) and \
           lab_results.get('bnp', 0) > 400:
            
            insights.append(ClinicalInsight(
                f"DX_HF_{patient_id}",
                InsightType.DIAGNOSIS_SUGGESTION,
                "Possible Heart Failure Exacerbation",
                "Clinical and laboratory findings suggest heart failure",
                RiskLevel.HIGH,
                0.78,
                [
                    "Dyspnea or edema present",
                    f"Elevated BNP: {lab_results.get('bnp')} pg/mL (>400)"
                ],
                [
                    "Obtain echocardiogram if not recent",
                    "Assess volume status",
                    "Consider diuresis",
                    "Review medication compliance",
                    "Cardiology consultation"
                ],
                ["ACC/AHA Heart Failure Guidelines"]
            ))
        
        # Acute coronary syndrome
        if 'chest_pain' in symptoms and \
           (lab_results.get('troponin', 0) > 0.04 or 
            vital_signs.get('systolic_bp', 120) > 180):
            
            insights.append(ClinicalInsight(
                f"DX_ACS_{patient_id}",
                InsightType.DIAGNOSIS_SUGGESTION,
                "Possible Acute Coronary Syndrome",
                "Chest pain with concerning features",
                RiskLevel.CRITICAL,
                0.85,
                [
                    "Chest pain present",
                    f"Troponin: {lab_results.get('troponin', 'pending')}",
                    "Hemodynamic instability" if vital_signs.get('systolic_bp', 120) > 180 else ""
                ],
                [
                    "URGENT: Obtain 12-lead ECG immediately",
                    "Serial troponins",
                    "Aspirin 325mg if not contraindicated",
                    "Cardiology consultation STAT",
                    "Consider cardiac catheterization"
                ],
                ["ACC/AHA STEMI/NSTEMI Guidelines"]
            ))
        
        return insights
    
    def get_patient_insights(
        self,
        patient_id: str,
        clinical_data: Dict[str, Any]
    ) -> List[ClinicalInsight]:
        """Get all AI insights for a patient"""
        
        insights = []
        
        # Sepsis risk
        if 'vital_signs' in clinical_data and 'lab_results' in clinical_data:
            sepsis_insight = self.predict_sepsis_risk(
                patient_id,
                clinical_data['vital_signs'],
                clinical_data['lab_results']
            )
            insights.append(sepsis_insight)
        
        # Deterioration detection
        if 'vital_signs_history' in clinical_data:
            deterioration = self.detect_deterioration(
                patient_id,
                clinical_data['vital_signs_history']
            )
            if deterioration:
                insights.append(deterioration)
        
        # Diagnosis suggestions
        if all(k in clinical_data for k in ['symptoms', 'vital_signs', 'lab_results']):
            diagnoses = self.suggest_diagnosis(
                patient_id,
                clinical_data['symptoms'],
                clinical_data['vital_signs'],
                clinical_data['lab_results']
            )
            insights.extend(diagnoses)
        
        # Cache insights
        self.insights_cache[patient_id] = insights
        
        return insights
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get AI insights statistics"""
        total_insights = sum(len(insights) for insights in self.insights_cache.values())
        
        critical_count = 0
        high_count = 0
        
        for insights in self.insights_cache.values():
            for insight in insights:
                if insight.risk_level == RiskLevel.CRITICAL:
                    critical_count += 1
                elif insight.risk_level == RiskLevel.HIGH:
                    high_count += 1
        
        return {
            'total_patients_analyzed': len(self.insights_cache),
            'total_insights_generated': total_insights,
            'critical_alerts': critical_count,
            'high_risk_alerts': high_count
        }


# Global AI insights instance
ai_insights = ClinicalAIInsights()