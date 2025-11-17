#!/usr/bin/env python3
"""
Load Testing Script for iTechSmart HL7
Tests API performance under various load conditions
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime
import json


class LoadTester:
    """Load testing for iTechSmart HL7 API"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.results = []

    async def make_request(
        self,
        session: aiohttp.ClientSession,
        method: str,
        endpoint: str,
        data: Dict = None,
    ) -> Dict[str, Any]:
        """Make a single API request and measure performance"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        start_time = time.time()

        try:
            if method == "GET":
                async with session.get(url, headers=headers) as response:
                    status = response.status
                    await response.text()
            elif method == "POST":
                async with session.post(url, headers=headers, json=data) as response:
                    status = response.status
                    await response.text()

            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                "success": True,
                "status": status,
                "duration_ms": duration,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            end_time = time.time()
            duration = (end_time - start_time) * 1000

            return {
                "success": False,
                "error": str(e),
                "duration_ms": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def run_concurrent_requests(
        self, num_requests: int, method: str, endpoint: str, data: Dict = None
    ) -> List[Dict[str, Any]]:
        """Run multiple concurrent requests"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.make_request(session, method, endpoint, data)
                for _ in range(num_requests)
            ]
            results = await asyncio.gather(*tasks)
            return results

    def analyze_results(self, results: List[Dict[str, Any]], test_name: str):
        """Analyze and display test results"""
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        if not successful:
            print(f"\n❌ {test_name}: All requests failed!")
            return

        durations = [r["duration_ms"] for r in successful]

        print(f"\n📊 {test_name}")
        print("=" * 60)
        print(f"Total Requests:     {len(results)}")
        print(
            f"Successful:         {len(successful)} ({len(successful)/len(results)*100:.1f}%)"
        )
        print(
            f"Failed:             {len(failed)} ({len(failed)/len(results)*100:.1f}%)"
        )
        print(f"\nResponse Times (ms):")
        print(f"  Min:              {min(durations):.2f}")
        print(f"  Max:              {max(durations):.2f}")
        print(f"  Mean:             {statistics.mean(durations):.2f}")
        print(f"  Median:           {statistics.median(durations):.2f}")
        print(f"  95th Percentile:  {statistics.quantiles(durations, n=20)[18]:.2f}")
        print(f"  99th Percentile:  {statistics.quantiles(durations, n=100)[98]:.2f}")

        # Calculate requests per second
        total_time = max([r["duration_ms"] for r in results]) / 1000
        rps = len(successful) / total_time if total_time > 0 else 0
        print(f"\nThroughput:         {rps:.2f} requests/second")

        # Status code distribution
        status_codes = {}
        for r in successful:
            status = r.get("status", "unknown")
            status_codes[status] = status_codes.get(status, 0) + 1

        print(f"\nStatus Codes:")
        for status, count in sorted(status_codes.items()):
            print(f"  {status}: {count}")

        # Performance rating
        avg_duration = statistics.mean(durations)
        if avg_duration < 100:
            rating = "🟢 Excellent"
        elif avg_duration < 500:
            rating = "🟡 Good"
        elif avg_duration < 1000:
            rating = "🟠 Fair"
        else:
            rating = "🔴 Poor"

        print(f"\nPerformance Rating: {rating}")

        return {
            "test_name": test_name,
            "total_requests": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "mean_ms": statistics.mean(durations),
            "median_ms": statistics.median(durations),
            "p95_ms": statistics.quantiles(durations, n=20)[18],
            "p99_ms": statistics.quantiles(durations, n=100)[98],
            "rps": rps,
        }


