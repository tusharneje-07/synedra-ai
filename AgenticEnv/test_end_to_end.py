"""
End-to-End Integration Test
============================

Complete system test covering:
- Database initialization
- Agent creation
- Trend detection
- Council deliberation
- Content generation
- Performance tracking

Author: AI Systems Engineer
Date: February 7, 2026
"""

import pytest
import asyncio
from datetime import datetime

from main import AutonomousCouncil
from graph import Platform
from pipeline.scheduler import ScheduleMode


@pytest.mark.asyncio
async def test_complete_workflow():
    """Test complete end-to-end workflow."""
    print("\n" + "=" * 70)
    print("END-TO-END INTEGRATION TEST")
    print("=" * 70)
    
    # Initialize council
    print("\n1. Initializing Autonomous Council...")
    council = AutonomousCouncil(
        brand_name="TestBrand",
        brand_keywords=["AI", "automation"],
        industry_keywords=["technology", "innovation"]
    )
    
    assert council is not None
    assert council.council is not None
    assert council.trend_monitor is not None
    assert council.content_generator is not None
    assert council.sentiment_analyzer is not None
    
    print("   ✓ Council initialized")
    
    # Test manual trigger
    print("\n2. Testing manual council trigger...")
    result = council.manual_trigger(
        topic="AI Innovation in 2026",
        platform=Platform.INSTAGRAM,
        context={
            'test_mode': True,
            'urgency': 'high'
        }
    )
    
    assert 'council_state' in result
    assert 'content' in result
    assert 'decision' in result
    
    decision = result['decision']
    print(f"   ✓ Council decision: {decision}")
    
    # Test content generation
    if result['content']:
        print("\n3. Verifying generated content...")
        content = result['content']
        
        assert hasattr(content, 'variants')
        assert len(content.variants) > 0
        
        for platform, piece in content.variants.items():
            print(f"\n   Platform: {platform.value}")
            print(f"   Text length: {len(piece.primary_text)} chars")
            print(f"   Hashtags: {len(piece.hashtags)}")
            print(f"   Estimated engagement: {piece.estimated_engagement:.2%}")
            
            # Validate content
            assert len(piece.primary_text) > 0
            assert len(piece.hashtags) > 0
            assert 0 <= piece.estimated_engagement <= 1
        
        print("   ✓ Content validated")
    
    # Test single cycle execution
    print("\n4. Testing single execution cycle...")
    cycle = await council.run_single_cycle()
    
    assert cycle is not None
    assert cycle.status in ['completed', 'running']
    assert cycle.trends_detected >= 0
    
    print(f"   ✓ Cycle complete: {cycle.status}")
    print(f"     - Trends detected: {cycle.trends_detected}")
    print(f"     - Councils triggered: {cycle.councils_triggered}")
    print(f"     - Content generated: {cycle.content_generated}")
    
    # Test performance tracking
    print("\n5. Testing performance tracking...")
    metrics = council.track_performance(
        post_id="test_e2e_post",
        platform=Platform.INSTAGRAM,
        likes=1000,
        comments=100,
        shares=50,
        views=10000,
        clicks=200,
        saves=150
    )
    
    assert metrics is not None
    assert metrics.engagement_rate > 0
    assert -1 <= metrics.sentiment_score <= 1
    
    print(f"   ✓ Performance tracked")
    print(f"     - Tier: {metrics.performance_tier.value}")
    print(f"     - Engagement: {metrics.engagement_rate:.2%}")
    print(f"     - Sentiment: {metrics.sentiment_category.value}")
    
    print("\n" + "=" * 70)
    print("END-TO-END TEST COMPLETE ✓")
    print("=" * 70)


