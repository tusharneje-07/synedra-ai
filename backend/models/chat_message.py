"""
Chat Message Database Model
===========================

Stores all chat messages for persistence across sessions.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class ChatMessage(Base):
    """
    Chat Message Table
    
    Stores all chat messages including user messages and agent responses.
    Links messages to projects and sessions for context preservation.
    """
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Message Identity
    message_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Context Links
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    session_id = Column(String(255), ForeignKey("project_sessions.session_id"), nullable=True, index=True)
    
    # Message Content
    content = Column(Text, nullable=False)
    sender_type = Column(
        String(50), 
        nullable=False,
        comment="user, agent, system"
    )
    sender_name = Column(String(255), nullable=True, comment="User name or agent ID")
    
    # Agent-specific data
    agent_id = Column(String(50), nullable=True, comment="ID if sender is an agent")
    agent_role = Column(String(255), nullable=True, comment="Agent's role description")
    
    # Message Metadata
    message_type = Column(
        String(50),
        nullable=True,
        comment="thinking, status, debate, decision, chat"
    )
    mentioned_agents = Column(JSON, nullable=True, comment="List of @mentioned agents")
    is_agent_triggered = Column(Integer, default=0, comment="1 if triggered specific agents")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "content": self.content,
            "sender_type": self.sender_type,
            "sender_name": self.sender_name,
            "agent_id": self.agent_id,
            "agent_role": self.agent_role,
            "message_type": self.message_type,
            "mentioned_agents": self.mentioned_agents,
            "is_agent_triggered": self.is_agent_triggered,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
