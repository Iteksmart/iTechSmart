"""
Knowledge Graph API Endpoints for iTechSmart Ninja
Provides REST API for knowledge graph operations
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..core.knowledge_graph import (
    KnowledgeGraph,
    Entity,
    Relationship,
    EntityType,
    RelationType,
    get_knowledge_graph,
)

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])


# Request/Response Models
class CreateEntityRequest(BaseModel):
    """Request to create an entity"""

    name: str = Field(..., description="Entity name")
    entity_type: str = Field(..., description="Entity type")
    created_by: str = Field(..., description="Creator user ID")
    properties: Optional[Dict[str, Any]] = Field(
        default=None, description="Entity properties"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )


class CreateRelationshipRequest(BaseModel):
    """Request to create a relationship"""

    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relation_type: str = Field(..., description="Relationship type")
    created_by: str = Field(..., description="Creator user ID")
    properties: Optional[Dict[str, Any]] = Field(
        default=None, description="Relationship properties"
    )
    weight: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Relationship weight"
    )


class UpdateEntityRequest(BaseModel):
    """Request to update an entity"""

    name: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class EntityResponse(BaseModel):
    """Response with entity information"""

    entity_id: str
    name: str
    entity_type: str
    properties: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    created_by: str


class RelationshipResponse(BaseModel):
    """Response with relationship information"""

    relationship_id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any]
    weight: float
    created_at: str
    updated_at: str
    created_by: str


class EntityListResponse(BaseModel):
    """Response with list of entities"""

    entities: List[EntityResponse]
    total: int


class PathResponse(BaseModel):
    """Response with graph path"""

    start_entity_id: str
    end_entity_id: str
    path: List[str]
    relationships: List[str]
    total_weight: float
    length: int


class ClusterResponse(BaseModel):
    """Response with cluster information"""

    cluster_id: str
    name: str
    entities: List[str]
    center_entity_id: Optional[str]
    cohesion_score: float


class StatsResponse(BaseModel):
    """Response with graph statistics"""

    total_entities: int
    total_relationships: int
    entity_type_counts: Dict[str, int]
    relation_type_counts: Dict[str, int]
    avg_connections_per_entity: float
    most_connected_entities: List[Dict[str, Any]]


# API Endpoints
@router.post("/entities", response_model=EntityResponse)
async def create_entity(
    request: CreateEntityRequest, graph: KnowledgeGraph = Depends(get_knowledge_graph)
):
    """
    Create a new entity

    **Entity Types:** person, organization, location, event, concept, document, product, technology, custom

    **Returns:**
    - Entity information
    """
    try:
        entity = await graph.create_entity(
            name=request.name,
            entity_type=EntityType(request.entity_type),
            created_by=request.created_by,
            properties=request.properties,
            metadata=request.metadata,
        )

        return EntityResponse(**entity.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create entity: {str(e)}"
        )


@router.post("/relationships", response_model=RelationshipResponse)
async def create_relationship(
    request: CreateRelationshipRequest,
    graph: KnowledgeGraph = Depends(get_knowledge_graph),
):
    """
    Create a relationship between entities

    **Relation Types:** related_to, part_of, works_for, located_in, created_by, depends_on,
                        similar_to, parent_of, child_of, mentions, custom

    **Returns:**
    - Relationship information
    """
    try:
        relationship = await graph.create_relationship(
            source_id=request.source_id,
            target_id=request.target_id,
            relation_type=RelationType(request.relation_type),
            created_by=request.created_by,
            properties=request.properties,
            weight=request.weight,
        )

        return RelationshipResponse(**relationship.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create relationship: {str(e)}"
        )


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str, graph: KnowledgeGraph = Depends(get_knowledge_graph)
):
    """Get entity by ID"""
    entity = await graph.get_entity(entity_id)

    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

    return EntityResponse(**entity.to_dict())


@router.put("/entities/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str,
    request: UpdateEntityRequest,
    graph: KnowledgeGraph = Depends(get_knowledge_graph),
):
    """Update an entity"""
    try:
        updates = request.dict(exclude_none=True)
        entity = await graph.update_entity(entity_id, updates)
        return EntityResponse(**entity.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update entity: {str(e)}"
        )


@router.delete("/entities/{entity_id}")
async def delete_entity(
    entity_id: str, graph: KnowledgeGraph = Depends(get_knowledge_graph)
):
    """Delete an entity and its relationships"""
    try:
        await graph.delete_entity(entity_id)
        return {"message": f"Entity {entity_id} deleted successfully"}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete entity: {str(e)}"
        )


@router.delete("/relationships/{relationship_id}")
async def delete_relationship(
    relationship_id: str, graph: KnowledgeGraph = Depends(get_knowledge_graph)
):
    """Delete a relationship"""
    try:
        await graph.delete_relationship(relationship_id)
        return {"message": f"Relationship {relationship_id} deleted successfully"}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete relationship: {str(e)}"
        )


@router.get("/entities/search", response_model=EntityListResponse)
async def search_entities(
    query: str = Query(..., description="Search query"),
    entity_type: Optional[str] = Query(
        default=None, description="Filter by entity type"
    ),
    limit: int = Query(default=10, ge=1, le=100),
    graph: KnowledgeGraph = Depends(get_knowledge_graph),
):
    """Search entities by name"""
    try:
        e_type = EntityType(entity_type) if entity_type else None
        entities = await graph.search_entities(query, e_type, limit)

        return EntityListResponse(
            entities=[EntityResponse(**e.to_dict()) for e in entities],
            total=len(entities),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search entities: {str(e)}"
        )


@router.get("/entities/{entity_id}/neighbors", response_model=EntityListResponse)
async def get_neighbors(
    entity_id: str,
    direction: str = Query(default="both", regex="^(outgoing|incoming|both)$"),
    relation_type: Optional[str] = Query(default=None),
    graph: KnowledgeGraph = Depends(get_knowledge_graph),
):
    """Get neighboring entities"""
    try:
        r_type = RelationType(relation_type) if relation_type else None
        neighbors = await graph.get_neighbors(entity_id, direction, r_type)

        return EntityListResponse(
            entities=[EntityResponse(**e.to_dict()) for e in neighbors],
            total=len(neighbors),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get neighbors: {str(e)}"
        )


@router.get("/path", response_model=PathResponse)
async def find_path(
    start_id: str = Query(..., description="Start entity ID"),
    end_id: str = Query(..., description="End entity ID"),
    max_depth: int = Query(default=5, ge=1, le=10),
    graph: KnowledgeGraph = Depends(get_knowledge_graph),
):
    """Find shortest path between two entities"""
    try:
        path = await graph.find_path(start_id, end_id, max_depth)

        if not path:
            raise HTTPException(
                status_code=404, detail="No path found between entities"
            )

        return PathResponse(**path.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find path: {str(e)}")


@router.get("/clusters", response_model=List[ClusterResponse])
async def find_clusters(
    min_size: int = Query(default=3, ge=2, le=100),
    max_clusters: int = Query(default=10, ge=1, le=50),
    graph: KnowledgeGraph = Depends(get_knowledge_graph),
):
    """Find clusters of related entities"""
    try:
        clusters = await graph.find_clusters(min_size, max_clusters)
        return [ClusterResponse(**c.to_dict()) for c in clusters]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to find clusters: {str(e)}"
        )


@router.get("/statistics", response_model=StatsResponse)
async def get_statistics(graph: KnowledgeGraph = Depends(get_knowledge_graph)):
    """Get knowledge graph statistics"""
    try:
        stats = await graph.get_statistics()
        return StatsResponse(**stats.to_dict())

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/export")
async def export_graph(graph: KnowledgeGraph = Depends(get_knowledge_graph)):
    """Export entire graph as JSON"""
    try:
        data = await graph.export_graph()
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export graph: {str(e)}")


@router.post("/import")
async def import_graph(
    data: Dict[str, Any] = Body(...),
    graph: KnowledgeGraph = Depends(get_knowledge_graph),
):
    """Import graph from JSON"""
    try:
        success = await graph.import_graph(data)
        return {"message": "Graph imported successfully", "success": success}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import graph: {str(e)}")


@router.get("/health")
async def health_check(graph: KnowledgeGraph = Depends(get_knowledge_graph)):
    """Check knowledge graph service health"""
    try:
        stats = await graph.get_statistics()

        return {
            "status": "healthy",
            "total_entities": stats.total_entities,
            "total_relationships": stats.total_relationships,
            "supported_entity_types": [t.value for t in EntityType],
            "supported_relation_types": [r.value for r in RelationType],
        }

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
