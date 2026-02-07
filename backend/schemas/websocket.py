"""
WebSocket Message Schemas
=========================

Pydantic models for WebSocket message validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class WSMessage(BaseModel):
    """Base WebSocket message."""
    type: str
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentThinkingMessage(WSMessage):
    """Agent thinking process message."""
    type: Literal["agent_thinking"] = "agent_thinking"
    agent_id: str = Field(..., description="Agent identifier (trend, engagement, brand, etc.)")
    agent_name: str = Field(..., description="Human-readable agent name")
    content: str = Field(..., description="Agent's current thinking/reasoning")
    step: Optional[str] = Field(None, description="Current processing step")


class AgentStatusMessage(WSMessage):
    """Agent status update message."""
    type: Literal["agent_status"] = "agent_status"
    agent_id: str
    agent_name: str
    status: Literal["idle", "thinking", "debating", "voting", "completed"] = Field(
        ..., description="Current agent status"
    )
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")


class DebateMessage(WSMessage):
    """Debate exchange message."""
    type: Literal["debate"] = "debate"
    agent_id: str
    agent_name: str
    position: str = Field(..., description="Agent's position/argument in debate")
    responding_to: Optional[str] = Field(None, description="ID of agent being responded to")
    debate_round: Optional[int] = Field(None, description="Current debate round number")


class DecisionMessage(WSMessage):
    """Council decision message."""
    type: Literal["decision"] = "decision"
    decision: str = Field(..., description="Final decision text")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Decision confidence")
    consensus_level: Optional[str] = Field(None, description="unanimous, majority, split")
    votes: Optional[Dict[str, Any]] = Field(None, description="Voting breakdown")


class SystemMessage(WSMessage):
    """System notification message."""
    type: Literal["system"] = "system"
    level: Literal["info", "warning", "error", "success"] = "info"
    message: str


class CouncilStartMessage(WSMessage):
    """Council session started."""
    type: Literal["council_start"] = "council_start"
    session_id: str
    topic: str = Field(..., description="Topic/prompt being discussed")
    agents: list[str] = Field(..., description="List of participating agents")


class CouncilEndMessage(WSMessage):
    """Council session ended."""
    type: Literal["council_end"] = "council_end"
    session_id: str
    duration_seconds: Optional[float] = None
    outcome: str = Field(..., description="Final outcome summary")


# Client -> Server Messages
class ClientMessage(BaseModel):
    """Message from client to server."""
    action: Literal["subscribe", "unsubscribe", "ping", "trigger_agent"]
    data: Optional[Dict[str, Any]] = None


class TriggerAgentRequest(BaseModel):
    """Request to trigger specific agent."""
    agent_id: str = Field(..., description="Agent to trigger")
    prompt: str = Field(..., description="User prompt/question")
    session_id: Optional[str] = None