@pytest.mark.asyncio
async def test_autonomous_workflow_simulation():
    """Simulate autonomous workflow (single iteration)."""
    print("\n" + "=" * 70)
    print("AUTONOMOUS WORKFLOW SIMULATION")
    print("=" * 70)
    
    council = AutonomousCouncil(
        brand_name="SimBrand",
        brand_keywords=["tech", "AI"],
        industry_keywords=["software"]
    )
    
    print("\n1. Scanning for trends...")
    trends = council.trend_monitor.scan_trends(
        brand_keywords=council.brand_keywords,
        industry_keywords=council.industry_keywords
    )
    
    print(f"   Found {len(trends)} trends")
    
    print("\n2. Checking trigger conditions...")
    triggered = []
    for trend in trends:
        if council.trend_monitor.should_trigger_council(trend):
            triggered.append(trend)
    
    print(f"   {len(triggered)} trends meet trigger threshold")
    
    if triggered:
        print("\n3. Processing first triggered trend...")
        trend = triggered[0]
        
        result = council.manual_trigger(
            topic=trend.topic,
            platform=trend.platform
        )
        
        print(f"   Decision: {result['decision']}")
        
        if result['content']:
            print(f"   Generated content for {len(result['content'].variants)} platforms")
    else:
        print("\n3. No trends triggered council (this is normal)")
    
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE ✓")
    print("=" * 70)


def test_system_components():
    """Test individual system components."""
    print("\n" + "=" * 70)
    print("SYSTEM COMPONENTS TEST")
    print("=" * 70)
    
    council = AutonomousCouncil(
        brand_name="ComponentTest",
        brand_keywords=["test"],
        industry_keywords=["testing"]
    )
    
    # Test components exist
    print("\n1. Checking components...")
    
    components = {
        'Database': council.db,
        'Council Graph': council.council,
        'Trend Monitor': council.trend_monitor,
        'Content Generator': council.content_generator,
        'Sentiment Analyzer': council.sentiment_analyzer
    }
    
    for name, component in components.items():
        assert component is not None
        print(f"   ✓ {name}")
    
    # Test agent creation
    print("\n2. Verifying agents...")
    agents = council.council.agents
    
    # Agents are keyed by AgentType enum values
    from graph.state_schema import AgentType
    
    expected_agent_types = [
        AgentType.TREND,
        AgentType.ENGAGEMENT,
        AgentType.BRAND,
        AgentType.RISK,
        AgentType.COMPLIANCE,
        AgentType.ARBITRATOR
    ]
    
    for agent_type in expected_agent_types:
        assert agent_type in agents
        agent = agents[agent_type]
        print(f"   ✓ {agent.__class__.__name__} ({agent_type.value})")
    
    print("\n" + "=" * 70)
    print("COMPONENTS TEST COMPLETE ✓")
    print("=" * 70)


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling and edge cases."""
    print("\n" + "=" * 70)
    print("ERROR HANDLING TEST")
    print("=" * 70)
    
    council = AutonomousCouncil()
    
    # Test with minimal data
    print("\n1. Testing with minimal input...")
    result = council.manual_trigger(
        topic="Test",
        platform=Platform.TWITTER
    )
    
    assert result is not None
    print("   ✓ Handled minimal input")
    
    # Test performance tracking with edge values
    print("\n2. Testing performance tracking edge cases...")
    
    # Zero engagement
    metrics = council.track_performance(
        post_id="test_zero",
        platform=Platform.INSTAGRAM,
        likes=0,
        comments=0,
        shares=0,
        views=1
    )
    
    assert metrics is not None
    assert metrics.engagement_rate == 0
    print("   ✓ Handled zero engagement")
    
    # High engagement
    metrics = council.track_performance(
        post_id="test_viral",
        platform=Platform.INSTAGRAM,
        likes=10000,
        comments=1000,
        shares=500,
        views=50000
    )
    
    assert metrics is not None
    assert metrics.engagement_rate > 0
    print("   ✓ Handled viral engagement")
    
    print("\n" + "=" * 70)
    print("ERROR HANDLING TEST COMPLETE ✓")
    print("=" * 70)


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("RUNNING END-TO-END TESTS")
    print("=" * 70)
    
    # Run tests
    asyncio.run(test_complete_workflow())
    asyncio.run(test_autonomous_workflow_simulation())
    test_system_components()
    asyncio.run(test_error_handling())
    
    print("\n" + "=" * 70)
    print("ALL END-TO-END TESTS COMPLETED ✓")
    print("=" * 70)
