"""
MCP (Model Context Protocol) Integration
Enables AI models to connect to external data sources and tools
"""

import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import logging

# Database connectors
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# API clients
import aiohttp
from urllib.parse import urljoin

# File system
import os
import boto3
from pathlib import Path

# Search engines
try:
    from elasticsearch import Elasticsearch, AsyncElasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)


class DataSourceType(str, Enum):
    """Supported data source types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    LOCAL_FS = "local_fs"
    S3 = "s3"
    ELASTICSEARCH = "elasticsearch"
    CUSTOM = "custom"


class MCPDataSource:
    """Base class for MCP data sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "Unnamed Source")
        self.type = config.get("type")
        self.connection = None
        self.last_used = None
        
    async def connect(self) -> bool:
        """Establish connection to data source"""
        raise NotImplementedError
        
    async def disconnect(self) -> bool:
        """Close connection to data source"""
        raise NotImplementedError
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to data source"""
        raise NotImplementedError
        
    async def query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute query on data source"""
        raise NotImplementedError
        
    async def get_schema(self) -> Dict[str, Any]:
        """Get schema information from data source"""
        raise NotImplementedError


class PostgreSQLSource(MCPDataSource):
    """PostgreSQL data source"""
    
    async def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 not installed")
            
        try:
            self.connection = psycopg2.connect(
                self.config.get("connection_string"),
                cursor_factory=RealDictCursor
            )
            logger.info(f"Connected to PostgreSQL: {self.name}")
            return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise
            
    async def disconnect(self) -> bool:
        """Disconnect from PostgreSQL"""
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test PostgreSQL connection"""
        try:
            await self.connect()
            cursor = self.connection.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            cursor.close()
            await self.disconnect()
            
            return {
                "success": True,
                "message": "Connection successful",
                "version": version[0] if version else None
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
            
    async def query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute PostgreSQL query"""
        if not self.connection:
            await self.connect()
            
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                self.connection.commit()
                return {"affected_rows": cursor.rowcount}
        finally:
            cursor.close()
            
    async def get_schema(self) -> Dict[str, Any]:
        """Get PostgreSQL schema"""
        if not self.connection:
            await self.connect()
            
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
        
        schema = {}
        for row in cursor.fetchall():
            table = row['table_name']
            if table not in schema:
                schema[table] = []
            schema[table].append({
                "column": row['column_name'],
                "type": row['data_type']
            })
            
        cursor.close()
        return schema


class MySQLSource(MCPDataSource):
    """MySQL data source"""
    
    async def connect(self) -> bool:
        """Connect to MySQL database"""
        if not MYSQL_AVAILABLE:
            raise ImportError("pymysql not installed")
            
        try:
            config = self.config.get("connection_config", {})
            self.connection = pymysql.connect(
                host=config.get("host", "localhost"),
                user=config.get("user"),
                password=config.get("password"),
                database=config.get("database"),
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"Connected to MySQL: {self.name}")
            return True
        except Exception as e:
            logger.error(f"MySQL connection failed: {e}")
            raise
            
    async def disconnect(self) -> bool:
        """Disconnect from MySQL"""
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test MySQL connection"""
        try:
            await self.connect()
            cursor = self.connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            await self.disconnect()
            
            return {
                "success": True,
                "message": "Connection successful",
                "version": version.get('VERSION()') if version else None
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
            
    async def query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute MySQL query"""
        if not self.connection:
            await self.connect()
            
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                return results
            else:
                self.connection.commit()
                return {"affected_rows": cursor.rowcount}
        finally:
            cursor.close()
            
    async def get_schema(self) -> Dict[str, Any]:
        """Get MySQL schema"""
        if not self.connection:
            await self.connect()
            
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            schema[table] = [
                {
                    "column": row['Field'],
                    "type": row['Type']
                }
                for row in cursor.fetchall()
            ]
            
        cursor.close()
        return schema


