"""
Brand Configuration Routes
==========================

REST APIs for managing brand configuration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.base import get_db
from schemas.brand_config import (
    BrandConfigCreate,
    BrandConfigUpdate,
    BrandConfigResponse,
    BrandConfigListResponse
)
from services.brand_config import BrandConfigService

router = APIRouter()


@router.get("/brand/active", response_model=BrandConfigResponse)
async def get_active_brand_config(db: AsyncSession = Depends(get_db)):
    """
    Get currently active brand configuration.
    
    Returns the brand config marked as active for use by AI agents.
    """
    config = await BrandConfigService.get_active_brand_config(db)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active brand configuration found"
        )
    
    return config.to_dict()


@router.get("/brand/{config_id}", response_model=BrandConfigResponse)
async def get_brand_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get brand configuration by ID.
    
    Args:
        config_id: Brand configuration ID
    """
    config = await BrandConfigService.get_brand_config(db, config_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand configuration with ID {config_id} not found"
        )
    
    return config.to_dict()


@router.get("/brand", response_model=BrandConfigListResponse)
async def list_brand_configs(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    List all brand configurations.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        active_only: Return only active configurations
    """
    configs = await BrandConfigService.list_brand_configs(db, skip, limit, active_only)
    
    return {
        "total": len(configs),
        "configs": [config.to_dict() for config in configs]
    }


@router.post("/brand", response_model=BrandConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_brand_config(
    config_data: BrandConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new brand configuration.
    
    Args:
        config_data: Brand configuration data
    """
    config = await BrandConfigService.create_brand_config(db, config_data)
    return config.to_dict()


@router.put("/brand/{config_id}", response_model=BrandConfigResponse)
async def update_brand_config(
    config_id: int,
    config_data: BrandConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update brand configuration.
    
    Args:
        config_id: Brand configuration ID
        config_data: Updated configuration data
    """
    config = await BrandConfigService.update_brand_config(db, config_id, config_data)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand configuration with ID {config_id} not found"
        )
    
    return config.to_dict()


@router.delete("/brand/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete brand configuration.
    
    Args:
        config_id: Brand configuration ID
    """
    success = await BrandConfigService.delete_brand_config(db, config_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand configuration with ID {config_id} not found"
        )
    
    return None


@router.post("/brand/{config_id}/activate", response_model=BrandConfigResponse)
async def activate_brand_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Set brand configuration as active (deactivates all others).
    
    Args:
        config_id: Brand configuration ID to activate
    """
    config = await BrandConfigService.set_active_config(db, config_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand configuration with ID {config_id} not found"
        )
    
    return config.to_dict()
