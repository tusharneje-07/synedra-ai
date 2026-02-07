"""
Chat Message Schemas
===================

Pydantic models for chat API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessageCreate(BaseModel):
    """Create a new chat message."""
    content: str = Field(..., min_length=1, description="Message content")
    project_id: int = Field(..., description="Project ID this message belongs to")
    user_name: Optional[str] = Field("User", description="Name of the user sending the message")


class MentionedAgent(BaseModel):
    """Agent mentioned in message."""
    agent_id: str
    agent_name: str


class ChatMessageResponse(BaseModel):
    """Chat message response."""
    id: str
    content: str
    sender_type: Optional[str] = "user"
    sender_name: Optional[str] = "User"
    agent_id: Optional[str] = None
    agent_role: Optional[str] = None
    message_type: Optional[str] = "chat"
    user_name: Optional[str] = None  # For backwards compatibility
    timestamp: str
    mentioned_agents: List[MentionedAgent] = []
    is_agent_triggered: bool = False
    session_id: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """Chat history response."""
    total: int
    messages: List[ChatMessageResponse]
