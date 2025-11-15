# Feature 10: MCP Data Sources - Complete Specification

## Overview
Model Context Protocol (MCP) integration for connecting AI models to external data sources, APIs, and tools. Enables models to access real-time data and perform actions.

---

## Capabilities

### Supported Data Sources
- **Databases** - PostgreSQL, MySQL, MongoDB, Redis
- **APIs** - REST, GraphQL, WebSocket
- **File Systems** - Local, S3, Google Drive, Dropbox
- **Search Engines** - Elasticsearch, Algolia
- **Message Queues** - RabbitMQ, Kafka
- **Custom Sources** - Plugin system

### Features
- Dynamic data source registration
- Query optimization
- Caching layer
- Access control
- Rate limiting
- Data transformation
- Real-time updates

---

## API Endpoints

```
POST   /api/mcp/sources/register
GET    /api/mcp/sources
GET    /api/mcp/sources/{source_id}
PUT    /api/mcp/sources/{source_id}
DELETE /api/mcp/sources/{source_id}
POST   /api/mcp/sources/{source_id}/query
POST   /api/mcp/sources/{source_id}/test
GET    /api/mcp/sources/{source_id}/schema
POST   /api/mcp/query
GET    /api/mcp/cache/stats
POST   /api/mcp/cache/clear
```

---

## Database Models

```python
class MCPDataSource(Base):
    __tablename__ = "mcp_data_sources"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    type = Column(String)  # database, api, filesystem, etc.
    connection_string = Column(String, encrypted=True)
    config = Column(JSON)
    enabled = Column(Boolean, default=True)
    last_used = Column(DateTime)
    created_at = Column(DateTime)

class MCPQuery(Base):
    __tablename__ = "mcp_queries"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("mcp_data_sources.id"))
    query = Column(Text)
    result = Column(JSON)
    cached = Column(Boolean)
    execution_time = Column(Float)
    executed_at = Column(DateTime)
```

---

## VS Code Commands

1. `iTechSmart: Register MCP Source`
2. `iTechSmart: List MCP Sources`
3. `iTechSmart: Query MCP Source`
4. `iTechSmart: Test MCP Connection`
5. `iTechSmart: View MCP Schema`

---

## Terminal Commands

```bash
mcp register <name> <type>  # Register source
mcp list                    # List sources
mcp query <id> <query>      # Query source
mcp test <id>              # Test connection
mcp schema <id>            # View schema
```

---

## Implementation Steps

**Total Time**: 7-8 hours

### Phase 1: Backend (6 hours)
1. Create `mcp_client.py` (3 hours)
2. Create `mcp.py` API (2 hours)
3. Add database models (1 hour)

### Phase 2: Frontend (1 hour)
1. Create `mcpCommands.ts`

### Phase 3: Testing (1 hour)

---

## Dependencies

```
sqlalchemy>=2.0.0
pymongo>=4.5.0
redis>=5.0.0
elasticsearch>=8.10.0
boto3>=1.28.0  # For S3
```

---

## Example Usage

```python
# Register database source
source = await register_mcp_source(
    name="Production DB",
    type="postgresql",
    connection_string="postgresql://user:pass@host/db"
)

# Query source
result = await query_mcp_source(
    source_id=source.id,
    query="SELECT * FROM users LIMIT 10"
)
```

---

## Status

**Specification**: ✅ Complete
**Skeleton Code**: ✅ Provided
**Implementation**: ⏳ Pending
**Estimated Time**: 7-8 hours