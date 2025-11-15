"""
iTechSmart Connect - API Management & Integration Platform
API gateway, rate limiting, versioning, and developer portal
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4


class APIStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class API:
    def __init__(self, api_id: str, name: str, version: str, endpoint: str):
        self.api_id = api_id
        self.name = name
        self.version = version
        self.endpoint = endpoint
        self.status = APIStatus.ACTIVE
        self.rate_limit = 1000
        self.requests_count = 0
        self.created_at = datetime.utcnow()
        self.documentation = ""


class APIKey:
    def __init__(self, key_id: str, api_id: str, owner: str):
        self.key_id = key_id
        self.api_id = api_id
        self.owner = owner
        self.key = f"sk_{uuid4().hex}"
        self.is_active = True
        self.rate_limit = 100
        self.requests_today = 0
        self.created_at = datetime.utcnow()


class Webhook:
    def __init__(self, webhook_id: str, url: str, events: List[str]):
        self.webhook_id = webhook_id
        self.url = url
        self.events = events
        self.is_active = True
        self.secret = uuid4().hex
        self.deliveries = 0
        self.failures = 0


class ConnectEngine:
    def __init__(self):
        self.apis: Dict[str, API] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.webhooks: Dict[str, Webhook] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}
    
    def register_api(self, name: str, version: str, endpoint: str, documentation: str) -> str:
        api_id = str(uuid4())
        api = API(api_id, name, version, endpoint)
        api.documentation = documentation
        self.apis[api_id] = api
        return api_id
    
    def create_api_key(self, api_id: str, owner: str, rate_limit: int = 100) -> Dict[str, str]:
        if api_id not in self.apis:
            raise ValueError("API not found")
        
        key_id = str(uuid4())
        api_key = APIKey(key_id, api_id, owner)
        api_key.rate_limit = rate_limit
        self.api_keys[key_id] = api_key
        
        return {
            "key_id": key_id,
            "api_key": api_key.key,
            "rate_limit": rate_limit
        }
    
    def check_rate_limit(self, key_id: str) -> bool:
        """Check if request is within rate limit"""
        api_key = self.api_keys.get(key_id)
        if not api_key:
            return False
        
        if key_id not in self.rate_limits:
            self.rate_limits[key_id] = []
        
        # Clean old requests (older than 1 minute)
        now = datetime.utcnow()
        self.rate_limits[key_id] = [
            req_time for req_time in self.rate_limits[key_id]
            if (now - req_time).seconds < 60
        ]
        
        # Check limit
        if len(self.rate_limits[key_id]) >= api_key.rate_limit:
            return False
        
        self.rate_limits[key_id].append(now)
        api_key.requests_today += 1
        return True
    
    def create_webhook(self, url: str, events: List[str]) -> str:
        webhook_id = str(uuid4())
        webhook = Webhook(webhook_id, url, events)
        self.webhooks[webhook_id] = webhook
        return webhook_id
    
    def trigger_webhook(self, webhook_id: str, event: str, payload: Dict[str, Any]) -> bool:
        webhook = self.webhooks.get(webhook_id)
        if not webhook or not webhook.is_active:
            return False
        
        if event not in webhook.events:
            return False
        
        # Simulate webhook delivery
        webhook.deliveries += 1
        return True
    
    def get_api_analytics(self, api_id: str) -> Dict[str, Any]:
        api = self.apis.get(api_id)
        if not api:
            return {}
        
        keys = [k for k in self.api_keys.values() if k.api_id == api_id]
        total_requests = sum(k.requests_today for k in keys)
        
        return {
            "api_id": api_id,
            "name": api.name,
            "version": api.version,
            "total_keys": len(keys),
            "total_requests": total_requests,
            "status": api.status.value
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_apis": len(self.apis),
            "active_apis": len([a for a in self.apis.values() if a.status == APIStatus.ACTIVE]),
            "total_api_keys": len(self.api_keys),
            "total_webhooks": len(self.webhooks),
            "active_webhooks": len([w for w in self.webhooks.values() if w.is_active])
        }


connect_engine = ConnectEngine()