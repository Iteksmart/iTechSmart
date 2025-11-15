"""
iTechSmart Integration Marketplace - Integration Hub Engine
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4


class IntegrationType(str, Enum):
    API = "api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE = "file"
    MESSAGING = "messaging"


class Integration:
    def __init__(self, integration_id: str, name: str, provider: str, integration_type: IntegrationType):
        self.integration_id = integration_id
        self.name = name
        self.provider = provider
        self.integration_type = integration_type
        self.is_active = False
        self.config = {}
        self.created_at = datetime.utcnow()
        self.installs = 0
        self.rating = 0.0


class MarketplaceEngine:
    def __init__(self):
        self.integrations: Dict[str, Integration] = {}
        self.installed: Dict[str, List[str]] = {}
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize popular integrations"""
        popular = [
            ("Salesforce", "salesforce", IntegrationType.API),
            ("Slack", "slack", IntegrationType.WEBHOOK),
            ("GitHub", "github", IntegrationType.API),
            ("Stripe", "stripe", IntegrationType.API),
            ("Twilio", "twilio", IntegrationType.API),
            ("SendGrid", "sendgrid", IntegrationType.API),
            ("AWS S3", "aws", IntegrationType.API),
            ("Google Drive", "google", IntegrationType.API),
            ("Dropbox", "dropbox", IntegrationType.API),
            ("Zoom", "zoom", IntegrationType.API),
        ]
        
        for name, provider, int_type in popular:
            integration_id = str(uuid4())
            integration = Integration(integration_id, name, provider, int_type)
            integration.rating = 4.5
            integration.installs = 1000
            self.integrations[integration_id] = integration
    
    def list_integrations(self, integration_type: Optional[IntegrationType] = None) -> List[Dict[str, Any]]:
        integrations = list(self.integrations.values())
        if integration_type:
            integrations = [i for i in integrations if i.integration_type == integration_type]
        
        return [{
            "integration_id": i.integration_id,
            "name": i.name,
            "provider": i.provider,
            "type": i.integration_type.value,
            "installs": i.installs,
            "rating": i.rating
        } for i in integrations]
    
    def install_integration(self, user_id: str, integration_id: str, config: Dict[str, Any]) -> bool:
        integration = self.integrations.get(integration_id)
        if not integration:
            return False
        
        if user_id not in self.installed:
            self.installed[user_id] = []
        
        self.installed[user_id].append(integration_id)
        integration.installs += 1
        integration.config = config
        integration.is_active = True
        return True
    
    def get_installed(self, user_id: str) -> List[Dict[str, Any]]:
        integration_ids = self.installed.get(user_id, [])
        return [
            {
                "integration_id": i.integration_id,
                "name": i.name,
                "provider": i.provider,
                "is_active": i.is_active
            }
            for i in [self.integrations.get(iid) for iid in integration_ids]
            if i
        ]


marketplace_engine = MarketplaceEngine()