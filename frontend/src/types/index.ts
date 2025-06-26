// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

// Authentication Types
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  client_id: string;
  created_at: string;
}

// Business Interest Types
export interface BusinessInterest {
  id: number;
  client_id: string;
  interest_text: string;
  created_at: string;
}

export interface BusinessInterestCreate {
  interest_text: string;
}

// Source Types
export interface Source {
  source_id: number;
  source_url: string;
  created_at: string;
}

export interface SourceCreate {
  source_url: string;
}

export interface SourceListResponse {
  sources: Source[];
  total_count: number;
}

export interface PopularSources {
  [category: string]: string[];
}

// News Analysis Types
export interface Article {
  title: string;
  content: string;
  url: string;
  source: string;
  published_date?: string;
  relevance_score?: number;
}

export interface NewsAnalysisRequest {
  business_interest: string;
  sources: string[];
}

export interface NewsAnalysisResponse {
  session_id: number;
  articles: Article[];
  summary?: string;
  total_articles: number;
  relevant_articles: number;
  analysis_date: string;
}

export interface AnalysisSession {
  id: number;
  business_interest_id: number;
  sources: string[];
  created_at: string;
  has_results: boolean;
}

// Statistics Types
export interface UserStatistics {
  total_business_interests: number;
  total_analysis_sessions: number;
  sessions_last_7_days: number;
  latest_interest?: string;
  account_created: string;
}

export interface DashboardData {
  recent_sessions: {
    id: number;
    created_at: string;
    has_results: boolean;
  }[];
  recent_interests: {
    id: number;
    interest_text: string;
    created_at: string;
  }[];
}

// UI State Types
export interface AppState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  currentStep: 'business-interest' | 'sources' | 'analysis' | 'results';
  businessInterest: string;
  selectedSources: string[];
  currentAnalysis: NewsAnalysisResponse | null;
}

// Form Types
export interface BusinessInterestForm {
  interest_text: string;
}

export interface SourceForm {
  source_url: string;
}

export interface AnalysisForm {
  business_interest: string;
  sources: string[];
} 