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
  status: AgentStatus;
  lastSeen?: Date;
  config: Record<string, any>;
  organizationId: string;
  licenseId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export enum AgentStatus {
  ACTIVE = 'ACTIVE',
  OFFLINE = 'OFFLINE',
  ERROR = 'ERROR',
  MAINTENANCE = 'MAINTENANCE',
}

export interface AgentMetric {
  id: string;
  agentId: string;
  metricType: MetricType;
  metricData: Record<string, any>;
  timestamp: Date;
}

export enum MetricType {
  SYSTEM = 'system',
  SECURITY = 'security',
  SOFTWARE = 'software',
  NETWORK = 'network',
  CUSTOM = 'custom',
}

export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  network_bytes_sent: number;
  network_bytes_recv: number;
  process_count?: number;
  uptime?: number;
}

export interface SecurityMetrics {
  firewall_enabled: boolean;
  antivirus_enabled: boolean;
  updates_available: number;
  open_ports?: number[];
  failed_login_attempts?: number;
}

export interface AgentAlert {
  id: string;
  agentId: string;
  alertType: AlertType;
  severity: AlertSeverity;
  message: string;
  details: Record<string, any>;
  resolved: boolean;
  resolvedAt?: Date;
  resolvedBy?: string;
  createdAt: Date;
}

export enum AlertType {
  CPU = 'cpu',
  MEMORY = 'memory',
  DISK = 'disk',
  NETWORK = 'network',
  SECURITY = 'security',
  UPDATES = 'updates',
  CUSTOM = 'custom',
}

export enum AlertSeverity {
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL',
}

export interface AgentCommand {
  id: string;
  agentId: string;
  commandType: CommandType;
  commandData: Record<string, any>;
  status: CommandStatus;
  result?: Record<string, any>;
  error?: string;
  createdAt: Date;
  sentAt?: Date;
  executedAt?: Date;
  completedAt?: Date;
  createdBy?: string;
}

export enum CommandType {
  EXECUTE = 'execute',
  RESTART = 'restart',
  UPDATE_CONFIG = 'update_config',
  INSTALL_SOFTWARE = 'install_software',
  UNINSTALL_SOFTWARE = 'uninstall_software',
  UPDATE_SOFTWARE = 'update_software',
  CUSTOM = 'custom',
}

export enum CommandStatus {
  PENDING = 'PENDING',
  SENT = 'SENT',
  EXECUTING = 'EXECUTING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
}

export interface AgentEvent {
  type: AgentEventType;
  agentId: string;
  data: any;
  timestamp: Date;
}

export enum AgentEventType {
  CONNECTED = 'agent:connected',
  DISCONNECTED = 'agent:disconnected',
  METRICS = 'agent:metrics',
  ALERT = 'agent:alert',
  COMMAND_RESULT = 'agent:command:result',
  STATUS = 'agents:status',
}

export interface AgentStats {
  totalAgents: number;
  activeAgents: number;
  offlineAgents: number;
  errorAgents: number;
  totalAlerts: number;
  unresolvedAlerts: number;
  pendingCommands: number;
}