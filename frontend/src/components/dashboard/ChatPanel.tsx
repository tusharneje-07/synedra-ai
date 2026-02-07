import { useEffect, useRef } from "react";
import { useChatHistory } from "@/hooks/useAPI";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Loader2 } from "lucide-react";

const agentColors: Record<string, string> = {
  "Trend Analyst": "bg-[#EEF2FF] text-[#4F46E5] dark:bg-[rgba(79,70,229,0.09)] dark:text-[#A5B4FC] border border-transparent dark:border-[rgba(79,70,229,0.22)]",
  "Risk Assessor": "bg-[#FFF7ED] text-[#D97706] dark:bg-[rgba(245,158,11,0.09)] dark:text-[#FCD34D] border border-transparent dark:border-[rgba(245,158,11,0.22)]",
  "Brand Strategist": "bg-[#FEF2F2] text-[#DC2626] dark:bg-[rgba(220,38,38,0.09)] dark:text-[#FCA5A5] border border-transparent dark:border-[rgba(220,38,38,0.22)]",
  "Data Scientist": "bg-[#F0FDF4] text-[#16A34A] dark:bg-[rgba(22,163,74,0.09)] dark:text-[#86EFAC] border border-transparent dark:border-[rgba(22,163,74,0.22)]",
  "CMO Advisor": "bg-[#E6F0FF] text-[#002147] dark:bg-[rgba(37,99,235,0.09)] dark:text-[#93C5FD] border border-transparent dark:border-[rgba(37,99,235,0.22)]",
};

const messages: ChatMessage[] = [
  {
    agent: "Trend Analyst",
    message: "Trend data indicates a 23% surge in AI governance discussions across social platforms this quarter.",
  },
  {
    agent: "User",
    message: "Can you analyze the competitive landscape?",
    isUser: true,
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
    agent: "User",
    message: "What about the engagement metrics?",
    isUser: true,
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
  const { data, isLoading } = useChatHistory(50, 0);
  const { messages: wsMessages } = useWebSocket();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [data, wsMessages]);

  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto pr-1 flex items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const chatMessages = data?.messages || [];
  
  // Combine chat history with WebSocket messages
  const allMessages = [
    ...chatMessages.map(msg => ({
      id: msg.id,
      agent: msg.user_name,
      message: msg.content,
      isUser: true,
      timestamp: msg.timestamp,
    })),
    ...wsMessages
      .filter(msg => 
        msg.type === 'agent_thinking' || 
        msg.type === 'debate' || 
        msg.type === 'system'
      )
      .map((msg, idx) => ({
        id: `ws-${idx}`,
        agent: 'agent_name' in msg ? msg.agent_name : 'System',
        message: 
          msg.type === 'agent_thinking' ? msg.content :
          msg.type === 'debate' ? msg.position :
          msg.type === 'system' ? msg.message : '',
        isUser: false,
        timestamp: msg.timestamp,
      })),
  ].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto pr-1 space-y-2">
      {allMessages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
          No messages yet. Start a conversation!
        </div>
      ) : (
        allMessages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`${msg.isUser ? 'max-w-[70%]' : 'max-w-[70%]'}`}>
              <p className="text-sm leading-loose">
                {msg.isUser ? (
                  <span className="inline-block bg-[#DCF8C6] dark:bg-[#056162] px-4 py-2 rounded-lg">
                    <span className="font-semibold text-[#075E54] dark:text-[#E9EDEF]">You: </span>
                    <span className="text-[#303030] dark:text-[#E9EDEF]">{msg.message}</span>
                  </span>
                ) : (
                  <>
                    <span className={`font-semibold px-3 py-1 rounded-full ${agentColors[msg.agent] || "bg-slate-200 text-slate-700"}`}>
                      {msg.agent}
                    </span>
                    <span className="text-muted-foreground"> {msg.message}</span>
                  </>
                )}
              </p>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default ChatPanel;
