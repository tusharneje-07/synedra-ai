"""
Sentiment Analyzer - Performance Feedback Loop
================================================

Analyzes social media post performance and provides feedback
to agents for continuous learning and improvement.

Features:
- Engagement metrics tracking
- Sentiment score calculation
- Performance trend analysis
- Agent feedback generation
- Learning recommendations

Author: AI Systems Engineer  
Date: February 7, 2026
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from graph import Platform
from db.database import DatabaseManager
from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class SentimentCategory(str, Enum):
    """Sentiment categories."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class PerformanceTier(str, Enum):
    """Performance tiers."""
    VIRAL = "viral"          # Top 5%
    EXCELLENT = "excellent"  # Top 10%
    GOOD = "good"            # Top 25%
    AVERAGE = "average"      # 25-75%
    POOR = "poor"            # Bottom 25%


@dataclass
class EngagementMetrics:
    """Engagement metrics for a post."""
    post_id: str
    platform: Platform
    posted_at: str
    
    # Raw metrics
    likes: int
    comments: int
    shares: int
    views: int
    clicks: int
    saves: int
    
    # Calculated metrics
    engagement_rate: float  # (likes + comments + shares) / views
    viral_coefficient: float  # shares / views
    click_through_rate: float  # clicks / views
    save_rate: float  # saves / views
    
    # Sentiment
    sentiment_score: float  # -1 to 1
    sentiment_category: SentimentCategory
    
    # Performance
    performance_tier: PerformanceTier
    relative_score: float  # 0-100 compared to historical average


@dataclass
class AgentFeedback:
    """Feedback for an agent based on performance."""
    agent_name: str
    post_id: str
    performance_tier: PerformanceTier
    
    # What worked
    successful_patterns: List[str]
    
    # What didn't work
    failed_patterns: List[str]
    
    # Recommendations
    recommendations: List[str]
    
    # Learning points
    learning_points: List[str]
    
    # Confidence adjustment
    confidence_delta: float  # -0.2 to +0.2


