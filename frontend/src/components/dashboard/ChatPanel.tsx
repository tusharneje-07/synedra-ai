interface ChatMessage {
  agent: string;
  message: string;
}

const agentColors: Record<string, string> = {
  "Trend Analyst": "bg-[#EEF2FF] text-[#4F46E5]",
  "Risk Assessor": "bg-[#FFF7ED] text-[#D97706]",
  "Brand Strategist": "bg-[#FEF2F2] text-[#DC2626]",
  "Data Scientist": "bg-[#ECFDF5] text-[#0F766E]",
  "CMO Advisor": "bg-[#E6F0FF] text-[#002147]",
};

const messages: ChatMessage[] = [
  {
    agent: "Trend Analyst",
    message: "Trend data indicates a 23% surge in AI governance discussions across social platforms this quarter.",
  },
  {
    agent: "Risk Assessor",
    message: "Risk flag: regulatory compliance deadline approaching. Recommend reviewing content for GDPR alignment.",
  },
  {
    agent: "Brand Strategist",
    message: "Brand voice consistency check passed. Tone aligns with our established communication framework.",
  },
  {
    agent: "Data Scientist",
    message: "Data pipeline processed 1.2M records. Sentiment analysis complete — overall positive at 68%.",
  },
  {
    agent: "CMO Advisor",
    message: "Strategic recommendation: prioritize LinkedIn and industry publications for maximum B2B engagement.",
  },
  {
    agent: "Trend Analyst",
    message: "Follow-up: competitor analysis shows gap in sustainability messaging we can capitalize on.",
  },
  {
    agent: "Risk Assessor",
    message: "Low-risk window identified for campaign launch between March 15–22. Minimal conflicting events.",
  },
  {
    agent: "Brand Strategist",
    message: "Content audit complete. 94% of assets align with updated brand guidelines.",
  },
  {
    agent: "Data Scientist",
    message: "Engagement metrics show 2.4x improvement in click-through rates after tone adjustment.",
  },
  {
    agent: "CMO Advisor",
    message: "Budget reallocation recommended: shift 15% from paid social to organic content strategy.",
  },
];

const ChatPanel = () => {
  return (
    <div className="flex-1 overflow-y-auto pr-1 space-y-0.5">
      {messages.map((msg, i) => (
        <div
          key={i}
          className="py-2.5 px-1 border-b border-border/50 last:border-b-0"
        >
          <div className="flex items-start gap-2">
            <span className={`text-xs font-semibold px-2.5 py-1 rounded-full whitespace-nowrap shrink-0 ${agentColors[msg.agent] || "bg-slate-200 text-slate-700"}`}>
              {msg.agent}
            </span>
            <p className="text-sm text-muted-foreground leading-relaxed pt-0.5">
              {msg.message}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChatPanel;
