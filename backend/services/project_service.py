"""
Project Service - Business logic for project management
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from datetime import datetime

from models.project import Project
from models.project_session import ProjectSession
from models.chat_message import ChatMessage
from schemas.project import ProjectCreate, ProjectUpdate, ProjectQuestionnaireUpdate


class ProjectService:
    """Service for managing projects"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_project(self, project_data: ProjectCreate) -> Project:
        """Create a new project"""
        project = Project(
            name=project_data.name,
            description=project_data.description,
            post_topic=project_data.post_topic,
            product_details=project_data.product_details,
            target_details=project_data.target_details,
            brand_config_id=project_data.brand_config_id,
            status="draft"
        )
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def list_projects(
        self, 
        brand_config_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """List projects with optional filtering"""
        query = select(Project).order_by(Project.updated_at.desc())
        
        if brand_config_id is not None:
            query = query.where(Project.brand_config_id == brand_config_id)
        
        if status is not None:
            query = query.where(Project.status == status)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_project(
        self, 
        project_id: int, 
        project_data: ProjectUpdate
    ) -> Optional[Project]:
        """Update a project"""
        project = await self.get_project(project_id)
        if not project:
            return None
        
        update_data = project_data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(project, key, value)
        
        project.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def update_questionnaire(
        self,
        project_id: int,
        questionnaire_data: ProjectQuestionnaireUpdate
    ) -> Optional[Project]:
        """Update project questionnaire data"""
        project = await self.get_project(project_id)
        if not project:
            return None
        
        project.questionnaire_data = questionnaire_data.questionnaire_data
        project.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def delete_project(self, project_id: int) -> bool:
        """Delete a project and all associated sessions and messages"""
        project = await self.get_project(project_id)
        if not project:
            return False
        
        # Delete associated chat messages
        await self.db.execute(
            delete(ChatMessage).where(ChatMessage.project_id == project_id)
        )
        
        # Delete associated sessions
        await self.db.execute(
            delete(ProjectSession).where(ProjectSession.project_id == project_id)
        )
        
        # Delete the project
        await self.db.delete(project)
        await self.db.commit()
        
        return True
    
    async def create_session(
        self,
        project_id: int,
        session_id: str,
        topic: str,
        prompt: Optional[str] = None
    ) -> Optional[ProjectSession]:
        """Create a new project session"""
        project = await self.get_project(project_id)
        if not project:
            return None
        
        session = ProjectSession(
            session_id=session_id,
            project_id=project_id,
            topic=topic,
            prompt=prompt,
            status="active"
        )
        
        self.db.add(session)
        
        # Update project's last session ID
        project.last_session_id = session_id
        project.status = "active"
        project.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[ProjectSession]:
        """Get a session by session_id"""
        result = await self.db.execute(
            select(ProjectSession).where(ProjectSession.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def update_session(
        self,
        session_id: str,
        decision: Optional[str] = None,
        confidence: Optional[float] = None,
        consensus_level: Optional[str] = None,
        agents_participated: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[ProjectSession]:
        """Update a project session"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        if decision is not None:
            session.decision = decision
        if confidence is not None:
            session.confidence = confidence
        if consensus_level is not None:
            session.consensus_level = consensus_level
        if agents_participated is not None:
            session.agents_participated = agents_participated
        if status is not None:
            session.status = status
            if status == "completed" or status == "failed":
                session.ended_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def get_project_sessions(
        self,
        project_id: int,
        limit: int = 10
    ) -> List[ProjectSession]:
        """Get recent sessions for a project"""
        result = await self.db.execute(
            select(ProjectSession)
            .where(ProjectSession.project_id == project_id)
            .order_by(ProjectSession.started_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_project_messages(
        self,
        project_id: int,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ChatMessage]:
        """Get messages for a project, optionally filtered by session"""
        query = (
            select(ChatMessage)
            .where(ChatMessage.project_id == project_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        
        if session_id:
            query = query.where(ChatMessage.session_id == session_id)
        
        result = await self.db.execute(query)
        messages = list(result.scalars().all())
        
        # Return in chronological order
        return list(reversed(messages))
