"""
Brand Configuration Service
===========================

Business logic for brand configuration management.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
import logging

from models.brand_config import BrandConfig
from schemas.brand_config import BrandConfigCreate, BrandConfigUpdate

logger = logging.getLogger(__name__)


class BrandConfigService:
    """Service layer for brand configuration operations."""
    
    @staticmethod
    async def create_brand_config(
        db: AsyncSession,
        config_data: BrandConfigCreate
    ) -> BrandConfig:
        """
        Create new brand configuration.
        
        Args:
            db: Database session
            config_data: Brand configuration data
            
        Returns:
            Created BrandConfig instance
        """
        new_config = BrandConfig(
            brand_name=config_data.brand_name,
            brand_tone=config_data.brand_tone,
            brand_description=config_data.brand_description,
            product_list=config_data.product_list,
            target_audience=config_data.target_audience,
            brand_keywords=config_data.brand_keywords,
            messaging_guidelines=config_data.messaging_guidelines,
            social_platforms=config_data.social_platforms,
            posting_frequency=config_data.posting_frequency,
            competitors=config_data.competitors,
            market_segment=config_data.market_segment,
        )
        
        db.add(new_config)
        await db.commit()
        await db.refresh(new_config)
        
        logger.info(f"Created brand config: {new_config.brand_name} (ID: {new_config.id})")
        return new_config
    
    @staticmethod
    async def get_brand_config(db: AsyncSession, config_id: int) -> Optional[BrandConfig]:
        """
        Get brand configuration by ID.
        
        Args:
            db: Database session
            config_id: Configuration ID
            
        Returns:
            BrandConfig instance or None
        """
        result = await db.execute(
            select(BrandConfig).where(BrandConfig.id == config_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_active_brand_config(db: AsyncSession) -> Optional[BrandConfig]:
        """
        Get currently active brand configuration.
        
        Returns:
            Active BrandConfig instance or None
        """
        result = await db.execute(
            select(BrandConfig)
            .where(BrandConfig.is_active == 1)
            .order_by(BrandConfig.updated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_brand_configs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[BrandConfig]:
        """
        List brand configurations.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Return only active configurations
            
        Returns:
            List of BrandConfig instances
        """
        query = select(BrandConfig).order_by(BrandConfig.updated_at.desc())
        
        if active_only:
            query = query.where(BrandConfig.is_active == 1)
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_brand_config(
        db: AsyncSession,
        config_id: int,
        config_data: BrandConfigUpdate
    ) -> Optional[BrandConfig]:
        """
        Update brand configuration.
        
        Args:
            db: Database session
            config_id: Configuration ID
            config_data: Updated configuration data
            
        Returns:
            Updated BrandConfig instance or None
        """
        # Get existing config
        config = await BrandConfigService.get_brand_config(db, config_id)
        if not config:
            return None
        
        # Update fields
        update_data = config_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(config, key, value)
        
        await db.commit()
        await db.refresh(config)
        
        logger.info(f"Updated brand config ID: {config_id}")
        return config
    
    @staticmethod
    async def delete_brand_config(db: AsyncSession, config_id: int) -> bool:
        """
        Delete brand configuration.
        
        Args:
            db: Database session
            config_id: Configuration ID
            
        Returns:
            True if deleted, False if not found
        """
        config = await BrandConfigService.get_brand_config(db, config_id)
        if not config:
            return False
        
        await db.delete(config)
        await db.commit()
        
        logger.info(f"Deleted brand config ID: {config_id}")
        return True
    
    @staticmethod
    async def set_active_config(db: AsyncSession, config_id: int) -> Optional[BrandConfig]:
        """
        Set a configuration as active (deactivate others).
        
        Args:
            db: Database session
            config_id: Configuration ID to activate
            
        Returns:
            Activated BrandConfig instance or None
        """
        # Deactivate all configs
        await db.execute(
            update(BrandConfig).values(is_active=0)
        )
        
        # Activate specified config
        config = await BrandConfigService.get_brand_config(db, config_id)
        if not config:
            await db.rollback()
            return None
        
        config.is_active = 1
        await db.commit()
        await db.refresh(config)
        
        logger.info(f"Set active brand config ID: {config_id}")
        return config
