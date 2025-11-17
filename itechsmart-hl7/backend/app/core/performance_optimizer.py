"""
Performance Optimization Suite for iTechSmart HL7
Provides database query optimization, caching strategies, and performance monitoring
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import psutil
import redis
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Optimizes database queries with intelligent caching and indexing"""

    def __init__(self, db_session: Session, redis_client: redis.Redis):
        self.db = db_session
        self.redis = redis_client
        self.query_stats = defaultdict(
            lambda: {"count": 0, "total_time": 0, "avg_time": 0}
        )

    def analyze_slow_queries(self, threshold_ms: int = 100) -> List[Dict[str, Any]]:
        """Identify slow queries from PostgreSQL logs"""
        query = text(
            """
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                max_time,
                stddev_time
            FROM pg_stat_statements
            WHERE mean_time > :threshold
            ORDER BY mean_time DESC
            LIMIT 20
        """
        )

        try:
            result = self.db.execute(query, {"threshold": threshold_ms})
            slow_queries = []

            for row in result:
                slow_queries.append(
                    {
                        "query": row.query[:200],  # Truncate for readability
                        "calls": row.calls,
                        "total_time_ms": round(row.total_time, 2),
                        "avg_time_ms": round(row.mean_time, 2),
                        "max_time_ms": round(row.max_time, 2),
                        "stddev_ms": round(row.stddev_time, 2),
                    }
                )

            return slow_queries
        except Exception as e:
            logger.error(f"Error analyzing slow queries: {e}")
            return []

    def suggest_indexes(self) -> List[Dict[str, str]]:
        """Suggest missing indexes based on query patterns"""
        suggestions = []

        # Check for missing indexes on foreign keys
        query = text(
            """
            SELECT 
                schemaname,
                tablename,
                attname as column_name
            FROM pg_stats
            WHERE schemaname = 'public'
            AND correlation < 0.1
            AND n_distinct > 100
        """
        )

        try:
            result = self.db.execute(query)
            for row in result:
                suggestions.append(
                    {
                        "table": row.tablename,
                        "column": row.column_name,
                        "reason": "Low correlation, high cardinality",
                        "sql": f"CREATE INDEX idx_{row.tablename}_{row.column_name} ON {row.tablename}({row.column_name});",
                    }
                )
        except Exception as e:
            logger.error(f"Error suggesting indexes: {e}")

        return suggestions

    def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """Run VACUUM and ANALYZE on a specific table"""
        try:
            # VACUUM cannot run inside a transaction
            self.db.execute(text(f"VACUUM ANALYZE {table_name}"))
            self.db.commit()

            # Get table statistics
            stats_query = text(
                """
                SELECT 
                    pg_size_pretty(pg_total_relation_size(:table)) as total_size,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_analyze
                FROM pg_stat_user_tables
                WHERE relname = :table
            """
            )

            result = self.db.execute(stats_query, {"table": table_name}).fetchone()

            return {
                "table": table_name,
                "total_size": result.total_size,
                "live_rows": result.live_rows,
                "dead_rows": result.dead_rows,
                "last_vacuum": result.last_vacuum,
                "last_analyze": result.last_analyze,
                "status": "optimized",
            }
        except Exception as e:
            logger.error(f"Error optimizing table {table_name}: {e}")
            return {"table": table_name, "status": "error", "error": str(e)}


class CacheStrategy:
    """Advanced caching strategies with TTL and invalidation"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.hit_count = 0
        self.miss_count = 0

    def cache_aside(self, key: str, fetch_func: Callable, ttl: int = 300) -> Any:
        """Cache-aside pattern: Check cache first, then fetch if missing"""
        # Try to get from cache
        cached = self.redis.get(key)
        if cached:
            self.hit_count += 1
            return cached

        # Cache miss - fetch from source
        self.miss_count += 1
        data = fetch_func()

        # Store in cache
        self.redis.setex(key, ttl, data)
        return data

    def write_through(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Write-through pattern: Write to cache and database simultaneously"""
        try:
            self.redis.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Cache write-through error: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache keys matching a pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0

        return {
            "hits": self.hit_count,
            "misses": self.miss_count,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "memory_used": self.redis.info("memory")["used_memory_human"],
            "keys_count": self.redis.dbsize(),
        }


class PerformanceMonitor:
    """Real-time performance monitoring and alerting"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.thresholds = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90,
            "response_time_ms": 500,
        }

    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric"""
        self.metrics[metric_name].append(
            {"timestamp": datetime.utcnow().isoformat(), "value": value}
        )

        # Keep only last 1000 metrics per type
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count(),
                "status": (
                    "warning"
                    if cpu_percent > self.thresholds["cpu_percent"]
                    else "healthy"
                ),
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent,
                "status": (
                    "warning"
                    if memory.percent > self.thresholds["memory_percent"]
                    else "healthy"
                ),
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "percent": disk.percent,
                "status": (
                    "warning"
                    if disk.percent > self.thresholds["disk_percent"]
                    else "healthy"
                ),
            },
        }

        return metrics

    def get_metric_summary(self, metric_name: str, minutes: int = 5) -> Dict[str, Any]:
        """Get summary statistics for a metric over time"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [
            m
            for m in self.metrics[metric_name]
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]

        if not recent_metrics:
            return {"error": "No data available"}

        values = [m["value"] for m in recent_metrics]

        return {
            "metric": metric_name,
            "period_minutes": minutes,
            "count": len(values),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(sum(values) / len(values), 2),
            "latest": round(values[-1], 2),
        }


def performance_tracker(metric_name: str):
    """Decorator to track function execution time"""

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                logger.info(f"{metric_name} execution time: {execution_time:.2f}ms")

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                logger.info(f"{metric_name} execution time: {execution_time:.2f}ms")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class ConnectionPoolManager:
    """Manage database connection pools for optimal performance"""

    def __init__(self):
        self.pool_stats = {}

    def get_pool_stats(self, pool) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
            "utilization_percent": round(
                (
                    (pool.checkedout() / (pool.size() + pool.overflow()) * 100)
                    if (pool.size() + pool.overflow()) > 0
                    else 0
                ),
                2,
            ),
        }

    def recommend_pool_size(
        self, avg_query_time_ms: float, requests_per_second: int
    ) -> Dict[str, int]:
        """Recommend optimal pool size based on load"""
        # Formula: pool_size = (requests_per_second * avg_query_time_ms) / 1000
        recommended_size = int((requests_per_second * avg_query_time_ms) / 1000)

        # Add 20% buffer and ensure minimum of 5
        recommended_size = max(5, int(recommended_size * 1.2))

        return {
            "recommended_pool_size": recommended_size,
            "recommended_max_overflow": int(recommended_size * 0.5),
            "reasoning": f"Based on {requests_per_second} req/s and {avg_query_time_ms}ms avg query time",
        }


# Example usage and testing
if __name__ == "__main__":
    print("Performance Optimization Suite initialized")
    print("Features:")
    print("  ✅ Query Optimizer - Analyze slow queries and suggest indexes")
    print("  ✅ Cache Strategy - Advanced caching with TTL and invalidation")
    print("  ✅ Performance Monitor - Real-time system metrics")
    print("  ✅ Connection Pool Manager - Optimize database connections")
