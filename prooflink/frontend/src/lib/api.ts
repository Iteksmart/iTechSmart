import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  
  register: async (email: string, password: string, name: string) => {
    const response = await api.post('/auth/register', { email, password, name });
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Documents API
export const documentsAPI = {
  list: async (params?: any) => {
    const response = await api.get('/documents', { params });
    return response.data;
  },
  
  get: async (id: string) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },
  
  upload: async (file: File, metadata?: any) => {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  verify: async (id: string) => {
    const response = await api.post(`/documents/${id}/verify`);
    return response.data;
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },
};

// Verification API
export const verificationAPI = {
  verify: async (documentId: string, options?: any) => {
    const response = await api.post('/verify', { documentId, ...options });
    return response.data;
  },
  
  getStatus: async (verificationId: string) => {
    const response = await api.get(`/verify/${verificationId}`);
    return response.data;
  },
  
  history: async (params?: any) => {
    const response = await api.get('/verify/history', { params });
    return response.data;
  },
};

// Batch API
export const batchAPI = {
  create: async (documents: string[]) => {
    const response = await api.post('/batch', { documents });
    return response.data;
  },
  
  get: async (id: string) => {
    const response = await api.get(`/batch/${id}`);
    return response.data;
  },
  
  list: async (params?: any) => {
    const response = await api.get('/batch', { params });
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  overview: async () => {
    const response = await api.get('/analytics/overview');
    return response.data;
  },
  
  verifications: async (period: string) => {
    const response = await api.get('/analytics/verifications', { params: { period } });
    return response.data;
  },
  
  accuracy: async (period: string) => {
    const response = await api.get('/analytics/accuracy', { params: { period } });
    return response.data;
  },
};

// API Keys API
export const apiKeysAPI = {
  list: async () => {
    const response = await api.get('/api-keys');
    return response.data;
  },
  
  create: async (name: string, permissions: string[]) => {
    const response = await api.post('/api-keys', { name, permissions });
    return response.data;
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/api-keys/${id}`);
    return response.data;
  },
};

// Alias exports for backward compatibility
  export { api };
  export const proofsAPI = verificationAPI;
  export const usersAPI = {
    list: async () => {
      const response = await api.get('/users');
      return response.data;
    },
    get: async (id: string) => {
      const response = await api.get(`/users/${id}`);
      return response.data;
    },
  };

  export default api;