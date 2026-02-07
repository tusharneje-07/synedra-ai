"""
WebSocket Routes
===============

WebSocket endpoints for real-time agent debate streaming.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
import logging

from services.websocket_manager import manager
from schemas.websocket import ClientMessage

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/debate")
async def websocket_debate_stream(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time debate streaming.
    
    Streams:
    - Agent thinking process (type: agent_thinking)
    - Debate messages (type: debate)
    - Agent status updates (type: agent_status)
    - Council decisions (type: decision)
    - System notifications (type: system)
    
    Client can send:
    - {"action": "subscribe", "data": {"agent_id": "trend"}}
    - {"action": "unsubscribe", "data": {"agent_id": "trend"}}
    - {"action": "ping"}
    - {"action": "trigger_agent", "data": {"agent_id": "trend", "prompt": "..."}}
    
    Query Parameters:
        client_id: Optional client identifier
    """
    # Connect client
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                # Parse client message
                message = json.loads(data)
                action = message.get("action")
                payload = message.get("data", {})
                
                # Handle client actions
                if action == "subscribe":
                    agent_id = payload.get("agent_id")
                    if agent_id:
                        manager.subscribe(websocket, agent_id)
                        await manager.send_personal_message(websocket, {
                            "type": "system",
                            "level": "info",
                            "message": f"Subscribed to {agent_id} updates"
                        })
                
                elif action == "unsubscribe":
                    agent_id = payload.get("agent_id")
                    if agent_id:
                        manager.unsubscribe(websocket, agent_id)
                        await manager.send_personal_message(websocket, {
                            "type": "system",
                            "level": "info",
                            "message": f"Unsubscribed from {agent_id} updates"
                        })
                
                elif action == "ping":
                    # Heartbeat - no need to send pong, just keep connection alive
                    # Connection is maintained by the websocket being open
                    pass
                
                elif action == "trigger_agent":
                    # Trigger specific agent (will implement in Step 6)
                    await manager.send_personal_message(websocket, {
                        "type": "system",
                        "level": "info",
                        "message": "Agent triggering will be implemented in Step 6"
                    })
                
                else:
                    await manager.send_personal_message(websocket, {
                        "type": "system",
                        "level": "warning",
                        "message": f"Unknown action: {action}"
                    })
            
            except json.JSONDecodeError:
                await manager.send_personal_message(websocket, {
                    "type": "system",
                    "level": "error",
                    "message": "Invalid JSON format"
                })
            
            except Exception as e:
                logger.error(f"Error processing client message: {e}")
                await manager.send_personal_message(websocket, {
                    "type": "system",
                    "level": "error",
                    "message": f"Error processing message: {str(e)}"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from debate stream")


@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.
    
    Returns connection count and subscription details.
    """
    return manager.get_stats()


@router.post("/test/simulate-debate")
async def trigger_simulated_debate():
    """
    Trigger a simulated debate for testing WebSocket streaming.
    
    This endpoint runs a mock council debate to test the WebSocket
    functionality without needing the full CouncilGraph integration.
    
    Usage:
    1. Connect to WebSocket: ws://localhost:8000/api/ws/debate
    2. Call this endpoint: POST /api/ws/test/simulate-debate
    3. Watch the debate stream in WebSocket connection
    """
    from services.debate_simulator import simulate_debate
    import asyncio
    
    # Run simulation in background
    asyncio.create_task(simulate_debate())
    
    return {
        "status": "started",
        "message": "Simulated debate started. Connect to WebSocket to view stream.",
        "websocket_url": "ws://localhost:8000/api/ws/debate"
    }