class MongoDBSource(MCPDataSource):
    """MongoDB data source"""
    
    async def connect(self) -> bool:
        """Connect to MongoDB"""
        if not MONGODB_AVAILABLE:
            raise ImportError("pymongo not installed")
            
        try:
            self.connection = MongoClient(
                self.config.get("connection_string")
            )
            # Test connection
            self.connection.server_info()
            logger.info(f"Connected to MongoDB: {self.name}")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
            
    async def disconnect(self) -> bool:
        """Disconnect from MongoDB"""
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test MongoDB connection"""
        try:
            await self.connect()
            info = self.connection.server_info()
            await self.disconnect()
            
            return {
                "success": True,
                "message": "Connection successful",
                "version": info.get('version')
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
            
    async def query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute MongoDB query"""
        if not self.connection:
            await self.connect()
            
        # Parse query format: db.collection.operation(args)
        try:
            query_dict = json.loads(query)
            db_name = query_dict.get("database")
            collection_name = query_dict.get("collection")
            operation = query_dict.get("operation", "find")
            args = query_dict.get("args", {})
            
            db = self.connection[db_name]
            collection = db[collection_name]
            
            if operation == "find":
                results = list(collection.find(args))
                # Convert ObjectId to string
                for doc in results:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                return results
            elif operation == "insert_one":
                result = collection.insert_one(args)
                return {"inserted_id": str(result.inserted_id)}
            elif operation == "update_one":
                result = collection.update_one(
                    args.get("filter", {}),
                    args.get("update", {})
                )
                return {"modified_count": result.modified_count}
            elif operation == "delete_one":
                result = collection.delete_one(args)
                return {"deleted_count": result.deleted_count}
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except json.JSONDecodeError:
            raise ValueError("Invalid MongoDB query format. Expected JSON.")
            
    async def get_schema(self) -> Dict[str, Any]:
        """Get MongoDB schema"""
        if not self.connection:
            await self.connect()
            
        schema = {}
        for db_name in self.connection.list_database_names():
            if db_name not in ['admin', 'local', 'config']:
                db = self.connection[db_name]
                schema[db_name] = {
                    "collections": db.list_collection_names()
                }
                
        return schema


