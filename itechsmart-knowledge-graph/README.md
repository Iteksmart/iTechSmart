# iTechSmart Knowledge Graph - Semantic Relationship Engine

## Overview

iTechSmart Knowledge Graph creates a semantic understanding of relationships across all IT assets, services, and dependencies. It enables the AI to understand how systems connect, predict impact of changes, and provide intelligent correlation of alerts and incidents.

## Key Features

### 🕸️ Relationship Mapping
- Automatic dependency discovery
- Service topology mapping
- Infrastructure relationship graph
- Application dependency analysis

### 🧠 Semantic Understanding
- Context-aware relationship analysis
- Impact prediction algorithms
- Root cause correlation
- Intelligent alert suppression

### 📊 Visual Analytics
- Interactive graph visualization
- Real-time topology updates
- Impact path analysis
- Dependency exploration

### 🔍 Smart Search
- Natural language graph queries
- Relationship-based search
- Contextual result filtering
- Semantic relevance ranking

### ⚡ Performance Optimization
- Graph traversal optimization
- Caching strategies
- Incremental updates
- Scalable architecture

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│   Graph Engine  │───▶│   Intelligence  │
│   (All Products)│    │   (Neo4j/AGE)   │    │   (Analytics)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
│   Relationship   │    │   Query Engine  │    │   API Layer     │
│   Discovery      │    │   (GraphQL)     │    │   (REST)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### Docker Deployment
```bash
cd itechsmart-knowledge-graph
docker-compose up -d
```

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

## Graph Schema

### Node Types
```cypher
// Infrastructure Nodes
(:Server {id, name, ip, os, cpu, memory, role, environment})
(:Database {id, name, type, version, size, environment})
(:Network {id, name, cidr, type, environment})
(:Storage {id, name, type, capacity, environment})

// Application Nodes
(:Application {id, name, version, environment, owner})
(:Service {id, name, type, endpoint, environment})
(:API {id, name, version, protocol, environment})

// Business Nodes
(:User {id, name, email, role, department})
(:Team {id, name, department, members})
(:Process {id, name, type, owner, criticality})

// iTechSmart Nodes
(:Product {id, name, version, capabilities})
(:Workflow {id, name, status, owner})
(:Incident {id, severity, status, created_at})
```

### Relationship Types
```cypher
// Infrastructure Relationships
- [:HOSTS]->      // Server hosts Application
- [:CONNECTS_TO]-> // Application connects to Database
- [:DEPENDS_ON]-> // Service depends on another Service
- [:MEMBER_OF]->  // Server member of Network

// Application Relationships
- [:USES]->       // Application uses API
- [:CALLS]->      // Service calls another Service
- [:TRIGGERS]->   // Process triggers Workflow
- [:OWNS]->       // User owns Application

// Impact Relationships
- [:IMPACTS]->    // Node impacts another Node
- [:AFFECTS]->    // Change affects dependent systems
- [:CORRELATES]-> // Incidents correlate with each other
- [:CAUSES]->     // Root cause relationships

// Business Relationships
- [:BELONGS_TO]-> // User belongs to Team
- [:RESPONSIBLE_FOR]-> // Team responsible for Application
- [:APPROVES]->   // User approves Workflow
```

## Integration Examples

### 1. Alert Correlation
```python
async def correlate_incidents(alerts):
    """Correlate related incidents using graph relationships"""
    
    correlated_groups = []
    
    for alert in alerts:
        # Find related nodes in graph
        affected_systems = await graph.query("""
            MATCH (alert:Incident {id: $alert_id})
            MATCH (alert)-[:IMPACTS]->(affected)
            RETURN affected
        """, {"alert_id": alert['id']})
        
        # Find other incidents affecting same systems
        related_incidents = await graph.query("""
            MATCH (other:Incident)-[:IMPACTS]->(affected)
            WHERE affected.id IN $affected_system_ids
            AND other.id <> $alert_id
            RETURN other
        """, {
            "affected_system_ids": [s['id'] for s in affected_systems],
            "alert_id": alert['id']
        })
        
        if related_incidents:
            correlated_groups.append({
                'primary_alert': alert,
                'related_incidents': related_incidents,
                'common_affected_systems': affected_systems
            })
    
    return correlated_groups
```

