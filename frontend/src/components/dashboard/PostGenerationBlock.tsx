import { useState, useEffect, useRef, useMemo } from "react";
import { Loader2, PlayCircle, Brain, Sparkles } from "lucide-react";
import { useWebSocket } from "@/hooks/useWebSocket";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { useSendChatMessage } from "@/hooks/useAPI";
import { useToast } from "@/hooks/use-toast";

interface PostGenerationBlockProps {
  projectId: number;
  projectName: string;
  postTopic?: string;
}

const PostGenerationBlock = ({ projectId, projectName, postTopic }: PostGenerationBlockProps) => {
  const [content, setContent] = useState(
    `# ${postTopic || 'Marketing Post'}

*Waiting for council decision...*

Once the AI council analyzes your project and reaches consensus, the generated post will appear here in Markdown format.

**To generate content:**
1. Click the "Start Council Debate" button below
2. Or use the chat to ask agents questions (e.g., "@all Create a marketing post for this campaign")
3. Agents will debate and reach consensus
4. The final decision will update here automatically`
  );
  
  const [phase, setPhase] = useState<'idle' | 'debating' | 'thinking' | 'complete'>('idle');
  const thinkingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const processingDecisionRef = useRef(false);
  const lastDecisionIdRef = useRef<string | null>(null);
  
  const { messages: wsMessages } = useWebSocket();
  const sendMessageMutation = useSendChatMessage();
  const { toast } = useToast();

  // Memoize derived values to prevent unnecessary recalculations
  const councilState = useMemo(() => {
    const hasCouncilStart = wsMessages.some(msg => msg.type === 'council_start');
    const hasCouncilEnd = wsMessages.some(msg => msg.type === 'council_end');
    const decisionMessages = wsMessages.filter(msg => msg.type === 'decision');
    const latestDecision = decisionMessages.length > 0 ? decisionMessages[decisionMessages.length - 1] : null;
    const decisionId = latestDecision && 'timestamp' in latestDecision ? String(latestDecision.timestamp) : null;
    
    return {
      hasCouncilStart,
      hasCouncilEnd,
      latestDecision,
      decisionId
    };
  }, [wsMessages.length]); // Only recalculate when message count changes

  // Simplified state machine - just track the most recent decision
  useEffect(() => {
    const { hasCouncilStart, hasCouncilEnd, latestDecision, decisionId } = councilState;
    
    // Skip if we've already processed this decision
    if (decisionId && lastDecisionIdRef.current === decisionId) {
      return;
    }
    
    // Phase 1: Council starts - reset everything
    if (hasCouncilStart && (phase === 'idle' || phase === 'complete')) {
      if (thinkingTimerRef.current) {
        clearTimeout(thinkingTimerRef.current);
        thinkingTimerRef.current = null;
      }
      processingDecisionRef.current = false;
      lastDecisionIdRef.current = null;
      setPhase('debating');
      return;
    }

    // Phase 2: Decision arrives - show thinking animation then complete
    if (latestDecision && phase === 'debating' && !processingDecisionRef.current) {
      const decisionContent = 'decision' in latestDecision ? latestDecision.decision : '';
      
      processingDecisionRef.current = true;
      lastDecisionIdRef.current = decisionId;
      setPhase('thinking');
      
      // Show thinking animation for 1.5 seconds then complete
      thinkingTimerRef.current = setTimeout(() => {
        setContent(decisionContent);
        setPhase('complete');
        thinkingTimerRef.current = null;
      }, 1500);
      return;
    }

    // Phase 3: If council ends without decision (error case), reset
    if (hasCouncilEnd && !latestDecision && phase === 'debating') {
      setContent('# Error\n\nCouncil session ended without generating content. Please try again.');
      setPhase('idle');
      processingDecisionRef.current = false;
      lastDecisionIdRef.current = null;
      return;
    }
  }, [councilState, phase]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (thinkingTimerRef.current) {
        clearTimeout(thinkingTimerRef.current);
      }
    };
  }, []);

  const handleStartCouncil = async () => {
    try {
      // Reset to beginning
      setPhase('idle');
      
      await sendMessageMutation.mutateAsync({
        content: "@all Create a comprehensive marketing campaign strategy for this project",
        project_id: projectId,
        user_name: "User",
      });
      toast({
        title: "Council Started",
        description: "AI agents are now debating to create your marketing strategy...",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start council. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="rounded-lg  bg-card p-5 flex flex-col flex-1 min-h-0 shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">
          Post Generation
        </h2>
        <div className="flex items-center gap-3">
          {phase === 'idle' && (
            <Button
              onClick={handleStartCouncil}
              disabled={sendMessageMutation.isPending}
              size="sm"
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
            >
              <PlayCircle className="h-4 w-4 mr-2" />
              {sendMessageMutation.isPending ? "Starting..." : "Start Council Debate"}
            </Button>
          )}
          {phase === 'complete' && (
            <Button
              onClick={handleStartCouncil}
              disabled={sendMessageMutation.isPending}
              size="sm"
              variant="outline"
              className="border-purple-600 text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-950/20"
            >
              <PlayCircle className="h-4 w-4 mr-2" />
              Regenerate
            </Button>
          )}
          <span className="text-xs text-muted-foreground">
            {projectName}
          </span>
        </div>
      </div>

      <div className="w-full h-px bg-border/60 mb-4" />

      {/* Deliberating message - only show during active debate */}
      {phase === 'debating' && (
        <div className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 mb-3 bg-blue-50 dark:bg-blue-950/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800">
          <Loader2 className="h-4 w-4 animate-spin flex-shrink-0" />
          <span className="font-medium">Council is deliberating and debating...</span>
        </div>
      )}

      {/* Thinking/Processing animation - show after debate ends */}
      {phase === 'thinking' && (
        <div className="hidden flex-col items-center justify-center gap-4 mb-3 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20 p-6 rounded-lg border border-purple-200 dark:border-purple-800">
          <div className="relative">
            <Brain className="h-8 w-8 text-purple-600 dark:text-purple-400 animate-pulse" />
            <Sparkles className="h-4 w-4 text-blue-500 absolute -top-1 -right-1 animate-bounce" />
          </div>
          <div className="text-center">
            <p className="text-sm font-semibold text-purple-700 dark:text-purple-300 mb-1">
              Synthesizing Final Strategy...
            </p>
            <p className="text-xs text-muted-foreground">
              Processing council decisions and creating comprehensive campaign plan
            </p>
          </div>
          <div className="flex gap-1">
            <div className="h-2 w-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="h-2 w-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="h-2 w-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
      )}

      <div className="flex-1 min-h-0 max-h-[60vh] overflow-y-scroll">
        <div className="h-full overflow-y-scroll pr-2 custom-scrollbar">
          <div className="prose prose-sm dark:prose-invert max-w-none p-4 bg-muted/30 rounded-lg">
            {phase === 'complete' || content.includes('#') ? (
              <ReactMarkdown
                components={{
                  h1: ({node, ...props}) => <h1 className="text-2xl font-bold mb-4 text-foreground border-b pb-2" {...props} />,
                  h2: ({node, ...props}) => <h2 className="text-xl font-semibold mb-3 mt-6 text-foreground" {...props} />,
                  h3: ({node, ...props}) => <h3 className="text-lg font-semibold mb-2 mt-4 text-foreground" {...props} />,
                  p: ({node, ...props}) => <p className="mb-3 leading-relaxed text-foreground/90" {...props} />,
                  ul: ({node, ...props}) => <ul className="mb-4 ml-6 list-disc space-y-2" {...props} />,
                  ol: ({node, ...props}) => <ol className="mb-4 ml-6 list-decimal space-y-2" {...props} />,
                  li: ({node, ...props}) => <li className="text-foreground/90" {...props} />,
                  strong: ({node, ...props}) => <strong className="font-bold text-foreground" {...props} />,
                  em: ({node, ...props}) => <em className="italic text-foreground/80" {...props} />,
                  code: ({node, ...props}) => <code className="bg-muted px-1 py-0.5 rounded text-sm font-mono" {...props} />,
                  pre: ({node, ...props}) => <pre className="bg-muted p-3 rounded-lg overflow-x-auto mb-4" {...props} />,
                  blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-primary pl-4 italic my-4" {...props} />,
                }}
              >
                {content}
              </ReactMarkdown>
            ) : (
              <div className="whitespace-pre-wrap text-foreground/90">{content}</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostGenerationBlock;
