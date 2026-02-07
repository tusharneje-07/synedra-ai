"""
Council Event Broadcaster
========================

Integrates with CouncilGraph to broadcast events to WebSocket clients.
"""

import asyncio
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from services.websocket_manager import manager
from models.chat_message import ChatMessage

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
        self.db: Optional[AsyncSession] = None
        self.project_id: Optional[int] = None
    
    def set_session_context(
        self, 
        session_id: str, 
        db: Optional[AsyncSession] = None,
        project_id: Optional[int] = None
    ):
        """
        Set the session context for database persistence.
        
        Args:
            session_id: Session identifier
            db: Database session for saving messages
            project_id: Project ID for linking messages
        """
        self.current_session_id = session_id
        self.db = db
        self.project_id = project_id
    
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
        # Save to database if session context is set
        if self.db and self.project_id and self.current_session_id:
            try:
                chat_message = ChatMessage(
                    message_id=str(uuid.uuid4()),
                    project_id=self.project_id,
                    session_id=self.current_session_id,
                    content=content,
                    sender_type="agent",
                    sender_name=agent_name,
                    agent_id=agent_id,
                    agent_role=agent_name,
                    message_type="thinking"
                )
                self.db.add(chat_message)
                await self.db.commit()
            except Exception as e:
                logger.error(f"Failed to save agent thinking to database: {e}")
        
        # Broadcast via WebSocket
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
        # Save to database if session context is set
        if self.db and self.project_id and self.current_session_id:
            try:
                chat_message = ChatMessage(
                    message_id=str(uuid.uuid4()),
                    project_id=self.project_id,
                    session_id=self.current_session_id,
                    content=position,
                    sender_type="agent",
                    sender_name=agent_name,
                    agent_id=agent_id,
                    agent_role=agent_name,
                    message_type="debate"
                )
                self.db.add(chat_message)
                await self.db.commit()
            except Exception as e:
                logger.error(f"Failed to save debate message to database: {e}")
        
        # Broadcast via WebSocket
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
        # Save to database if session context is set
        if self.db and self.project_id and self.current_session_id:
            try:
                chat_message = ChatMessage(
                    message_id=str(uuid.uuid4()),
                    project_id=self.project_id,
                    session_id=self.current_session_id,
                    content=decision,
                    sender_type="system",
                    sender_name="Council",
                    message_type="decision"
                )
                self.db.add(chat_message)
                await self.db.commit()
            except Exception as e:
                logger.error(f"Failed to save decision to database: {e}")
        
        # Broadcast via WebSocket with session_id
        await manager.send_decision(decision, confidence, consensus_level, votes, self.current_session_id)
    
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
