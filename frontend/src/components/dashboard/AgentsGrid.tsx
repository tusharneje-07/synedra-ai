import AgentCard, { type AgentStatus, type AgentColor } from "./AgentCard";
import { useAgentsStatus } from "@/hooks/useAPI";
import { Loader2 } from "lucide-react";

// Map agent IDs to colors
const agentColors: Record<string, AgentColor> = {
  "trend": "indigo",
  "engagement": "teal",
  "brand": "purple",
  "risk": "amber",
  "compliance": "blue",
  "arbitrator": "blue",
};

// Map backend status to frontend status
const mapStatus = (status: string): AgentStatus => {
  if (status === "idle") return "Idle";
  if (status === "thinking" || status === "debating" || status === "voting") return "Active";
  if (status === "completed") return "Active";
  return "Idle";
};

const AgentsGrid = () => {
  const { data, isLoading, error } = useAgentsStatus();

  if (isLoading) {
    return (
      <div className="rounded-lg bg-card p-5 shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
          Agents
        </h2>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-card p-5 shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
          Agents
        </h2>
        <p className="text-sm text-destructive">Failed to load agents</p>
      </div>
    );
  }

  const agents = data?.agents || [];

  return (
    <div className="rounded-lg bg-card p-5 shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
        Agents ({data?.active_agents || 0} Active)
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <AgentCard
            key={agent.agent_id}
            name={agent.agent_name}
            status={mapStatus(agent.status)}
            color={agentColors[agent.agent_id] || "indigo"}
          />
        ))}
      </div>
    </div>
  );
};

export default AgentsGrid;
