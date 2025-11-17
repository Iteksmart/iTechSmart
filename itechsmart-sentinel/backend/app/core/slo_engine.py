"""
iTechSmart Sentinel - SLO Tracking Engine
Service Level Objectives with error budgets and burn rate alerts
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.models import Service, SLO, SLOMeasurement, SLOStatus


class SLOEngine:
    """
    SLO tracking with error budgets and burn rate monitoring
    """

    def __init__(self, db: Session):
        self.db = db

    async def create_slo(
        self,
        service_name: str,
        name: str,
        slo_type: str,
        target_percentage: float,
        window_days: int = 30,
        description: Optional[str] = None,
        warning_threshold: float = 95.0,
        critical_threshold: float = 90.0,
        alert_on_breach: bool = True,
        alert_on_burn_rate: bool = True,
    ) -> SLO:
        """
        Create a new SLO
        """
        # Get or create service
        service = self.db.query(Service).filter(Service.name == service_name).first()
        if not service:
            service = Service(
                name=service_name, display_name=service_name, is_healthy=True
            )
            self.db.add(service)
            self.db.flush()

        # Create SLO
        slo = SLO(
            service_id=service.id,
            name=name,
            description=description,
            slo_type=slo_type,
            target_percentage=target_percentage,
            window_days=window_days,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            alert_on_breach=alert_on_breach,
            alert_on_burn_rate=alert_on_burn_rate,
            status=SLOStatus.HEALTHY.value,
            error_budget_remaining=100.0,
        )

        self.db.add(slo)
        self.db.commit()
        self.db.refresh(slo)

        return slo

    async def record_measurement(
        self,
        slo_id: int,
        success_count: int,
        total_count: int,
        timestamp: Optional[datetime] = None,
    ) -> SLOMeasurement:
        """
        Record an SLO measurement
        """
        slo = self.db.query(SLO).filter(SLO.id == slo_id).first()
        if not slo:
            raise ValueError(f"SLO {slo_id} not found")

        if not timestamp:
            timestamp = datetime.utcnow()

        # Calculate success percentage
        success_percentage = (
            (success_count / total_count * 100) if total_count > 0 else 100.0
        )

        # Calculate error budget consumption
        error_budget_consumed = max(
            0, 100 - (success_percentage / slo.target_percentage * 100)
        )

        # Calculate burn rate (errors per hour)
        burn_rate = await self._calculate_burn_rate(slo, error_budget_consumed)

        # Create measurement
        measurement = SLOMeasurement(
            slo_id=slo_id,
            timestamp=timestamp,
            success_count=success_count,
            total_count=total_count,
            success_percentage=success_percentage,
            error_budget_consumed=error_budget_consumed,
            burn_rate=burn_rate,
        )

        self.db.add(measurement)

        # Update SLO current status
        await self._update_slo_status(slo)

        self.db.commit()
        self.db.refresh(measurement)

        return measurement

    async def get_slo_status(self, slo_id: int) -> Dict[str, Any]:
        """
        Get current SLO status with error budget
        """
        slo = self.db.query(SLO).filter(SLO.id == slo_id).first()
        if not slo:
            raise ValueError(f"SLO {slo_id} not found")

        # Get measurements from window
        since = datetime.utcnow() - timedelta(days=slo.window_days)
        measurements = (
            self.db.query(SLOMeasurement)
            .filter(
                and_(SLOMeasurement.slo_id == slo_id, SLOMeasurement.timestamp >= since)
            )
            .order_by(SLOMeasurement.timestamp)
            .all()
        )

        if not measurements:
            return {
                "slo_id": slo.id,
                "name": slo.name,
                "service": slo.service.name,
                "status": slo.status,
                "current_percentage": None,
                "target_percentage": slo.target_percentage,
                "error_budget_remaining": 100.0,
                "burn_rate": 0.0,
                "measurements_count": 0,
            }

        # Calculate overall statistics
        total_success = sum(m.success_count for m in measurements)
        total_requests = sum(m.total_count for m in measurements)

        current_percentage = (
            (total_success / total_requests * 100) if total_requests > 0 else 100.0
        )

        # Calculate error budget
        error_budget_remaining = max(
            0,
            100
            - (
                (slo.target_percentage - current_percentage)
                / (100 - slo.target_percentage)
                * 100
            ),
        )

        # Get recent burn rate
        recent_measurements = measurements[-10:]  # Last 10 measurements
        avg_burn_rate = sum(m.burn_rate for m in recent_measurements) / len(
            recent_measurements
        )

        return {
            "slo_id": slo.id,
            "name": slo.name,
            "service": slo.service.name,
            "slo_type": slo.slo_type,
            "status": slo.status,
            "current_percentage": round(current_percentage, 3),
            "target_percentage": slo.target_percentage,
            "error_budget_remaining": round(error_budget_remaining, 2),
            "error_budget_consumed": round(100 - error_budget_remaining, 2),
            "burn_rate": round(avg_burn_rate, 4),
            "measurements_count": len(measurements),
            "window_days": slo.window_days,
            "total_requests": total_requests,
            "successful_requests": total_success,
            "failed_requests": total_requests - total_success,
        }

    async def get_slo_history(
        self, slo_id: int, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get SLO measurement history
        """
        since = datetime.utcnow() - timedelta(hours=hours)

        measurements = (
            self.db.query(SLOMeasurement)
            .filter(
                and_(SLOMeasurement.slo_id == slo_id, SLOMeasurement.timestamp >= since)
            )
            .order_by(SLOMeasurement.timestamp)
            .all()
        )

        return [
            {
                "timestamp": m.timestamp.isoformat(),
                "success_percentage": round(m.success_percentage, 3),
                "error_budget_consumed": round(m.error_budget_consumed, 2),
                "burn_rate": round(m.burn_rate, 4),
                "total_count": m.total_count,
                "success_count": m.success_count,
            }
            for m in measurements
        ]

    async def get_all_slos(
        self, service_name: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all SLOs with current status
        """
        query = self.db.query(SLO)

        if service_name:
            query = query.join(Service).filter(Service.name == service_name)

        if status:
            query = query.filter(SLO.status == status)

        slos = query.all()

        result = []
        for slo in slos:
            status_data = await self.get_slo_status(slo.id)
            result.append(status_data)

        return result

    async def check_slo_violations(
        self, service_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Check for SLO violations and breaches
        """
        query = self.db.query(SLO)

        if service_name:
            query = query.join(Service).filter(Service.name == service_name)

        slos = query.all()

        violations = []

        for slo in slos:
            status_data = await self.get_slo_status(slo.id)

            # Check for violations
            if status_data["current_percentage"] is not None:
                current = status_data["current_percentage"]
                target = slo.target_percentage

                if current < target:
                    violation_type = "breach"
                    severity = "critical"
                elif current < slo.warning_threshold:
                    violation_type = "warning"
                    severity = "warning"
                else:
                    continue

                violations.append(
                    {
                        "slo_id": slo.id,
                        "slo_name": slo.name,
                        "service": slo.service.name,
                        "violation_type": violation_type,
                        "severity": severity,
                        "current_percentage": current,
                        "target_percentage": target,
                        "error_budget_remaining": status_data["error_budget_remaining"],
                        "burn_rate": status_data["burn_rate"],
                    }
                )

        return violations

    async def predict_slo_breach(
        self, slo_id: int, hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """
        Predict if SLO will breach based on current burn rate
        """
        slo = self.db.query(SLO).filter(SLO.id == slo_id).first()
        if not slo:
            raise ValueError(f"SLO {slo_id} not found")

        status_data = await self.get_slo_status(slo_id)

        if status_data["current_percentage"] is None:
            return {
                "will_breach": False,
                "confidence": 0.0,
                "reason": "Insufficient data",
            }

        current_percentage = status_data["current_percentage"]
        burn_rate = status_data["burn_rate"]
        error_budget_remaining = status_data["error_budget_remaining"]

        # Calculate projected percentage after hours_ahead
        projected_error_budget = error_budget_remaining - (burn_rate * hours_ahead)

        will_breach = projected_error_budget <= 0

        # Calculate confidence based on data quality
        measurements_count = status_data["measurements_count"]
        confidence = min(
            measurements_count / 100, 1.0
        )  # Max confidence at 100 measurements

        time_to_breach = None
        if burn_rate > 0 and error_budget_remaining > 0:
            time_to_breach = error_budget_remaining / burn_rate

        return {
            "slo_id": slo.id,
            "slo_name": slo.name,
            "will_breach": will_breach,
            "confidence": round(confidence, 2),
            "current_percentage": current_percentage,
            "target_percentage": slo.target_percentage,
            "error_budget_remaining": error_budget_remaining,
            "burn_rate": burn_rate,
            "projected_error_budget": round(projected_error_budget, 2),
            "time_to_breach_hours": (
                round(time_to_breach, 2) if time_to_breach else None
            ),
            "prediction_window_hours": hours_ahead,
        }

    async def get_slo_report(
        self, service_name: Optional[str] = None, days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate comprehensive SLO report
        """
        query = self.db.query(SLO)

        if service_name:
            query = query.join(Service).filter(Service.name == service_name)

        slos = query.all()

        total_slos = len(slos)
        healthy_slos = sum(1 for s in slos if s.status == SLOStatus.HEALTHY.value)
        warning_slos = sum(1 for s in slos if s.status == SLOStatus.WARNING.value)
        critical_slos = sum(1 for s in slos if s.status == SLOStatus.CRITICAL.value)
        breached_slos = sum(1 for s in slos if s.status == SLOStatus.BREACHED.value)

        # Get detailed status for each SLO
        slo_details = []
        for slo in slos:
            status_data = await self.get_slo_status(slo.id)
            slo_details.append(status_data)

        return {
            "report_period_days": days,
            "total_slos": total_slos,
            "by_status": {
                "healthy": healthy_slos,
                "warning": warning_slos,
                "critical": critical_slos,
                "breached": breached_slos,
            },
            "compliance_rate": round(
                (healthy_slos / total_slos * 100) if total_slos > 0 else 100.0, 2
            ),
            "slos": slo_details,
        }

    async def _calculate_burn_rate(
        self, slo: SLO, error_budget_consumed: float
    ) -> float:
        """
        Calculate current error budget burn rate (per hour)
        """
        # Get recent measurements (last hour)
        since = datetime.utcnow() - timedelta(hours=1)
        recent_measurements = (
            self.db.query(SLOMeasurement)
            .filter(
                and_(SLOMeasurement.slo_id == slo.id, SLOMeasurement.timestamp >= since)
            )
            .all()
        )

        if len(recent_measurements) < 2:
            return 0.0

        # Calculate burn rate based on error budget consumption
        first_measurement = recent_measurements[0]
        last_measurement = recent_measurements[-1]

        budget_change = (
            last_measurement.error_budget_consumed
            - first_measurement.error_budget_consumed
        )
        time_diff_hours = (
            last_measurement.timestamp - first_measurement.timestamp
        ).total_seconds() / 3600

        if time_diff_hours > 0:
            burn_rate = budget_change / time_diff_hours
        else:
            burn_rate = 0.0

        return max(0.0, burn_rate)

    async def _update_slo_status(self, slo: SLO):
        """
        Update SLO status based on current measurements
        """
        status_data = await self.get_slo_status(slo.id)

        if status_data["current_percentage"] is None:
            slo.status = SLOStatus.HEALTHY.value
            return

        current = status_data["current_percentage"]
        target = slo.target_percentage

        # Determine status
        if current < target:
            slo.status = SLOStatus.BREACHED.value
        elif current < slo.critical_threshold:
            slo.status = SLOStatus.CRITICAL.value
        elif current < slo.warning_threshold:
            slo.status = SLOStatus.WARNING.value
        else:
            slo.status = SLOStatus.HEALTHY.value

        # Update current values
        slo.current_percentage = current
        slo.error_budget_remaining = status_data["error_budget_remaining"]
        slo.error_budget_consumed = status_data["error_budget_consumed"]
        slo.burn_rate = status_data["burn_rate"]
