import axios from 'axios';
import {
  LoginResponse,
  BusinessInterest,
  BusinessInterestCreate,
  Source,
  SourceCreate,
  SourceListResponse,
  PopularSources,
  NewsAnalysisRequest,
  NewsAnalysisResponse,
  AnalysisSession,
  UserStatistics,
  DashboardData,
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api',  // Use full backend URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
};

// Business Interest API
export const businessInterestAPI = {
  create: async (data: BusinessInterestCreate): Promise<BusinessInterest> => {
    const response = await api.post<BusinessInterest>('/analysis/business-interest', data);
    return response.data;
  },

  getAll: async (): Promise<BusinessInterest[]> => {
    const response = await api.get<BusinessInterest[]>('/analysis/business-interest');
    return response.data;
  },

  getById: async (id: number): Promise<BusinessInterest> => {
    const response = await api.get<BusinessInterest>(`/analysis/business-interest/${id}`);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/analysis/business-interest/${id}`);
    return response.data;
  },
};

// Sources API
export const sourcesAPI = {
  getAll: async (): Promise<SourceListResponse> => {
    const response = await api.get<SourceListResponse>('/sources/');
    return response.data;
  },

  add: async (data: SourceCreate): Promise<Source> => {
    console.log('sourcesAPI.add called with:', data);
    console.log('API base URL:', api.defaults.baseURL);
    const response = await api.post<Source>('/sources/', data);
    console.log('API response:', response.data);
    return response.data;
  },

  remove: async (sourceId: number) => {
    const response = await api.delete(`/sources/${sourceId}`);
    return response.data;
  },

  getPopular: async (): Promise<PopularSources> => {
    const response = await api.get<PopularSources>('/sources/popular');
    return response.data;
  },
};

// News Analysis API
export const newsAPI = {
  analyze: async (data: NewsAnalysisRequest): Promise<NewsAnalysisResponse> => {
    const response = await api.post<NewsAnalysisResponse>('/news/analyze', data);
    return response.data;
  },

  getSessions: async (): Promise<AnalysisSession[]> => {
    const response = await api.get<AnalysisSession[]>('/news/sessions');
    return response.data;
  },

  getSession: async (sessionId: number): Promise<NewsAnalysisResponse> => {
    const response = await api.get<NewsAnalysisResponse>(`/news/sessions/${sessionId}`);
    return response.data;
  },

  deleteSession: async (sessionId: number) => {
    const response = await api.delete(`/news/sessions/${sessionId}`);
    return response.data;
  },
};

// Analysis API
export const analysisAPI = {
  getStatistics: async (): Promise<UserStatistics> => {
    const response = await api.get<UserStatistics>('/analysis/statistics');
    return response.data;
  },

  getDashboard: async (): Promise<DashboardData> => {
    const response = await api.get<DashboardData>('/analysis/dashboard');
    return response.data;
  },
};

export default api; 