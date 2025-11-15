"""
Web dashboard for iTechSmart Supreme
"""

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import logging
from typing import Dict, Any
from datetime import datetime
import os

from ..core.models import Alert, RemediationAction


class Dashboard:
    """Real-time web dashboard"""
    
    def __init__(self, app: Flask, socketio: SocketIO, supreme_instance):
        self.app = app
        self.socketio = socketio
        self.supreme = supreme_instance
        self.logger = logging.getLogger(__name__)
        
        # Register routes
        self.register_routes()
        self.register_socketio_events()
    
    def register_routes(self):
        """Register Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('dashboard.html')
        
        @self.app.route('/static/<path:path>')
        def send_static(path):
            return send_from_directory('static', path)
    
    def register_socketio_events(self):
        """Register SocketIO events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.logger.info("Client connected to dashboard")
            emit('status', {'msg': 'Connected to iTechSmart Supreme'})
            
            # Send initial data
            emit('initial_data', {
                'alerts': self.supreme.get_active_alerts(),
                'actions': self.supreme.get_pending_actions(),
                'status': self.supreme.get_system_status()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.logger.info("Client disconnected from dashboard")
        
        @self.socketio.on('approve_action')
        def handle_approve_action(data):
            action_id = data.get('action_id')
            approved_by = data.get('approved_by', 'dashboard_user')
            
            success = self.supreme.approve_action(action_id, approved_by)
            
            if success:
                emit('action_approved', {'action_id': action_id}, broadcast=True)
            else:
                emit('error', {'message': 'Failed to approve action'})
        
        @self.socketio.on('reject_action')
        def handle_reject_action(data):
            action_id = data.get('action_id')
            rejected_by = data.get('rejected_by', 'dashboard_user')
            reason = data.get('reason', 'No reason provided')
            
            success = self.supreme.reject_action(action_id, rejected_by, reason)
            
            if success:
                emit('action_rejected', {'action_id': action_id}, broadcast=True)
            else:
                emit('error', {'message': 'Failed to reject action'})
        
        @self.socketio.on('enable_killswitch')
        def handle_enable_killswitch():
            self.supreme.enable_kill_switch()
            emit('killswitch_status', {'enabled': True}, broadcast=True)
        
        @self.socketio.on('disable_killswitch')
        def handle_disable_killswitch():
            self.supreme.disable_kill_switch()
            emit('killswitch_status', {'enabled': False}, broadcast=True)
        
        @self.socketio.on('request_status')
        def handle_request_status():
            emit('status_update', self.supreme.get_system_status())
    
    def broadcast_alert(self, alert: Alert):
        """Broadcast new alert to all connected clients"""
        self.socketio.emit('new_alert', {
            'id': alert.id,
            'timestamp': alert.timestamp.isoformat(),
            'severity': alert.severity.value,
            'message': alert.message,
            'host': alert.host,
            'source': alert.source.value,
            'tags': alert.tags
        })
    
    def broadcast_action(self, action: RemediationAction):
        """Broadcast new action to all connected clients"""
        self.socketio.emit('new_action', {
            'id': action.id,
            'alert_id': action.alert_id,
            'description': action.description,
            'command': action.command,
            'risk_level': action.risk_level.value,
            'requires_approval': action.requires_approval,
            'status': action.status.value
        })
    
    def broadcast_action_result(self, action_id: str, result: Dict[str, Any]):
        """Broadcast action execution result"""
        self.socketio.emit('action_result', {
            'action_id': action_id,
            'success': result.get('success', False),
            'stdout': result.get('stdout', ''),
            'stderr': result.get('stderr', ''),
            'timestamp': datetime.now().isoformat()
        })
    
    def broadcast_status_update(self):
        """Broadcast system status update"""
        self.socketio.emit('status_update', self.supreme.get_system_status())