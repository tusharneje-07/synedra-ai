"""
Project Routes - API endpoints for project management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from database.base import get_db
from services.project_service import ProjectService
from services.question_service import QuestionGenerationService
from schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListItem,
    ProjectQuestionnaireUpdate,
    ProjectSessionResponse
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    service = ProjectService(db)
    new_project = await service.create_project(project)
    return new_project


@router.get("", response_model=List[ProjectListItem])
async def list_projects(
    brand_config_id: Optional[int] = Query(None, description="Filter by brand config ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all projects with optional filtering"""
    service = ProjectService(db)
    projects = await service.list_projects(
        brand_config_id=brand_config_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project by ID"""
    service = ProjectService(db)
    project = await service.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a project"""
    service = ProjectService(db)
    updated_project = await service.update_project(project_id, project_data)
    
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return updated_project


@router.put("/{project_id}/questionnaire", response_model=ProjectResponse)
async def update_project_questionnaire(
    project_id: int,
    questionnaire: ProjectQuestionnaireUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update project questionnaire data"""
    service = ProjectService(db)
    updated_project = await service.update_questionnaire(project_id, questionnaire)
    
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return updated_project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a project and all associated data"""
    service = ProjectService(db)
    deleted = await service.delete_project(project_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return None


@router.get("/{project_id}/sessions", response_model=List[ProjectSessionResponse])
async def get_project_sessions(
    project_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of sessions to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get recent sessions for a project"""
    service = ProjectService(db)
    
    # Verify project exists
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    sessions = await service.get_project_sessions(project_id, limit)
    return sessions


@router.get("/{project_id}/messages")
async def get_project_messages(
    project_id: int,
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(100, ge=1, le=500, description="Number of messages to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a project"""
    service = ProjectService(db)
    
    # Verify project exists
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    messages = await service.get_project_messages(project_id, session_id, limit)
    
    # Convert to dict for JSON response
    return [
        {
            "id": msg.id,
            "message_id": msg.message_id,
            "project_id": msg.project_id,
            "session_id": msg.session_id,
            "content": msg.content,
            "sender_type": msg.sender_type,
            "sender_name": msg.sender_name,
            "agent_id": msg.agent_id,
            "agent_role": msg.agent_role,
            "message_type": msg.message_type,
            "mentioned_agents": msg.mentioned_agents,
            "is_agent_triggered": msg.is_agent_triggered,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]


@router.post("/generate-questionnaire")
async def generate_questionnaire(
    project_name: str = Body(..., description="Project name"),
    description: Optional[str] = Body(None, description="Project description"),
    product_details: Optional[Dict[str, Any]] = Body(None, description="Product details"),
    target_details: Optional[Dict[str, Any]] = Body(None, description="Target audience details")
):
    """Generate AI-powered questionnaire for a project"""
    question_service = QuestionGenerationService()
    
    questionnaire = question_service.generate_questionnaire(
        project_name=project_name,
        description=description,
        product_details=product_details,
        target_details=target_details
    )
    
    return questionnaire


@router.post("/validate-responses")
async def validate_questionnaire_responses(
    questionnaire: Dict[str, Any] = Body(..., description="The questionnaire structure"),
    responses: Dict[str, Any] = Body(..., description="User responses to validate")
):
    """Validate questionnaire responses"""
    question_service = QuestionGenerationService()
    
    validation_result = question_service.validate_responses(
        questionnaire=questionnaire,
        responses=responses
    )
    
    return validation_result
