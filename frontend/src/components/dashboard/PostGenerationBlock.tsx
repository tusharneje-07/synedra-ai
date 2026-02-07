import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { RotateCcw, MessageSquare, Send, Loader2 } from "lucide-react";
import { useExecuteCouncil, useCouncilStatus } from "@/hooks/useAPI";
import { useToast } from "@/hooks/use-toast";

const sampleContent = `The latest trend analysis reveals a significant shift in consumer sentiment toward sustainable AI practices. Our brand positioning should leverage this momentum by highlighting our commitment to ethical AI development.

Key findings from the data pipeline:
• 73% increase in sustainability-related searches
• Brand sentiment score improved by 12 points
• Risk assessment flags potential regulatory changes in Q3
• Recommended pivot: emphasize transparency in AI decision-making

The CMO advisory suggests a phased rollout strategy, beginning with thought leadership content before transitioning to product-specific messaging. This approach minimizes brand risk while maximizing engagement potential across target demographics.`;

const PostGenerationBlock = () => {
  const [content, setContent] = useState(sampleContent);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const { toast } = useToast();
  
  const executeCouncil = useExecuteCouncil();
  const { data: councilStatus } = useCouncilStatus();
  
  const isExecuting = councilStatus?.is_active || executeCouncil.isPending;

  // Update content when council execution completes
  useEffect(() => {
    if (executeCouncil.isSuccess && executeCouncil.data?.decision) {
      setContent(executeCouncil.data.decision);
      setIsRegenerating(false);
      toast({
        title: "Council Decision Complete",
        description: `Decision reached with ${executeCouncil.data.confidence}% confidence.`,
      });
    }
  }, [executeCouncil.isSuccess, executeCouncil.data, toast]);

  const handleSendToDebate = () => {
    if (!content.trim()) {
      toast({
        title: "No content",
        description: "Please enter some content to send to the council.",
        variant: "destructive",
      });
      return;
    }

    setIsRegenerating(false);
    executeCouncil.mutate({
      prompt: content,
    });
  };

  const handleRegenerate = () => {
    if (isExecuting) return;
    
    setIsRegenerating(true);
    executeCouncil.mutate({
      prompt: "Generate a new marketing post based on current trends and brand guidelines.",
    });
  };

  return (
    <div className="rounded-lg bg-card p-5 flex flex-col flex-1 min-h-0 shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">
          Post Generation
        </h2>
        <span className="text-xs text-muted-foreground">Draft v1.2</span>
      </div>

      <div className="w-full h-px bg-border/60 mb-4" />

      <div className="flex-1 min-h-0 mb-4">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          disabled={isExecuting}
          className="w-full h-full min-h-[200px] resize-none rounded-lg bg-muted/50 p-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/30 transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
          placeholder="Generated post content will appear here..."
        />
      </div>

      {isExecuting && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Council is deliberating...</span>
        </div>
      )}

      <div className="flex items-center gap-2 mt-3">
        <Button 
          variant="ghost" 
          size="sm" 
          className="text-muted-foreground"
          onClick={handleRegenerate}
          disabled={isExecuting}
        >
          {isExecuting && isRegenerating ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <RotateCcw className="h-3.5 w-3.5" />
          )}
          Regenerate
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          onClick={handleSendToDebate}
          disabled={isExecuting}
        >
          {isExecuting && !isRegenerating ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <MessageSquare className="h-3.5 w-3.5" />
          )}
          Send to Debate
        </Button>
        <Button size="sm" className="ml-auto" disabled={isExecuting}>
          <Send className="h-3.5 w-3.5" />
          Publish
        </Button>
      </div>
    </div>
  );
};

export default PostGenerationBlock;
