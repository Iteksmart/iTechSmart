"""
API endpoints for self-healing and auto-evolution
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.self_healing_engine import SelfHealingEngine
from app.core.auto_evolution_engine import AutoEvolutionEngine
from app.models.self_healing import (
    ErrorLog, CodeFix, HealthCheck, SystemMetric,
    ImprovementSuggestion, InnovationLog, AutoUpdateLog
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/self-healing", tags=["self-healing"])


# Pydantic models
class HealthStatus(BaseModel):
    overall_health: float
    checks: dict
    timestamp: str
    issues_detected: int
    auto_fixed: int


class ErrorLogResponse(BaseModel):
    id: int
    timestamp: str
    error_type: str
    error_message: str
    severity: str
    resolved: bool
    
    class Config:
        from_attributes = True


class CodeFixResponse(BaseModel):
    id: int
    timestamp: str
    fix_type: str
    fix_description: str
    confidence_score: float
    applied: bool
    success: Optional[bool]
    
    class Config:
        from_attributes = True


class InnovationResponse(BaseModel):
    id: int
    timestamp: str
    innovation_type: str
    title: str
    description: str
    status: str
    
    class Config:
        from_attributes = True


class ConfigUpdate(BaseModel):
    auto_fix_enabled: Optional[bool] = None
    auto_deploy_enabled: Optional[bool] = None
    auto_optimize_enabled: Optional[bool] = None
    auto_innovate_enabled: Optional[bool] = None
    confidence_threshold: Optional[float] = None


# Endpoints
@router.get("/health", response_model=HealthStatus)
async def get_health_status(db: Session = Depends(get_db)):
    """Get current system health status"""
    engine = SelfHealingEngine(db)
    health = await engine.run_health_checks()
    
    return HealthStatus(
        overall_health=engine._calculate_overall_health(health),
        checks=health["checks"],
        timestamp=health["timestamp"],
        issues_detected=0,
        auto_fixed=0
    )


@router.get("/errors", response_model=List[ErrorLogResponse])
async def get_errors(
    limit: int = 50,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get error logs"""
    query = db.query(ErrorLog)
    
    if severity:
        query = query.filter(ErrorLog.severity == severity)
    
    if resolved is not None:
        query = query.filter(ErrorLog.resolved == resolved)
    
    errors = query.order_by(ErrorLog.timestamp.desc()).limit(limit).all()
    
    return [
        ErrorLogResponse(
            id=e.id,
            timestamp=e.timestamp.isoformat(),
            error_type=e.error_type,
            error_message=e.error_message,
            severity=e.severity,
            resolved=e.resolved
        )
        for e in errors
    ]


@router.get("/errors/{error_id}")
async def get_error_detail(error_id: int, db: Session = Depends(get_db)):
    """Get detailed error information"""
    error = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()
    
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    
    return {
        "id": error.id,
        "timestamp": error.timestamp.isoformat(),
        "error_type": error.error_type,
        "error_message": error.error_message,
        "stack_trace": error.stack_trace,
        "file_path": error.file_path,
        "line_number": error.line_number,
        "severity": error.severity,
        "resolved": error.resolved,
        "fixes": [
            {
                "id": f.id,
                "fix_type": f.fix_type,
                "description": f.fix_description,
                "confidence": f.confidence_score,
                "applied": f.applied,
                "success": f.success
            }
            for f in error.fixes
        ]
    }


