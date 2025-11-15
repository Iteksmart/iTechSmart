"""
iTechSmart Suite - Crash Reporting System
Handles crash detection, reporting, and recovery
"""

import os
import sys
import json
import traceback
import platform
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import requests
import psutil

class CrashReporter:
    """Manages crash detection and reporting"""
    
    # Crash reporting server URL
    CRASH_SERVER = "https://crashes.itechsmart.dev/api/v1"
    
    def __init__(self, app_name: str = "iTechSmart Suite", version: str = "1.0.0"):
        self.app_name = app_name
        self.version = version
        self.crash_dir = ".crashes"
        self.enabled = True
        
        # Create crash directory
        os.makedirs(self.crash_dir, exist_ok=True)
        
        # Install exception handler
        sys.excepthook = self._exception_handler
    
    def _exception_handler(self, exc_type, exc_value, exc_traceback):
        """Global exception handler"""
        if self.enabled:
            self.report_crash(exc_type, exc_value, exc_traceback)
        
        # Call default handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    def report_crash(
        self,
        exc_type,
        exc_value,
        exc_traceback,
        context: Dict = None
    ) -> str:
        """
        Report a crash
        Returns: crash_id
        """
        try:
            # Generate crash ID
            crash_id = self._generate_crash_id(exc_type, exc_value)
            
            # Collect crash data
            crash_data = self._collect_crash_data(
                exc_type,
                exc_value,
                exc_traceback,
                context
            )
            
            # Save crash report locally
            self._save_crash_report(crash_id, crash_data)
            
            # Send to server
            self._send_crash_report(crash_id, crash_data)
            
            return crash_id
            
        except Exception as e:
            print(f"Error reporting crash: {str(e)}")
            return None
    
    def _collect_crash_data(
        self,
        exc_type,
        exc_value,
        exc_traceback,
        context: Dict = None
    ) -> Dict:
        """Collect comprehensive crash data"""
        
        # Extract stack trace
        stack_trace = ''.join(traceback.format_exception(
            exc_type,
            exc_value,
            exc_traceback
        ))
        
        # Get system information
        system_info = self._get_system_info()
        
        # Get process information
        process_info = self._get_process_info()
        
        # Build crash data
        crash_data = {
            "app_name": self.app_name,
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "exception": {
                "type": exc_type.__name__,
                "message": str(exc_value),
                "stack_trace": stack_trace
            },
            "system": system_info,
            "process": process_info,
            "context": context or {}
        }
        
        return crash_data
    
    def _get_system_info(self) -> Dict:
        """Get system information"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }
    
    def _get_process_info(self) -> Dict:
        """Get process information"""
        try:
            process = psutil.Process()
            
            return {
                "pid": process.pid,
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "num_threads": process.num_threads(),
                "create_time": datetime.fromtimestamp(
                    process.create_time()
                ).isoformat()
            }
        except:
            return {}
    
    def _generate_crash_id(self, exc_type, exc_value) -> str:
        """Generate unique crash ID"""
        crash_string = f"{exc_type.__name__}:{str(exc_value)}:{datetime.now().isoformat()}"
        return hashlib.sha256(crash_string.encode()).hexdigest()[:16]
    
    def _save_crash_report(self, crash_id: str, crash_data: Dict):
        """Save crash report to local file"""
        crash_file = os.path.join(self.crash_dir, f"crash_{crash_id}.json")
        
        with open(crash_file, 'w') as f:
            json.dump(crash_data, f, indent=2)
    
    def _send_crash_report(self, crash_id: str, crash_data: Dict):
        """Send crash report to server"""
        try:
            response = requests.post(
                f"{self.CRASH_SERVER}/report",
                json={
                    "crash_id": crash_id,
                    "crash_data": crash_data
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Crash report sent: {crash_id}")
            else:
                print(f"Failed to send crash report: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"Error sending crash report: {str(e)}")
    
    def get_crash_reports(self) -> list:
        """Get all crash reports"""
        reports = []
        
        for filename in os.listdir(self.crash_dir):
            if filename.startswith("crash_") and filename.endswith(".json"):
                filepath = os.path.join(self.crash_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        report = json.load(f)
                        reports.append(report)
                except:
                    pass
        
        return reports
    
    def clear_crash_reports(self):
        """Clear all crash reports"""
        for filename in os.listdir(self.crash_dir):
            if filename.startswith("crash_"):
                filepath = os.path.join(self.crash_dir, filename)
                os.remove(filepath)
    
    def enable(self):
        """Enable crash reporting"""
        self.enabled = True
    
    def disable(self):
        """Disable crash reporting"""
        self.enabled = False


# Decorator for crash-safe functions
def crash_safe(reporter: CrashReporter):
    """Decorator to make functions crash-safe"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                reporter.report_crash(
                    type(e),
                    e,
                    sys.exc_info()[2],
                    context={
                        "function": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }
                )
                raise
        return wrapper
    return decorator


# Context manager for crash reporting
class CrashContext:
    """Context manager for crash reporting with additional context"""
    
    def __init__(self, reporter: CrashReporter, context: Dict):
        self.reporter = reporter
        self.context = context
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            self.reporter.report_crash(
                exc_type,
                exc_value,
                exc_traceback,
                self.context
            )
        return False  # Don't suppress exceptions


# CLI interface for crash reporting
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python crash_reporter.py list")
        print("  python crash_reporter.py clear")
        print("  python crash_reporter.py test")
        sys.exit(1)
    
    command = sys.argv[1]
    reporter = CrashReporter()
    
    if command == "list":
        reports = reporter.get_crash_reports()
        print(f"Found {len(reports)} crash reports:")
        for report in reports:
            print(f"\n{report['timestamp']}")
            print(f"  Exception: {report['exception']['type']}")
            print(f"  Message: {report['exception']['message']}")
    
    elif command == "clear":
        reporter.clear_crash_reports()
        print("Crash reports cleared")
    
    elif command == "test":
        print("Testing crash reporter...")
        
        try:
            # Intentionally cause an error
            raise ValueError("Test crash")
        except Exception as e:
            crash_id = reporter.report_crash(
                type(e),
                e,
                sys.exc_info()[2],
                context={"test": True}
            )
            print(f"Test crash reported: {crash_id}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)