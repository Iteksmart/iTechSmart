"""
Comprehensive Test Suite for iTechSmart Supreme
Tests all major features and components
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.models import Alert, AlertSource, SeverityLevel, Platform, HostCredentials
from core.auto_remediation_engine import AutoRemediationEngine, RemediationMode
from core.vm_provisioner import VMProvisioner, CloudProvider, VMSize, VMImage
from core.domain_admin_manager import DomainAdminManager
from execution.command_executor import SecureCommandExecutor
from execution.network_device_manager import NetworkDeviceManager, NetworkVendor
from use_cases.use_case_manager import UseCaseManager
from use_cases.web_server_remediation import WebServerRemediation
from use_cases.security_remediation import SecurityRemediation
from use_cases.system_remediation import SystemRemediation


class FeatureTester:
    """Test all iTechSmart Supreme features"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name: str):
        """Decorator for test functions"""
        def decorator(func):
            self.tests.append((name, func))
            return func
        return decorator
    
    async def run_all_tests(self):
        """Run all registered tests"""
        
        print("=" * 80)
        print("🧪 iTechSmart Supreme - Comprehensive Feature Test")
        print("=" * 80)
        print()
        
        for name, test_func in self.tests:
            try:
                print(f"Testing: {name}...", end=" ")
                await test_func()
                print("✅ PASS")
                self.passed += 1
            except Exception as e:
                print(f"❌ FAIL: {e}")
                self.failed += 1
        
        print()
        print("=" * 80)
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print("=" * 80)
        
        return self.failed == 0


# Create tester instance
tester = FeatureTester()


@tester.test("Core Models")
async def test_models():
    """Test core data models"""
    
    # Test Alert
    alert = Alert(
        source=AlertSource.PROMETHEUS,
        severity=SeverityLevel.HIGH,
        message="High CPU usage",
        host="server-01",
        metrics={'cpu_usage': 95}
    )
    assert alert.id is not None
    assert alert.source == AlertSource.PROMETHEUS
    
    # Test HostCredentials
    creds = HostCredentials(
        host="localhost",
        username="admin",
        platform=Platform.LINUX
    )
    assert creds.host == "localhost"


@tester.test("Command Executor")
async def test_command_executor():
    """Test secure command executor"""
    
    executor = SecureCommandExecutor()
    
    # Test kill switch
    executor.enable_kill_switch()
    assert executor.global_kill_switch == True
    
    executor.disable_kill_switch()
    assert executor.global_kill_switch == False


@tester.test("Use Case Manager")
async def test_use_case_manager():
    """Test use case manager"""
    
    manager = UseCaseManager()
    
    # Test high CPU alert
    alert = Alert(
        source=AlertSource.PROMETHEUS,
        severity=SeverityLevel.HIGH,
        message="High CPU usage detected: 95%",
        host="web-server-01",
        metrics={'cpu_usage': 95, 'metric_type': 'cpu'}
    )
    
    diagnosis = await manager.diagnose_and_remediate(alert)
    assert diagnosis.root_cause is not None
    assert len(diagnosis.recommendations) > 0
    
    # Test statistics
    stats = manager.get_statistics()
    assert 'total_remediations' in stats


@tester.test("Web Server Remediation")
async def test_web_server_remediation():
    """Test web server remediation use case"""
    
    remediation = WebServerRemediation()
    
    # Test Apache detection
    alert = Alert(
        source=AlertSource.PROMETHEUS,
        severity=SeverityLevel.HIGH,
        message="Apache service down",
        host="web-01"
    )
    
    diagnosis = await remediation.diagnose_web_server_issue(alert)
    assert diagnosis.root_cause is not None


@tester.test("Security Remediation")
async def test_security_remediation():
    """Test security remediation use case"""
    
    remediation = SecurityRemediation()
    
    # Test brute force detection
    alert = Alert(
        source=AlertSource.WAZUH,
        severity=SeverityLevel.HIGH,
        message="Brute force attack detected from 192.168.1.100",
        host="server-01",
        metrics={'source_ip': '192.168.1.100'}
    )
    
    diagnosis = await remediation.diagnose_security_incident(alert)
    assert diagnosis.root_cause is not None
    assert '192.168.1.100' in diagnosis.root_cause


