import React, { useState, useEffect } from 'react';
import './App.css';

const iTechSmartArbiter = () => {
  const [riskScore, setRiskScore] = useState(35);
  const [policies, setPolicies] = useState([]);
  const [actionHistory, setActionHistory] = useState([]);
  const [systemStatus, setSystemStatus] = useState('active');
  const [emergencyMode, setEmergencyMode] = useState(false);
  const [businessHours, setBusinessHours] = useState(true);
  const [loading, setLoading] = useState(false);

  // Sample data for demonstration
  useEffect(() => {
    // Simulate real-time risk assessment
    const riskInterval = setInterval(() => {
      setRiskScore(prev => {
        const change = Math.random() * 10 - 5;
        const newScore = Math.max(0, Math.min(100, prev + change));
        return Math.round(newScore);
      });
    }, 5000);

    // Load sample policies
    const samplePolicies = [
      {
        id: 1,
        rule: 'No root access in production',
        status: 'forbidden',
        severity: 'critical',
        description: 'Prevents any operation requiring root privileges'
      },
      {
        id: 2,
        rule: 'Database schema changes require approval',
        status: 'approved',
        severity: 'high',
        description: 'Schema modifications need human approval'
      },
      {
        id: 3,
        rule: 'Limited API rate limits per user',
        status: 'approved',
        severity: 'medium',
        description: 'Enforces API throttling to prevent abuse'
      },
      {
        id: 4,
        rule: 'Encryption at rest for all data',
        status: 'approved',
        severity: 'critical',
        description: 'All persistent data must be encrypted'
      },
      {
        id: 5,
        rule: 'Weekly security scans required',
        status: 'pending',
        severity: 'medium',
        description: 'Automated security vulnerability scanning'
      }
    ];
    setPolicies(samplePolicies);

    // Load sample action history
    const sampleHistory = [
      {
        id: 1,
        action: 'Command Blocked',
        details: 'Attempted rm -rf / command blocked by safety policy',
        timestamp: new Date(Date.now() - 300000),
        status: 'blocked',
        risk: 95
      },
      {
        id: 2,
        action: 'Request Approved',
        details: 'Database backup approved for 2:00 AM execution',
        timestamp: new Date(Date.now() - 600000),
        status: 'approved',
        risk: 15
      },
      {
        id: 3,
        action: 'Policy Violation',
        details: 'Unauthorized access attempt detected and logged',
        timestamp: new Date(Date.now() - 900000),
        status: 'blocked',
        risk: 80
      },
      {
        id: 4,
        action: 'Emergency Override',
        details: 'Manual override used for critical system maintenance',
        timestamp: new Date(Date.now() - 1800000),
        status: 'approved',
        risk: 60
      }
    ];
    setActionHistory(sampleHistory);

    return () => clearInterval(riskInterval);
  }, []);

  const getRiskLevel = (score) => {
    if (score <= 25) return 'low';
    if (score <= 50) return 'medium';
    if (score <= 75) return 'high';
    return 'critical';
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'low': return '#2e7d32';
      case 'medium': return '#ed6c02';
      case 'high': return '#d32f2f';
      case 'critical': return '#dc004e';
      default: return '#1976d2';
    }
  };

  const handleEmergencyStop = () => {
    setLoading(true);
    setEmergencyMode(true);
    
    // Simulate emergency stop
    setTimeout(() => {
      setLoading(false);
      setSystemStatus('emergency');
      
      // Add to action history
      const emergencyAction = {
        id: actionHistory.length + 1,
        action: 'Emergency Stop',
        details: 'Emergency kill switch activated - all autonomous operations stopped',
        timestamp: new Date(),
        status: 'blocked',
        risk: 100
      };
      setActionHistory([emergencyAction, ...actionHistory]);
    }, 2000);
  };

  const handleApproveAll = () => {
    setLoading(true);
    
    setTimeout(() => {
      setLoading(false);
      setPolicies(policies.map(policy => 
        policy.status === 'pending' ? { ...policy, status: 'approved' } : policy
      ));
      
      const approveAction = {
        id: actionHistory.length + 1,
        action: 'Bulk Approval',
        details: 'All pending policies approved by administrator',
        timestamp: new Date(),
        status: 'approved',
        risk: 20
      };
      setActionHistory([approveAction, ...actionHistory]);
    }, 1500);
  };

  const handleResetSystem = () => {
    setLoading(true);
    
    setTimeout(() => {
      setLoading(false);
      setEmergencyMode(false);
      setSystemStatus('active');
      setRiskScore(35);
      
      const resetAction = {
        id: actionHistory.length + 1,
        action: 'System Reset',
        details: 'Emergency mode deactivated - normal operations resumed',
        timestamp: new Date(),
        status: 'approved',
        risk: 25
      };
      setActionHistory([resetAction, ...actionHistory]);
    }, 1500);
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return timestamp.toLocaleDateString();
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">🛡️</div>
            <div className="logo-text">iTechSmart Arbiter</div>
          </div>
          <div className="header-actions">
            <div className="status-badge">
              System Status: {systemStatus.toUpperCase()}
            </div>
            <div className="status-badge">
              Risk Level: {getRiskLevel(riskScore).toUpperCase()}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="dashboard-grid">
          {/* Risk Assessment Card */}
          <div className="card fade-in">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">⚠️</div>
                Real-Time Risk Assessment
              </div>
            </div>
            <div className="card-content">
              <div className={`risk-score ${getRiskLevel(riskScore)}`}>
                {riskScore}
              </div>
              <div className="risk-gauge">
                <div 
                  className="risk-indicator"
                  style={{ left: `${riskScore}%` }}
                />
              </div>
              <p style={{ textAlign: 'center', margin: '1rem 0' }}>
                Current Risk Level: <strong>{getRiskLevel(riskScore)}</strong>
              </p>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                {emergencyMode ? (
                  <span style={{ color: 'var(--error-color)' }}>
                    🚨 Emergency Mode Active - All operations suspended
                  </span>
                ) : (
                  <span style={{ color: 'var(--success-color)' }}>
                    ✅ System operating within normal parameters
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Control Panel Card */}
          <div className="card fade-in">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">🎮</div>
                Safety Control Panel
              </div>
            </div>
            <div className="card-content">
              <div className="control-panel">
                <button
                  className="control-button emergency"
                  onClick={handleEmergencyStop}
                  disabled={loading || emergencyMode}
                >
                  <div className="control-button-icon">🛑</div>
                  <div className="control-button-text">
                    {loading ? <span className="loading-spinner"></span> : 'Emergency Stop'}
                  </div>
                </button>
                
                <button
                  className="control-button approve"
                  onClick={handleApproveAll}
                  disabled={loading}
                >
                  <div className="control-button-icon">✅</div>
                  <div className="control-button-text">
                    {loading ? <span className="loading-spinner"></span> : 'Approve All'}
                  </div>
                </button>
                
                <button
                  className="control-button block"
                  onClick={handleResetSystem}
                  disabled={loading || !emergencyMode}
                >
                  <div className="control-button-icon">🔄</div>
                  <div className="control-button-text">
                    {loading ? <span className="loading-spinner"></span> : 'Reset System'}
                  </div>
                </button>
              </div>
              
              <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--background-color)', borderRadius: '8px' }}>
                <strong>Business Hours:</strong> {businessHours ? '✅ Active' : '❌ Restricted'}
                <br />
                <strong>Human-in-the-Loop:</strong> ✅ Required for high-risk operations
                <br />
                <strong>Auto-Approval:</strong> {riskScore < 50 ? '✅ Enabled' : '❌ Disabled'}
              </div>
            </div>
          </div>

          {/* Policy Rules Card */}
          <div className="card fade-in">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">📋</div>
                Constitution Policies
              </div>
            </div>
            <div className="card-content">
              <ul className="policy-list">
                {policies.map(policy => (
                  <li key={policy.id} className={`policy-item ${policy.status}`}>
                    <div>
                      <strong>{policy.rule}</strong>
                      <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                        {policy.description}
                      </div>
                    </div>
                    <span className={`policy-status ${policy.status}`}>
                      {policy.status}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Action History Card */}
          <div className="card fade-in" style={{ gridColumn: 'span 2' }}>
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">📜</div>
                Action History
              </div>
            </div>
            <div className="card-content">
              <div className="history-timeline">
                {actionHistory.map(action => (
                  <div key={action.id} className={`history-item ${action.status}`}>
                    <div className="history-header">
                      <span className="history-action">{action.action}</span>
                      <span className="history-time">{formatTime(action.timestamp)}</span>
                    </div>
                    <div className="history-details">{action.details}</div>
                    {action.risk && (
                      <div style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>
                        Risk Score: <strong>{action.risk}</strong> ({getRiskLevel(action.risk)})
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default iTechSmartArbiter;