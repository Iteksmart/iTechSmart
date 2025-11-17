"""
Performance Optimization API Endpoints
Provides real-time performance monitoring and optimization controls
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import redis
from datetime import datetime

from app.models.database import get_db
from app.core.performance_optimizer import (
    QueryOptimizer,
    CacheStrategy,
    PerformanceMonitor,
    ConnectionPoolManager,
)

router = APIRouter(prefix="/api/performance", tags=["Performance"])

# Initialize performance components
performance_monitor = PerformanceMonitor()
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
cache_strategy = CacheStrategy(redis_client)
pool_manager = ConnectionPoolManager()


@router.get("/system-metrics")
async def get_system_metrics():
    """Get current system performance metrics"""
    try:
        metrics = performance_monitor.get_system_metrics()
        return {
            "success": True,
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching system metrics: {str(e)}"
        )


@router.get("/slow-queries")
async def get_slow_queries(threshold_ms: int = 100, db: Session = Depends(get_db)):
    """Identify slow database queries"""
    try:
        optimizer = QueryOptimizer(db, redis_client)
        slow_queries = optimizer.analyze_slow_queries(threshold_ms)

        return {
            "success": True,
            "threshold_ms": threshold_ms,
            "count": len(slow_queries),
            "queries": slow_queries,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing queries: {str(e)}"
        )


@router.get("/index-suggestions")
async def get_index_suggestions(db: Session = Depends(get_db)):
    """Get suggestions for missing database indexes"""
    try:
        optimizer = QueryOptimizer(db, redis_client)
        suggestions = optimizer.suggest_indexes()

        return {"success": True, "count": len(suggestions), "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating suggestions: {str(e)}"
        )


@router.post("/optimize-table/{table_name}")
async def optimize_table(table_name: str, db: Session = Depends(get_db)):
    """Run VACUUM and ANALYZE on a specific table"""
    try:
        optimizer = QueryOptimizer(db, redis_client)
        result = optimizer.optimize_table(table_name)

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing table: {str(e)}")


@router.get("/cache-stats")
async def get_cache_stats():
    """Get cache performance statistics"""
    try:
        stats = cache_strategy.get_stats()

        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching cache stats: {str(e)}"
        )


@router.post("/cache-invalidate")
async def invalidate_cache(pattern: str):
    """Invalidate cache keys matching a pattern"""
    try:
        count = cache_strategy.invalidate_pattern(pattern)

        return {"success": True, "pattern": pattern, "keys_invalidated": count}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error invalidating cache: {str(e)}"
        )


@router.get("/metric-summary/{metric_name}")
async def get_metric_summary(metric_name: str, minutes: int = 5):
    """Get summary statistics for a performance metric"""
    try:
        summary = performance_monitor.get_metric_summary(metric_name, minutes)

        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching metric summary: {str(e)}"
        )


@router.get("/connection-pool-stats")
async def get_connection_pool_stats(db: Session = Depends(get_db)):
    """Get database connection pool statistics"""
    try:
        pool = db.get_bind().pool
        stats = pool_manager.get_pool_stats(pool)

        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching pool stats: {str(e)}"
        )


@router.post("/recommend-pool-size")
async def recommend_pool_size(avg_query_time_ms: float, requests_per_second: int):
    """Get recommendations for optimal connection pool size"""
    try:
        recommendation = pool_manager.recommend_pool_size(
            avg_query_time_ms, requests_per_second
        )

        return {"success": True, "data": recommendation}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating recommendation: {str(e)}"
        )


@router.get("/health-check")
async def performance_health_check():
    """Comprehensive performance health check"""
    try:
        system_metrics = performance_monitor.get_system_metrics()
        cache_stats = cache_strategy.get_stats()

        # Determine overall health status
        warnings = []
        if system_metrics["cpu"]["status"] == "warning":
            warnings.append("High CPU usage")
        if system_metrics["memory"]["status"] == "warning":
            warnings.append("High memory usage")
        if system_metrics["disk"]["status"] == "warning":
            warnings.append("High disk usage")
        if cache_stats["hit_rate_percent"] < 70:
            warnings.append("Low cache hit rate")

        overall_status = "healthy" if not warnings else "warning"

        return {
            "success": True,
            "status": overall_status,
            "warnings": warnings,
            "system": system_metrics,
            "cache": cache_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error performing health check: {str(e)}"
        )


@router.get("/performance-report")
async def get_performance_report(db: Session = Depends(get_db)):
    """Generate comprehensive performance report"""
    try:
        optimizer = QueryOptimizer(db, redis_client)

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": performance_monitor.get_system_metrics(),
            "cache_stats": cache_strategy.get_stats(),
            "slow_queries": optimizer.analyze_slow_queries(100),
            "index_suggestions": optimizer.suggest_indexes(),
            "recommendations": [],
        }

        # Generate recommendations
        if report["cache_stats"]["hit_rate_percent"] < 70:
            report["recommendations"].append(
                {
                    "type": "cache",
                    "priority": "high",
                    "message": "Cache hit rate is below 70%. Consider increasing TTL or cache size.",
                }
            )

        if len(report["slow_queries"]) > 5:
            report["recommendations"].append(
                {
                    "type": "database",
                    "priority": "high",
                    "message": f"Found {len(report['slow_queries'])} slow queries. Review and optimize.",
                }
            )

        if len(report["index_suggestions"]) > 0:
            report["recommendations"].append(
                {
                    "type": "database",
                    "priority": "medium",
                    "message": f"Found {len(report['index_suggestions'])} missing indexes. Consider adding them.",
                }
            )

        return {"success": True, "data": report}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating report: {str(e)}"
        )
