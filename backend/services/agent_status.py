"""
Agent Status Service
===================

Tracks and manages agent states and status.
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    THINKING = "thinking"
    DEBATING = "debating"
    VOTING = "voting"
    COMPLETED = "completed"
    ERROR = "error"


class AgentState:
    """Represents the current state of an agent."""
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        role: str,
        description: str
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.role = role
        self.description = description
        self.status = AgentStatus.IDLE
        self.progress: Optional[int] = None
        self.current_task: Optional[str] = None
        self.last_output: Optional[str] = None
        self.is_available = True
        self.error_message: Optional[str] = None
        
        # Metrics
        self.total_analyses = 0
        self.successful_analyses = 0
        self.response_times: List[float] = []
        self.last_active: Optional[datetime] = None
    
    def update_status(
        self,
        status: AgentStatus,
        progress: Optional[int] = None,
        current_task: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Update agent status."""
        self.status = status
        self.progress = progress
        self.current_task = current_task
        self.error_message = error_message
        self.last_active = datetime.utcnow()
        
        if status == AgentStatus.IDLE:
            self.progress = None
            self.current_task = None
    
    def record_analysis(self, success: bool, response_time: float = None):
        """Record an analysis completion."""
        self.total_analyses += 1
        if success:
            self.successful_analyses += 1
        if response_time is not None:
            self.response_times.append(response_time)
            # Keep only last 100 response times
            if len(self.response_times) > 100:
                self.response_times.pop(0)
    
    def get_average_response_time(self) -> Optional[float]:
        """Calculate average response time."""
        if not self.response_times:
            return None
        return sum(self.response_times) / len(self.response_times)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "role": self.role,
            "status": self.status.value,
            "progress": self.progress,
            "current_task": self.current_task,
            "last_output": self.last_output,
            "is_available": self.is_available,
            "error_message": self.error_message,
            "metrics": {
                "total_analyses": self.total_analyses,
                "successful_analyses": self.successful_analyses,
                "average_response_time": self.get_average_response_time(),
                "last_active": self.last_active.isoformat() if self.last_active else None
            }
        }


