"""
WebSocket Demo/Test Endpoint
============================

Simulates council debate for testing WebSocket streaming.
"""

import asyncio
from datetime import datetime
import random
from services.websocket_manager import manager


async def simulate_debate():
    """
    Simulate a council debate for testing.
    
    This function can be called to test WebSocket streaming
    without running the full CouncilGraph.
    """
    session_id = f"sim_{datetime.utcnow().timestamp()}"
    
    agents = [
        {"id": "trend", "name": "Trend Analyst"},
        {"id": "engagement", "name": "Engagement Expert"},
        {"id": "brand", "name": "Brand Strategist"},
        {"id": "risk", "name": "Risk Assessor"},
        {"id": "compliance", "name": "Compliance Officer"},
    ]
    
    # Start session
    await manager.broadcast({
        "type": "council_start",
        "session_id": session_id,
        "topic": "Launch campaign for new product line",
        "agents": [a["id"] for a in agents]
    })
    
    await asyncio.sleep(1)
    
    # Simulate each agent thinking
    for agent in agents:
        await manager.send_agent_status(
            agent["id"],
            agent["name"],
            "thinking",
            progress=0
        )
        
        await asyncio.sleep(0.5)
        
        await manager.send_agent_thinking(
            agent["id"],
            agent["name"],
            f"{agent['name']} analyzing the situation...",
            step="analysis"
        )
        
        await asyncio.sleep(1)
        
        await manager.send_agent_status(
            agent["id"],
            agent["name"],
            "thinking",
            progress=50
        )
        
        await asyncio.sleep(0.5)
        
        await manager.send_agent_status(
            agent["id"],
            agent["name"],
            "completed",
            progress=100
        )
    
    # Simulate debate
    await asyncio.sleep(1)
    
    debate_points = [
        ("trend", "Trend Analyst", "Based on current data, I recommend focusing on Gen Z audience with short-form video content."),
        ("brand", "Brand Strategist", "I agree, but we must ensure it aligns with our premium brand positioning."),
        ("risk", "Risk Assessor", "We should consider potential backlash from our existing customer base."),
        ("engagement", "Engagement Expert", "The engagement metrics support the Gen Z strategy - 3x higher interaction rates."),
    ]
    
    for i, (agent_id, agent_name, position) in enumerate(debate_points):
        await manager.send_agent_status(agent_id, agent_name, "debating")
        await asyncio.sleep(0.5)
        
        await manager.send_debate_message(
            agent_id,
            agent_name,
            position,
            debate_round=1
        )
        
        await asyncio.sleep(1.5)
        await manager.send_agent_status(agent_id, agent_name, "idle")
    
    # Final decision
    await asyncio.sleep(1)
    
    await manager.send_decision(
        decision="Proceed with Gen Z-focused campaign using short-form video, while maintaining premium brand voice. Gradual rollout to minimize existing customer concerns.",
        confidence=0.85,
        consensus_level="majority",
        votes={
            "approve": ["trend", "engagement", "brand"],
            "approve_with_conditions": ["risk"],
            "abstain": ["compliance"]
        }
    )
    
    await asyncio.sleep(1)
    
    # End session
    await manager.broadcast({
        "type": "council_end",
        "session_id": session_id,
        "duration_seconds": 12.5,
        "outcome": "Campaign strategy approved with risk mitigation measures"
    })
    
    await manager.send_system_message(
        "success",
        "Council session completed successfully"
    )
