"""
iTechSmart Analytics - Data Ingestion Layer
Real-time and batch data ingestion from multiple sources
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import asyncio
import json
from enum import Enum
import pandas as pd


class DataSourceType(str, Enum):
    """Supported data source types"""

    REST_API = "rest_api"
    DATABASE = "database"
    KAFKA = "kafka"
    WEBHOOK = "webhook"
    FILE = "file"
    STREAM = "stream"


class IngestionMode(str, Enum):
    """Data ingestion modes"""

    REAL_TIME = "real_time"
    BATCH = "batch"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"


class DataIngestionEngine:
    """Core data ingestion engine for analytics platform"""

    def __init__(self, db: Session):
        self.db = db
        self.active_streams = {}
        self.batch_jobs = {}
        self.transformers = {}
        self.validators = {}

    async def create_data_source(
        self,
        name: str,
        source_type: DataSourceType,
        config: Dict[str, Any],
        ingestion_mode: IngestionMode = IngestionMode.BATCH,
    ) -> Dict[str, Any]:
        """
        Create a new data source

        Args:
            name: Data source name
            source_type: Type of data source
            config: Source configuration
            ingestion_mode: How data should be ingested

        Returns:
            Created data source details
        """

        data_source = {
            "id": self._generate_id(),
            "name": name,
            "type": source_type.value,
            "config": config,
            "ingestion_mode": ingestion_mode.value,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "last_ingestion": None,
            "records_ingested": 0,
        }

        # Validate configuration
        self._validate_source_config(source_type, config)

        # Initialize based on type
        if source_type == DataSourceType.KAFKA:
            await self._init_kafka_source(data_source)
        elif source_type == DataSourceType.REST_API:
            await self._init_api_source(data_source)
        elif source_type == DataSourceType.DATABASE:
            await self._init_database_source(data_source)

        return data_source

    async def ingest_data(
        self, source_id: int, data: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest data from a source

        Args:
            source_id: Data source ID
            data: Data to ingest
            metadata: Optional metadata

        Returns:
            Ingestion result
        """

        start_time = datetime.utcnow()

        try:
            # Transform data
            transformed_data = await self._transform_data(source_id, data)

            # Validate data
            validation_result = await self._validate_data(source_id, transformed_data)

            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Data validation failed",
                    "details": validation_result["errors"],
                }

            # Store data
            stored_records = await self._store_data(
                source_id, transformed_data, metadata
            )

            # Update metrics
            await self._update_ingestion_metrics(source_id, len(stored_records))

            duration = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "source_id": source_id,
                "records_ingested": len(stored_records),
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def start_real_time_ingestion(self, source_id: int) -> Dict[str, Any]:
        """
        Start real-time data ingestion

        Args:
            source_id: Data source ID

        Returns:
            Stream status
        """

        if source_id in self.active_streams:
            return {
                "status": "already_running",
                "message": f"Real-time ingestion already active for source {source_id}",
            }

        # Start ingestion stream
        stream_task = asyncio.create_task(self._real_time_ingestion_loop(source_id))

        self.active_streams[source_id] = {
            "task": stream_task,
            "started_at": datetime.utcnow().isoformat(),
            "records_processed": 0,
        }

        return {
            "status": "started",
            "source_id": source_id,
            "started_at": datetime.utcnow().isoformat(),
        }

    async def stop_real_time_ingestion(self, source_id: int) -> Dict[str, Any]:
        """
        Stop real-time data ingestion

        Args:
            source_id: Data source ID

        Returns:
            Stop status
        """

        if source_id not in self.active_streams:
            return {
                "status": "not_running",
                "message": f"No active ingestion for source {source_id}",
            }

        # Cancel the stream task
        stream_info = self.active_streams[source_id]
        stream_info["task"].cancel()

        del self.active_streams[source_id]

        return {
            "status": "stopped",
            "source_id": source_id,
            "records_processed": stream_info["records_processed"],
            "stopped_at": datetime.utcnow().isoformat(),
        }

    async def schedule_batch_ingestion(
        self, source_id: int, schedule: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schedule batch data ingestion

        Args:
            source_id: Data source ID
            schedule: Cron-like schedule string
            config: Optional batch configuration

        Returns:
            Scheduled job details
        """

        job = {
            "id": self._generate_id(),
            "source_id": source_id,
            "schedule": schedule,
            "config": config or {},
            "status": "scheduled",
            "next_run": self._calculate_next_run(schedule),
            "created_at": datetime.utcnow().isoformat(),
        }

        self.batch_jobs[job["id"]] = job

        return job

    async def run_batch_ingestion(
        self, source_id: int, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run batch data ingestion immediately

        Args:
            source_id: Data source ID
            config: Optional batch configuration

        Returns:
            Batch ingestion result
        """

        start_time = datetime.utcnow()

        try:
            # Fetch data from source
            data = await self._fetch_batch_data(source_id, config)

            # Ingest data
            result = await self.ingest_data(source_id, data)

            duration = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": result["success"],
                "source_id": source_id,
                "records_ingested": result.get("records_ingested", 0),
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def register_transformer(self, source_id: int, transformer: Callable):
        """
        Register data transformer for a source

        Args:
            source_id: Data source ID
            transformer: Transformation function
        """
        self.transformers[source_id] = transformer

    def register_validator(self, source_id: int, validator: Callable):
        """
        Register data validator for a source

        Args:
            source_id: Data source ID
            validator: Validation function
        """
        self.validators[source_id] = validator

    async def get_ingestion_stats(
        self, source_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get ingestion statistics

        Args:
            source_id: Optional source ID filter

        Returns:
            Ingestion statistics
        """

        stats = {
            "total_sources": len(self.active_streams) + len(self.batch_jobs),
            "active_streams": len(self.active_streams),
            "scheduled_jobs": len(self.batch_jobs),
            "timestamp": datetime.utcnow().isoformat(),
        }

        if source_id:
            # Get specific source stats
            if source_id in self.active_streams:
                stats["source"] = self.active_streams[source_id]

        return stats

    # Private helper methods

    async def _real_time_ingestion_loop(self, source_id: int):
        """Real-time ingestion loop"""

        while True:
            try:
                # Fetch data from source
                data = await self._fetch_real_time_data(source_id)

                if data:
                    # Ingest data
                    result = await self.ingest_data(source_id, data)

                    if result["success"]:
                        self.active_streams[source_id]["records_processed"] += result[
                            "records_ingested"
                        ]

                # Wait before next fetch
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in real-time ingestion: {str(e)}")
                await asyncio.sleep(5)

    async def _transform_data(self, source_id: int, data: Any) -> Any:
        """Transform data using registered transformer"""

        if source_id in self.transformers:
            return await self.transformers[source_id](data)

        return data

    async def _validate_data(self, source_id: int, data: Any) -> Dict[str, Any]:
        """Validate data using registered validator"""

        if source_id in self.validators:
            return await self.validators[source_id](data)

        return {"valid": True, "errors": []}

    async def _store_data(
        self, source_id: int, data: Any, metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Store ingested data"""

        # Convert to list of records
        if isinstance(data, pd.DataFrame):
            records = data.to_dict("records")
        elif isinstance(data, list):
            records = data
        else:
            records = [data]

        # Add metadata
        for record in records:
            record["_source_id"] = source_id
            record["_ingested_at"] = datetime.utcnow().isoformat()
            if metadata:
                record["_metadata"] = metadata

        # In production, store in database
        # For now, just return the records

        return records

    async def _update_ingestion_metrics(self, source_id: int, record_count: int):
        """Update ingestion metrics"""

        # In production, update database
        pass

    async def _fetch_real_time_data(self, source_id: int) -> Any:
        """Fetch data for real-time ingestion"""

        # In production, fetch from actual source
        # For now, return mock data
        return None

    async def _fetch_batch_data(
        self, source_id: int, config: Optional[Dict[str, Any]]
    ) -> Any:
        """Fetch data for batch ingestion"""

        # In production, fetch from actual source
        # For now, return mock data
        return []

    def _validate_source_config(
        self, source_type: DataSourceType, config: Dict[str, Any]
    ):
        """Validate source configuration"""

        required_fields = {
            DataSourceType.REST_API: ["url", "method"],
            DataSourceType.DATABASE: ["connection_string", "query"],
            DataSourceType.KAFKA: ["brokers", "topic"],
            DataSourceType.WEBHOOK: ["endpoint"],
            DataSourceType.FILE: ["path", "format"],
        }

        if source_type in required_fields:
            for field in required_fields[source_type]:
                if field not in config:
                    raise ValueError(f"Missing required field: {field}")

    async def _init_kafka_source(self, data_source: Dict[str, Any]):
        """Initialize Kafka data source"""
        # In production, set up Kafka consumer
        pass

    async def _init_api_source(self, data_source: Dict[str, Any]):
        """Initialize REST API data source"""
        # In production, set up API client
        pass

    async def _init_database_source(self, data_source: Dict[str, Any]):
        """Initialize database data source"""
        # In production, set up database connection
        pass

    def _calculate_next_run(self, schedule: str) -> str:
        """Calculate next run time from schedule"""
        # Simplified - in production, use proper cron parser
        return (datetime.utcnow() + timedelta(hours=1)).isoformat()

    def _generate_id(self) -> int:
        """Generate unique ID"""
        import random

        return random.randint(1000, 9999)
