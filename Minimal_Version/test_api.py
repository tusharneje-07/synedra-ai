"""
Test API connection and LLM functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.api_manager import get_active_api_key, test_api_key
from groq import Groq
import json

print("=" * 60)
print("TESTING API CONNECTION")
print("=" * 60)

# Test 1: Get active API key
print("\n1. Testing API key retrieval...")
try:
    api_key = get_active_api_key()
    print(f"✓ Successfully retrieved API key: {api_key[:20]}...")
except Exception as e:
    print(f"✗ Failed to get API key: {e}")
    sys.exit(1)

# Test 2: Test API key health
print("\n2. Testing API key health...")
try:
    result = test_api_key(api_key)
    print(f"✓ API key health check: {result}")
except Exception as e:
    print(f"✗ API health check failed: {e}")

# Test 3: Simple LLM call
print("\n3. Testing simple LLM call...")
try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, API is working!' in JSON format with a 'message' field."}
        ],
        temperature=0.7,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    print(f"✓ LLM Response: {content}")
    parsed = json.loads(content)
    print(f"✓ JSON parsed successfully: {parsed}")
except Exception as e:
    print(f"✗ LLM call failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test with agent-like prompt
print("\n4. Testing agent-like prompt with JSON mode...")
try:
    client = Groq(api_key=api_key)
    
    system_prompt = """You are a test agent. Respond in JSON format with these fields:
{
  "agent_name": "TestAgent",
  "recommendation": "A test recommendation in 2-3 sentences",
  "reasoning": "Test reasoning in paragraph form with 4-5 sentences",
  "score": 75,
  "vote": "approve"
}"""
    
    user_prompt = "Analyze this test content and provide your assessment."
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1000,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    print(f"✓ Agent-like response received")
    parsed = json.loads(content)
    print(f"✓ Parsed JSON:")
    print(f"  - Agent: {parsed.get('agent_name')}")
    print(f"  - Recommendation: {parsed.get('recommendation')}")
    print(f"  - Reasoning: {parsed.get('reasoning')[:100]}...")
    print(f"  - Vote: {parsed.get('vote')}")
    
except Exception as e:
    print(f"✗ Agent-like prompt failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("API TESTING COMPLETE")
print("=" * 60)
