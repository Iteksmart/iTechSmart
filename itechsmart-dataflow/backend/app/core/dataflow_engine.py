"""
iTechSmart DataFlow - Data Pipeline & ETL Engine
Real-time data streaming, ETL pipelines, and data quality validation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4
import json


class PipelineStatus(str, Enum):
    """Pipeline execution status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class DataSourceType(str, Enum):
    """Supported data source types"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    WEBHOOK = "webhook"
    CLOUD_STORAGE = "cloud_storage"


class TransformationType(str, Enum):
    """Data transformation types"""
    MAP = "map"
    FILTER = "filter"
    AGGREGATE = "aggregate"
    JOIN = "join"
    SPLIT = "split"
    MERGE = "merge"
    ENRICH = "enrich"
    VALIDATE = "validate"


class DataSource:
    """Represents a data source"""
    
    def __init__(
        self,
        source_id: str,
        name: str,
        source_type: DataSourceType,
        config: Dict[str, Any]
    ):
        self.source_id = source_id
        self.name = name
        self.source_type = source_type
        self.config = config
        self.is_active = True
        self.schema = {}
        self.last_sync = None
        self.records_processed = 0
        self.created_at = datetime.utcnow()


class Transformation:
    """Represents a data transformation"""
    
    def __init__(
        self,
        transform_id: str,
        transform_type: TransformationType,
        config: Dict[str, Any]
    ):
        self.transform_id = transform_id
        self.transform_type = transform_type
        self.config = config
        self.is_active = True


class DataPipeline:
    """Represents a data pipeline"""
    
    def __init__(
        self,
        pipeline_id: str,
        name: str,
        source_id: str,
        target_id: str
    ):
        self.pipeline_id = pipeline_id
        self.name = name
        self.source_id = source_id
        self.target_id = target_id
        self.transformations: List[Transformation] = []
        self.status = PipelineStatus.DRAFT
        self.schedule = None
        self.is_realtime = False
        self.quality_rules = []
        self.lineage = []
        self.created_at = datetime.utcnow()
        self.last_run = None
        self.records_processed = 0
        self.errors = []
        self.self_healing_enabled = True


class DataQualityRule:
    """Data quality validation rule"""
    
    def __init__(
        self,
        rule_id: str,
        rule_type: str,
        condition: str,
        severity: str
    ):
        self.rule_id = rule_id
        self.rule_type = rule_type  # completeness, accuracy, consistency, timeliness
        self.condition = condition
        self.severity = severity  # critical, high, medium, low
        self.violations = 0
        self.is_active = True


class DataFlowEngine:
    """Main DataFlow engine for ETL and streaming"""
    
    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        self.pipelines: Dict[str, DataPipeline] = {}
        self.quality_rules: Dict[str, DataQualityRule] = {}
        self.connectors = self._initialize_connectors()
    
    def _initialize_connectors(self) -> Dict[str, Dict[str, Any]]:
        """Initialize 100+ data source connectors"""
        connectors = {}
        
        # Databases (20+)
        databases = [
            "PostgreSQL", "MySQL", "MongoDB", "Oracle", "SQL Server",
            "MariaDB", "Cassandra", "Redis", "Elasticsearch", "DynamoDB",
            "Snowflake", "BigQuery", "Redshift", "Databricks", "ClickHouse",
            "CockroachDB", "TimescaleDB", "InfluxDB", "Neo4j", "Couchbase"
        ]
        
        # Cloud Storage (10+)
        cloud_storage = [
            "AWS S3", "Azure Blob", "Google Cloud Storage", "Dropbox",
            "Box", "OneDrive", "Google Drive", "MinIO", "Wasabi", "Backblaze"
        ]
        
        # SaaS Applications (30+)
        saas = [
            "Salesforce", "HubSpot", "Zendesk", "Intercom", "Stripe",
            "Shopify", "WooCommerce", "Magento", "QuickBooks", "Xero",
            "Slack", "Microsoft Teams", "Google Workspace", "Office 365",
            "Jira", "Asana", "Trello", "Monday.com", "ClickUp", "Notion",
            "Mailchimp", "SendGrid", "Twilio", "Zoom", "GitHub",
            "GitLab", "Bitbucket", "Jenkins", "CircleCI", "Travis CI"
        ]
        
        # Marketing & Analytics (15+)
        marketing = [
            "Google Analytics", "Adobe Analytics", "Mixpanel", "Amplitude",
            "Segment", "Facebook Ads", "Google Ads", "LinkedIn Ads",
            "Twitter Ads", "Instagram", "TikTok", "Snapchat", "Pinterest",
            "Mailchimp", "Constant Contact"
        ]
        
        # Data Warehouses (10+)
        warehouses = [
            "Snowflake", "BigQuery", "Redshift", "Azure Synapse",
            "Databricks", "Teradata", "Vertica", "Greenplum",
            "Amazon Athena", "Presto"
        ]
        
        # Streaming (10+)
        streaming = [
            "Apache Kafka", "Amazon Kinesis", "Azure Event Hubs",
            "Google Pub/Sub", "RabbitMQ", "Apache Pulsar", "NATS",
            "Redis Streams", "AWS SQS", "Azure Service Bus"
        ]
        
        # Files (5+)
        files = ["CSV", "JSON", "XML", "Parquet", "Avro", "ORC", "Excel"]
        
        # APIs (10+)
        apis = [
            "REST API", "GraphQL", "SOAP", "gRPC", "WebSocket",
            "Webhook", "FTP", "SFTP", "HTTP", "HTTPS"
        ]
        
        # Combine all connectors
        all_connectors = (
            databases + cloud_storage + saas + marketing +
            warehouses + streaming + files + apis
        )
        
        for connector in all_connectors:
            connectors[connector.lower().replace(" ", "_")] = {
                "name": connector,
                "type": self._get_connector_type(connector),
                "supported": True,
                "config_required": ["connection_string", "credentials"]
            }
        
        return connectors
    
    def _get_connector_type(self, connector: str) -> str:
        """Determine connector type"""
        if any(db in connector for db in ["SQL", "Mongo", "Redis", "Elastic"]):
            return "database"
        elif any(cloud in connector for cloud in ["S3", "Azure", "Google Cloud", "Drive"]):
            return "cloud_storage"
        elif any(stream in connector for stream in ["Kafka", "Kinesis", "Pub/Sub"]):
            return "stream"
        elif connector in ["CSV", "JSON", "XML", "Parquet", "Avro"]:
            return "file"
        else:
            return "api"
    
    # Data Source Management
    def create_source(
        self,
        name: str,
        source_type: DataSourceType,
        config: Dict[str, Any]
    ) -> str:
        """Create a data source"""
        source_id = str(uuid4())
        
        source = DataSource(
            source_id=source_id,
            name=name,
            source_type=source_type,
            config=config
        )
        
        self.sources[source_id] = source
        return source_id
    
    def get_source(self, source_id: str) -> Optional[DataSource]:
        """Get data source"""
        return self.sources.get(source_id)
    
    def list_sources(
        self,
        source_type: Optional[DataSourceType] = None
    ) -> List[Dict[str, Any]]:
        """List all data sources"""
        sources = list(self.sources.values())
        
        if source_type:
            sources = [s for s in sources if s.source_type == source_type]
        
        return [
            {
                "source_id": s.source_id,
                "name": s.name,
                "type": s.source_type.value,
                "is_active": s.is_active,
                "records_processed": s.records_processed,
                "last_sync": s.last_sync.isoformat() if s.last_sync else None
            }
            for s in sources
        ]
    
    def test_connection(self, source_id: str) -> Dict[str, Any]:
        """Test data source connection"""
        source = self.sources.get(source_id)
        if not source:
            return {"success": False, "error": "Source not found"}
        
        # Simulate connection test
        return {
            "success": True,
            "source_id": source_id,
            "latency_ms": 45,
            "message": "Connection successful"
        }
    
    # Pipeline Management
    def create_pipeline(
        self,
        name: str,
        source_id: str,
        target_id: str,
        is_realtime: bool = False
    ) -> str:
        """Create a data pipeline"""
        pipeline_id = str(uuid4())
        
        pipeline = DataPipeline(
            pipeline_id=pipeline_id,
            name=name,
            source_id=source_id,
            target_id=target_id
        )
        pipeline.is_realtime = is_realtime
        
        self.pipelines[pipeline_id] = pipeline
        return pipeline_id
    
    def add_transformation(
        self,
        pipeline_id: str,
        transform_type: TransformationType,
        config: Dict[str, Any]
    ) -> str:
        """Add transformation to pipeline"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        transform_id = str(uuid4())
        transformation = Transformation(
            transform_id=transform_id,
            transform_type=transform_type,
            config=config
        )
        
        pipeline.transformations.append(transformation)
        return transform_id
    
    def add_quality_rule(
        self,
        pipeline_id: str,
        rule_type: str,
        condition: str,
        severity: str
    ) -> str:
        """Add data quality rule to pipeline"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        rule_id = str(uuid4())
        rule = DataQualityRule(
            rule_id=rule_id,
            rule_type=rule_type,
            condition=condition,
            severity=severity
        )
        
        self.quality_rules[rule_id] = rule
        pipeline.quality_rules.append(rule_id)
        return rule_id
    
    def run_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Execute a pipeline"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        pipeline.status = PipelineStatus.RUNNING
        pipeline.last_run = datetime.utcnow()
        
        # Simulate pipeline execution
        try:
            # Extract
            source = self.sources.get(pipeline.source_id)
            if not source:
                raise ValueError("Source not found")
            
            records_extracted = 1000  # Simulated
            
            # Transform
            records_transformed = records_extracted
            for transform in pipeline.transformations:
                # Apply transformation
                if transform.transform_type == TransformationType.FILTER:
                    records_transformed = int(records_transformed * 0.8)
            
            # Validate
            quality_passed = True
            for rule_id in pipeline.quality_rules:
                rule = self.quality_rules.get(rule_id)
                if rule and rule.is_active:
                    # Simulate quality check
                    if rule.severity == "critical":
                        quality_passed = True  # Simulated pass
            
            # Load
            if quality_passed:
                target = self.sources.get(pipeline.target_id)
                if target:
                    target.records_processed += records_transformed
                
                pipeline.records_processed += records_transformed
                pipeline.status = PipelineStatus.COMPLETED
                
                # Update lineage
                pipeline.lineage.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "records": records_transformed,
                    "status": "success"
                })
                
                return {
                    "pipeline_id": pipeline_id,
                    "status": "completed",
                    "records_extracted": records_extracted,
                    "records_transformed": records_transformed,
                    "records_loaded": records_transformed,
                    "duration_seconds": 12.5,
                    "quality_passed": quality_passed
                }
            else:
                pipeline.status = PipelineStatus.FAILED
                return {
                    "pipeline_id": pipeline_id,
                    "status": "failed",
                    "error": "Data quality validation failed"
                }
                
        except Exception as e:
            pipeline.status = PipelineStatus.FAILED
            pipeline.errors.append({
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            })
            
            # Self-healing: Try to fix the issue
            if pipeline.self_healing_enabled:
                self._self_heal_pipeline(pipeline_id, str(e))
            
            return {
                "pipeline_id": pipeline_id,
                "status": "failed",
                "error": str(e),
                "self_healing_attempted": pipeline.self_healing_enabled
            }
    
    def _self_heal_pipeline(self, pipeline_id: str, error: str):
        """Self-healing pipeline using Ninja integration"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return
        
        # Simulate self-healing actions
        healing_actions = []
        
        if "connection" in error.lower():
            healing_actions.append("Reconnecting to data source")
            # Attempt reconnection
        
        if "timeout" in error.lower():
            healing_actions.append("Increasing timeout settings")
            # Adjust timeout
        
        if "memory" in error.lower():
            healing_actions.append("Optimizing memory usage")
            # Optimize batch size
        
        pipeline.errors[-1]["healing_actions"] = healing_actions
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline status"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return {}
        
        return {
            "pipeline_id": pipeline.pipeline_id,
            "name": pipeline.name,
            "status": pipeline.status.value,
            "is_realtime": pipeline.is_realtime,
            "records_processed": pipeline.records_processed,
            "last_run": pipeline.last_run.isoformat() if pipeline.last_run else None,
            "transformations_count": len(pipeline.transformations),
            "quality_rules_count": len(pipeline.quality_rules),
            "errors_count": len(pipeline.errors)
        }
    
    def get_data_lineage(self, pipeline_id: str) -> Dict[str, Any]:
        """Get data lineage for pipeline"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return {}
        
        source = self.sources.get(pipeline.source_id)
        target = self.sources.get(pipeline.target_id)
        
        return {
            "pipeline_id": pipeline_id,
            "source": {
                "id": source.source_id if source else None,
                "name": source.name if source else None,
                "type": source.source_type.value if source else None
            },
            "target": {
                "id": target.source_id if target else None,
                "name": target.name if target else None,
                "type": target.source_type.value if target else None
            },
            "transformations": [
                {
                    "type": t.transform_type.value,
                    "config": t.config
                }
                for t in pipeline.transformations
            ],
            "lineage_history": pipeline.lineage
        }
    
    def get_connectors(self) -> List[Dict[str, Any]]:
        """Get list of available connectors"""
        return [
            {
                "id": key,
                "name": value["name"],
                "type": value["type"],
                "supported": value["supported"]
            }
            for key, value in self.connectors.items()
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get DataFlow statistics"""
        total_pipelines = len(self.pipelines)
        running = len([p for p in self.pipelines.values() if p.status == PipelineStatus.RUNNING])
        completed = len([p for p in self.pipelines.values() if p.status == PipelineStatus.COMPLETED])
        failed = len([p for p in self.pipelines.values() if p.status == PipelineStatus.FAILED])
        
        total_records = sum(p.records_processed for p in self.pipelines.values())
        
        return {
            "total_sources": len(self.sources),
            "total_pipelines": total_pipelines,
            "running_pipelines": running,
            "completed_pipelines": completed,
            "failed_pipelines": failed,
            "total_records_processed": total_records,
            "available_connectors": len(self.connectors),
            "realtime_pipelines": len([p for p in self.pipelines.values() if p.is_realtime])
        }


# Global DataFlow engine instance
dataflow_engine = DataFlowEngine()