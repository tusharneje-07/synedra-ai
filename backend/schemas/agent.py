"""
Agent Status Schemas
===================

Pydantic models for agent status API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class AgentMetrics(BaseModel):
    """Agent performance metrics."""
    total_analyses: int = 0
    successful_analyses: int = 0
    average_response_time: Optional[float] = None
    last_active: Optional[str] = None


class AgentStatusResponse(BaseModel):
    """Single agent status response."""
    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Human-readable agent name")
    role: str = Field(..., description="Agent role/specialty")
    status: Literal["idle", "thinking", "debating", "voting", "completed", "error"] = Field(
        ..., description="Current agent status"
    )
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    current_task: Optional[str] = Field(None, description="Current task description")
    last_output: Optional[str] = Field(None, description="Last analysis/output")
    metrics: Optional[AgentMetrics] = None
    is_available: bool = Field(True, description="Whether agent is available for tasks")
    error_message: Optional[str] = Field(None, description="Error message if status is error")


class AllAgentsStatusResponse(BaseModel):
    """Status of all agents."""
    total_agents: int
    active_agents: int
    idle_agents: int
    agents: List[AgentStatusResponse]
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentCapability(BaseModel):
    """Agent capability description."""
    name: str
    description: str
    examples: Optional[List[str]] = None


class AgentInfoResponse(BaseModel):
    """Detailed agent information."""
    agent_id: str
    agent_name: str
    role: str
    description: str
    capabilities: List[AgentCapability]
    prompt_template: Optional[str] = None
    model: Optional[str] = None
    status: str


class CouncilSessionStatus(BaseModel):
    """Current council session status."""
    session_id: Optional[str] = None
    is_active: bool = False
    topic: Optional[str] = None
    participating_agents: List[str] = []
    current_phase: Optional[Literal["analysis", "debate", "voting", "completed"]] = None
    started_at: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
