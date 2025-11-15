// iTechSmart Supreme Dashboard JavaScript

let socket;
let currentActionId = null;
let alerts = [];
let actions = [];

// Initialize Socket.IO connection
function initSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to iTechSmart Supreme');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from iTechSmart Supreme');
        updateConnectionStatus(false);
    });
    
    socket.on('initial_data', (data) => {
        console.log('Received initial data:', data);
        alerts = data.alerts || [];
        actions = data.actions || [];
        updateDashboard(data);
    });
    
    socket.on('new_alert', (alert) => {
        console.log('New alert:', alert);
        alerts.push(alert);
        addAlert(alert);
        updateStats();
        addActivity(`New ${alert.severity} alert: ${alert.message}`, 'alert');
    });
    
    socket.on('new_action', (action) => {
        console.log('New action:', action);
        actions.push(action);
        addAction(action);
        updateStats();
        addActivity(`New action pending: ${action.description}`, 'action');
    });
    
    socket.on('action_approved', (data) => {
        console.log('Action approved:', data);
        removeAction(data.action_id);
        addActivity(`Action approved: ${data.action_id}`, 'success');
    });
    
    socket.on('action_rejected', (data) => {
        console.log('Action rejected:', data);
        removeAction(data.action_id);
        addActivity(`Action rejected: ${data.action_id}`, 'warning');
    });
    
    socket.on('action_result', (result) => {
        console.log('Action result:', result);
        const status = result.success ? 'success' : 'error';
        addActivity(`Action ${result.success ? 'succeeded' : 'failed'}: ${result.action_id}`, status);
    });
    
    socket.on('status_update', (status) => {
        console.log('Status update:', status);
        updateSystemStatus(status);
    });
    
    socket.on('killswitch_status', (data) => {
        updateKillSwitchButton(data.enabled);
    });
    
    socket.on('error', (error) => {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    });
}

// Update dashboard with initial data
function updateDashboard(data) {
    // Update alerts
    const alertsContainer = document.getElementById('alerts-container');
    alertsContainer.innerHTML = '';
    
    if (data.alerts && data.alerts.length > 0) {
        data.alerts.forEach(alert => addAlert(alert));
    } else {
        alertsContainer.innerHTML = '<div class="empty-state"><p>No active alerts. System is healthy! 🎉</p></div>';
    }
    
    // Update actions
    const actionsContainer = document.getElementById('actions-container');
    actionsContainer.innerHTML = '';
    
    if (data.actions && data.actions.length > 0) {
        data.actions.forEach(action => addAction(action));
    } else {
        actionsContainer.innerHTML = '<div class="empty-state"><p>No pending actions requiring approval.</p></div>';
    }
    
    // Update system status
    if (data.status) {
        updateSystemStatus(data.status);
    }
    
    updateStats();
}

