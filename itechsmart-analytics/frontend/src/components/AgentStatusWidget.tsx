/**
 * iTechSmart Analytics - Agent Status Widget
 * Displays real-time agent monitoring information
 */

import React, { useState, useEffect } from 'react';

interface Agent {
  id: string;
  hostname: string;
  status: 'ACTIVE' | 'OFFLINE' | 'ERROR' | 'MAINTENANCE';
  lastSeen: string;
  lastMetrics?: {
    cpuUsage: number;
    memoryUsage: number;
    diskUsage: number;
  };
  alertCount?: number;
}

interface AgentSummary {
  total: number;
  active: number;
  offline: number;
  error: number;
  averageMetrics: {
    cpu: number;
    memory: number;
    disk: number;
  };
}

interface HealthScore {
  healthScore: number;
  status: string;
  totalAgents: number;
}

const AgentStatusWidget: React.FC = () => {
  const [summary, setSummary] = useState<AgentSummary | null>(null);
  const [healthScore, setHealthScore] = useState<HealthScore | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8003';

  const fetchData = async () => {
    try {
      setError(null);
      
      // Fetch summary
      const summaryRes = await fetch(`${API_BASE}/api/v1/agents/stats/summary`);
      if (!summaryRes.ok) throw new Error('Failed to fetch summary');
      const summaryData = await summaryRes.json();
      setSummary(summaryData);

      // Fetch health score
      const healthRes = await fetch(`${API_BASE}/api/v1/agents/analytics/health-score`);
      if (!healthRes.ok) throw new Error('Failed to fetch health score');
      const healthData = await healthRes.json();
      setHealthScore(healthData);

      // Fetch agents list
      const agentsRes = await fetch(`${API_BASE}/api/v1/agents?limit=10`);
      if (!agentsRes.ok) throw new Error('Failed to fetch agents');
      const agentsData = await agentsRes.json();
      setAgents(agentsData.agents || []);

      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agent data');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return '#10b981';
      case 'OFFLINE': return '#6b7280';
      case 'ERROR': return '#ef4444';
      case 'MAINTENANCE': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 90) return '#10b981';
    if (score >= 75) return '#3b82f6';
    if (score >= 60) return '#f59e0b';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  };

  const getMetricColor = (value: number) => {
    if (value >= 90) return '#ef4444';
    if (value >= 80) return '#f59e0b';
    if (value >= 70) return '#3b82f6';
    return '#10b981';
  };

  if (loading) {
    return (
      <div style={styles.widget}>
        <div style={styles.header}>
          <h3 style={styles.title}>Agent Monitoring</h3>
        </div>
        <div style={styles.loading}>Loading agent data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.widget}>
        <div style={styles.header}>
          <h3 style={styles.title}>Agent Monitoring</h3>
        </div>
        <div style={styles.error}>
          <span style={styles.errorIcon}>⚠️</span>
          <span>{error}</span>
          <button onClick={fetchData} style={styles.retryButton}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.widget}>
      <div style={styles.header}>
        <h3 style={styles.title}>Agent Monitoring</h3>
        <div style={styles.controls}>
          <label style={styles.autoRefreshLabel}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              style={styles.checkbox}
            />
            Auto-refresh
          </label>
          <button onClick={fetchData} style={styles.refreshButton}>🔄</button>
        </div>
      </div>

      {/* Health Score */}
      {healthScore && (
        <div style={styles.healthSection}>
          <div style={styles.healthScoreContainer}>
            <div
              style={{
                ...styles.healthScoreCircle,
                background: `conic-gradient(${getHealthColor(healthScore.healthScore)} ${healthScore.healthScore}%, #e5e7eb 0)`
              }}
            >
              <div style={styles.healthScoreInner}>
                <div style={styles.healthScoreValue}>{healthScore.healthScore}</div>
                <div style={styles.healthScoreLabel}>Health</div>
              </div>
            </div>
            <div style={styles.healthScoreInfo}>
              <div style={styles.healthStatus}>{healthScore.status.toUpperCase()}</div>
              <div style={styles.healthAgents}>{healthScore.totalAgents} agents monitored</div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      {summary && (
        <div style={styles.summarySection}>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{summary.total}</div>
            <div style={styles.statLabel}>Total</div>
          </div>
          <div style={styles.statCard}>
            <div style={{...styles.statValue, color: '#10b981'}}>{summary.active}</div>
            <div style={styles.statLabel}>Active</div>
          </div>
          <div style={styles.statCard}>
            <div style={{...styles.statValue, color: '#6b7280'}}>{summary.offline}</div>
            <div style={styles.statLabel}>Offline</div>
          </div>
          <div style={styles.statCard}>
            <div style={{...styles.statValue, color: '#ef4444'}}>{summary.error}</div>
            <div style={styles.statLabel}>Error</div>
          </div>
        </div>
      )}

      {/* Average Metrics */}
      {summary && (
        <div style={styles.metricsSection}>
          <h4 style={styles.sectionTitle}>Average Metrics</h4>
          <div style={styles.metricBars}>
            <div style={styles.metricBar}>
              <div style={styles.metricLabel}>
                <span>CPU</span>
                <span style={{color: getMetricColor(summary.averageMetrics.cpu)}}>
                  {summary.averageMetrics.cpu.toFixed(1)}%
                </span>
              </div>
              <div style={styles.progressBar}>
                <div
                  style={{
                    ...styles.progressFill,
                    width: `${summary.averageMetrics.cpu}%`,
                    backgroundColor: getMetricColor(summary.averageMetrics.cpu)
                  }}
                />
              </div>
            </div>
            <div style={styles.metricBar}>
              <div style={styles.metricLabel}>
                <span>Memory</span>
                <span style={{color: getMetricColor(summary.averageMetrics.memory)}}>
                  {summary.averageMetrics.memory.toFixed(1)}%
                </span>
              </div>
              <div style={styles.progressBar}>
                <div
                  style={{
                    ...styles.progressFill,
                    width: `${summary.averageMetrics.memory}%`,
                    backgroundColor: getMetricColor(summary.averageMetrics.memory)
                  }}
                />
              </div>
            </div>
            <div style={styles.metricBar}>
              <div style={styles.metricLabel}>
                <span>Disk</span>
                <span style={{color: getMetricColor(summary.averageMetrics.disk)}}>
                  {summary.averageMetrics.disk.toFixed(1)}%
                </span>
              </div>
              <div style={styles.progressBar}>
                <div
                  style={{
                    ...styles.progressFill,
                    width: `${summary.averageMetrics.disk}%`,
                    backgroundColor: getMetricColor(summary.averageMetrics.disk)
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Agents */}
      <div style={styles.agentsSection}>
        <h4 style={styles.sectionTitle}>Recent Agents</h4>
        <div style={styles.agentsList}>
          {agents.length === 0 ? (
            <div style={styles.noAgents}>No agents registered</div>
          ) : (
            agents.map((agent) => (
              <div key={agent.id} style={styles.agentCard}>
                <div style={styles.agentHeader}>
                  <div style={styles.agentName}>{agent.hostname}</div>
                  <div
                    style={{
                      ...styles.agentStatus,
                      backgroundColor: getStatusColor(agent.status)
                    }}
                  >
                    {agent.status}
                  </div>
                </div>
                {agent.lastMetrics && (
                  <div style={styles.agentMetrics}>
                    <span style={styles.agentMetric}>
                      CPU: {agent.lastMetrics.cpuUsage.toFixed(1)}%
                    </span>
                    <span style={styles.agentMetric}>
                      MEM: {agent.lastMetrics.memoryUsage.toFixed(1)}%
                    </span>
                    <span style={styles.agentMetric}>
                      DISK: {agent.lastMetrics.diskUsage.toFixed(1)}%
                    </span>
                  </div>
                )}
                {agent.alertCount !== undefined && agent.alertCount > 0 && (
                  <div style={styles.agentAlerts}>
                    ⚠️ {agent.alertCount} alert{agent.alertCount !== 1 ? 's' : ''}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  widget: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '24px',
    marginBottom: '24px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  title: {
    margin: 0,
    fontSize: '20px',
    fontWeight: '600',
    color: '#1f2937',
  },
  controls: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  autoRefreshLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '14px',
    color: '#6b7280',
    cursor: 'pointer',
  },
  checkbox: {
    cursor: 'pointer',
  },
  refreshButton: {
    background: 'none',
    border: 'none',
    fontSize: '18px',
    cursor: 'pointer',
    padding: '4px',
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    color: '#6b7280',
  },
  error: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '16px',
    backgroundColor: '#fef2f2',
    borderRadius: '8px',
    color: '#991b1b',
  },
  errorIcon: {
    fontSize: '20px',
  },
  retryButton: {
    marginLeft: 'auto',
    padding: '6px 12px',
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  healthSection: {
    marginBottom: '24px',
  },
  healthScoreContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '24px',
  },
  healthScoreCircle: {
    width: '120px',
    height: '120px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  healthScoreInner: {
    width: '100px',
    height: '100px',
    borderRadius: '50%',
    backgroundColor: '#ffffff',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  },
  healthScoreValue: {
    fontSize: '32px',
    fontWeight: '700',
    color: '#1f2937',
  },
  healthScoreLabel: {
    fontSize: '12px',
    color: '#6b7280',
    textTransform: 'uppercase',
  },
  healthScoreInfo: {
    flex: 1,
  },
  healthStatus: {
    fontSize: '24px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '8px',
  },
  healthAgents: {
    fontSize: '14px',
    color: '#6b7280',
  },
  summarySection: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '16px',
    marginBottom: '24px',
  },
  statCard: {
    textAlign: 'center',
    padding: '16px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
  },
  statValue: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#1f2937',
    marginBottom: '4px',
  },
  statLabel: {
    fontSize: '12px',
    color: '#6b7280',
    textTransform: 'uppercase',
  },
  metricsSection: {
    marginBottom: '24px',
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '12px',
  },
  metricBars: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  metricBar: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  metricLabel: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '14px',
    color: '#4b5563',
  },
  progressBar: {
    height: '8px',
    backgroundColor: '#e5e7eb',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    transition: 'width 0.3s ease',
  },
  agentsSection: {
    marginTop: '24px',
  },
  agentsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  noAgents: {
    textAlign: 'center',
    padding: '24px',
    color: '#6b7280',
    fontSize: '14px',
  },
  agentCard: {
    padding: '12px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    border: '1px solid #e5e7eb',
  },
  agentHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
  },
  agentName: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#1f2937',
  },
  agentStatus: {
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: '600',
    color: 'white',
    textTransform: 'uppercase',
  },
  agentMetrics: {
    display: 'flex',
    gap: '12px',
    fontSize: '12px',
    color: '#6b7280',
  },
  agentMetric: {
    display: 'inline-block',
  },
  agentAlerts: {
    marginTop: '8px',
    padding: '6px',
    backgroundColor: '#fef2f2',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#991b1b',
  },
};

export default AgentStatusWidget;