"""
Council Execution Schemas
=========================

Pydantic models for triggering council sessions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CouncilExecutionRequest(BaseModel):
    """Request to execute council session."""
    prompt: str = Field(..., min_length=1, description="Topic or question for the council to discuss")
    trigger_agents: Optional[List[str]] = Field(
        None,
        description="Specific agents to trigger. If None, all agents participate."
    )
    use_active_brand_config: bool = Field(
        True,
        description="Use active brand configuration from database"
    )
    brand_config_id: Optional[int] = Field(
        None,
        description="Specific brand config ID to use. Overrides use_active_brand_config."
    )


class CouncilExecutionResponse(BaseModel):
    """Response from council execution."""
    session_id: str
    success: bool
    decision: Optional[str] = None
    confidence: Optional[float] = None
    consensus_level: Optional[str] = None
    agent_outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    websocket_url: str = Field(
        default="ws://localhost:8001/api/ws/debate",
        description="WebSocket URL to connect for real-time updates"
    )
