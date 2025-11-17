"""
iTechSmart Supreme Plus - Monitoring API
Endpoints for infrastructure monitoring and metrics

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from models import InfrastructureNode, Metric, AlertRule
from engine import SupremePlusEngine

router = APIRouter()


# Pydantic models
class NodeCreate(BaseModel):
    hostname: str
    ip_address: str
    node_type: str
    os_type: str
    metadata: Optional[dict] = None


class NodeUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    node_type: Optional[str] = None
    os_type: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[dict] = None


class NodeResponse(BaseModel):
    id: int
    hostname: str
    ip_address: str
    node_type: str
    os_type: str
    status: str
    metadata: dict
    last_seen: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MetricResponse(BaseModel):
    id: int
    node_id: int
    metric_name: str
    value: float
    unit: str
    timestamp: datetime

    class Config:
        from_attributes = True


class AlertRuleCreate(BaseModel):
    name: str
    description: str
    node_id: int
    metric_name: str
    condition: str
    threshold: float
    severity: str
    enabled: bool = True


class AlertRuleResponse(BaseModel):
    id: int
    name: str
    description: str
    node_id: int
    metric_name: str
    condition: str
    threshold: float
    severity: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== NODE MANAGEMENT ====================


@router.post("/nodes", response_model=NodeResponse)
async def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    """Create a new infrastructure node"""
    new_node = InfrastructureNode(
        hostname=node.hostname,
        ip_address=node.ip_address,
        node_type=node.node_type,
        os_type=node.os_type,
        status="active",
        metadata=node.metadata or {},
        created_at=datetime.utcnow(),
    )
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node


@router.get("/nodes", response_model=List[NodeResponse])
async def list_nodes(
    node_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List infrastructure nodes"""
    query = db.query(InfrastructureNode)

    if node_type:
        query = query.filter(InfrastructureNode.node_type == node_type)
    if status:
        query = query.filter(InfrastructureNode.status == status)

    nodes = (
        query.order_by(InfrastructureNode.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return nodes


@router.get("/nodes/{node_id}", response_model=NodeResponse)
async def get_node(node_id: int, db: Session = Depends(get_db)):
    """Get node by ID"""
    node = db.query(InfrastructureNode).filter(InfrastructureNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.put("/nodes/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: int, node_update: NodeUpdate, db: Session = Depends(get_db)
):
    """Update a node"""
    node = db.query(InfrastructureNode).filter(InfrastructureNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    update_data = node_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(node, field, value)

    db.commit()
    db.refresh(node)
    return node


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: int, db: Session = Depends(get_db)):
    """Delete a node"""
    node = db.query(InfrastructureNode).filter(InfrastructureNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    db.delete(node)
    db.commit()
    return {"message": "Node deleted successfully"}


# ==================== METRICS ====================


@router.post("/nodes/{node_id}/metrics/collect")
async def collect_node_metrics(node_id: int, db: Session = Depends(get_db)):
    """Collect metrics from a node"""
    engine = SupremePlusEngine(db)
    try:
        metrics = engine.collect_metrics(node_id)
        return {
            "message": "Metrics collected successfully",
            "node_id": node_id,
            "metrics_count": len(metrics),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}/metrics", response_model=List[MetricResponse])
async def get_node_metrics(
    node_id: int,
    metric_name: Optional[str] = None,
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db),
):
    """Get metrics for a node"""
    query = db.query(Metric).filter(
        Metric.node_id == node_id,
        Metric.timestamp >= datetime.utcnow() - timedelta(hours=hours),
    )

    if metric_name:
        query = query.filter(Metric.metric_name == metric_name)

    metrics = query.order_by(Metric.timestamp.desc()).all()
    return metrics


@router.get("/metrics/latest")
async def get_latest_metrics(
    node_id: Optional[int] = None,
    metric_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get latest metrics across all nodes or specific node"""
    query = db.query(Metric)

    if node_id:
        query = query.filter(Metric.node_id == node_id)
    if metric_name:
        query = query.filter(Metric.metric_name == metric_name)

    # Get latest metric for each node/metric combination
    from sqlalchemy import func

    subquery = (
        db.query(
            Metric.node_id,
            Metric.metric_name,
            func.max(Metric.timestamp).label("max_timestamp"),
        )
        .group_by(Metric.node_id, Metric.metric_name)
        .subquery()
    )

    metrics = query.join(
        subquery,
        (Metric.node_id == subquery.c.node_id)
        & (Metric.metric_name == subquery.c.metric_name)
        & (Metric.timestamp == subquery.c.max_timestamp),
    ).all()

    return [
        {
            "id": m.id,
            "node_id": m.node_id,
            "metric_name": m.metric_name,
            "value": m.value,
            "unit": m.unit,
            "timestamp": m.timestamp,
        }
        for m in metrics
    ]


# ==================== ALERT RULES ====================


@router.post("/alert-rules", response_model=AlertRuleResponse)
async def create_alert_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """Create a new alert rule"""
    new_rule = AlertRule(
        name=rule.name,
        description=rule.description,
        node_id=rule.node_id,
        metric_name=rule.metric_name,
        condition=rule.condition,
        threshold=rule.threshold,
        severity=rule.severity,
        enabled=rule.enabled,
        created_at=datetime.utcnow(),
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule


@router.get("/alert-rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    node_id: Optional[int] = None,
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List alert rules"""
    query = db.query(AlertRule)

    if node_id:
        query = query.filter(AlertRule.node_id == node_id)
    if enabled is not None:
        query = query.filter(AlertRule.enabled == enabled)

    rules = query.order_by(AlertRule.created_at.desc()).all()
    return rules


@router.get("/alert-rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get alert rule by ID"""
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return rule


@router.delete("/alert-rules/{rule_id}")
async def delete_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete an alert rule"""
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Alert rule deleted successfully"}


@router.post("/alert-rules/check")
async def check_alert_rules(db: Session = Depends(get_db)):
    """Check all alert rules and create incidents if triggered"""
    engine = SupremePlusEngine(db)
    incidents = engine.check_alert_rules()
    return {
        "message": "Alert rules checked",
        "incidents_created": len(incidents),
        "incident_ids": [i.id for i in incidents],
    }


# ==================== STATISTICS ====================


@router.get("/stats/nodes")
async def get_node_stats(db: Session = Depends(get_db)):
    """Get node statistics"""
    total = db.query(InfrastructureNode).count()
    active = (
        db.query(InfrastructureNode)
        .filter(InfrastructureNode.status == "active")
        .count()
    )
    inactive = (
        db.query(InfrastructureNode)
        .filter(InfrastructureNode.status == "inactive")
        .count()
    )

    # By type
    from sqlalchemy import func

    by_type = (
        db.query(InfrastructureNode.node_type, func.count(InfrastructureNode.id))
        .group_by(InfrastructureNode.node_type)
        .all()
    )

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "by_type": {node_type: count for node_type, count in by_type},
    }


@router.get("/stats/metrics")
async def get_metric_stats(db: Session = Depends(get_db)):
    """Get metric statistics"""
    total = db.query(Metric).count()

    # Recent metrics (last hour)
    recent = (
        db.query(Metric)
        .filter(Metric.timestamp >= datetime.utcnow() - timedelta(hours=1))
        .count()
    )

    # By metric name
    from sqlalchemy import func

    by_name = (
        db.query(Metric.metric_name, func.count(Metric.id))
        .group_by(Metric.metric_name)
        .all()
    )

    return {
        "total": total,
        "recent_1h": recent,
        "by_name": {name: count for name, count in by_name},
    }
