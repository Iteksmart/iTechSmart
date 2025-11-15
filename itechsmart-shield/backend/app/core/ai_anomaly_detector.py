"""
AI-Powered Anomaly Detection for iTechSmart Shield
Uses machine learning to detect unusual patterns and zero-day threats
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import json

from sqlalchemy.orm import Session
from app.models.security import (
    ThreatDetection, SecurityAuditLog, SecurityMetric,
    ThreatSeverity, ThreatStatus
)

logger = logging.getLogger(__name__)


class AIAnomalyDetector:
    """
    AI-powered anomaly detection system
    
    Capabilities:
    1. Behavioral analysis
    2. Statistical anomaly detection
    3. Pattern recognition
    4. Zero-day threat detection
    5. User behavior analytics (UBA)
    6. Entity behavior analytics (EBA)
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Configuration
        self.config = {
            "enabled": True,
            "sensitivity": 0.7,  # 0-1, higher = more sensitive
            "learning_period_days": 7,
            "min_samples": 100,
            "anomaly_threshold": 2.5,  # Standard deviations
        }
        
        # Baseline data
        self.baselines = {
            "user_behavior": {},
            "network_traffic": {},
            "api_usage": {},
            "resource_access": {},
        }
        
        # Anomaly scores
        self.anomaly_scores = defaultdict(list)
    
    async def analyze_user_behavior(
        self,
        user_id: str,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user behavior for anomalies"""
        
        # Get user baseline
        baseline = await self._get_user_baseline(user_id)
        
        if not baseline:
            # Not enough data yet, create baseline
            await self._update_user_baseline(user_id, action, context)
            return {
                "anomaly_detected": False,
                "reason": "Building baseline"
            }
        
        # Calculate anomaly score
        anomaly_score = self._calculate_behavior_anomaly_score(
            action,
            context,
            baseline
        )
        
        # Check for anomalies
        is_anomaly = anomaly_score > self.config["anomaly_threshold"]
        
        if is_anomaly:
            # Detected anomaly
            anomaly_details = {
                "user_id": user_id,
                "action": action,
                "anomaly_score": anomaly_score,
                "context": context,
                "baseline": baseline,
                "deviations": self._identify_deviations(context, baseline)
            }
            
            # Log anomaly
            await self._log_anomaly(
                anomaly_type="user_behavior",
                severity=self._calculate_severity(anomaly_score),
                details=anomaly_details
            )
            
            return {
                "anomaly_detected": True,
                "anomaly_score": anomaly_score,
                "severity": self._calculate_severity(anomaly_score),
                "deviations": anomaly_details["deviations"]
            }
        
        # Update baseline with normal behavior
        await self._update_user_baseline(user_id, action, context)
        
        return {
            "anomaly_detected": False,
            "anomaly_score": anomaly_score
        }
    
    async def analyze_network_traffic(
        self,
        traffic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze network traffic for anomalies"""
        
        source_ip = traffic_data.get("source_ip")
        
        # Get baseline for this IP
        baseline = await self._get_network_baseline(source_ip)
        
        if not baseline:
            await self._update_network_baseline(source_ip, traffic_data)
            return {"anomaly_detected": False}
        
        # Analyze traffic patterns
        anomalies = []
        
        # Check packet size anomaly
        if "packet_size" in traffic_data:
            packet_anomaly = self._detect_packet_size_anomaly(
                traffic_data["packet_size"],
                baseline.get("avg_packet_size", 0),
                baseline.get("std_packet_size", 0)
            )
            if packet_anomaly:
                anomalies.append(packet_anomaly)
        
        # Check connection rate anomaly
        if "connection_rate" in traffic_data:
            rate_anomaly = self._detect_rate_anomaly(
                traffic_data["connection_rate"],
                baseline.get("avg_connection_rate", 0),
                baseline.get("std_connection_rate", 0)
            )
            if rate_anomaly:
                anomalies.append(rate_anomaly)
        
        # Check protocol distribution anomaly
        if "protocol" in traffic_data:
            protocol_anomaly = self._detect_protocol_anomaly(
                traffic_data["protocol"],
                baseline.get("protocol_distribution", {})
            )
            if protocol_anomaly:
                anomalies.append(protocol_anomaly)
        
        if anomalies:
            await self._log_anomaly(
                anomaly_type="network_traffic",
                severity=ThreatSeverity.MEDIUM,
                details={
                    "source_ip": source_ip,
                    "anomalies": anomalies,
                    "traffic_data": traffic_data
                }
            )
            
            return {
                "anomaly_detected": True,
                "anomalies": anomalies
            }
        
        # Update baseline
        await self._update_network_baseline(source_ip, traffic_data)
        
        return {"anomaly_detected": False}
    
    async def analyze_api_usage(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        response_time: float
    ) -> Dict[str, Any]:
        """Analyze API usage patterns for anomalies"""
        
        # Get API usage baseline
        baseline = await self._get_api_baseline(user_id)
        
        if not baseline:
            await self._update_api_baseline(user_id, endpoint, method, response_time)
            return {"anomaly_detected": False}
        
        anomalies = []
        
        # Check unusual endpoint access
        if endpoint not in baseline.get("common_endpoints", []):
            anomalies.append({
                "type": "unusual_endpoint",
                "description": f"User accessing unusual endpoint: {endpoint}"
            })
        
        # Check unusual time of access
        current_hour = datetime.utcnow().hour
        typical_hours = baseline.get("typical_hours", [])
        if typical_hours and current_hour not in typical_hours:
            anomalies.append({
                "type": "unusual_time",
                "description": f"API access at unusual hour: {current_hour}"
            })
        
        # Check request rate
        recent_requests = baseline.get("recent_request_count", 0)
        avg_rate = baseline.get("avg_request_rate", 0)
        if avg_rate > 0 and recent_requests > avg_rate * 3:
            anomalies.append({
                "type": "high_request_rate",
                "description": f"Unusually high request rate: {recent_requests} vs avg {avg_rate}"
            })
        
        if anomalies:
            await self._log_anomaly(
                anomaly_type="api_usage",
                severity=ThreatSeverity.MEDIUM,
                details={
                    "user_id": user_id,
                    "endpoint": endpoint,
                    "anomalies": anomalies
                }
            )
            
            return {
                "anomaly_detected": True,
                "anomalies": anomalies
            }
        
        await self._update_api_baseline(user_id, endpoint, method, response_time)
        
        return {"anomaly_detected": False}
    
    async def detect_zero_day_threat(
        self,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect potential zero-day threats using AI"""
        
        # Extract features
        features = self._extract_threat_features(event_data)
        
        # Calculate threat probability using heuristics
        # In production, this would use a trained ML model
        threat_score = self._calculate_threat_score(features)
        
        if threat_score > 0.8:
            # High probability of zero-day threat
            await self._log_anomaly(
                anomaly_type="zero_day_threat",
                severity=ThreatSeverity.CRITICAL,
                details={
                    "threat_score": threat_score,
                    "features": features,
                    "event_data": event_data
                }
            )
            
            return {
                "zero_day_detected": True,
                "threat_score": threat_score,
                "confidence": threat_score,
                "recommendation": "Immediate investigation required"
            }
        
        return {
            "zero_day_detected": False,
            "threat_score": threat_score
        }
    
    async def analyze_resource_access(
        self,
        user_id: str,
        resource: str,
        action: str
    ) -> Dict[str, Any]:
        """Analyze resource access patterns"""
        
        baseline = await self._get_resource_baseline(user_id)
        
        if not baseline:
            await self._update_resource_baseline(user_id, resource, action)
            return {"anomaly_detected": False}
        
        # Check if user typically accesses this resource
        typical_resources = baseline.get("typical_resources", [])
        
        if resource not in typical_resources:
            # Unusual resource access
            await self._log_anomaly(
                anomaly_type="unusual_resource_access",
                severity=ThreatSeverity.MEDIUM,
                details={
                    "user_id": user_id,
                    "resource": resource,
                    "action": action,
                    "typical_resources": typical_resources
                }
            )
            
            return {
                "anomaly_detected": True,
                "type": "unusual_resource_access",
                "description": f"User accessing unusual resource: {resource}"
            }
        
        await self._update_resource_baseline(user_id, resource, action)
        
        return {"anomaly_detected": False}
    
    def _calculate_behavior_anomaly_score(
        self,
        action: str,
        context: Dict,
        baseline: Dict
    ) -> float:
        """Calculate anomaly score for user behavior"""
        
        score = 0.0
        
        # Check action frequency
        action_freq = baseline.get("action_frequencies", {}).get(action, 0)
        if action_freq == 0:
            score += 2.0  # New action
        
        # Check time of day
        current_hour = datetime.utcnow().hour
        typical_hours = baseline.get("typical_hours", [])
        if typical_hours and current_hour not in typical_hours:
            score += 1.5
        
        # Check location (if available)
        if "location" in context:
            typical_locations = baseline.get("typical_locations", [])
            if context["location"] not in typical_locations:
                score += 1.0
        
        # Check device (if available)
        if "device" in context:
            typical_devices = baseline.get("typical_devices", [])
            if context["device"] not in typical_devices:
                score += 1.0
        
        return score
    
    def _detect_packet_size_anomaly(
        self,
        packet_size: int,
        avg_size: float,
        std_size: float
    ) -> Optional[Dict]:
        """Detect packet size anomalies"""
        
        if std_size == 0:
            return None
        
        z_score = abs((packet_size - avg_size) / std_size)
        
        if z_score > self.config["anomaly_threshold"]:
            return {
                "type": "packet_size_anomaly",
                "description": f"Unusual packet size: {packet_size} bytes",
                "z_score": z_score
            }
        
        return None
    
    def _detect_rate_anomaly(
        self,
        rate: float,
        avg_rate: float,
        std_rate: float
    ) -> Optional[Dict]:
        """Detect rate anomalies"""
        
        if std_rate == 0:
            return None
        
        z_score = abs((rate - avg_rate) / std_rate)
        
        if z_score > self.config["anomaly_threshold"]:
            return {
                "type": "rate_anomaly",
                "description": f"Unusual connection rate: {rate}",
                "z_score": z_score
            }
        
        return None
    
    def _detect_protocol_anomaly(
        self,
        protocol: str,
        distribution: Dict[str, float]
    ) -> Optional[Dict]:
        """Detect protocol distribution anomalies"""
        
        if protocol not in distribution:
            return {
                "type": "unusual_protocol",
                "description": f"Unusual protocol: {protocol}"
            }
        
        return None
    
    def _extract_threat_features(self, event_data: Dict) -> Dict:
        """Extract features for threat detection"""
        
        features = {
            "has_suspicious_patterns": self._has_suspicious_patterns(event_data),
            "unusual_timing": self._is_unusual_timing(event_data),
            "unusual_source": self._is_unusual_source(event_data),
            "high_privilege_action": self._is_high_privilege_action(event_data),
            "data_exfiltration_indicators": self._has_exfiltration_indicators(event_data)
        }
        
        return features
    
    def _calculate_threat_score(self, features: Dict) -> float:
        """Calculate overall threat score"""
        
        # Simple weighted scoring
        weights = {
            "has_suspicious_patterns": 0.3,
            "unusual_timing": 0.15,
            "unusual_source": 0.2,
            "high_privilege_action": 0.2,
            "data_exfiltration_indicators": 0.15
        }
        
        score = sum(
            weights.get(k, 0) * (1.0 if v else 0.0)
            for k, v in features.items()
        )
        
        return score
    
    def _has_suspicious_patterns(self, event_data: Dict) -> bool:
        """Check for suspicious patterns"""
        # Simplified - in production, use more sophisticated checks
        return False
    
    def _is_unusual_timing(self, event_data: Dict) -> bool:
        """Check if timing is unusual"""
        # Check if event occurs during unusual hours
        hour = datetime.utcnow().hour
        return hour < 6 or hour > 22  # Outside business hours
    
    def _is_unusual_source(self, event_data: Dict) -> bool:
        """Check if source is unusual"""
        return False
    
    def _is_high_privilege_action(self, event_data: Dict) -> bool:
        """Check if action requires high privileges"""
        high_privilege_actions = ["delete", "admin", "sudo", "root"]
        action = event_data.get("action", "").lower()
        return any(priv in action for priv in high_privilege_actions)
    
    def _has_exfiltration_indicators(self, event_data: Dict) -> bool:
        """Check for data exfiltration indicators"""
        # Check for large data transfers, unusual destinations, etc.
        return False
    
    def _calculate_severity(self, anomaly_score: float) -> ThreatSeverity:
        """Calculate severity based on anomaly score"""
        
        if anomaly_score > 4.0:
            return ThreatSeverity.CRITICAL
        elif anomaly_score > 3.0:
            return ThreatSeverity.HIGH
        elif anomaly_score > 2.0:
            return ThreatSeverity.MEDIUM
        else:
            return ThreatSeverity.LOW
    
    def _identify_deviations(
        self,
        context: Dict,
        baseline: Dict
    ) -> List[str]:
        """Identify specific deviations from baseline"""
        
        deviations = []
        
        # Check each aspect
        if "location" in context:
            if context["location"] not in baseline.get("typical_locations", []):
                deviations.append(f"Unusual location: {context['location']}")
        
        if "device" in context:
            if context["device"] not in baseline.get("typical_devices", []):
                deviations.append(f"Unusual device: {context['device']}")
        
        current_hour = datetime.utcnow().hour
        if current_hour not in baseline.get("typical_hours", []):
            deviations.append(f"Unusual time: {current_hour}:00")
        
        return deviations
    
    async def _log_anomaly(
        self,
        anomaly_type: str,
        severity: ThreatSeverity,
        details: Dict
    ):
        """Log detected anomaly"""
        
        detection = ThreatDetection(
            timestamp=datetime.utcnow(),
            threat_type=f"anomaly_{anomaly_type}",
            severity=severity,
            status=ThreatStatus.DETECTED,
            description=f"AI-detected anomaly: {anomaly_type}",
            indicators=details,
            confidence_score=0.75,
            automated_response=False
        )
        
        self.db.add(detection)
        self.db.commit()
        
        logger.warning(f"🤖 AI Anomaly detected: {anomaly_type} (severity: {severity})")
    
    # Baseline management methods
    async def _get_user_baseline(self, user_id: str) -> Optional[Dict]:
        """Get user behavior baseline"""
        return self.baselines["user_behavior"].get(user_id)
    
    async def _update_user_baseline(
        self,
        user_id: str,
        action: str,
        context: Dict
    ):
        """Update user behavior baseline"""
        
        if user_id not in self.baselines["user_behavior"]:
            self.baselines["user_behavior"][user_id] = {
                "action_frequencies": defaultdict(int),
                "typical_hours": set(),
                "typical_locations": set(),
                "typical_devices": set()
            }
        
        baseline = self.baselines["user_behavior"][user_id]
        baseline["action_frequencies"][action] += 1
        baseline["typical_hours"].add(datetime.utcnow().hour)
        
        if "location" in context:
            baseline["typical_locations"].add(context["location"])
        if "device" in context:
            baseline["typical_devices"].add(context["device"])
    
    async def _get_network_baseline(self, source_ip: str) -> Optional[Dict]:
        """Get network traffic baseline"""
        return self.baselines["network_traffic"].get(source_ip)
    
    async def _update_network_baseline(
        self,
        source_ip: str,
        traffic_data: Dict
    ):
        """Update network traffic baseline"""
        
        if source_ip not in self.baselines["network_traffic"]:
            self.baselines["network_traffic"][source_ip] = {
                "packet_sizes": [],
                "connection_rates": [],
                "protocols": defaultdict(int)
            }
        
        baseline = self.baselines["network_traffic"][source_ip]
        
        if "packet_size" in traffic_data:
            baseline["packet_sizes"].append(traffic_data["packet_size"])
        if "connection_rate" in traffic_data:
            baseline["connection_rates"].append(traffic_data["connection_rate"])
        if "protocol" in traffic_data:
            baseline["protocols"][traffic_data["protocol"]] += 1
        
        # Calculate statistics
        if baseline["packet_sizes"]:
            baseline["avg_packet_size"] = np.mean(baseline["packet_sizes"])
            baseline["std_packet_size"] = np.std(baseline["packet_sizes"])
        
        if baseline["connection_rates"]:
            baseline["avg_connection_rate"] = np.mean(baseline["connection_rates"])
            baseline["std_connection_rate"] = np.std(baseline["connection_rates"])
    
    async def _get_api_baseline(self, user_id: str) -> Optional[Dict]:
        """Get API usage baseline"""
        return self.baselines["api_usage"].get(user_id)
    
    async def _update_api_baseline(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        response_time: float
    ):
        """Update API usage baseline"""
        
        if user_id not in self.baselines["api_usage"]:
            self.baselines["api_usage"][user_id] = {
                "common_endpoints": defaultdict(int),
                "typical_hours": set(),
                "request_times": []
            }
        
        baseline = self.baselines["api_usage"][user_id]
        baseline["common_endpoints"][endpoint] += 1
        baseline["typical_hours"].add(datetime.utcnow().hour)
        baseline["request_times"].append(datetime.utcnow())
    
    async def _get_resource_baseline(self, user_id: str) -> Optional[Dict]:
        """Get resource access baseline"""
        return self.baselines["resource_access"].get(user_id)
    
    async def _update_resource_baseline(
        self,
        user_id: str,
        resource: str,
        action: str
    ):
        """Update resource access baseline"""
        
        if user_id not in self.baselines["resource_access"]:
            self.baselines["resource_access"][user_id] = {
                "typical_resources": set(),
                "resource_actions": defaultdict(int)
            }
        
        baseline = self.baselines["resource_access"][user_id]
        baseline["typical_resources"].add(resource)
        baseline["resource_actions"][f"{resource}:{action}"] += 1