"""
Autonomous AI Council - Main Entry Point
=========================================

Fully autonomous, debate-driven, multi-agent AI council for social media
strategy and content generation.

Usage:
    # Start autonomous execution
    python main.py --mode auto --interval 30 --brand "Your Brand"
    
    # Manual council trigger
    python main.py --mode manual --topic "AI Innovation" --platform instagram
    
    # Check status
    python main.py --status
    
    # Run single cycle
    python main.py --mode once

Author: AI Systems Engineer
Date: February 7, 2026
"""

import asyncio
import argparse
import logging
import sys
from typing import Optional
from datetime import datetime

from config import Settings
from db.database import DatabaseManager
from graph import CouncilGraph, Platform
from pipeline import (
    TrendMonitor,
    ContentGenerator,
    AutonomousScheduler,
    SentimentAnalyzer
)
from pipeline.scheduler import ScheduleMode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('council.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AutonomousCouncil:
    """
    Main orchestrator for the autonomous AI council system.
    
    Coordinates:
    - Trend monitoring
    - Council deliberations
    - Content generation
    - Performance tracking
    - Autonomous execution
    """
    
    def __init__(
        self,
        brand_name: Optional[str] = None,
        brand_keywords: Optional[list] = None,
        industry_keywords: Optional[list] = None
    ):
        """
        Initialize Autonomous Council.
        
        Args:
            brand_name: Your brand name
            brand_keywords: Keywords related to your brand
            industry_keywords: Industry keywords for trend filtering
        """
        self.settings = Settings()
        
        # Brand configuration
        self.brand_name = brand_name or "Your Brand"
        self.brand_keywords = brand_keywords or ["AI", "innovation"]
        self.industry_keywords = industry_keywords or ["technology", "software"]
        
        # Initialize components
        logger.info("Initializing Autonomous Council components...")
        
        self.db = DatabaseManager()
        self.council = CouncilGraph(auto_create_agents=True)
        self.trend_monitor = TrendMonitor()
        self.content_generator = ContentGenerator()
        self.sentiment_analyzer = SentimentAnalyzer(
            db_manager=self.db
        )
        
        self.scheduler = None
        
        logger.info(f"✓ Council initialized for: {self.brand_name}")
        logger.info(f"  Brand keywords: {', '.join(self.brand_keywords)}")
        logger.info(f"  Industry keywords: {', '.join(self.industry_keywords)}")
    
    async def start_autonomous(
        self,
        mode: ScheduleMode = ScheduleMode.INTERVAL,
        interval_minutes: int = 30
    ):
        """
        Start autonomous execution.
        
        Args:
            mode: Execution mode (CONTINUOUS, INTERVAL, TRIGGERED)
            interval_minutes: Interval between cycles (for INTERVAL mode)
        """
        logger.info("=" * 70)
        logger.info("STARTING AUTONOMOUS AI COUNCIL")
        logger.info("=" * 70)
        
        self.scheduler = AutonomousScheduler(
            council_graph=self.council,
            trend_monitor=self.trend_monitor,
            content_generator=self.content_generator,
            db_manager=self.db,
            mode=mode,
            interval_minutes=interval_minutes
        )
        
        try:
            await self.scheduler.start(
                brand_keywords=self.brand_keywords,
                industry_keywords=self.industry_keywords
            )
        except KeyboardInterrupt:
            logger.info("\n⚠️  Received shutdown signal")
            self.scheduler.stop()
            logger.info("✓ Autonomous execution stopped gracefully")
        except Exception as e:
            logger.error(f"❌ Error during autonomous execution: {e}")
            raise
    
    async def run_single_cycle(self):
        """Run a single execution cycle."""
        logger.info("=" * 70)
        logger.info("RUNNING SINGLE EXECUTION CYCLE")
        logger.info("=" * 70)
        
        scheduler = AutonomousScheduler(
            council_graph=self.council,
            trend_monitor=self.trend_monitor,
            content_generator=self.content_generator,
            db_manager=self.db,
            mode=ScheduleMode.MANUAL
        )
        
        cycle = await scheduler.execute_cycle(
            brand_keywords=self.brand_keywords,
            industry_keywords=self.industry_keywords
        )
        
        logger.info("=" * 70)
        logger.info("CYCLE COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Status: {cycle.status}")
        logger.info(f"Trends detected: {cycle.trends_detected}")
        logger.info(f"Councils triggered: {cycle.councils_triggered}")
        logger.info(f"Content generated: {cycle.content_generated}")
        logger.info(f"Duration: {cycle.duration_seconds:.1f}s")
        
        if cycle.errors:
            logger.warning(f"Errors: {len(cycle.errors)}")
            for error in cycle.errors:
                logger.warning(f"  - {error}")
        
        return cycle
    
    def manual_trigger(
        self,
        topic: str,
        platform: Platform = Platform.INSTAGRAM,
        context: dict = None
    ):
        """
        Manually trigger council analysis for a topic.
        
        Args:
            topic: Topic to analyze
            platform: Target platform
            context: Additional context
            
        Returns:
            Council decision and generated content
        """
        logger.info("=" * 70)
        logger.info(f"MANUAL TRIGGER: {topic}")
        logger.info("=" * 70)
        
        scheduler = AutonomousScheduler(
            council_graph=self.council,
            trend_monitor=self.trend_monitor,
            content_generator=self.content_generator,
            db_manager=self.db,
            mode=ScheduleMode.MANUAL
        )
        
        result = scheduler.manual_trigger(
            topic=topic,
            platform=platform,
            context=context or {}
        )
        
        logger.info("=" * 70)
        logger.info("COUNCIL DECISION")
        logger.info("=" * 70)
        logger.info(f"Decision: {result['decision']}")
        
        if result['content']:
            logger.info(f"\nContent generated for {len(result['content'].variants)} platform(s):")
            for platform, piece in result['content'].variants.items():
                logger.info(f"\n{platform.value.upper()}:")
                logger.info(f"  Text: {piece.primary_text[:100]}...")
                logger.info(f"  Hashtags: {', '.join(piece.hashtags[:5])}")
                logger.info(f"  Est. Engagement: {piece.estimated_engagement:.2%}")
        
        return result
    
    def get_status(self):
        """Get current system status."""
        logger.info("=" * 70)
        logger.info("SYSTEM STATUS")
        logger.info("=" * 70)
        
        if self.scheduler and self.scheduler.is_running:
            stats = self.scheduler.get_execution_stats()
            
            logger.info(f"Status: RUNNING ({stats['mode']})")
            logger.info(f"Total cycles: {stats['total_cycles']}")
            logger.info(f"Success rate: {stats['success_rate']:.1%}")
            logger.info(f"Trends detected: {stats['total_trends_detected']}")
            logger.info(f"Councils triggered: {stats['total_councils_triggered']}")
            logger.info(f"Content generated: {stats['total_content_generated']}")
            logger.info(f"Avg cycle duration: {stats['average_cycle_duration_seconds']:.1f}s")
            
            # Show recent cycles
            recent = self.scheduler.get_recent_cycles(count=3)
            if recent:
                logger.info(f"\nRecent cycles ({len(recent)}):")
                for cycle in recent:
                    logger.info(f"  {cycle.cycle_id}: {cycle.status} - "
                              f"{cycle.councils_triggered} councils, "
                              f"{cycle.content_generated} content")
        else:
            logger.info("Status: STOPPED")
            logger.info("Use --mode auto to start autonomous execution")
        
        logger.info("=" * 70)
    
    def track_performance(
        self,
        post_id: str,
        platform: Platform,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        views: int = 1,
        clicks: int = 0,
        saves: int = 0
    ):
        """
        Track performance of a posted content.
        
        Args:
            post_id: Unique post identifier
            platform: Platform where posted
            likes: Number of likes
            comments: Number of comments
            shares: Number of shares
            views: Number of views
            clicks: Number of clicks
            saves: Number of saves
        """
        logger.info(f"Tracking performance for post: {post_id}")
        
        metrics = self.sentiment_analyzer.track_post_performance(
            post_id=post_id,
            platform=platform,
            posted_at=datetime.now().isoformat(),
            likes=likes,
            comments=comments,
            shares=shares,
            views=views,
            clicks=clicks,
            saves=saves
        )
        
        logger.info(f"Performance tier: {metrics.performance_tier.value}")
        logger.info(f"Engagement rate: {metrics.engagement_rate:.2%}")
        logger.info(f"Sentiment: {metrics.sentiment_category.value} ({metrics.sentiment_score:.2f})")
        
        return metrics


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous AI Council for Social Media Strategy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start autonomous execution (checks every 30 minutes)
  python main.py --mode auto --interval 30 --brand "TechCorp"
  
  # Run single cycle
  python main.py --mode once
  
  # Manual trigger
  python main.py --mode manual --topic "AI Innovation" --platform instagram
  
  # Check status
  python main.py --status
  
  # Track post performance
  python main.py --track --post-id "post123" --platform instagram --likes 500 --views 10000
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['auto', 'continuous', 'once', 'manual'],
        help='Execution mode'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Interval in minutes for auto mode (default: 30)'
    )
    
    parser.add_argument(
        '--brand',
        help='Your brand name'
    )
    
    parser.add_argument(
        '--brand-keywords',
        nargs='+',
        help='Brand keywords (space-separated)'
    )
    
    parser.add_argument(
        '--industry-keywords',
        nargs='+',
        help='Industry keywords (space-separated)'
    )
    
    parser.add_argument(
        '--topic',
        help='Topic for manual trigger'
    )
    
    parser.add_argument(
        '--platform',
        choices=['instagram', 'twitter', 'linkedin', 'youtube'],
        default='instagram',
        help='Target platform (default: instagram)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status'
    )
    
    parser.add_argument(
        '--track',
        action='store_true',
        help='Track post performance'
    )
    
    parser.add_argument('--post-id', help='Post ID for tracking')
    parser.add_argument('--likes', type=int, default=0)
    parser.add_argument('--comments', type=int, default=0)
    parser.add_argument('--shares', type=int, default=0)
    parser.add_argument('--views', type=int, default=1)
    parser.add_argument('--clicks', type=int, default=0)
    parser.add_argument('--saves', type=int, default=0)
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()
    
    # Initialize council
    council = AutonomousCouncil(
        brand_name=args.brand,
        brand_keywords=args.brand_keywords,
        industry_keywords=args.industry_keywords
    )
    
    # Status check
    if args.status:
        council.get_status()
        return
    
    # Performance tracking
    if args.track:
        if not args.post_id:
            logger.error("--post-id required for tracking")
            sys.exit(1)
        
        platform_map = {
            'instagram': Platform.INSTAGRAM,
            'twitter': Platform.TWITTER,
            'linkedin': Platform.LINKEDIN,
            'youtube': Platform.YOUTUBE
        }
        
        council.track_performance(
            post_id=args.post_id,
            platform=platform_map[args.platform],
            likes=args.likes,
            comments=args.comments,
            shares=args.shares,
            views=args.views,
            clicks=args.clicks,
            saves=args.saves
        )
        return
    
    # Execution modes
    if args.mode == 'auto':
        await council.start_autonomous(
            mode=ScheduleMode.INTERVAL,
            interval_minutes=args.interval
        )
    
    elif args.mode == 'continuous':
        await council.start_autonomous(
            mode=ScheduleMode.CONTINUOUS,
            interval_minutes=1
        )
    
    elif args.mode == 'once':
        await council.run_single_cycle()
    
    elif args.mode == 'manual':
        if not args.topic:
            logger.error("--topic required for manual mode")
            sys.exit(1)
        
        platform_map = {
            'instagram': Platform.INSTAGRAM,
            'twitter': Platform.TWITTER,
            'linkedin': Platform.LINKEDIN,
            'youtube': Platform.YOUTUBE
        }
        
        council.manual_trigger(
            topic=args.topic,
            platform=platform_map[args.platform]
        )
    
    else:
        logger.error("Please specify a mode: --mode auto|continuous|once|manual or use --status")
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✓ Shutdown complete")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
