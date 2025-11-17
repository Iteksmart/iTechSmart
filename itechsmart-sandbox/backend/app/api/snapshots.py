"""
iTechSmart Sandbox - Snapshot API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.sandbox_engine import SandboxEngine

router = APIRouter(prefix="/api/snapshots", tags=["Snapshots"])


class SnapshotCreate(BaseModel):
    sandbox_id: str
    name: str
    description: Optional[str] = None


class SnapshotRestore(BaseModel):
    snapshot_id: str


@router.post("/")
def create_snapshot(snapshot: SnapshotCreate, db: Session = Depends(get_db)):
    """Create sandbox snapshot"""
    engine = SandboxEngine(db)

    try:
        snap = engine.create_snapshot(
            snapshot.sandbox_id, snapshot.name, snapshot.description
        )
        return {
            "snapshot_id": snap.snapshot_id,
            "name": snap.name,
            "status": snap.status,
            "message": "Snapshot created successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{sandbox_id}/restore")
def restore_snapshot(
    sandbox_id: str, restore: SnapshotRestore, db: Session = Depends(get_db)
):
    """Restore sandbox from snapshot"""
    engine = SandboxEngine(db)

    try:
        success = engine.restore_snapshot(sandbox_id, restore.snapshot_id)
        return {"success": success, "message": "Snapshot restored successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
