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
    bg: "bg-[#EEF2FF] dark:bg-[rgba(79,70,229,0.09)]",
    text: "text-[#4F46E5] dark:text-[#A5B4FC]",
    border: "border border-transparent dark:border-[rgba(79,70,229,0.22)]",
    idleBadge: "bg-[#DDD6FE] text-[#4F46E5] dark:bg-[rgba(79,70,229,0.15)] dark:text-[#A5B4FC]",
  },
  amber: {
    bg: "bg-[#FFF7ED] dark:bg-[rgba(245,158,11,0.09)]",
    text: "text-[#D97706] dark:text-[#FCD34D]",
    border: "border border-transparent dark:border-[rgba(245,158,11,0.22)]",
    idleBadge: "bg-[#FED7AA] text-[#D97706] dark:bg-[rgba(245,158,11,0.15)] dark:text-[#FCD34D]",
  },
  purple: {
    bg: "bg-[#FEF2F2] dark:bg-[rgba(220,38,38,0.09)]",
    text: "text-[#DC2626] dark:text-[#FCA5A5]",
    border: "border border-transparent dark:border-[rgba(220,38,38,0.22)]",
    idleBadge: "bg-[#FECACA] text-[#DC2626] dark:bg-[rgba(220,38,38,0.15)] dark:text-[#FCA5A5]",
  },
  teal: {
    bg: "bg-[#F0FDF4] dark:bg-[rgba(22,163,74,0.09)]",
    text: "text-[#16A34A] dark:text-[#86EFAC] ",
    border: "border border-transparent dark:border-[rgba(22,163,74,0.22)]",
    idleBadge: "bg-[#BBF7D0] text-[#16A34A] dark:bg-[rgba(22,163,74,0.15)] dark:text-[#86EFAC]",
  },
  blue: {
    bg: "bg-[#E6F0FF] dark:bg-[rgba(37,99,235,0.09)]",
    text: "text-[#002147] dark:text-[#93C5FD]",
    border: "border border-transparent dark:border-[rgba(37,99,235,0.22)]",
    idleBadge: "bg-[#BFDBFE] text-[#002147] dark:bg-[rgba(37,99,235,0.15)] dark:text-[#93C5FD]",
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
  const isIdle = status === "Idle";
  
  return (
    <div
      className={cn(
        "rounded-lg px-2 py-3 flex justify-center transition-all duration-200",
        "hover:-translate-y-[2px]",
        "shadow-[0_1px_3px_rgba(0,0,0,0.05)] hover:shadow-[0_4px_16px_rgba(0,0,0,0.12)] dark:hover:shadow-[0_4px_16px_rgba(0,0,0,0.3)]",
        styles.bg,
        isIdle ? "" : styles.border
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
          <span className={cn(
            "text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-medium whitespace-nowrap",
            styles.idleBadge
          )}>
            IDLE
          </span>
        )}
      </div>
    </div>
  );
};

export default AgentCard;
