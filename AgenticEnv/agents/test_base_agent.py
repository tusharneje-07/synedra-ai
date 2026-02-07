"""
Test Script for Base Agent Architecture
========================================

This script validates the base agent implementation by:
1. Testing configuration loading
2. Testing LLM client initialization
3. Testing markdown file loading
4. Testing memory integration

Run this before implementing specialized agents.

Usage:
    python -m agents.test_base_agent
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import get_settings, validate_environment, setup_logging
from db.database import get_database
from memory.memory_manager import get_memory_manager
from agents.base_agent import BaseLLMClient, BaseAgent
from graph.state_schema import AgentType, create_initial_state


def test_configuration():
    """Test configuration loading."""
    print("\n" + "="*60)
    print("TEST 1: Configuration Loading")
    print("="*60)
    
    try:
        settings = get_settings()
        print(f"✓ Settings loaded successfully")
        print(f"  - LLM Model: {settings.llm_model}")
        print(f"  - Temperature: {settings.llm_temperature}")
        print(f"  - Max Tokens: {settings.max_tokens}")
        print(f"  - Database Path: {settings.get_absolute_database_path()}")
        print(f"  - Agent Definitions: {settings.get_absolute_agent_definitions_path()}")
        
        # Validate environment
        is_valid, errors = validate_environment()
        if is_valid:
            print(f"✓ Environment validation passed")
        else:
            print(f"✗ Environment validation failed:")
            for error in errors:
                print(f"    - {error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_database():
    """Test database initialization."""
    print("\n" + "="*60)
    print("TEST 2: Database Initialization")
    print("="*60)
    
    try:
        db = get_database()
        print(f"✓ Database initialized")
        
        stats = db.get_database_stats()
        print(f"  - Agent Memory Records: {stats.get('agent_memory', 0)}")
        print(f"  - Council Decisions: {stats.get('council_decisions', 0)}")
        print(f"  - Engagement Metrics: {stats.get('engagement_metrics', 0)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_memory_manager():
    """Test memory manager."""
    print("\n" + "="*60)
    print("TEST 3: Memory Manager")
    print("="*60)
    
    try:
        memory = get_memory_manager()
        print(f"✓ Memory manager initialized")
        
        # Store test memory
        record_id = memory.store_memory(
            agent_name="TestAgent",
            context="Test context",
            decision={"action": "test"},
            reasoning="This is a test",
            importance=0.5
        )
        print(f"✓ Stored test memory (ID: {record_id})")
        
        # Retrieve memory
        memories = memory.get_agent_context("TestAgent", limit=1)
        if memories:
            print(f"✓ Retrieved test memory")
            print(f"  - Context: {memories[0].get('context', 'N/A')}")
        
        stats = memory.get_memory_stats()
        print(f"  - Total memories: {stats['total_agent_memories']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Memory manager test failed: {e}")
        return False


def test_llm_client():
    """Test LLM client initialization."""
    print("\n" + "="*60)
    print("TEST 4: LLM Client")
    print("="*60)
    
    try:
        settings = get_settings()
        
        # Check API key
        if not settings.validate_api_key():
            print(f"✗ Invalid GROQ API key")
            print(f"  Please set GROQ_API_KEY in .env file")
            print(f"  Get your key from: https://console.groq.com/keys")
            return False
        
        print(f"✓ GROQ API key validated")
        
        # Initialize client
        llm = BaseLLMClient()
        print(f"✓ LLM client initialized")
        print(f"  - Model: {settings.llm_model}")
        
        # Test generation (simple prompt)
        print(f"\n  Testing LLM generation...")
        response = llm.generate(
            prompt="Say 'Hello, I am working!' in exactly those words.",
            system_prompt="You are a helpful assistant.",
            max_tokens=50
        )
        print(f"✓ LLM generation successful")
        print(f"  Response: {response[:100]}...")
        
        # Test JSON generation
        print(f"\n  Testing JSON generation...")
        json_response = llm.generate_json(
            prompt="Generate a JSON object with keys 'status' and 'message'",
            schema_description='{"status": "string", "message": "string"}'
        )
        print(f"✓ JSON generation successful")
        print(f"  Response: {json_response}")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_markdown_loading():
    """Test markdown file loading."""
    print("\n" + "="*60)
    print("TEST 5: Markdown Behavior Loading")
    print("="*60)
    
    try:
        settings = get_settings()
        agent_files = {
            "CMOAgent.md": "Arbitrator",
            "TrendAgent.md": "Trend Agent",
            "EngagementAgent.md": "Engagement Agent",
            "BrandAgent.md": "Brand Agent",
            "RiskAgent.md": "Risk Agent",
            "ComplianceAgent.md": "Compliance Agent"
        }
        
        all_found = True
        for filename, agent_name in agent_files.items():
            file_path = settings.get_absolute_agent_definitions_path() / filename
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"✓ {agent_name}: {filename} ({size:,} bytes)")
            else:
                print(f"✗ {agent_name}: {filename} NOT FOUND")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"✗ Markdown loading test failed: {e}")
        return False


def test_base_agent_mock():
    """Test base agent with a mock implementation."""
    print("\n" + "="*60)
    print("TEST 6: Base Agent Mock")
    print("="*60)
    
    try:
        # Create a simple mock agent for testing
        class MockAgent(BaseAgent):
            def analyze(self, state, context=None):
                return self._create_base_proposal(
                    recommendation="Test recommendation",
                    confidence=0.75,
                    reasoning="This is a test",
                    vote="approve"
                )
            
            def debate(self, state, other_proposals):
                return {"response": "Test debate response"}
        
        # Initialize mock agent
        agent = MockAgent(
            agent_name="Mock Agent",
            agent_type=AgentType.TREND,
            behavior_file="TrendAgent.md",
            voting_weight=0.20
        )
        
        print(f"✓ Mock agent initialized: {agent}")
        print(f"  - Name: {agent.agent_name}")
        print(f"  - Type: {agent.agent_type}")
        print(f"  - Weight: {agent.voting_weight}")
        print(f"  - Behavior spec loaded: {len(agent.behavior_spec)} chars")
        print(f"  - System prompt length: {len(agent.system_prompt)} chars")
        
        # Test proposal generation
        state = create_initial_state(
            cycle_id="test-001",
            topic="Test topic",
            trigger_event="test"
        )
        
        proposal = agent.analyze(state)
        print(f"✓ Generated test proposal")
        print(f"  - Recommendation: {proposal.get('recommendation', 'N/A')}")
        print(f"  - Confidence: {proposal.get('confidence', 0)}")
        print(f"  - Vote: {proposal.get('vote', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Base agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all validation tests."""
    print("\n" + "█"*60)
    print("  BASE AGENT ARCHITECTURE VALIDATION")
    print("█"*60)
    
    # Setup logging first
    settings = get_settings()
    setup_logging(settings)
    
    results = {}
    
    # Run tests
    results['Configuration'] = test_configuration()
    results['Database'] = test_database()
    results['Memory Manager'] = test_memory_manager()
    results['LLM Client'] = test_llm_client()
    results['Markdown Loading'] = test_markdown_loading()
    results['Base Agent'] = test_base_agent_mock()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Base agent architecture is ready.")
        return True
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Please fix before proceeding.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
