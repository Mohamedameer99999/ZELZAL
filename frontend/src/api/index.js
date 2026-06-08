import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('zelzal_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('zelzal_refresh')
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/auth/refresh', {}, {
            headers: { Authorization: `Bearer ${refreshToken}` },
          })
          localStorage.setItem('zelzal_token', data.access_token)
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('zelzal_token')
          localStorage.removeItem('zelzal_refresh')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (username, email, password) => api.post('/auth/register', { username, email, password }),
  me: () => api.get('/auth/me'),
  refresh: () => api.post('/auth/refresh'),
}

export const dashboardAPI = {
  stats: () => api.get('/dashboard/stats'),
  activities: (limit) => api.get(`/dashboard/activities?limit=${limit || 20}`),
  overview: () => api.get('/dashboard/overview'),
}

export const securityAPI = {
  events: (params) => api.get('/security/events', { params }),
  createEvent: (data) => api.post('/security/events', data),
  updateEvent: (id, data) => api.patch(`/security/events/${id}`, data),
  threatMap: () => api.get('/security/threat-map'),
  reports: () => api.get('/security/reports'),
}

export const aiAPI = {
  chat: (message, conversationId) => api.post('/ai/chat', { message, conversation_id: conversationId }),
  conversations: () => api.get('/ai/conversations'),
  getConversation: (id) => api.get(`/ai/conversations/${id}`),
  deleteConversation: (id) => api.delete(`/ai/conversations/${id}`),
  recommendations: () => api.get('/ai/recommendations'),
}

export const projectsAPI = {
  list: (params) => api.get('/projects', { params }),
  create: (data) => api.post('/projects', data),
  get: (id) => api.get(`/projects/${id}`),
  update: (id, data) => api.patch(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
  createTask: (projectId, data) => api.post(`/projects/${projectId}/tasks`, data),
  updateTask: (taskId, data) => api.patch(`/projects/tasks/${taskId}`, data),
  deleteTask: (taskId) => api.delete(`/projects/tasks/${taskId}`),
}

export const analyticsAPI = {
  metrics: (period) => api.get(`/analytics/metrics?period=${period || '7d'}`),
  trackEvent: (data) => api.post('/analytics/events', data),
  performance: () => api.get('/analytics/performance'),
}

export const usersAPI = {
  list: () => api.get('/users'),
  profile: () => api.get('/users/profile'),
  updateProfile: (data) => api.patch('/users/profile', data),
  updateRole: (userId, role) => api.patch(`/users/${userId}/role`, { role }),
  deleteUser: (userId) => api.delete(`/users/${userId}`),
}

export default api
