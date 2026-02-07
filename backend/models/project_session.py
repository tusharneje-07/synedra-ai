"""
Project Session Database Model
==============================

Tracks individual council sessions within a project.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class ProjectSession(Base):
    """
    Project Session Table
    
    Stores individual council execution sessions for a project.
    Links council decisions to specific projects.
    """
    __tablename__ = "project_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Session Identity
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Project Link
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Session Details
    topic = Column(String(500), nullable=True, comment="Council discussion topic")
    prompt = Column(Text, nullable=True, comment="User's original prompt")
    
    # Results
    decision = Column(Text, nullable=True, comment="Final council decision")
    confidence = Column(Float, nullable=True, comment="Decision confidence score")
    consensus_level = Column(String(50), nullable=True, comment="unanimous, majority, split")
    
    # Metadata
    agents_participated = Column(String(500), nullable=True, comment="Comma-separated agent IDs")
    total_messages = Column(Integer, default=0, comment="Number of chat messages in session")
    
    # Status
    status = Column(
        String(50), 
        nullable=False, 
        default="active",
        comment="active, completed, failed"
    )
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "project_id": self.project_id,
            "topic": self.topic,
            "prompt": self.prompt,
            "decision": self.decision,
            "confidence": self.confidence,
            "consensus_level": self.consensus_level,
            "agents_participated": self.agents_participated,
            "total_messages": self.total_messages,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }
