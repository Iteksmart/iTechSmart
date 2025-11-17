import axios, { AxiosInstance } from 'axios';
import { io, Socket } from 'socket.io-client';
import { EventEmitter } from 'events';

export interface AgentClientConfig {
  serverUrl: string;
  apiKey?: string;
  token?: string;
  autoConnect?: boolean;
}

export interface Agent {
  id: string;
  hostname: string;
  ipAddress?: string;
  osType: string;
  osVersion?: string;
  agentVersion: string;
  status: 'ACTIVE' | 'OFFLINE' | 'ERROR' | 'MAINTENANCE';
  lastSeen?: Date;
  config: Record<string, any>;
  organizationId: string;
  licenseId?: string;
}

export interface AgentMetric {
  id: string;
  agentId: string;
  metricType: string;
  metricData: Record<string, any>;
  timestamp: Date;
}

export interface AgentAlert {
  id: string;
  agentId: string;
  alertType: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  message: string;
  details: Record<string, any>;
  resolved: boolean;
  resolvedAt?: Date;
  createdAt: Date;
}

export interface AgentCommand {
  id: string;
  agentId: string;
  commandType: string;
  commandData: Record<string, any>;
  status: 'PENDING' | 'SENT' | 'EXECUTING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  result?: Record<string, any>;
  error?: string;
  createdAt: Date;
  executedAt?: Date;
  completedAt?: Date;
}

export class AgentClient extends EventEmitter {
  private config: AgentClientConfig;
  private httpClient: AxiosInstance;
  private socket?: Socket;
  private connected: boolean = false;

