"""
Test AgentFactory - Validate agent creation and council setup
===============================================================

This script tests the AgentFactory implementation:
1. Creating individual agents by type
2. Creating full council
3. Verifying agent properties
4. Testing default weights

Run: python -m agents.test_agent_factory
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import (
    AgentFactory,
    TrendAgent,
    EngagementAgent,
    BrandAgent,
    RiskAgent,
    ComplianceAgent,
    ArbitratorAgent
)
from graph.state_schema import AgentType


def test_create_individual_agents():
    """Test creating individual agents by type."""
    print("\n" + "="*70)
    print("TEST 1: Create Individual Agents")
    print("="*70)
    
    try:
        # Create each agent type
        trend = AgentFactory.create_agent(AgentType.TREND)
        engagement = AgentFactory.create_agent(AgentType.ENGAGEMENT)
        brand = AgentFactory.create_agent(AgentType.BRAND)
        risk = AgentFactory.create_agent(AgentType.RISK)
        compliance = AgentFactory.create_agent(AgentType.COMPLIANCE)
        arbitrator = AgentFactory.create_agent(AgentType.ARBITRATOR)
        
        # Verify types
        assert isinstance(trend, TrendAgent), "TrendAgent creation failed"
        assert isinstance(engagement, EngagementAgent), "EngagementAgent creation failed"
        assert isinstance(brand, BrandAgent), "BrandAgent creation failed"
        assert isinstance(risk, RiskAgent), "RiskAgent creation failed"
        assert isinstance(compliance, ComplianceAgent), "ComplianceAgent creation failed"
        assert isinstance(arbitrator, ArbitratorAgent), "ArbitratorAgent creation failed"
        
        print("✅ All 6 agent types created successfully")
        print(f"   - TrendAgent: {trend.agent_name}")
        print(f"   - EngagementAgent: {engagement.agent_name}")
        print(f"   - BrandAgent: {brand.agent_name}")
        print(f"   - RiskAgent: {risk.agent_name}")
        print(f"   - ComplianceAgent: {compliance.agent_name}")
        print(f"   - ArbitratorAgent: {arbitrator.agent_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_full_council():
    """Test creating full council with all agents."""
    print("\n" + "="*70)
    print("TEST 2: Create Full Council")
    print("="*70)
    
    try:
        # Create full council
        council = AgentFactory.create_full_council()
        
        # Verify all types present
        expected_types = [
            AgentType.TREND,
            AgentType.ENGAGEMENT,
            AgentType.BRAND,
            AgentType.RISK,
            AgentType.COMPLIANCE,
            AgentType.ARBITRATOR
        ]
        
        for agent_type in expected_types:
            assert agent_type in council, f"{agent_type} missing from council"
        
        assert len(council) == 6, f"Expected 6 agents, got {len(council)}"
        
        print("✅ Full council created with 6 agents:")
        for agent_type, agent in council.items():
            print(f"   - {agent_type.value}: {agent.agent_name} (weight={agent.voting_weight:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Full council creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_voting_weights():
    """Test creating agents with custom voting weights."""
    print("\n" + "="*70)
    print("TEST 3: Custom Voting Weights")
    print("="*70)
    
    try:
        # Create agent with custom weight
        trend = AgentFactory.create_agent(AgentType.TREND, voting_weight=0.25)
        
        assert trend.voting_weight == 0.25, f"Expected 0.25, got {trend.voting_weight}"
        
        print("✅ Custom voting weight applied successfully")
        print(f"   TrendAgent weight: {trend.voting_weight}")
        
        # Create council with custom weights
        custom_weights = {
            AgentType.TREND: 0.30,
            AgentType.BRAND: 0.25,
            AgentType.ARBITRATOR: 0.20
        }
        
        council = AgentFactory.create_full_council(custom_weights=custom_weights)
        
        assert council[AgentType.TREND].voting_weight == 0.30
        assert council[AgentType.BRAND].voting_weight == 0.25
        assert council[AgentType.ARBITRATOR].voting_weight == 0.20
        
        print("✅ Custom council weights applied:")
        for agent_type, agent in council.items():
            print(f"   - {agent_type.value}: {agent.voting_weight:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Custom weights test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_default_weights():
    """Test default voting weights configuration."""
    print("\n" + "="*70)
    print("TEST 4: Default Weights Configuration")
    print("="*70)
    
    try:
        default_weights = AgentFactory.get_default_weights()
        
        expected = {
            AgentType.ARBITRATOR: 0.25,
            AgentType.BRAND: 0.20,
            AgentType.RISK: 0.15,
            AgentType.COMPLIANCE: 0.15,
            AgentType.ENGAGEMENT: 0.13,
            AgentType.TREND: 0.12
        }
        
        assert default_weights == expected, "Default weights mismatch"
        
        # Verify weights sum to 1.0
        total = sum(default_weights.values())
        assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected 1.0"
        
        print("✅ Default weights configured correctly:")
        for agent_type, weight in default_weights.items():
            print(f"   - {agent_type.value}: {weight:.2f}")
        print(f"   Total: {total:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Default weights test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_behavior_loading():
    """Test that agents load their behavior specifications."""
    print("\n" + "="*70)
    print("TEST 5: Behavior Specification Loading")
    print("="*70)
    
    try:
        council = AgentFactory.create_full_council()
        
        behavior_checks = {
            AgentType.TREND: "viral",
            AgentType.ENGAGEMENT: "community",
            AgentType.BRAND: "consistency",
            AgentType.RISK: "safety",
            AgentType.COMPLIANCE: "compliance",
            AgentType.ARBITRATOR: "CMO"
        }
        
        for agent_type, keyword in behavior_checks.items():
            agent = council[agent_type]
            
            # Check if behavior spec is loaded and contains expected keyword
            assert agent.behavior_spec is not None, f"{agent_type} has no behavior spec"
            assert len(agent.behavior_spec) > 0, f"{agent_type} behavior spec is empty"
            
            # Check for keyword (case insensitive)
            contains_keyword = keyword.lower() in agent.behavior_spec.lower()
            
            print(f"   - {agent_type.value}: Loaded {len(agent.behavior_spec)} chars "
                  f"{'✅' if contains_keyword else '⚠️  (keyword not found)'}")
        
        print("✅ All agents have behavior specifications loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Behavior loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_agent_type():
    """Test error handling for invalid agent type."""
    print("\n" + "="*70)
    print("TEST 6: Invalid Agent Type Handling")
    print("="*70)
    
    try:
        # This should raise ValueError
        try:
            AgentFactory.create_agent("INVALID_TYPE")
            print("❌ Should have raised ValueError for invalid type")
            return False
        except (ValueError, AttributeError) as e:
            print(f"✅ Correctly raised error for invalid type: {type(e).__name__}")
            return True
        
    except Exception as e:
        print(f"❌ Invalid type test failed unexpectedly: {e}")
        return False


def main():
    """Run all AgentFactory tests."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "AGENT FACTORY VALIDATION TEST SUITE" + " "*17 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        test_create_individual_agents,
        test_create_full_council,
        test_custom_voting_weights,
        test_default_weights,
        test_agent_behavior_loading,
        test_invalid_agent_type
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - AgentFactory is working correctly!")
        print("\nPhase 4: Specialized Agents - COMPLETED ✅")
        print("\nNext: Phase 5 - LangGraph Council Architecture")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
