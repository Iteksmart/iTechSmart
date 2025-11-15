"""
iTechSmart Suite - Performance Testing & Benchmarking
Load testing, stress testing, and performance benchmarks
"""

import asyncio
import httpx
import time
import statistics
from typing import Dict, Any, List
from datetime import datetime
import json


class PerformanceTests:
    """Performance testing and benchmarking"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.tenant_id = 1
        self.timeout = 60.0
        self.results = []
        
        self.endpoints = {
            "compliance": f"{base_url}:8019",
            "enterprise": f"{base_url}:8002",
            "workflow": f"{base_url}:8023",
            "observatory": f"{base_url}:8036",
            "analytics": f"{base_url}:8003"
        }
    
    # ==================== LOAD TESTING ====================
    
    async def load_test_endpoint(
        self,
        name: str,
        url: str,
        method: str = "GET",
        data: Dict = None,
        params: Dict = None,
        concurrent_requests: int = 10,
        total_requests: int = 100
    ) -> Dict[str, Any]:
        """Load test a specific endpoint"""
        print(f"\n=== Load Testing: {name} ===")
        print(f"Concurrent: {concurrent_requests}, Total: {total_requests}")
        
        response_times = []
        errors = 0
        
        async def make_request():
            nonlocal errors
            start = time.time()
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, params=params)
                    elif method.upper() == "POST":
                        response = await client.post(url, json=data, params=params)
                    else:
                        return None
                    
                    duration = time.time() - start
                    if response.status_code < 400:
                        response_times.append(duration)
                    else:
                        errors += 1
                    return duration
            except Exception as e:
                errors += 1
                return None
        
        # Run load test
        start_time = time.time()
        
        for batch in range(0, total_requests, concurrent_requests):
            batch_size = min(concurrent_requests, total_requests - batch)
            tasks = [make_request() for _ in range(batch_size)]
            await asyncio.gather(*tasks)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            result = {
                "name": name,
                "total_requests": total_requests,
                "successful_requests": len(response_times),
                "failed_requests": errors,
                "success_rate": (len(response_times) / total_requests) * 100,
                "total_duration": total_duration,
                "requests_per_second": total_requests / total_duration,
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "median_response_time": statistics.median(response_times),
                "p95_response_time": self._percentile(response_times, 95),
                "p99_response_time": self._percentile(response_times, 99)
            }
        else:
            result = {
                "name": name,
                "total_requests": total_requests,
                "successful_requests": 0,
                "failed_requests": errors,
                "success_rate": 0,
                "error": "All requests failed"
            }
        
        self.results.append(result)
        self._print_load_test_result(result)
        return result
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _print_load_test_result(self, result: Dict):
        """Print load test result"""
        print(f"  Total Requests: {result['total_requests']}")
        print(f"  Successful: {result['successful_requests']} ({result['success_rate']:.1f}%)")
        print(f"  Failed: {result['failed_requests']}")
        
        if 'avg_response_time' in result:
            print(f"  Requests/sec: {result['requests_per_second']:.2f}")
            print(f"  Avg Response: {result['avg_response_time']*1000:.2f}ms")
            print(f"  Min Response: {result['min_response_time']*1000:.2f}ms")
            print(f"  Max Response: {result['max_response_time']*1000:.2f}ms")
            print(f"  P95 Response: {result['p95_response_time']*1000:.2f}ms")
            print(f"  P99 Response: {result['p99_response_time']*1000:.2f}ms")
    
    # ==================== COMPLIANCE CENTER PERFORMANCE ====================
    
    async def test_compliance_performance(self):
        """Test Compliance Center performance"""
        print("\n" + "="*60)
        print("COMPLIANCE CENTER PERFORMANCE TESTS")
        print("="*60)
        
        # Test 1: List frameworks
        await self.load_test_endpoint(
            "Compliance - List Frameworks",
            f"{self.endpoints['compliance']}/api/v1/compliance/frameworks",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=20,
            total_requests=200
        )
        
        # Test 2: Get compliance score
        await self.load_test_endpoint(
            "Compliance - Get Score",
            f"{self.endpoints['compliance']}/api/v1/compliance/score",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=15,
            total_requests=150
        )
        
        # Test 3: List assessments
        await self.load_test_endpoint(
            "Compliance - List Assessments",
            f"{self.endpoints['compliance']}/api/v1/compliance/assessments",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=10,
            total_requests=100
        )
    
    # ==================== SERVICE CATALOG PERFORMANCE ====================
    
    async def test_service_catalog_performance(self):
        """Test Service Catalog performance"""
        print("\n" + "="*60)
        print("SERVICE CATALOG PERFORMANCE TESTS")
        print("="*60)
        
        # Test 1: List services
        await self.load_test_endpoint(
            "Service Catalog - List Services",
            f"{self.endpoints['enterprise']}/api/v1/service-catalog/services",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=20,
            total_requests=200
        )
        
        # Test 2: List requests
        await self.load_test_endpoint(
            "Service Catalog - List Requests",
            f"{self.endpoints['enterprise']}/api/v1/service-catalog/requests",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=15,
            total_requests=150
        )
    
    # ==================== AUTOMATION ORCHESTRATOR PERFORMANCE ====================
    
    async def test_automation_performance(self):
        """Test Automation Orchestrator performance"""
        print("\n" + "="*60)
        print("AUTOMATION ORCHESTRATOR PERFORMANCE TESTS")
        print("="*60)
        
        # Test 1: List workflows
        await self.load_test_endpoint(
            "Automation - List Workflows",
            f"{self.endpoints['workflow']}/api/v1/automation/workflows",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=20,
            total_requests=200
        )
        
        # Test 2: List executions
        await self.load_test_endpoint(
            "Automation - List Executions",
            f"{self.endpoints['workflow']}/api/v1/automation/executions",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=15,
            total_requests=150
        )
    
    # ==================== OBSERVATORY PERFORMANCE ====================
    
    async def test_observatory_performance(self):
        """Test Observatory performance"""
        print("\n" + "="*60)
        print("OBSERVATORY PERFORMANCE TESTS")
        print("="*60)
        
        # Test 1: List services
        await self.load_test_endpoint(
            "Observatory - List Services",
            f"{self.endpoints['observatory']}/api/v1/services",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=25,
            total_requests=250
        )
        
        # Test 2: Query metrics
        await self.load_test_endpoint(
            "Observatory - Query Metrics",
            f"{self.endpoints['observatory']}/api/v1/metrics",
            method="GET",
            params={
                "tenant_id": self.tenant_id,
                "service_name": "test-service"
            },
            concurrent_requests=20,
            total_requests=200
        )
        
        # Test 3: Ingest metrics (write performance)
        await self.load_test_endpoint(
            "Observatory - Ingest Metrics",
            f"{self.endpoints['observatory']}/api/v1/metrics/ingest",
            method="POST",
            data={
                "service_id": 1,
                "metrics": [{
                    "name": "test_metric",
                    "value": 100.0,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            },
            params={"tenant_id": self.tenant_id},
            concurrent_requests=15,
            total_requests=150
        )
    
    # ==================== AI INSIGHTS PERFORMANCE ====================
    
    async def test_ai_insights_performance(self):
        """Test AI Insights performance"""
        print("\n" + "="*60)
        print("AI INSIGHTS PERFORMANCE TESTS")
        print("="*60)
        
        # Test 1: List models
        await self.load_test_endpoint(
            "AI Insights - List Models",
            f"{self.endpoints['analytics']}/api/v1/ai/models",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=20,
            total_requests=200
        )
        
        # Test 2: List predictions
        await self.load_test_endpoint(
            "AI Insights - List Predictions",
            f"{self.endpoints['analytics']}/api/v1/ai/predictions",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=15,
            total_requests=150
        )
        
        # Test 3: List insights
        await self.load_test_endpoint(
            "AI Insights - List Insights",
            f"{self.endpoints['analytics']}/api/v1/ai/insights",
            method="GET",
            params={"tenant_id": self.tenant_id},
            concurrent_requests=15,
            total_requests=150
        )
    
    # ==================== STRESS TESTING ====================
    
    async def stress_test_endpoint(
        self,
        name: str,
        url: str,
        method: str = "GET",
        data: Dict = None,
        params: Dict = None,
        duration_seconds: int = 60,
        concurrent_requests: int = 50
    ) -> Dict[str, Any]:
        """Stress test an endpoint for a duration"""
        print(f"\n=== Stress Testing: {name} ===")
        print(f"Duration: {duration_seconds}s, Concurrent: {concurrent_requests}")
        
        response_times = []
        errors = 0
        total_requests = 0
        
        async def make_request():
            nonlocal errors, total_requests
            total_requests += 1
            start = time.time()
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, params=params)
                    elif method.upper() == "POST":
                        response = await client.post(url, json=data, params=params)
                    else:
                        return None
                    
                    duration = time.time() - start
                    if response.status_code < 400:
                        response_times.append(duration)
                    else:
                        errors += 1
            except Exception as e:
                errors += 1
        
        # Run stress test
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            tasks = [make_request() for _ in range(concurrent_requests)]
            await asyncio.gather(*tasks)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            result = {
                "name": name,
                "test_type": "stress",
                "duration": total_duration,
                "total_requests": total_requests,
                "successful_requests": len(response_times),
                "failed_requests": errors,
                "success_rate": (len(response_times) / total_requests) * 100,
                "requests_per_second": total_requests / total_duration,
                "avg_response_time": statistics.mean(response_times),
                "p95_response_time": self._percentile(response_times, 95),
                "p99_response_time": self._percentile(response_times, 99)
            }
        else:
            result = {
                "name": name,
                "test_type": "stress",
                "error": "All requests failed"
            }
        
        self._print_stress_test_result(result)
        return result
    
    def _print_stress_test_result(self, result: Dict):
        """Print stress test result"""
        if 'error' in result:
            print(f"  ❌ {result['error']}")
            return
        
        print(f"  Duration: {result['duration']:.2f}s")
        print(f"  Total Requests: {result['total_requests']}")
        print(f"  Success Rate: {result['success_rate']:.1f}%")
        print(f"  Requests/sec: {result['requests_per_second']:.2f}")
        print(f"  Avg Response: {result['avg_response_time']*1000:.2f}ms")
        print(f"  P95 Response: {result['p95_response_time']*1000:.2f}ms")
        print(f"  P99 Response: {result['p99_response_time']*1000:.2f}ms")
    
    # ==================== BENCHMARKS ====================
    
    def generate_benchmark_report(self) -> Dict[str, Any]:
        """Generate performance benchmark report"""
        benchmarks = {
            "compliance_center": [],
            "service_catalog": [],
            "automation_orchestrator": [],
            "observatory": [],
            "ai_insights": []
        }
        
        for result in self.results:
            name = result["name"].lower()
            if "compliance" in name:
                benchmarks["compliance_center"].append(result)
            elif "service catalog" in name:
                benchmarks["service_catalog"].append(result)
            elif "automation" in name:
                benchmarks["automation_orchestrator"].append(result)
            elif "observatory" in name:
                benchmarks["observatory"].append(result)
            elif "ai insights" in name:
                benchmarks["ai_insights"].append(result)
        
        return {
            "benchmarks": benchmarks,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def print_benchmark_report(self):
        """Print benchmark report"""
        report = self.generate_benchmark_report()
        
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK REPORT")
        print("="*60)
        
        for product, results in report["benchmarks"].items():
            if not results:
                continue
            
            print(f"\n{product.replace('_', ' ').title()}:")
            for result in results:
                if 'avg_response_time' in result:
                    print(f"  {result['name']}:")
                    print(f"    Requests/sec: {result['requests_per_second']:.2f}")
                    print(f"    Avg Response: {result['avg_response_time']*1000:.2f}ms")
                    print(f"    P95 Response: {result['p95_response_time']*1000:.2f}ms")
                    print(f"    Success Rate: {result['success_rate']:.1f}%")
        
        print("="*60)
    
    def save_benchmark_report(self, filename: str = "performance_benchmarks.json"):
        """Save benchmark report to file"""
        report = self.generate_benchmark_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nBenchmark report saved to: {filename}")


async def run_performance_tests():
    """Run all performance tests"""
    tests = PerformanceTests()
    
    print("="*60)
    print("iTechSmart Suite - Performance Tests")
    print("="*60)
    
    # Load tests
    await tests.test_compliance_performance()
    await tests.test_service_catalog_performance()
    await tests.test_automation_performance()
    await tests.test_observatory_performance()
    await tests.test_ai_insights_performance()
    
    # Generate report
    tests.print_benchmark_report()
    tests.save_benchmark_report()


if __name__ == "__main__":
    asyncio.run(run_performance_tests())