  constructor(config: AgentClientConfig) {
    super();
    this.config = {
      autoConnect: true,
      ...config,
    };

    // Setup HTTP client
    this.httpClient = axios.create({
      baseURL: `${config.serverUrl}/api`,
      headers: this.getAuthHeaders(),
    });

    // Auto-connect WebSocket if enabled
    if (this.config.autoConnect) {
      this.connect();
    }
  }

  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};
    
    if (this.config.apiKey) {
      headers['X-API-Key'] = this.config.apiKey;
    }
    
    if (this.config.token) {
      headers['Authorization'] = `Bearer ${this.config.token}`;
    }
    
    return headers;
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.socket?.connected) {
      return;
    }

    const auth: Record<string, string> = {};
    if (this.config.token) {
      auth.token = this.config.token;
    } else if (this.config.apiKey) {
      auth.token = this.config.apiKey;
    }

    this.socket = io(this.config.serverUrl, {
      path: '/ws/agents',
      auth,
    });

    this.socket.on('connect', () => {
      this.connected = true;
      this.emit('connected');
    });

    this.socket.on('disconnect', () => {
      this.connected = false;
      this.emit('disconnected');
    });

    this.socket.on('error', (error: Error) => {
      this.emit('error', error);
    });

    // Agent events
    this.socket.on('agents:status', (data: any) => {
      this.emit('agents:status', data);
    });

    this.socket.on('agent:connected', (data: any) => {
      this.emit('agent:connected', data);
    });

    this.socket.on('agent:disconnected', (data: any) => {
      this.emit('agent:disconnected', data);
    });

    this.socket.on('agent:metrics', (data: any) => {
      this.emit('agent:metrics', data);
    });

    this.socket.on('agent:alert', (data: any) => {
      this.emit('agent:alert', data);
    });

    this.socket.on('agent:command:result', (data: any) => {
      this.emit('agent:command:result', data);
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = undefined;
      this.connected = false;
    }
  }

  /**
   * Check if connected to WebSocket
   */
  isConnected(): boolean {
    return this.connected;
  }

  // ==================== Agent Management ====================

  /**
   * Get all agents
   */
  async getAgents(params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ agents: Agent[]; total: number }> {
    const response = await this.httpClient.get('/agents', { params });
    return response.data;
  }

  /**
   * Get agent by ID
   */
  async getAgent(agentId: string): Promise<Agent> {
    const response = await this.httpClient.get(`/agents/${agentId}`);
    return response.data;
  }

  /**
   * Update agent configuration
   */
  async updateAgent(
    agentId: string,
    data: { config?: Record<string, any>; status?: string }
  ): Promise<Agent> {
    const response = await this.httpClient.put(`/agents/${agentId}`, data);
    return response.data;
  }

  /**
   * Delete agent
   */
  async deleteAgent(agentId: string): Promise<void> {
    await this.httpClient.delete(`/agents/${agentId}`);
  }

  // ==================== Metrics ====================

  /**
   * Get agent metrics
   */
  async getMetrics(
    agentId: string,
    params?: {
      metricType?: string;
      from?: string;
      to?: string;
      limit?: number;
    }
  ): Promise<{ metrics: AgentMetric[] }> {
    const response = await this.httpClient.get(`/agents/${agentId}/metrics`, {
      params,
    });
    return response.data;
  }

  /**
   * Submit metrics (for agent use)
   */
  async submitMetrics(
    agentId: string,
    data: {
      metricType: string;
      metricData: Record<string, any>;
      timestamp?: string;
    }
  ): Promise<{ status: string; alerts: any[] }> {
    const response = await this.httpClient.post(
      `/agents/${agentId}/metrics`,
      data
    );
    return response.data;
  }

  // ==================== Alerts ====================

  /**
   * Get agent alerts
   */
  async getAlerts(
    agentId: string,
    params?: {
      resolved?: boolean;
      severity?: string;
      limit?: number;
    }
  ): Promise<{ alerts: AgentAlert[] }> {
    const response = await this.httpClient.get(`/agents/${agentId}/alerts`, {
      params,
    });
    return response.data;
  }

  /**
   * Resolve alert
   */
  async resolveAlert(agentId: string, alertId: string): Promise<AgentAlert> {
    const response = await this.httpClient.put(
      `/agents/${agentId}/alerts/${alertId}/resolve`
    );
    return response.data;
  }

  // ==================== Commands ====================

  /**
   * Send command to agent
   */
  async sendCommand(
    agentId: string,
    command: {
      commandType: string;
      commandData: Record<string, any>;
    }
  ): Promise<AgentCommand> {
    if (this.socket?.connected) {
      // Send via WebSocket for real-time execution
      return new Promise((resolve, reject) => {
        this.socket!.emit('command:send', {
          agentId,
          ...command,
        });

        this.socket!.once('command:sent', (data: any) => {
          resolve(data);
        });

        this.socket!.once('error', (error: Error) => {
          reject(error);
        });

        // Timeout after 30 seconds
        setTimeout(() => {
          reject(new Error('Command send timeout'));
        }, 30000);
      });
    } else {
      // Fallback to HTTP API
      const response = await this.httpClient.post(
        `/agents/${agentId}/commands`,
        command
      );
      return response.data;
    }
  }

  /**
   * Get agent commands
   */
  async getCommands(
    agentId: string,
    params?: {
      status?: string;
      limit?: number;
    }
  ): Promise<{ commands: AgentCommand[] }> {
    const response = await this.httpClient.get(`/agents/${agentId}/commands`, {
      params,
    });
    return response.data;
  }

  // ==================== Convenience Methods ====================

  /**
   * Get agent system metrics (latest)
   */
  async getSystemMetrics(agentId: string): Promise<{
    cpu: number;
    memory: number;
    disk: number;
    network: { sent: number; received: number };
  } | null> {
    const { metrics } = await this.getMetrics(agentId, {
      metricType: 'system',
      limit: 1,
    });

    if (metrics.length === 0) {
      return null;
    }

    const data = metrics[0].metricData;
    return {
      cpu: data.cpu_percent || 0,
      memory: data.memory_percent || 0,
      disk: data.disk_percent || 0,
      network: {
        sent: data.network_bytes_sent || 0,
        received: data.network_bytes_recv || 0,
      },
    };
  }

  /**
   * Get agent security status (latest)
   */
  async getSecurityStatus(agentId: string): Promise<{
    firewallEnabled: boolean;
    antivirusEnabled: boolean;
    updatesAvailable: number;
  } | null> {
    const { metrics } = await this.getMetrics(agentId, {
      metricType: 'security',
      limit: 1,
    });

    if (metrics.length === 0) {
      return null;
    }

    const data = metrics[0].metricData;
    return {
      firewallEnabled: data.firewall_enabled || false,
      antivirusEnabled: data.antivirus_enabled || false,
      updatesAvailable: data.updates_available || 0,
    };
  }

  /**
   * Get unresolved alerts count
   */
  async getUnresolvedAlertsCount(agentId: string): Promise<number> {
    const { alerts } = await this.getAlerts(agentId, {
      resolved: false,
      limit: 1000,
    });
    return alerts.length;
  }

  /**
   * Execute shell command on agent
   */
  async executeCommand(
    agentId: string,
    command: string
  ): Promise<AgentCommand> {
    return this.sendCommand(agentId, {
      commandType: 'execute',
      commandData: { command },
    });
  }

  /**
   * Restart agent
   */
  async restartAgent(agentId: string): Promise<AgentCommand> {
    return this.sendCommand(agentId, {
      commandType: 'restart',
      commandData: {},
    });
  }

  /**
   * Update agent configuration remotely
   */
  async updateAgentConfig(
    agentId: string,
    config: Record<string, any>
  ): Promise<AgentCommand> {
    return this.sendCommand(agentId, {
      commandType: 'update_config',
      commandData: { config },
    });
  }
}

// Export types
export * from './types';

// Default export
export default AgentClient;