class RedisSource(MCPDataSource):
    """Redis data source"""
    
    async def connect(self) -> bool:
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            raise ImportError("redis not installed")
            
        try:
            config = self.config.get("connection_config", {})
            self.connection = redis.Redis(
                host=config.get("host", "localhost"),
                port=config.get("port", 6379),
                password=config.get("password"),
                db=config.get("db", 0),
                decode_responses=True
            )
            # Test connection
            self.connection.ping()
            logger.info(f"Connected to Redis: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
            
    async def disconnect(self) -> bool:
        """Disconnect from Redis"""
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test Redis connection"""
        try:
            await self.connect()
            info = self.connection.info()
            await self.disconnect()
            
            return {
                "success": True,
                "message": "Connection successful",
                "version": info.get('redis_version')
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
            
    async def query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute Redis command"""
        if not self.connection:
            await self.connect()
            
        # Parse command format: {"command": "GET", "args": ["key"]}
        try:
            query_dict = json.loads(query)
            command = query_dict.get("command", "").upper()
            args = query_dict.get("args", [])
            
            if command == "GET":
                return self.connection.get(args[0])
            elif command == "SET":
                return self.connection.set(args[0], args[1])
            elif command == "KEYS":
                return self.connection.keys(args[0] if args else "*")
            elif command == "HGETALL":
                return self.connection.hgetall(args[0])
            else:
                # Generic command execution
                return self.connection.execute_command(command, *args)
                
        except json.JSONDecodeError:
            raise ValueError("Invalid Redis query format. Expected JSON.")
            
    async def get_schema(self) -> Dict[str, Any]:
        """Get Redis info"""
        if not self.connection:
            await self.connect()
            
        info = self.connection.info()
        return {
            "server": {
                "version": info.get('redis_version'),
                "mode": info.get('redis_mode')
            },
            "stats": {
                "total_keys": self.connection.dbsize(),
                "used_memory": info.get('used_memory_human')
            }
        }


class RESTAPISource(MCPDataSource):
    """REST API data source"""
    
    async def connect(self) -> bool:
        """Initialize REST API client"""
        self.base_url = self.config.get("base_url")
        self.headers = self.config.get("headers", {})
        self.auth = self.config.get("auth")
        logger.info(f"Initialized REST API: {self.name}")
        return True
        
    async def disconnect(self) -> bool:
        """No persistent connection for REST API"""
        return True
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test REST API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return {
                        "success": response.status < 400,
                        "message": f"Status: {response.status}",
                        "status_code": response.status
                    }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
            
    async def query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute REST API request"""
        # Parse query format: {"method": "GET", "endpoint": "/users", "data": {}}
        try:
            query_dict = json.loads(query)
            method = query_dict.get("method", "GET").upper()
            endpoint = query_dict.get("endpoint", "")
            data = query_dict.get("data")
            query_params = query_dict.get("params")
            
            url = urljoin(self.base_url, endpoint)
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=self.headers,
                    json=data,
                    params=query_params
                ) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
                    
        except json.JSONDecodeError:
            raise ValueError("Invalid REST API query format. Expected JSON.")
            
    async def get_schema(self) -> Dict[str, Any]:
        """Get API schema (if available)"""
        # Try to fetch OpenAPI/Swagger schema
        schema_endpoints = ["/openapi.json", "/swagger.json", "/api-docs"]
        
        for endpoint in schema_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 200:
                            return await response.json()
            except:
                continue
                
        return {
            "message": "No schema available",
            "base_url": self.base_url
        }


class ElasticsearchSource(MCPDataSource):
    """Elasticsearch data source"""
    
    async def connect(self) -> bool:
        """Connect to Elasticsearch"""
        if not ELASTICSEARCH_AVAILABLE:
            raise ImportError("elasticsearch not installed")
            
        try:
            config = self.config.get("connection_config", {})
            self.connection = AsyncElasticsearch(
                hosts=[config.get("host", "localhost:9200")],
                basic_auth=(config.get("user"), config.get("password")) if config.get("user") else None
            )
            # Test connection
            await self.connection.info()
            logger.info(f"Connected to Elasticsearch: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Elasticsearch connection failed: {e}")
            raise
            
    async def disconnect(self) -> bool:
        """Disconnect from Elasticsearch"""
        if self.connection:
            await self.connection.close()
            self.connection = None
        return True
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test Elasticsearch connection"""
        try:
            await self.connect()
            info = await self.connection.info()
            await self.disconnect()
            
            return {
                "success": True,
                "message": "Connection successful",
                "version": info.get('version', {}).get('number')
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
            
    async def query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute Elasticsearch query"""
        if not self.connection:
            await self.connect()
            
        # Parse query format: {"index": "logs", "body": {...}}
        try:
            query_dict = json.loads(query)
            index = query_dict.get("index")
            body = query_dict.get("body", {})
            
            result = await self.connection.search(index=index, body=body)
            return result['hits']['hits']
            
        except json.JSONDecodeError:
            raise ValueError("Invalid Elasticsearch query format. Expected JSON.")
            
    async def get_schema(self) -> Dict[str, Any]:
        """Get Elasticsearch indices"""
        if not self.connection:
            await self.connect()
            
        indices = await self.connection.cat.indices(format='json')
        return {
            "indices": [
                {
                    "name": idx['index'],
                    "docs_count": idx.get('docs.count'),
                    "size": idx.get('store.size')
                }
                for idx in indices
            ]
        }


class MCPClient:
    """Main MCP client for managing data sources"""
    
    def __init__(self):
        self.sources: Dict[str, MCPDataSource] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes default
        self.query_history: List[Dict] = []
        
    def _get_source_class(self, source_type: str) -> type:
        """Get appropriate source class for type"""
        source_map = {
            DataSourceType.POSTGRESQL: PostgreSQLSource,
            DataSourceType.MYSQL: MySQLSource,
            DataSourceType.MONGODB: MongoDBSource,
            DataSourceType.REDIS: RedisSource,
            DataSourceType.REST_API: RESTAPISource,
            DataSourceType.ELASTICSEARCH: ElasticsearchSource,
        }
        
        source_class = source_map.get(source_type)
        if not source_class:
            raise ValueError(f"Unsupported source type: {source_type}")
            
        return source_class
        
    async def register_source(
        self,
        source_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register a new data source"""
        try:
            source_type = config.get("type")
            source_class = self._get_source_class(source_type)
            
            source = source_class(config)
            await source.connect()
            
            self.sources[source_id] = source
            
            return {
                "success": True,
                "source_id": source_id,
                "message": f"Source '{config.get('name')}' registered successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to register source: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def unregister_source(self, source_id: str) -> Dict[str, Any]:
        """Unregister a data source"""
        if source_id not in self.sources:
            return {
                "success": False,
                "error": "Source not found"
            }
            
        source = self.sources[source_id]
        await source.disconnect()
        del self.sources[source_id]
        
        return {
            "success": True,
            "message": f"Source '{source_id}' unregistered"
        }
        
    async def test_source(self, source_id: str) -> Dict[str, Any]:
        """Test connection to a data source"""
        if source_id not in self.sources:
            return {
                "success": False,
                "error": "Source not found"
            }
            
        source = self.sources[source_id]
        return await source.test_connection()
        
    async def query_source(
        self,
        source_id: str,
        query: str,
        params: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Query a data source"""
        if source_id not in self.sources:
            return {
                "success": False,
                "error": "Source not found"
            }
            
        # Check cache
        cache_key = self._get_cache_key(source_id, query, params)
        if use_cache and cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() < cached_data['expires']:
                logger.info(f"Cache hit for query: {cache_key[:50]}...")
                return {
                    "success": True,
                    "data": cached_data['data'],
                    "cached": True,
                    "execution_time": 0
                }
                
        # Execute query
        source = self.sources[source_id]
        start_time = datetime.now()
        
        try:
            result = await source.query(query, params)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Cache result
            if use_cache:
                self.cache[cache_key] = {
                    'data': result,
                    'expires': datetime.now() + timedelta(seconds=self.cache_ttl)
                }
                
            # Record in history
            self.query_history.append({
                'source_id': source_id,
                'query': query[:100],  # Truncate for storage
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'cached': False
            })
            
            return {
                "success": True,
                "data": result,
                "cached": False,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def get_schema(self, source_id: str) -> Dict[str, Any]:
        """Get schema from a data source"""
        if source_id not in self.sources:
            return {
                "success": False,
                "error": "Source not found"
            }
            
        source = self.sources[source_id]
        try:
            schema = await source.get_schema()
            return {
                "success": True,
                "schema": schema
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def list_sources(self) -> List[Dict[str, Any]]:
        """List all registered sources"""
        return [
            {
                "id": source_id,
                "name": source.name,
                "type": source.type,
                "last_used": source.last_used.isoformat() if source.last_used else None
            }
            for source_id, source in self.sources.items()
        ]
        
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for data in self.cache.values()
            if datetime.now() >= data['expires']
        )
        
        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries,
            "cache_ttl": self.cache_ttl
        }
        
    def clear_cache(self, source_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear cache"""
        if source_id:
            # Clear cache for specific source
            keys_to_delete = [
                key for key in self.cache.keys()
                if key.startswith(f"{source_id}:")
            ]
            for key in keys_to_delete:
                del self.cache[key]
            return {
                "success": True,
                "message": f"Cleared {len(keys_to_delete)} cache entries for source {source_id}"
            }
        else:
            # Clear all cache
            count = len(self.cache)
            self.cache.clear()
            return {
                "success": True,
                "message": f"Cleared {count} cache entries"
            }
            
    def _get_cache_key(
        self,
        source_id: str,
        query: str,
        params: Optional[Dict]
    ) -> str:
        """Generate cache key"""
        key_data = f"{source_id}:{query}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def get_query_history(
        self,
        source_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get query history"""
        history = self.query_history
        
        if source_id:
            history = [
                entry for entry in history
                if entry['source_id'] == source_id
            ]
            
        return history[-limit:]


# Global MCP client instance
mcp_client = MCPClient()