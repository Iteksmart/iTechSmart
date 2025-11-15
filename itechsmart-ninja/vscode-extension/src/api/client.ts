/**
 * API Client for iTechSmart Ninja Backend
 */
import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';
import { AuthManager } from '../auth/manager';

export interface Task {
    id: number;
    title: string;
    description: string;
    task_type: string;
    status: string;
    progress: number;
    result?: any;
    error?: string;
    created_at: string;
    started_at?: string;
    completed_at?: string;
}

export interface TaskStep {
    id: number;
    task_id: number;
    step_number: number;
    agent_type: string;
    description: string;
    status: string;
    result?: any;
    error?: string;
    started_at?: string;
    completed_at?: string;
}

export interface Agent {
    name: string;
    type: string;
    description: string;
    capabilities: string[];
    supported_languages?: string[];
    example_tasks: string[];
}

export interface FileInfo {
    filename: string;
    filepath: string;
    size: number;
    content_type: string;
    uploaded_at: string;
    url: string;
}

export class ApiClient {
    private client: AxiosInstance;
    private authManager: AuthManager;

    constructor(authManager: AuthManager) {
        this.authManager = authManager;
        
        const config = vscode.workspace.getConfiguration('itechsmart');
        const apiUrl = config.get<string>('apiUrl') || 'http://localhost:8000';

        this.client = axios.create({
            baseURL: apiUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Add auth interceptor
        this.client.interceptors.request.use(
            (config) => {
                const token = this.authManager.getAccessToken();
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => {
                return Promise.reject(error);
            }
        );

        // Add response interceptor for token refresh
        this.client.interceptors.response.use(
            (response) => response,
            async (error) => {
                const originalRequest = error.config;

                if (error.response?.status === 401 && !originalRequest._retry) {
                    originalRequest._retry = true;

                    try {
                        await this.authManager.refreshToken();
                        const token = this.authManager.getAccessToken();
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return this.client(originalRequest);
                    } catch (refreshError) {
                        await this.authManager.logout();
                        return Promise.reject(refreshError);
                    }
                }

                return Promise.reject(error);
            }
        );
    }

    // Authentication
    async login(email: string, password: string): Promise<any> {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await this.client.post('/api/v1/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        return response.data;
    }

    async register(email: string, password: string, fullName: string): Promise<any> {
        const response = await this.client.post('/api/v1/auth/register', {
            email,
            password,
            full_name: fullName
        });

        return response.data;
    }

    async getCurrentUser(): Promise<any> {
        const response = await this.client.get('/api/v1/auth/me');
        return response.data;
    }

    async refreshAccessToken(refreshToken: string): Promise<any> {
        const response = await this.client.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken
        });
        return response.data;
    }

    // Tasks
    async createTask(data: {
        title: string;
        description: string;
        task_type: string;
        parameters?: any;
    }): Promise<Task> {
        const response = await this.client.post('/api/v1/tasks', data);
        return response.data;
    }

    async getTasks(filters?: {
        status?: string;
        task_type?: string;
        limit?: number;
    }): Promise<Task[]> {
        const response = await this.client.get('/api/v1/tasks', {
            params: filters
        });
        return response.data;
    }

    async getTask(taskId: number): Promise<Task> {
        const response = await this.client.get(`/api/v1/tasks/${taskId}`);
        return response.data;
    }

    async getTaskSteps(taskId: number): Promise<TaskStep[]> {
        const response = await this.client.get(`/api/v1/tasks/${taskId}/steps`);
        return response.data;
    }

    async cancelTask(taskId: number): Promise<void> {
        await this.client.post(`/api/v1/tasks/${taskId}/cancel`);
    }

    async deleteTask(taskId: number): Promise<void> {
        await this.client.delete(`/api/v1/tasks/${taskId}`);
    }

    async getTaskStats(): Promise<any> {
        const response = await this.client.get('/api/v1/tasks/stats/summary');
        return response.data;
    }

    // Agents
    async getAgents(): Promise<Agent[]> {
        const response = await this.client.get('/api/v1/agents');
        return response.data;
    }

    async getAgent(agentType: string): Promise<Agent> {
        const response = await this.client.get(`/api/v1/agents/${agentType}`);
        return response.data;
    }

    async getAgentCapabilities(agentType: string): Promise<any[]> {
        const response = await this.client.get(`/api/v1/agents/${agentType}/capabilities`);
        return response.data;
    }

    // Files
    async uploadFile(file: Buffer, filename: string): Promise<FileInfo> {
        const formData = new FormData();
        const blob = new Blob([file]);
        formData.append('file', blob, filename);

        const response = await this.client.post('/api/v1/files/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        return response.data;
    }

    async getFiles(): Promise<FileInfo[]> {
        const response = await this.client.get('/api/v1/files');
        return response.data.files;
    }

    async downloadFile(userId: number, filename: string): Promise<Buffer> {
        const response = await this.client.get(
            `/api/v1/files/download/${userId}/${filename}`,
            { responseType: 'arraybuffer' }
        );
        return Buffer.from(response.data);
    }

    async deleteFile(filename: string): Promise<void> {
        await this.client.delete(`/api/v1/files/${filename}`);
    }

    // Health check
    async healthCheck(): Promise<any> {
        const response = await this.client.get('/health');
        return response.data;
    }
}