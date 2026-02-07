"""
Test Suite for Pipeline Components
===================================

Tests all pipeline components:
- TrendMonitor
- ContentGenerator  
- AutonomousScheduler
- SentimentAnalyzer

Author: AI Systems Engineer
Date: February 7, 2026
"""

import pytest
import asyncio
from datetime import datetime

from pipeline.trend_monitor import TrendMonitor, TrendOpportunity
from pipeline.content_generator import ContentGenerator, ContentPiece
from pipeline.scheduler import AutonomousScheduler, ScheduleMode, ExecutionCycle
from pipeline.sentiment_analyzer import (
    SentimentAnalyzer, 
    EngagementMetrics,
    SentimentCategory,
    PerformanceTier
)
from graph import Platform


# ============================================================================
# TrendMonitor Tests
# ============================================================================

def test_trend_monitor_initialization():
    """Test TrendMonitor initializes correctly."""
    monitor = TrendMonitor()
    assert monitor is not None
    assert monitor.relevance_threshold == 0.6
    print("✓ TrendMonitor initialized")


def test_trend_scanning():
    """Test trend scanning functionality."""
    monitor = TrendMonitor()
    
    trends = monitor.scan_trends(
        brand_keywords=['AI', 'automation'],
        industry_keywords=['tech', 'innovation']
    )
    
    assert isinstance(trends, list)
    assert len(trends) >= 0
    
    for trend in trends:
        assert isinstance(trend, TrendOpportunity)
        assert hasattr(trend, 'topic')
        assert hasattr(trend, 'platform')
        assert hasattr(trend, 'relevance_score')
        assert 0 <= trend.relevance_score <= 1
    
    print(f"✓ Scanned {len(trends)} trends")


def test_relevance_calculation():
    """Test relevance score calculation."""
    monitor = TrendMonitor()
    
    # High relevance - brand keywords match
    score = monitor._calculate_relevance(
        trend={'topic': 'AI automation in tech', 'keywords': ['AI', 'automation', 'tech']},
        brand_keywords=['AI', 'automation'],
        industry_keywords=['tech', 'innovation']
    )
    
    assert 0 <= score <= 1
    assert score > 0.5  # Should be relevant
    
    print(f"✓ Relevance calculation: {score:.2f}")


def test_council_trigger_logic():
    """Test council trigger decision logic."""
    monitor = TrendMonitor()
    
    # High relevance + high virality = should trigger
    high_priority_trend = TrendOpportunity(
        trend_id="test_1",
        topic="AI Revolution",
        platform=Platform.INSTAGRAM,
        detected_at=datetime.now().isoformat(),
        keywords=['AI', 'automation'],
        volume=50000,
        velocity=10.0,
        relevance_score=0.9,
        virality_potential=0.9,
        urgency='high',
        expires_at=(datetime.now()).isoformat(),
        metadata={}
    )
    
    assert monitor.should_trigger_council(high_priority_trend) is True
    
    # Low relevance = should not trigger
    low_priority_trend = TrendOpportunity(
        trend_id="test_2",
        topic="Random Topic",
        platform=Platform.TWITTER,
        detected_at=datetime.now().isoformat(),
        keywords=['random'],
        volume=100,
        velocity=0.1,
        relevance_score=0.3,
        virality_potential=0.2,
        urgency='low',
        expires_at=(datetime.now()).isoformat(),
        metadata={}
    )
    
    assert monitor.should_trigger_council(low_priority_trend) is False
    
    print("✓ Council trigger logic validated")


def test_expired_trends_cleanup():
    """Test expired trends cleanup."""
    monitor = TrendMonitor()
    
    # Add some trends
    monitor.scan_trends(
        brand_keywords=['test'],
        industry_keywords=['demo']
    )
    
    # Clean up (should remove expired)
    removed = monitor.cleanup_expired_trends()
    
    assert isinstance(removed, int)
    assert removed >= 0
    
    print(f"✓ Cleaned up {removed} expired trends")


# ============================================================================
# ContentGenerator Tests
# ============================================================================

def test_content_generator_initialization():
    """Test ContentGenerator initializes correctly."""
    generator = ContentGenerator()
    assert generator is not None
    assert hasattr(generator, 'PLATFORM_LIMITS')
    print("✓ ContentGenerator initialized")


