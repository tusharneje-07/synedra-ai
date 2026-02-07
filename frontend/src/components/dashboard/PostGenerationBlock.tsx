import { useState } from "react";
import { Button } from "@/components/ui/button";
import { RotateCcw, MessageSquare, Send } from "lucide-react";

const sampleContent = `The latest trend analysis reveals a significant shift in consumer sentiment toward sustainable AI practices. Our brand positioning should leverage this momentum by highlighting our commitment to ethical AI development.

Key findings from the data pipeline:
• 73% increase in sustainability-related searches
• Brand sentiment score improved by 12 points
• Risk assessment flags potential regulatory changes in Q3
• Recommended pivot: emphasize transparency in AI decision-making

The CMO advisory suggests a phased rollout strategy, beginning with thought leadership content before transitioning to product-specific messaging. This approach minimizes brand risk while maximizing engagement potential across target demographics.`;

const PostGenerationBlock = () => {
  const [content, setContent] = useState(sampleContent);

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
          className="w-full h-full min-h-[200px] resize-none rounded-lg bg-muted/50 p-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/30 transition-shadow"
          placeholder="Generated post content will appear here..."
        />
      </div>

      <div className="flex items-center gap-2 mt-3">
        <Button variant="ghost" size="sm" className="text-muted-foreground">
          <RotateCcw className="h-3.5 w-3.5" />
          Regenerate
        </Button>
        <Button variant="outline" size="sm">
          <MessageSquare className="h-3.5 w-3.5" />
          Send to Debate
        </Button>
        <Button size="sm" className="ml-auto">
          <Send className="h-3.5 w-3.5" />
          Publish
        </Button>
      </div>
    </div>
  );
};

export default PostGenerationBlock;
