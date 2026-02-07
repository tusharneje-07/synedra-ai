"""
Project Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProjectBase(BaseModel):
    """Base schema for project data"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    post_topic: Optional[str] = Field(None, description="Social media post topic")
    product_details: Optional[Dict[str, Any]] = Field(None, description="Product/service details")
    target_details: Optional[Dict[str, Any]] = Field(None, description="Target audience details")
    brand_config_id: int = Field(..., description="Associated brand configuration ID")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    post_topic: Optional[str] = None
    product_details: Optional[Dict[str, Any]] = None
    target_details: Optional[Dict[str, Any]] = None
    questionnaire_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|completed|archived)$")
    last_session_id: Optional[str] = None
    council_summary: Optional[str] = None


class ProjectQuestionnaireUpdate(BaseModel):
    """Schema for updating questionnaire data"""
    questionnaire_data: Dict[str, Any] = Field(..., description="AI-generated questionnaire responses")


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: int
    status: str
    questionnaire_data: Optional[Dict[str, Any]] = None
    last_session_id: Optional[str] = None
    council_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListItem(BaseModel):
    """Lightweight schema for listing projects"""
    id: int
    name: str
    description: Optional[str]
    status: str
    brand_config_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectSessionCreate(BaseModel):
    """Schema for creating a new project session"""
    topic: str = Field(..., description="Session topic/prompt")
    prompt: Optional[str] = Field(None, description="Full prompt sent to council")


class ProjectSessionResponse(BaseModel):
    """Schema for project session response"""
    id: int
    session_id: str
    project_id: int
    topic: str
    prompt: Optional[str]
    decision: Optional[str]
    confidence: Optional[float]
    consensus_level: Optional[str]
    agents_participated: Optional[str]
    total_messages: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True