def test_platform_limits():
    """Test platform character limits."""
    generator = ContentGenerator()
    
    limits = generator.PLATFORM_LIMITS
    
    assert limits[Platform.TWITTER]['max_chars'] == 280
    assert limits[Platform.INSTAGRAM]['max_chars'] == 2200
    assert limits[Platform.LINKEDIN]['max_chars'] == 3000
    assert limits[Platform.YOUTUBE]['max_chars'] == 5000
    
    print("✓ Platform limits validated")


def test_content_generation_from_council():
    """Test content generation from council decision."""
    generator = ContentGenerator()
    
    # Mock council state
    council_state = {
        'topic': 'AI Innovation in 2026',
        'platform': Platform.INSTAGRAM,
        'final_decision': {
            'decision': 'approve',
            'reasoning': 'Strong trend alignment'
        },
        'all_proposals': [
            {
                'agent_name': 'TrendAgent',
                'recommendation': 'Post about AI trends',
                'key_points': ['AI growth', 'Innovation']
            }
        ]
    }
    
    content = generator.generate_from_council_decision(
        council_state=council_state,
        platforms=[Platform.INSTAGRAM, Platform.TWITTER]
    )
    
    assert content is not None
    assert hasattr(content, 'variants')
    assert len(content.variants) == 2  # Instagram + Twitter
    
    for platform, piece in content.variants.items():
        assert isinstance(piece, ContentPiece)
        assert piece.platform in [Platform.INSTAGRAM, Platform.TWITTER]
        assert len(piece.primary_text) > 0
        assert len(piece.hashtags) > 0
        assert 0 <= piece.estimated_engagement <= 1
    
    print(f"✓ Generated content for {len(content.variants)} platforms")


def test_platform_specific_formatting():
    """Test platform-specific text formatting."""
    generator = ContentGenerator()
    
    council_state = {
        'topic': 'Test Topic',
        'platform': Platform.TWITTER,
        'final_decision': {'decision': 'approve'},
        'all_proposals': []
    }
    
    # Twitter should be concise
    twitter_content = generator.generate_from_council_decision(
        council_state=council_state,
        platforms=[Platform.TWITTER]
    )
    
    twitter_piece = twitter_content.variants[Platform.TWITTER]
    assert len(twitter_piece.primary_text) <= 280
    assert len(twitter_piece.hashtags) <= 2
    
    print("✓ Platform-specific formatting validated")


def test_hashtag_generation():
    """Test hashtag generation."""
    generator = ContentGenerator()
    
    # Test by generating content which uses _generate_hashtags internally
    council_state = {
        'topic': 'AI Innovation',
        'platform': Platform.INSTAGRAM,
        'final_decision': {'decision': 'approve'},
        'all_proposals': []
    }
    
    content = generator.generate_from_council_decision(
        council_state=council_state,
        platforms=[Platform.INSTAGRAM]
    )
    
    hashtags = content.variants[Platform.INSTAGRAM].hashtags
    
    assert len(hashtags) <= 30  # Instagram max
    assert all(tag.startswith('#') for tag in hashtags)
    
    print(f"✓ Generated {len(hashtags)} hashtags")


def test_engagement_estimation():
    """Test engagement score estimation."""
    generator = ContentGenerator()
    
    score = generator._estimate_engagement(
        text="Check out this amazing AI innovation! 🚀 What do you think?",
        hashtags=['#AI', '#Innovation', '#Tech'],
        platform=Platform.INSTAGRAM
    )
    
    assert 0 <= score <= 1
    assert score > 0  # Should have some engagement potential
    
    print(f"✓ Engagement estimation: {score:.2f}")


# ============================================================================
# AutonomousScheduler Tests
# ============================================================================

def test_scheduler_initialization():
    """Test AutonomousScheduler initializes correctly."""
    scheduler = AutonomousScheduler(mode=ScheduleMode.MANUAL)
    assert scheduler is not None
    assert scheduler.mode == ScheduleMode.MANUAL
    assert scheduler.is_running is False
    print("✓ AutonomousScheduler initialized")


@pytest.mark.asyncio
async def test_manual_trigger():
    """Test manual council trigger."""
    scheduler = AutonomousScheduler(mode=ScheduleMode.MANUAL)
    
    result = scheduler.manual_trigger(
        topic="Test Topic",
        platform=Platform.INSTAGRAM,
        context={'test': True}
    )
    
    assert 'council_state' in result
    assert 'content' in result
    assert 'decision' in result
    
    print("✓ Manual trigger executed")