@tester.test("System Remediation")
async def test_system_remediation():
    """Test system remediation use case"""
    
    remediation = SystemRemediation()
    
    # Test high CPU
    alert = Alert(
        source=AlertSource.PROMETHEUS,
        severity=SeverityLevel.HIGH,
        message="High CPU usage: 95%",
        host="server-01",
        metrics={'cpu_usage': 95}
    )
    
    diagnosis = await remediation.diagnose_high_cpu(alert)
    assert diagnosis.root_cause is not None
    assert len(diagnosis.recommendations) > 0


@tester.test("Network Device Manager")
async def test_network_device_manager():
    """Test network device manager"""
    
    manager = NetworkDeviceManager()
    
    # Test vendor support
    assert len(NetworkVendor) >= 13
    
    # Test available use cases
    use_cases = manager.__class__.__dict__
    assert 'connect_device' in use_cases
    assert 'configure_vlan' in use_cases
    assert 'configure_interface' in use_cases


@tester.test("VM Provisioner")
async def test_vm_provisioner():
    """Test VM provisioner"""
    
    config = {}
    provisioner = VMProvisioner(config)
    
    # Test cloud provider support
    assert len(CloudProvider) >= 8
    
    # Test VM sizes
    assert len(VMSize) >= 5
    
    # Test VM images
    assert len(VMImage) >= 7
    
    # Test statistics
    stats = provisioner.get_statistics()
    assert 'active_vms' in stats


@tester.test("Domain Admin Manager")
async def test_domain_admin_manager():
    """Test domain admin manager"""
    
    config = {
        'domain_controller': 'dc.example.com',
        'domain': 'example.com',
        'admin_username': 'admin',
        'admin_password': 'password'
    }
    
    manager = DomainAdminManager(config)
    
    # Test statistics
    stats = manager.get_statistics()
    assert 'active_accounts' in stats


@tester.test("Auto-Remediation Engine Configuration")
async def test_auto_remediation_engine():
    """Test auto-remediation engine configuration"""
    
    # Test with minimal config
    engine = AutoRemediationEngine(
        prometheus_endpoints=[],
        wazuh_endpoints=[],
        mode=RemediationMode.MANUAL
    )
    
    assert engine.mode == RemediationMode.MANUAL
    assert engine.running == False
    
    # Test statistics
    stats = engine.get_statistics()
    assert 'total_alerts' in stats
    assert 'mode' in stats


@tester.test("Use Case Detection")
async def test_use_case_detection():
    """Test automatic use case detection"""
    
    manager = UseCaseManager()
    
    # Test different alert types
    test_cases = [
        ("apache service down", "web_server"),
        ("brute force attack", "security"),
        ("high cpu usage", "high_cpu"),
        ("disk space critical", "disk_full"),
        ("ssl certificate expired", "ssl_expiration"),
    ]
    
    for message, expected_type in test_cases:
        alert = Alert(
            source=AlertSource.PROMETHEUS,
            severity=SeverityLevel.HIGH,
            message=message,
            host="test-host"
        )
        
        detected_type = manager._detect_use_case_type(alert)
        assert detected_type == expected_type, f"Expected {expected_type}, got {detected_type}"


@tester.test("Available Use Cases")
async def test_available_use_cases():
    """Test listing available use cases"""
    
    manager = UseCaseManager()
    
    use_cases = manager.list_available_use_cases()
    
    assert 'web_server' in use_cases
    assert 'security' in use_cases
    assert 'system' in use_cases
    
    # Verify specific use cases
    assert 'restart_apache' in use_cases['web_server']
    assert 'block_ip' in use_cases['security']
    assert 'clean_disk' in use_cases['system']


async def main():
    """Run all tests"""
    
    success = await tester.run_all_tests()
    
    if success:
        print()
        print("🎉 All tests passed! iTechSmart Supreme is fully functional.")
        print()
        return 0
    else:
        print()
        print("❌ Some tests failed. Please review the errors above.")
        print()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)