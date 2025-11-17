"""
MCP (Model Context Protocol) API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..database import get_db
from ..models.database import MCPDataSource, MCPQuery, User
from ..integrations.mcp_integration import mcp_client, DataSourceType
from ..auth import get_current_user

router = APIRouter(prefix="/api/mcp", tags=["mcp"])
logger = logging.getLogger(__name__)


# Request/Response Models
from pydantic import BaseModel


class RegisterSourceRequest(BaseModel):
    name: str
    type: str
    connection_string: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None


class UpdateSourceRequest(BaseModel):
    name: Optional[str] = None
    connection_string: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class QueryRequest(BaseModel):
    query: str
    params: Optional[Dict[str, Any]] = None
    use_cache: bool = True


class MultiQueryRequest(BaseModel):
    queries: List[Dict[str, Any]]  # List of {source_id, query, params}


@router.post("/sources/register")
async def register_source(
    request: RegisterSourceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Register a new MCP data source

    Example:
    ```json
    {
        "name": "Production DB",
        "type": "postgresql",
        "connection_string": "postgresql://user:pass@host/db"
    }
    ```
    """
    try:
        # Validate source type
        if request.type not in [t.value for t in DataSourceType]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source type. Supported: {[t.value for t in DataSourceType]}",
            )

        # Create database record
        db_source = MCPDataSource(
            user_id=current_user.id,
            name=request.name,
            type=request.type,
            connection_string=request.connection_string,
            config={
                "connection_config": request.connection_config,
                **(request.config or {}),
            },
            enabled=True,
            created_at=datetime.utcnow(),
        )

        db.add(db_source)
        db.commit()
        db.refresh(db_source)

        # Register with MCP client
        source_config = {
            "name": request.name,
            "type": request.type,
            "connection_string": request.connection_string,
            "connection_config": request.connection_config,
            **(request.config or {}),
        }

        result = await mcp_client.register_source(
            source_id=str(db_source.id), config=source_config
        )

        if not result.get("success"):
            # Rollback database if registration failed
            db.delete(db_source)
            db.commit()
            raise HTTPException(status_code=400, detail=result.get("error"))

        return {
            "success": True,
            "source": {
                "id": db_source.id,
                "name": db_source.name,
                "type": db_source.type,
                "enabled": db_source.enabled,
                "created_at": db_source.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def list_sources(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List all MCP data sources for current user"""
    try:
        sources = (
            db.query(MCPDataSource)
            .filter(MCPDataSource.user_id == current_user.id)
            .all()
        )

        return {
            "success": True,
            "sources": [
                {
                    "id": source.id,
                    "name": source.name,
                    "type": source.type,
                    "enabled": source.enabled,
                    "last_used": (
                        source.last_used.isoformat() if source.last_used else None
                    ),
                    "created_at": source.created_at.isoformat(),
                }
                for source in sources
            ],
        }

    except Exception as e:
        logger.error(f"Failed to list sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/{source_id}")
async def get_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific MCP data source"""
    try:
        source = (
            db.query(MCPDataSource)
            .filter(
                MCPDataSource.id == source_id, MCPDataSource.user_id == current_user.id
            )
            .first()
        )

        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        return {
            "success": True,
            "source": {
                "id": source.id,
                "name": source.name,
                "type": source.type,
                "enabled": source.enabled,
                "config": source.config,
                "last_used": source.last_used.isoformat() if source.last_used else None,
                "created_at": source.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sources/{source_id}")
async def update_source(
    source_id: int,
    request: UpdateSourceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an MCP data source"""
    try:
        source = (
            db.query(MCPDataSource)
            .filter(
                MCPDataSource.id == source_id, MCPDataSource.user_id == current_user.id
            )
            .first()
        )

        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        # Update fields
        if request.name is not None:
            source.name = request.name
        if request.connection_string is not None:
            source.connection_string = request.connection_string
        if request.connection_config is not None:
            source.config["connection_config"] = request.connection_config
        if request.config is not None:
            source.config.update(request.config)
        if request.enabled is not None:
            source.enabled = request.enabled

        db.commit()
        db.refresh(source)

        # Re-register with MCP client if enabled
        if source.enabled:
            source_config = {
                "name": source.name,
                "type": source.type,
                "connection_string": source.connection_string,
                "connection_config": source.config.get("connection_config"),
                **source.config,
            }

            await mcp_client.register_source(
                source_id=str(source.id), config=source_config
            )

        return {
            "success": True,
            "source": {
                "id": source.id,
                "name": source.name,
                "type": source.type,
                "enabled": source.enabled,
                "created_at": source.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an MCP data source"""
    try:
        source = (
            db.query(MCPDataSource)
            .filter(
                MCPDataSource.id == source_id, MCPDataSource.user_id == current_user.id
            )
            .first()
        )

        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        # Unregister from MCP client
        await mcp_client.unregister_source(str(source_id))

        # Delete from database
        db.delete(source)
        db.commit()

        return {
            "success": True,
            "message": f"Source '{source.name}' deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/{source_id}/query")
async def query_source(
    source_id: int,
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute a query on an MCP data source

    Example for PostgreSQL:
    ```json
    {
        "query": "SELECT * FROM users LIMIT 10",
        "use_cache": true
    }
    ```

    Example for MongoDB:
    ```json
    {
        "query": "{&quot;database&quot;: &quot;mydb&quot;, &quot;collection&quot;: &quot;users&quot;, &quot;operation&quot;: &quot;find&quot;, &quot;args&quot;: {&quot;age&quot;: {&quot;$gt&quot;: 18}}}",
        "use_cache": true
    }
    ```
    """
    try:
        # Verify source exists and belongs to user
        source = (
            db.query(MCPDataSource)
            .filter(
                MCPDataSource.id == source_id, MCPDataSource.user_id == current_user.id
            )
            .first()
        )

        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        if not source.enabled:
            raise HTTPException(status_code=400, detail="Source is disabled")

        # Execute query
        start_time = datetime.utcnow()
        result = await mcp_client.query_source(
            source_id=str(source_id),
            query=request.query,
            params=request.params,
            use_cache=request.use_cache,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        # Record query in database
        db_query = MCPQuery(
            source_id=source_id,
            query=request.query[:1000],  # Truncate for storage
            result=result.get("data"),
            cached=result.get("cached", False),
            execution_time=result.get("execution_time", 0),
            executed_at=start_time,
        )

        db.add(db_query)

        # Update source last_used
        source.last_used = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "data": result.get("data"),
            "cached": result.get("cached", False),
            "execution_time": result.get("execution_time", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/{source_id}/test")
async def test_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Test connection to an MCP data source"""
    try:
        # Verify source exists and belongs to user
        source = (
            db.query(MCPDataSource)
            .filter(
                MCPDataSource.id == source_id, MCPDataSource.user_id == current_user.id
            )
            .first()
        )

        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        # Test connection
        result = await mcp_client.test_source(str(source_id))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/{source_id}/schema")
async def get_source_schema(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get schema information from an MCP data source"""
    try:
        # Verify source exists and belongs to user
        source = (
            db.query(MCPDataSource)
            .filter(
                MCPDataSource.id == source_id, MCPDataSource.user_id == current_user.id
            )
            .first()
        )

        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        if not source.enabled:
            raise HTTPException(status_code=400, detail="Source is disabled")

        # Get schema
        result = await mcp_client.get_schema(str(source_id))

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        return {"success": True, "schema": result.get("schema")}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def multi_query(
    request: MultiQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute multiple queries across different sources

    Example:
    ```json
    {
        "queries": [
            {
                "source_id": 1,
                "query": "SELECT * FROM users",
                "params": null
            },
            {
                "source_id": 2,
                "query": "{&quot;database&quot;: &quot;logs&quot;, &quot;collection&quot;: &quot;events&quot;, &quot;operation&quot;: &quot;find&quot;}",
                "params": null
            }
        ]
    }
    ```
    """
    try:
        results = []

        for query_item in request.queries:
            source_id = query_item.get("source_id")
            query = query_item.get("query")
            params = query_item.get("params")

            # Verify source
            source = (
                db.query(MCPDataSource)
                .filter(
                    MCPDataSource.id == source_id,
                    MCPDataSource.user_id == current_user.id,
                )
                .first()
            )

            if not source or not source.enabled:
                results.append(
                    {
                        "source_id": source_id,
                        "success": False,
                        "error": "Source not found or disabled",
                    }
                )
                continue

            # Execute query
            result = await mcp_client.query_source(
                source_id=str(source_id), query=query, params=params
            )

            results.append(
                {
                    "source_id": source_id,
                    "success": result.get("success"),
                    "data": result.get("data") if result.get("success") else None,
                    "error": result.get("error") if not result.get("success") else None,
                    "cached": result.get("cached", False),
                    "execution_time": result.get("execution_time", 0),
                }
            )

        return {"success": True, "results": results}

    except Exception as e:
        logger.error(f"Failed to execute multi-query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats")
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """Get MCP cache statistics"""
    try:
        stats = mcp_client.get_cache_stats()
        return {"success": True, "stats": stats}

    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache(
    source_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clear MCP cache"""
    try:
        if source_id:
            # Verify source belongs to user
            source = (
                db.query(MCPDataSource)
                .filter(
                    MCPDataSource.id == source_id,
                    MCPDataSource.user_id == current_user.id,
                )
                .first()
            )

            if not source:
                raise HTTPException(status_code=404, detail="Source not found")

        result = mcp_client.clear_cache(str(source_id) if source_id else None)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_query_history(
    source_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get query execution history"""
    try:
        query = (
            db.query(MCPQuery)
            .join(MCPDataSource)
            .filter(MCPDataSource.user_id == current_user.id)
        )

        if source_id:
            query = query.filter(MCPQuery.source_id == source_id)

        queries = query.order_by(MCPQuery.executed_at.desc()).limit(limit).all()

        return {
            "success": True,
            "history": [
                {
                    "id": q.id,
                    "source_id": q.source_id,
                    "query": q.query,
                    "cached": q.cached,
                    "execution_time": q.execution_time,
                    "executed_at": q.executed_at.isoformat(),
                }
                for q in queries
            ],
        }

    except Exception as e:
        logger.error(f"Failed to get query history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
