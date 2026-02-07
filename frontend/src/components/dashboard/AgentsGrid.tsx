import AgentCard, { type AgentStatus, type AgentColor } from "./AgentCard";

interface Agent {
  name: string;
  status: AgentStatus;
  color: AgentColor;
}

const agents: Agent[] = [
  { name: "Trend Analyst", status: "Active", color: "indigo" },
  { name: "Risk Assessor", status: "Active", color: "amber" },
  { name: "Brand Strategist", status: "Active", color: "purple" },
  { name: "Data Scientist", status: "Idle", color: "teal" },
  { name: "CMO Advisor", status: "Active", color: "blue" },
];

const AgentsGrid = () => {
  return (
    <div className="rounded-lg bg-card p-5 shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
        Agents
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <AgentCard key={agent.name} {...agent} />
        ))}
      </div>
    </div>
  );
};

export default AgentsGrid;
