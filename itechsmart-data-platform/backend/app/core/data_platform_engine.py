"""
iTechSmart Data Platform - Data Governance and Management Engine
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4


class DataQuality(str, Enum):
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"  # 70-89%
    FAIR = "fair"  # 50-69%
    POOR = "poor"  # <50%


class DataAsset:
    def __init__(self, asset_id: str, name: str, asset_type: str, source: str):
        self.asset_id = asset_id
        self.name = name
        self.asset_type = asset_type  # table, file, api, stream
        self.source = source
        self.schema = {}
        self.metadata = {}
        self.quality_score = 100
        self.lineage = []
        self.tags = []
        self.owner = None
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()


class DataQualityRule:
    def __init__(self, rule_id: str, asset_id: str, rule_type: str, condition: str):
        self.rule_id = rule_id
        self.asset_id = asset_id
        self.rule_type = rule_type  # completeness, accuracy, consistency, timeliness
        self.condition = condition
        self.is_active = True
        self.violations = 0


class DataPlatformEngine:
    def __init__(self):
        self.assets: Dict[str, DataAsset] = {}
        self.quality_rules: Dict[str, DataQualityRule] = {}
        self.lineage_graph: Dict[str, List[str]] = {}

    def register_asset(
        self, name: str, asset_type: str, source: str, schema: Dict[str, Any]
    ) -> str:
        asset_id = str(uuid4())
        asset = DataAsset(asset_id, name, asset_type, source)
        asset.schema = schema
        self.assets[asset_id] = asset
        return asset_id

    def get_catalog(self, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        assets = list(self.assets.values())
        if asset_type:
            assets = [a for a in assets if a.asset_type == asset_type]

        return [
            {
                "asset_id": a.asset_id,
                "name": a.name,
                "type": a.asset_type,
                "source": a.source,
                "quality_score": a.quality_score,
                "owner": a.owner,
                "tags": a.tags,
            }
            for a in assets
        ]

    def add_quality_rule(self, asset_id: str, rule_type: str, condition: str) -> str:
        rule_id = str(uuid4())
        rule = DataQualityRule(rule_id, asset_id, rule_type, condition)
        self.quality_rules[rule_id] = rule
        return rule_id

    def check_data_quality(self, asset_id: str) -> Dict[str, Any]:
        asset = self.assets.get(asset_id)
        if not asset:
            return {}

        # Get rules for this asset
        asset_rules = [
            r
            for r in self.quality_rules.values()
            if r.asset_id == asset_id and r.is_active
        ]

        passed = len([r for r in asset_rules if r.violations == 0])
        total = len(asset_rules)

        if total > 0:
            quality_score = int((passed / total) * 100)
        else:
            quality_score = 100

        asset.quality_score = quality_score

        if quality_score >= 90:
            quality = DataQuality.EXCELLENT
        elif quality_score >= 70:
            quality = DataQuality.GOOD
        elif quality_score >= 50:
            quality = DataQuality.FAIR
        else:
            quality = DataQuality.POOR

        return {
            "asset_id": asset_id,
            "quality_score": quality_score,
            "quality_status": quality.value,
            "rules_checked": total,
            "rules_passed": passed,
            "rules_failed": total - passed,
        }

    def track_lineage(self, source_asset_id: str, target_asset_id: str) -> bool:
        if source_asset_id not in self.lineage_graph:
            self.lineage_graph[source_asset_id] = []

        self.lineage_graph[source_asset_id].append(target_asset_id)

        # Update asset lineage
        source = self.assets.get(source_asset_id)
        target = self.assets.get(target_asset_id)

        if source and target:
            target.lineage.append(
                {
                    "source": source.name,
                    "source_id": source_asset_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        return True

    def get_lineage(self, asset_id: str) -> Dict[str, Any]:
        asset = self.assets.get(asset_id)
        if not asset:
            return {}

        upstream = asset.lineage
        downstream = self.lineage_graph.get(asset_id, [])

        return {
            "asset_id": asset_id,
            "asset_name": asset.name,
            "upstream_sources": upstream,
            "downstream_targets": [
                {"asset_id": aid, "asset_name": self.assets[aid].name}
                for aid in downstream
                if aid in self.assets
            ],
        }

    def search_catalog(self, query: str) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()

        for asset in self.assets.values():
            if (
                query_lower in asset.name.lower()
                or query_lower in asset.asset_type.lower()
                or any(query_lower in tag.lower() for tag in asset.tags)
            ):
                results.append(
                    {
                        "asset_id": asset.asset_id,
                        "name": asset.name,
                        "type": asset.asset_type,
                        "quality_score": asset.quality_score,
                    }
                )

        return results

    def get_statistics(self) -> Dict[str, Any]:
        total_assets = len(self.assets)
        by_type = {}

        for asset in self.assets.values():
            if asset.asset_type not in by_type:
                by_type[asset.asset_type] = 0
            by_type[asset.asset_type] += 1

        avg_quality = (
            sum(a.quality_score for a in self.assets.values()) / total_assets
            if total_assets > 0
            else 0
        )

        return {
            "total_assets": total_assets,
            "by_type": by_type,
            "average_quality_score": round(avg_quality, 2),
            "total_quality_rules": len(self.quality_rules),
            "lineage_connections": sum(len(v) for v in self.lineage_graph.values()),
        }


data_platform_engine = DataPlatformEngine()
