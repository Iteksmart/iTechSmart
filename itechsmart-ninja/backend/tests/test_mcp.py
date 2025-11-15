"""
Tests for MCP (Model Context Protocol) Integration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.integrations.mcp_integration import (
    MCPClient,
    PostgreSQLSource,
    MySQLSource,
    MongoDBSource,
    RedisSource,
    RESTAPISource,
    ElasticsearchSource,
    DataSourceType
)


@pytest.fixture
def mcp_client():
    """Create MCP client instance"""
    return MCPClient()


@pytest.mark.asyncio
async def test_register_postgresql_source(mcp_client):
    """Test registering PostgreSQL data source"""
    config = {
        "name": "Test DB",
        "type": DataSourceType.POSTGRESQL,
        "connection_string": "postgresql://user:pass@localhost/testdb"
    }
    
    with patch.object(PostgreSQLSource, 'connect', return_value=True):
        result = await mcp_client.register_source("test_source", config)
        
        assert result["success"] is True
        assert "test_source" in mcp_client.sources


@pytest.mark.asyncio
async def test_register_mysql_source(mcp_client):
    """Test registering MySQL data source"""
    config = {
        "name": "Test MySQL",
        "type": DataSourceType.MYSQL,
        "connection_config": {
            "host": "localhost",
            "user": "root",
            "password": "password",
            "database": "testdb"
        }
    }
    
    with patch.object(MySQLSource, 'connect', return_value=True):
        result = await mcp_client.register_source("mysql_source", config)
        
        assert result["success"] is True
        assert "mysql_source" in mcp_client.sources


@pytest.mark.asyncio
async def test_register_mongodb_source(mcp_client):
    """Test registering MongoDB data source"""
    config = {
        "name": "Test MongoDB",
        "type": DataSourceType.MONGODB,
        "connection_string": "mongodb://localhost:27017/testdb"
    }
    
    with patch.object(MongoDBSource, 'connect', return_value=True):
        result = await mcp_client.register_source("mongo_source", config)
        
        assert result["success"] is True
        assert "mongo_source" in mcp_client.sources


@pytest.mark.asyncio
async def test_register_redis_source(mcp_client):
    """Test registering Redis data source"""
    config = {
        "name": "Test Redis",
        "type": DataSourceType.REDIS,
        "connection_config": {
            "host": "localhost",
            "port": 6379
        }
    }
    
    with patch.object(RedisSource, 'connect', return_value=True):
        result = await mcp_client.register_source("redis_source", config)
        
        assert result["success"] is True
        assert "redis_source" in mcp_client.sources


@pytest.mark.asyncio
async def test_register_rest_api_source(mcp_client):
    """Test registering REST API data source"""
    config = {
        "name": "Test API",
        "type": DataSourceType.REST_API,
        "connection_config": {
            "base_url": "https://api.example.com"
        }
    }
    
    with patch.object(RESTAPISource, 'connect', return_value=True):
        result = await mcp_client.register_source("api_source", config)
        
        assert result["success"] is True
        assert "api_source" in mcp_client.sources


@pytest.mark.asyncio
async def test_unregister_source(mcp_client):
    """Test unregistering data source"""
    config = {
        "name": "Test DB",
        "type": DataSourceType.POSTGRESQL,
        "connection_string": "postgresql://user:pass@localhost/testdb"
    }
    
    with patch.object(PostgreSQLSource, 'connect', return_value=True):
        await mcp_client.register_source("test_source", config)
    
    with patch.object(PostgreSQLSource, 'disconnect', return_value=True):
        result = await mcp_client.unregister_source("test_source")
        
        assert result["success"] is True
        assert "test_source" not in mcp_client.sources


@pytest.mark.asyncio
async def test_query_source_with_cache(mcp_client):
    """Test querying data source with caching"""
    config = {
        "name": "Test DB",
        "type": DataSourceType.POSTGRESQL,
        "connection_string": "postgresql://user:pass@localhost/testdb"
    }
    
    mock_data = [{"id": 1, "name": "Test"}]
    
    with patch.object(PostgreSQLSource, 'connect', return_value=True):
        await mcp_client.register_source("test_source", config)
    
    with patch.object(PostgreSQLSource, 'query', return_value=mock_data):
        # First query - should not be cached
        result1 = await mcp_client.query_source(
            "test_source",
            "SELECT * FROM users",
            use_cache=True
        )
        
        assert result1["success"] is True
        assert result1["cached"] is False
        assert result1["data"] == mock_data
        
        # Second query - should be cached
        result2 = await mcp_client.query_source(
            "test_source",
            "SELECT * FROM users",
            use_cache=True
        )
        
        assert result2["success"] is True
        assert result2["cached"] is True
        assert result2["data"] == mock_data


@pytest.mark.asyncio
async def test_query_source_without_cache(mcp_client):
    """Test querying data source without caching"""
    config = {
        "name": "Test DB",
        "type": DataSourceType.POSTGRESQL,
        "connection_string": "postgresql://user:pass@localhost/testdb"
    }
    
    mock_data = [{"id": 1, "name": "Test"}]
    
    with patch.object(PostgreSQLSource, 'connect', return_value=True):
        await mcp_client.register_source("test_source", config)
    
    with patch.object(PostgreSQLSource, 'query', return_value=mock_data):
        result = await mcp_client.query_source(
            "test_source",
            "SELECT * FROM users",
            use_cache=False
        )
        
        assert result["success"] is True
        assert result["cached"] is False
        assert result["data"] == mock_data


@pytest.mark.asyncio
async def test_get_schema(mcp_client):
    """Test getting data source schema"""
    config = {
        "name": "Test DB",
        "type": DataSourceType.POSTGRESQL,
        "connection_string": "postgresql://user:pass@localhost/testdb"
    }
    
    mock_schema = {
        "users": [
            {"column": "id", "type": "integer"},
            {"column": "name", "type": "varchar"}
        ]
    }
    
    with patch.object(PostgreSQLSource, 'connect', return_value=True):
        await mcp_client.register_source("test_source", config)
    
    with patch.object(PostgreSQLSource, 'get_schema', return_value=mock_schema):
        result = await mcp_client.get_schema("test_source")
        
        assert result["success"] is True
        assert result["schema"] == mock_schema


@pytest.mark.asyncio
async def test_test_source_connection(mcp_client):
    """Test testing data source connection"""
    config = {
        "name": "Test DB",
        "type": DataSourceType.POSTGRESQL,
        "connection_string": "postgresql://user:pass@localhost/testdb"
    }
    
    with patch.object(PostgreSQLSource, 'connect', return_value=True):
        await mcp_client.register_source("test_source", config)
    
    with patch.object(PostgreSQLSource, 'test_connection', return_value={
        "success": True,
        "message": "Connection successful"
    }):
        result = await mcp_client.test_source("test_source")
        
        assert result["success"] is True
        assert "Connection successful" in result["message"]


def test_list_sources(mcp_client):
    """Test listing data sources"""
    # Initially empty
    sources = mcp_client.list_sources()
    assert len(sources) == 0
    
    # Add a source
    config = {
        "name": "Test DB",
        "type": DataSourceType.POSTGRESQL,
        "connection_string": "postgresql://user:pass@localhost/testdb"
    }
    
    with patch.object(PostgreSQLSource, 'connect', return_value=True):
        import asyncio
        asyncio.run(mcp_client.register_source("test_source", config))
    
    sources = mcp_client.list_sources()
    assert len(sources) == 1
    assert sources[0]["id"] == "test_source"
    assert sources[0]["name"] == "Test DB"


def test_cache_stats(mcp_client):
    """Test getting cache statistics"""
    stats = mcp_client.get_cache_stats()
    
    assert "total_entries" in stats
    assert "active_entries" in stats
    assert "expired_entries" in stats
    assert "cache_ttl" in stats


def test_clear_cache(mcp_client):
    """Test clearing cache"""
    # Add some cache entries
    mcp_client.cache["test_key"] = {
        "data": "test",
        "expires": "2099-01-01"
    }
    
    result = mcp_client.clear_cache()
    
    assert result["success"] is True
    assert len(mcp_client.cache) == 0


def test_clear_cache_for_source(mcp_client):
    """Test clearing cache for specific source"""
    # Add cache entries for different sources
    mcp_client.cache["source1:query1"] = {"data": "test1", "expires": "2099-01-01"}
    mcp_client.cache["source2:query1"] = {"data": "test2", "expires": "2099-01-01"}
    
    result = mcp_client.clear_cache("source1")
    
    assert result["success"] is True
    assert "source1:query1" not in mcp_client.cache
    assert "source2:query1" in mcp_client.cache


def test_query_history(mcp_client):
    """Test getting query history"""
    # Add some history entries
    mcp_client.query_history.append({
        "source_id": "test_source",
        "query": "SELECT * FROM users",
        "execution_time": 0.5,
        "timestamp": "2024-01-01T00:00:00",
        "cached": False
    })
    
    history = mcp_client.get_query_history()
    
    assert len(history) == 1
    assert history[0]["source_id"] == "test_source"


def test_query_history_with_source_filter(mcp_client):
    """Test getting query history filtered by source"""
    # Add history entries for different sources
    mcp_client.query_history.append({
        "source_id": "source1",
        "query": "SELECT * FROM users",
        "execution_time": 0.5,
        "timestamp": "2024-01-01T00:00:00",
        "cached": False
    })
    mcp_client.query_history.append({
        "source_id": "source2",
        "query": "SELECT * FROM posts",
        "execution_time": 0.3,
        "timestamp": "2024-01-01T00:00:00",
        "cached": False
    })
    
    history = mcp_client.get_query_history(source_id="source1")
    
    assert len(history) == 1
    assert history[0]["source_id"] == "source1"


@pytest.mark.asyncio
async def test_invalid_source_type(mcp_client):
    """Test registering invalid source type"""
    config = {
        "name": "Invalid Source",
        "type": "invalid_type",
        "connection_string": "invalid://connection"
    }
    
    result = await mcp_client.register_source("invalid_source", config)
    
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_query_nonexistent_source(mcp_client):
    """Test querying non-existent source"""
    result = await mcp_client.query_source(
        "nonexistent_source",
        "SELECT * FROM users"
    )
    
    assert result["success"] is False
    assert "not found" in result["error"].lower()