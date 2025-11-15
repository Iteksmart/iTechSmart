"""
iTechSmart Suite - Integration Test Framework
Comprehensive testing framework for cross-product integration
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import time


class IntegrationTestFramework:
    """Framework for testing cross-product integrations"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.test_results = []
        self.tenant_id = 1
        self.timeout = 30.0
        
        # Product endpoints
        self.endpoints = {
            "hub": f"{base_url}:8001",
            "enterprise": f"{base_url}:8002",
            "analytics": f"{base_url}:8003",
            "pulse": f"{base_url}:8011",
            "workflow": f"{base_url}:8023",
            "compliance": f"{base_url}:8019",
            "notify": f"{base_url}:8014",
            "supreme_plus": f"{base_url}:8034",
            "citadel": f"{base_url}:8035",
            "observatory": f"{base_url}:8036"
        }
    
    # ==================== TEST UTILITIES ====================
    
    async def make_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, params=params)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data, params=params)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, params=params)
                else:
                    return {"error": f"Unsupported method: {method}"}
                
                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.status_code < 400 else None,
                    "error": None if response.status_code < 400 else response.text
                }
            except Exception as e:
                return {
                    "status_code": 0,
                    "data": None,
                    "error": str(e)
                }
    
    def log_test_result(
        self,
        test_name: str,
        passed: bool,
        duration: float,
        details: str = ""
    ):
        """Log test result"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "duration": duration,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name} ({duration:.2f}s)")
        if details:
            print(f"  Details: {details}")
    
    def assert_response(
        self,
        response: Dict[str, Any],
        expected_status: int = 200,
        check_data: bool = True
    ) -> bool:
        """Assert response is valid"""
        if response["status_code"] != expected_status:
            return False
        if check_data and not response["data"]:
            return False
        if response["error"]:
            return False
        return True
    
    # ==================== HEALTH CHECKS ====================
    
    async def test_all_services_health(self) -> Dict[str, bool]:
        """Test health of all services"""
        print("\n=== Testing Service Health ===")
        results = {}
        
        for service, endpoint in self.endpoints.items():
            start_time = time.time()
            response = await self.make_request("GET", f"{endpoint}/health")
            duration = time.time() - start_time
            
            passed = self.assert_response(response)
            results[service] = passed
            
            self.log_test_result(
                f"Health Check - {service}",
                passed,
                duration,
                f"Status: {response['status_code']}"
            )
        
        return results
    
    # ==================== COMPLIANCE CENTER TESTS ====================
    
    async def test_compliance_center_integration(self):
        """Test Compliance Center integrations"""
        print("\n=== Testing Compliance Center Integration ===")
        
        # Test 1: Create compliance framework
        start_time = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['compliance']}/api/v1/compliance/frameworks",
            data={
                "name": "Test Framework",
                "description": "Integration test framework",
                "framework_type": "SOC2"
            },
            params={"tenant_id": self.tenant_id}
        )
        duration = time.time() - start_time
        
        passed = self.assert_response(response, 200)
        framework_id = response["data"]["id"] if passed else None
        
        self.log_test_result(
            "Compliance - Create Framework",
            passed,
            duration,
            f"Framework ID: {framework_id}"
        )
        
        # Test 2: Create assessment
        if framework_id:
            start_time = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['compliance']}/api/v1/compliance/assessments",
                data={
                    "framework_id": framework_id,
                    "name": "Test Assessment",
                    "description": "Integration test assessment"
                },
                params={"tenant_id": self.tenant_id}
            )
            duration = time.time() - start_time
            
            passed = self.assert_response(response, 200)
            self.log_test_result(
                "Compliance - Create Assessment",
                passed,
                duration
            )
        
        # Test 3: Get compliance score
        start_time = time.time()
        response = await self.make_request(
            "GET",
            f"{self.endpoints['compliance']}/api/v1/compliance/score",
            params={"tenant_id": self.tenant_id}
        )
        duration = time.time() - start_time
        
        passed = self.assert_response(response, 200)
        self.log_test_result(
            "Compliance - Get Score",
            passed,
            duration,
            f"Score: {response['data'].get('overall_score', 'N/A')}"
        )
    
    # ==================== SERVICE CATALOG TESTS ====================
    
    async def test_service_catalog_integration(self):
        """Test Service Catalog integrations"""
        print("\n=== Testing Service Catalog Integration ===")
        
        # Test 1: Create service
        start_time = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['enterprise']}/api/v1/service-catalog/services",
            data={
                "name": "Test Service",
                "description": "Integration test service",
                "category": "infrastructure",
                "approval_required": True
            },
            params={"tenant_id": self.tenant_id}
        )
        duration = time.time() - start_time
        
        passed = self.assert_response(response, 200)
        service_id = response["data"]["id"] if passed else None
        
        self.log_test_result(
            "Service Catalog - Create Service",
            passed,
            duration,
            f"Service ID: {service_id}"
        )
        
        # Test 2: Create request
        if service_id:
            start_time = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['enterprise']}/api/v1/service-catalog/requests",
                data={
                    "service_id": service_id,
                    "requested_by": 1,
                    "request_data": {"quantity": 1}
                },
                params={"tenant_id": self.tenant_id}
            )
            duration = time.time() - start_time
            
            passed = self.assert_response(response, 200)
            request_id = response["data"]["id"] if passed else None
            
            self.log_test_result(
                "Service Catalog - Create Request",
                passed,
                duration,
                f"Request ID: {request_id}"
            )
            
            # Test 3: Approve request
            if request_id:
                start_time = time.time()
                response = await self.make_request(
                    "POST",
                    f"{self.endpoints['enterprise']}/api/v1/service-catalog/requests/{request_id}/approve",
                    data={"approver_id": 1},
                    params={"tenant_id": self.tenant_id}
                )
                duration = time.time() - start_time
                
                passed = self.assert_response(response, 200)
                self.log_test_result(
                    "Service Catalog - Approve Request",
                    passed,
                    duration
                )
    
    # ==================== AUTOMATION ORCHESTRATOR TESTS ====================
    
    async def test_automation_orchestrator_integration(self):
        """Test Automation Orchestrator integrations"""
        print("\n=== Testing Automation Orchestrator Integration ===")
        
        # Test 1: Create workflow
        start_time = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['workflow']}/api/v1/automation/workflows",
            data={
                "name": "Test Workflow",
                "description": "Integration test workflow",
                "trigger_type": "manual"
            },
            params={"tenant_id": self.tenant_id}
        )
        duration = time.time() - start_time
        
        passed = self.assert_response(response, 200)
        workflow_id = response["data"]["id"] if passed else None
        
        self.log_test_result(
            "Automation - Create Workflow",
            passed,
            duration,
            f"Workflow ID: {workflow_id}"
        )
        
        # Test 2: Add nodes
        if workflow_id:
            start_time = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['workflow']}/api/v1/automation/workflows/{workflow_id}/nodes",
                data={
                    "node_type": "action",
                    "action_type": "http_request",
                    "config": {"url": "http://example.com"}
                },
                params={"tenant_id": self.tenant_id}
            )
            duration = time.time() - start_time
            
            passed = self.assert_response(response, 200)
            self.log_test_result(
                "Automation - Add Node",
                passed,
                duration
            )
        
        # Test 3: Execute workflow
        if workflow_id:
            start_time = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['workflow']}/api/v1/automation/workflows/{workflow_id}/execute",
                data={"input_data": {}},
                params={"tenant_id": self.tenant_id}
            )
            duration = time.time() - start_time
            
            passed = self.assert_response(response, 200)
            self.log_test_result(
                "Automation - Execute Workflow",
                passed,
                duration
            )
    
    # ==================== OBSERVATORY TESTS ====================
    
    async def test_observatory_integration(self):
        """Test Observatory integrations"""
        print("\n=== Testing Observatory Integration ===")
        
        # Test 1: Register service
        start_time = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['observatory']}/api/v1/services",
            data={
                "name": "test-service",
                "service_type": "api",
                "environment": "test"
            },
            params={"tenant_id": self.tenant_id}
        )
        duration = time.time() - start_time
        
        passed = self.assert_response(response, 200)
        service_id = response["data"]["id"] if passed else None
        
        self.log_test_result(
            "Observatory - Register Service",
            passed,
            duration,
            f"Service ID: {service_id}"
        )
        
        # Test 2: Ingest metrics
        if service_id:
            start_time = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['observatory']}/api/v1/metrics/ingest",
                data={
                    "service_id": service_id,
                    "metrics": [
                        {
                            "name": "response_time",
                            "value": 150.5,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    ]
                },
                params={"tenant_id": self.tenant_id}
            )
            duration = time.time() - start_time
            
            passed = self.assert_response(response, 200)
            self.log_test_result(
                "Observatory - Ingest Metrics",
                passed,
                duration
            )
        
        # Test 3: Query metrics
        start_time = time.time()
        response = await self.make_request(
            "GET",
            f"{self.endpoints['observatory']}/api/v1/metrics",
            params={
                "tenant_id": self.tenant_id,
                "service_name": "test-service",
                "metric_name": "response_time"
            }
        )
        duration = time.time() - start_time
        
        passed = self.assert_response(response, 200)
        self.log_test_result(
            "Observatory - Query Metrics",
            passed,
            duration
        )
    
    # ==================== AI INSIGHTS TESTS ====================
    
    async def test_ai_insights_integration(self):
        """Test AI Insights integrations"""
        print("\n=== Testing AI Insights Integration ===")
        
        # Test 1: Create AI model
        start_time = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['analytics']}/api/v1/ai/models",
            data={
                "name": "Test Model",
                "model_type": "classification",
                "algorithm": "RandomForest",
                "features": ["feature1", "feature2"],
                "target_variable": "target"
            },
            params={"tenant_id": self.tenant_id}
        )
        duration = time.time() - start_time
        
        passed = self.assert_response(response, 200)
        model_id = response["data"]["id"] if passed else None
        
        self.log_test_result(
            "AI Insights - Create Model",
            passed,
            duration,
            f"Model ID: {model_id}"
        )
        
        # Test 2: Generate insights
        start_time = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['analytics']}/api/v1/ai/insights/generate",
            data={
                "data": [
                    {"metric1": 100, "metric2": 200},
                    {"metric1": 150, "metric2": 250}
                ],
                "metrics": ["metric1", "metric2"],
                "time_range_days": 7
            },
            params={"tenant_id": self.tenant_id}
        )
        duration = time.time() - start_time
        
        passed = self.assert_response(response, 200)
        self.log_test_result(
            "AI Insights - Generate Insights",
            passed,
            duration,
            f"Insights: {response['data'].get('total_insights', 0)}"
        )
        
        # Test 3: Assess data quality
        start_time = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['analytics']}/api/v1/ai/quality/assess",
            data={
                "dataset_name": "test_dataset",
                "data": [
                    {"col1": 1, "col2": "a"},
                    {"col1": 2, "col2": "b"}
                ]
            },
            params={"tenant_id": self.tenant_id}
        )
        duration = time.time() - start_time
        
        passed = self.assert_response(response, 200)
        self.log_test_result(
            "AI Insights - Assess Quality",
            passed,
            duration,
            f"Score: {response['data'].get('overall_score', 'N/A')}"
        )
    
    # ==================== END-TO-END SCENARIOS ====================
    
    async def test_scenario_incident_to_remediation(self):
        """Test: Incident Detection → Auto-Remediation"""
        print("\n=== Testing Scenario: Incident → Remediation ===")
        
        # Step 1: Observatory detects anomaly
        start_time = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['observatory']}/api/v1/metrics/ingest",
            data={
                "service_id": 1,
                "metrics": [
                    {
                        "name": "error_rate",
                        "value": 50.0,  # High error rate
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ]
            },
            params={"tenant_id": self.tenant_id}
        )
        
        passed = self.assert_response(response, 200)
        duration = time.time() - start_time
        
        self.log_test_result(
            "Scenario 1 - Step 1: Detect Anomaly",
            passed,
            duration
        )
        
        # Step 2: Create Pulse incident
        if passed:
            start_time = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['pulse']}/api/v1/incidents",
                data={
                    "title": "High Error Rate Detected",
                    "description": "Error rate exceeded threshold",
                    "severity": "high",
                    "source": "observatory"
                },
                params={"tenant_id": self.tenant_id}
            )
            
            passed = self.assert_response(response, 200)
            duration = time.time() - start_time
            incident_id = response["data"]["id"] if passed else None
            
            self.log_test_result(
                "Scenario 1 - Step 2: Create Incident",
                passed,
                duration,
                f"Incident ID: {incident_id}"
            )
        
        # Step 3: Trigger Supreme Plus remediation
        if passed and incident_id:
            start_time = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['supreme_plus']}/api/v1/remediations/trigger",
                data={
                    "incident_id": incident_id,
                    "remediation_type": "restart_service",
                    "target": "api-gateway"
                },
                params={"tenant_id": self.tenant_id}
            )
            
            passed = self.assert_response(response, 200)
            duration = time.time() - start_time
            
            self.log_test_result(
                "Scenario 1 - Step 3: Trigger Remediation",
                passed,
                duration
            )
    
    async def test_scenario_compliance_workflow(self):
        """Test: Compliance Violation → Workflow → Notification"""
        print("\n=== Testing Scenario: Compliance → Workflow → Notification ===")
        
        # Step 1: Detect compliance violation
        start_time = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['compliance']}/api/v1/compliance/violations",
            data={
                "control_id": 1,
                "description": "Test violation",
                "severity": "high"
            },
            params={"tenant_id": self.tenant_id}
        )
        
        passed = self.assert_response(response, 200)
        duration = time.time() - start_time
        violation_id = response["data"]["id"] if passed else None
        
        self.log_test_result(
            "Scenario 2 - Step 1: Detect Violation",
            passed,
            duration,
            f"Violation ID: {violation_id}"
        )
        
        # Step 2: Trigger remediation workflow
        if passed and violation_id:
            start_time = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['workflow']}/api/v1/automation/workflows/1/execute",
                data={
                    "input_data": {
                        "violation_id": violation_id,
                        "action": "remediate"
                    }
                },
                params={"tenant_id": self.tenant_id}
            )
            
            passed = self.assert_response(response, 200)
            duration = time.time() - start_time
            
            self.log_test_result(
                "Scenario 2 - Step 2: Execute Workflow",
                passed,
                duration
            )
        
        # Step 3: Send notification
        if passed:
            start_time = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['notify']}/api/v1/notifications/send",
                data={
                    "type": "compliance_violation",
                    "priority": "high",
                    "subject": "Compliance Violation Detected",
                    "message": f"Violation {violation_id} requires attention",
                    "recipients": ["admin@tenant.com"]
                },
                params={"tenant_id": self.tenant_id}
            )
            
            passed = self.assert_response(response, 200)
            duration = time.time() - start_time
            
            self.log_test_result(
                "Scenario 2 - Step 3: Send Notification",
                passed,
                duration
            )
    
    # ==================== REPORT GENERATION ====================
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["passed"]])
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r["duration"] for r in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "avg_duration": avg_duration
            },
            "results": self.test_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def print_report(self):
        """Print test report"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("INTEGRATION TEST REPORT")
        print("="*60)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']} ✅")
        print(f"Failed: {report['summary']['failed']} ❌")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Total Duration: {report['summary']['total_duration']:.2f}s")
        print(f"Average Duration: {report['summary']['avg_duration']:.2f}s")
        print("="*60)
        
        if report['summary']['failed'] > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  ❌ {result['test_name']}")
                    if result["details"]:
                        print(f"     {result['details']}")
    
    def save_report(self, filename: str = "integration_test_report.json"):
        """Save test report to file"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {filename}")


# ==================== MAIN TEST RUNNER ====================

async def run_all_tests():
    """Run all integration tests"""
    framework = IntegrationTestFramework()
    
    print("="*60)
    print("iTechSmart Suite - Integration Tests")
    print("="*60)
    
    # Health checks
    await framework.test_all_services_health()
    
    # Component tests
    await framework.test_compliance_center_integration()
    await framework.test_service_catalog_integration()
    await framework.test_automation_orchestrator_integration()
    await framework.test_observatory_integration()
    await framework.test_ai_insights_integration()
    
    # End-to-end scenarios
    await framework.test_scenario_incident_to_remediation()
    await framework.test_scenario_compliance_workflow()
    
    # Generate report
    framework.print_report()
    framework.save_report()


if __name__ == "__main__":
    asyncio.run(run_all_tests())