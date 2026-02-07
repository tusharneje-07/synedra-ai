/**
 * API Client Configuration
 * 
 * Centralized API client for backend communication
 */

import type {
  AllAgentsStatusResponse,
  AgentInfo,
  ChatHistoryResponse,
  ChatMessage,
  ChatMessageCreate,
  BrandConfig,
  BrandConfigCreate,
  CouncilExecutionRequest,
  CouncilExecutionResponse,
} from "@/types/api";

// Get API URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";
const API_PREFIX = "/api";

/**
 * Base fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${API_PREFIX}${endpoint}`;
  
  const defaultHeaders: HeadersInit = {
    "Content-Type": "application/json",
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred");
  }
}

/**
 * API Client
 */
export const api = {
  // Health Check
  health: {
    check: () => apiFetch<{ status: string; database: string }>("/health"),
  },

  // Agents
  agents: {
    getAll: () => apiFetch<AllAgentsStatusResponse>("/agents/status"),
    
    getStatus: (agentId: string) =>
      apiFetch<any>(`/agents/${agentId}/status`),
    
    getInfo: (agentId: string) =>
      apiFetch<AgentInfo>(`/agents/${agentId}/info`),
    
    list: () => apiFetch<AgentInfo[]>("/agents/"),
    
    updateStatus: (
      agentId: string,
      status: string,
      progress?: number,
      currentTask?: string
    ) =>
      apiFetch<any>(`/agents/${agentId}/status`, {
        method: "POST",
        body: JSON.stringify({ status, progress, current_task: currentTask }),
      }),
    
    getSessionStatus: () =>
      apiFetch<any>("/agents/session/status"),
  },

  // Chat
  chat: {
    getHistory: (limit: number = 50, skip: number = 0) =>
      apiFetch<ChatHistoryResponse>(
        `/chat/history?limit=${limit}&skip=${skip}`
      ),
    
    sendMessage: (message: ChatMessageCreate) =>
      apiFetch<ChatMessage>("/chat/message", {
        method: "POST",
        body: JSON.stringify(message),
      }),
    
    getMentions: () =>
      apiFetch<any>("/chat/agents/mentions"),
  },

  // Brand Configuration
  brandConfig: {
    getActive: () =>
      apiFetch<BrandConfig>("/config/brand/active"),
    
    get: (configId: number) =>
      apiFetch<BrandConfig>(`/config/brand/${configId}`),
    
    list: (skip: number = 0, limit: number = 100, activeOnly: boolean = false) =>
      apiFetch<{ total: number; configs: BrandConfig[] }>(
        `/config/brand?skip=${skip}&limit=${limit}&active_only=${activeOnly}`
      ),
    
    create: (config: BrandConfigCreate) =>
      apiFetch<BrandConfig>("/config/brand", {
        method: "POST",
        body: JSON.stringify(config),
      }),
    
    update: (configId: number, config: Partial<BrandConfigCreate>) =>
      apiFetch<BrandConfig>(`/config/brand/${configId}`, {
        method: "PUT",
        body: JSON.stringify(config),
      }),
    
    delete: (configId: number) =>
      apiFetch<void>(`/config/brand/${configId}`, {
        method: "DELETE",
      }),
    
    activate: (configId: number) =>
      apiFetch<BrandConfig>(`/config/brand/${configId}/activate`, {
        method: "POST",
      }),
  },

  // Council Execution
  council: {
    execute: (request: CouncilExecutionRequest) =>
      apiFetch<CouncilExecutionResponse>("/council/execute", {
        method: "POST",
        body: JSON.stringify(request),
      }),
    
    getStatus: () =>
      apiFetch<{
        is_running: boolean;
        current_session_id: string | null;
        initialized: boolean;
      }>("/council/status"),
    
    initialize: () =>
      apiFetch<{
        success: boolean;
        initialized: boolean;
        message: string;
      }>("/council/initialize", {
        method: "POST",
      }),
  },

  // WebSocket
  websocket: {
    getStats: () =>
      apiFetch<any>("/ws/stats"),
    
    triggerSimulation: () =>
      apiFetch<any>("/ws/test/simulate-debate", {
        method: "POST",
      }),
  },
};

// Export API base URL for WebSocket connections
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8001";
export const WS_DEBATE_URL = `${WS_BASE_URL}${API_PREFIX}/ws/debate`;
