"""
iTechSmart Supreme - Main Application Entry Point
"""

import asyncio
import logging
from flask import Flask
from flask_socketio import SocketIO
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from itechsmart_supreme.core.orchestrator import iTechSmartSupreme
from itechsmart_supreme.api.webhook_receiver import WebhookReceiver
from itechsmart_supreme.api.rest_api import RestAPI
from itechsmart_supreme.web.dashboard import Dashboard


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("itechsmart_supreme.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def create_app(config: dict):
    """Create and configure Flask application"""

    app = Flask(
        __name__,
        template_folder="itechsmart_supreme/web/templates",
        static_folder="itechsmart_supreme/web/static",
    )

    app.config["SECRET_KEY"] = config.get("secret_key", "change_me_in_production")

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    # Initialize iTechSmart Supreme
    supreme = iTechSmartSupreme(config)

    # Initialize components
    webhook_receiver = WebhookReceiver(app, supreme.handle_alert)
    rest_api = RestAPI(app, supreme)
    dashboard = Dashboard(app, socketio, supreme)

    # Set webhook secrets if provided
    if "webhook_secrets" in config:
        for source, secret in config["webhook_secrets"].items():
            webhook_receiver.set_webhook_secret(source, secret)

    return app, socketio, supreme


def load_config():
    """Load configuration from file or environment"""

    config = {
        # Core settings
        "master_password": os.getenv("MASTER_PASSWORD", "change_me_in_production"),
        "secret_key": os.getenv("SECRET_KEY", "change_me_in_production"),
        "credentials_path": os.getenv("CREDENTIALS_PATH", "credentials.enc"),
        # AI settings
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "offline_mode": os.getenv("OFFLINE_MODE", "true").lower() == "true",
        # Automation settings
        "auto_remediation": os.getenv("AUTO_REMEDIATION", "false").lower() == "true",
        "require_approval_high_risk": os.getenv(
            "REQUIRE_APPROVAL_HIGH_RISK", "true"
        ).lower()
        == "true",
        # Monitoring endpoints
        "prometheus_endpoints": (
            os.getenv("PROMETHEUS_ENDPOINTS", "").split(",")
            if os.getenv("PROMETHEUS_ENDPOINTS")
            else []
        ),
        "wazuh_endpoints": [],
        # Webhook secrets
        "webhook_secrets": {
            "github": os.getenv("GITHUB_WEBHOOK_SECRET", ""),
            "prometheus": os.getenv("PROMETHEUS_WEBHOOK_SECRET", ""),
        },
    }

    # Parse Wazuh endpoints (format: url:username:password)
    wazuh_endpoints_str = os.getenv("WAZUH_ENDPOINTS", "")
    if wazuh_endpoints_str:
        for endpoint_str in wazuh_endpoints_str.split(","):
            parts = endpoint_str.split(":")
            if len(parts) >= 3:
                config["wazuh_endpoints"].append(
                    {
                        "url": parts[0],
                        "username": parts[1],
                        "password": ":".join(parts[2:]),  # Handle passwords with colons
                    }
                )

    return config


async def start_monitoring(supreme):
    """Start monitoring in background"""
    try:
        await supreme.start()
    except Exception as e:
        logger.error(f"Error in monitoring: {e}")


def main():
    """Main entry point"""

    logger.info("=" * 80)
    logger.info("🚀 Starting iTechSmart Supreme")
    logger.info("The End of IT Downtime. Forever.")
    logger.info("=" * 80)

    # Load configuration
    config = load_config()

    logger.info(f"Configuration loaded:")
    logger.info(f"  - Offline Mode: {config['offline_mode']}")
    logger.info(f"  - Auto Remediation: {config['auto_remediation']}")
    logger.info(f"  - Prometheus Endpoints: {len(config['prometheus_endpoints'])}")
    logger.info(f"  - Wazuh Endpoints: {len(config['wazuh_endpoints'])}")

    # Create application
    app, socketio, supreme = create_app(config)

    # Start monitoring in background
    import threading

    def run_monitoring():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_monitoring(supreme))

    monitoring_thread = threading.Thread(target=run_monitoring, daemon=True)
    monitoring_thread.start()

    # Get port from environment or use default
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"🌐 Starting web server on {host}:{port}")
    logger.info(f"📊 Dashboard: http://{host}:{port}")
    logger.info(f"🔌 API: http://{host}:{port}/api")
    logger.info(f"🪝 Webhooks: http://{host}:{port}/webhook")
    logger.info("=" * 80)

    # Run Flask app with SocketIO
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down iTechSmart Supreme...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