### 2. Impact Analysis
```python
async def predict_change_impact(change_request):
    """Predict impact of proposed changes using dependency graph"""
    
    target_system = change_request['target_system']
    
    # Find all downstream dependencies
    downstream_impact = await graph.query("""
        MATCH path = (start:System {id: $target_id})-[:DEPENDS_ON*1..5]->(downstream)
        RETURN DISTINCT downstream, length(path) as distance
        ORDER BY distance
    """, {"target_id": target_system})
    
    # Find upstream dependencies
    upstream_impact = await graph.query("""
        MATCH path = (upstream)-[:DEPENDS_ON*1..5]->(end:System {id: $target_id})
        RETURN DISTINCT upstream, length(path) as distance
        ORDER BY distance
    """, {"target_id": target_system})
    
    # Calculate business impact
    business_impact = await graph.query("""
        MATCH (system:System {id: $target_id})
        OPTIONAL MATCH (system)<-[:OWNS]-(owner:User)
        OPTIONAL MATCH (system)<-[:RESPONSIBLE_FOR]-(team:Team)
        OPTIONAL MATCH (system)-[:SUPPORTS]-(process:Process)
        RETURN owner, team, collect(process) as supported_processes
    """, {"target_id": target_system})
    
    return {
        'downstream_systems': downstream_impact,
        'upstream_systems': upstream_impact,
        'business_impact': business_impact,
        'total_affected_count': len(downstream_impact) + len(upstream_impact)
    }
```

### 3. Root Cause Analysis
```python
async def analyze_root_cause(incident_id):
    """Analyze root cause using graph relationships"""
    
    # Get incident details
    incident = await graph.query("""
        MATCH (incident:Incident {id: $id})
        RETURN incident
    """, {"id": incident_id})
    
    # Find potential root causes
    potential_causes = await graph.query("""
        MATCH (incident:Incident {id: $id})-[:IMPACTS]->(affected)
        MATCH (potential_cause)-[:AFFECTS]->(affected)
        WHERE potential_cause:Change OR potential_cause:Deployment
        RETURN potential_cause, affected
    """, {"id": incident_id})
    
    # Find correlation patterns
    correlation_patterns = await graph.query("""
        MATCH (incident:Incident {id: $id})
        MATCH (similar:Incident)-[:IMPACTS]->(same_affected)
        WHERE similar.id <> incident.id
        AND (incident)-[:IMPACTS]->(same_affected)
        RETURN similar, same_affected
        ORDER BY similar.created_at DESC
        LIMIT 10
    """, {"id": incident_id})
    
    return {
        'incident': incident,
        'potential_causes': potential_causes,
        'correlation_patterns': correlation_patterns
    }
```

## API Endpoints

### Graph Management
- `POST /api/v1/graph/sync` - Sync with all iTechSmart products
- `GET /api/v1/graph/schema` - Get graph schema
- `POST /api/v1/graph/nodes` - Create/update nodes
- `POST /api/v1/graph/relationships` - Create relationships

### Query Operations
- `POST /api/v1/query/cypher` - Execute Cypher queries
- `POST /api/v1/query/impact` - Impact analysis queries
- `POST /api/v1/query/correlation` - Alert correlation
- `POST /api/v1/query/dependencies` - Dependency analysis

### Analytics
- `GET /api/v1/analytics/topology` - Get topology metrics
- `GET /api/v1/analytics/dependencies` - Dependency analysis
- `GET /api/v1/analytics/risks` - Risk assessment
- `GET /api/v1/analytics/performance` - Graph performance

