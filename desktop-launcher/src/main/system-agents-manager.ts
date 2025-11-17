/**
 * System Agents Manager
 * Manages iTechSmart Agent monitoring and management for Desktop Launcher
 */

import axios, { AxiosInstance } from 'axios';

interface Agent {
  id: string;
  hostname: string;
  ip_address: string;
  platform: string;
  status: 'ACTIVE' | 'OFFLINE' | 'ERROR' | 'MAINTENANCE';
  last_seen: string;
  version: string;
  organization_id?: string;
}

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_rx: number;
  network_tx: number;
}

interface AgentStats {
  total_agents: number;
  active_agents: number;
  offline_agents: number;
  error_agents: number;
  total_unresolved_alerts: number;
}

interface AgentAlert {
  id: string;
  agent_id: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  message: string;
  created_at: string;
  resolved: boolean;
}

export class SystemAgentsManager {
  private client: AxiosInstance;
  private licenseServerUrl: string;
  private authToken: string | null = null;

  constructor() {
    this.licenseServerUrl = process.env.LICENSE_SERVER_URL || 'http://localhost:3000';
    
    this.client = axios.create({
      baseURL: this.licenseServerUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth
    this.client.interceptors.request.use((config) => {
      if (this.authToken) {
        config.headers.Authorization = `Bearer ${this.authToken}`;
      }
      return config;
    });
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string): void {
    this.authToken = token;
  }

  /**
   * Get all agents
   */
  async getAgents(params?: {
    page?: number;
    limit?: number;
    status?: string;
    search?: string;
  }): Promise<{ agents: Agent[]; total: number }> {
    try {
      const response = await this.client.get('/api/agents', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to get agents:', error);
      throw error;
    }
  }

  /**
   * Get specific agent
   */
  async getAgent(agentId: string): Promise<Agent> {
    try {
      const response = await this.client.get(`/api/agents/${agentId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get agent ${agentId}:`, error);
      throw error;
    }
  }

  /**
   * Get agent system metrics
   */
  async getSystemMetrics(agentId: string): Promise<SystemMetrics> {
    try {
      const response = await this.client.get(`/api/agents/${agentId}/metrics/latest`);
      const metrics = response.data;
      
      return {
        cpu_usage: metrics.cpu_usage || 0,
        memory_usage: metrics.memory_usage || 0,
        disk_usage: metrics.disk_usage || 0,
        network_rx: metrics.network_rx || 0,
        network_tx: metrics.network_tx || 0,
      };
    } catch (error) {
      console.error(`Failed to get metrics for agent ${agentId}:`, error);
      throw error;
    }
  }

  /**
   * Get agent alerts
   */
  async getAgentAlerts(
    agentId: string,
    params?: {
      severity?: string;
      resolved?: boolean;
    }
  ): Promise<AgentAlert[]> {
    try {
      const response = await this.client.get(`/api/agents/${agentId}/alerts`, { params });
      return response.data;
    } catch (error) {
      console.error(`Failed to get alerts for agent ${agentId}:`, error);
      throw error;
    }
  }

  /**
   * Get unresolved alert count
   */
  async getUnresolvedAlertCount(agentId: string): Promise<number> {
    try {
      const response = await this.client.get(`/api/agents/${agentId}/alerts/count`);
      return response.data.count || 0;
    } catch (error) {
      console.error(`Failed to get alert count for agent ${agentId}:`, error);
      return 0;
    }
  }

  /**
   * Resolve alert
   */
  async resolveAlert(agentId: string, alertId: string): Promise<void> {
    try {
      await this.client.put(`/api/agents/${agentId}/alerts/${alertId}/resolve`);
    } catch (error) {
      console.error(`Failed to resolve alert ${alertId}:`, error);
      throw error;
    }
  }

  /**
   * Execute command on agent
   */
  async executeCommand(
    agentId: string,
    command: string,
    parameters?: Record<string, any>
  ): Promise<any> {
    try {
      const response = await this.client.post(
        `/api/agents/${agentId}/commands/execute`,
        { command, parameters }
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to execute command on agent ${agentId}:`, error);
      throw error;
    }
  }

  /**
   * Get agent statistics
   */
  async getAgentStats(): Promise<AgentStats> {
    try {
      const { agents } = await this.getAgents({ limit: 1000 });
      
      const total = agents.length;
      const active = agents.filter(a => a.status === 'ACTIVE').length;
      const offline = agents.filter(a => a.status === 'OFFLINE').length;
      const error = agents.filter(a => a.status === 'ERROR').length;
      
      // Get total unresolved alerts
      let totalAlerts = 0;
      for (const agent of agents) {
        try {
          const count = await this.getUnresolvedAlertCount(agent.id);
          totalAlerts += count;
        } catch {
          // Ignore errors for individual agents
        }
      }
      
      return {
        total_agents: total,
        active_agents: active,
        offline_agents: offline,
        error_agents: error,
        total_unresolved_alerts: totalAlerts,
      };
    } catch (error) {
      console.error('Failed to get agent stats:', error);
      throw error;
    }
  }

  /**
   * Get system health score (0-100)
   */
  async getSystemHealthScore(): Promise<number> {
    try {
      const stats = await this.getAgentStats();
      
      if (stats.total_agents === 0) {
        return 100;
      }
      
      // Calculate health score based on active agents
      const healthScore = Math.round((stats.active_agents / stats.total_agents) * 100);
      
      return healthScore;
    } catch (error) {
      console.error('Failed to get system health score:', error);
      return 0;
    }
  }

  /**
   * Check if any agents have critical alerts
   */
  async hasCriticalAlerts(): Promise<boolean> {
    try {
      const { agents } = await this.getAgents({ limit: 100 });
      
      for (const agent of agents) {
        const alerts = await this.getAgentAlerts(agent.id, {
          severity: 'CRITICAL',
          resolved: false,
        });
        
        if (alerts.length > 0) {
          return true;
        }
      }
      
      return false;
    } catch (error) {
      console.error('Failed to check critical alerts:', error);
      return false;
    }
  }

  /**
   * Get agents with issues (offline or error status)
   */
  async getAgentsWithIssues(): Promise<Agent[]> {
    try {
      const { agents } = await this.getAgents({ limit: 1000 });
      return agents.filter(a => a.status === 'OFFLINE' || a.status === 'ERROR');
    } catch (error) {
      console.error('Failed to get agents with issues:', error);
      return [];
    }
  }

  /**
   * Get system tray status text
   */
  async getSystemTrayStatus(): Promise<string> {
    try {
      const stats = await this.getAgentStats();
      const healthScore = await this.getSystemHealthScore();
      
      if (stats.total_agents === 0) {
        return 'No agents deployed';
      }
      
      if (healthScore >= 90) {
        return `All systems operational (${stats.active_agents}/${stats.total_agents})`;
      } else if (healthScore >= 70) {
        return `Some issues detected (${stats.active_agents}/${stats.total_agents})`;
      } else {
        return `Critical: ${stats.error_agents + stats.offline_agents} agents down`;
      }
    } catch (error) {
      console.error('Failed to get system tray status:', error);
      return 'Status unavailable';
    }
  }
}

// Export singleton instance
export const systemAgentsManager = new SystemAgentsManager();