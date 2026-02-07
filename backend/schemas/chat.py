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
    user_name: Optional[str] = Field("User", description="Name of the user sending the message")


class MentionedAgent(BaseModel):
    """Agent mentioned in message."""
    agent_id: str
    agent_name: str


class ChatMessageResponse(BaseModel):
    """Chat message response."""
    id: str
    content: str
    user_name: str
    timestamp: str
    mentioned_agents: List[MentionedAgent] = []
    is_agent_triggered: bool = False
    session_id: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """Chat history response."""
    total: int
    messages: List[ChatMessageResponse]
