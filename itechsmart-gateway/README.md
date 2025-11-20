# iTechSmart Gateway - Unified API Gateway

## Overview

iTechSmart Gateway serves as the single entry point for all iTechSmart services, providing unified authentication, rate limiting, routing, and observability across the entire 42+ product ecosystem. It ensures consistent security, performance, and user experience across all services.

## Key Features

### 🚪 Unified Entry Point
- Single API endpoint for all services
- Intelligent routing and load balancing
- Protocol translation (REST, GraphQL, WebSocket)
- Version management and backward compatibility

### 🔐 Security & Authentication
- Centralized authentication and authorization
- OAuth 2.0, JWT, API key support
- Role-based access control (RBAC)
- Service-to-service authentication

### ⚡ Performance Optimization
- Request/response caching
- Rate limiting and throttling
- Connection pooling
- Request compression and optimization

### 📊 Observability & Monitoring
- Centralized logging and metrics
- Request tracing across services
- Performance analytics
- Error tracking and alerting

### 🔄 Service Discovery
- Automatic service registration
- Health checking and failover
- Dynamic routing updates
- Service version management

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │───▶│   iTechSmart    │───▶│   Target        │
│   Applications  │    │   Gateway       │    │   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Security &    │
                       │   Auth Layer    │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Routing &     │
                       │   Load Balance  │
                       └─────────────────┘
```

## Quick Start

### Docker Deployment
```bash
cd itechsmart-gateway
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

## API Gateway Configuration

### Route Configuration
```yaml
routes:
  # iTechSmart Arbiter
  - path: "/api/v1/arbiter/*"
    service: "itechsmart-arbiter"
    methods: ["GET", "POST", "PUT", "DELETE"]
    auth_required: true
    rate_limit: 1000  # requests per hour
    
  # iTechSmart Digital Twin
  - path: "/api/v1/digital-twin/*"
    service: "itechsmart-digital-twin"
    methods: ["GET", "POST", "PUT", "DELETE"]
    auth_required: true
    rate_limit: 500
    timeout: 300000  # 5 minutes (long-running simulations)
    
  # iTechSmart Generative Workflow
  - path: "/api/v1/workflow/*"
    service: "itechsmart-generative-workflow"
    methods: ["GET", "POST", "PUT", "DELETE"]
    auth_required: true
    rate_limit: 100
    
  # iTechSmart Ninja
  - path: "/api/v1/ninja/*"
    service: "itechsmart-ninja"
    methods: ["GET", "POST", "PUT", "DELETE"]
    auth_required: true
    rate_limit: 2000
    
  # Public endpoints
  - path: "/api/v1/public/*"
    service: "itechsmart-public"
    methods: ["GET"]
    auth_required: false
    rate_limit: 10000
```

### Service Discovery
```yaml
service_discovery:
  type: "consul"
  consul:
    host: "consul.itechsmart.local"
    port: 8500
    datacenter: "dc1"
    
  health_check:
    interval: 10  # seconds
    timeout: 5     # seconds
    deregister_after: 30  # seconds
    
  services:
    - name: "itechsmart-arbiter"
      port: 8080
      health_check: "/health"
      
    - name: "itechsmart-digital-twin"
      port: 8090
      health_check: "/health"
      
    - name: "itechsmart-generative-workflow"
      port: 8100
      health_check: "/health"
```

## Authentication & Authorization

### JWT Authentication
```python
# JWT Token Structure
jwt_payload = {
    "sub": "user_id",
    "email": "user@company.com",
    "roles": ["admin", "operator"],
    "permissions": [
        "arbiter:read",
        "arbiter:write",
        "ninja:execute",
        "digital-twin:simulate"
    ],
    "iat": 1640995200,
    "exp": 1641081600,
    "iss": "itechsmart-gateway",
    "aud": "itechsmart-services"
}
```

### Role-Based Access Control
```yaml
rbac:
  roles:
    admin:
      permissions: ["*"]
      services: ["*"]
      
    operator:
      permissions: ["read", "write", "execute"]
      services: ["ninja", "sentinel", "workflow"]
      
    analyst:
      permissions: ["read"]
      services: ["arbiter", "analytics", "pulse"]
      
    developer:
      permissions: ["read", "write", "execute"]
      services: ["digital-twin", "generative-workflow", "sandbox"]
      
  service_permissions:
    itechsmart-arbiter:
      admin: ["read", "write", "delete"]
      operator: ["read", "write"]
      analyst: ["read"]
      
    itechsmart-ninja:
      admin: ["read", "write", "execute", "delete"]
      operator: ["read", "write", "execute"]
      developer: ["read", "write", "execute"]
```

