import AgentsGrid from "@/components/dashboard/AgentsGrid";
import PostGenerationBlock from "@/components/dashboard/PostGenerationBlock";
import ChatPanel from "@/components/dashboard/ChatPanel";
import ChatInput from "@/components/dashboard/ChatInput";
import ThemeToggle from "@/components/dashboard/ThemeToggle";

const Index = () => {
  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-3 bg-card shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
        <div className="flex items-center gap-3">
          <h1 className="text-base font-bold tracking-tight text-foreground">
            AI Multi-Agent Dashboard
          </h1>
          <span className="text-[10px] uppercase tracking-widest text-muted-foreground bg-muted rounded-full px-2.5 py-0.5 font-medium">
            WebLLM Blocks
          </span>
        </div>
        <ThemeToggle />
      </header>

      {/* Main Content */}
      <div className="flex flex-1 min-h-0">
        {/* Left Column – 50% */}
        <div className="flex flex-col w-1/2 p-5 gap-5 min-h-0">
          <div className="flex-[0_0_auto]">
            <AgentsGrid />
          </div>
          <div className="flex-1 min-h-0">
            <PostGenerationBlock />
          </div>
        </div>

        {/* Right Column – Chat – 50% */}
        <div className="flex flex-col w-1/2 p-5 pl-0 min-h-0">
          <div className="flex flex-col flex-1 min-h-0 rounded-lg bg-card shadow-[0_1px_3px_rgba(0,0,0,0.05)] p-5">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
              Agent Activity
            </h2>
            <div className="w-full h-px bg-border/60 mb-3" />
            <ChatPanel />
            <ChatInput />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
