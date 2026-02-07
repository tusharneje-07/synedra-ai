"""
Brand Configuration Database Model
==================================

Stores brand tone, product list, target audience, and brand keywords.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from database.base import Base


class BrandConfig(Base):
    """
    Brand Configuration Table
    
    Stores:
    - Brand tone/voice
    - Product list
    - Target audience
    - Brand keywords
    """
    __tablename__ = "brand_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Brand Identity
    brand_name = Column(String(255), nullable=False, index=True)
    brand_tone = Column(Text, nullable=True, comment="Brand voice and tone description")
    brand_description = Column(Text, nullable=True, comment="Overall brand description")
    
    # Products
    product_list = Column(JSON, nullable=True, comment="Array of products/services")
    
    # Target Audience
    target_audience = Column(JSON, nullable=True, comment="Target demographics and psychographics")
    
    # Keywords & Messaging
    brand_keywords = Column(JSON, nullable=True, comment="Core brand keywords and hashtags")
    messaging_guidelines = Column(Text, nullable=True, comment="Content guidelines and restrictions")
    
    # Social Media
    social_platforms = Column(JSON, nullable=True, comment="Active social media platforms")
    posting_frequency = Column(JSON, nullable=True, comment="Posting schedule per platform")
    
    # Competition & Market
    competitors = Column(JSON, nullable=True, comment="List of competitor brands")
    market_segment = Column(String(255), nullable=True, comment="Market category/segment")
    
    # Metadata
    is_active = Column(Integer, default=1, comment="1 = active, 0 = inactive")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "brand_name": self.brand_name,
            "brand_tone": self.brand_tone,
            "brand_description": self.brand_description,
            "product_list": self.product_list,
            "target_audience": self.target_audience,
            "brand_keywords": self.brand_keywords,
            "messaging_guidelines": self.messaging_guidelines,
            "social_platforms": self.social_platforms,
            "posting_frequency": self.posting_frequency,
            "competitors": self.competitors,
            "market_segment": self.market_segment,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
