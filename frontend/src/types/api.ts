/**
 * API Type Definitions
 * 
 * TypeScript types matching backend FastAPI schemas
 */

// Agent Types
export interface AgentMetrics {
  total_analyses: number;
  successful_analyses: number;
  average_response_time: number | null;
  last_active: string | null;
}

export interface Agent {
  agent_id: string;
  agent_name: string;
  role: string;
  status: "idle" | "thinking" | "debating" | "voting" | "completed" | "error";
  progress: number | null;
  current_task: string | null;
  last_output: string | null;
  metrics: AgentMetrics;
  is_available: boolean;
  error_message: string | null;
}

export interface AllAgentsStatusResponse {
  total_agents: number;
  active_agents: number;
  idle_agents: number;
  agents: Agent[];
  last_updated: string;
}

export interface AgentCapability {
  name: string;
  description: string;
  examples?: string[];
}

export interface AgentInfo {
  agent_id: string;
  agent_name: string;
  role: string;
  description: string;
  capabilities: AgentCapability[];
  status: string;
  model?: string;
}

// Chat Types
export interface MentionedAgent {
  agent_id: string;
  agent_name: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  user_name: string;
  timestamp: string;
  mentioned_agents: MentionedAgent[];
  is_agent_triggered: boolean;
  session_id: string | null;
}

export interface ChatHistoryResponse {
  total: number;
  messages: ChatMessage[];
}

export interface ChatMessageCreate {
  content: string;
  user_name?: string;
}

// Brand Config Types
export interface BrandConfig {
  id: number;
  brand_name: string;
  brand_tone: string | null;
  brand_description: string | null;
  product_list: any[] | null;
  target_audience: any | null;
  brand_keywords: string[] | null;
  messaging_guidelines: string | null;
  social_platforms: any[] | null;
  posting_frequency: any[] | null;
  competitors: string[] | null;
  market_segment: string | null;
  is_active: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface BrandConfigCreate {
  brand_name: string;
  brand_tone?: string;
  brand_description?: string;
  product_list?: any[];
  target_audience?: any;
  brand_keywords?: string[];
  messaging_guidelines?: string;
  social_platforms?: any[];
  posting_frequency?: any[];
  competitors?: string[];
  market_segment?: string;
}

// WebSocket Message Types
export interface WSMessage {
  type: string;
  timestamp: string;
}

export interface AgentThinkingMessage extends WSMessage {
  type: "agent_thinking";
  agent_id: string;
  agent_name: string;
  content: string;
  step: string | null;
}

export interface AgentStatusMessage extends WSMessage {
  type: "agent_status";
  agent_id: string;
  agent_name: string;
  status: "idle" | "thinking" | "debating" | "voting" | "completed";
  progress: number | null;
}

export interface DebateMessage extends WSMessage {
  type: "debate";
  agent_id: string;
  agent_name: string;
  position: string;
  responding_to: string | null;
  debate_round: number | null;
}

export interface DecisionMessage extends WSMessage {
  type: "decision";
  decision: string;
  confidence: number | null;
  consensus_level: string | null;
  votes: any | null;
}

export interface SystemMessage extends WSMessage {
  type: "system";
  level: "info" | "warning" | "error" | "success";
  message: string;
}

export interface CouncilStartMessage extends WSMessage {
  type: "council_start";
  session_id: string;
  topic: string;
  agents: string[];
}

export interface CouncilEndMessage extends WSMessage {
  type: "council_end";
  session_id: string;
  duration_seconds: number | null;
  outcome: string;
}

export type WebSocketMessage =
  | AgentThinkingMessage
  | AgentStatusMessage
  | DebateMessage
  | DecisionMessage
  | SystemMessage
  | CouncilStartMessage
  | CouncilEndMessage;

// Council Execution Types
export interface CouncilExecutionRequest {
  prompt: string;
  trigger_agents?: string[];
  use_active_brand_config?: boolean;
  brand_config_id?: number;
}

export interface CouncilExecutionResponse {
  session_id: string;
  success: boolean;
  decision: string | null;
  confidence: number | null;
  consensus_level: string | null;
  agent_outputs: any | null;
  error: string | null;
  websocket_url: string;
}
