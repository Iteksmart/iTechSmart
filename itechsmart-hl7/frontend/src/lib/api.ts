import axios from 'axios'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },
  
  logout: async () => {
    return api.post('/auth/logout')
  },
  
  getCurrentUser: async () => {
    return api.get('/auth/me')
  },
}

// Connections API
export const connectionsAPI = {
  list: async () => {
    const response = await api.get('/connections')
    return response.data
  },
  
  get: async (id: string) => {
    const response = await api.get(`/connections/${id}`)
    return response.data
  },
  
  create: async (data: any) => {
    const response = await api.post('/connections', data)
    return response.data
  },
  
  update: async (id: string, data: any) => {
    const response = await api.put(`/connections/${id}`, data)
    return response.data
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/connections/${id}`)
    return response.data
  },
  
  test: async (id: string) => {
    const response = await api.post(`/connections/${id}/test`)
    return response.data
  },
  
  stats: async () => {
    const response = await api.get('/connections/stats')
    return response.data
  },
}

// Health API
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health')
    return response.data
  },
  
  detailed: async () => {
    const response = await api.get('/health/detailed')
    return response.data
  },
}

// Messages API
export const messagesAPI = {
  list: async (params?: any) => {
    const response = await api.get('/messages', { params })
    return response.data
  },
  
  get: async (id: string) => {
    const response = await api.get(`/messages/${id}`)
    return response.data
  },
  
  stats: async () => {
    const response = await api.get('/messages/stats')
    return response.data
  },
}

// Patients API
export const patientsAPI = {
  list: async (params?: any) => {
    const response = await api.get('/patients', { params })
    return response.data
  },
  
  get: async (id: string) => {
    const response = await api.get(`/patients/${id}`)
    return response.data
  },
  
  search: async (query: string) => {
    const response = await api.get('/patients/search', { params: { q: query } })
    return response.data
  },
}

// Analytics API
export const analyticsAPI = {
  overview: async () => {
    const response = await api.get('/analytics/overview')
    return response.data
  },
  
  messageVolume: async (period: string) => {
    const response = await api.get('/analytics/message-volume', { params: { period } })
    return response.data
  },
  
  errorRates: async (period: string) => {
    const response = await api.get('/analytics/error-rates', { params: { period } })
    return response.data
  },
}

// Security API
export const securityAPI = {
  alerts: async () => {
    const response = await api.get('/security/alerts')
    return response.data
  },
  
  auditLogs: async (params?: any) => {
    const response = await api.get('/security/audit-logs', { params })
    return response.data
  },
}

export default api