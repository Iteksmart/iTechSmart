"""
REST API for iTechSmart Supreme
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..core.models import Alert, RemediationAction, ActionStatus


class RestAPI:
    """REST API for external integrations and management"""

    def __init__(self, app: Flask, supreme_instance):
        self.app = app
        self.supreme = supreme_instance
        self.logger = logging.getLogger(__name__)

        # Enable CORS
        CORS(app)

        # Register routes
        self.register_routes()

    def register_routes(self):
        """Register API endpoints"""

        # Health and status
        @self.app.route("/api/health", methods=["GET"])
        def health():
            return jsonify(
                {
                    "status": "healthy",
                    "version": "1.0.0",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        @self.app.route("/api/status", methods=["GET"])
        def status():
            return jsonify(self.supreme.get_system_status())

        # Alerts
        @self.app.route("/api/alerts", methods=["GET"])
        def get_alerts():
            return jsonify(self.supreme.get_active_alerts())

        @self.app.route("/api/alerts/<alert_id>", methods=["GET"])
        def get_alert(alert_id):
            alert = self.supreme.get_alert(alert_id)
            if alert:
                return jsonify(alert)
            return jsonify({"error": "Alert not found"}), 404

        @self.app.route("/api/alerts/<alert_id>/resolve", methods=["POST"])
        def resolve_alert(alert_id):
            success = self.supreme.resolve_alert(alert_id)
            if success:
                return jsonify({"status": "success", "alert_id": alert_id})
            return jsonify({"error": "Failed to resolve alert"}), 500

        # Actions
        @self.app.route("/api/actions/pending", methods=["GET"])
        def get_pending_actions():
            return jsonify(self.supreme.get_pending_actions())

        @self.app.route("/api/actions/<action_id>", methods=["GET"])
        def get_action(action_id):
            action = self.supreme.get_action(action_id)
            if action:
                return jsonify(action)
            return jsonify({"error": "Action not found"}), 404

        @self.app.route("/api/actions/<action_id>/approve", methods=["POST"])
        def approve_action(action_id):
            data = request.get_json() or {}
            approved_by = data.get("approved_by", "api_user")

            success = self.supreme.approve_action(action_id, approved_by)
            if success:
                return jsonify({"status": "success", "action_id": action_id})
            return jsonify({"error": "Failed to approve action"}), 500

        @self.app.route("/api/actions/<action_id>/reject", methods=["POST"])
        def reject_action(action_id):
            data = request.get_json() or {}
            rejected_by = data.get("rejected_by", "api_user")
            reason = data.get("reason", "No reason provided")

            success = self.supreme.reject_action(action_id, rejected_by, reason)
            if success:
                return jsonify({"status": "success", "action_id": action_id})
            return jsonify({"error": "Failed to reject action"}), 500

        # Execution history
        @self.app.route("/api/executions", methods=["GET"])
        def get_executions():
            limit = request.args.get("limit", 100, type=int)
            return jsonify(self.supreme.get_execution_history(limit))

        @self.app.route("/api/executions/<execution_id>", methods=["GET"])
        def get_execution(execution_id):
            execution = self.supreme.get_execution(execution_id)
            if execution:
                return jsonify(execution)
            return jsonify({"error": "Execution not found"}), 404

        # Configuration
        @self.app.route("/api/config", methods=["GET"])
        def get_config():
            return jsonify(self.supreme.get_config())

        @self.app.route("/api/config", methods=["PUT"])
        def update_config():
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            success = self.supreme.update_config(data)
            if success:
                return jsonify({"status": "success"})
            return jsonify({"error": "Failed to update config"}), 500

        # Kill switch
        @self.app.route("/api/killswitch/enable", methods=["POST"])
        def enable_killswitch():
            self.supreme.enable_kill_switch()
            return jsonify({"status": "success", "killswitch": "enabled"})

        @self.app.route("/api/killswitch/disable", methods=["POST"])
        def disable_killswitch():
            self.supreme.disable_kill_switch()
            return jsonify({"status": "success", "killswitch": "disabled"})

        @self.app.route("/api/killswitch/status", methods=["GET"])
        def killswitch_status():
            return jsonify({"enabled": self.supreme.executor.global_kill_switch})

        # Hosts
        @self.app.route("/api/hosts", methods=["GET"])
        def get_hosts():
            return jsonify(self.supreme.get_monitored_hosts())

        @self.app.route("/api/hosts", methods=["POST"])
        def add_host():
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            success = self.supreme.add_host(data)
            if success:
                return jsonify({"status": "success"})
            return jsonify({"error": "Failed to add host"}), 500

        @self.app.route("/api/hosts/<host>", methods=["DELETE"])
        def remove_host(host):
            success = self.supreme.remove_host(host)
            if success:
                return jsonify({"status": "success"})
            return jsonify({"error": "Host not found"}), 404

        # Metrics
        @self.app.route("/api/metrics/summary", methods=["GET"])
        def get_metrics_summary():
            return jsonify(self.supreme.get_metrics_summary())

        @self.app.route("/api/metrics/alerts", methods=["GET"])
        def get_alert_metrics():
            days = request.args.get("days", 7, type=int)
            return jsonify(self.supreme.get_alert_metrics(days))

        # Manual trigger
        @self.app.route("/api/trigger/diagnosis", methods=["POST"])
        def trigger_diagnosis():
            data = request.get_json()
            if not data or "alert_id" not in data:
                return jsonify({"error": "alert_id required"}), 400

            result = self.supreme.trigger_manual_diagnosis(data["alert_id"])
            if result:
                return jsonify(result)
            return jsonify({"error": "Failed to trigger diagnosis"}), 500

        @self.app.route("/api/trigger/action", methods=["POST"])
        def trigger_action():
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            result = self.supreme.trigger_manual_action(data)
            if result:
                return jsonify(result)
            return jsonify({"error": "Failed to trigger action"}), 500