@router.post("/errors/{error_id}/fix")
async def trigger_fix(
    error_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger fix for an error"""
    error = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()
    
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    
    engine = SelfHealingEngine(db)
    
    # Run fix in background
    background_tasks.add_task(engine.auto_fix_error, error)
    
    return {"message": "Fix triggered", "error_id": error_id}


@router.get("/fixes", response_model=List[CodeFixResponse])
async def get_fixes(
    limit: int = 50,
    applied: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get code fixes"""
    query = db.query(CodeFix)
    
    if applied is not None:
        query = query.filter(CodeFix.applied == applied)
    
    fixes = query.order_by(CodeFix.timestamp.desc()).limit(limit).all()
    
    return [
        CodeFixResponse(
            id=f.id,
            timestamp=f.timestamp.isoformat(),
            fix_type=f.fix_type,
            fix_description=f.fix_description,
            confidence_score=f.confidence_score,
            applied=f.applied,
            success=f.success
        )
        for f in fixes
    ]


@router.post("/fixes/{fix_id}/approve")
async def approve_fix(
    fix_id: int,
    approved_by: str,
    db: Session = Depends(get_db)
):
    """Approve a pending fix"""
    fix = db.query(CodeFix).filter(CodeFix.id == fix_id).first()
    
    if not fix:
        raise HTTPException(status_code=404, detail="Fix not found")
    
    if not fix.requires_approval:
        raise HTTPException(status_code=400, detail="Fix does not require approval")
    
    fix.approved_by = approved_by
    fix.approved_at = datetime.utcnow()
    
    # Apply the fix
    engine = SelfHealingEngine(db)
    success = await engine._apply_fix(fix.code_changes)
    
    fix.applied = True
    fix.success = success
    
    db.commit()
    
    return {"message": "Fix approved and applied", "success": success}


@router.post("/fixes/{fix_id}/reject")
async def reject_fix(fix_id: int, reason: str, db: Session = Depends(get_db)):
    """Reject a pending fix"""
    fix = db.query(CodeFix).filter(CodeFix.id == fix_id).first()
    
    if not fix:
        raise HTTPException(status_code=404, detail="Fix not found")
    
    fix.applied = False
    fix.success = False
    
    db.commit()
    
    return {"message": "Fix rejected", "reason": reason}


@router.get("/innovations", response_model=List[InnovationResponse])
async def get_innovations(
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get innovation logs"""
    query = db.query(InnovationLog)
    
    if status:
        query = query.filter(InnovationLog.status == status)
    
    innovations = query.order_by(InnovationLog.timestamp.desc()).limit(limit).all()
    
    return [
        InnovationResponse(
            id=i.id,
            timestamp=i.timestamp.isoformat(),
            innovation_type=i.innovation_type,
            title=i.title,
            description=i.description,
            status=i.status
        )
        for i in innovations
    ]


@router.get("/innovations/{innovation_id}")
async def get_innovation_detail(innovation_id: int, db: Session = Depends(get_db)):
    """Get detailed innovation information"""
    innovation = db.query(InnovationLog).filter(
        InnovationLog.id == innovation_id
    ).first()
    
    if not innovation:
        raise HTTPException(status_code=404, detail="Innovation not found")
    
    return {
        "id": innovation.id,
        "timestamp": innovation.timestamp.isoformat(),
        "innovation_type": innovation.innovation_type,
        "title": innovation.title,
        "description": innovation.description,
        "rationale": innovation.rationale,
        "implementation": innovation.implementation,
        "estimated_value": innovation.estimated_value,
        "status": innovation.status,
        "implemented_at": innovation.implemented_at.isoformat() if innovation.implemented_at else None,
        "impact_metrics": innovation.impact_metrics
    }


@router.post("/innovations/generate")
async def generate_innovations(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger innovation generation"""
    engine = AutoEvolutionEngine(db)
    
    # Run in background
    background_tasks.add_task(engine.generate_innovations)
    
    return {"message": "Innovation generation triggered"}


@router.post("/innovations/{innovation_id}/approve")
async def approve_innovation(
    innovation_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Approve and implement an innovation"""
    innovation = db.query(InnovationLog).filter(
        InnovationLog.id == innovation_id
    ).first()
    
    if not innovation:
        raise HTTPException(status_code=404, detail="Innovation not found")
    
    innovation.status = "approved"
    db.commit()
    
    # Implement in background
    engine = AutoEvolutionEngine(db)
    background_tasks.add_task(
        engine.implement_innovation,
        innovation.implementation
    )
    
    return {"message": "Innovation approved and implementation started"}


@router.get("/metrics")
async def get_metrics(
    metric_type: Optional[str] = None,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get system metrics"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(SystemMetric).filter(SystemMetric.timestamp >= since)
    
    if metric_type:
        query = query.filter(SystemMetric.metric_type == metric_type)
    
    metrics = query.order_by(SystemMetric.timestamp.desc()).all()
    
    return [
        {
            "timestamp": m.timestamp.isoformat(),
            "metric_type": m.metric_type,
            "value": m.metric_value,
            "unit": m.unit,
            "threshold_exceeded": m.threshold_exceeded
        }
        for m in metrics
    ]


@router.get("/improvements")
async def get_improvements(
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get improvement suggestions"""
    query = db.query(ImprovementSuggestion)
    
    if status:
        query = query.filter(ImprovementSuggestion.status == status)
    
    improvements = query.order_by(
        ImprovementSuggestion.timestamp.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": i.id,
            "timestamp": i.timestamp.isoformat(),
            "category": i.category,
            "title": i.title,
            "description": i.description,
            "impact": i.impact,
            "effort": i.effort,
            "risk": i.risk,
            "confidence": i.confidence,
            "status": i.status
        }
        for i in improvements
    ]


@router.get("/updates")
async def get_updates(limit: int = 50, db: Session = Depends(get_db)):
    """Get auto-update logs"""
    updates = db.query(AutoUpdateLog).order_by(
        AutoUpdateLog.timestamp.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": u.id,
            "timestamp": u.timestamp.isoformat(),
            "update_type": u.update_type,
            "description": u.description,
            "version_before": u.version_before,
            "version_after": u.version_after,
            "success": u.success
        }
        for u in updates
    ]


@router.get("/config")
async def get_config(db: Session = Depends(get_db)):
    """Get self-healing configuration"""
    engine = SelfHealingEngine(db)
    evolution_engine = AutoEvolutionEngine(db)
    
    return {
        "self_healing": engine.config,
        "auto_evolution": evolution_engine.config
    }


@router.put("/config")
async def update_config(config: ConfigUpdate, db: Session = Depends(get_db)):
    """Update self-healing configuration"""
    engine = SelfHealingEngine(db)
    evolution_engine = AutoEvolutionEngine(db)
    
    if config.auto_fix_enabled is not None:
        engine.config["auto_fix_enabled"] = config.auto_fix_enabled
    
    if config.auto_deploy_enabled is not None:
        engine.config["auto_deploy_enabled"] = config.auto_deploy_enabled
    
    if config.auto_optimize_enabled is not None:
        evolution_engine.config["auto_optimize_enabled"] = config.auto_optimize_enabled
    
    if config.auto_innovate_enabled is not None:
        evolution_engine.config["auto_innovate_enabled"] = config.auto_innovate_enabled
    
    if config.confidence_threshold is not None:
        engine.config["confidence_threshold"] = config.confidence_threshold
    
    return {
        "message": "Configuration updated",
        "self_healing": engine.config,
        "auto_evolution": evolution_engine.config
    }


@router.post("/start")
async def start_self_healing(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start self-healing and auto-evolution engines"""
    healing_engine = SelfHealingEngine(db)
    evolution_engine = AutoEvolutionEngine(db)
    
    # Start both engines in background
    background_tasks.add_task(healing_engine.start_monitoring)
    background_tasks.add_task(evolution_engine.start_evolution)
    
    return {
        "message": "Self-healing and auto-evolution engines started",
        "status": "running"
    }


@router.post("/stop")
async def stop_self_healing(db: Session = Depends(get_db)):
    """Stop self-healing and auto-evolution engines"""
    # Set flags to stop engines
    engine = SelfHealingEngine(db)
    evolution_engine = AutoEvolutionEngine(db)
    
    engine.config["auto_fix_enabled"] = False
    evolution_engine.config["auto_optimize_enabled"] = False
    evolution_engine.config["auto_innovate_enabled"] = False
    
    return {
        "message": "Self-healing and auto-evolution engines stopped",
        "status": "stopped"
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get self-healing statistics"""
    
    # Count errors
    total_errors = db.query(ErrorLog).count()
    resolved_errors = db.query(ErrorLog).filter(ErrorLog.resolved == True).count()
    
    # Count fixes
    total_fixes = db.query(CodeFix).count()
    successful_fixes = db.query(CodeFix).filter(
        CodeFix.applied == True,
        CodeFix.success == True
    ).count()
    
    # Count innovations
    total_innovations = db.query(InnovationLog).count()
    implemented_innovations = db.query(InnovationLog).filter(
        InnovationLog.status == "implemented"
    ).count()
    
    # Recent health
    recent_health = db.query(HealthCheck).order_by(
        HealthCheck.timestamp.desc()
    ).first()
    
    return {
        "errors": {
            "total": total_errors,
            "resolved": resolved_errors,
            "resolution_rate": resolved_errors / total_errors if total_errors > 0 else 0
        },
        "fixes": {
            "total": total_fixes,
            "successful": successful_fixes,
            "success_rate": successful_fixes / total_fixes if total_fixes > 0 else 0
        },
        "innovations": {
            "total": total_innovations,
            "implemented": implemented_innovations,
            "implementation_rate": implemented_innovations / total_innovations if total_innovations > 0 else 0
        },
        "health": {
            "current": recent_health.overall_health if recent_health else 0,
            "timestamp": recent_health.timestamp.isoformat() if recent_health else None
        }
    }