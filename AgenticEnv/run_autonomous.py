#!/usr/bin/env python3
"""
Simple Runner for Autonomous AI Council
========================================

Quick start script for autonomous execution.

Usage:
    python run_autonomous.py
    
Or make executable and run:
    chmod +x run_autonomous.py
    ./run_autonomous.py

Author: AI Systems Engineer
Date: February 7, 2026
"""

import asyncio
import logging
from main import AutonomousCouncil
from pipeline.scheduler import ScheduleMode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def run():
    """Run autonomous council with default configuration."""
    
    # Configuration - CUSTOMIZE THESE
    BRAND_NAME = "YourBrand"
    BRAND_KEYWORDS = ["AI", "automation", "innovation"]
    INDUSTRY_KEYWORDS = ["technology", "software", "SaaS"]
    INTERVAL_MINUTES = 30  # Check for trends every 30 minutes
    
    logger.info("🚀 Starting Autonomous AI Council")
    logger.info(f"   Brand: {BRAND_NAME}")
    logger.info(f"   Checking trends every {INTERVAL_MINUTES} minutes")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    # Initialize council
    council = AutonomousCouncil(
        brand_name=BRAND_NAME,
        brand_keywords=BRAND_KEYWORDS,
        industry_keywords=INDUSTRY_KEYWORDS
    )
    
    # Start autonomous execution
    try:
        await council.start_autonomous(
            mode=ScheduleMode.INTERVAL,
            interval_minutes=INTERVAL_MINUTES
        )
    except KeyboardInterrupt:
        logger.info("\n✓ Stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(run())
