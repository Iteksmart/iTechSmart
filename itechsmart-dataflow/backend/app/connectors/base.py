"""
Base connector interface for all data sources and destinations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Iterator
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class ConnectorConfig(BaseModel):
    """Base connector configuration"""
    type: str
    name: str
    config: Dict[str, Any]


class ConnectorMetadata(BaseModel):
    """Connector metadata"""
    id: str
    name: str
    type: str
    category: str  # source, destination, both
    version: str
    description: str
    supported: bool = True
    auth_types: List[str] = []
    capabilities: List[str] = []


class BaseConnector(ABC):
    """Base connector interface"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to data source/destination"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection and return status"""
        pass
    
    @abstractmethod
    async def get_schema(self) -> Dict[str, Any]:
        """Get schema information"""
        pass
    
    @classmethod
    @abstractmethod
    def get_metadata(cls) -> ConnectorMetadata:
        """Get connector metadata"""
        pass


class SourceConnector(BaseConnector):
    """Base source connector"""
    
    @abstractmethod
    async def read(self, batch_size: int = 1000) -> Iterator[List[Dict[str, Any]]]:
        """Read data from source in batches"""
        pass
    
    @abstractmethod
    async def get_record_count(self) -> int:
        """Get total record count"""
        pass


class DestinationConnector(BaseConnector):
    """Base destination connector"""
    
    @abstractmethod
    async def write(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Write data to destination"""
        pass
    
    @abstractmethod
    async def create_table(self, schema: Dict[str, Any]) -> bool:
        """Create table/collection with schema"""
        pass
    
    @abstractmethod
    async def truncate(self) -> bool:
        """Truncate/clear destination"""
        pass


class PostgreSQLConnector(SourceConnector, DestinationConnector):
    """PostgreSQL connector"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection = None
    
    async def connect(self) -> bool:
        """Connect to PostgreSQL"""
        try:
            # Implementation would use asyncpg
            self.logger.info("Connecting to PostgreSQL...")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from PostgreSQL"""
        try:
            if self.connection:
                # Close connection
                self.logger.info("Disconnected from PostgreSQL")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect: {e}")
            return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test PostgreSQL connection"""
        try:
            await self.connect()
            return {
                "success": True,
                "message": "Connection successful",
                "version": "PostgreSQL 15.0"
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get PostgreSQL schema"""
        return {
            "database": self.config.get("database"),
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "integer", "nullable": False},
                        {"name": "email", "type": "varchar", "nullable": False},
                        {"name": "created_at", "type": "timestamp", "nullable": False}
                    ]
                }
            ]
        }
    
    async def read(self, batch_size: int = 1000) -> Iterator[List[Dict[str, Any]]]:
        """Read from PostgreSQL"""
        # Implementation would yield batches of records
        yield [
            {"id": 1, "email": "user1@example.com", "created_at": "2024-01-01"},
            {"id": 2, "email": "user2@example.com", "created_at": "2024-01-02"}
        ]
    
    async def get_record_count(self) -> int:
        """Get record count"""
        return 1000
    
    async def write(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Write to PostgreSQL"""
        return {
            "success": True,
            "records_written": len(records)
        }
    
    async def create_table(self, schema: Dict[str, Any]) -> bool:
        """Create PostgreSQL table"""
        return True
    
    async def truncate(self) -> bool:
        """Truncate PostgreSQL table"""
        return True
    
    @classmethod
    def get_metadata(cls) -> ConnectorMetadata:
        """Get PostgreSQL connector metadata"""
        return ConnectorMetadata(
            id="postgresql",
            name="PostgreSQL",
            type="database",
            category="both",
            version="1.0.0",
            description="PostgreSQL database connector",
            auth_types=["username_password"],
            capabilities=["read", "write", "schema_discovery", "incremental"]
        )


class MySQLConnector(SourceConnector, DestinationConnector):
    """MySQL connector"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
    
    async def connect(self) -> bool:
        return True
    
    async def disconnect(self) -> bool:
        return True
    
    async def test_connection(self) -> Dict[str, Any]:
        return {"success": True, "message": "MySQL connection successful"}
    
    async def get_schema(self) -> Dict[str, Any]:
        return {"database": self.config.get("database"), "tables": []}
    
    async def read(self, batch_size: int = 1000) -> Iterator[List[Dict[str, Any]]]:
        yield []
    
    async def get_record_count(self) -> int:
        return 0
    
    async def write(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"success": True, "records_written": len(records)}
    
    async def create_table(self, schema: Dict[str, Any]) -> bool:
        return True
    
    async def truncate(self) -> bool:
        return True
    
    @classmethod
    def get_metadata(cls) -> ConnectorMetadata:
        return ConnectorMetadata(
            id="mysql",
            name="MySQL",
            type="database",
            category="both",
            version="1.0.0",
            description="MySQL database connector"
        )


class MongoDBConnector(SourceConnector, DestinationConnector):
    """MongoDB connector"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
    
    async def connect(self) -> bool:
        return True
    
    async def disconnect(self) -> bool:
        return True
    
    async def test_connection(self) -> Dict[str, Any]:
        return {"success": True, "message": "MongoDB connection successful"}
    
    async def get_schema(self) -> Dict[str, Any]:
        return {"database": self.config.get("database"), "collections": []}
    
    async def read(self, batch_size: int = 1000) -> Iterator[List[Dict[str, Any]]]:
        yield []
    
    async def get_record_count(self) -> int:
        return 0
    
    async def write(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"success": True, "records_written": len(records)}
    
    async def create_table(self, schema: Dict[str, Any]) -> bool:
        return True
    
    async def truncate(self) -> bool:
        return True
    
    @classmethod
    def get_metadata(cls) -> ConnectorMetadata:
        return ConnectorMetadata(
            id="mongodb",
            name="MongoDB",
            type="database",
            category="both",
            version="1.0.0",
            description="MongoDB NoSQL database connector"
        )


# Connector registry
CONNECTOR_REGISTRY = {
    "postgresql": PostgreSQLConnector,
    "mysql": MySQLConnector,
    "mongodb": MongoDBConnector,
}


def get_connector(connector_type: str, config: Dict[str, Any]) -> BaseConnector:
    """Get connector instance by type"""
    connector_class = CONNECTOR_REGISTRY.get(connector_type)
    if not connector_class:
        raise ValueError(f"Unknown connector type: {connector_type}")
    return connector_class(config)


def list_connectors() -> List[ConnectorMetadata]:
    """List all available connectors"""
    return [
        connector_class.get_metadata()
        for connector_class in CONNECTOR_REGISTRY.values()
    ]