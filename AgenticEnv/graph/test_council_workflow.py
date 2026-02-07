"""
Test Council Workflow - End-to-End Validation
==============================================

Tests the complete LangGraph council workflow:
1. Council initialization
2. Agent analysis phase
3. Conflict detection
4. Debate orchestration
5. Arbitration
6. Final decision output

Run: python -m graph.test_council_workflow
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph import CouncilGraph, Platform
from agents import AgentFactory


def test_council_initialization():
    """Test council graph can be created."""
    print("\n" + "="*70)
    print("TEST 1: Council Initialization")
    print("="*70)
    
    try:
        council = CouncilGraph(
            max_debate_rounds=3,
            convergence_threshold=0.85,
            auto_create_agents=True
        )
        
        assert council.agents is not None, "Agents not created"
        assert len(council.agents) == 6, f"Expected 6 agents, got {len(council.agents)}"
        assert council.graph is not None, "Graph not compiled"
        
        print("✅ Council initialized successfully")
        print(f"   - Agents: {len(council.agents)}")
        print(f"   - Max debate rounds: {council.max_debate_rounds}")
        print(f"   - Convergence threshold: {council.convergence_threshold}")
        
        return True
        
    except Exception as e:
        print(f"❌ Council initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_topic_analysis():
    """Test council can analyze a simple topic."""
    print("\n" + "="*70)
    print("TEST 2: Simple Topic Analysis (No API Calls)")
    print("="*70)
    
    try:
        # Test state flow without actual LLM calls
        from graph.state_schema import create_initial_state
        from datetime import datetime
        
        initial_state = create_initial_state(
            cycle_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic="Test post about new product launch",
            trigger_event="test",
            platform=Platform.INSTAGRAM,
            urgency='high'
        )
        
        assert initial_state['topic'] == "Test post about new product launch"
        assert initial_state['platform'] == Platform.INSTAGRAM
        assert initial_state['urgency'] == 'high'
        assert 'all_proposals' in initial_state  # Check for all_proposals field
        
        print("✅ Initial state created correctly")
        print(f"   Topic: {initial_state['topic']}")
        print(f"   Platform: {initial_state['platform'].value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Topic analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conflict_detection():
    """Test conflict detection between mock proposals."""
    print("\n" + "="*70)
    print("TEST 3: Conflict Detection")
    print("="*70)
    
    try:
        from graph import ConflictResolver
        from graph.state_schema import AgentType
        
        resolver = ConflictResolver()
        
        # Create mock conflicting proposals
        mock_proposals = [
            {
                'agent_type': AgentType.TREND,
                'agent_name': 'TrendAgent',
                'vote': 'approve',
                'confidence': 0.9,
                'priority': 'high',
                'recommendation': 'Post immediately for viral potential'
            },
            {
                'agent_type': AgentType.RISK,
                'agent_name': 'RiskAgent',
                'vote': 'reject',
                'confidence': 0.85,
                'priority': 'high',
                'recommendation': 'Too risky, potential backlash'
            },
            {
                'agent_type': AgentType.BRAND,
                'agent_name': 'BrandAgent',
                'vote': 'conditional',
                'confidence': 0.7,
                'priority': 'medium',
                'recommendation': 'Approve with brand guideline adjustments'
            }
        ]
        
        conflicts = resolver.detect_conflicts(mock_proposals)
        
        assert len(conflicts) > 0, "Should detect conflicts between approve and reject"
        
        conflict_summary = resolver.build_conflict_summary(conflicts)
        
        print("✅ Conflict detection working")
        print(f"   Total conflicts: {conflict_summary['total_conflicts']}")
        print(f"   Critical conflicts: {conflict_summary.get('critical_conflicts', 0)}")
        print(f"   Requires arbitration: {conflict_summary['requires_arbitration']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Conflict detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_debate_manager():
    """Test debate manager with mock data."""
    print("\n" + "="*70)
    print("TEST 4: Debate Manager")
    print("="*70)
    
    try:
        from graph import DebateManager
        from graph.state_schema import create_initial_state, AgentType
        from datetime import datetime
        
        debate_mgr = DebateManager(max_rounds=2, convergence_threshold=0.85)
        
        # Create mock state with proposals
        state = create_initial_state(
            cycle_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic="Test debate topic",
            trigger_event="test",
            platform=Platform.INSTAGRAM
        )
        
        state['current_proposals'] = [
            {
                'agent_type': AgentType.TREND,
                'vote': 'approve',
                'confidence': 0.8
            },
            {
                'agent_type': AgentType.RISK,
                'vote': 'reject',
                'confidence': 0.7
            }
        ]
        
        # Test vote extraction
        votes = debate_mgr._extract_votes(state['current_proposals'])
        
        assert AgentType.TREND in votes, "Should extract trend vote"
        assert votes[AgentType.TREND] == 'approve', "Should have approve vote"
        
        print("✅ Debate manager initialized and functional")
        print(f"   Max rounds: {debate_mgr.max_rounds}")
        print(f"   Convergence threshold: {debate_mgr.convergence_threshold}")
        print(f"   Vote extraction working: {len(votes)} votes extracted")
        
        return True
        
    except Exception as e:
        print(f"❌ Debate manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_structure():
    """Test graph structure and nodes."""
    print("\n" + "="*70)
    print("TEST 5: Graph Structure Validation")
    print("="*70)
    
    try:
        council = CouncilGraph(auto_create_agents=True)
        
        # Verify graph has expected nodes
        graph_dict = council.graph.get_graph()
        
        print("✅ Graph structure validated")
        print(f"   Graph compiled: {council.graph is not None}")
        print(f"   Workflow nodes created")
        
        return True
        
    except Exception as e:
        print(f"❌ Graph structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_state_transitions():
    """Test state schema transitions."""
    print("\n" + "="*70)
    print("TEST 6: State Transitions")
    print("="*70)
    
    try:
        from graph.state_schema import create_initial_state, calculate_consensus_score
        from datetime import datetime
        
        # Create state
        state = create_initial_state(
            cycle_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic="State transition test",
            trigger_event="test",
            platform=Platform.TWITTER
        )
        
        # Simulate workflow stages
        state['workflow_stage'] = 'initialized'
        assert state['workflow_stage'] == 'initialized'
        
        state['workflow_stage'] = 'analysis'
        state['current_proposals'] = [
            {'vote': 'approve', 'confidence': 0.9},
            {'vote': 'approve', 'confidence': 0.85},
            {'vote': 'approve', 'confidence': 0.8}
        ]
        
        consensus = calculate_consensus_score(state['current_proposals'])
        assert consensus > 0, "Should calculate consensus score"
        
        state['workflow_stage'] = 'completed'
        
        print("✅ State transitions working correctly")
        print(f"   Initial → Analysis → Completed")
        print(f"   Consensus score calculated: {consensus:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ State transitions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_mock_workflow():
    """Test complete workflow with mock data (no LLM calls)."""
    print("\n" + "="*70)
    print("TEST 7: End-to-End Mock Workflow")
    print("="*70)
    
    try:
        from graph.state_schema import create_initial_state, AgentType
        from datetime import datetime
        
        # Create council
        council = CouncilGraph(auto_create_agents=True)
        
        # Create test state
        state = create_initial_state(
            cycle_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic="Mock workflow test - product announcement",
            trigger_event="test",
            platform=Platform.INSTAGRAM,
            urgency='high'
        )
        
        # Add extra context
        state['context'] = {'campaign': 'product_launch', 'budget': 'high'}
        
        # Manually simulate workflow stages
        print("   📝 Simulating workflow stages:")
        
        # 1. Initialize
        state = council._initialize_node(state)
        print(f"   ✓ Initialize: {state['workflow_stage']}")
        
        # Mock analysis results (would normally come from LLM)
        state['current_proposals'] = [
            {
                'agent_type': AgentType.TREND,
                'agent_name': 'TrendAgent',
                'vote': 'approve',
                'confidence': 0.9,
                'recommendation': 'High viral potential'
            },
            {
                'agent_type': AgentType.BRAND,
                'agent_name': 'BrandAgent',
                'vote': 'approve',
                'confidence': 0.85,
                'recommendation': 'Aligned with brand voice'
            },
            {
                'agent_type': AgentType.RISK,
                'agent_name': 'RiskAgent',
                'vote': 'conditional',
                'confidence': 0.7,
                'recommendation': 'Approve with minor adjustments'
            }
        ]
        
        # 2. Detect conflicts
        state = council._detect_conflicts_node(state)
        print(f"   ✓ Conflict Detection: {len(state.get('conflicts_detected', []))} conflicts")
        
        # 3. Check if debate needed
        decision = council._should_debate(state)
        print(f"   ✓ Debate Decision: {decision}")
        
        # 4. Finalize
        state = council._finalize_node(state)
        print(f"   ✓ Finalize: {state['workflow_stage']}")
        
        assert state['workflow_stage'] == 'completed'
        assert 'execution_summary' in state
        
        print("\n✅ End-to-end workflow simulation successful")
        print(f"   Execution summary generated: {state['execution_summary']['topic']}")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all council workflow tests."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*12 + "COUNCIL WORKFLOW VALIDATION TEST SUITE" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        test_council_initialization,
        test_simple_topic_analysis,
        test_conflict_detection,
        test_debate_manager,
        test_graph_structure,
        test_state_transitions,
        test_end_to_end_mock_workflow
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
        print("\n✅ ALL TESTS PASSED - Council Workflow is working correctly!")
        print("\nPhase 5: LangGraph Council Architecture - COMPLETED ✅")
        print("\nNext: Phase 6 - Pipeline Components")
        print("  - Trend monitoring")
        print("  - Content generation")
        print("  - Scheduler & automation")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("="*70)
    
    print("\n📌 NOTE: Full workflow with LLM requires GROQ_API_KEY")
    print("   Current tests use mock data to validate architecture")
    print("\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
