"""
Disaster Recovery API Endpoints
Provides backup, restore, and failover management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.database import get_db
from app.core.disaster_recovery import (
    DisasterRecoveryManager,
    FailoverManager,
    BackupType,
    RecoveryStatus,
)

router = APIRouter(prefix="/api/disaster-recovery", tags=["Disaster Recovery"])

# Initialize disaster recovery components
dr_config = {
    "backup_dir": "/backups",
    "db_host": "localhost",
    "db_user": "postgres",
    "s3_bucket": "itechsmart-hl7-backups",
    "retention_days": 30,
    "primary_endpoint": "http://primary.itechsmart.dev",
    "standby_endpoints": [
        "http://standby1.itechsmart.dev",
        "http://standby2.itechsmart.dev",
    ],
}

dr_manager = DisasterRecoveryManager(dr_config)
failover_manager = FailoverManager(dr_config)


@router.post("/backup/create")
async def create_backup(
    background_tasks: BackgroundTasks,
    backup_type: str = "full",
    databases: Optional[List[str]] = None,
):
    """Create a new backup"""
    try:
        # Validate backup type
        try:
            backup_type_enum = BackupType[backup_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid backup type. Must be one of: {[t.value for t in BackupType]}",
            )

        # Create backup in background
        backup_info = await dr_manager.create_backup(
            backup_type=backup_type_enum, databases=databases
        )

        return {
            "success": True,
            "message": "Backup created successfully",
            "data": backup_info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")


@router.get("/backup/list")
async def list_backups():
    """Get list of all available backups"""
    try:
        backups = dr_manager.get_backup_list()

        return {"success": True, "count": len(backups), "data": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")


@router.post("/backup/verify/{backup_id}")
async def verify_backup(backup_id: str):
    """Verify backup integrity and restorability"""
    try:
        verification = await dr_manager.verify_backup(backup_id)

        return {
            "success": verification["status"] == RecoveryStatus.VERIFIED.value,
            "data": verification,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Backup verification failed: {str(e)}"
        )


@router.post("/backup/restore/{backup_id}")
async def restore_backup(backup_id: str, target_database: Optional[str] = None):
    """Restore from a backup"""
    try:
        restore_info = await dr_manager.restore_backup(
            backup_id=backup_id, target_database=target_database
        )

        return {
            "success": restore_info["status"] == RecoveryStatus.COMPLETED.value,
            "message": (
                "Restore completed successfully"
                if restore_info["status"] == RecoveryStatus.COMPLETED.value
                else "Restore failed"
            ),
            "data": restore_info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.post("/backup/cleanup")
async def cleanup_old_backups():
    """Remove backups older than retention period"""
    try:
        cleanup_info = await dr_manager.cleanup_old_backups()

        return {
            "success": True,
            "message": f"Removed {len(cleanup_info['removed'])} old backups",
            "data": cleanup_info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.post("/failover/initiate")
async def initiate_failover():
    """Initiate failover to standby system"""
    try:
        failover_info = await failover_manager.initiate_failover()

        return {
            "success": failover_info["status"] == RecoveryStatus.COMPLETED.value,
            "message": (
                "Failover completed successfully"
                if failover_info["status"] == RecoveryStatus.COMPLETED.value
                else "Failover failed"
            ),
            "data": failover_info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failover failed: {str(e)}")


@router.get("/failover/status")
async def get_failover_status():
    """Get current failover status"""
    try:
        return {
            "success": True,
            "data": {
                "current_active": failover_manager.get_current_active(),
                "primary_endpoint": dr_config["primary_endpoint"],
                "standby_endpoints": dr_config["standby_endpoints"],
                "failover_history": failover_manager.get_failover_history(),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get failover status: {str(e)}"
        )


@router.get("/health-check")
async def dr_health_check():
    """Comprehensive disaster recovery health check"""
    try:
        backups = dr_manager.get_backup_list()

        # Check if we have recent backups
        recent_backup = None
        if backups:
            recent_backup = backups[0]
            backup_age_hours = (
                datetime.utcnow() - datetime.fromisoformat(recent_backup["timestamp"])
            ).total_seconds() / 3600
        else:
            backup_age_hours = None

        # Determine health status
        warnings = []
        if not backups:
            warnings.append("No backups available")
        elif backup_age_hours and backup_age_hours > 24:
            warnings.append(f"Most recent backup is {backup_age_hours:.1f} hours old")

        # Check standby health
        standby_health = {}
        for standby in dr_config["standby_endpoints"]:
            standby_health[standby] = await failover_manager.check_health(standby)

        healthy_standbys = sum(1 for h in standby_health.values() if h)
        if healthy_standbys == 0:
            warnings.append("No healthy standby systems available")

        overall_status = "healthy" if not warnings else "warning"

        return {
            "success": True,
            "status": overall_status,
            "warnings": warnings,
            "backup_status": {
                "total_backups": len(backups),
                "most_recent": recent_backup["timestamp"] if recent_backup else None,
                "age_hours": round(backup_age_hours, 1) if backup_age_hours else None,
            },
            "failover_status": {
                "current_active": failover_manager.get_current_active(),
                "healthy_standbys": healthy_standbys,
                "total_standbys": len(dr_config["standby_endpoints"]),
                "standby_health": standby_health,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/recovery-plan")
async def get_recovery_plan():
    """Get disaster recovery plan and procedures"""
    try:
        plan = {
            "rpo_minutes": 60,  # Recovery Point Objective
            "rto_minutes": 30,  # Recovery Time Objective
            "backup_schedule": {
                "full": "Daily at 2:00 AM UTC",
                "incremental": "Every 4 hours",
                "retention": f"{dr_config['retention_days']} days",
            },
            "failover_procedure": [
                "1. Detect primary system failure",
                "2. Verify standby system health",
                "3. Promote standby to active",
                "4. Update DNS/load balancer",
                "5. Verify service restoration",
                "6. Monitor for issues",
            ],
            "restore_procedure": [
                "1. Identify appropriate backup",
                "2. Verify backup integrity",
                "3. Stop application services",
                "4. Restore database from backup",
                "5. Verify data integrity",
                "6. Restart application services",
                "7. Perform smoke tests",
            ],
            "contact_information": {
                "primary_oncall": "oncall@itechsmart.dev",
                "escalation": "cto@itechsmart.dev",
                "vendor_support": "support@itechsmart.dev",
            },
        }

        return {"success": True, "data": plan}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get recovery plan: {str(e)}"
        )


@router.post("/test-recovery")
async def test_recovery_procedure():
    """Test disaster recovery procedure (non-destructive)"""
    try:
        test_results = {"timestamp": datetime.utcnow().isoformat(), "tests": []}

        # Test 1: Verify backup exists
        backups = dr_manager.get_backup_list()
        test_results["tests"].append(
            {
                "name": "Backup Availability",
                "status": "passed" if backups else "failed",
                "message": f"Found {len(backups)} backups",
            }
        )

        # Test 2: Verify most recent backup
        if backups:
            recent_backup = backups[0]
            verification = await dr_manager.verify_backup(recent_backup["backup_id"])
            test_results["tests"].append(
                {
                    "name": "Backup Verification",
                    "status": (
                        "passed"
                        if verification["status"] == RecoveryStatus.VERIFIED.value
                        else "failed"
                    ),
                    "message": f"Verified backup {recent_backup['backup_id']}",
                }
            )

        # Test 3: Check standby health
        standby_health = {}
        for standby in dr_config["standby_endpoints"]:
            standby_health[standby] = await failover_manager.check_health(standby)

        healthy_count = sum(1 for h in standby_health.values() if h)
        test_results["tests"].append(
            {
                "name": "Standby System Health",
                "status": "passed" if healthy_count > 0 else "failed",
                "message": f"{healthy_count}/{len(standby_health)} standby systems healthy",
            }
        )

        # Overall result
        all_passed = all(t["status"] == "passed" for t in test_results["tests"])
        test_results["overall_status"] = "passed" if all_passed else "failed"

        return {"success": True, "data": test_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recovery test failed: {str(e)}")
