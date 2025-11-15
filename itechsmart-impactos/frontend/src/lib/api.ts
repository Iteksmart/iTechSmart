import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (email: string, password: string, name: string, organizationName?: string) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      name,
      organization_name: organizationName,
    });
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

  refreshToken: async (refreshToken: string) => {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
};

// Organizations API
export const organizationsApi = {
  getAll: async () => {
    const response = await api.get('/organizations');
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/organizations/${id}`);
    return response.data;
  },

  create: async (data: any) => {
    const response = await api.post('/organizations', data);
    return response.data;
  },

  update: async (id: string, data: any) => {
    const response = await api.put(`/organizations/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/organizations/${id}`);
    return response.data;
  },
};

// Projects API
export const projectsApi = {
  getAll: async () => {
    const response = await api.get('/projects');
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },

  create: async (data: any) => {
    const response = await api.post('/projects', data);
    return response.data;
  },

  update: async (id: string, data: any) => {
    const response = await api.put(`/projects/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/projects/${id}`);
    return response.data;
  },
};

// Impact Assessments API
export const impactAssessmentsApi = {
  getAll: async () => {
    const response = await api.get('/impact-assessments');
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/impact-assessments/${id}`);
    return response.data;
  },

  create: async (data: any) => {
    const response = await api.post('/impact-assessments', data);
    return response.data;
  },

  update: async (id: string, data: any) => {
    const response = await api.put(`/impact-assessments/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/impact-assessments/${id}`);
    return response.data;
  },

  calculate: async (id: string) => {
    const response = await api.post(`/impact-assessments/${id}/calculate`);
    return response.data;
  },
};

// Analytics API
export const analyticsApi = {
  getOverview: async () => {
    const response = await api.get('/analytics/overview');
    return response.data;
  },

  getImpactMetrics: async (projectId?: string) => {
    const params = projectId ? { project_id: projectId } : {};
    const response = await api.get('/analytics/impact', { params });
    return response.data;
  },

  getFinancialMetrics: async (projectId?: string) => {
    const params = projectId ? { project_id: projectId } : {};
    const response = await api.get('/analytics/financial', { params });
    return response.data;
  },

  getTimeSeriesData: async (metric: string, projectId?: string) => {
    const params = projectId ? { project_id: projectId } : {};
    const response = await api.get(`/analytics/timeseries/${metric}`, { params });
    return response.data;
  },
};

// Users API
export const usersApi = {
  getAll: async () => {
    const response = await api.get('/users');
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  create: async (data: any) => {
    const response = await api.post('/users', data);
    return response.data;
  },

  update: async (id: string, data: any) => {
    const response = await api.put(`/users/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  },
};

export default api;