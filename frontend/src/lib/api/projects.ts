/**
 * Project API Client
 * Handles all project-related API calls
 */

// API Base URL and helper
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api';

async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${API_PREFIX}${endpoint}`;
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `HTTP ${response.status}: ${response.statusText}`
    );
  }

  if (options.method === 'DELETE') {
    return undefined as T;
  }

  return await response.json();
}

const apiClient = {
  get: <T>(endpoint: string) => apiFetch<T>(endpoint, { method: 'GET' }),
  post: <T>(endpoint: string, data?: any) =>
    apiFetch<T>(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: <T>(endpoint: string, data?: any) =>
    apiFetch<T>(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint: string) => apiFetch(endpoint, { method: 'DELETE' }),
};

export interface Project {
  id: number;
  name: string;
  description?: string;
  post_topic?: string;
  product_details?: Record<string, any>;
  target_details?: Record<string, any>;
  questionnaire_data?: Record<string, any>;
  brand_config_id: number;
  status: 'draft' | 'active' | 'completed' | 'archived';
  last_session_id?: string;
  council_summary?: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectListItem {
  id: number;
  name: string;
  description?: string;
  status: string;
  brand_config_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectData {
  name: string;
  description?: string;
  post_topic?: string;
  product_details?: Record<string, any>;
  target_details?: Record<string, any>;
  brand_config_id: number;
}

export interface UpdateProjectData {
  name?: string;
  description?: string;
  post_topic?: string;
  product_details?: Record<string, any>;
  target_details?: Record<string, any>;
  questionnaire_data?: Record<string, any>;
  status?: 'draft' | 'active' | 'completed' | 'archived';
  last_session_id?: string;
  council_summary?: string;
}

export interface QuestionnaireSection {
  id: string;
  title: string;
  description: string;
  questions: Question[];
}

export interface Question {
  id: string;
  question: string;
  type: 'text' | 'textarea' | 'select' | 'multi-select';
  required: boolean;
  placeholder?: string;
  options?: string[];
}

export interface Questionnaire {
  project_name: string;
  sections: QuestionnaireSection[];
  metadata: {
    total_sections: number;
    total_questions: number;
    estimated_time_minutes: number;
  };
}

export const projectsApi = {
  /**
   * List all projects
   */
  list: async (params?: {
    brand_config_id?: number;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<ProjectListItem[]> => {
    const searchParams = new URLSearchParams();
    if (params?.brand_config_id) searchParams.append('brand_config_id', params.brand_config_id.toString());
    if (params?.status) searchParams.append('status', params.status);
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const query = searchParams.toString();
    const url = `/projects${query ? `?${query}` : ''}`;
    
    return apiClient.get<ProjectListItem[]>(url);
  },

  /**
   * Get a specific project by ID
   */
  get: async (projectId: number): Promise<Project> => {
    return apiClient.get<Project>(`/projects/${projectId}`);
  },

  /**
   * Create a new project
   */
  create: async (data: CreateProjectData): Promise<Project> => {
    return apiClient.post<Project>('/projects', data);
  },

  /**
   * Update an existing project
   */
  update: async (projectId: number, data: UpdateProjectData): Promise<Project> => {
    return apiClient.put<Project>(`/projects/${projectId}`, data);
  },

  /**
   * Update project questionnaire data
   */
  updateQuestionnaire: async (
    projectId: number,
    questionnaireData: Record<string, any>
  ): Promise<Project> => {
    return apiClient.put<Project>(`/projects/${projectId}/questionnaire`, {
      questionnaire_data: questionnaireData,
    });
  },

  /**
   * Delete a project
   */
  delete: async (projectId: number): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}`);
  },

  /**
   * Generate AI-powered questionnaire
   */
  generateQuestionnaire: async (params: {
    project_name: string;
    description?: string;
    product_details?: Record<string, any>;
    target_details?: Record<string, any>;
  }): Promise<Questionnaire> => {
    return apiClient.post<Questionnaire>('/projects/generate-questionnaire', params);
  },

  /**
   * Validate questionnaire responses
   */
  validateResponses: async (
    questionnaire: Questionnaire,
    responses: Record<string, any>
  ): Promise<{ valid: boolean; errors: any[] }> => {
    return apiClient.post('/projects/validate-responses', {
      questionnaire,
      responses,
    });
  },

  /**
   * Get project sessions
   */
  getSessions: async (projectId: number, limit = 10) => {
    return apiClient.get(`/projects/${projectId}/sessions?limit=${limit}`);
  },

  /**
   * Get project messages
   */
  getMessages: async (projectId: number, sessionId?: string, limit = 100) => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (sessionId) params.append('session_id', sessionId);
    return apiClient.get(`/projects/${projectId}/messages?${params}`);
  },
};