class SentimentAnalyzer:
    """
    Analyzes post performance and generates agent feedback.
    
    Creates a feedback loop:
    1. Track post performance
    2. Analyze engagement patterns
    3. Generate agent-specific feedback
    4. Store insights in agent memory
    5. Adjust future decisions
    """
    
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        memory_manager: Optional[MemoryManager] = None
    ):
        """
        Initialize Sentiment Analyzer.
        
        Args:
            db_manager: Database manager
            memory_manager: Memory manager for feedback storage
        """
        self.db = db_manager or DatabaseManager()
        self.memory = memory_manager or MemoryManager()
        
        # Performance baselines (updated over time)
        self.baselines: Dict[Platform, Dict[str, float]] = {
            Platform.INSTAGRAM: {
                'engagement_rate': 0.05,
                'viral_coefficient': 0.01,
                'ctr': 0.02,
                'save_rate': 0.03
            },
            Platform.TWITTER: {
                'engagement_rate': 0.04,
                'viral_coefficient': 0.02,
                'ctr': 0.03,
                'save_rate': 0.01
            },
            Platform.LINKEDIN: {
                'engagement_rate': 0.06,
                'viral_coefficient': 0.005,
                'ctr': 0.04,
                'save_rate': 0.02
            },
            Platform.YOUTUBE: {
                'engagement_rate': 0.08,
                'viral_coefficient': 0.03,
                'ctr': 0.05,
                'save_rate': 0.04
            }
        }
        
        logger.info("SentimentAnalyzer initialized")
    
    def track_post_performance(
        self,
        post_id: str,
        platform: Platform,
        posted_at: str,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        views: int = 1,
        clicks: int = 0,
        saves: int = 0,
        comment_sentiments: List[float] = None
    ) -> EngagementMetrics:
        """
        Track performance metrics for a post.
        
        Args:
            post_id: Unique post identifier
            platform: Platform where posted
            posted_at: ISO timestamp
            likes: Number of likes
            comments: Number of comments
            shares: Number of shares
            views: Number of views
            clicks: Number of clicks
            saves: Number of saves
            comment_sentiments: Sentiment scores of comments (-1 to 1)
            
        Returns:
            Calculated engagement metrics
        """
        # Calculate rates
        total_views = max(views, 1)  # Prevent division by zero
        engagement_rate = (likes + comments + shares) / total_views
        viral_coefficient = shares / total_views
        ctr = clicks / total_views
        save_rate = saves / total_views
        
        # Calculate sentiment
        sentiment_score = self._calculate_sentiment(
            likes=likes,
            comments=comments,
            shares=shares,
            comment_sentiments=comment_sentiments or []
        )
        sentiment_category = self._categorize_sentiment(sentiment_score)
        
        # Calculate performance tier
        performance_tier, relative_score = self._calculate_performance(
            platform=platform,
            engagement_rate=engagement_rate,
            viral_coefficient=viral_coefficient,
            ctr=ctr,
            save_rate=save_rate
        )
        
        metrics = EngagementMetrics(
            post_id=post_id,
            platform=platform,
            posted_at=posted_at,
            likes=likes,
            comments=comments,
            shares=shares,
            views=views,
            clicks=clicks,
            saves=saves,
            engagement_rate=engagement_rate,
            viral_coefficient=viral_coefficient,
            click_through_rate=ctr,
            save_rate=save_rate,
            sentiment_score=sentiment_score,
            sentiment_category=sentiment_category,
            performance_tier=performance_tier,
            relative_score=relative_score
        )
        
        # Store in database
        self._store_metrics(metrics)
        
        logger.info(
            f"Tracked {post_id}: {performance_tier.value}, "
            f"engagement={engagement_rate:.2%}, sentiment={sentiment_score:.2f}"
        )
        
        return metrics
    
    def _calculate_sentiment(
        self,
        likes: int,
        comments: int,
        shares: int,
        comment_sentiments: List[float]
    ) -> float:
        """Calculate overall sentiment score (-1 to 1)."""
        # Positive signals
        positive_weight = (
            likes * 0.5 +      # Likes are mildly positive
            shares * 1.0       # Shares are strongly positive
        )
        
        # Comment sentiment
        if comment_sentiments:
            avg_comment_sentiment = sum(comment_sentiments) / len(comment_sentiments)
            comment_weight = avg_comment_sentiment * len(comment_sentiments) * 0.8
        else:
            # If no sentiment data, assume neutral to mildly positive
            comment_weight = comments * 0.3
        
        total_interactions = max(likes + comments + shares, 1)
        
        # Normalize to -1 to 1
        raw_score = (positive_weight + comment_weight) / (total_interactions * 1.5)
        
        return max(-1.0, min(1.0, raw_score))
    
    def _categorize_sentiment(self, score: float) -> SentimentCategory:
        """Categorize sentiment score."""
        if score >= 0.7:
            return SentimentCategory.VERY_POSITIVE
        elif score >= 0.3:
            return SentimentCategory.POSITIVE
        elif score >= -0.3:
            return SentimentCategory.NEUTRAL
        elif score >= -0.7:
            return SentimentCategory.NEGATIVE
        else:
            return SentimentCategory.VERY_NEGATIVE
    
    def _calculate_performance(
        self,
        platform: Platform,
        engagement_rate: float,
        viral_coefficient: float,
        ctr: float,
        save_rate: float
    ) -> Tuple[PerformanceTier, float]:
        """Calculate performance tier and relative score."""
        baseline = self.baselines.get(platform, self.baselines[Platform.INSTAGRAM])
        
        # Calculate relative performance
        engagement_ratio = engagement_rate / max(baseline['engagement_rate'], 0.001)
        viral_ratio = viral_coefficient / max(baseline['viral_coefficient'], 0.001)
        ctr_ratio = ctr / max(baseline['ctr'], 0.001)
        save_ratio = save_rate / max(baseline['save_rate'], 0.001)
        
        # Weighted average (engagement and virality matter most)
        relative_score = (
            engagement_ratio * 0.4 +
            viral_ratio * 0.3 +
            ctr_ratio * 0.2 +
            save_ratio * 0.1
        ) * 100
        
        # Determine tier
        if relative_score >= 500:  # 5x baseline
            tier = PerformanceTier.VIRAL
        elif relative_score >= 300:  # 3x baseline
            tier = PerformanceTier.EXCELLENT
        elif relative_score >= 150:  # 1.5x baseline
            tier = PerformanceTier.GOOD
        elif relative_score >= 75:  # 0.75x baseline
            tier = PerformanceTier.AVERAGE
        else:
            tier = PerformanceTier.POOR
        
        return tier, relative_score
    
    def generate_agent_feedback(
        self,
        post_id: str,
        metrics: EngagementMetrics,
        agent_proposals: Dict[str, Any]
    ) -> List[AgentFeedback]:
        """
        Generate feedback for agents based on performance.
        
        Args:
            post_id: Post identifier
            metrics: Performance metrics
            agent_proposals: Agent proposals that led to this post
            
        Returns:
            Feedback for each agent
        """
        feedbacks = []
        
        # Analyze patterns based on performance
        successful_patterns = self._identify_successful_patterns(metrics)
        failed_patterns = self._identify_failed_patterns(metrics)
        
        # Generate agent-specific feedback
        for agent_name, proposal in agent_proposals.items():
            feedback = self._create_agent_feedback(
                agent_name=agent_name,
                post_id=post_id,
                metrics=metrics,
                proposal=proposal,
                successful_patterns=successful_patterns,
                failed_patterns=failed_patterns
            )
            
            feedbacks.append(feedback)
            
            # Store in agent memory
            self._store_agent_feedback(feedback)
        
        return feedbacks
    
    def _identify_successful_patterns(
        self,
        metrics: EngagementMetrics
    ) -> List[str]:
        """Identify what worked well."""
        patterns = []
        
        if metrics.performance_tier in [PerformanceTier.VIRAL, PerformanceTier.EXCELLENT]:
            if metrics.viral_coefficient > 0.05:
                patterns.append("High shareability - content resonated deeply")
            if metrics.save_rate > 0.03:
                patterns.append("High save rate - valuable reference content")
            if metrics.click_through_rate > 0.04:
                patterns.append("Strong CTR - compelling call-to-action")
            if metrics.sentiment_score > 0.7:
                patterns.append("Very positive sentiment - emotional connection")
        
        return patterns
    
    def _identify_failed_patterns(
        self,
        metrics: EngagementMetrics
    ) -> List[str]:
        """Identify what didn't work."""
        patterns = []
        
        if metrics.performance_tier == PerformanceTier.POOR:
            if metrics.engagement_rate < 0.02:
                patterns.append("Low engagement - content not compelling")
            if metrics.viral_coefficient < 0.005:
                patterns.append("Low shares - limited viral potential")
            if metrics.click_through_rate < 0.01:
                patterns.append("Weak CTA - unclear next step")
            if metrics.sentiment_score < 0:
                patterns.append("Negative sentiment - messaging issue")
        
        return patterns
    
    def _create_agent_feedback(
        self,
        agent_name: str,
        post_id: str,
        metrics: EngagementMetrics,
        proposal: Any,
        successful_patterns: List[str],
        failed_patterns: List[str]
    ) -> AgentFeedback:
        """Create feedback for specific agent."""
        recommendations = []
        learning_points = []
        confidence_delta = 0.0
        
        # Generate recommendations based on agent role
        if metrics.performance_tier in [PerformanceTier.VIRAL, PerformanceTier.EXCELLENT]:
            recommendations.append(f"Continue this approach - {metrics.performance_tier.value} performance")
            learning_points.append(f"Successful strategy on {metrics.platform.value}")
            confidence_delta = 0.1
            
        elif metrics.performance_tier == PerformanceTier.POOR:
            recommendations.append("Reassess strategy - underperformed baseline")
            learning_points.append(f"Needs improvement on {metrics.platform.value}")
            confidence_delta = -0.1
        
        # Agent-specific recommendations
        if 'trend' in agent_name.lower():
            if metrics.viral_coefficient < 0.01:
                recommendations.append("Trend timing may be off - recalibrate trend detection")
        elif 'engagement' in agent_name.lower():
            if metrics.engagement_rate < 0.03:
                recommendations.append("Low engagement - review content format and CTAs")
        elif 'brand' in agent_name.lower():
            if metrics.sentiment_score < 0.3:
                recommendations.append("Brand perception not strong - refine messaging")
        
        return AgentFeedback(
            agent_name=agent_name,
            post_id=post_id,
            performance_tier=metrics.performance_tier,
            successful_patterns=successful_patterns,
            failed_patterns=failed_patterns,
            recommendations=recommendations,
            learning_points=learning_points,
            confidence_delta=confidence_delta
        )
    
    def _store_agent_feedback(self, feedback: AgentFeedback):
        """Store feedback in agent's memory."""
        feedback_text = (
            f"Performance Feedback for {feedback.post_id}:\n"
            f"- Tier: {feedback.performance_tier.value}\n"
            f"- Successful: {', '.join(feedback.successful_patterns)}\n"
            f"- Failed: {', '.join(feedback.failed_patterns)}\n"
            f"- Recommendations: {', '.join(feedback.recommendations)}\n"
            f"- Learning: {', '.join(feedback.learning_points)}"
        )
        
        # Store in memory with correct signature
        self.memory.store_memory(
            agent_name=feedback.agent_name,
            context=feedback_text,
            decision={'feedback_type': 'performance', 'tier': feedback.performance_tier.value},
            reasoning=f"Post {feedback.post_id} performance analysis",
            outcome=f"Confidence delta: {feedback.confidence_delta}",
            tags=['performance_feedback', feedback.performance_tier.value],
            importance=abs(feedback.confidence_delta)  # Higher for big changes
        )
    
    def _store_metrics(self, metrics: EngagementMetrics):
        """Store metrics in database."""
        try:
            self.db.store_engagement_metrics(
                post_id=metrics.post_id,
                platform=metrics.platform.value,
                engagement_rate=metrics.engagement_rate,
                sentiment_score=metrics.sentiment_score,
                viral_score=metrics.viral_coefficient
            )
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    def get_performance_insights(
        self,
        platform: Optional[Platform] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance insights over time period.
        
        Args:
            platform: Filter by platform
            days: Number of days to analyze
            
        Returns:
            Aggregated insights
        """
        # This would query the database for historical metrics
        # For now, return a placeholder structure
        
        return {
            'time_period_days': days,
            'platform': platform.value if platform else 'all',
            'total_posts': 0,
            'average_engagement_rate': 0.0,
            'average_sentiment_score': 0.0,
            'viral_posts': 0,
            'top_performing_patterns': [],
            'underperforming_patterns': [],
            'trending_topics': [],
            'recommendation': "Collect more data for insights"
        }
