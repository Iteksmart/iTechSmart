// Type definitions for iTechSmart MDM Agent

export interface Deployment {
  deployment_id: string;
  product_name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'rolled_back';
  strategy: 'docker_compose' | 'kubernetes' | 'manual';
  environment: 'development' | 'staging' | 'production';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  port?: number;
  health_endpoint?: string;
}

export interface DeploymentStatus {
  deployment_id: string;
  product_name: string;
  status: string;
  progress: number;
  message: string;
  logs?: string;
  error_message?: string;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  total_services: number;
  healthy: number;
  degraded: number;
  unhealthy: number;
  active_alerts: number;
  timestamp: string;
}

export interface ProductHealth {
  product_name: string;
  status: string;
  response_time: number;
  last_check: string;
  uptime: string;
  details: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
  };
}

export interface Metrics {
  timestamp: string;
  services: ServiceMetric[];
}

export interface ServiceMetric {
  name: string;
  cpu_usage: number;
  memory_usage: number;
  request_count: number;
  error_count: number;
  avg_response_time: number;
}

export interface Alert {
  id: string;
  service_name: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: string;
  resolved: boolean;
}

export interface AIOptimization {
  product_name: string;
  current_resources: any;
  recommended_resources: any;
  estimated_savings: any;
  confidence_score: number;
  reasoning: string;
  timestamp: string;
}

export interface ConfigTemplate {
  product_name: string;
  environment: string;
  template: any;
  variables: any;
}

export interface DeploymentPlan {
  plan_id: string;
  products: string[];
  execution_order: string[];
  environment: string;
  recommended_strategy: string;
  estimated_duration: string;
  steps: any[];
  ai_optimizations: string[];
  confidence_score: number;
  timestamp: string;
}
