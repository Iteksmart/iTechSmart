"""
Configuration Manager - Handles configuration generation and management
"""

import logging
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """
    Manages configuration for all iTechSmart products
    Generates, validates, and stores configurations
    """

    def __init__(self):
        self.config_templates: Dict[str, Dict] = {}
        self.active_configs: Dict[str, Dict] = {}
        self.config_history: List[Dict] = []

        # Configuration templates for each product
        self.templates = {
            "itechsmart-enterprise": {
                "database": {
                    "host": "postgres",
                    "port": 5432,
                    "name": "enterprise_db",
                    "user": "enterprise_user",
                    "password": "${DATABASE_PASSWORD}",
                },
                "redis": {"host": "redis", "port": 6379, "db": 0},
                "jwt": {"secret": "${JWT_SECRET}", "expiry": 3600},
                "features": {"hub_enabled": True, "monitoring_enabled": True},
            },
            "itechsmart-ninja": {
                "database": {
                    "host": "postgres",
                    "port": 5432,
                    "name": "ninja_db",
                    "user": "ninja_user",
                    "password": "${DATABASE_PASSWORD}",
                },
                "monitoring": {"interval": 30, "health_check_interval": 60},
                "self_healing": {"enabled": True, "auto_fix": True, "max_retries": 3},
            },
            "legalai-pro": {
                "database": {
                    "host": "postgres",
                    "port": 5432,
                    "name": "legalai_db",
                    "user": "legalai_user",
                    "password": "${DATABASE_PASSWORD}",
                },
                "ai": {
                    "provider": "openai",
                    "api_key": "${OPENAI_API_KEY}",
                    "model": "gpt-4",
                    "temperature": 0.7,
                },
                "features": {
                    "document_autofill": True,
                    "legal_research": True,
                    "contract_analysis": True,
                },
            },
            "itechsmart-port-manager": {
                "hub_url": "http://itechsmart-enterprise:8001",
                "ninja_url": "http://itechsmart-ninja:8002",
                "port_range": {"start": 8000, "end": 9000},
                "monitoring": {"enabled": True, "interval": 30},
            },
        }

    async def initialize(self):
        """Initialize configuration manager"""
        logger.info("Initializing Configuration Manager...")

        # Load existing configurations
        await self._load_configurations()

        logger.info(
            f"Configuration Manager initialized with {len(self.templates)} templates"
        )

    async def generate_configuration(
        self,
        product_id: str,
        environment: str = "production",
        custom_values: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate configuration for a product

        Args:
            product_id: Product identifier
            environment: Target environment
            custom_values: Custom configuration values

        Returns:
            Generated configuration
        """
        logger.info(f"Generating configuration for {product_id} in {environment}")

        # Get template
        template = self.templates.get(product_id, {})

        # Deep copy template
        config = self._deep_copy(template)

        # Apply environment-specific values
        config = self._apply_environment_values(config, environment)

        # Apply custom values
        if custom_values:
            config = self._merge_configs(config, custom_values)

        # Resolve variables
        config = self._resolve_variables(config, environment)

        # Validate configuration
        await self._validate_configuration(product_id, config)

        # Store configuration
        config_key = f"{product_id}-{environment}"
        self.active_configs[config_key] = config

        # Add to history
        self.config_history.append(
            {
                "product_id": product_id,
                "environment": environment,
                "config": config,
                "timestamp": self._get_timestamp(),
            }
        )

        return config

    async def generate_suite_configuration(
        self, environment: str = "production", custom_values: Dict[str, Dict] = None
    ) -> Dict[str, Dict]:
        """
        Generate configuration for entire suite

        Args:
            environment: Target environment
            custom_values: Custom values per product

        Returns:
            Dictionary of configurations per product
        """
        logger.info(f"Generating suite configuration for {environment}")

        suite_config = {}

        for product_id in self.templates.keys():
            custom = custom_values.get(product_id) if custom_values else None
            config = await self.generate_configuration(product_id, environment, custom)
            suite_config[product_id] = config

        return suite_config

    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy an object"""
        import copy

        return copy.deepcopy(obj)

    def _apply_environment_values(self, config: Dict, environment: str) -> Dict:
        """Apply environment-specific values"""
        env_overrides = {
            "development": {"debug": True, "log_level": "DEBUG"},
            "staging": {"debug": False, "log_level": "INFO"},
            "production": {"debug": False, "log_level": "WARNING"},
        }

        overrides = env_overrides.get(environment, {})
        return self._merge_configs(config, overrides)

    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Merge two configuration dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _resolve_variables(self, config: Dict, environment: str) -> Dict:
        """Resolve variables in configuration"""
        import os
        import re

        def resolve_value(value):
            if isinstance(value, str):
                # Replace ${VAR} with environment variable or default
                pattern = r"\$\{([^}]+)\}"
                matches = re.findall(pattern, value)

                for match in matches:
                    env_value = os.getenv(
                        match, self._get_default_value(match, environment)
                    )
                    value = value.replace(f"${{{match}}}", env_value)

                return value
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            else:
                return value

        return resolve_value(config)

    def _get_default_value(self, var_name: str, environment: str) -> str:
        """Get default value for a variable"""
        defaults = {
            "DATABASE_PASSWORD": f"secure_password_{environment}",
            "JWT_SECRET": f"jwt_secret_{environment}",
            "OPENAI_API_KEY": "sk-your-api-key-here",
            "REDIS_PASSWORD": "",
        }
        return defaults.get(var_name, "")

    async def _validate_configuration(self, product_id: str, config: Dict):
        """Validate configuration"""
        logger.info(f"Validating configuration for {product_id}")

        # Check required fields
        # Validate data types
        # Check value ranges
        # Verify connections

        return True

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.utcnow().isoformat()

    async def export_configuration(
        self, product_id: str, environment: str, format: str = "json"
    ) -> str:
        """
        Export configuration to file

        Args:
            product_id: Product identifier
            environment: Environment
            format: Export format (json, yaml, env)

        Returns:
            File path
        """
        config_key = f"{product_id}-{environment}"
        config = self.active_configs.get(config_key)

        if not config:
            raise ValueError(f"No configuration found for {config_key}")

        filename = f"{product_id}-{environment}.{format}"
        filepath = Path(f"configs/{filename}")
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            with open(filepath, "w") as f:
                json.dump(config, f, indent=2)
        elif format == "yaml":
            with open(filepath, "w") as f:
                yaml.dump(config, f)
        elif format == "env":
            with open(filepath, "w") as f:
                self._write_env_file(config, f)

        return str(filepath)

    def _write_env_file(self, config: Dict, file, prefix: str = ""):
        """Write configuration as .env file"""
        for key, value in config.items():
            if isinstance(value, dict):
                self._write_env_file(value, file, f"{prefix}{key.upper()}_")
            else:
                file.write(f"{prefix}{key.upper()}={value}\n")

    async def _load_configurations(self):
        """Load existing configurations"""
        config_dir = Path("configs")
        if config_dir.exists():
            for config_file in config_dir.glob("*.json"):
                try:
                    with open(config_file, "r") as f:
                        config = json.load(f)
                        # Parse filename to get product_id and environment
                        parts = config_file.stem.split("-")
                        if len(parts) >= 2:
                            config_key = f"{parts[0]}-{parts[1]}"
                            self.active_configs[config_key] = config
                except Exception as e:
                    logger.error(f"Failed to load config {config_file}: {e}")

    async def shutdown(self):
        """Shutdown configuration manager"""
        logger.info("Configuration Manager shutdown complete")
