"""
iTechSmart Suite - End-to-End Scenario Tests
Comprehensive workflow testing across multiple products
"""

import asyncio
import httpx
from typing import Dict, Any
from datetime import datetime
import time


class ScenarioTests:
    """End-to-end scenario testing"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.tenant_id = 1
        self.timeout = 30.0
        self.test_results = []
        
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
    
    async def make_request(self, method: str, url: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, params=params)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data, params=params)
                else:
                    return {"status_code": 0, "data": None, "error": "Unsupported method"}
                
                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.status_code < 400 else None,
                    "error": None if response.status_code < 400 else response.text
                }
            except Exception as e:
                return {"status_code": 0, "data": None, "error": str(e)}
    
    def log_step(self, scenario: str, step: str, passed: bool, duration: float, details: str = ""):
        """Log scenario step"""
        result = {
            "scenario": scenario,
            "step": step,
            "passed": passed,
            "duration": duration,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if passed else "❌"
        print(f"  {status} {step} ({duration:.2f}s)")
        if details:
            print(f"     {details}")
    
    # ==================== SCENARIO 1: INCIDENT DETECTION → AUTO-REMEDIATION ====================
    
    async def scenario_1_incident_to_remediation(self):
        """
        Scenario 1: Incident Detection → Auto-Remediation
        
        Flow:
        1. Observatory detects high error rate
        2. AI Insights generates anomaly insight
        3. Pulse creates incident
        4. Supreme Plus triggers auto-remediation
        5. Notify sends alert
        6. Workflow tracks resolution
        """
        print("\n" + "="*60)
        print("SCENARIO 1: Incident Detection → Auto-Remediation")
        print("="*60)
        
        scenario = "Incident to Remediation"
        
        # Step 1: Observatory detects anomaly
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['observatory']}/api/v1/metrics/ingest",
            data={
                "service_id": 1,
                "metrics": [{
                    "name": "error_rate",
                    "value": 45.0,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Observatory: Ingest High Error Rate", passed, time.time() - start)
        
        if not passed:
            return False
        
        # Step 2: AI Insights detects anomaly
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['analytics']}/api/v1/ai/insights/generate",
            data={
                "data": [{"error_rate": 45.0, "timestamp": datetime.utcnow().isoformat()}],
                "metrics": ["error_rate"],
                "time_range_days": 1
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        insight_count = response["data"].get("total_insights", 0) if passed else 0
        self.log_step(
            scenario,
            "AI Insights: Detect Anomaly",
            passed,
            time.time() - start,
            f"Generated {insight_count} insights"
        )
        
        # Step 3: Create Pulse incident
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['pulse']}/api/v1/incidents",
            data={
                "title": "Critical: High Error Rate Detected",
                "description": "Error rate exceeded 40% threshold",
                "severity": "critical",
                "source": "observatory",
                "affected_service": "api-gateway"
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        incident_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Pulse: Create Incident",
            passed,
            time.time() - start,
            f"Incident ID: {incident_id}"
        )
        
        if not passed or not incident_id:
            return False
        
        # Step 4: Supreme Plus triggers remediation
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['supreme_plus']}/api/v1/remediations/trigger",
            data={
                "incident_id": incident_id,
                "remediation_type": "restart_service",
                "target": "api-gateway",
                "reason": "high_error_rate"
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        remediation_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Supreme Plus: Trigger Remediation",
            passed,
            time.time() - start,
            f"Remediation ID: {remediation_id}"
        )
        
        # Step 5: Send notification
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['notify']}/api/v1/notifications/send",
            data={
                "type": "incident_alert",
                "priority": "critical",
                "subject": "Critical Incident: High Error Rate",
                "message": f"Incident {incident_id} - Auto-remediation triggered",
                "recipients": ["oncall@company.com"]
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Notify: Send Alert", passed, time.time() - start)
        
        # Step 6: Track in workflow
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['workflow']}/api/v1/automation/workflows/1/execute",
            data={
                "input_data": {
                    "incident_id": incident_id,
                    "remediation_id": remediation_id,
                    "action": "track_resolution"
                }
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Workflow: Track Resolution", passed, time.time() - start)
        
        return True
    
    # ==================== SCENARIO 2: COMPLIANCE VIOLATION → WORKFLOW → NOTIFICATION ====================
    
    async def scenario_2_compliance_workflow(self):
        """
        Scenario 2: Compliance Violation → Workflow → Notification
        
        Flow:
        1. Compliance Center detects violation
        2. Create remediation plan
        3. Trigger automated workflow
        4. Assign tasks
        5. Send notifications
        6. Track completion
        """
        print("\n" + "="*60)
        print("SCENARIO 2: Compliance Violation → Workflow → Notification")
        print("="*60)
        
        scenario = "Compliance Workflow"
        
        # Step 1: Detect compliance violation
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['compliance']}/api/v1/compliance/violations",
            data={
                "control_id": 1,
                "description": "Unencrypted data transmission detected",
                "severity": "high",
                "evidence": "Network traffic analysis"
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        violation_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Compliance: Detect Violation",
            passed,
            time.time() - start,
            f"Violation ID: {violation_id}"
        )
        
        if not passed or not violation_id:
            return False
        
        # Step 2: Create remediation plan
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['compliance']}/api/v1/compliance/remediation-plans",
            data={
                "violation_id": violation_id,
                "title": "Enable TLS Encryption",
                "description": "Implement TLS 1.3 for all data transmission",
                "priority": "high"
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        plan_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Compliance: Create Remediation Plan",
            passed,
            time.time() - start,
            f"Plan ID: {plan_id}"
        )
        
        # Step 3: Trigger automated workflow
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['workflow']}/api/v1/automation/workflows",
            data={
                "name": "Compliance Remediation Workflow",
                "description": f"Remediate violation {violation_id}",
                "trigger_type": "event"
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        workflow_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Workflow: Create Remediation Workflow",
            passed,
            time.time() - start,
            f"Workflow ID: {workflow_id}"
        )
        
        # Step 4: Assign tasks (via Service Catalog)
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['enterprise']}/api/v1/service-catalog/requests",
            data={
                "service_id": 1,
                "requested_by": 1,
                "request_data": {
                    "task": "enable_tls",
                    "violation_id": violation_id
                }
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        request_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Service Catalog: Create Task Request",
            passed,
            time.time() - start,
            f"Request ID: {request_id}"
        )
        
        # Step 5: Send notifications
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['notify']}/api/v1/notifications/send",
            data={
                "type": "compliance_violation",
                "priority": "high",
                "subject": "Compliance Violation Requires Action",
                "message": f"Violation {violation_id}: Unencrypted data transmission",
                "recipients": ["compliance@company.com", "security@company.com"]
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Notify: Send Compliance Alert", passed, time.time() - start)
        
        # Step 6: Track completion
        start = time.time()
        response = await self.make_request(
            "GET",
            f"{self.endpoints['compliance']}/api/v1/compliance/violations/{violation_id}",
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        status = response["data"].get("status", "unknown") if passed else "unknown"
        self.log_step(
            scenario,
            "Compliance: Track Status",
            passed,
            time.time() - start,
            f"Status: {status}"
        )
        
        return True
    
    # ==================== SCENARIO 3: AI ANOMALY → PULSE INCIDENT → SUPREME PLUS FIX ====================
    
    async def scenario_3_ai_anomaly_remediation(self):
        """
        Scenario 3: AI Anomaly → Pulse Incident → Supreme Plus Fix
        
        Flow:
        1. AI Insights detects performance anomaly
        2. Generate recommendation
        3. Create Pulse incident
        4. Supreme Plus executes fix
        5. Verify resolution
        6. Update incident status
        """
        print("\n" + "="*60)
        print("SCENARIO 3: AI Anomaly → Pulse Incident → Supreme Plus Fix")
        print("="*60)
        
        scenario = "AI-Driven Remediation"
        
        # Step 1: AI detects anomaly
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['analytics']}/api/v1/ai/insights/generate",
            data={
                "data": [
                    {"cpu_usage": 95.0, "memory_usage": 88.0},
                    {"cpu_usage": 92.0, "memory_usage": 85.0},
                    {"cpu_usage": 98.0, "memory_usage": 90.0}
                ],
                "metrics": ["cpu_usage", "memory_usage"],
                "time_range_days": 1
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        insights = response["data"].get("insights", []) if passed else []
        self.log_step(
            scenario,
            "AI Insights: Detect Anomaly",
            passed,
            time.time() - start,
            f"Found {len(insights)} insights"
        )
        
        if not passed or not insights:
            return False
        
        insight_id = insights[0]["id"] if insights else None
        
        # Step 2: Generate recommendation
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['analytics']}/api/v1/ai/insights/{insight_id}/recommendations",
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        recommendations = response["data"].get("recommendations", []) if passed else []
        self.log_step(
            scenario,
            "AI Insights: Generate Recommendation",
            passed,
            time.time() - start,
            f"Generated {len(recommendations)} recommendations"
        )
        
        # Step 3: Create Pulse incident
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['pulse']}/api/v1/incidents",
            data={
                "title": "High Resource Usage Detected",
                "description": "CPU and memory usage exceeding thresholds",
                "severity": "high",
                "source": "ai_insights",
                "metadata": {"insight_id": insight_id}
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        incident_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Pulse: Create Incident",
            passed,
            time.time() - start,
            f"Incident ID: {incident_id}"
        )
        
        # Step 4: Supreme Plus executes fix
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['supreme_plus']}/api/v1/remediations/trigger",
            data={
                "incident_id": incident_id,
                "remediation_type": "scale_resources",
                "target": "app-server",
                "parameters": {"cpu_limit": "4", "memory_limit": "8Gi"}
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        remediation_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Supreme Plus: Execute Fix",
            passed,
            time.time() - start,
            f"Remediation ID: {remediation_id}"
        )
        
        # Step 5: Verify resolution (Observatory)
        start = time.time()
        response = await self.make_request(
            "GET",
            f"{self.endpoints['observatory']}/api/v1/metrics",
            params={
                "tenant_id": self.tenant_id,
                "service_name": "app-server",
                "metric_name": "cpu_usage"
            }
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Observatory: Verify Resolution", passed, time.time() - start)
        
        # Step 6: Update incident status
        start = time.time()
        response = await self.make_request(
            "PUT",
            f"{self.endpoints['pulse']}/api/v1/incidents/{incident_id}",
            data={"status": "resolved"},
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Pulse: Update Incident Status", passed, time.time() - start)
        
        return True
    
    # ==================== SCENARIO 4: SERVICE REQUEST → APPROVAL → FULFILLMENT ====================
    
    async def scenario_4_service_request_fulfillment(self):
        """
        Scenario 4: Service Request → Approval → Fulfillment
        
        Flow:
        1. User submits service request
        2. Workflow triggers approval process
        3. Manager approves request
        4. Automation Orchestrator fulfills request
        5. Notify user of completion
        6. Track in Service Catalog
        """
        print("\n" + "="*60)
        print("SCENARIO 4: Service Request → Approval → Fulfillment")
        print("="*60)
        
        scenario = "Service Request Fulfillment"
        
        # Step 1: Submit service request
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['enterprise']}/api/v1/service-catalog/requests",
            data={
                "service_id": 1,
                "requested_by": 1,
                "request_data": {
                    "type": "vm_provisioning",
                    "specs": {"cpu": 4, "memory": "16GB", "storage": "100GB"}
                }
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        request_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Service Catalog: Submit Request",
            passed,
            time.time() - start,
            f"Request ID: {request_id}"
        )
        
        if not passed or not request_id:
            return False
        
        # Step 2: Trigger approval workflow
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['workflow']}/api/v1/automation/workflows",
            data={
                "name": "Service Request Approval",
                "description": f"Approval for request {request_id}",
                "trigger_type": "event"
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        workflow_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Workflow: Trigger Approval",
            passed,
            time.time() - start,
            f"Workflow ID: {workflow_id}"
        )
        
        # Step 3: Approve request
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['enterprise']}/api/v1/service-catalog/requests/{request_id}/approve",
            data={"approver_id": 2, "comments": "Approved for production use"},
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Service Catalog: Approve Request", passed, time.time() - start)
        
        # Step 4: Fulfill request (Automation Orchestrator)
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['workflow']}/api/v1/automation/workflows/{workflow_id}/execute",
            data={
                "input_data": {
                    "request_id": request_id,
                    "action": "provision_vm"
                }
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        execution_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Automation: Fulfill Request",
            passed,
            time.time() - start,
            f"Execution ID: {execution_id}"
        )
        
        # Step 5: Notify user
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['notify']}/api/v1/notifications/send",
            data={
                "type": "service_request",
                "priority": "normal",
                "subject": "Service Request Completed",
                "message": f"Your request {request_id} has been fulfilled",
                "recipients": ["user@company.com"]
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Notify: Send Completion Notice", passed, time.time() - start)
        
        # Step 6: Track completion
        start = time.time()
        response = await self.make_request(
            "GET",
            f"{self.endpoints['enterprise']}/api/v1/service-catalog/requests/{request_id}",
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        status = response["data"].get("status", "unknown") if passed else "unknown"
        self.log_step(
            scenario,
            "Service Catalog: Verify Completion",
            passed,
            time.time() - start,
            f"Status: {status}"
        )
        
        return True
    
    # ==================== SCENARIO 5: PERFORMANCE ISSUE → OBSERVATORY → AI INSIGHTS → RECOMMENDATION ====================
    
    async def scenario_5_performance_optimization(self):
        """
        Scenario 5: Performance Issue → Observatory → AI Insights → Recommendation
        
        Flow:
        1. Observatory detects performance degradation
        2. Collect metrics over time
        3. AI Insights analyzes trends
        4. Generate optimization recommendations
        5. Create action items
        6. Track implementation
        """
        print("\n" + "="*60)
        print("SCENARIO 5: Performance Issue → Observatory → AI → Recommendation")
        print("="*60)
        
        scenario = "Performance Optimization"
        
        # Step 1: Detect performance degradation
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['observatory']}/api/v1/metrics/ingest",
            data={
                "service_id": 1,
                "metrics": [
                    {"name": "response_time", "value": 850.0, "timestamp": datetime.utcnow().isoformat()},
                    {"name": "throughput", "value": 120.0, "timestamp": datetime.utcnow().isoformat()}
                ]
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Observatory: Detect Degradation", passed, time.time() - start)
        
        # Step 2: Collect metrics
        start = time.time()
        response = await self.make_request(
            "GET",
            f"{self.endpoints['observatory']}/api/v1/metrics",
            params={
                "tenant_id": self.tenant_id,
                "service_name": "api-gateway",
                "metric_name": "response_time"
            }
        )
        passed = response["status_code"] == 200
        metrics_count = len(response["data"]) if passed and response["data"] else 0
        self.log_step(
            scenario,
            "Observatory: Collect Metrics",
            passed,
            time.time() - start,
            f"Collected {metrics_count} data points"
        )
        
        # Step 3: AI analyzes trends
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['analytics']}/api/v1/ai/insights/generate",
            data={
                "data": [
                    {"response_time": 850.0, "throughput": 120.0},
                    {"response_time": 920.0, "throughput": 110.0},
                    {"response_time": 980.0, "throughput": 105.0}
                ],
                "metrics": ["response_time", "throughput"],
                "time_range_days": 7
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        insights = response["data"].get("insights", []) if passed else []
        self.log_step(
            scenario,
            "AI Insights: Analyze Trends",
            passed,
            time.time() - start,
            f"Generated {len(insights)} insights"
        )
        
        # Step 4: Generate recommendations
        if insights:
            insight_id = insights[0]["id"]
            start = time.time()
            response = await self.make_request(
                "POST",
                f"{self.endpoints['analytics']}/api/v1/ai/insights/{insight_id}/recommendations",
                params={"tenant_id": self.tenant_id}
            )
            passed = response["status_code"] == 200
            recommendations = response["data"].get("recommendations", []) if passed else []
            self.log_step(
                scenario,
                "AI Insights: Generate Recommendations",
                passed,
                time.time() - start,
                f"Generated {len(recommendations)} recommendations"
            )
        
        # Step 5: Create action items
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['enterprise']}/api/v1/service-catalog/requests",
            data={
                "service_id": 1,
                "requested_by": 1,
                "request_data": {
                    "task": "optimize_performance",
                    "target": "api-gateway"
                }
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        request_id = response["data"]["id"] if passed else None
        self.log_step(
            scenario,
            "Service Catalog: Create Action Item",
            passed,
            time.time() - start,
            f"Request ID: {request_id}"
        )
        
        # Step 6: Track implementation
        start = time.time()
        response = await self.make_request(
            "POST",
            f"{self.endpoints['workflow']}/api/v1/automation/workflows",
            data={
                "name": "Performance Optimization Tracking",
                "description": "Track optimization implementation",
                "trigger_type": "manual"
            },
            params={"tenant_id": self.tenant_id}
        )
        passed = response["status_code"] == 200
        self.log_step(scenario, "Workflow: Track Implementation", passed, time.time() - start)
        
        return True
    
    # ==================== REPORT GENERATION ====================
    
    def generate_report(self):
        """Generate scenario test report"""
        scenarios = {}
        for result in self.test_results:
            scenario = result["scenario"]
            if scenario not in scenarios:
                scenarios[scenario] = {
                    "steps": [],
                    "total_duration": 0,
                    "passed_steps": 0,
                    "failed_steps": 0
                }
            
            scenarios[scenario]["steps"].append(result)
            scenarios[scenario]["total_duration"] += result["duration"]
            if result["passed"]:
                scenarios[scenario]["passed_steps"] += 1
            else:
                scenarios[scenario]["failed_steps"] += 1
        
        return {
            "scenarios": scenarios,
            "total_scenarios": len(scenarios),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def print_report(self):
        """Print scenario test report"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("END-TO-END SCENARIO TEST REPORT")
        print("="*60)
        
        for scenario_name, scenario_data in report["scenarios"].items():
            total_steps = len(scenario_data["steps"])
            passed = scenario_data["passed_steps"]
            failed = scenario_data["failed_steps"]
            success_rate = (passed / total_steps * 100) if total_steps > 0 else 0
            
            print(f"\n{scenario_name}:")
            print(f"  Total Steps: {total_steps}")
            print(f"  Passed: {passed} ✅")
            print(f"  Failed: {failed} ❌")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Duration: {scenario_data['total_duration']:.2f}s")
            
            if failed > 0:
                print(f"  Failed Steps:")
                for step in scenario_data["steps"]:
                    if not step["passed"]:
                        print(f"    ❌ {step['step']}")
        
        print("="*60)


async def run_scenario_tests():
    """Run all scenario tests"""
    tests = ScenarioTests()
    
    print("="*60)
    print("iTechSmart Suite - End-to-End Scenario Tests")
    print("="*60)
    
    await tests.scenario_1_incident_to_remediation()
    await tests.scenario_2_compliance_workflow()
    await tests.scenario_3_ai_anomaly_remediation()
    await tests.scenario_4_service_request_fulfillment()
    await tests.scenario_5_performance_optimization()
    
    tests.print_report()


if __name__ == "__main__":
    asyncio.run(run_scenario_tests())