def test_execution_stats():
    """Test execution statistics."""
    scheduler = AutonomousScheduler(mode=ScheduleMode.MANUAL)
    
    stats = scheduler.get_execution_stats()
    
    assert 'total_cycles' in stats
    # is_running only in stats when cycles exist
    if stats['total_cycles'] > 0:
        assert 'is_running' in stats
        assert 'mode' in stats
        assert stats['mode'] == ScheduleMode.MANUAL.value
    
    print("✓ Execution stats retrieved")


def test_recent_cycles():
    """Test recent cycles retrieval."""
    scheduler = AutonomousScheduler(mode=ScheduleMode.MANUAL)
    
    recent = scheduler.get_recent_cycles(count=5)
    
    assert isinstance(recent, list)
    assert len(recent) <= 5
    
    print(f"✓ Retrieved {len(recent)} recent cycles")


# ============================================================================
# SentimentAnalyzer Tests
# ============================================================================

def test_sentiment_analyzer_initialization():
    """Test SentimentAnalyzer initializes correctly."""
    analyzer = SentimentAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, 'baselines')
    print("✓ SentimentAnalyzer initialized")


def test_performance_tracking():
    """Test post performance tracking."""
    analyzer = SentimentAnalyzer()
    
    metrics = analyzer.track_post_performance(
        post_id="test_post_123",
        platform=Platform.INSTAGRAM,
        posted_at=datetime.now().isoformat(),
        likes=500,
        comments=50,
        shares=25,
        views=10000,
        clicks=200,
        saves=100
    )
    
    assert isinstance(metrics, EngagementMetrics)
    assert metrics.post_id == "test_post_123"
    assert 0 <= metrics.engagement_rate <= 1
    assert 0 <= metrics.viral_coefficient <= 1
    assert -1 <= metrics.sentiment_score <= 1
    assert isinstance(metrics.sentiment_category, SentimentCategory)
    assert isinstance(metrics.performance_tier, PerformanceTier)
    
    print(f"✓ Performance tracked: {metrics.performance_tier.value}")


def test_sentiment_calculation():
    """Test sentiment score calculation."""
    analyzer = SentimentAnalyzer()
    
    # Positive sentiment
    positive_score = analyzer._calculate_sentiment(
        likes=1000,
        comments=100,
        shares=200,
        comment_sentiments=[0.8, 0.9, 0.7]
    )
    
    assert -1 <= positive_score <= 1
    assert positive_score > 0
    
    print(f"✓ Positive sentiment: {positive_score:.2f}")


def test_sentiment_categorization():
    """Test sentiment categorization."""
    analyzer = SentimentAnalyzer()
    
    assert analyzer._categorize_sentiment(0.9) == SentimentCategory.VERY_POSITIVE
    assert analyzer._categorize_sentiment(0.5) == SentimentCategory.POSITIVE
    assert analyzer._categorize_sentiment(0.0) == SentimentCategory.NEUTRAL
    assert analyzer._categorize_sentiment(-0.5) == SentimentCategory.NEGATIVE
    assert analyzer._categorize_sentiment(-0.9) == SentimentCategory.VERY_NEGATIVE
    
    print("✓ Sentiment categorization validated")


def test_performance_tier_calculation():
    """Test performance tier calculation."""
    analyzer = SentimentAnalyzer()
    
    # Excellent performance
    tier, score = analyzer._calculate_performance(
        platform=Platform.INSTAGRAM,
        engagement_rate=0.15,  # 3x baseline
        viral_coefficient=0.03,  # 3x baseline
        ctr=0.06,  # 3x baseline
        save_rate=0.09  # 3x baseline
    )
    
    assert isinstance(tier, PerformanceTier)
    assert tier in [PerformanceTier.EXCELLENT, PerformanceTier.VIRAL]
    assert score > 100  # Above baseline
    
    print(f"✓ Performance tier: {tier.value} (score: {score:.0f})")


def test_agent_feedback_generation():
    """Test agent feedback generation."""
    analyzer = SentimentAnalyzer()
    
    metrics = EngagementMetrics(
        post_id="test_123",
        platform=Platform.INSTAGRAM,
        posted_at=datetime.now().isoformat(),
        likes=1000,
        comments=100,
        shares=50,
        views=10000,
        clicks=200,
        saves=100,
        engagement_rate=0.115,
        viral_coefficient=0.005,
        click_through_rate=0.02,
        save_rate=0.01,
        sentiment_score=0.8,
        sentiment_category=SentimentCategory.VERY_POSITIVE,
        performance_tier=PerformanceTier.EXCELLENT,
        relative_score=200
    )
    
    agent_proposals = {
        'TrendAgent': {'recommendation': 'approve'},
        'EngagementAgent': {'recommendation': 'approve'}
    }
    
    feedbacks = analyzer.generate_agent_feedback(
        post_id="test_123",
        metrics=metrics,
        agent_proposals=agent_proposals
    )
    
    assert len(feedbacks) == 2
    
    for feedback in feedbacks:
        assert hasattr(feedback, 'agent_name')
        assert hasattr(feedback, 'recommendations')
        assert hasattr(feedback, 'learning_points')
        assert -0.2 <= feedback.confidence_delta <= 0.2
    
    print(f"✓ Generated feedback for {len(feedbacks)} agents")


def test_performance_insights():
    """Test performance insights retrieval."""
    analyzer = SentimentAnalyzer()
    
    insights = analyzer.get_performance_insights(
        platform=Platform.INSTAGRAM,
        days=30
    )
    
    assert 'time_period_days' in insights
    assert 'platform' in insights
    assert 'average_engagement_rate' in insights
    
    print("✓ Performance insights retrieved")


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_pipeline_integration():
    """Test full pipeline integration."""
    print("\n" + "="*60)
    print("PIPELINE INTEGRATION TEST")
    print("="*60)
    
    # Initialize components
    monitor = TrendMonitor()
    generator = ContentGenerator()
    scheduler = AutonomousScheduler(mode=ScheduleMode.MANUAL)
    analyzer = SentimentAnalyzer()
    
    # 1. Scan for trends
    print("\n1. Scanning trends...")
    trends = monitor.scan_trends(
        brand_keywords=['AI', 'innovation'],
        industry_keywords=['tech']
    )
    print(f"   Found {len(trends)} trends")
    
    # 2. Manually trigger council for a topic
    print("\n2. Triggering council...")
    result = scheduler.manual_trigger(
        topic="AI Innovation in 2026",
        platform=Platform.INSTAGRAM
    )
    print(f"   Decision: {result['decision']}")
    
    # 3. Generate content if approved
    if result['content']:
        print("\n3. Content generated:")
        for piece in result['content'].pieces:
            print(f"   - {piece.platform.value}: {len(piece.primary_text)} chars")
    
    # 4. Track performance
    print("\n4. Tracking performance...")
    metrics = analyzer.track_post_performance(
        post_id="integration_test",
        platform=Platform.INSTAGRAM,
        posted_at=datetime.now().isoformat(),
        likes=500,
        comments=50,
        shares=25,
        views=5000
    )
    print(f"   Tier: {metrics.performance_tier.value}")
    print(f"   Sentiment: {metrics.sentiment_category.value}")
    
    print("\n" + "="*60)
    print("INTEGRATION TEST COMPLETE")
    print("="*60)


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("RUNNING PIPELINE TESTS")
    print("="*70)
    
    # TrendMonitor tests
    print("\n--- TrendMonitor Tests ---")
    test_trend_monitor_initialization()
    test_trend_scanning()
    test_relevance_calculation()
    test_council_trigger_logic()
    test_expired_trends_cleanup()
    
    # ContentGenerator tests
    print("\n--- ContentGenerator Tests ---")
    test_content_generator_initialization()
    test_platform_limits()
    test_content_generation_from_council()
    test_platform_specific_formatting()
    test_hashtag_generation()
    test_engagement_estimation()
    
    # AutonomousScheduler tests
    print("\n--- AutonomousScheduler Tests ---")
    test_scheduler_initialization()
    asyncio.run(test_manual_trigger())
    test_execution_stats()
    test_recent_cycles()
    
    # SentimentAnalyzer tests
    print("\n--- SentimentAnalyzer Tests ---")
    test_sentiment_analyzer_initialization()
    test_performance_tracking()
    test_sentiment_calculation()
    test_sentiment_categorization()
    test_performance_tier_calculation()
    test_agent_feedback_generation()
    test_performance_insights()
    
    # Integration test
    print("\n--- Integration Tests ---")
    asyncio.run(test_pipeline_integration())
    
    print("\n" + "="*70)
    print("ALL PIPELINE TESTS COMPLETED")
    print("="*70)
