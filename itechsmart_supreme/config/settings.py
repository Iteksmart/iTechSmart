"""
Configuration Management for iTechSmart Supreme
"""
import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "iTechSmart Supreme"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # Database
    database_url: str = "postgresql://user:pass@localhost:5432/itechsmart"
    redis_url: str = "redis://localhost:6379/0"
    
    # AI Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Integrations
    ansible_config_path: Optional[str] = None
    vault_url: Optional[str] = None
    vault_token: Optional[str] = None
    prometheus_url: str = "http://localhost:9090"
    grafana_url: str = "http://localhost:3000"
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self.settings = Settings()
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    self._config = yaml.safe_load(f)
                elif self.config_path.endswith('.json'):
                    self._config = json.load(f)
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                yaml.dump(self._config, f)
            elif self.config_path.endswith('.json'):
                json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
    
    def update(self, config: Dict[str, Any]):
        """Update configuration"""
        self._config.update(config)

# Global config instance
config = ConfigManager()