async def main():
    """Run load tests"""
    print("🚀 iTechSmart HL7 Load Testing")
    print("=" * 60)

    # Configuration
    BASE_URL = "http://localhost:8000"
    TOKEN = "your-jwt-token-here"  # Replace with actual token

    # You can get a token by logging in first
    print("\n⚠️  Note: Update TOKEN variable with a valid JWT token")
    print("   You can get one by calling POST /api/auth/login")

    tester = LoadTester(BASE_URL, TOKEN)
    all_results = []

    # Test 1: Health Check - Light Load
    print("\n" + "=" * 60)
    print("TEST 1: Health Check - Light Load (10 concurrent requests)")
    print("=" * 60)
    results = await tester.run_concurrent_requests(
        num_requests=10, method="GET", endpoint="/health"
    )
    test_result = tester.analyze_results(results, "Health Check - Light Load")
    all_results.append(test_result)

    # Test 2: Health Check - Medium Load
    print("\n" + "=" * 60)
    print("TEST 2: Health Check - Medium Load (50 concurrent requests)")
    print("=" * 60)
    results = await tester.run_concurrent_requests(
        num_requests=50, method="GET", endpoint="/health"
    )
    test_result = tester.analyze_results(results, "Health Check - Medium Load")
    all_results.append(test_result)

    # Test 3: Health Check - Heavy Load
    print("\n" + "=" * 60)
    print("TEST 3: Health Check - Heavy Load (100 concurrent requests)")
    print("=" * 60)
    results = await tester.run_concurrent_requests(
        num_requests=100, method="GET", endpoint="/health"
    )
    test_result = tester.analyze_results(results, "Health Check - Heavy Load")
    all_results.append(test_result)

    # Test 4: Patient List - Medium Load
    print("\n" + "=" * 60)
    print("TEST 4: Patient List - Medium Load (50 concurrent requests)")
    print("=" * 60)
    results = await tester.run_concurrent_requests(
        num_requests=50, method="GET", endpoint="/api/patients"
    )
    test_result = tester.analyze_results(results, "Patient List - Medium Load")
    all_results.append(test_result)

    # Test 5: Drug Interaction Check - Medium Load
    print("\n" + "=" * 60)
    print("TEST 5: Drug Interaction Check - Medium Load (30 concurrent requests)")
    print("=" * 60)
    drug_check_data = {
        "new_medication": "warfarin",
        "current_medications": ["aspirin", "lisinopril"],
        "allergies": ["penicillin"],
        "is_pregnant": False,
        "creatinine_clearance": 60.0,
    }
    results = await tester.run_concurrent_requests(
        num_requests=30,
        method="POST",
        endpoint="/api/clinicals/drug-check",
        data=drug_check_data,
    )
    test_result = tester.analyze_results(results, "Drug Check - Medium Load")
    all_results.append(test_result)

    # Test 6: Workflow Templates - Light Load
    print("\n" + "=" * 60)
    print("TEST 6: Workflow Templates - Light Load (20 concurrent requests)")
    print("=" * 60)
    results = await tester.run_concurrent_requests(
        num_requests=20, method="GET", endpoint="/api/clinicals/workflows/templates"
    )
    test_result = tester.analyze_results(results, "Workflow Templates - Light Load")
    all_results.append(test_result)

    # Test 7: Clinical Guidelines - Medium Load
    print("\n" + "=" * 60)
    print("TEST 7: Clinical Guidelines - Medium Load (40 concurrent requests)")
    print("=" * 60)
    results = await tester.run_concurrent_requests(
        num_requests=40,
        method="GET",
        endpoint="/api/clinicals/decision-support/categories",
    )
    test_result = tester.analyze_results(results, "Clinical Guidelines - Medium Load")
    all_results.append(test_result)

    # Test 8: Stress Test - Very Heavy Load
    print("\n" + "=" * 60)
    print("TEST 8: Stress Test - Very Heavy Load (200 concurrent requests)")
    print("=" * 60)
    results = await tester.run_concurrent_requests(
        num_requests=200, method="GET", endpoint="/health"
    )
    test_result = tester.analyze_results(results, "Stress Test - Very Heavy Load")
    all_results.append(test_result)

    # Summary Report
    print("\n" + "=" * 60)
    print("📈 LOAD TEST SUMMARY")
    print("=" * 60)

    print("\n{:<40} {:>8} {:>10}".format("Test Name", "Success%", "Avg (ms)"))
    print("-" * 60)

    for result in all_results:
        if result:
            success_rate = (result["successful"] / result["total_requests"]) * 100
            print(
                "{:<40} {:>7.1f}% {:>10.2f}".format(
                    result["test_name"][:40], success_rate, result["mean_ms"]
                )
            )

    # Performance Recommendations
    print("\n" + "=" * 60)
    print("💡 PERFORMANCE RECOMMENDATIONS")
    print("=" * 60)

    avg_response_times = [r["mean_ms"] for r in all_results if r]
    overall_avg = statistics.mean(avg_response_times)

    print(f"\nOverall Average Response Time: {overall_avg:.2f}ms")

    if overall_avg < 100:
        print("\n🟢 Excellent Performance!")
        print("   • System is performing very well")
        print("   • Can handle current load easily")
        print("   • Consider increasing capacity for future growth")
    elif overall_avg < 500:
        print("\n🟡 Good Performance")
        print("   • System is performing well")
        print("   • Monitor during peak hours")
        print("   • Consider caching for frequently accessed data")
    elif overall_avg < 1000:
        print("\n🟠 Fair Performance")
        print("   • System is under stress")
        print("   • Recommendations:")
        print("     - Increase backend replicas")
        print("     - Optimize database queries")
        print("     - Implement caching")
        print("     - Review slow endpoints")
    else:
        print("\n🔴 Poor Performance")
        print("   • System is overloaded")
        print("   • Immediate actions needed:")
        print("     - Scale up backend pods")
        print("     - Optimize database indexes")
        print("     - Implement aggressive caching")
        print("     - Review and optimize slow queries")
        print("     - Consider load balancing improvements")

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"load_test_results_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n💾 Results saved to: {filename}")
    print("\n✅ Load testing complete!")


if __name__ == "__main__":
    print("\n⚠️  Prerequisites:")
    print("   1. iTechSmart HL7 backend must be running")
    print("   2. Update BASE_URL if not using localhost:8000")
    print("   3. Update TOKEN with a valid JWT token")
    print(
        "        -d '{&quot;username&quot;:&quot;admin&quot;,&quot;password&quot;:&quot;admin123&quot;}'"
    )
    print("\n" + "=" * 60)

    input("\nPress Enter to start load testing...")

    asyncio.run(main())