## Rate Limiting Configuration

### Rate Limiting Strategies
```python
rate_limiting = {
    "user_based": {
        "window": "1h",
        "limits": {
            "admin": 10000,
            "operator": 5000,
            "analyst": 1000,
            "developer": 2000
        }
    },
    "service_based": {
        "itechsmart-ninja": 2000,
        "itechsmart-digital-twin": 500,
        "itechsmart-generative-workflow": 100,
        "itechsmart-arbiter": 1000
    },
    "endpoint_based": {
        "/api/v1/ninja/execute": 100,
        "/api/v1/digital-twin/simulation": 50,
        "/api/v1/workflow/generate": 25
    },
    "global": {
        "total_requests": 100000,
        "window": "1h"
    }
}
```

## API Endpoints

### Gateway Management
- `GET /api/v1/gateway/status` - Gateway health status
- `GET /api/v1/gateway/routes` - List all routes
- `POST /api/v1/gateway/routes` - Add new route
- `PUT /api/v1/gateway/routes/{id}` - Update route
- `DELETE /api/v1/gateway/routes/{id}` - Delete route

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `GET /api/v1/auth/me` - Get current user info

### Service Discovery
- `GET /api/v1/services` - List all services
- `GET /api/v1/services/{name}` - Get service details
- `GET /api/v1/services/{name}/health` - Check service health
- `POST /api/v1/services/{name}/register` - Register service

### Monitoring & Analytics
- `GET /api/v1/analytics/metrics` - Get performance metrics
- `GET /api/v1/analytics/requests` - Request analytics
- `GET /api/v1/analytics/errors` - Error analytics
- `GET /api/v1/analytics/users` - User activity analytics

## Advanced Features

### 1. Request Transformation
```python
async def transform_request(request, target_service):
    """Transform request format for target service"""
    
    transformations = {
        "itechsmart-ninja": {
            "headers": {
                "X-API-Version": "v1",
                "X-Request-ID": generate_request_id()
            },
            "body": normalize_ninja_request
        },
        "itechsmart-digital-twin": {
            "headers": {
                "Content-Type": "application/json",
                "X-Simulation-Timeout": "300000"
            },
            "body": validate_simulation_request
        }
    }
    
    transformer = transformations.get(target_service, {})
    
    # Apply transformations
    if "headers" in transformer:
        request.headers.update(transformer["headers"])
    
    if "body" in transformer:
        request.body = transformer["body"](request.body)
    
    return request
```

### 2. Response Caching
```python
cache_config = {
    "default_ttl": 300,  # 5 minutes
    "max_size": 1000,   # max cached responses
    
    "cacheable_endpoints": {
        "GET:/api/v1/services": 60,
        "GET:/api/v1/gateway/status": 30,
        "GET:/api/v1/analytics/metrics": 120,
        "GET:/api/v1/auth/me": 300
    },
    
    "cache_keys": {
        "user_specific": ["GET:/api/v1/auth/me"],
        "role_specific": ["GET:/api/v1/services"],
        "global": ["GET:/api/v1/gateway/status"]
    }
}

async def get_cached_response(cache_key):
    """Get response from cache"""
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

async def cache_response(cache_key, response, ttl):
    """Cache response with TTL"""
    await redis_client.setex(
        cache_key,
        ttl,
        json.dumps({
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.body
        })
    )
```

### 3. Circuit Breaker Pattern
```python
circuit_breaker_config = {
    "failure_threshold": 5,      # Open circuit after 5 failures
    "recovery_timeout": 60,      # Wait 60 seconds before trying again
    "expected_exception": Exception,
    "success_threshold": 3       # Close circuit after 3 successes
}

class CircuitBreaker:
    def __init__(self, service_name):
        self.service_name = service_name
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > circuit_breaker_config["recovery_timeout"]:
                self.state = "HALF_OPEN"
            else:
                raise ServiceUnavailableError(f"Circuit breaker OPEN for {self.service_name}")
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= circuit_breaker_config["failure_threshold"]:
            self.state = "OPEN"
```

