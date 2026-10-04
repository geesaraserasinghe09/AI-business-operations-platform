import axios from 'axios';
import {
  User,
  Workflow,
  Task,
  Approval,
  AgentMetric,
  DocumentItem,
  ReportItem,
  DashboardStats,
  ActivityLog,
  NotificationItem,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Auth
  auth: {
    login: async (email: string, password: string) => {
      const res = await apiClient.post('/auth/login', { email, password });
      return res.data;
    },
    register: async (email: string, password: string, full_name: string, role = 'employee') => {
      const res = await apiClient.post('/auth/register', { email, password, full_name, role });
      return res.data;
    },
    getMe: async (): Promise<User> => {
      const res = await apiClient.get('/auth/me');
      return res.data;
    },
  },

  // Workflows
  workflows: {
    list: async (status?: string, search?: string): Promise<Workflow[]> => {
      const params: Record<string, any> = {};
      if (status) params.status = status;
      if (search) params.search = search;
      const res = await apiClient.get('/workflows', { params });
      return res.data;
    },
    get: async (id: string): Promise<Workflow> => {
      const res = await apiClient.get(`/workflows/${id}`);
      return res.data;
    },
    create: async (prompt: string, title?: string): Promise<Workflow> => {
      const res = await apiClient.post('/workflows', { prompt, title, auto_execute: true });
      return res.data;
    },
    retry: async (id: string): Promise<Workflow> => {
      const res = await apiClient.post(`/workflows/${id}/retry`);
      return res.data;
    },
  },

  // Tasks
  tasks: {
    list: async (filters?: { status?: string; priority?: string; agent?: string; search?: string }): Promise<Task[]> => {
      const res = await apiClient.get('/tasks', { params: filters });
      return res.data;
    },
    create: async (task: Partial<Task>): Promise<Task> => {
      const res = await apiClient.post('/tasks', task);
      return res.data;
    },
    update: async (id: string, updates: Partial<Task>): Promise<Task> => {
      const res = await apiClient.put(`/tasks/${id}`, updates);
      return res.data;
    },
  },

  // Approvals (Human-in-the-Loop)
  approvals: {
    list: async (status?: string): Promise<Approval[]> => {
      const params = status ? { status } : {};
      const res = await apiClient.get('/approvals', { params });
      return res.data;
    },
    action: async (id: string, action: 'approve' | 'reject', review_notes?: string): Promise<Approval> => {
      const res = await apiClient.post(`/approvals/${id}/action`, { action, review_notes });
      return res.data;
    },
    modify: async (id: string, modification_payload: Record<string, any>, review_notes?: string): Promise<Approval> => {
      const res = await apiClient.post(`/approvals/${id}/modify`, { modification_payload, review_notes });
      return res.data;
    },
  },

  // Agents
  agents: {
    list: async (): Promise<AgentMetric[]> => {
      const res = await apiClient.get('/agents');
      return res.data;
    },
    toggleStatus: async (agentType: string) => {
      const res = await apiClient.post(`/agents/${agentType}/toggle-status`);
      return res.data;
    },
  },

  // Documents & RAG
  documents: {
    list: async (): Promise<DocumentItem[]> => {
      const res = await apiClient.get('/documents');
      return res.data;
    },
    get: async (id: string): Promise<DocumentItem> => {
      const res = await apiClient.get(`/documents/${id}`);
      return res.data;
    },
    upload: async (file: File): Promise<DocumentItem> => {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    },
    queryRAG: async (question: string, documentId?: string) => {
      const res = await apiClient.post('/documents/query', {
        question,
        document_id: documentId || null,
      });
      return res.data;
    },
    delete: async (id: string) => {
      const res = await apiClient.delete(`/documents/${id}`);
      return res.data;
    },
  },

  // Reports
  reports: {
    list: async (type?: string): Promise<ReportItem[]> => {
      const params = type ? { report_type: type } : {};
      const res = await apiClient.get('/reports', { params });
      return res.data;
    },
    get: async (id: string): Promise<ReportItem> => {
      const res = await apiClient.get(`/reports/${id}`);
      return res.data;
    },
    getDownloadUrl: (id: string, format = 'markdown') => {
      const token = localStorage.getItem('access_token');
      const tokenParam = token ? `&token=${encodeURIComponent(token)}` : '';
      return `${API_BASE_URL}/reports/${id}/download?format_type=${format}${tokenParam}`;
    },
  },

  // Analytics & Dashboard
  analytics: {
    getDashboard: async (): Promise<DashboardStats> => {
      const res = await apiClient.get('/analytics/dashboard');
      return res.data;
    },
  },

  // Audit Logs
  audit: {
    list: async (action?: string, agent?: string): Promise<ActivityLog[]> => {
      const params: Record<string, any> = {};
      if (action) params.action = action;
      if (agent) params.agent = agent;
      const res = await apiClient.get('/audit', { params });
      return res.data;
    },
  },

  // Notifications
  notifications: {
    list: async (): Promise<NotificationItem[]> => {
      const res = await apiClient.get('/notifications');
      return res.data;
    },
    markRead: async (id: string) => {
      const res = await apiClient.put(`/notifications/${id}/read`);
      return res.data;
    },
    markAllRead: async () => {
      const res = await apiClient.post('/notifications/read-all');
      return res.data;
    },
  },

  // Users (Admin)
  users: {
    list: async (): Promise<User[]> => {
      const res = await apiClient.get('/users');
      return res.data;
    },
    update: async (id: string, updates: Partial<User>): Promise<User> => {
      const res = await apiClient.put(`/users/${id}`, updates);
      return res.data;
    },
  },
};

export default apiClient;
