"""
Redis Cache Manager
Caching layer for improved performance
"""

import redis
import json
import logging
from typing import Any, Optional
from datetime import timedelta
import os

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)


class CacheManager:
    """
    Redis cache manager with common operations
    """

    def __init__(self, client: redis.Redis = redis_client):
        self.client = client
        self.default_ttl = 3600  # 1 hour default TTL

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with optional TTL
        """
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            return self.client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        """
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        """
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for key
        """
        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False

    def ttl(self, key: str) -> int:
        """
        Get remaining TTL for key
        """
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1

    def flush_all(self) -> bool:
        """
        Flush all keys from cache (use with caution!)
        """
        try:
            return bool(self.client.flushdb())
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False

    def get_keys(self, pattern: str = "*") -> list:
        """
        Get all keys matching pattern
        """
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Cache get_keys error: {e}")
            return []

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment counter
        """
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Decrement counter
        """
        try:
            return self.client.decrby(key, amount)
        except Exception as e:
            logger.error(f"Cache decrement error for key {key}: {e}")
            return None

    # Hash operations

    def hget(self, name: str, key: str) -> Optional[Any]:
        """
        Get value from hash
        """
        try:
            value = self.client.hget(name, key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache hget error for {name}:{key}: {e}")
            return None

    def hset(self, name: str, key: str, value: Any) -> bool:
        """
        Set value in hash
        """
        try:
            serialized = json.dumps(value)
            return bool(self.client.hset(name, key, serialized))
        except Exception as e:
            logger.error(f"Cache hset error for {name}:{key}: {e}")
            return False

    def hgetall(self, name: str) -> dict:
        """
        Get all values from hash
        """
        try:
            data = self.client.hgetall(name)
            return {k: json.loads(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Cache hgetall error for {name}: {e}")
            return {}

    def hdel(self, name: str, *keys: str) -> int:
        """
        Delete keys from hash
        """
        try:
            return self.client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Cache hdel error for {name}: {e}")
            return 0

    # List operations

    def lpush(self, key: str, *values: Any) -> Optional[int]:
        """
        Push values to left of list
        """
        try:
            serialized = [json.dumps(v) for v in values]
            return self.client.lpush(key, *serialized)
        except Exception as e:
            logger.error(f"Cache lpush error for key {key}: {e}")
            return None

    def rpush(self, key: str, *values: Any) -> Optional[int]:
        """
        Push values to right of list
        """
        try:
            serialized = [json.dumps(v) for v in values]
            return self.client.rpush(key, *serialized)
        except Exception as e:
            logger.error(f"Cache rpush error for key {key}: {e}")
            return None

    def lrange(self, key: str, start: int = 0, end: int = -1) -> list:
        """
        Get range of values from list
        """
        try:
            values = self.client.lrange(key, start, end)
            return [json.loads(v) for v in values]
        except Exception as e:
            logger.error(f"Cache lrange error for key {key}: {e}")
            return []

    def llen(self, key: str) -> int:
        """
        Get length of list
        """
        try:
            return self.client.llen(key)
        except Exception as e:
            logger.error(f"Cache llen error for key {key}: {e}")
            return 0

    # Set operations

    def sadd(self, key: str, *values: Any) -> Optional[int]:
        """
        Add values to set
        """
        try:
            serialized = [json.dumps(v) for v in values]
            return self.client.sadd(key, *serialized)
        except Exception as e:
            logger.error(f"Cache sadd error for key {key}: {e}")
            return None

    def smembers(self, key: str) -> set:
        """
        Get all members of set
        """
        try:
            values = self.client.smembers(key)
            return {json.loads(v) for v in values}
        except Exception as e:
            logger.error(f"Cache smembers error for key {key}: {e}")
            return set()

    def sismember(self, key: str, value: Any) -> bool:
        """
        Check if value is member of set
        """
        try:
            serialized = json.dumps(value)
            return bool(self.client.sismember(key, serialized))
        except Exception as e:
            logger.error(f"Cache sismember error for key {key}: {e}")
            return False

    def srem(self, key: str, *values: Any) -> int:
        """
        Remove values from set
        """
        try:
            serialized = [json.dumps(v) for v in values]
            return self.client.srem(key, *serialized)
        except Exception as e:
            logger.error(f"Cache srem error for key {key}: {e}")
            return 0


# Global cache manager instance
cache_manager = CacheManager()


# Cache key generators
class CacheKeys:
    """
    Cache key generators for consistent naming
    """

    @staticmethod
    def patient(patient_id: str) -> str:
        return f"patient:{patient_id}"

    @staticmethod
    def patient_by_mrn(mrn: str) -> str:
        return f"patient:mrn:{mrn}"

    @staticmethod
    def observations(patient_id: str, category: Optional[str] = None) -> str:
        if category:
            return f"observations:{patient_id}:{category}"
        return f"observations:{patient_id}"

    @staticmethod
    def medications(patient_id: str) -> str:
        return f"medications:{patient_id}"

    @staticmethod
    def allergies(patient_id: str) -> str:
        return f"allergies:{patient_id}"

    @staticmethod
    def connection(connection_id: str) -> str:
        return f"connection:{connection_id}"

    @staticmethod
    def connection_status(connection_id: str) -> str:
        return f"connection:status:{connection_id}"

    @staticmethod
    def hl7_message(message_control_id: str) -> str:
        return f"hl7:message:{message_control_id}"

    @staticmethod
    def rate_limit(client_id: str) -> str:
        return f"ratelimit:{client_id}"

    @staticmethod
    def session(session_id: str) -> str:
        return f"session:{session_id}"


# Cache health check
def check_redis_connection() -> bool:
    """
    Check if Redis connection is working
    """
    try:
        return redis_client.ping()
    except Exception as e:
        logger.error(f"Redis connection check failed: {e}")
        return False


def get_redis_health() -> dict:
    """
    Get Redis health status
    """
    health = {"status": "unknown", "connection": False, "info": {}}

    try:
        # Check connection
        health["connection"] = check_redis_connection()

        if health["connection"]:
            # Get Redis info
            info = redis_client.info()
            health["info"] = {
                "version": info.get("redis_version"),
                "uptime_seconds": info.get("uptime_in_seconds"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "total_keys": sum(redis_client.dbsize() for _ in range(16)),
            }
            health["status"] = "healthy"
        else:
            health["status"] = "unhealthy"

    except Exception as e:
        logger.error(f"Failed to get Redis health: {e}")
        health["status"] = "error"
        health["error"] = str(e)

    return health
