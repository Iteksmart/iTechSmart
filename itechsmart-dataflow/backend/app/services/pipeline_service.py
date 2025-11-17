"""
Pipeline service for managing data pipelines
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
from ..models.pipeline import (
    Pipeline,
    PipelineRun,
    PipelineStatus,
    PipelineType,
    PipelineCreate,
    PipelineUpdate,
    PipelineResponse,
)
from ..connectors.base import get_connector

logger = logging.getLogger(__name__)


class PipelineService:
    """Service for managing pipelines"""

    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.runs: Dict[str, PipelineRun] = {}

    async def create_pipeline(
        self, pipeline_data: PipelineCreate, user_id: str
    ) -> PipelineResponse:
        """Create a new pipeline"""
        pipeline_id = f"pipeline-{uuid.uuid4().hex[:8]}"

        pipeline = Pipeline(
            id=pipeline_id,
            name=pipeline_data.name,
            description=pipeline_data.description,
            type=pipeline_data.type,
            status=PipelineStatus.DRAFT,
            source_type=pipeline_data.source.type,
            source_config=pipeline_data.source.config,
            destination_type=pipeline_data.destination.type,
            destination_config=pipeline_data.destination.config,
            transformations=[t.dict() for t in pipeline_data.transformations],
            schedule=pipeline_data.schedule,
            created_by=user_id,
            retry_enabled=pipeline_data.retry_enabled,
            retry_attempts=pipeline_data.retry_attempts,
            timeout_seconds=pipeline_data.timeout_seconds,
        )

        self.pipelines[pipeline_id] = pipeline

        logger.info(f"Created pipeline: {pipeline_id}")

        return self._to_response(pipeline)

    async def get_pipeline(self, pipeline_id: str) -> Optional[PipelineResponse]:
        """Get pipeline by ID"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
        return self._to_response(pipeline)

    async def list_pipelines(
        self, status: Optional[PipelineStatus] = None, limit: int = 100, offset: int = 0
    ) -> List[PipelineResponse]:
        """List pipelines with optional filtering"""
        pipelines = list(self.pipelines.values())

        if status:
            pipelines = [p for p in pipelines if p.status == status]

        pipelines = pipelines[offset : offset + limit]

        return [self._to_response(p) for p in pipelines]

    async def update_pipeline(
        self, pipeline_id: str, pipeline_data: PipelineUpdate
    ) -> Optional[PipelineResponse]:
        """Update pipeline"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None

        # Update fields
        if pipeline_data.name:
            pipeline.name = pipeline_data.name
        if pipeline_data.description is not None:
            pipeline.description = pipeline_data.description
        if pipeline_data.status:
            pipeline.status = pipeline_data.status
        if pipeline_data.schedule is not None:
            pipeline.schedule = pipeline_data.schedule

        pipeline.updated_at = datetime.utcnow()

        logger.info(f"Updated pipeline: {pipeline_id}")

        return self._to_response(pipeline)

    async def delete_pipeline(self, pipeline_id: str) -> bool:
        """Delete pipeline"""
        if pipeline_id in self.pipelines:
            del self.pipelines[pipeline_id]
            logger.info(f"Deleted pipeline: {pipeline_id}")
            return True
        return False

    async def run_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Execute pipeline"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")

        run_id = f"run-{uuid.uuid4().hex[:8]}"

        run = PipelineRun(
            id=run_id,
            pipeline_id=pipeline_id,
            status=PipelineStatus.RUNNING,
            started_at=datetime.utcnow(),
        )

        self.runs[run_id] = run

        try:
            # Get source connector
            source_connector = get_connector(
                pipeline.source_type, pipeline.source_config
            )

            # Get destination connector
            destination_connector = get_connector(
                pipeline.destination_type, pipeline.destination_config
            )

            # Connect to source
            await source_connector.connect()

            # Connect to destination
            await destination_connector.connect()

            # Read and write data
            records_read = 0
            records_written = 0

            async for batch in source_connector.read(batch_size=1000):
                # Apply transformations
                transformed_batch = await self._apply_transformations(
                    batch, pipeline.transformations
                )

                # Write to destination
                result = await destination_connector.write(transformed_batch)

                records_read += len(batch)
                records_written += result.get("records_written", 0)

            # Disconnect
            await source_connector.disconnect()
            await destination_connector.disconnect()

            # Update run
            run.status = PipelineStatus.COMPLETED
            run.completed_at = datetime.utcnow()
            run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
            run.records_read = records_read
            run.records_written = records_written

            # Update pipeline statistics
            pipeline.last_run_at = run.completed_at
            pipeline.last_success_at = run.completed_at
            pipeline.total_runs += 1
            pipeline.successful_runs += 1
            pipeline.records_processed += records_written

            if pipeline.total_runs > 0:
                pipeline.success_rate = (
                    pipeline.successful_runs / pipeline.total_runs
                ) * 100

            logger.info(f"Pipeline run completed: {run_id}")

            return {
                "run_id": run_id,
                "status": "completed",
                "records_read": records_read,
                "records_written": records_written,
                "duration_seconds": run.duration_seconds,
            }

        except Exception as e:
            logger.error(f"Pipeline run failed: {e}")

            run.status = PipelineStatus.FAILED
            run.completed_at = datetime.utcnow()
            run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
            run.error_message = str(e)

            pipeline.last_run_at = run.completed_at
            pipeline.last_failure_at = run.completed_at
            pipeline.total_runs += 1
            pipeline.failed_runs += 1

            if pipeline.total_runs > 0:
                pipeline.success_rate = (
                    pipeline.successful_runs / pipeline.total_runs
                ) * 100

            return {"run_id": run_id, "status": "failed", "error": str(e)}

    async def _apply_transformations(
        self, records: List[Dict[str, Any]], transformations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply transformations to records"""
        result = records

        for transformation in transformations:
            transform_type = transformation.get("type")
            config = transformation.get("config", {})

            if transform_type == "filter":
                # Apply filter
                result = [r for r in result if self._evaluate_filter(r, config)]

            elif transform_type == "map":
                # Apply field mapping
                fields = config.get("fields", [])
                result = [{k: r.get(k) for k in fields} for r in result]

            elif transform_type == "deduplicate":
                # Remove duplicates
                seen = set()
                unique = []
                key_field = config.get("key_field", "id")
                for r in result:
                    key = r.get(key_field)
                    if key not in seen:
                        seen.add(key)
                        unique.append(r)
                result = unique

        return result

    def _evaluate_filter(self, record: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Evaluate filter condition"""
        # Simple filter evaluation
        field = config.get("field")
        operator = config.get("operator", "eq")
        value = config.get("value")

        record_value = record.get(field)

        if operator == "eq":
            return record_value == value
        elif operator == "ne":
            return record_value != value
        elif operator == "gt":
            return record_value > value
        elif operator == "lt":
            return record_value < value
        elif operator == "contains":
            return value in str(record_value)

        return True

    def _to_response(self, pipeline: Pipeline) -> PipelineResponse:
        """Convert pipeline to response model"""
        return PipelineResponse(
            id=pipeline.id,
            name=pipeline.name,
            description=pipeline.description,
            type=pipeline.type,
            status=pipeline.status,
            source={"type": pipeline.source_type, "config": pipeline.source_config},
            destination={
                "type": pipeline.destination_type,
                "config": pipeline.destination_config,
            },
            transformations=pipeline.transformations,
            schedule=pipeline.schedule,
            created_at=pipeline.created_at,
            updated_at=pipeline.updated_at,
            last_run_at=pipeline.last_run_at,
            total_runs=pipeline.total_runs,
            successful_runs=pipeline.successful_runs,
            failed_runs=pipeline.failed_runs,
            success_rate=pipeline.success_rate,
        )


# Global service instance
pipeline_service = PipelineService()
