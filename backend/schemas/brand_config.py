"""
Brand Configuration Schemas
===========================

Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductItem(BaseModel):
    """Single product/service item."""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price_range: Optional[str] = None
    target_segment: Optional[str] = None


class TargetAudienceDetail(BaseModel):
    """Target audience details."""
    demographics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Age, gender, location, income, etc."
    )
    psychographics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Interests, values, lifestyle, pain points"
    )
    behaviors: Optional[List[str]] = Field(
        default=None,
        description="Purchase behaviors, social media usage"
    )


class SocialPlatform(BaseModel):
    """Social media platform configuration."""
    platform: str  # e.g., "Instagram", "Twitter", "LinkedIn"
    handle: Optional[str] = None
    priority: Optional[str] = "medium"  # low, medium, high
    content_types: Optional[List[str]] = None  # e.g., ["image", "video", "carousel"]


class PostingSchedule(BaseModel):
    """Posting frequency per platform."""
    platform: str
    posts_per_week: Optional[int] = None
    best_times: Optional[List[str]] = None  # e.g., ["9:00 AM", "3:00 PM"]


# Request Schemas
class BrandConfigCreate(BaseModel):
    """Schema for creating new brand configuration."""
    brand_name: str = Field(..., min_length=1, max_length=255)
    brand_tone: Optional[str] = Field(None, description="Brand voice: friendly, professional, casual, etc.")
    brand_description: Optional[str] = None
    product_list: Optional[List[Dict[str, Any]]] = None
    target_audience: Optional[Dict[str, Any]] = None
    brand_keywords: Optional[List[str]] = Field(None, description="Core keywords and hashtags")
    messaging_guidelines: Optional[str] = None
    social_platforms: Optional[List[Dict[str, Any]]] = None
    posting_frequency: Optional[List[Dict[str, Any]]] = None
    competitors: Optional[List[str]] = None
    market_segment: Optional[str] = None


class BrandConfigUpdate(BaseModel):
    """Schema for updating brand configuration."""
    brand_name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand_tone: Optional[str] = None
    brand_description: Optional[str] = None
    product_list: Optional[List[Dict[str, Any]]] = None
    target_audience: Optional[Dict[str, Any]] = None
    brand_keywords: Optional[List[str]] = None
    messaging_guidelines: Optional[str] = None
    social_platforms: Optional[List[Dict[str, Any]]] = None
    posting_frequency: Optional[List[Dict[str, Any]]] = None
    competitors: Optional[List[str]] = None
    market_segment: Optional[str] = None
    is_active: Optional[int] = Field(None, ge=0, le=1)


# Response Schemas
class BrandConfigResponse(BaseModel):
    """Schema for brand configuration response."""
    id: int
    brand_name: str
    brand_tone: Optional[str] = None
    brand_description: Optional[str] = None
    product_list: Optional[List[Dict[str, Any]]] = None
    target_audience: Optional[Dict[str, Any]] = None
    brand_keywords: Optional[List[str]] = None
    messaging_guidelines: Optional[str] = None
    social_platforms: Optional[List[Dict[str, Any]]] = None
    posting_frequency: Optional[List[Dict[str, Any]]] = None
    competitors: Optional[List[str]] = None
    market_segment: Optional[str] = None
    is_active: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class BrandConfigListResponse(BaseModel):
    """Schema for listing brand configurations."""
    total: int
    configs: List[BrandConfigResponse]