### Visualization
- `GET /api/v1/visualization/subgraph` - Get subgraph for visualization
- `GET /api/v1/visualization/topology` - Get full topology
- `GET /api/v1/visualization/impact-path` - Get impact visualization
- `GET /api/v1/visualization/dependencies` - Get dependency graph

## Data Sources Integration

### iTechSmart Products
```yaml
data_sources:
  itechsmart_ninja:
    type: "automation_agent"
    data: ["executed_workflows", "managed_systems", "dependencies"]
    sync_frequency: "realtime"
    
  itechsmart_sentinel:
    type: "monitoring"
    data: ["metrics", "alerts", "incidents", "dependencies"]
    sync_frequency: "realtime"
    
  itechsmart_cloud:
    type: "infrastructure"
    data: ["servers", "databases", "networks", "storage"]
    sync_frequency: "hourly"
    
  itechsmart_workflow:
    type: "automation"
    data: ["workflows", "steps", "dependencies"]
    sync_frequency: "realtime"
    
  itechsmart_passport:
    type: "identity"
    data: ["users", "teams", "permissions", "roles"]
    sync_frequency: "hourly"
```

### External Systems
```yaml
external_sources:
  aws:
    type: "cloud_provider"
    data: ["ec2_instances", "rds_databases", "vpcs", "security_groups"]
    auth: "iam_role"
    
  kubernetes:
    type: "orchestration"
    data: ["pods", "services", "deployments", "configmaps"]
    auth: "service_account"
    
  active_directory:
    type: "directory_service"
    data: ["users", "groups", "computers", "ous"]
    auth: "ldap_bind"
```

## Performance Optimization

### Graph Partitioning
```python
# Partition graph by environment
partition_strategy = {
    "production": {
        "priority": "high",
        "update_frequency": "realtime",
        "retention": "indefinite"
    },
    "staging": {
        "priority": "medium", 
        "update_frequency": "hourly",
        "retention": "90_days"
    },
    "development": {
        "priority": "low",
        "update_frequency": "daily", 
        "retention": "30_days"
    }
}
```

### Caching Strategy
```python
# Multi-level caching
cache_config = {
    "l1_cache": {
        "type": "memory",
        "ttl": 300,  # 5 minutes
        "size": "1GB"
    },
    "l2_cache": {
        "type": "redis",
        "ttl": 3600,  # 1 hour
        "size": "10GB"
    },
    "l3_cache": {
        "type": "disk",
        "ttl": 86400,  # 24 hours
        "size": "100GB"
    }
}
```

## Advanced Features

### 1. Intelligent Alert Suppression
```python
async def suppress_redundant_alerts(new_alert):
    """Suppress redundant alerts based on graph relationships"""
    
    # Check if parent alert exists
    parent_alerts = await graph.query("""
        MATCH (parent:Incident)-[:CAUSES]->(child:Incident)
        WHERE child.id = $alert_id
        AND parent.status = 'active'
        RETURN parent
    """, {"alert_id": new_alert['id']})
    
    if parent_alerts:
        return {
            'action': 'suppress',
            'reason': 'Child of active parent incident',
            'parent_incident': parent_alerts[0]
        }
    
    # Check for duplicate alerts on same system
    duplicate_alerts = await graph.query("""
        MATCH (existing:Incident)-[:IMPACTS]->(system)
        WHERE system.id IN $affected_systems
        AND existing.type = $alert_type
        AND existing.status = 'active'
        AND existing.created_at > $time_window
        RETURN existing
    """, {
        'affected_systems': new_alert['affected_systems'],
        'alert_type': new_alert['type'],
        'time_window': datetime.utcnow() - timedelta(minutes=5)
    })
    
    if duplicate_alerts:
        return {
            'action': 'suppress',
            'reason': 'Duplicate alert on same systems',
            'duplicate_alert': duplicate_alerts[0]
        }
    
    return {'action': 'create', 'reason': 'No suppression applicable'}
```

