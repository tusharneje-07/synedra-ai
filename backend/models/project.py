"""
Project Database Model
=====================

Stores marketing projects with their details and status.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class Project(Base):
    """
    Project Table
    
    Stores marketing campaign projects with metadata.
    Each project can have multiple sessions and chat messages.
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True, comment="Project brief/overview")
    
    # Project Details
    post_topic = Column(String(500), nullable=True, comment="What to post about")
    product_details = Column(JSON, nullable=True, comment="Product/service information")
    target_details = Column(JSON, nullable=True, comment="Target audience, goals, etc.")
    
    # Questionnaire Responses
    questionnaire_data = Column(JSON, nullable=True, comment="Answers to dynamic questions")
    
    # Brand Association
    brand_config_id = Column(Integer, ForeignKey("brand_configs.id"), nullable=True)
    
    # Status
    status = Column(
        String(50), 
        nullable=False, 
        default="draft",
        comment="draft, active, completed, archived"
    )
    
    # Council Context
    last_session_id = Column(String(255), nullable=True, comment="Last council session ID")
    council_summary = Column(Text, nullable=True, comment="Summary of council decisions")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "post_topic": self.post_topic,
            "product_details": self.product_details,
            "target_details": self.target_details,
            "questionnaire_data": self.questionnaire_data,
            "brand_config_id": self.brand_config_id,
            "status": self.status,
            "last_session_id": self.last_session_id,
            "council_summary": self.council_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
