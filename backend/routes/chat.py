"""
Chat Routes
===========

REST APIs for chat messages with database persistence and @mentions support.
"""

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_db
from schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse
)
from services.chat_service import ChatService
from services.council_integration import council_integration
from services.brand_config import BrandConfigService
from services.project_service import ProjectService
from services.websocket_manager import manager

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    message: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Send chat message with @mentions to trigger specific agents.
    
    **Requires project_id to link message to a project.**
    
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
        message: Chat message with content and project_id
    
    Returns:
        Message with mentioned agents and trigger status
    """
    # Verify project exists
    project_service = ProjectService(db)
    project = await project_service.get_project(message.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create chat service with db session
    chat_svc = ChatService(db)
    
    # Create and save message to database
    chat_message = await chat_svc.create_message(
        content=message.content,
        project_id=message.project_id,
        session_id=None,  # Will be set when council starts
        sender_type="user",
        sender_name=message.user_name,
        message_type="chat"
    )
    
    # Parse mentions
    mentioned_agents, _ = chat_svc.parse_mentions(message.content)
    
    # Broadcast user message to WebSocket clients in real-time
    await manager.broadcast({
        "type": "user_message",
        "content": chat_message.content,
        "sender_name": chat_message.sender_name,
        "project_id": message.project_id,
        "mentioned_agents": mentioned_agents,
        "timestamp": chat_message.created_at.isoformat()
    })
    
    # If agents were mentioned, trigger council in background
    if mentioned_agents:
        # Get active brand config
        brand_config = None
        config = await BrandConfigService.get_active_brand_config(db)
        if config:
            brand_config = config.to_dict()
        
        # Prepare project context
        project_context = {
            "project_id": project.id,
            "project_name": project.name,
            "description": project.description,
            "post_topic": project.post_topic,
            "product_details": project.product_details,
            "target_details": project.target_details,
            "questionnaire_data": project.questionnaire_data,
        }
        
        # Create prompt for agents
        prompt = chat_svc.get_prompt_for_agents(
            message.content,
            mentioned_agents
        )
        
        # Trigger council in background
        background_tasks.add_task(
            council_integration.run_council_session,
            prompt=prompt,
            brand_config=brand_config,
            trigger_agents=mentioned_agents,
            project_context=project_context,
            db=db
        )
    
    return {
        "id": chat_message.message_id,
        "content": chat_message.content,
        "sender_type": chat_message.sender_type,
        "sender_name": chat_message.sender_name,
        "user_name": chat_message.sender_name,  # For backwards compatibility
        "message_type": chat_message.message_type,
        "timestamp": chat_message.created_at.isoformat(),
        "mentioned_agents": [
            {"agent_id": aid, "agent_name": aid}
            for aid in mentioned_agents
        ],
        "is_agent_triggered": len(mentioned_agents) > 0,
        "session_id": chat_message.session_id
    }


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    project_id: int,
    session_id: str = None,
    limit: int = 100,
    skip: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Get chat message history for a project from database.
    
    Args:
        project_id: Project ID to get messages for (required)
        session_id: Optional session ID to filter by specific council session
        limit: Maximum number of messages to return (default: 100)
        skip: Number of messages to skip for pagination (default: 0)
    
    Returns:
        Chat history with total count and messages
    """
    # Verify project exists
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get message history from database
    chat_svc = ChatService(db)
    history = await chat_svc.get_message_history(
        project_id=project_id,
        session_id=session_id,
        limit=limit,
        skip=skip
    )
    
    return history


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
