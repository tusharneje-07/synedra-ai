"""
Chat Routes
===========

REST APIs for chat messages with @mentions support.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_db
from schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse
)
from services.chat_service import chat_service
from services.council_integration import council_integration
from services.brand_config import BrandConfigService

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    message: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Send chat message with @mentions to trigger specific agents.
    
    Use @mentions to trigger specific agents:
    - @trend - Trigger Trend Analyst
    - @engagement - Trigger Engagement Expert
    - @brand - Trigger Brand Strategist
    - @risk - Trigger Risk Assessor
    - @compliance - Trigger Compliance Officer
    - @arbitrator or @cmo - Trigger CMO Arbitrator
    - @all or @everyone - Trigger all agents
    
    Example messages:
    - "@trend What's trending in tech?"
    - "@brand @risk Should we launch this campaign?"
    - "@all Analyze our Q2 strategy"
    
    Args:
        message: Chat message with content
    
    Returns:
        Message with mentioned agents and trigger status
    """
    # Create message and parse mentions
    chat_message = chat_service.create_message(
        content=message.content,
        user_name=message.user_name
    )
    
    # If agents were mentioned, trigger council in background
    if chat_message["is_agent_triggered"]:
        mentioned_agent_ids = [
            agent["agent_id"]
            for agent in chat_message["mentioned_agents"]
        ]
        
        # Get active brand config
        brand_config = None
        config = await BrandConfigService.get_active_brand_config(db)
        if config:
            brand_config = config.to_dict()
        
        # Create prompt for agents
        prompt = chat_service.get_prompt_for_agents(
            message.content,
            mentioned_agent_ids
        )
        
        # Trigger council in background
        background_tasks.add_task(
            council_integration.run_council_session,
            prompt=prompt,
            brand_config=brand_config,
            trigger_agents=mentioned_agent_ids
        )
    
    return chat_message


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    skip: int = 0
):
    """
    Get chat message history.
    
    Args:
        limit: Maximum number of messages to return (default: 50)
        skip: Number of messages to skip for pagination (default: 0)
    
    Returns:
        Chat history with total count and messages
    """
    return chat_service.get_message_history(limit=limit, skip=skip)


@router.get("/agents/mentions")
async def get_agent_mention_syntax():
    """
    Get available @mention syntax for agents.
    
    Returns dictionary of agent IDs and their mention aliases.
    """
    return {
        "mentions": {
            agent_id: {
                "name": chat_service.AGENT_ALIASES.get(agent_id, [f"@{agent_id}"])[0],
                "aliases": chat_service.AGENT_ALIASES.get(agent_id, []),
                "description": f"Mention {agent_id} agent"
            }
            for agent_id in ["trend", "engagement", "brand", "risk", "compliance", "arbitrator", "all"]
        },
        "examples": [
            "@trend What's trending in AI?",
            "@brand @risk Evaluate campaign risk",
            "@all Full council analysis needed"
        ]
    }
