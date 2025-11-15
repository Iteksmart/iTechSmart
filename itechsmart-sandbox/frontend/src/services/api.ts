import axios from 'axios';
import type {
  Sandbox,
  CreateSandboxRequest,
  Process,
  ExecuteCodeRequest,
  SandboxFile,
  FileUploadRequest,
  Snapshot,
  CreateSnapshotRequest,
  ResourceMetric,
  TestRun,
  RunTestRequest,
  Template,
  Volume,
  Project,
  ApiResponse,
  PaginatedResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8033';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Sandbox API
export const sandboxApi = {
  list: async (): Promise<Sandbox[]> => {
    const response = await api.get<ApiResponse<Sandbox[]>>('/api/sandboxes');
    return response.data.data;
  },

  get: async (id: string): Promise<Sandbox> => {
    const response = await api.get<ApiResponse<Sandbox>>(`/api/sandboxes/${id}`);
    return response.data.data;
  },

  create: async (data: CreateSandboxRequest): Promise<Sandbox> => {
    const response = await api.post<ApiResponse<Sandbox>>('/api/sandboxes', data);
    return response.data.data;
  },

  start: async (id: string): Promise<Sandbox> => {
    const response = await api.post<ApiResponse<Sandbox>>(`/api/sandboxes/${id}/start`);
    return response.data.data;
  },

  stop: async (id: string): Promise<Sandbox> => {
    const response = await api.post<ApiResponse<Sandbox>>(`/api/sandboxes/${id}/stop`);
    return response.data.data;
  },

  terminate: async (id: string): Promise<void> => {
    await api.delete(`/api/sandboxes/${id}`);
  },

  executeCode: async (id: string, data: ExecuteCodeRequest): Promise<Process> => {
    const response = await api.post<ApiResponse<Process>>(
      `/api/sandboxes/${id}/execute`,
      data
    );
    return response.data.data;
  },

  executeCommand: async (id: string, command: string): Promise<Process> => {
    const response = await api.post<ApiResponse<Process>>(
      `/api/sandboxes/${id}/command`,
      { command }
    );
    return response.data.data;
  },

  getMetrics: async (id: string, limit: number = 100): Promise<ResourceMetric[]> => {
    const response = await api.get<ApiResponse<ResourceMetric[]>>(
      `/api/sandboxes/${id}/metrics`,
      { params: { limit } }
    );
    return response.data.data;
  },

  exposePort: async (id: string, port: number): Promise<{ url: string }> => {
    const response = await api.post<ApiResponse<{ url: string }>>(
      `/api/sandboxes/${id}/expose-port`,
      { port }
    );
    return response.data.data;
  },
};

// File API
export const fileApi = {
  list: async (sandboxId: string, path: string = '/'): Promise<SandboxFile[]> => {
    const response = await api.get<ApiResponse<SandboxFile[]>>(
      `/api/sandboxes/${sandboxId}/files`,
      { params: { path } }
    );
    return response.data.data;
  },

  upload: async (sandboxId: string, data: FileUploadRequest): Promise<SandboxFile> => {
    const response = await api.post<ApiResponse<SandboxFile>>(
      `/api/sandboxes/${sandboxId}/files`,
      data
    );
    return response.data.data;
  },

  download: async (sandboxId: string, path: string): Promise<Blob> => {
    const response = await api.get(`/api/sandboxes/${sandboxId}/files/download`, {
      params: { path },
      responseType: 'blob',
    });
    return response.data;
  },

  delete: async (sandboxId: string, path: string): Promise<void> => {
    await api.delete(`/api/sandboxes/${sandboxId}/files`, {
      params: { path },
    });
  },
};

// Snapshot API
export const snapshotApi = {
  list: async (sandboxId: string): Promise<Snapshot[]> => {
    const response = await api.get<ApiResponse<Snapshot[]>>(
      `/api/snapshots/sandbox/${sandboxId}`
    );
    return response.data.data;
  },

  create: async (sandboxId: string, data: CreateSnapshotRequest): Promise<Snapshot> => {
    const response = await api.post<ApiResponse<Snapshot>>(
      `/api/snapshots/sandbox/${sandboxId}`,
      data
    );
    return response.data.data;
  },

  restore: async (snapshotId: string): Promise<void> => {
    await api.post(`/api/snapshots/${snapshotId}/restore`);
  },

  delete: async (snapshotId: string): Promise<void> => {
    await api.delete(`/api/snapshots/${snapshotId}`);
  },
};

// Test API
export const testApi = {
  list: async (sandboxId: string): Promise<TestRun[]> => {
    const response = await api.get<ApiResponse<TestRun[]>>(
      `/api/tests/sandbox/${sandboxId}`
    );
    return response.data.data;
  },

  run: async (sandboxId: string, data: RunTestRequest): Promise<TestRun> => {
    const response = await api.post<ApiResponse<TestRun>>(
      `/api/tests/sandbox/${sandboxId}/run`,
      data
    );
    return response.data.data;
  },

  get: async (testId: string): Promise<TestRun> => {
    const response = await api.get<ApiResponse<TestRun>>(`/api/tests/${testId}`);
    return response.data.data;
  },
};

// Template API
export const templateApi = {
  list: async (): Promise<Template[]> => {
    const response = await api.get<ApiResponse<Template[]>>('/api/templates');
    return response.data.data;
  },

  get: async (id: string): Promise<Template> => {
    const response = await api.get<ApiResponse<Template>>(`/api/templates/${id}`);
    return response.data.data;
  },
};

// Process API
export const processApi = {
  get: async (processId: string): Promise<Process> => {
    const response = await api.get<ApiResponse<Process>>(`/api/processes/${processId}`);
    return response.data.data;
  },

  list: async (sandboxId: string): Promise<Process[]> => {
    const response = await api.get<ApiResponse<Process[]>>(
      `/api/sandboxes/${sandboxId}/processes`
    );
    return response.data.data;
  },
};

export default api;