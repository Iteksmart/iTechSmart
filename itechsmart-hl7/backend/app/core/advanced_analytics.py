"""
Advanced Analytics Engine for iTechSmart HL7
Provides business intelligence, predictive analytics, and data insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Core analytics engine for data processing and insights"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.cache = {}

    def get_patient_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive patient statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = text(
            """
            SELECT 
                COUNT(DISTINCT patient_id) as total_patients,
                COUNT(DISTINCT CASE WHEN created_at >= :cutoff THEN patient_id END) as new_patients,
                AVG(EXTRACT(YEAR FROM AGE(date_of_birth))) as avg_age,
                COUNT(CASE WHEN gender = 'M' THEN 1 END) as male_count,
                COUNT(CASE WHEN gender = 'F' THEN 1 END) as female_count,
                COUNT(CASE WHEN gender NOT IN ('M', 'F') THEN 1 END) as other_gender_count
            FROM patients
        """
        )

        result = self.db.execute(query, {"cutoff": cutoff_date}).fetchone()

        return {
            "total_patients": result.total_patients or 0,
            "new_patients_last_30_days": result.new_patients or 0,
            "average_age": round(result.avg_age, 1) if result.avg_age else 0,
            "gender_distribution": {
                "male": result.male_count or 0,
                "female": result.female_count or 0,
                "other": result.other_gender_count or 0,
            },
            "growth_rate": round(
                (
                    (result.new_patients / result.total_patients * 100)
                    if result.total_patients
                    else 0
                ),
                2,
            ),
        }

    def get_message_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Analyze HL7 message patterns and trends"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = text(
            """
            SELECT 
                message_type,
                COUNT(*) as count,
                AVG(processing_time_ms) as avg_processing_time,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as error_count
            FROM hl7_messages
            WHERE created_at >= :cutoff
            GROUP BY message_type
            ORDER BY count DESC
        """
        )

        results = self.db.execute(query, {"cutoff": cutoff_date}).fetchall()

        message_stats = []
        total_messages = 0
        total_errors = 0

        for row in results:
            total_messages += row.count
            total_errors += row.error_count

            message_stats.append(
                {
                    "type": row.message_type,
                    "count": row.count,
                    "avg_processing_time_ms": (
                        round(row.avg_processing_time, 2)
                        if row.avg_processing_time
                        else 0
                    ),
                    "success_rate": (
                        round(row.success_count / row.count * 100, 2)
                        if row.count
                        else 0
                    ),
                    "error_count": row.error_count,
                }
            )

        return {
            "period_days": days,
            "total_messages": total_messages,
            "total_errors": total_errors,
            "error_rate": (
                round(total_errors / total_messages * 100, 2) if total_messages else 0
            ),
            "by_type": message_stats,
        }

    def get_clinical_insights(self) -> Dict[str, Any]:
        """Generate clinical insights from patient data"""
        # Most common diagnoses
        diagnosis_query = text(
            """
            SELECT 
                diagnosis_code,
                diagnosis_name,
                COUNT(*) as frequency
            FROM patient_diagnoses
            GROUP BY diagnosis_code, diagnosis_name
            ORDER BY frequency DESC
            LIMIT 10
        """
        )

        # Most prescribed medications
        medication_query = text(
            """
            SELECT 
                medication_name,
                COUNT(*) as prescription_count,
                COUNT(DISTINCT patient_id) as unique_patients
            FROM medications
            WHERE status = 'active'
            GROUP BY medication_name
            ORDER BY prescription_count DESC
            LIMIT 10
        """
        )

        try:
            diagnoses = self.db.execute(diagnosis_query).fetchall()
            medications = self.db.execute(medication_query).fetchall()

            return {
                "top_diagnoses": [
                    {
                        "code": d.diagnosis_code,
                        "name": d.diagnosis_name,
                        "frequency": d.frequency,
                    }
                    for d in diagnoses
                ],
                "top_medications": [
                    {
                        "name": m.medication_name,
                        "prescriptions": m.prescription_count,
                        "unique_patients": m.unique_patients,
                    }
                    for m in medications
                ],
            }
        except Exception as e:
            logger.error(f"Error generating clinical insights: {e}")
            return {"top_diagnoses": [], "top_medications": []}

    def get_system_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze system performance trends"""
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)

        query = text(
            """
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                COUNT(*) as message_count,
                AVG(processing_time_ms) as avg_processing_time,
                MAX(processing_time_ms) as max_processing_time,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as error_count
            FROM hl7_messages
            WHERE created_at >= :cutoff
            GROUP BY DATE_TRUNC('hour', created_at)
            ORDER BY hour
        """
        )

        results = self.db.execute(query, {"cutoff": cutoff_date}).fetchall()

        hourly_stats = []
        for row in results:
            hourly_stats.append(
                {
                    "hour": row.hour.isoformat(),
                    "message_count": row.message_count,
                    "avg_processing_time_ms": (
                        round(row.avg_processing_time, 2)
                        if row.avg_processing_time
                        else 0
                    ),
                    "max_processing_time_ms": (
                        round(row.max_processing_time, 2)
                        if row.max_processing_time
                        else 0
                    ),
                    "error_count": row.error_count,
                    "error_rate": (
                        round(row.error_count / row.message_count * 100, 2)
                        if row.message_count
                        else 0
                    ),
                }
            )

        return {
            "period_hours": hours,
            "data_points": len(hourly_stats),
            "hourly_stats": hourly_stats,
        }

    def predict_patient_risk(self, patient_id: str) -> Dict[str, Any]:
        """Predict patient risk scores using simple heuristics"""
        # Get patient data
        patient_query = text(
            """
            SELECT 
                p.*,
                COUNT(DISTINCT d.diagnosis_code) as diagnosis_count,
                COUNT(DISTINCT m.medication_id) as medication_count,
                COUNT(DISTINCT o.observation_id) as observation_count
            FROM patients p
            LEFT JOIN patient_diagnoses d ON p.patient_id = d.patient_id
            LEFT JOIN medications m ON p.patient_id = m.patient_id
            LEFT JOIN observations o ON p.patient_id = o.patient_id
            WHERE p.patient_id = :patient_id
            GROUP BY p.patient_id
        """
        )

        try:
            patient = self.db.execute(
                patient_query, {"patient_id": patient_id}
            ).fetchone()

            if not patient:
                return {"error": "Patient not found"}

            # Calculate risk scores (0-100)
            age = (
                datetime.utcnow().year - patient.date_of_birth.year
                if patient.date_of_birth
                else 0
            )

            # Age risk (higher age = higher risk)
            age_risk = min(age / 100 * 100, 100)

            # Comorbidity risk (more diagnoses = higher risk)
            comorbidity_risk = min(patient.diagnosis_count * 10, 100)

            # Medication risk (polypharmacy)
            medication_risk = min(patient.medication_count * 8, 100)

            # Overall risk (weighted average)
            overall_risk = (
                age_risk * 0.3 + comorbidity_risk * 0.4 + medication_risk * 0.3
            )

            risk_level = (
                "low"
                if overall_risk < 30
                else "medium" if overall_risk < 60 else "high"
            )

            return {
                "patient_id": patient_id,
                "risk_scores": {
                    "overall": round(overall_risk, 1),
                    "age": round(age_risk, 1),
                    "comorbidity": round(comorbidity_risk, 1),
                    "medication": round(medication_risk, 1),
                },
                "risk_level": risk_level,
                "factors": {
                    "age": age,
                    "diagnosis_count": patient.diagnosis_count,
                    "medication_count": patient.medication_count,
                    "observation_count": patient.observation_count,
                },
                "recommendations": self._generate_recommendations(
                    risk_level, overall_risk
                ),
            }
        except Exception as e:
            logger.error(f"Error predicting patient risk: {e}")
            return {"error": str(e)}

    def _generate_recommendations(
        self, risk_level: str, risk_score: float
    ) -> List[str]:
        """Generate recommendations based on risk level"""
        recommendations = []

        if risk_level == "high":
            recommendations.extend(
                [
                    "Schedule immediate follow-up appointment",
                    "Review medication list for potential interactions",
                    "Consider care coordination with specialists",
                    "Implement enhanced monitoring protocols",
                ]
            )
        elif risk_level == "medium":
            recommendations.extend(
                [
                    "Schedule routine follow-up within 2 weeks",
                    "Review current treatment plan",
                    "Monitor for changes in condition",
                ]
            )
        else:
            recommendations.extend(
                ["Continue current care plan", "Schedule annual wellness visit"]
            )

        return recommendations


