import { useEffect, useLayoutEffect, useRef, useMemo } from "react";
import { useChatHistory, useClearChats } from "@/hooks/useAPI";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Loader2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

interface ChatPanelProps {
  projectId: number;
}

const agentColors: Record<string, string> = {
  "Trend Analyst": "bg-[#EEF2FF] text-[#4F46E5] dark:bg-[rgba(79,70,229,0.09)] dark:text-[#A5B4FC] border border-transparent dark:border-[rgba(79,70,229,0.22)]",
  "Risk Assessor": "bg-[#FFF7ED] text-[#D97706] dark:bg-[rgba(245,158,11,0.09)] dark:text-[#FCD34D] border border-transparent dark:border-[rgba(245,158,11,0.22)]",
  "Brand Strategist": "bg-[#FEF2F2] text-[#DC2626] dark:bg-[rgba(220,38,38,0.09)] dark:text-[#FCA5A5] border border-transparent dark:border-[rgba(220,38,38,0.22)]",
  "Data Scientist": "bg-[#F0FDF4] text-[#16A34A] dark:bg-[rgba(22,163,74,0.09)] dark:text-[#86EFAC] border border-transparent dark:border-[rgba(22,163,74,0.22)]",
  "CMO Advisor": "bg-[#E6F0FF] text-[#002147] dark:bg-[rgba(37,99,235,0.09)] dark:text-[#93C5FD] border border-transparent dark:border-[rgba(37,99,235,0.22)]",
};

const ChatPanel = ({ projectId }: ChatPanelProps) => {
  const { data, isLoading, isFetching } = useChatHistory(projectId);
  const { messages: wsMessages } = useWebSocket();
  const clearChatsMutation = useClearChats();
  const scrollRef = useRef<HTMLDivElement>(null);
  const prevMessageCountRef = useRef(0);
  const isInitialLoadRef = useRef(true);

  const handleClearChats = async () => {
    try {
      await clearChatsMutation.mutateAsync(projectId);
    } catch (error) {
      console.error("Failed to clear chats:", error);
    }
  };

  const chatMessages = data?.messages || [];

  // Show initial loading only on first load, not on refetches
  const showInitialLoading = isLoading && chatMessages.length === 0;
  
  // Scroll to bottom helper
  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    if (scrollRef.current) {
      const scrollElement = scrollRef.current;
      // Use setTimeout to ensure DOM has updated
      setTimeout(() => {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }, 0);
    }
  };
  // Memoize message processing to avoid recalculating on every render
  const allMessages = useMemo(() => [
    // Messages from database (both user and agent messages)
    ...chatMessages.map(msg => ({
      id: msg.id,
      agent: msg.sender_name || (msg.sender_type === 'user' ? 'You' : msg.agent_role || 'Agent'),
      message: msg.content,
      isUser: msg.sender_type === 'user',
      timestamp: msg.timestamp,
      messageType: msg.message_type,
    })),
    // Real-time WebSocket messages (not yet in database)
    ...wsMessages
      .filter(msg => {
        // Filter out heartbeat/pong messages
        if (msg.type === 'system' && 
            (msg.message?.toLowerCase().includes('pong') || 
             msg.message?.toLowerCase().includes('connected to ai council'))) {
          return false;
        }
        // Only show agent messages, user messages, and important system messages
        return msg.type === 'agent_thinking' || 
               msg.type === 'debate' || 
               msg.type === 'decision' ||
               msg.type === 'council_start' ||
               msg.type === 'council_end' ||
               msg.type === 'user_message';
      })
      .map((msg, idx) => ({
        id: `ws-${idx}`,
        agent: 
          msg.type === 'user_message' ? msg.sender_name :
          'agent_name' in msg ? msg.agent_name : 'Council',
        message: 
          msg.type === 'user_message' ? msg.content :
          msg.type === 'agent_thinking' ? msg.content :
          msg.type === 'debate' ? msg.position :
          msg.type === 'decision' ? msg.decision :
          msg.type === 'council_start' ? `Council session started: ${msg.topic}` :
          msg.type === 'council_end' ? `Council session ended: ${msg.outcome}` :
          msg.type === 'system' ? msg.message : '',
        isUser: msg.type === 'user_message',
        timestamp: msg.timestamp,
        messageType: msg.type,
      })),
  ].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()), [chatMessages, wsMessages]);

  // Auto-scroll using useLayoutEffect for immediate DOM updates
  useLayoutEffect(() => {
    const currentMessageCount = allMessages.length;
    
    if (currentMessageCount > 0) {
      // On initial load, scroll immediately
      if (isInitialLoadRef.current) {
        scrollToBottom();
        isInitialLoadRef.current = false;
      } 
      // When new messages arrive
      else if (currentMessageCount > prevMessageCountRef.current) {
        scrollToBottom();
      }
      
      prevMessageCountRef.current = currentMessageCount;
    }
  }, [allMessages]);

  // Additional effect to ensure scroll after data loads
  useEffect(() => {
    if (!isLoading && allMessages.length > 0 && isInitialLoadRef.current) {
      scrollToBottom();
      isInitialLoadRef.current = false;
    }
  }, [isLoading, allMessages.length]);

  // Reset on project change
  useEffect(() => {
    isInitialLoadRef.current = true;
    prevMessageCountRef.current = 0;
  }, [projectId]);

  if (showInitialLoading) {
    return (
      <div className="flex-1 overflow-y-auto pr-1 flex items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Clear Chats Button */}
      {allMessages.length > 0 && (
        <div className="flex justify-end pb-2">
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="text-destructive hover:text-destructive hover:bg-destructive/10"
                disabled={clearChatsMutation.isPending}
              >
                {clearChatsMutation.isPending ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4 mr-2" />
                )}
                Clear Chats
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete all chat messages for this project.
                  This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleClearChats}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  Delete All
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      )}

      <div ref={scrollRef} className="flex-1 overflow-y-auto overflow-x-hidden pr-1 space-y-2 custom-scrollbar">
      {allMessages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
          No messages yet. Start a conversation!
        </div>
      ) : (
        allMessages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'} w-full`}
          >
            <div className={`${msg.isUser ? 'max-w-[85%]' : 'max-w-[85%]'} break-words`}>
              <p className="text-sm leading-relaxed break-words">
                {msg.isUser ? (
                  <span className="inline-block bg-[#DCF8C6] dark:bg-[#056162] px-4 py-2 rounded-lg break-words overflow-wrap-anywhere">
                    <span className="font-semibold text-[#075E54] dark:text-[#E9EDEF]">You: </span>
                    <span className="text-[#303030] dark:text-[#E9EDEF] break-words">{msg.message}</span>
                  </span>
                ) : (
                  <div className="flex flex-col gap-1">
                    <span className={`font-semibold px-3 py-1 rounded-full inline-block w-fit ${agentColors[msg.agent] || "bg-slate-200 text-slate-700"}`}>
                      {msg.agent}
                    </span>
                    <span className="text-muted-foreground break-words whitespace-pre-wrap">{msg.message}</span>
                  </div>
                )}
              </p>
            </div>
          </div>
        ))
      )}
    </div>
    </div>
  );
};

export default ChatPanel;
