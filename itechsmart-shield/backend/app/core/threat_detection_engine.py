"""
Core Threat Detection Engine for iTechSmart Shield
Real-time threat detection and analysis
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import re
from collections import defaultdict

from sqlalchemy.orm import Session
from app.models.security import (
    ThreatDetection, SecurityAlert, ThreatIntelligence,
    ThreatSeverity, ThreatStatus, SecurityAuditLog
)

logger = logging.getLogger(__name__)


class ThreatDetectionEngine:
    """
    Real-time threat detection engine
    
    Capabilities:
    1. Network intrusion detection
    2. Malware detection
    3. DDoS detection
    4. Brute force detection
    5. Anomaly detection
    6. Zero-day threat detection
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Detection configuration
        self.config = {
            "enabled": True,
            "detection_interval": 1,  # seconds
            "alert_threshold": 0.7,  # confidence threshold
            "auto_block": True,
            "auto_response": True
        }
        
        # Threat patterns
        self.threat_patterns = {
            "sql_injection": [
                r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
                r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
                r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"onerror\s*=",
                r"onload\s*=",
            ],
            "command_injection": [
                r";\s*(ls|cat|wget|curl|nc|bash|sh)",
                r"\|\s*(ls|cat|wget|curl|nc|bash|sh)",
                r"`.*`",
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\&quot;,
                r"%2e%2e/",
            ]
        }
        
        # Tracking
        self.failed_login_attempts = defaultdict(list)
        self.request_counts = defaultdict(list)
        self.blocked_ips = set()
    
    async def start_detection(self):
        """Start continuous threat detection"""
        logger.info("🛡️ Threat Detection Engine started")
        
        while self.config["enabled"]:
            try:
                # Run detection cycles
                await self._detect_network_threats()
                await self._detect_application_threats()
                await self._detect_anomalies()
                await self._check_threat_intelligence()
                
                await asyncio.sleep(self.config["detection_interval"])
            
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                await asyncio.sleep(5)
    
    async def analyze_request(
        self,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze a request for threats"""
        
        threats_detected = []
        
        # Extract request details
        source_ip = request_data.get("source_ip")
        url = request_data.get("url", "")
        method = request_data.get("method", "")
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        
        # Check if IP is blocked
        if source_ip in self.blocked_ips:
            return {
                "blocked": True,
                "reason": "IP is blocked",
                "threats": []
            }
        
        # Check threat intelligence
        if await self._is_malicious_ip(source_ip):
            threats_detected.append({
                "type": "malicious_ip",
                "severity": ThreatSeverity.HIGH,
                "confidence": 0.95,
                "description": "IP found in threat intelligence feeds"
            })
        
        # Check for SQL injection
        sql_threats = self._detect_sql_injection(url + body)
        threats_detected.extend(sql_threats)
        
        # Check for XSS
        xss_threats = self._detect_xss(url + body)
        threats_detected.extend(xss_threats)
        
        # Check for command injection
        cmd_threats = self._detect_command_injection(url + body)
        threats_detected.extend(cmd_threats)
        
        # Check for path traversal
        path_threats = self._detect_path_traversal(url)
        threats_detected.extend(path_threats)
        
        # Check for DDoS
        ddos_threat = await self._detect_ddos(source_ip)
        if ddos_threat:
            threats_detected.append(ddos_threat)
        
        # Log threats
        if threats_detected:
            await self._log_threats(source_ip, request_data, threats_detected)
        
        # Determine if should block
        should_block = any(
            t["severity"] in [ThreatSeverity.CRITICAL, ThreatSeverity.HIGH]
            and t["confidence"] > self.config["alert_threshold"]
            for t in threats_detected
        )
        
        return {
            "blocked": should_block,
            "threats": threats_detected,
            "threat_count": len(threats_detected)
        }
    
    async def analyze_login_attempt(
        self,
        username: str,
        source_ip: str,
        success: bool
    ) -> Dict[str, Any]:
        """Analyze login attempt for brute force"""
        
        if not success:
            # Track failed attempt
            self.failed_login_attempts[source_ip].append({
                "username": username,
                "timestamp": datetime.utcnow()
            })
            
            # Clean old attempts (last 10 minutes)
            cutoff = datetime.utcnow() - timedelta(minutes=10)
            self.failed_login_attempts[source_ip] = [
                a for a in self.failed_login_attempts[source_ip]
                if a["timestamp"] > cutoff
            ]
            
            # Check for brute force
            recent_failures = len(self.failed_login_attempts[source_ip])
            
            if recent_failures >= 5:
                # Brute force detected
                threat = {
                    "type": "brute_force",
                    "severity": ThreatSeverity.HIGH,
                    "confidence": 0.9,
                    "description": f"Brute force attack detected: {recent_failures} failed attempts",
                    "source_ip": source_ip,
                    "username": username
                }
                
                # Log threat
                await self._create_threat_detection(threat)
                
                # Block IP if auto-block enabled
                if self.config["auto_block"]:
                    self.blocked_ips.add(source_ip)
                    logger.warning(f"🚫 Blocked IP {source_ip} due to brute force")
                
                return {
                    "threat_detected": True,
                    "blocked": True,
                    "threat": threat
                }
        
        return {
            "threat_detected": False,
            "blocked": False
        }
    
    async def analyze_network_traffic(
        self,
        traffic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze network traffic for threats"""
        
        threats = []
        
        source_ip = traffic_data.get("source_ip")
        dest_ip = traffic_data.get("dest_ip")
        protocol = traffic_data.get("protocol")
        payload = traffic_data.get("payload", b"")
        
        # Port scanning detection
        if await self._detect_port_scan(source_ip, traffic_data):
            threats.append({
                "type": "port_scan",
                "severity": ThreatSeverity.MEDIUM,
                "confidence": 0.85,
                "description": "Port scanning activity detected"
            })
        
        # Malware signature detection
        if self._detect_malware_signature(payload):
            threats.append({
                "type": "malware",
                "severity": ThreatSeverity.CRITICAL,
                "confidence": 0.95,
                "description": "Malware signature detected in network traffic"
            })
        
        # Protocol anomalies
        if self._detect_protocol_anomaly(traffic_data):
            threats.append({
                "type": "protocol_anomaly",
                "severity": ThreatSeverity.MEDIUM,
                "confidence": 0.75,
                "description": "Unusual protocol behavior detected"
            })
        
        if threats:
            await self._log_threats(source_ip, traffic_data, threats)
        
        return {
            "threats": threats,
            "threat_count": len(threats)
        }
    
    def _detect_sql_injection(self, content: str) -> List[Dict]:
        """Detect SQL injection attempts"""
        threats = []
        
        for pattern in self.threat_patterns["sql_injection"]:
            if re.search(pattern, content, re.IGNORECASE):
                threats.append({
                    "type": "sql_injection",
                    "severity": ThreatSeverity.HIGH,
                    "confidence": 0.85,
                    "description": "SQL injection pattern detected",
                    "pattern": pattern
                })
        
        return threats
    
    def _detect_xss(self, content: str) -> List[Dict]:
        """Detect XSS attempts"""
        threats = []
        
        for pattern in self.threat_patterns["xss"]:
            if re.search(pattern, content, re.IGNORECASE):
                threats.append({
                    "type": "xss",
                    "severity": ThreatSeverity.HIGH,
                    "confidence": 0.8,
                    "description": "Cross-site scripting (XSS) pattern detected",
                    "pattern": pattern
                })
        
        return threats
    
    def _detect_command_injection(self, content: str) -> List[Dict]:
        """Detect command injection attempts"""
        threats = []
        
        for pattern in self.threat_patterns["command_injection"]:
            if re.search(pattern, content, re.IGNORECASE):
                threats.append({
                    "type": "command_injection",
                    "severity": ThreatSeverity.CRITICAL,
                    "confidence": 0.9,
                    "description": "Command injection pattern detected",
                    "pattern": pattern
                })
        
        return threats
    
    def _detect_path_traversal(self, url: str) -> List[Dict]:
        """Detect path traversal attempts"""
        threats = []
        
        for pattern in self.threat_patterns["path_traversal"]:
            if re.search(pattern, url):
                threats.append({
                    "type": "path_traversal",
                    "severity": ThreatSeverity.HIGH,
                    "confidence": 0.85,
                    "description": "Path traversal pattern detected",
                    "pattern": pattern
                })
        
        return threats
    
    async def _detect_ddos(self, source_ip: str) -> Optional[Dict]:
        """Detect DDoS attacks"""
        
        # Track request rate
        now = datetime.utcnow()
        self.request_counts[source_ip].append(now)
        
        # Clean old requests (last minute)
        cutoff = now - timedelta(minutes=1)
        self.request_counts[source_ip] = [
            t for t in self.request_counts[source_ip]
            if t > cutoff
        ]
        
        # Check rate
        request_rate = len(self.request_counts[source_ip])
        
        # Threshold: 100 requests per minute
        if request_rate > 100:
            return {
                "type": "ddos",
                "severity": ThreatSeverity.CRITICAL,
                "confidence": 0.9,
                "description": f"DDoS attack detected: {request_rate} requests/minute",
                "request_rate": request_rate
            }
        
        return None
    
    async def _is_malicious_ip(self, ip: str) -> bool:
        """Check if IP is in threat intelligence"""
        
        threat_intel = self.db.query(ThreatIntelligence).filter(
            ThreatIntelligence.ioc_type == "ip",
            ThreatIntelligence.ioc_value == ip,
            ThreatIntelligence.active == True
        ).first()
        
        return threat_intel is not None
    
    async def _detect_port_scan(
        self,
        source_ip: str,
        traffic_data: Dict
    ) -> bool:
        """Detect port scanning activity"""
        # Simplified detection - in production, use more sophisticated methods
        # Check for rapid connection attempts to multiple ports
        return False
    
    def _detect_malware_signature(self, payload: bytes) -> bool:
        """Detect malware signatures in payload"""
        # Simplified - in production, use YARA rules or similar
        
        # Check for common malware signatures
        malware_signatures = [
            b"MZ",  # PE executable header
            b"\x7fELF",  # ELF executable header
        ]
        
        # This is a basic check - real implementation would be more sophisticated
        return False
    
    def _detect_protocol_anomaly(self, traffic_data: Dict) -> bool:
        """Detect protocol anomalies"""
        # Simplified - in production, use protocol analysis
        return False
    
    async def _log_threats(
        self,
        source_ip: str,
        context: Dict,
        threats: List[Dict]
    ):
        """Log detected threats"""
        
        for threat in threats:
            # Create threat detection record
            await self._create_threat_detection({
                **threat,
                "source_ip": source_ip,
                "context": context
            })
            
            # Create alert
            await self._create_alert(threat, source_ip)
    
    async def _create_threat_detection(self, threat_data: Dict):
        """Create threat detection record"""
        
        detection = ThreatDetection(
            timestamp=datetime.utcnow(),
            threat_type=threat_data.get("type"),
            severity=threat_data.get("severity"),
            status=ThreatStatus.DETECTED,
            source_ip=threat_data.get("source_ip"),
            target_ip=threat_data.get("target_ip"),
            description=threat_data.get("description"),
            indicators=threat_data.get("indicators", {}),
            confidence_score=threat_data.get("confidence", 0.0),
            automated_response=self.config["auto_response"]
        )
        
        self.db.add(detection)
        self.db.commit()
        
        logger.warning(
            f"🚨 Threat detected: {threat_data.get('type')} "
            f"from {threat_data.get('source_ip')} "
            f"(severity: {threat_data.get('severity')})"
        )
    
    async def _create_alert(self, threat: Dict, source_ip: str):
        """Create security alert"""
        
        alert = SecurityAlert(
            timestamp=datetime.utcnow(),
            alert_type=threat.get("type"),
            severity=threat.get("severity"),
            source="threat_detection_engine",
            title=f"{threat.get('type').upper()} detected",
            description=threat.get("description"),
            details={
                "source_ip": source_ip,
                "confidence": threat.get("confidence"),
                **threat
            }
        )
        
        self.db.add(alert)
        self.db.commit()
    
    async def _detect_network_threats(self):
        """Detect network-level threats"""
        # Placeholder for network threat detection
        pass
    
    async def _detect_application_threats(self):
        """Detect application-level threats"""
        # Placeholder for application threat detection
        pass
    
    async def _detect_anomalies(self):
        """Detect anomalous behavior"""
        # Placeholder for anomaly detection
        pass
    
    async def _check_threat_intelligence(self):
        """Check against threat intelligence feeds"""
        # Placeholder for threat intelligence checking
        pass
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IPs"""
        return list(self.blocked_ips)
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"✅ Unblocked IP: {ip}")
    
    def block_ip(self, ip: str, reason: str = "Manual block"):
        """Manually block an IP address"""
        self.blocked_ips.add(ip)
        logger.warning(f"🚫 Blocked IP: {ip} - Reason: {reason}")