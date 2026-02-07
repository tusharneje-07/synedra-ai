"""
Trend Monitor - Viral Opportunity Detection
============================================

Monitors trends across platforms and triggers council analysis for opportunities.

Features:
- Platform trend tracking
- Viral opportunity detection
- Relevance scoring
- Automatic council triggering

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from graph import Platform

logger = logging.getLogger(__name__)


@dataclass
class TrendOpportunity:
    """Represents a detected trend opportunity."""
    trend_id: str
    platform: Platform
    topic: str
    keywords: List[str]
    relevance_score: float  # 0-1
    virality_potential: float  # 0-1
    velocity: float  # Growth rate
    volume: int  # Mention count
    detected_at: str
    expires_at: str
    urgency: str  # low, medium, high
    metadata: Dict[str, Any]


class TrendMonitor:
    """
    Monitors social media trends and detects opportunities.
    
    In production, this would integrate with:
    - Twitter Trending API
    - Google Trends API
    - Instagram Hashtag tracking
    - TikTok trending sounds
    - Reddit trending posts
    """
    
    def __init__(
        self,
        platforms: List[Platform] = None,
        relevance_threshold: float = 0.6,
        check_interval_minutes: int = 15
    ):
        """
        Initialize Trend Monitor.
        
        Args:
            platforms: Platforms to monitor (default: all)
            relevance_threshold: Minimum relevance score to trigger
            check_interval_minutes: How often to check trends
        """
        self.platforms = platforms or list(Platform)
        self.relevance_threshold = relevance_threshold
        self.check_interval = timedelta(minutes=check_interval_minutes)
        
        self.tracked_trends: Dict[str, TrendOpportunity] = {}
        self.last_check: Optional[datetime] = None
        
        logger.info(
            f"TrendMonitor initialized: {len(self.platforms)} platforms, "
            f"threshold={relevance_threshold}"
        )
    
    def scan_trends(
        self,
        brand_keywords: List[str] = None,
        industry_keywords: List[str] = None
    ) -> List[TrendOpportunity]:
        """
        Scan all platforms for relevant trends.
        
        Args:
            brand_keywords: Keywords related to brand
            industry_keywords: Keywords for industry
            
        Returns:
            List of detected opportunities
        """
        logger.info("Scanning trends across platforms")
        
        opportunities = []
        
        for platform in self.platforms:
            platform_trends = self._scan_platform(
                platform=platform,
                brand_keywords=brand_keywords,
                industry_keywords=industry_keywords
            )
            opportunities.extend(platform_trends)
        
        # Filter by relevance
        filtered = [
            opp for opp in opportunities
            if opp.relevance_score >= self.relevance_threshold
        ]
        
        # Sort by urgency and virality
        filtered.sort(
            key=lambda x: (x.urgency == 'high', x.virality_potential),
            reverse=True
        )
        
        # Update tracking
        for opp in filtered:
            self.tracked_trends[opp.trend_id] = opp
        
        self.last_check = datetime.now()
        
        logger.info(f"Scan complete: {len(filtered)} opportunities found")
        
        return filtered
    
    def _scan_platform(
        self,
        platform: Platform,
        brand_keywords: List[str] = None,
        industry_keywords: List[str] = None
    ) -> List[TrendOpportunity]:
        """
        Scan a specific platform for trends.
        
        In production, this would call actual platform APIs.
        For now, returns mock data for testing.
        """
        # Mock implementation - in production, call actual APIs
        logger.debug(f"Scanning {platform.value}")
        
        # Example mock trends
        mock_trends = []
        
        # This would be replaced with real API calls
        if platform == Platform.TWITTER:
            mock_trends = self._get_mock_twitter_trends()
        elif platform == Platform.INSTAGRAM:
            mock_trends = self._get_mock_instagram_trends()
        
        # Score relevance
        scored = []
        for trend in mock_trends:
            relevance = self._calculate_relevance(
                trend=trend,
                brand_keywords=brand_keywords or [],
                industry_keywords=industry_keywords or []
            )
            
            if relevance > 0:
                trend['relevance_score'] = relevance
                scored.append(self._create_opportunity(trend))
        
        return scored
    
    def _get_mock_twitter_trends(self) -> List[Dict[str, Any]]:
        """Mock Twitter trends for testing."""
        return [
            {
                'topic': 'AI product launches',
                'keywords': ['AI', 'product', 'launch', 'tech'],
                'volume': 15000,
                'velocity': 2.5,
                'virality_potential': 0.85
            },
            {
                'topic': 'Marketing automation',
                'keywords': ['marketing', 'automation', 'AI', 'tools'],
                'volume': 8000,
                'velocity': 1.8,
                'virality_potential': 0.7
            }
        ]
    
    def _get_mock_instagram_trends(self) -> List[Dict[str, Any]]:
        """Mock Instagram trends for testing."""
        return [
            {
                'topic': 'Behind the scenes content',
                'keywords': ['BTS', 'authentic', 'real', 'brand'],
                'volume': 25000,
                'velocity': 3.2,
                'virality_potential': 0.9
            }
        ]
    
    def _calculate_relevance(
        self,
        trend: Dict[str, Any],
        brand_keywords: List[str],
        industry_keywords: List[str]
    ) -> float:
        """
        Calculate how relevant a trend is to the brand.
        
        Args:
            trend: Trend data
            brand_keywords: Brand-related keywords
            industry_keywords: Industry keywords
            
        Returns:
            Relevance score 0-1
        """
        trend_keywords = set(k.lower() for k in trend.get('keywords', []))
        brand_kw = set(k.lower() for k in brand_keywords)
        industry_kw = set(k.lower() for k in industry_keywords)
        
        # Calculate overlap
        brand_overlap = len(trend_keywords & brand_kw) / max(len(brand_kw), 1)
        industry_overlap = len(trend_keywords & industry_kw) / max(len(industry_kw), 1)
        
        # Weighted relevance
        relevance = (brand_overlap * 0.6) + (industry_overlap * 0.4)
        
        return min(relevance, 1.0)
    
    def _create_opportunity(self, trend: Dict[str, Any]) -> TrendOpportunity:
        """Create TrendOpportunity from trend data."""
        now = datetime.now()
        
        # Determine urgency based on velocity
        velocity = trend.get('velocity', 1.0)
        if velocity > 3.0:
            urgency = 'high'
        elif velocity > 1.5:
            urgency = 'medium'
        else:
            urgency = 'low'
        
        # Calculate expiration (trends decay quickly)
        hours_valid = 24 / max(velocity, 0.5)
        expires_at = now + timedelta(hours=hours_valid)
        
        trend_id = f"trend_{now.strftime('%Y%m%d_%H%M%S')}_{trend['topic'][:20]}"
        
        return TrendOpportunity(
            trend_id=trend_id,
            platform=Platform.TWITTER,  # Would be passed from caller
            topic=trend['topic'],
            keywords=trend.get('keywords', []),
            relevance_score=trend.get('relevance_score', 0),
            virality_potential=trend.get('virality_potential', 0.5),
            velocity=velocity,
            volume=trend.get('volume', 0),
            detected_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
            urgency=urgency,
            metadata=trend
        )
    
    def should_trigger_council(
        self,
        opportunity: TrendOpportunity
    ) -> bool:
        """
        Decide if opportunity should trigger council analysis.
        
        Args:
            opportunity: Detected opportunity
            
        Returns:
            True if council should analyze
        """
        # Trigger if high relevance and virality
        if opportunity.relevance_score >= 0.8 and opportunity.virality_potential >= 0.8:
            return True
        
        # Trigger if high urgency
        if opportunity.urgency == 'high' and opportunity.relevance_score >= 0.6:
            return True
        
        return False
    
    def get_trending_topics(
        self,
        platform: Optional[Platform] = None,
        top_n: int = 10
    ) -> List[TrendOpportunity]:
        """
        Get top trending opportunities.
        
        Args:
            platform: Filter by platform (None = all)
            top_n: Number to return
            
        Returns:
            Top trending opportunities
        """
        trends = list(self.tracked_trends.values())
        
        # Filter by platform if specified
        if platform:
            trends = [t for t in trends if t.platform == platform]
        
        # Sort by virality potential
        trends.sort(key=lambda x: x.virality_potential, reverse=True)
        
        return trends[:top_n]
    
    def is_trend_expired(self, trend_id: str) -> bool:
        """Check if a trend has expired."""
        trend = self.tracked_trends.get(trend_id)
        
        if not trend:
            return True
        
        expires_at = datetime.fromisoformat(trend.expires_at)
        return datetime.now() > expires_at
    
    def cleanup_expired_trends(self) -> int:
        """Remove expired trends from tracking."""
        expired_ids = [
            tid for tid in self.tracked_trends.keys()
            if self.is_trend_expired(tid)
        ]
        
        for tid in expired_ids:
            del self.tracked_trends[tid]
        
        logger.info(f"Cleaned up {len(expired_ids)} expired trends")
        
        return len(expired_ids)
    
    def get_monitor_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            'platforms_monitored': len(self.platforms),
            'active_trends': len(self.tracked_trends),
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'relevance_threshold': self.relevance_threshold,
            'check_interval_minutes': self.check_interval.total_seconds() / 60
        }
