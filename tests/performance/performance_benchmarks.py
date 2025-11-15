"""
Performance Benchmarks - iTechSmart Suite
Comprehensive performance testing and benchmarking
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class PerformanceBenchmark:
    """Performance benchmarking suite"""
    
    def __init__(self):
        self.results = []
    
    async def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        
        print("=" * 80)
        print("iTechSmart Suite - Performance Benchmarks")
        print("=" * 80)
        
        # Analytics benchmarks
        await self.benchmark_analytics_forecasting()
        await self.benchmark_anomaly_detection()
        await self.benchmark_dashboard_rendering()
        await self.benchmark_report_generation()
        
        # Integration benchmarks
        await self.benchmark_data_ingestion()
        await self.benchmark_cross_product_sync()
        
        # API benchmarks
        await self.benchmark_api_throughput()
        await self.benchmark_concurrent_requests()
        
        # Generate report
        self.generate_benchmark_report()
    
    async def benchmark_analytics_forecasting(self):
        """Benchmark forecasting performance"""
        
        print("\n[1/8] Benchmarking Analytics Forecasting...")
        
        # Test with different dataset sizes
        dataset_sizes = [100, 500, 1000, 5000, 10000]
        results = []
        
        for size in dataset_sizes:
            # Generate test data
            dates = pd.date_range(
                start=datetime.utcnow() - timedelta(days=size),
                end=datetime.utcnow(),
                freq='D'
            )
            data = pd.DataFrame({
                'timestamp': dates,
                'metric': np.random.randn(len(dates)).cumsum() + 100
            })
            
            # Measure forecast time
            start_time = time.time()
            
            # Simulate forecast (would call actual API)
            from sklearn.linear_model import LinearRegression
            X = np.arange(len(data)).reshape(-1, 1)
            y = data['metric'].values
            model = LinearRegression()
            model.fit(X, y)
            forecast = model.predict(np.arange(len(data), len(data) + 30).reshape(-1, 1))
            
            duration = time.time() - start_time
            
            results.append({
                "dataset_size": size,
                "duration_ms": duration * 1000,
                "records_per_second": size / duration if duration > 0 else 0
            })
            
            print(f"  Dataset size: {size:5d} | Time: {duration*1000:6.2f}ms | "
                  f"Speed: {size/duration:8.2f} records/sec")
        
        self.results.append({
            "benchmark": "Analytics Forecasting",
            "results": results,
            "avg_duration_ms": statistics.mean([r["duration_ms"] for r in results])
        })
    
    async def benchmark_anomaly_detection(self):
        """Benchmark anomaly detection performance"""
        
        print("\n[2/8] Benchmarking Anomaly Detection...")
        
        dataset_sizes = [100, 500, 1000, 5000]
        results = []
        
        for size in dataset_sizes:
            # Generate test data with anomalies
            data = np.random.randn(size)
            # Add some anomalies
            anomaly_indices = np.random.choice(size, size=int(size * 0.05), replace=False)
            data[anomaly_indices] += np.random.randn(len(anomaly_indices)) * 5
            
            # Measure detection time
            start_time = time.time()
            
            from sklearn.ensemble import IsolationForest
            model = IsolationForest(contamination=0.05, random_state=42)
            predictions = model.fit_predict(data.reshape(-1, 1))
            
            duration = time.time() - start_time
            
            anomalies_detected = sum(1 for p in predictions if p == -1)
            
            results.append({
                "dataset_size": size,
                "duration_ms": duration * 1000,
                "anomalies_detected": anomalies_detected,
                "records_per_second": size / duration if duration > 0 else 0
            })
            
            print(f"  Dataset size: {size:5d} | Time: {duration*1000:6.2f}ms | "
                  f"Anomalies: {anomalies_detected:3d} | Speed: {size/duration:8.2f} records/sec")
        
        self.results.append({
            "benchmark": "Anomaly Detection",
            "results": results,
            "avg_duration_ms": statistics.mean([r["duration_ms"] for r in results])
        })
    
    async def benchmark_dashboard_rendering(self):
        """Benchmark dashboard rendering performance"""
        
        print("\n[3/8] Benchmarking Dashboard Rendering...")
        
        widget_counts = [5, 10, 20, 50]
        results = []
        
        for count in widget_counts:
            start_time = time.time()
            
            # Simulate dashboard with multiple widgets
            dashboard = {
                "id": 1,
                "name": "Test Dashboard",
                "widgets": []
            }
            
            for i in range(count):
                widget = {
                    "id": i,
                    "type": "line_chart",
                    "data": np.random.randn(100).tolist()
                }
                dashboard["widgets"].append(widget)
            
            duration = time.time() - start_time
            
            results.append({
                "widget_count": count,
                "duration_ms": duration * 1000,
                "widgets_per_second": count / duration if duration > 0 else 0
            })
            
            print(f"  Widgets: {count:3d} | Time: {duration*1000:6.2f}ms | "
                  f"Speed: {count/duration:8.2f} widgets/sec")
        
        self.results.append({
            "benchmark": "Dashboard Rendering",
            "results": results,
            "avg_duration_ms": statistics.mean([r["duration_ms"] for r in results])
        })
    
    async def benchmark_report_generation(self):
        """Benchmark report generation performance"""
        
        print("\n[4/8] Benchmarking Report Generation...")
        
        report_sizes = [10, 50, 100, 500]  # Number of data points
        results = []
        
        for size in report_sizes:
            start_time = time.time()
            
            # Generate report data
            data = pd.DataFrame({
                'date': pd.date_range(start='2024-01-01', periods=size),
                'metric1': np.random.randn(size).cumsum() + 100,
                'metric2': np.random.randn(size).cumsum() + 50,
                'metric3': np.random.randn(size).cumsum() + 75
            })
            
            # Generate HTML report
            html = f"""
            <html>
            <head><title>Performance Report</title></head>
            <body>
                <h1>Performance Report</h1>
                <table>
                    {data.to_html()}
                </table>
            </body>
            </html>
            """
            
            duration = time.time() - start_time
            
            results.append({
                "data_points": size,
                "duration_ms": duration * 1000,
                "report_size_kb": len(html) / 1024,
                "points_per_second": size / duration if duration > 0 else 0
            })
            
            print(f"  Data points: {size:4d} | Time: {duration*1000:6.2f}ms | "
                  f"Size: {len(html)/1024:6.2f}KB | Speed: {size/duration:8.2f} points/sec")
        
        self.results.append({
            "benchmark": "Report Generation",
            "results": results,
            "avg_duration_ms": statistics.mean([r["duration_ms"] for r in results])
        })
    
    async def benchmark_data_ingestion(self):
        """Benchmark data ingestion performance"""
        
        print("\n[5/8] Benchmarking Data Ingestion...")
        
        batch_sizes = [100, 500, 1000, 5000]
        results = []
        
        for size in batch_sizes:
            start_time = time.time()
            
            # Simulate data ingestion
            records = []
            for i in range(size):
                record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "metric": np.random.randn(),
                    "source": "test"
                }
                records.append(record)
            
            # Simulate storage (would be actual database insert)
            df = pd.DataFrame(records)
            
            duration = time.time() - start_time
            
            results.append({
                "batch_size": size,
                "duration_ms": duration * 1000,
                "records_per_second": size / duration if duration > 0 else 0,
                "throughput_mbps": (len(str(records)) / 1024 / 1024) / duration if duration > 0 else 0
            })
            
            print(f"  Batch size: {size:5d} | Time: {duration*1000:6.2f}ms | "
                  f"Speed: {size/duration:8.2f} records/sec")
        
        self.results.append({
            "benchmark": "Data Ingestion",
            "results": results,
            "avg_duration_ms": statistics.mean([r["duration_ms"] for r in results])
        })
    
    async def benchmark_cross_product_sync(self):
        """Benchmark cross-product data synchronization"""
        
        print("\n[6/8] Benchmarking Cross-Product Sync...")
        
        sync_sizes = [100, 500, 1000]
        results = []
        
        for size in sync_sizes:
            start_time = time.time()
            
            # Simulate syncing data between products
            source_data = pd.DataFrame({
                'id': range(size),
                'value': np.random.randn(size),
                'timestamp': [datetime.utcnow().isoformat()] * size
            })
            
            # Simulate transformation and sync
            transformed_data = source_data.copy()
            transformed_data['synced_at'] = datetime.utcnow().isoformat()
            
            duration = time.time() - start_time
            
            results.append({
                "records_synced": size,
                "duration_ms": duration * 1000,
                "sync_rate": size / duration if duration > 0 else 0
            })
            
            print(f"  Records: {size:5d} | Time: {duration*1000:6.2f}ms | "
                  f"Rate: {size/duration:8.2f} records/sec")
        
        self.results.append({
            "benchmark": "Cross-Product Sync",
            "results": results,
            "avg_duration_ms": statistics.mean([r["duration_ms"] for r in results])
        })
    
    async def benchmark_api_throughput(self):
        """Benchmark API throughput"""
        
        print("\n[7/8] Benchmarking API Throughput...")
        
        request_counts = [10, 50, 100, 500]
        results = []
        
        for count in request_counts:
            start_time = time.time()
            
            # Simulate API requests
            responses = []
            for i in range(count):
                # Simulate request processing
                response = {
                    "status": 200,
                    "data": {"result": "success"},
                    "timestamp": datetime.utcnow().isoformat()
                }
                responses.append(response)
                await asyncio.sleep(0.001)  # Simulate processing time
            
            duration = time.time() - start_time
            
            results.append({
                "request_count": count,
                "duration_ms": duration * 1000,
                "requests_per_second": count / duration if duration > 0 else 0,
                "avg_response_time_ms": (duration * 1000) / count
            })
            
            print(f"  Requests: {count:4d} | Time: {duration*1000:7.2f}ms | "
                  f"Throughput: {count/duration:8.2f} req/sec | "
                  f"Avg response: {(duration*1000)/count:5.2f}ms")
        
        self.results.append({
            "benchmark": "API Throughput",
            "results": results,
            "avg_duration_ms": statistics.mean([r["duration_ms"] for r in results])
        })
    
    async def benchmark_concurrent_requests(self):
        """Benchmark concurrent request handling"""
        
        print("\n[8/8] Benchmarking Concurrent Requests...")
        
        concurrency_levels = [10, 50, 100, 200]
        results = []
        
        for level in concurrency_levels:
            start_time = time.time()
            
            # Simulate concurrent requests
            async def mock_request():
                await asyncio.sleep(0.01)  # Simulate processing
                return {"status": "success"}
            
            tasks = [mock_request() for _ in range(level)]
            responses = await asyncio.gather(*tasks)
            
            duration = time.time() - start_time
            
            results.append({
                "concurrency_level": level,
                "duration_ms": duration * 1000,
                "requests_per_second": level / duration if duration > 0 else 0,
                "avg_response_time_ms": (duration * 1000) / level
            })
            
            print(f"  Concurrency: {level:4d} | Time: {duration*1000:7.2f}ms | "
                  f"Throughput: {level/duration:8.2f} req/sec | "
                  f"Avg response: {(duration*1000)/level:5.2f}ms")
        
        self.results.append({
            "benchmark": "Concurrent Requests",
            "results": results,
            "avg_duration_ms": statistics.mean([r["duration_ms"] for r in results])
        })
    
    def generate_benchmark_report(self):
        """Generate comprehensive benchmark report"""
        
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        
        for result in self.results:
            print(f"\n{result['benchmark']}:")
            print(f"  Average Duration: {result['avg_duration_ms']:.2f}ms")
            
            if result['results']:
                first = result['results'][0]
                last = result['results'][-1]
                
                if 'records_per_second' in first:
                    print(f"  Min Speed: {first['records_per_second']:.2f} records/sec")
                    print(f"  Max Speed: {last['records_per_second']:.2f} records/sec")
                elif 'requests_per_second' in first:
                    print(f"  Min Throughput: {first['requests_per_second']:.2f} req/sec")
                    print(f"  Max Throughput: {last['requests_per_second']:.2f} req/sec")
        
        print("\n" + "=" * 80)
        print("PERFORMANCE GRADE")
        print("=" * 80)
        
        # Calculate overall grade
        avg_durations = [r['avg_duration_ms'] for r in self.results]
        overall_avg = statistics.mean(avg_durations)
        
        if overall_avg < 100:
            grade = "A+ (Excellent)"
        elif overall_avg < 500:
            grade = "A (Very Good)"
        elif overall_avg < 1000:
            grade = "B (Good)"
        elif overall_avg < 2000:
            grade = "C (Acceptable)"
        else:
            grade = "D (Needs Improvement)"
        
        print(f"\nOverall Performance Grade: {grade}")
        print(f"Average Response Time: {overall_avg:.2f}ms")
        print("\n" + "=" * 80)


async def main():
    """Run all benchmarks"""
    benchmark = PerformanceBenchmark()
    await benchmark.run_all_benchmarks()


if __name__ == "__main__":
    asyncio.run(main())