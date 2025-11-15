"""
iTechSmart Suite - Telemetry & Analytics System
Handles usage tracking, performance metrics, and analytics
"""

import os
import json
import uuid
import platform
import psutil
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from collections import defaultdict
import threading
import time

class TelemetryManager:
    """Manages telemetry data collection and reporting"""
    
    # Telemetry server URL
    TELEMETRY_SERVER = "https://telemetry.itechsmart.dev/api/v1"
    
    def __init__(self, enabled: bool = True, anonymous: bool = True):
        self.enabled = enabled
        self.anonymous = anonymous
        self.session_id = str(uuid.uuid4())
        self.installation_id = self._get_installation_id()
        self.telemetry_file = "telemetry.json"
        self.metrics_cache = defaultdict(list)
        self.batch_size = 50
        self.send_interval = 300  # 5 minutes
        
        # Start background sender
        if self.enabled:
            self._start_background_sender()
    
    def _get_installation_id(self) -> str:
        """Get or create unique installation ID"""
        id_file = ".installation_id"
        
        if os.path.exists(id_file):
            with open(id_file, 'r') as f:
                return f.read().strip()
        else:
            installation_id = str(uuid.uuid4())
            with open(id_file, 'w') as f:
                f.write(installation_id)
            return installation_id
    
    def track_event(
        self,
        event_name: str,
        properties: Dict[str, Any] = None,
        user_id: str = None
    ):
        """Track an event"""
        if not self.enabled:
            return
        
        event_data = {
            "event_id": str(uuid.uuid4()),
            "event_name": event_name,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "installation_id": self.installation_id if self.anonymous else None,
            "user_id": None if self.anonymous else user_id,
            "properties": properties or {},
            "system_info": self._get_system_info()
        }
        
        self.metrics_cache["events"].append(event_data)
        self._check_and_send()
    
    def track_page_view(self, page_name: str, properties: Dict = None):
        """Track a page view"""
        self.track_event("page_view", {
            "page_name": page_name,
            **(properties or {})
        })
    
    def track_feature_usage(self, feature_name: str, duration_ms: int = None):
        """Track feature usage"""
        self.track_event("feature_usage", {
            "feature_name": feature_name,
            "duration_ms": duration_ms
        })
    
    def track_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: str = None,
        context: Dict = None
    ):
        """Track an error"""
        self.track_event("error", {
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "context": context or {}
        })
    
    def track_performance(
        self,
        operation_name: str,
        duration_ms: int,
        success: bool = True,
        metadata: Dict = None
    ):
        """Track performance metrics"""
        perf_data = {
            "metric_id": str(uuid.uuid4()),
            "operation_name": operation_name,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "installation_id": self.installation_id,
            "metadata": metadata or {}
        }
        
        self.metrics_cache["performance"].append(perf_data)
        self._check_and_send()
    
    def track_system_metrics(self):
        """Track system resource usage"""
        if not self.enabled:
            return
        
        metrics = {
            "metric_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "installation_id": self.installation_id,
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "network_io": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }
        
        self.metrics_cache["system_metrics"].append(metrics)
        self._check_and_send()
    
    def track_user_action(
        self,
        action_name: str,
        target: str = None,
        value: Any = None
    ):
        """Track user action"""
        self.track_event("user_action", {
            "action_name": action_name,
            "target": target,
            "value": value
        })
    
    def start_session(self, user_id: str = None):
        """Start a new session"""
        self.session_id = str(uuid.uuid4())
        
        self.track_event("session_start", {
            "user_id": user_id if not self.anonymous else None
        })
    
    def end_session(self):
        """End current session"""
        self.track_event("session_end")
        self._send_batch(force=True)
    
    def _get_system_info(self) -> Dict:
        """Get system information"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "processor": platform.processor()
        }
    
    def _check_and_send(self):
        """Check if batch should be sent"""
        total_events = sum(len(events) for events in self.metrics_cache.values())
        
        if total_events >= self.batch_size:
            self._send_batch()
    
    def _send_batch(self, force: bool = False):
        """Send batch of telemetry data"""
        if not self.enabled:
            return
        
        if not force and not self.metrics_cache:
            return
        
        try:
            # Prepare batch
            batch_data = {
                "batch_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "installation_id": self.installation_id,
                "session_id": self.session_id,
                "metrics": dict(self.metrics_cache)
            }
            
            # Send to server
            response = requests.post(
                f"{self.TELEMETRY_SERVER}/batch",
                json=batch_data,
                timeout=5
            )
            
            if response.status_code == 200:
                # Clear cache on success
                self.metrics_cache.clear()
            else:
                # Save to file for retry
                self._save_to_file(batch_data)
                
        except Exception as e:
            # Save to file on error
            self._save_to_file(batch_data)
            print(f"Telemetry send error: {str(e)}")
    
    def _save_to_file(self, data: Dict):
        """Save telemetry data to file"""
        try:
            existing_data = []
            if os.path.exists(self.telemetry_file):
                with open(self.telemetry_file, 'r') as f:
                    existing_data = json.load(f)
            
            existing_data.append(data)
            
            with open(self.telemetry_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving telemetry: {str(e)}")
    
    def _start_background_sender(self):
        """Start background thread to send telemetry periodically"""
        def sender_loop():
            while self.enabled:
                time.sleep(self.send_interval)
                self._send_batch()
        
        thread = threading.Thread(target=sender_loop, daemon=True)
        thread.start()
    
    def get_analytics_summary(self) -> Dict:
        """Get analytics summary"""
        summary = {
            "session_id": self.session_id,
            "installation_id": self.installation_id,
            "events_count": len(self.metrics_cache.get("events", [])),
            "performance_metrics_count": len(self.metrics_cache.get("performance", [])),
            "system_metrics_count": len(self.metrics_cache.get("system_metrics", [])),
            "enabled": self.enabled,
            "anonymous": self.anonymous
        }
        
        return summary


# Context manager for tracking operation duration
class TrackPerformance:
    """Context manager for tracking operation performance"""
    
    def __init__(self, telemetry: TelemetryManager, operation_name: str, metadata: Dict = None):
        self.telemetry = telemetry
        self.operation_name = operation_name
        self.metadata = metadata
        self.start_time = None
        self.success = True
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)
        self.success = exc_type is None
        
        self.telemetry.track_performance(
            self.operation_name,
            duration_ms,
            self.success,
            self.metadata
        )
        
        return False  # Don't suppress exceptions


# CLI interface for telemetry management
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python telemetry_manager.py enable")
        print("  python telemetry_manager.py disable")
        print("  python telemetry_manager.py status")
        print("  python telemetry_manager.py test")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "enable":
        telemetry = TelemetryManager(enabled=True)
        print("Telemetry enabled")
    
    elif command == "disable":
        telemetry = TelemetryManager(enabled=False)
        print("Telemetry disabled")
    
    elif command == "status":
        telemetry = TelemetryManager()
        summary = telemetry.get_analytics_summary()
        print(json.dumps(summary, indent=2))
    
    elif command == "test":
        telemetry = TelemetryManager(enabled=True)
        
        # Test various tracking methods
        telemetry.start_session("test_user")
        telemetry.track_page_view("test_page")
        telemetry.track_feature_usage("test_feature", 1000)
        telemetry.track_user_action("click", "test_button")
        
        with TrackPerformance(telemetry, "test_operation"):
            time.sleep(0.1)
        
        telemetry.track_system_metrics()
        telemetry.end_session()
        
        print("Test events tracked successfully")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)