class ReportGenerator:
    """Generate comprehensive reports and dashboards"""

    def __init__(self, analytics_engine: AnalyticsEngine):
        self.analytics = analytics_engine

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary report"""
        return {
            "report_type": "Executive Summary",
            "generated_at": datetime.utcnow().isoformat(),
            "patient_overview": self.analytics.get_patient_statistics(30),
            "message_analytics": self.analytics.get_message_analytics(7),
            "clinical_insights": self.analytics.get_clinical_insights(),
            "system_performance": self.analytics.get_system_performance_trends(24),
        }

    def generate_clinical_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate detailed clinical report"""
        return {
            "report_type": "Clinical Report",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "generated_at": datetime.utcnow().isoformat(),
            "clinical_insights": self.analytics.get_clinical_insights(),
            "patient_statistics": self.analytics.get_patient_statistics(
                (end_date - start_date).days
            ),
        }

    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate system performance report"""
        return {
            "report_type": "Performance Report",
            "period_hours": hours,
            "generated_at": datetime.utcnow().isoformat(),
            "performance_trends": self.analytics.get_system_performance_trends(hours),
            "message_analytics": self.analytics.get_message_analytics(hours // 24 or 1),
        }


class PredictiveAnalytics:
    """Predictive analytics and forecasting"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def forecast_patient_volume(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Forecast patient volume for next N days"""
        # Get historical data
        query = text(
            """
            SELECT 
                DATE(created_at) as date,
                COUNT(DISTINCT patient_id) as patient_count
            FROM patients
            WHERE created_at >= NOW() - INTERVAL '90 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        )

        try:
            results = self.db.execute(query).fetchall()

            if len(results) < 7:
                return {"error": "Insufficient historical data"}

            # Simple moving average forecast
            historical_counts = [r.patient_count for r in results]
            avg_daily = np.mean(historical_counts[-30:])  # Last 30 days average
            trend = (historical_counts[-1] - historical_counts[-30]) / 30  # Daily trend

            forecast = []
            for i in range(1, days_ahead + 1):
                predicted_count = int(avg_daily + (trend * i))
                forecast.append(
                    {
                        "day": i,
                        "date": (datetime.utcnow() + timedelta(days=i))
                        .date()
                        .isoformat(),
                        "predicted_patients": max(0, predicted_count),
                    }
                )

            return {
                "forecast_days": days_ahead,
                "historical_average": round(avg_daily, 1),
                "daily_trend": round(trend, 2),
                "forecast": forecast,
            }
        except Exception as e:
            logger.error(f"Error forecasting patient volume: {e}")
            return {"error": str(e)}

    def identify_anomalies(
        self, metric: str = "message_count", hours: int = 24
    ) -> Dict[str, Any]:
        """Identify anomalies in system metrics"""
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)

        query = text(
            """
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                COUNT(*) as message_count
            FROM hl7_messages
            WHERE created_at >= :cutoff
            GROUP BY DATE_TRUNC('hour', created_at)
            ORDER BY hour
        """
        )

        try:
            results = self.db.execute(query, {"cutoff": cutoff_date}).fetchall()

            if len(results) < 3:
                return {"error": "Insufficient data for anomaly detection"}

            counts = [r.message_count for r in results]
            mean = np.mean(counts)
            std = np.std(counts)

            # Detect anomalies (values > 2 standard deviations from mean)
            anomalies = []
            for r in results:
                z_score = (r.message_count - mean) / std if std > 0 else 0
                if abs(z_score) > 2:
                    anomalies.append(
                        {
                            "hour": r.hour.isoformat(),
                            "value": r.message_count,
                            "z_score": round(z_score, 2),
                            "severity": "high" if abs(z_score) > 3 else "medium",
                        }
                    )

            return {
                "metric": metric,
                "period_hours": hours,
                "mean": round(mean, 2),
                "std_dev": round(std, 2),
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
            }
        except Exception as e:
            logger.error(f"Error identifying anomalies: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    print("Advanced Analytics Engine initialized")
    print("Features:")
    print("  ✅ Patient Statistics & Demographics")
    print("  ✅ Message Analytics & Trends")
    print("  ✅ Clinical Insights & Patterns")
    print("  ✅ System Performance Monitoring")
    print("  ✅ Predictive Risk Scoring")
    print("  ✅ Volume Forecasting")
    print("  ✅ Anomaly Detection")
