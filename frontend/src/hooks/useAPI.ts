/**
 * API Hooks
 * 
 * React Query hooks for API communication
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  ChatMessageCreate,
  BrandConfigCreate,
  CouncilExecutionRequest,
} from "@/types/api";

// Query Keys
export const QUERY_KEYS = {
  agents: {
    all: ["agents", "status"] as const,
    status: (id: string) => ["agents", id, "status"] as const,
    info: (id: string) => ["agents", id, "info"] as const,
    list: ["agents", "list"] as const,
    session: ["agents", "session"] as const,
  },
  chat: {
    history: (limit: number, skip: number) => ["chat", "history", limit, skip] as const,
    mentions: ["chat", "mentions"] as const,
  },
  brandConfig: {
    active: ["brandConfig", "active"] as const,
    detail: (id: number) => ["brandConfig", id] as const,
    list: (skip: number, limit: number, activeOnly: boolean) =>
      ["brandConfig", "list", skip, limit, activeOnly] as const,
  },
  council: {
    status: ["council", "status"] as const,
  },
  websocket: {
    stats: ["websocket", "stats"] as const,
  },
};

// ============================================================================
// AGENTS
// ============================================================================

/**
 * Fetch all agents status
 * Auto-refetches every 3 seconds
 */
export function useAgentsStatus() {
  return useQuery({
    queryKey: QUERY_KEYS.agents.all,
    queryFn: api.agents.getAll,
    refetchInterval: 3000, // Poll every 3 seconds
    staleTime: 2000,
  });
}

/**
 * Fetch specific agent status
 */
export function useAgentStatus(agentId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.agents.status(agentId),
    queryFn: () => api.agents.getStatus(agentId),
    enabled: !!agentId,
    refetchInterval: 3000,
  });
}

/**
 * Fetch agent info (capabilities, description)
 */
export function useAgentInfo(agentId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.agents.info(agentId),
    queryFn: () => api.agents.getInfo(agentId),
    enabled: !!agentId,
    staleTime: 60000, // Cache for 1 minute
  });
}

/**
 * List all agents
 */
export function useAgentsList() {
  return useQuery({
    queryKey: QUERY_KEYS.agents.list,
    queryFn: api.agents.list,
    staleTime: 60000,
  });
}

/**
 * Get current council session status
 */
export function useSessionStatus() {
  return useQuery({
    queryKey: QUERY_KEYS.agents.session,
    queryFn: api.agents.getSessionStatus,
    refetchInterval: 5000,
  });
}

// ============================================================================
// CHAT
// ============================================================================

/**
 * Fetch chat history for a specific project
 */
export function useChatHistory(projectId: number | null, limit: number = 100, skip: number = 0) {
  return useQuery({
    queryKey: [...QUERY_KEYS.chat.history(limit, skip), projectId],
    queryFn: () => projectId ? api.chat.getHistory(projectId, limit, skip) : Promise.resolve({ total: 0, messages: [] }),
    enabled: projectId !== null,
    staleTime: 30000, // Cache for 30 seconds
    gcTime: 60000, // Keep in cache for 1 minute
    refetchOnMount: false, // Don't refetch on remount, use cached data
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });
}

/**
 * Send chat message
 */
export function useSendChatMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (message: ChatMessageCreate) => api.chat.sendMessage(message),
    onSuccess: () => {
      // Invalidate chat history to refetch
      queryClient.invalidateQueries({ queryKey: ["chat", "history"] });
    },
  });
}

/**
 * Get available @mentions
 */
export function useChatMentions() {
  return useQuery({
    queryKey: QUERY_KEYS.chat.mentions,
    queryFn: api.chat.getMentions,
    staleTime: 300000, // Cache for 5 minutes
  });
}

// ============================================================================
// BRAND CONFIGURATION
// ============================================================================

/**
 * Get active brand configuration
 */
export function useActiveBrandConfig() {
  return useQuery({
    queryKey: QUERY_KEYS.brandConfig.active,
    queryFn: api.brandConfig.getActive,
    retry: false, // Don't retry if no active config
  });
}

/**
 * Get specific brand configuration
 */
export function useBrandConfig(configId: number) {
  return useQuery({
    queryKey: QUERY_KEYS.brandConfig.detail(configId),
    queryFn: () => api.brandConfig.get(configId),
    enabled: configId > 0,
  });
}

/**
 * List brand configurations
 */
export function useBrandConfigList(
  skip: number = 0,
  limit: number = 100,
  activeOnly: boolean = false
) {
  return useQuery({
    queryKey: QUERY_KEYS.brandConfig.list(skip, limit, activeOnly),
    queryFn: () => api.brandConfig.list(skip, limit, activeOnly),
  });
}

/**
 * Create brand configuration
 */
export function useCreateBrandConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: BrandConfigCreate) => api.brandConfig.create(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brandConfig"] });
    },
  });
}

/**
 * Update brand configuration
 */
export function useUpdateBrandConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      configId,
      config,
    }: {
      configId: number;
      config: Partial<BrandConfigCreate>;
    }) => api.brandConfig.update(configId, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brandConfig"] });
    },
  });
}

/**
 * Delete brand configuration
 */
export function useDeleteBrandConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (configId: number) => api.brandConfig.delete(configId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brandConfig"] });
    },
  });
}

/**
 * Activate brand configuration
 */
export function useActivateBrandConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (configId: number) => api.brandConfig.activate(configId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brandConfig"] });
    },
  });
}

// ============================================================================
// COUNCIL EXECUTION
// ============================================================================

/**
 * Execute council session
 */
export function useExecuteCouncil() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CouncilExecutionRequest) =>
      api.council.execute(request),
    onSuccess: () => {
      // Invalidate agents and chat to reflect new session
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      queryClient.invalidateQueries({ queryKey: ["chat"] });
    },
  });
}

/**
 * Get council status
 */
export function useCouncilStatus() {
  return useQuery({
    queryKey: QUERY_KEYS.council.status,
    queryFn: api.council.getStatus,
    refetchInterval: 5000,
  });
}

/**
 * Initialize council
 */
export function useInitializeCouncil() {
  return useMutation({
    mutationFn: api.council.initialize,
  });
}

// ============================================================================
// WEBSOCKET
// ============================================================================

/**
 * Get WebSocket connection stats
 */
export function useWebSocketStats() {
  return useQuery({
    queryKey: QUERY_KEYS.websocket.stats,
    queryFn: api.websocket.getStats,
    refetchInterval: 10000,
  });
}

/**
 * Trigger simulated debate
 */
export function useTriggerSimulation() {
  return useMutation({
    mutationFn: api.websocket.triggerSimulation,
  });
}
