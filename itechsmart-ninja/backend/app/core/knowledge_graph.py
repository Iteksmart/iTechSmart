"""
Knowledge Graph Integration for iTechSmart Ninja
Provides entity extraction, relationship mapping, and graph-based knowledge management
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class EntityType(str, Enum):
    """Entity types in knowledge graph"""

    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    CONCEPT = "concept"
    DOCUMENT = "document"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    CUSTOM = "custom"


class RelationType(str, Enum):
    """Relationship types between entities"""

    RELATED_TO = "related_to"
    PART_OF = "part_of"
    WORKS_FOR = "works_for"
    LOCATED_IN = "located_in"
    CREATED_BY = "created_by"
    DEPENDS_ON = "depends_on"
    SIMILAR_TO = "similar_to"
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    MENTIONS = "mentions"
    CUSTOM = "custom"


@dataclass
class Entity:
    """Entity in knowledge graph"""

    entity_id: str
    name: str
    entity_type: EntityType
    properties: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "properties": self.properties,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
        }


@dataclass
class Relationship:
    """Relationship between entities"""

    relationship_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    properties: Dict[str, Any]
    weight: float  # Strength of relationship (0.0 to 1.0)
    created_at: datetime
    updated_at: datetime
    created_by: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "properties": self.properties,
            "weight": self.weight,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
        }


@dataclass
class GraphPath:
    """Path between entities in graph"""

    start_entity_id: str
    end_entity_id: str
    path: List[str]  # List of entity IDs
    relationships: List[str]  # List of relationship IDs
    total_weight: float
    length: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_entity_id": self.start_entity_id,
            "end_entity_id": self.end_entity_id,
            "path": self.path,
            "relationships": self.relationships,
            "total_weight": self.total_weight,
            "length": self.length,
        }


@dataclass
class GraphCluster:
    """Cluster of related entities"""

    cluster_id: str
    name: str
    entities: List[str]  # List of entity IDs
    center_entity_id: Optional[str]
    cohesion_score: float  # How tightly connected (0.0 to 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "name": self.name,
            "entities": self.entities,
            "center_entity_id": self.center_entity_id,
            "cohesion_score": self.cohesion_score,
        }


@dataclass
class GraphStats:
    """Knowledge graph statistics"""

    total_entities: int
    total_relationships: int
    entity_type_counts: Dict[str, int]
    relation_type_counts: Dict[str, int]
    avg_connections_per_entity: float
    most_connected_entities: List[Tuple[str, int]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_entities": self.total_entities,
            "total_relationships": self.total_relationships,
            "entity_type_counts": self.entity_type_counts,
            "relation_type_counts": self.relation_type_counts,
            "avg_connections_per_entity": self.avg_connections_per_entity,
            "most_connected_entities": [
                {"entity_id": e_id, "connections": count}
                for e_id, count in self.most_connected_entities
            ],
        }


class KnowledgeGraph:
    """Manages knowledge graph operations"""

    def __init__(self):
        """Initialize knowledge graph"""
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        # Adjacency lists for efficient graph traversal
        self.outgoing: Dict[str, List[str]] = {}  # entity_id -> [relationship_ids]
        self.incoming: Dict[str, List[str]] = {}  # entity_id -> [relationship_ids]
        logger.info("KnowledgeGraph initialized successfully")

    async def create_entity(
        self,
        name: str,
        entity_type: EntityType,
        created_by: str,
        properties: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Entity:
        """
        Create a new entity

        Args:
            name: Entity name
            entity_type: Entity type
            created_by: Creator user ID
            properties: Entity properties
            metadata: Additional metadata

        Returns:
            Entity object
        """
        entity_id = str(uuid.uuid4())

        entity = Entity(
            entity_id=entity_id,
            name=name,
            entity_type=entity_type,
            properties=properties or {},
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=created_by,
        )

        self.entities[entity_id] = entity
        self.outgoing[entity_id] = []
        self.incoming[entity_id] = []

        logger.info(f"Entity {entity_id} created: {name}")
        return entity

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        created_by: str,
        properties: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
    ) -> Relationship:
        """
        Create a relationship between entities

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relation_type: Relationship type
            created_by: Creator user ID
            properties: Relationship properties
            weight: Relationship weight (0.0 to 1.0)

        Returns:
            Relationship object
        """
        if source_id not in self.entities:
            raise ValueError(f"Source entity {source_id} not found")
        if target_id not in self.entities:
            raise ValueError(f"Target entity {target_id} not found")

        relationship_id = str(uuid.uuid4())

        relationship = Relationship(
            relationship_id=relationship_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            properties=properties or {},
            weight=max(0.0, min(1.0, weight)),  # Clamp to [0, 1]
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=created_by,
        )

        self.relationships[relationship_id] = relationship

        # Update adjacency lists
        self.outgoing[source_id].append(relationship_id)
        self.incoming[target_id].append(relationship_id)

        logger.info(
            f"Relationship {relationship_id} created: {source_id} -> {target_id}"
        )
        return relationship

    async def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> Entity:
        """Update an entity"""
        entity = self.entities.get(entity_id)
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")

        if "name" in updates:
            entity.name = updates["name"]
        if "properties" in updates:
            entity.properties.update(updates["properties"])
        if "metadata" in updates:
            entity.metadata.update(updates["metadata"])

        entity.updated_at = datetime.now()

        logger.info(f"Entity {entity_id} updated")
        return entity

    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships"""
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} not found")

        # Delete all relationships involving this entity
        relationships_to_delete = []

        # Outgoing relationships
        for rel_id in self.outgoing.get(entity_id, []):
            relationships_to_delete.append(rel_id)

        # Incoming relationships
        for rel_id in self.incoming.get(entity_id, []):
            relationships_to_delete.append(rel_id)

        for rel_id in relationships_to_delete:
            await self.delete_relationship(rel_id)

        # Delete entity
        del self.entities[entity_id]
        del self.outgoing[entity_id]
        del self.incoming[entity_id]

        logger.info(f"Entity {entity_id} deleted")
        return True

    async def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship"""
        if relationship_id not in self.relationships:
            raise ValueError(f"Relationship {relationship_id} not found")

        relationship = self.relationships[relationship_id]

        # Remove from adjacency lists
        self.outgoing[relationship.source_id].remove(relationship_id)
        self.incoming[relationship.target_id].remove(relationship_id)

        # Delete relationship
        del self.relationships[relationship_id]

        logger.info(f"Relationship {relationship_id} deleted")
        return True

    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)

    async def search_entities(
        self, query: str, entity_type: Optional[EntityType] = None, limit: int = 10
    ) -> List[Entity]:
        """
        Search entities by name

        Args:
            query: Search query
            entity_type: Filter by entity type
            limit: Maximum results

        Returns:
            List of matching entities
        """
        query_lower = query.lower()
        results = []

        for entity in self.entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue

            if query_lower in entity.name.lower():
                results.append(entity)

            if len(results) >= limit:
                break

        return results

    async def get_neighbors(
        self,
        entity_id: str,
        direction: str = "both",  # "outgoing", "incoming", "both"
        relation_type: Optional[RelationType] = None,
    ) -> List[Entity]:
        """
        Get neighboring entities

        Args:
            entity_id: Entity ID
            direction: Direction of relationships
            relation_type: Filter by relationship type

        Returns:
            List of neighboring entities
        """
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} not found")

        neighbor_ids = set()

        # Outgoing relationships
        if direction in ["outgoing", "both"]:
            for rel_id in self.outgoing.get(entity_id, []):
                rel = self.relationships[rel_id]
                if relation_type is None or rel.relation_type == relation_type:
                    neighbor_ids.add(rel.target_id)

        # Incoming relationships
        if direction in ["incoming", "both"]:
            for rel_id in self.incoming.get(entity_id, []):
                rel = self.relationships[rel_id]
                if relation_type is None or rel.relation_type == relation_type:
                    neighbor_ids.add(rel.source_id)

        return [self.entities[nid] for nid in neighbor_ids]

    async def find_path(
        self, start_id: str, end_id: str, max_depth: int = 5
    ) -> Optional[GraphPath]:
        """
        Find shortest path between two entities using BFS

        Args:
            start_id: Start entity ID
            end_id: End entity ID
            max_depth: Maximum path length

        Returns:
            GraphPath object or None if no path found
        """
        if start_id not in self.entities or end_id not in self.entities:
            return None

        if start_id == end_id:
            return GraphPath(
                start_entity_id=start_id,
                end_entity_id=end_id,
                path=[start_id],
                relationships=[],
                total_weight=0.0,
                length=0,
            )

        # BFS
        queue = [(start_id, [start_id], [], 0.0)]
        visited = {start_id}

        while queue:
            current_id, path, rels, weight = queue.pop(0)

            if len(path) > max_depth:
                continue

            # Check outgoing relationships
            for rel_id in self.outgoing.get(current_id, []):
                rel = self.relationships[rel_id]
                next_id = rel.target_id

                if next_id == end_id:
                    return GraphPath(
                        start_entity_id=start_id,
                        end_entity_id=end_id,
                        path=path + [next_id],
                        relationships=rels + [rel_id],
                        total_weight=weight + rel.weight,
                        length=len(path),
                    )

                if next_id not in visited:
                    visited.add(next_id)
                    queue.append(
                        (
                            next_id,
                            path + [next_id],
                            rels + [rel_id],
                            weight + rel.weight,
                        )
                    )

        return None

    async def find_clusters(
        self, min_size: int = 3, max_clusters: int = 10
    ) -> List[GraphCluster]:
        """
        Find clusters of related entities

        Args:
            min_size: Minimum cluster size
            max_clusters: Maximum number of clusters

        Returns:
            List of clusters
        """
        # Simple clustering based on connectivity
        visited = set()
        clusters = []

        for entity_id in self.entities:
            if entity_id in visited:
                continue

            # BFS to find connected component
            cluster_entities = []
            queue = [entity_id]
            component_visited = {entity_id}

            while queue:
                current_id = queue.pop(0)
                cluster_entities.append(current_id)

                # Get neighbors
                neighbors = await self.get_neighbors(current_id, "both")
                for neighbor in neighbors:
                    if neighbor.entity_id not in component_visited:
                        component_visited.add(neighbor.entity_id)
                        queue.append(neighbor.entity_id)

            visited.update(component_visited)

            if len(cluster_entities) >= min_size:
                # Find center (most connected entity)
                center_id = max(
                    cluster_entities,
                    key=lambda eid: len(self.outgoing.get(eid, []))
                    + len(self.incoming.get(eid, [])),
                )

                cluster = GraphCluster(
                    cluster_id=str(uuid.uuid4()),
                    name=f"Cluster {len(clusters) + 1}",
                    entities=cluster_entities,
                    center_entity_id=center_id,
                    cohesion_score=len(cluster_entities) / len(self.entities),
                )
                clusters.append(cluster)

            if len(clusters) >= max_clusters:
                break

        return clusters

    async def get_statistics(self) -> GraphStats:
        """Get knowledge graph statistics"""
        entity_type_counts = {}
        for entity in self.entities.values():
            entity_type = entity.entity_type.value
            entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1

        relation_type_counts = {}
        for rel in self.relationships.values():
            rel_type = rel.relation_type.value
            relation_type_counts[rel_type] = relation_type_counts.get(rel_type, 0) + 1

        # Calculate connections per entity
        connection_counts = []
        for entity_id in self.entities:
            connections = len(self.outgoing.get(entity_id, [])) + len(
                self.incoming.get(entity_id, [])
            )
            connection_counts.append((entity_id, connections))

        avg_connections = (
            sum(c for _, c in connection_counts) / len(self.entities)
            if self.entities
            else 0
        )

        # Most connected entities
        most_connected = sorted(connection_counts, key=lambda x: x[1], reverse=True)[
            :10
        ]

        return GraphStats(
            total_entities=len(self.entities),
            total_relationships=len(self.relationships),
            entity_type_counts=entity_type_counts,
            relation_type_counts=relation_type_counts,
            avg_connections_per_entity=round(avg_connections, 2),
            most_connected_entities=most_connected,
        )

    async def export_graph(self) -> Dict[str, Any]:
        """Export entire graph as JSON"""
        return {
            "entities": [e.to_dict() for e in self.entities.values()],
            "relationships": [r.to_dict() for r in self.relationships.values()],
        }

    async def import_graph(self, data: Dict[str, Any]) -> bool:
        """Import graph from JSON"""
        try:
            # Import entities
            for entity_data in data.get("entities", []):
                entity = Entity(
                    entity_id=entity_data["entity_id"],
                    name=entity_data["name"],
                    entity_type=EntityType(entity_data["entity_type"]),
                    properties=entity_data["properties"],
                    metadata=entity_data["metadata"],
                    created_at=datetime.fromisoformat(entity_data["created_at"]),
                    updated_at=datetime.fromisoformat(entity_data["updated_at"]),
                    created_by=entity_data["created_by"],
                )
                self.entities[entity.entity_id] = entity
                self.outgoing[entity.entity_id] = []
                self.incoming[entity.entity_id] = []

            # Import relationships
            for rel_data in data.get("relationships", []):
                rel = Relationship(
                    relationship_id=rel_data["relationship_id"],
                    source_id=rel_data["source_id"],
                    target_id=rel_data["target_id"],
                    relation_type=RelationType(rel_data["relation_type"]),
                    properties=rel_data["properties"],
                    weight=rel_data["weight"],
                    created_at=datetime.fromisoformat(rel_data["created_at"]),
                    updated_at=datetime.fromisoformat(rel_data["updated_at"]),
                    created_by=rel_data["created_by"],
                )
                self.relationships[rel.relationship_id] = rel
                self.outgoing[rel.source_id].append(rel.relationship_id)
                self.incoming[rel.target_id].append(rel.relationship_id)

            logger.info("Graph imported successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to import graph: {e}")
            raise


# Global knowledge graph instance
_knowledge_graph: Optional[KnowledgeGraph] = None


def get_knowledge_graph() -> KnowledgeGraph:
    """Get or create global knowledge graph instance"""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
    return _knowledge_graph