// Add alert to dashboard
function addAlert(alert) {
    const container = document.getElementById('alerts-container');
    
    // Remove empty state if exists
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const alertCard = document.createElement('div');
    alertCard.className = `alert-card ${alert.severity}`;
    alertCard.id = `alert-${alert.id}`;
    
    const timestamp = new Date(alert.timestamp).toLocaleString();
    
    alertCard.innerHTML = `
        <div class="alert-header">
            <span class="alert-title">${alert.message}</span>
            <span class="badge ${alert.severity}">${alert.severity.toUpperCase()}</span>
        </div>
        <div class="alert-meta">
            <span>🖥️ ${alert.host}</span>
            <span>📡 ${alert.source}</span>
            <span>🕐 ${timestamp}</span>
        </div>
        ${alert.tags && alert.tags.length > 0 ? `
            <div class="alert-tags">
                ${alert.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
        ` : ''}
    `;
    
    container.insertBefore(alertCard, container.firstChild);
}

// Add action to dashboard
function addAction(action) {
    const container = document.getElementById('actions-container');
    
    // Remove empty state if exists
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const actionCard = document.createElement('div');
    actionCard.className = 'action-card';
    actionCard.id = `action-${action.id}`;
    
    actionCard.innerHTML = `
        <div class="action-header">
            <span class="action-description">${action.description}</span>
            <span class="badge ${action.risk_level}">${action.risk_level.toUpperCase()}</span>
        </div>
        <div class="action-command">
            <code>${action.command}</code>
        </div>
        <div class="action-buttons">
            <button class="btn btn-success" onclick="showApprovalModal('${action.id}')">
                ✅ Approve
            </button>
            <button class="btn btn-danger" onclick="showRejectionModal('${action.id}')">
                ❌ Reject
            </button>
        </div>
    `;
    
    container.insertBefore(actionCard, container.firstChild);
}

// Remove action from dashboard
function removeAction(actionId) {
    const actionCard = document.getElementById(`action-${actionId}`);
    if (actionCard) {
        actionCard.remove();
    }
    
    // Remove from actions array
    actions = actions.filter(a => a.id !== actionId);
    
    // Check if container is empty
    const container = document.getElementById('actions-container');
    if (container.children.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No pending actions requiring approval.</p></div>';
    }
    
    updateStats();
}

// Show approval modal
function showApprovalModal(actionId) {
    currentActionId = actionId;
    const action = actions.find(a => a.id === actionId);
    
    if (!action) return;
    
    document.getElementById('modal-description').textContent = action.description;
    document.getElementById('modal-command').textContent = action.command;
    document.getElementById('modal-risk').textContent = action.risk_level.toUpperCase();
    document.getElementById('modal-risk').className = `badge ${action.risk_level}`;
    
    const alert = alerts.find(a => a.id === action.alert_id);
    document.getElementById('modal-host').textContent = alert ? alert.host : 'Unknown';
    
    document.getElementById('approval-modal').classList.add('show');
}

// Close modal
function closeModal() {
    document.getElementById('approval-modal').classList.remove('show');
    currentActionId = null;
}

// Approve action
function approveAction() {
    if (!currentActionId) return;
    
    socket.emit('approve_action', {
        action_id: currentActionId,
        approved_by: 'dashboard_user'
    });
    
    closeModal();
}

// Reject action
function rejectAction() {
    if (!currentActionId) return;
    
    const reason = prompt('Reason for rejection (optional):') || 'No reason provided';
    
    socket.emit('reject_action', {
        action_id: currentActionId,
        rejected_by: 'dashboard_user',
        reason: reason
    });
    
    closeModal();
}

// Show rejection modal (simplified version)
function showRejectionModal(actionId) {
    currentActionId = actionId;
    const reason = prompt('Reason for rejection (optional):') || 'No reason provided';
    
    socket.emit('reject_action', {
        action_id: actionId,
        rejected_by: 'dashboard_user',
        reason: reason
    });
}

// Update statistics
function updateStats() {
    const activeAlerts = alerts.filter(a => !a.resolved).length;
    const pendingActions = actions.length;
    const resolvedAlerts = alerts.filter(a => a.resolved).length;
    
    document.getElementById('active-alerts').textContent = activeAlerts;
    document.getElementById('pending-actions').textContent = pendingActions;
    document.getElementById('resolved-alerts').textContent = resolvedAlerts;
    document.getElementById('alerts-badge').textContent = activeAlerts;
    document.getElementById('actions-badge').textContent = pendingActions;
}

// Update system status
function updateSystemStatus(status) {
    if (status.statistics) {
        const stats = status.statistics;
        
        // Calculate success rate
        const totalActions = stats.successful_actions + stats.failed_actions;
        const successRate = totalActions > 0 
            ? Math.round((stats.successful_actions / totalActions) * 100)
            : 0;
        
        document.getElementById('success-rate').textContent = `${successRate}%`;
        document.getElementById('resolved-alerts').textContent = stats.resolved_alerts;
    }
    
    if (status.configuration) {
        const autoRemediation = status.configuration.auto_remediation ? 'ON' : 'OFF';
        document.getElementById('auto-remediation').textContent = autoRemediation;
        
        updateKillSwitchButton(status.configuration.kill_switch);
    }
    
    if (status.uptime_seconds) {
        const hours = Math.floor(status.uptime_seconds / 3600);
        const minutes = Math.floor((status.uptime_seconds % 3600) / 60);
        document.getElementById('uptime').textContent = `${hours}h ${minutes}m`;
    }
    
    if (status.monitored_hosts !== undefined) {
        document.getElementById('monitored-hosts').textContent = status.monitored_hosts;
    }
}

// Update kill switch button
function updateKillSwitchButton(enabled) {
    const btn = document.getElementById('killswitch-btn');
    const icon = document.getElementById('killswitch-icon');
    const text = document.getElementById('killswitch-text');
    
    if (enabled) {
        btn.classList.add('active');
        icon.textContent = '🟢';
        text.textContent = 'Kill Switch: ON';
    } else {
        btn.classList.remove('active');
        icon.textContent = '🛑';
        text.textContent = 'Kill Switch: OFF';
    }
}

// Toggle kill switch
document.getElementById('killswitch-btn').addEventListener('click', () => {
    const btn = document.getElementById('killswitch-btn');
    const isEnabled = btn.classList.contains('active');
    
    if (confirm(`Are you sure you want to ${isEnabled ? 'disable' : 'enable'} the kill switch?`)) {
        if (isEnabled) {
            socket.emit('disable_killswitch');
        } else {
            socket.emit('enable_killswitch');
        }
    }
});

// Add activity to timeline
function addActivity(message, type = 'info') {
    const timeline = document.getElementById('activity-timeline');
    
    // Remove empty state if exists
    const emptyState = timeline.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const activityItem = document.createElement('div');
    activityItem.className = 'activity-item';
    
    const timestamp = new Date().toLocaleTimeString();
    
    const icon = {
        'alert': '🚨',
        'action': '⚡',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }[type] || 'ℹ️';
    
    activityItem.innerHTML = `
        <div class="activity-time">${timestamp}</div>
        <div class="activity-message">${icon} ${message}</div>
    `;
    
    timeline.insertBefore(activityItem, timeline.firstChild);
    
    // Keep only last 20 items
    while (timeline.children.length > 20) {
        timeline.removeChild(timeline.lastChild);
    }
}

// Update connection status
function updateConnectionStatus(connected) {
    const aiStatus = document.getElementById('ai-status');
    const monitoringStatus = document.getElementById('monitoring-status');
    const executionStatus = document.getElementById('execution-status');
    
    if (connected) {
        aiStatus.innerHTML = '<span class="status-indicator online"></span> Online';
        monitoringStatus.innerHTML = '<span class="status-indicator online"></span> Active';
        executionStatus.innerHTML = '<span class="status-indicator online"></span> Ready';
    } else {
        aiStatus.innerHTML = '<span class="status-indicator offline"></span> Offline';
        monitoringStatus.innerHTML = '<span class="status-indicator offline"></span> Inactive';
        executionStatus.innerHTML = '<span class="status-indicator offline"></span> Unavailable';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple console notification for now
    console.log(`[${type.toUpperCase()}] ${message}`);
    addActivity(message, type);
}

// Request status update periodically
setInterval(() => {
    if (socket && socket.connected) {
        socket.emit('request_status');
    }
}, 30000); // Every 30 seconds

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initSocket();
});

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('approval-modal');
    if (event.target === modal) {
        closeModal();
    }
}