class AgentStatusService:
    """Service for managing agent status."""
    
    # Agent definitions
    AGENTS = {
        "trend": {
            "name": "Trend Analyst",
            "role": "Market & Social Trends Analysis",
            "description": "Analyzes current market trends, social media patterns, and emerging topics to inform content strategy",
            "capabilities": [
                {
                    "name": "Trend Detection",
                    "description": "Identifies trending topics and hashtags",
                    "examples": ["#TechInnovation trending +150%", "AI content surging in engagement"]
                },
                {
                    "name": "Platform Analysis",
                    "description": "Analyzes performance across social platforms",
                    "examples": ["Instagram Reels performing 3x better", "LinkedIn posts peak at 9AM"]
                }
            ]
        },
        "engagement": {
            "name": "Engagement Expert",
            "role": "Audience Engagement Analysis",
            "description": "Evaluates content for engagement potential, analyzes audience preferences and interaction patterns",
            "capabilities": [
                {
                    "name": "Engagement Prediction",
                    "description": "Predicts content engagement rates",
                    "examples": ["Video format: +45% engagement", "Question posts: 2x comments"]
                },
                {
                    "name": "Audience Insights",
                    "description": "Analyzes audience behavior and preferences",
                    "examples": ["Gen Z prefers short-form video", "B2B audience engages with data"]
                }
            ]
        },
        "brand": {
            "name": "Brand Strategist",
            "role": "Brand Voice & Positioning",
            "description": "Ensures content aligns with brand voice, values, and positioning strategy",
            "capabilities": [
                {
                    "name": "Brand Alignment",
                    "description": "Validates content matches brand voice",
                    "examples": ["Maintains premium tone", "Aligns with sustainability values"]
                },
                {
                    "name": "Competitive Positioning",
                    "description": "Analyzes competitive landscape",
                    "examples": ["Differentiate from Competitor X", "Emphasize unique value prop"]
                }
            ]
        },
        "risk": {
            "name": "Risk Assessor",
            "role": "Risk & Crisis Management",
            "description": "Identifies potential risks, controversies, and crisis scenarios in proposed content",
            "capabilities": [
                {
                    "name": "Risk Detection",
                    "description": "Identifies potential controversies",
                    "examples": ["Sensitive topic alert", "Regulatory compliance check"]
                },
                {
                    "name": "Crisis Prevention",
                    "description": "Suggests risk mitigation strategies",
                    "examples": ["Add disclaimer", "Avoid polarizing language"]
                }
            ]
        },
        "compliance": {
            "name": "Compliance Officer",
            "role": "Legal & Regulatory Compliance",
            "description": "Ensures content meets legal requirements, advertising standards, and platform policies",
            "capabilities": [
                {
                    "name": "Legal Review",
                    "description": "Validates legal compliance",
                    "examples": ["FTC disclosure required", "Copyright clearance needed"]
                },
                {
                    "name": "Platform Policy",
                    "description": "Checks platform-specific rules",
                    "examples": ["Meets Instagram ad policy", "Complies with GDPR"]
                }
            ]
        },
        "arbitrator": {
            "name": "CMO Arbitrator",
            "role": "Final Decision Making",
            "description": "Makes final decisions by weighing all agent inputs and resolving conflicts",
            "capabilities": [
                {
                    "name": "Consensus Building",
                    "description": "Synthesizes agent recommendations",
                    "examples": ["Balance risk vs. innovation", "Prioritize brand safety"]
                },
                {
                    "name": "Strategic Decisions",
                    "description": "Makes executive-level calls",
                    "examples": ["Approve campaign direction", "Authorize budget allocation"]
                }
            ]
        }
    }
    
    def __init__(self):
        """Initialize agent status service."""
        self.agents: Dict[str, AgentState] = {}
        self._initialize_agents()
        self.current_session_id: Optional[str] = None
        self.session_topic: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
        self.session_phase: Optional[str] = None
    
    def _initialize_agents(self):
        """Initialize all agents with idle status."""
        for agent_id, info in self.AGENTS.items():
            self.agents[agent_id] = AgentState(
                agent_id=agent_id,
                agent_name=info["name"],
                role=info["role"],
                description=info["description"]
            )
        logger.info(f"Initialized {len(self.agents)} agents")
    
    def get_agent_status(self, agent_id: str) -> Optional[dict]:
        """Get status of specific agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        return agent.to_dict()
    
    def get_all_agents_status(self) -> dict:
        """Get status of all agents."""
        agents_list = [agent.to_dict() for agent in self.agents.values()]
        active_count = sum(1 for a in agents_list if a["status"] != "idle")
        idle_count = sum(1 for a in agents_list if a["status"] == "idle")
        
        return {
            "total_agents": len(agents_list),
            "active_agents": active_count,
            "idle_agents": idle_count,
            "agents": agents_list,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def update_agent_status(
        self,
        agent_id: str,
        status: str,
        progress: Optional[int] = None,
        current_task: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update agent status."""
        agent = self.agents.get(agent_id)
        if not agent:
            logger.warning(f"Agent not found: {agent_id}")
            return False
        
        try:
            agent_status = AgentStatus(status)
            agent.update_status(agent_status, progress, current_task, error_message)
            logger.info(f"Updated {agent_id} status to {status}")
            return True
        except ValueError:
            logger.error(f"Invalid status: {status}")
            return False
    
    def get_agent_info(self, agent_id: str) -> Optional[dict]:
        """Get detailed agent information including capabilities."""
        if agent_id not in self.AGENTS:
            return None
        
        info = self.AGENTS[agent_id]
        agent = self.agents.get(agent_id)
        
        return {
            "agent_id": agent_id,
            "agent_name": info["name"],
            "role": info["role"],
            "description": info["description"],
            "capabilities": info["capabilities"],
            "status": agent.status.value if agent else "idle",
            "model": "llama-3.3-70b-versatile"  # From AgenticEnv config
        }
    
    def start_council_session(self, session_id: str, topic: str, agents: List[str]):
        """Start a new council session."""
        self.current_session_id = session_id
        self.session_topic = topic
        self.session_start_time = datetime.utcnow()
        self.session_phase = "analysis"
        
        # Set participating agents to thinking
        for agent_id in agents:
            if agent_id in self.agents:
                self.update_agent_status(agent_id, AgentStatus.THINKING.value, current_task=topic)
        
        logger.info(f"Council session started: {session_id}")
    
    def end_council_session(self):
        """End current council session."""
        # Reset all agents to idle
        for agent in self.agents.values():
            agent.update_status(AgentStatus.IDLE)
        
        self.current_session_id = None
        self.session_topic = None
        self.session_start_time = None
        self.session_phase = None
        
        logger.info("Council session ended")
    
    def get_council_session_status(self) -> dict:
        """Get current council session status."""
        if not self.current_session_id:
            return {
                "session_id": None,
                "is_active": False,
                "topic": None,
                "participating_agents": [],
                "current_phase": None,
                "started_at": None,
                "progress": None
            }
        
        # Calculate progress based on agent statuses
        active_agents = [a for a in self.agents.values() if a.status != AgentStatus.IDLE]
        total_progress = sum(a.progress or 0 for a in active_agents) if active_agents else 0
        avg_progress = int(total_progress / len(active_agents)) if active_agents else 0
        
        return {
            "session_id": self.current_session_id,
            "is_active": True,
            "topic": self.session_topic,
            "participating_agents": [a.agent_id for a in active_agents],
            "current_phase": self.session_phase,
            "started_at": self.session_start_time.isoformat() if self.session_start_time else None,
            "progress": avg_progress
        }


# Global service instance
agent_status_service = AgentStatusService()
