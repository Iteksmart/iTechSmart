import axios from 'axios';
import type {
  Deployment,
  DeploymentStatus,
  HealthStatus,
  ProductHealth,
  Metrics,
  Alert,
  AIOptimization,
  ConfigTemplate,
  DeploymentPlan,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8200';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Deployment API
export const deploymentApi = {
  deployProduct: async (data: {
    product_name: string;
    version?: string;
    strategy: string;
    environment: string;
    configuration?: any;
    port?: number;
  }) => {
    const response = await api.post('/api/deploy/product', data);
    return response.data;
  },

  deploySuite: async (data: {
    strategy: string;
    environment: string;
    products?: string[];
    configuration?: any;
  }) => {
    const response = await api.post('/api/deploy/suite', data);
    return response.data;
  },

  getDeploymentStatus: async (deploymentId: string): Promise<DeploymentStatus> => {
    const response = await api.get(`/api/deploy/status/${deploymentId}`);
    return response.data;
  },

  rollbackDeployment: async (deploymentId: string, reason?: string) => {
    const response = await api.post(`/api/deploy/rollback/${deploymentId}`, { reason });
    return response.data;
  },

  getDeploymentHistory: async (limit = 50, offset = 0): Promise<Deployment[]> => {
    const response = await api.get('/api/deploy/history', {
      params: { limit, offset },
    });
    return response.data;
  },

  getActiveDeployments: async () => {
    const response = await api.get('/api/deploy/active');
    return response.data;
  },

  deleteDeployment: async (deploymentId: string) => {
    const response = await api.delete(`/api/deploy/${deploymentId}`);
    return response.data;
  },
};

// Configuration API
export const configApi = {
  listTemplates: async () => {
    const response = await api.get('/api/config/templates');
    return response.data;
  },

  getTemplate: async (productName: string, environment = 'production'): Promise<ConfigTemplate> => {
    const response = await api.get(`/api/config/template/${productName}`, {
      params: { environment },
    });
    return response.data;
  },

  generateConfig: async (data: {
    product_name: string;
    environment: string;
    overrides?: any;
  }) => {
    const response = await api.post('/api/config/generate', data);
    return response.data;
  },

  validateConfig: async (data: {
    product_name: string;
    configuration: any;
  }) => {
    const response = await api.post('/api/config/validate', data);
    return response.data;
  },

  exportConfig: async (productName: string, format = 'json') => {
    const response = await api.get(`/api/config/export/${productName}`, {
      params: { format },
    });
    return response.data;
  },

  getVariables: async (productName: string) => {
    const response = await api.get(`/api/config/variables/${productName}`);
    return response.data;
  },
};

// Monitoring API
export const monitoringApi = {
  getOverallHealth: async (): Promise<HealthStatus> => {
    const response = await api.get('/api/monitor/health');
    return response.data;
  },

  getProductHealth: async (productName: string): Promise<ProductHealth> => {
    const response = await api.get(`/api/monitor/health/${productName}`);
    return response.data;
  },

  getAllMetrics: async (): Promise<Metrics> => {
    const response = await api.get('/api/monitor/metrics');
    return response.data;
  },

  getProductMetrics: async (productName: string, hours = 24) => {
    const response = await api.get(`/api/monitor/metrics/${productName}`, {
      params: { hours },
    });
    return response.data;
  },

  getActiveAlerts: async (): Promise<{ active_alerts: Alert[]; total: number }> => {
    const response = await api.get('/api/monitor/alerts');
    return response.data;
  },

  getProductAlerts: async (productName: string) => {
    const response = await api.get(`/api/monitor/alerts/${productName}`);
    return response.data;
  },

  triggerHealthCheck: async (productName: string) => {
    const response = await api.post(`/api/monitor/check/${productName}`);
    return response.data;
  },

  resolveAlert: async (alertId: string, notes?: string) => {
    const response = await api.post(`/api/monitor/alerts/${alertId}/resolve`, { notes });
    return response.data;
  },

  getUptime: async (productName: string, days = 30) => {
    const response = await api.get(`/api/monitor/uptime/${productName}`, {
      params: { days },
    });
    return response.data;
  },

  getPerformance: async (productName: string) => {
    const response = await api.get(`/api/monitor/performance/${productName}`);
    return response.data;
  },
};

// AI API
export const aiApi = {
  optimizeResources: async (data: {
    product_name: string;
    current_resources: any;
    workload_data?: any;
  }): Promise<AIOptimization> => {
    const response = await api.post('/api/ai/optimize/resources', data);
    return response.data;
  },

  optimizeStrategy: async (data: {
    products: string[];
    environment: string;
    constraints?: any;
  }) => {
    const response = await api.post('/api/ai/optimize/strategy', data);
    return response.data;
  },

  optimizeConfig: async (data: {
    product_name: string;
    current_config: any;
    optimization_goals?: string[];
  }) => {
    const response = await api.post('/api/ai/optimize/config', data);
    return response.data;
  },

  predictErrors: async (data: {
    product_name: string;
    deployment_plan: any;
  }) => {
    const response = await api.post('/api/ai/predict/errors', data);
    return response.data;
  },

  analyzePatterns: async (productName?: string) => {
    const response = await api.post('/api/ai/analyze/patterns', { product_name: productName });
    return response.data;
  },

  generatePlan: async (data: {
    products: string[];
    environment: string;
    strategy?: string;
  }): Promise<DeploymentPlan> => {
    const response = await api.post('/api/ai/plan', data);
    return response.data;
  },

  getInsights: async () => {
    const response = await api.get('/api/ai/insights');
    return response.data;
  },
};

export default api;
