import { useState } from "react";
import { SendHorizontal, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";

const ChatInput = () => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim()) {
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-center gap-2 pt-3 border-t border-border/50">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message..."
        rows={1}
        className="flex-1 rounded-lg bg-muted/50 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/30 transition-shadow resize-none max-h-32 overflow-y-auto"
      />
      <Button
        size="icon"
        variant="outline"
        className="shrink-0 h-9 w-9"
      >
        <Volume2 className="h-4 w-4" />
      </Button>
      <Button
        size="icon"
        onClick={handleSend}
        className="shrink-0 h-9 w-9"
      >
        <SendHorizontal className="h-4 w-4" />
      </Button>
    </div>
  );
};

export default ChatInput;
