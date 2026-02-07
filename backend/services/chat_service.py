"""
Chat Service
===========

Handles chat messages and @mention parsing.
"""

import re
import logging
from typing import List, Tuple, Dict, Any
from datetime import datetime

from services.agent_status import agent_status_service

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat message processing."""
    
    # Agent mention patterns
    AGENT_ALIASES = {
        "trend": ["@trend", "@trendanalyst", "@trends"],
        "engagement": ["@engagement", "@engage", "@engagementexpert"],
        "brand": ["@brand", "@brandstrategist", "@branding"],
        "risk": ["@risk", "@riskassessor", "@risks"],
        "compliance": ["@compliance", "@complianceofficer", "@legal"],
        "arbitrator": ["@arbitrator", "@cmo", "@arbitrate"],
        "all": ["@all", "@everyone", "@council"]
    }
    
    def __init__(self):
        self.message_history: List[Dict[str, Any]] = []
        self.message_counter = 0
    
    def parse_mentions(self, content: str) -> Tuple[List[str], str]:
        """
        Parse @mentions from message content.
        
        Args:
            content: Message text with potential @mentions
        
        Returns:
            Tuple of (list of agent_ids, cleaned content)
        
        Example:
            "@trend @brand What's the best strategy?" 
            -> (["trend", "brand"], "What's the best strategy?")
        """
        mentioned_agents = set()
        
        # Find all @mentions
        words = content.split()
        for word in words:
            mention = word.lower().strip(".,!?;:")
            
            # Check against aliases
            for agent_id, aliases in self.AGENT_ALIASES.items():
                if mention in aliases:
                    if agent_id == "all":
                        # @all mentions all agents
                        mentioned_agents.update(
                            list(agent_status_service.AGENTS.keys())
                        )
                    else:
                        mentioned_agents.add(agent_id)
                    break
        
        return list(mentioned_agents), content
    
    def create_message(
        self,
        content: str,
        user_name: str = "User"
    ) -> Dict[str, Any]:
        """
        Create a chat message.
        
        Args:
            content: Message content
            user_name: User's name
        
        Returns:
            Message dictionary
        """
        self.message_counter += 1
        message_id = f"msg_{self.message_counter}_{datetime.utcnow().timestamp()}"
        
        # Parse mentions
        mentioned_agents, cleaned_content = self.parse_mentions(content)
        
        # Create message
        message = {
            "id": message_id,
            "content": content,
            "user_name": user_name,
            "timestamp": datetime.utcnow().isoformat(),
            "mentioned_agents": [
                {
                    "agent_id": agent_id,
                    "agent_name": agent_status_service.AGENTS[agent_id]["name"]
                }
                for agent_id in mentioned_agents
                if agent_id in agent_status_service.AGENTS
            ],
            "is_agent_triggered": len(mentioned_agents) > 0,
            "session_id": None
        }
        
        # Add to history
        self.message_history.append(message)
        
        # Keep only last 100 messages
        if len(self.message_history) > 100:
            self.message_history.pop(0)
        
        logger.info(f"Chat message created: {message_id}, mentions: {mentioned_agents}")
        
        return message
    
    def get_message_history(
        self,
        limit: int = 50,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        Get chat message history.
        
        Args:
            limit: Maximum number of messages to return
            skip: Number of messages to skip
        
        Returns:
            Dictionary with total count and messages
        """
        total = len(self.message_history)
        
        # Get paginated messages (newest first)
        messages = list(reversed(self.message_history))
        paginated = messages[skip:skip + limit]
        
        return {
            "total": total,
            "messages": paginated
        }
    
    def get_prompt_for_agents(
        self,
        content: str,
        mentioned_agents: List[str]
    ) -> str:
        """
        Create a prompt for the mentioned agents.
        
        Args:
            content: Original message content
            mentioned_agents: List of agent IDs
        
        Returns:
            Formatted prompt
        """
        # Remove @mentions from content
        clean_content = content
        for agent_id, aliases in self.AGENT_ALIASES.items():
            for alias in aliases:
                clean_content = clean_content.replace(alias, "").strip()
        
        # Clean up multiple spaces
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Add context about which agents were mentioned
        if len(mentioned_agents) == 1:
            agent_name = agent_status_service.AGENTS[mentioned_agents[0]]["name"]
            prompt = f"[Direct question for {agent_name}]\n\n{clean_content}"
        else:
            agent_names = [
                agent_status_service.AGENTS[aid]["name"]
                for aid in mentioned_agents
                if aid in agent_status_service.AGENTS
            ]
            prompt = f"[Question for: {', '.join(agent_names)}]\n\n{clean_content}"
        
        return prompt


# Global service instance
chat_service = ChatService()