### 4. Distributed Tracing
```python
async def trace_request(request, handler):
    """Distributed tracing for requests"""
    
    # Generate or extract trace ID
    trace_id = request.headers.get("X-Trace-ID") or generate_trace_id()
    span_id = generate_span_id()
    
    # Start span
    span = {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": request.headers.get("X-Parent-Span-ID"),
        "operation_name": f"{request.method} {request.path}",
        "start_time": time.time(),
        "tags": {
            "http.method": request.method,
            "http.url": str(request.url),
            "user_agent": request.headers.get("User-Agent"),
            "service": request.headers.get("X-Service-Name", "unknown")
        }
    }
    
    try:
        # Add trace headers to downstream request
        request.headers["X-Trace-ID"] = trace_id
        request.headers["X-Parent-Span-ID"] = span_id
        
        # Execute request
        response = await handler(request)
        
        # Complete span
        span["end_time"] = time.time()
        span["duration"] = span["end_time"] - span["start_time"]
        span["status_code"] = response.status_code
        span["success"] = 200 <= response.status_code < 400
        
        # Send span to tracing system
        await send_span_to_jaeger(span)
        
        return response
        
    except Exception as e:
        span["end_time"] = time.time()
        span["duration"] = span["end_time"] - span["start_time"]
        span["error"] = str(e)
        span["success"] = False
        
        await send_span_to_jaeger(span)
        raise
```

## Performance Optimization

### Connection Pooling
```python
pool_config = {
    "http_connections": {
        "max_size": 100,
        "min_size": 10,
        "max_idle_time": 300,
        "max_lifetime": 1800
    },
    "database_connections": {
        "max_size": 20,
        "min_size": 5,
        "max_idle_time": 600
    },
    "redis_connections": {
        "max_size": 50,
        "min_size": 5,
        "max_idle_time": 300
    }
}
```

### Request Compression
```python
compression_config = {
    "enabled": True,
    "algorithms": ["gzip", "deflate", "br"],
    "min_size": 1024,  # Only compress responses > 1KB
    "compressible_types": [
        "application/json",
        "text/html",
        "text/css",
        "application/javascript"
    ]
}
```

## Monitoring & Observability

### Metrics Collection
```yaml
metrics:
  request_metrics:
    - "request_count_total"
    - "request_duration_seconds"
    - "request_size_bytes"
    - "response_size_bytes"
    - "response_status_codes"
    
  service_metrics:
    - "service_up_total"
    - "service_response_time_seconds"
    - "service_error_rate"
    
  gateway_metrics:
    - "gateway_cpu_usage"
    - "gateway_memory_usage"
    - "gateway_connection_count"
    - "circuit_breaker_state"
    
  security_metrics:
    - "auth_success_total"
    - "auth_failure_total"
    - "rate_limit_violations_total"
    - "blocked_requests_total"
```

### Alerting Rules
```yaml
alerts:
  high_error_rate:
    condition: "error_rate > 0.05"
    duration: "5m"
    severity: "warning"
    
  service_down:
    condition: "service_up == 0"
    duration: "1m"
    severity: "critical"
    
  high_latency:
    condition: "p95_response_time > 1000"
    duration: "10m"
    severity: "warning"
    
  rate_limit_exceeded:
    condition: "rate_limit_violations > 100"
    duration: "1m"
    severity: "info"
```

## Security Features

### API Security
```python
security_config = {
    "cors": {
        "allowed_origins": ["https://app.itechsmart.com", "https://dashboard.itechsmart.com"],
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allowed_headers": ["Content-Type", "Authorization", "X-API-Key"],
        "max_age": 86400
    },
    
    "csrf": {
        "enabled": True,
        "token_header": "X-CSRF-Token",
        "cookie_name": "csrf_token"
    },
    
    "security_headers": {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    },
    
    "input_validation": {
        "max_request_size": 10485760,  # 10MB
        "max_header_size": 8192,       # 8KB
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
    }
}
```

## Configuration Management

### Environment Configuration
```yaml
environments:
  production:
    debug: false
    log_level: "INFO"
    redis_url: "redis://redis-cluster:6379"
    database_url: "postgresql://user:pass@postgres-cluster:5432/gateway"
    
  staging:
    debug: true
    log_level: "DEBUG"
    redis_url: "redis://redis-staging:6379"
    database_url: "postgresql://user:pass@postgres-staging:5432/gateway"
    
  development:
    debug: true
    log_level: "DEBUG"
    redis_url: "redis://localhost:6379"
    database_url: "postgresql://user:pass@localhost:5432/gateway"
```

## Deployment

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: itechsmart-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: itechsmart-gateway
  template:
    metadata:
      labels:
        app: itechsmart-gateway
    spec:
      containers:
      - name: gateway
        image: itechsmart/gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: DATABASE_URL
          value: "postgresql://user:pass@postgres:5432/gateway"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Documentation

- [API Documentation](./docs/API_DOCUMENTATION.md)
- [Configuration Guide](./docs/CONFIGURATION_GUIDE.md)
- [Security Guide](./docs/SECURITY_GUIDE.md)
- [Monitoring Guide](./docs/MONITORING_GUIDE.md)

## License

© 2025 iTechSmart. All rights reserved.