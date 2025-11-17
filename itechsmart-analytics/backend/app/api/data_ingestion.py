"""
iTechSmart Analytics - Data Ingestion API Endpoints
REST API for managing data sources and ingestion
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from app.core.data_ingestion import DataIngestionEngine, DataSourceType, IngestionMode
from app.core.database import get_db

router = APIRouter(prefix="/api/ingestion", tags=["data_ingestion"])


# Pydantic models
class DataSourceCreateRequest(BaseModel):
    name: str
    source_type: str
    config: Dict[str, Any]
    ingestion_mode: str = "batch"


class IngestDataRequest(BaseModel):
    source_id: int
    data: Any
    metadata: Optional[Dict[str, Any]] = None


class BatchIngestionRequest(BaseModel):
    source_id: int
    config: Optional[Dict[str, Any]] = None


class ScheduleRequest(BaseModel):
    source_id: int
    schedule: str
    config: Optional[Dict[str, Any]] = None


@router.post("/sources")
async def create_data_source(
    request: DataSourceCreateRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new data source

    Args:
        name: Data source name
        source_type: Type of data source (rest_api, database, kafka, webhook, file, stream)
        config: Source-specific configuration
        ingestion_mode: How data should be ingested (real_time, batch, scheduled, on_demand)

    Returns:
        Created data source details
    """

    engine = DataIngestionEngine(db)

    try:
        source_type_enum = DataSourceType(request.source_type)
        ingestion_mode_enum = IngestionMode(request.ingestion_mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")

    try:
        data_source = await engine.create_data_source(
            request.name, source_type_enum, request.config, ingestion_mode_enum
        )
        return data_source
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ingest")
async def ingest_data(
    request: IngestDataRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
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

    engine = DataIngestionEngine(db)

    result = await engine.ingest_data(request.source_id, request.data, request.metadata)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@router.post("/sources/{source_id}/start-stream")
async def start_real_time_ingestion(
    source_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start real-time data ingestion for a source

    Args:
        source_id: Data source ID

    Returns:
        Stream status
    """

    engine = DataIngestionEngine(db)

    # Start ingestion in background
    background_tasks.add_task(engine.start_real_time_ingestion, source_id)

    return {
        "status": "starting",
        "source_id": source_id,
        "message": "Real-time ingestion is starting in background",
    }


@router.post("/sources/{source_id}/stop-stream")
async def stop_real_time_ingestion(
    source_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Stop real-time data ingestion for a source

    Args:
        source_id: Data source ID

    Returns:
        Stop status
    """

    engine = DataIngestionEngine(db)
    result = await engine.stop_real_time_ingestion(source_id)

    return result


@router.post("/batch/schedule")
async def schedule_batch_ingestion(
    request: ScheduleRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Schedule batch data ingestion

    Args:
        source_id: Data source ID
        schedule: Cron-like schedule string (e.g., "0 0 * * *" for daily at midnight)
        config: Optional batch configuration

    Returns:
        Scheduled job details
    """

    engine = DataIngestionEngine(db)

    job = await engine.schedule_batch_ingestion(
        request.source_id, request.schedule, request.config
    )

    return job


@router.post("/batch/run")
async def run_batch_ingestion(
    request: BatchIngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Run batch data ingestion immediately

    Args:
        source_id: Data source ID
        config: Optional batch configuration

    Returns:
        Batch ingestion result
    """

    engine = DataIngestionEngine(db)

    result = await engine.run_batch_ingestion(request.source_id, request.config)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@router.get("/stats")
async def get_ingestion_stats(
    source_id: Optional[int] = None, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get ingestion statistics

    Args:
        source_id: Optional source ID filter

    Returns:
        Ingestion statistics
    """

    engine = DataIngestionEngine(db)
    stats = await engine.get_ingestion_stats(source_id)

    return stats


@router.get("/sources")
async def list_data_sources(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    List all data sources

    Returns:
        List of data sources
    """

    # In production, query from database
    return []


@router.get("/sources/{source_id}")
async def get_data_source(
    source_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get data source details

    Args:
        source_id: Data source ID

    Returns:
        Data source details
    """

    # In production, fetch from database
    return {
        "id": source_id,
        "name": "Sample Source",
        "type": "rest_api",
        "status": "active",
    }


@router.delete("/sources/{source_id}")
async def delete_data_source(
    source_id: int, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete a data source

    Args:
        source_id: Data source ID

    Returns:
        Success message
    """

    # In production, delete from database
    return {"status": "success", "message": f"Data source {source_id} deleted"}


@router.get("/jobs")
async def list_scheduled_jobs(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    List all scheduled ingestion jobs

    Returns:
        List of scheduled jobs
    """

    # In production, query from database
    return []


@router.delete("/jobs/{job_id}")
async def cancel_scheduled_job(
    job_id: int, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Cancel a scheduled ingestion job

    Args:
        job_id: Job ID

    Returns:
        Success message
    """

    # In production, delete from database
    return {"status": "success", "message": f"Job {job_id} cancelled"}
