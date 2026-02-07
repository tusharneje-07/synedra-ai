"""
Chat Service
===========

Handles chat messages and @mention parsing with database persistence.
"""

import re
import logging
import uuid
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from services.agent_status import agent_status_service
from models.chat_message import ChatMessage

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat message processing with database persistence."""
    
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
    
    def __init__(self, db: Optional[AsyncSession] = None):
        """
        Initialize chat service.
        
        Args:
            db: Optional database session for persistence
        """
        self.db = db
    
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
    
    async def create_message(
        self,
        content: str,
        project_id: int,
        session_id: Optional[str] = None,
        sender_type: str = "user",
        sender_name: str = "User",
        agent_id: Optional[str] = None,
        agent_role: Optional[str] = None,
        message_type: str = "chat"
    ) -> ChatMessage:
        """
        Create and save a chat message to database.
        
        Args:
            content: Message content
            project_id: Project ID
            session_id: Session ID (for council executions)
            sender_type: 'user', 'agent', or 'system'
            sender_name: Name of sender
            agent_id: Agent ID if sender is agent
            agent_role: Agent role if sender is agent
            message_type: 'chat', 'thinking', 'debate', 'decision', 'status'
        
        Returns:
            Created ChatMessage instance
        """
        # Generate unique message ID
        message_id = str(uuid.uuid4())
        
        # Parse mentions if it's a user message
        mentioned_agents = []
        if sender_type == "user":
            mentioned_agents, _ = self.parse_mentions(content)
        
        # Create message instance
        message = ChatMessage(
            message_id=message_id,
            project_id=project_id,
            session_id=session_id,
            content=content,
            sender_type=sender_type,
            sender_name=sender_name,
            agent_id=agent_id,
            agent_role=agent_role,
            message_type=message_type,
            mentioned_agents=mentioned_agents if mentioned_agents else None,
            is_agent_triggered=len(mentioned_agents) > 0
        )
        
        # Save to database if db session available
        if self.db:
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)
            
            logger.info(
                f"Chat message saved: {message_id}, "
                f"project={project_id}, session={session_id}, "
                f"sender={sender_type}/{sender_name}"
            )
        
        return message
    
    async def get_message_history(
        self,
        project_id: int,
        session_id: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        Get chat message history from database.
        
        Args:
            project_id: Project ID to filter by
            session_id: Optional session ID to filter by
            limit: Maximum number of messages to return
            skip: Number of messages to skip
        
        Returns:
            Dictionary with total count and messages
        """
        if not self.db:
            return {"total": 0, "messages": []}
        
        # Build query
        query = select(ChatMessage).where(ChatMessage.project_id == project_id)
        
        if session_id:
            query = query.where(ChatMessage.session_id == session_id)
        
        # Get total count
        count_query = select(ChatMessage).where(ChatMessage.project_id == project_id)
        if session_id:
            count_query = count_query.where(ChatMessage.session_id == session_id)
        
        result = await self.db.execute(count_query)
        total = len(result.scalars().all())
        
        # Get paginated messages (chronological order)
        query = query.order_by(ChatMessage.created_at.asc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        # Convert to dict
        message_list = [
            {
                "id": msg.message_id,
                "content": msg.content,
                "sender_type": msg.sender_type,
                "sender_name": msg.sender_name,
                "agent_id": msg.agent_id,
                "agent_role": msg.agent_role,
                "message_type": msg.message_type,
                "mentioned_agents": [
                    {"agent_id": aid, "agent_name": aid}
                    for aid in (msg.mentioned_agents or [])
                ] if msg.mentioned_agents else [],
                "is_agent_triggered": msg.is_agent_triggered,
                "timestamp": msg.created_at.isoformat(),
                "session_id": msg.session_id
            }
            for msg in messages
        ]
        
        return {
            "total": total,
            "messages": message_list
        }
    
    async def delete_all_messages(self, project_id: int) -> int:
        """
        Delete all chat messages for a project.
        
        Args:
            project_id: Project ID to delete messages for
        
        Returns:
            Number of messages deleted
        """
        if not self.db:
            return 0
        
        # Get all messages for the project
        query = select(ChatMessage).where(ChatMessage.project_id == project_id)
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        count = len(messages)
        
        # Delete all messages
        for message in messages:
            await self.db.delete(message)
        
        await self.db.commit()
        
        logger.info(f"Deleted {count} chat messages for project {project_id}")
        
        return count
    
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
