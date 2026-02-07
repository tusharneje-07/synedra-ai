"""
Agent Status Routes
==================

REST APIs for agent status and monitoring.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from schemas.agent import (
    AgentStatusResponse,
    AllAgentsStatusResponse,
    AgentInfoResponse,
    CouncilSessionStatus
)
from services.agent_status import agent_status_service

router = APIRouter()


@router.get("/status", response_model=AllAgentsStatusResponse)
async def get_all_agents_status():
    """
    Get status of all agents.
    
    Returns current status, progress, and metrics for all AI agents
    in the council.
    """
    return agent_status_service.get_all_agents_status()


@router.get("/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str):
    """
    Get status of specific agent.
    
    Args:
        agent_id: Agent identifier (trend, engagement, brand, risk, compliance, arbitrator)
    
    Returns:
        Current status, progress, metrics, and task information
    """
    agent_status = agent_status_service.get_agent_status(agent_id)
    
    if not agent_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )
    
    return agent_status


@router.get("/{agent_id}/info", response_model=AgentInfoResponse)
async def get_agent_info(agent_id: str):
    """
    Get detailed information about an agent.
    
    Args:
        agent_id: Agent identifier
    
    Returns:
        Agent capabilities, role, description, and current status
    """
    agent_info = agent_status_service.get_agent_info(agent_id)
    
    if not agent_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )
    
    return agent_info


@router.get("/", response_model=list[AgentInfoResponse])
async def list_all_agents():
    """
    List all available agents with their capabilities.
    
    Returns list of all agents in the council with their roles,
    descriptions, and capabilities.
    """
    agents = []
    for agent_id in agent_status_service.AGENTS.keys():
        agent_info = agent_status_service.get_agent_info(agent_id)
        if agent_info:
            agents.append(agent_info)
    
    return agents


@router.post("/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status: str,
    progress: Optional[int] = None,
    current_task: Optional[str] = None
):
    """
    Update agent status (internal use).
    
    Args:
        agent_id: Agent identifier
        status: New status (idle, thinking, debating, voting, completed, error)
        progress: Progress percentage (0-100)
        current_task: Current task description
    
    Note: This endpoint is for internal use by the council orchestrator.
    """
    success = agent_status_service.update_agent_status(
        agent_id,
        status,
        progress,
        current_task
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update agent status"
        )
    
    return {"success": True, "agent_id": agent_id, "status": status}


@router.get("/session/status", response_model=CouncilSessionStatus)
async def get_council_session_status():
    """
    Get current council session status.
    
    Returns information about the active council session,
    including participating agents, topic, and progress.
    """
    return agent_status_service.get_council_session_status()
