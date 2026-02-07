"""
Council Event Broadcaster
========================

Integrates with CouncilGraph to broadcast events to WebSocket clients.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from services.websocket_manager import manager

logger = logging.getLogger(__name__)


class CouncilEventBroadcaster:
    """
    Broadcasts council events to WebSocket clients.
    
    This class acts as a bridge between the CouncilGraph
    and WebSocket clients, streaming real-time updates.
    """
    
    def __init__(self):
        self.current_session_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
    
    async def broadcast_council_start(
        self,
        session_id: str,
        topic: str,
        agents: list[str]
    ):
        """
        Broadcast council session start.
        
        Args:
            session_id: Unique session identifier
            topic: Topic being discussed
            agents: List of participating agents
        """
        self.current_session_id = session_id
        self.session_start_time = datetime.utcnow()
        
        message = {
            "type": "council_start",
            "session_id": session_id,
            "topic": topic,
            "agents": agents,
            "timestamp": self.session_start_time.isoformat()
        }
        
        await manager.broadcast(message)
        logger.info(f"Council session started: {session_id}")
    
    async def broadcast_council_end(
        self,
        session_id: str,
        outcome: str
    ):
        """
        Broadcast council session end.
        
        Args:
            session_id: Session identifier
            outcome: Final outcome summary
        """
        duration = None
        if self.session_start_time:
            duration = (datetime.utcnow() - self.session_start_time).total_seconds()
        
        message = {
            "type": "council_end",
            "session_id": session_id,
            "duration_seconds": duration,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.broadcast(message)
        logger.info(f"Council session ended: {session_id}")
        
        # Reset session
        self.current_session_id = None
        self.session_start_time = None
    
    async def broadcast_agent_thinking(
        self,
        agent_id: str,
        agent_name: str,
        content: str,
        step: Optional[str] = None
    ):
        """
        Broadcast agent thinking process.
        
        Args:
            agent_id: Agent identifier
            agent_name: Human-readable agent name
            content: Agent's reasoning/thinking
            step: Current processing step
        """
        await manager.send_agent_thinking(agent_id, agent_name, content, step)
    
    async def broadcast_agent_status(
        self,
        agent_id: str,
        agent_name: str,
        status: str,
        progress: Optional[int] = None
    ):
        """
        Broadcast agent status update.
        
        Args:
            agent_id: Agent identifier
            agent_name: Human-readable agent name
            status: Current status (idle, thinking, debating, voting, completed)
            progress: Progress percentage (0-100)
        """
        await manager.send_agent_status(agent_id, agent_name, status, progress)
    
    async def broadcast_debate(
        self,
        agent_id: str,
        agent_name: str,
        position: str,
        responding_to: Optional[str] = None,
        debate_round: Optional[int] = None
    ):
        """
        Broadcast debate message.
        
        Args:
            agent_id: Agent identifier
            agent_name: Human-readable agent name
            position: Agent's argument/position
            responding_to: Agent being responded to
            debate_round: Current debate round
        """
        await manager.send_debate_message(
            agent_id,
            agent_name,
            position,
            responding_to,
            debate_round
        )
    
    async def broadcast_decision(
        self,
        decision: str,
        confidence: Optional[float] = None,
        consensus_level: Optional[str] = None,
        votes: Optional[Dict[str, Any]] = None
    ):
        """
        Broadcast final council decision.
        
        Args:
            decision: Final decision text
            confidence: Decision confidence (0.0-1.0)
            consensus_level: unanimous, majority, split
            votes: Voting breakdown
        """
        await manager.send_decision(decision, confidence, consensus_level, votes)
    
    async def broadcast_system_message(self, level: str, message: str):
        """
        Broadcast system message.
        
        Args:
            level: Message level (info, warning, error, success)
            message: Message text
        """
        await manager.send_system_message(level, message)
    
    # Helper method to stream agent output in chunks
    async def stream_agent_output(
        self,
        agent_id: str,
        agent_name: str,
        output_generator
    ):
        """
        Stream agent output in real-time chunks.
        
        Args:
            agent_id: Agent identifier
            agent_name: Agent name
            output_generator: Async generator yielding text chunks
        """
        full_output = ""
        
        try:
            async for chunk in output_generator:
                full_output += chunk
                
                # Stream chunk
                await self.broadcast_agent_thinking(
                    agent_id,
                    agent_name,
                    chunk,
                    step="streaming"
                )
                
                # Small delay to avoid overwhelming clients
                await asyncio.sleep(0.05)
            
            # Send complete output
            await self.broadcast_agent_thinking(
                agent_id,
                agent_name,
                full_output,
                step="completed"
            )
        
        except Exception as e:
            logger.error(f"Error streaming agent output: {e}")
            await self.broadcast_system_message(
                "error",
                f"Error streaming {agent_name} output: {str(e)}"
            )


# Global broadcaster instance
broadcaster = CouncilEventBroadcaster()
