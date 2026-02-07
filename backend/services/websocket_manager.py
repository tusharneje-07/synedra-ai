"""
WebSocket Connection Manager
============================

Manages WebSocket connections and broadcasts messages to clients.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Set
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager.
    
    Handles multiple client connections and broadcasting messages.
    """
    
    def __init__(self):
        # Active connections
        self.active_connections: List[WebSocket] = []
        
        # Connection metadata
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Subscriptions (agent-specific)
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """
        Accept new WebSocket connection.
        
        Args:
            websocket: WebSocket instance
            client_id: Optional client identifier
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Store connection metadata
        self.connection_info[websocket] = {
            "client_id": client_id or f"client_{id(websocket)}",
            "connected_at": datetime.utcnow().isoformat(),
            "subscriptions": set()
        }
        
        logger.info(f"WebSocket connected: {self.connection_info[websocket]['client_id']}")
        logger.info(f"Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message(
            websocket,
            {
                "type": "system",
                "level": "info",
                "message": "Connected to AI Council debate stream",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection.
        
        Args:
            websocket: WebSocket instance to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
            # Clean up subscriptions
            for agent_id, subscribers in self.subscriptions.items():
                if websocket in subscribers:
                    subscribers.remove(websocket)
            
            client_id = self.connection_info.get(websocket, {}).get("client_id", "unknown")
            logger.info(f"WebSocket disconnected: {client_id}")
            logger.info(f"Total connections: {len(self.active_connections)}")
            
            # Clean up metadata
            if websocket in self.connection_info:
                del self.connection_info[websocket]
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send message to specific client.
        
        Args:
            websocket: Target WebSocket
            message: Message dictionary
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any], exclude: WebSocket = None):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message dictionary
            exclude: Optional WebSocket to exclude from broadcast
        """
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
        
        # Send to all connections
        disconnected = []
        for connection in self.active_connections:
            if connection == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_subscribers(self, agent_id: str, message: Dict[str, Any]):
        """
        Broadcast message to clients subscribed to specific agent.
        
        Args:
            agent_id: Agent identifier
            message: Message dictionary
        """
        if agent_id not in self.subscriptions:
            # No subscribers for this agent, broadcast to all
            await self.broadcast(message)
            return
        
        # Send to subscribers
        disconnected = []
        for connection in self.subscriptions[agent_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to subscriber: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected
        for conn in disconnected:
            if agent_id in self.subscriptions and conn in self.subscriptions[agent_id]:
                self.subscriptions[agent_id].remove(conn)
    
    def subscribe(self, websocket: WebSocket, agent_id: str):
        """
        Subscribe client to specific agent updates.
        
        Args:
            websocket: WebSocket instance
            agent_id: Agent identifier
        """
        if agent_id not in self.subscriptions:
            self.subscriptions[agent_id] = set()
        
        self.subscriptions[agent_id].add(websocket)
        
        if websocket in self.connection_info:
            self.connection_info[websocket]["subscriptions"].add(agent_id)
        
        logger.info(f"Client subscribed to agent: {agent_id}")
    
    def unsubscribe(self, websocket: WebSocket, agent_id: str):
        """
        Unsubscribe client from agent updates.
        
        Args:
            websocket: WebSocket instance
            agent_id: Agent identifier
        """
        if agent_id in self.subscriptions and websocket in self.subscriptions[agent_id]:
            self.subscriptions[agent_id].remove(websocket)
        
        if websocket in self.connection_info:
            self.connection_info[websocket]["subscriptions"].discard(agent_id)
        
        logger.info(f"Client unsubscribed from agent: {agent_id}")
    
    async def send_agent_thinking(
        self,
        agent_id: str,
        agent_name: str,
        content: str,
        step: str = None
    ):
        """Send agent thinking message to all clients."""
        message = {
            "type": "agent_thinking",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "content": content,
            "step": step,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def send_agent_status(
        self,
        agent_id: str,
        agent_name: str,
        status: str,
        progress: int = None
    ):
        """Send agent status update to all clients."""
        message = {
            "type": "agent_status",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "status": status,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def send_debate_message(
        self,
        agent_id: str,
        agent_name: str,
        position: str,
        responding_to: str = None,
        debate_round: int = None
    ):
        """Send debate message to all clients."""
        message = {
            "type": "debate",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "position": position,
            "responding_to": responding_to,
            "debate_round": debate_round,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def send_decision(
        self,
        decision: str,
        confidence: float = None,
        consensus_level: str = None,
        votes: Dict[str, Any] = None,
        session_id: str = None
    ):
        """Send final decision to all clients."""
        message = {
            "type": "decision",
            "decision": decision,
            "confidence": confidence,
            "consensus_level": consensus_level,
            "votes": votes,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def send_system_message(self, level: str, text: str):
        """Send system message to all clients."""
        message = {
            "type": "system",
            "level": level,
            "message": text,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "subscriptions": {
                agent_id: len(subs)
                for agent_id, subs in self.subscriptions.items()
            }
        }


# Global connection manager instance
manager = ConnectionManager()
