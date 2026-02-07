"""
Council Execution Routes
========================

APIs to trigger council sessions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_db
from schemas.council import CouncilExecutionRequest, CouncilExecutionResponse
from services.council_integration import council_integration
from services.brand_config import BrandConfigService

router = APIRouter()


@router.post("/execute", response_model=CouncilExecutionResponse)
async def execute_council(
    request: CouncilExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute AI Council session.
    
    This endpoint triggers a full council session with the specified
    prompt and agents. The session execution is streamed via WebSocket
    to connected clients.
    
    Args:
        request: Council execution request with prompt and agent selection
    
    Returns:
        Session ID and execution details. Connect to WebSocket for real-time updates.
    
    Example:
        ```json
        {
            "prompt": "Should we launch product X in Q2?",
            "trigger_agents": ["trend", "brand", "risk"],
            "use_active_brand_config": true
        }
        ```
    """
    # Get brand configuration if requested
    brand_config = None
    
    if request.brand_config_id:
        # Use specific brand config
        config = await BrandConfigService.get_brand_config(db, request.brand_config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand configuration with ID {request.brand_config_id} not found"
            )
        brand_config = config.to_dict()
    
    elif request.use_active_brand_config:
        # Use active brand config
        config = await BrandConfigService.get_active_brand_config(db)
        if config:
            brand_config = config.to_dict()
    
    # Execute council session
    result = await council_integration.run_council_session(
        prompt=request.prompt,
        brand_config=brand_config,
        trigger_agents=request.trigger_agents
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Council execution failed")
        )
    
    session_result = result["result"]
    
    return CouncilExecutionResponse(
        session_id=result["session_id"],
        success=True,
        decision=session_result.get("decision"),
        confidence=session_result.get("confidence"),
        consensus_level=session_result.get("consensus_level"),
        agent_outputs=session_result.get("agent_outputs"),
        websocket_url="ws://localhost:8001/api/ws/debate"
    )


@router.get("/status")
async def get_council_status():
    """
    Get current council execution status.
    
    Returns whether a council session is currently running.
    """
    session_status = council_integration.current_session_id
    
    return {
        "is_running": session_status is not None,
        "current_session_id": session_status,
        "initialized": council_integration.is_initialized
    }


@router.post("/initialize")
async def initialize_council():
    """
    Initialize CouncilGraph integration.
    
    This endpoint manually triggers initialization of the council system.
    Normally called automatically on first execution.
    """
    success = council_integration.initialize()
    
    return {
        "success": success,
        "initialized": council_integration.is_initialized,
        "message": "CouncilGraph initialized successfully" if success else "Failed to initialize CouncilGraph - using mock mode"
    }