### 2. Predictive Impact Analysis
```python
async def predict_cascade_impact(initial_failure):
    """Predict cascade failure impact"""
    
    # Calculate impact propagation
    cascade_prediction = await graph.query("""
        MATCH path = (failure:System)-[:DEPENDS_ON*1..10]->(dependent:System)
        WHERE failure.id = $initial_failure_id
        WITH dependent, length(path) as hop_count
        MATCH (dependent)<-[:OWNS]-(owner:User)
        MATCH (dependent)<-[:RESPONSIBLE_FOR]-(team:Team)
        RETURN dependent, hop_count, owner, team
        ORDER BY hop_count
    """, {"initial_failure_id": initial_failure['id']})
    
    # Calculate business impact per hop
    impact_by_hop = {}
    for item in cascade_prediction:
        hop = item['hop_count']
        if hop not in impact_by_hop:
            impact_by_hop[hop] = {
                'systems': [],
                'users': set(),
                'teams': set(),
                'business_processes': []
            }
        
        impact_by_hop[hop]['systems'].append(item['dependent'])
        impact_by_hop[hop]['users'].add(item['owner']['id'])
        impact_by_hop[hop]['teams'].add(item['team']['id'])
    
    # Calculate probability of cascade
    cascade_probability = calculate_cascade_probability(impact_by_hop)
    
    return {
        'cascade_prediction': impact_by_hop,
        'cascade_probability': cascade_probability,
        'total_potential_impact': sum(len(imp['systems']) for imp in impact_by_hop.values())
    }
```

### 3. Semantic Search
```python
async def semantic_search(query, context=None):
    """Semantic search across the graph"""
    
    # Parse natural language query
    parsed_query = parse_natural_language(query)
    
    # Convert to graph query
    cypher_query = natural_language_to_cypher(parsed_query)
    
    # Execute with ranking
    results = await graph.query(cypher_query)
    
    # Apply semantic relevance ranking
    ranked_results = apply_semantic_ranking(results, parsed_query, context)
    
    return ranked_results
```

## Monitoring & Analytics

### Graph Health Metrics
```yaml
health_metrics:
  node_count:
    description: "Total number of nodes in graph"
    alert_threshold: 1000000
    
  relationship_count:
    description: "Total number of relationships"
    alert_threshold: 5000000
    
  query_performance:
    description: "Average query response time"
    alert_threshold: 1000  # milliseconds
    
  sync_lag:
    description: "Data synchronization lag"
    alert_threshold: 300  # seconds
```

### Business Intelligence
```yaml
bi_metrics:
  dependency_depth:
    description: "Average dependency chain depth"
    
  critical_path_analysis:
    description: "Critical system dependencies"
    
  single_point_failure:
    description: "Single points of failure"
    
  change_impact_radius:
    description: "Average impact radius for changes"
```

## Security & Compliance

### Access Control
```python
# Role-based graph access
access_control = {
    "read_only": {
        "permissions": ["read"],
        "node_filters": ["environment != 'sensitive'"],
        "relationship_filters": []
    },
    "operator": {
        "permissions": ["read", "write"],
        "node_filters": [],
        "relationship_filters": []
    },
    "admin": {
        "permissions": ["read", "write", "delete", "schema"],
        "node_filters": [],
        "relationship_filters": []
    }
}
```

### Data Privacy
- **Sensitive Data Masking**: Automatically mask sensitive information
- **Audit Logging**: Log all graph queries and modifications
- **Data Retention**: Automatic cleanup of historical data
- **Encryption**: Encrypt sensitive relationships and properties

## Documentation

- [Schema Documentation](./docs/SCHEMA.md)
- [Query Guide](./docs/QUERY_GUIDE.md)
- [API Documentation](./docs/API_DOCUMENTATION.md)
- [Integration Guide](./docs/INTEGRATION_GUIDE.md)

## License

© 2025 iTechSmart. All rights reserved.