// Sandbox Types
export interface Sandbox {
  id: string;
  name: string;
  status: 'creating' | 'running' | 'stopped' | 'terminated' | 'error';
  image: string;
  gpu_type?: string;
  created_at: string;
  updated_at: string;
  terminated_at?: string;
  ttl_seconds: number;
  project_id?: string;
  template_id?: string;
  metadata?: Record<string, any>;
}

export interface CreateSandboxRequest {
  name: string;
  image: string;
  gpu_type?: string;
  ttl_seconds?: number;
  project_id?: string;
  template_id?: string;
  metadata?: Record<string, any>;
}

// Process Types
export interface Process {
  id: string;
  sandbox_id: string;
  command: string;
  status: 'running' | 'completed' | 'failed';
  exit_code?: number;
  stdout?: string;
  stderr?: string;
  created_at: string;
  completed_at?: string;
}

export interface ExecuteCodeRequest {
  code: string;
  language: string;
  timeout?: number;
}

// File Types
export interface SandboxFile {
  id: string;
  sandbox_id: string;
  path: string;
  size: number;
  created_at: string;
  updated_at: string;
}

export interface FileUploadRequest {
  path: string;
  content: string;
}

// Snapshot Types
export interface Snapshot {
  id: string;
  sandbox_id: string;
  name: string;
  description?: string;
  size_bytes: number;
  created_at: string;
}

export interface CreateSnapshotRequest {
  name: string;
  description?: string;
}

// Resource Metrics Types
export interface ResourceMetric {
  id: string;
  sandbox_id: string;
  cpu_percent: number;
  memory_mb: number;
  memory_percent: number;
  gpu_percent?: number;
  gpu_memory_mb?: number;
  disk_read_mb: number;
  disk_write_mb: number;
  network_rx_mb: number;
  network_tx_mb: number;
  timestamp: string;
}

// Test Types
export interface TestRun {
  id: string;
  sandbox_id: string;
  product_name: string;
  test_type: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  results?: Record<string, any>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

export interface RunTestRequest {
  product_name: string;
  test_type: string;
}

// Template Types
export interface Template {
  id: string;
  name: string;
  description?: string;
  image: string;
  gpu_type?: string;
  default_ttl_seconds: number;
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Volume Types
export interface Volume {
  id: string;
  name: string;
  size_gb: number;
  mount_path: string;
  created_at: string;
}

// Project Types
export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}