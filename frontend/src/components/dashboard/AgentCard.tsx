import { cn } from "@/lib/utils";

export type AgentStatus = "Active" | "Idle";
export type AgentColor = "indigo" | "amber" | "purple" | "teal" | "blue";

interface AgentCardProps {
  name: string;
  status: AgentStatus;
  color: AgentColor;
}

const colorStyles = {
  indigo: {
    bg: "bg-[#EEF2FF]",
    text: "text-[#4F46E5]",
  },
  amber: {
    bg: "bg-[#FFF7ED]",
    text: "text-[#D97706]",
  },
  purple: {
    bg: "bg-[#FEF2F2]",
    text: "text-[#DC2626]",
  },
  teal: {
    bg: "bg-[#ECFDF5]",
    text: "text-[#0F766E]",
  },
  blue: {
    bg: "bg-[#E6F0FF]",
    text: "text-[#002147]",
  },
};

const TypingIndicator = () => (
  <span className="inline-flex items-center gap-0.5 ml-2">
    <span className="thinking-dot h-1 w-1 rounded-full bg-slate-400 dark:bg-slate-500" />
    <span className="thinking-dot h-1 w-1 rounded-full bg-slate-400 dark:bg-slate-500" />
    <span className="thinking-dot h-1 w-1 rounded-full bg-slate-400 dark:bg-slate-500" />
  </span>
);

const AgentCard = ({ name, status, color }: AgentCardProps) => {
  const styles = colorStyles[color];
  
  return (
    <div
      className={cn(
        "rounded-lg px-2 py-3 flex justify-center transition-all duration-200 hover:-translate-y-0.5",
        "shadow-[0_1px_3px_rgba(0,0,0,0.05)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)]",
        styles.bg
      )}
    >
      <div className="flex items-center gap-4">
        <div className="min-w-0 flex items-center justify-between gap-3">
          <span className={cn(
            "text-xs font-semibold",
            styles.text
          )}>
            {name}
          </span>
          {status === "Active" && <TypingIndicator />}
        </div>
        {status === "Idle" && (
          <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-medium whitespace-nowrap bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
            IDLE
          </span>
        )}
      </div>
    </div>
  );
};

export default AgentCard;
