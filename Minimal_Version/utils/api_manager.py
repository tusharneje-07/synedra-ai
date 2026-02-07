"""
API Manager - Manages API keys and ensures healthy API before any LLM operation
"""

import json
import logging
from pathlib import Path
from groq import Groq

logger = logging.getLogger(__name__)

API_KEYS_FILE = Path('apiconfig/apis.json')

def load_api_keys():
    """Load API keys from JSON file"""
    if not API_KEYS_FILE.exists():
        API_KEYS_FILE.parent.mkdir(exist_ok=True)
        return []
    
    try:
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading API keys: {e}")
        return []

def save_api_keys(keys):
    """Save API keys to JSON file"""
    API_KEYS_FILE.parent.mkdir(exist_ok=True)
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def test_api_key(api_key: str) -> bool:
    """
    Test if an API key is working by sending a simple 'Hello' message
    
    Returns:
        True if API responds successfully
        False if API fails (invalid key, rate limit, network error, etc.)
    """
    try:
        logger.info("📤 Sending test message: 'Hello'")
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
            timeout=10
        )
        
        # Check if we got a valid response
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            if content is not None:
                logger.info(f"✅ API key test SUCCESS - Got reply: {content[:50]}")
                return True
        
        logger.warning("⚠️ API key test FAILED - No valid response content")
        return False
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate_limit" in error_msg.lower():
            logger.warning(f"⚠️ API key test FAILED - Rate limit: {error_msg[:100]}")
        elif "401" in error_msg or "invalid" in error_msg.lower():
            logger.error(f"❌ API key test FAILED - Invalid key: {error_msg[:100]}")
        else:
            logger.error(f"❌ API key test FAILED - Error: {error_msg[:100]}")
        return False

def get_active_api_key() -> str:
    """
    Get the first active API key based on saved status
    Does NOT re-test keys - uses the 'active' status from Settings
    
    Use ensure_api_health() before starting debate to verify keys work
    This function is for retrieving the key during operations
    """
    keys = load_api_keys()
    
    if not keys:
        raise Exception("No API keys configured. Please add API keys in Settings.")
    
    # Return first active key (based on saved status)
    for key_data in keys:
        if key_data.get('active', False):
            logger.info(f"🔑 Using API key: {key_data.get('name')}")
            return key_data['key']
    
    # If no active key found, raise error
    raise Exception("No active API keys available. Please test your API keys in Settings.")

def get_current_key_name(api_key: str) -> str:
    """
    Get the name of the current API key being used
    Used for logging which key is handling a request
    """
    keys = load_api_keys()
    for key_data in keys:
        if key_data['key'] == api_key:
            return key_data.get('name', 'Unnamed Key')
    return 'Unknown Key'

def test_all_keys_and_update_status():
    """
    Test all API keys by sending 'Hello' message to each
    Updates active status in JSON file based on results
    
    This should be called:
    - Before starting any debate
    - When user clicks "Test All Keys" in Settings
    
    Returns dict with results
    """
    logger.info("🧪 Starting API key tests...")
    keys = load_api_keys()
    
    if not keys:
        logger.warning("No API keys configured")
        return {
            'success': False,
            'message': 'No API keys configured',
            'active_count': 0,
            'total_count': 0
        }
    
    results = []
    active_count = 0
    
    for key_data in keys:
        key_name = key_data.get('name', 'Unnamed Key')
        logger.info(f"Testing: {key_name}")
        
        # Send 'Hello' message to test the key
        is_working = test_api_key(key_data['key'])
        
        # Update active status in the key data
        key_data['active'] = is_working
        
        if is_working:
            active_count += 1
            logger.info(f"✅ {key_name}: ACTIVE")
        else:
            logger.warning(f"❌ {key_name}: INACTIVE")
        
        results.append({
            'id': key_data['id'],
            'name': key_name,
            'active': is_working,
            'status': 'Working ✓' if is_working else 'Failed ✗'
        })
    
    # Save updated status to JSON file
    logger.info(f"💾 Saving updated status to {API_KEYS_FILE}")
    save_api_keys(keys)
    
    logger.info(f"📊 API Key Test Complete: {active_count}/{len(keys)} working")
    
    return {
        'success': True,
        'message': f'Tested {len(keys)} API keys. {active_count} are working.',
        'active_count': active_count,
        'total_count': len(keys),
        'results': results
    }

def reactivate_all_keys():
    """
    Re-test and reactivate all API keys
    Useful after rate limit periods expire (typically after 24 hours)
    """
    logger.info("🔄 Re-testing all API keys...")
    return test_all_keys_and_update_status()

def mark_key_rate_limited(api_key: str):
    """
    Mark an API key as rate limited (exhausted) and deactivate it
    This is called when a 429 error occurs
    """
    keys = load_api_keys()
    
    for key_data in keys:
        if key_data['key'] == api_key:
            logger.warning(f"⚠️ API key '{key_data.get('name')}' hit rate limit - marking inactive")
            key_data['active'] = False
            save_api_keys(keys)
            break

def get_next_api_key(current_key: str) -> str:
    """
    Get the next available API key when current one hits rate limit
    Tests each candidate key to ensure it works before returning
    
    Returns:
        str: Next working API key
    Raises:
        Exception: If no other working keys available
    """
    keys = load_api_keys()
    
    if not keys:
        raise Exception("No API keys configured")
    
    # Get name of current key for logging
    current_name = get_current_key_name(current_key)
    logger.warning(f"🔄 Rotating away from: {current_name}")
    
    # Mark current key as inactive (rate limited)
    mark_key_rate_limited(current_key)
    
    # Try to find another active key
    available_keys = [k for k in keys if k.get('active', False) and k['key'] != current_key]
    logger.info(f"📋 Found {len(available_keys)} other active keys to try")
    
    for key_data in available_keys:
        logger.info(f"🧪 Testing next API key: {key_data.get('name')}")
        
        # Test the key to make sure it works
        if test_api_key(key_data['key']):
            logger.info(f"✅ Successfully rotated to: {key_data.get('name')}")
            return key_data['key']
        else:
            # Mark as inactive if test fails
            logger.warning(f"❌ API key '{key_data.get('name')}' failed test, marking inactive")
            key_data['active'] = False
            save_api_keys(keys)
    
    raise Exception("No other working API keys available. All keys exhausted or failed.")

def ensure_api_health():
    """
    CRITICAL PRE-CHECK: Test the first active API key before starting debate
    Uses same 'Hello' message test as Settings
    
    Call this before:
    - Starting any debate
    
    This TESTS the key to verify it works, then updates JSON file if it fails
    
    Raises Exception if no working API found
    """
    logger.info("🔍 Checking API health before debate...")
    
    keys = load_api_keys()
    
    if not keys:
        raise Exception("No API keys configured. Please add API keys in Settings.")
    
    # Find and test active keys
    tested_any = False
    for key_data in keys:
        if key_data.get('active', False):
            key_name = key_data.get('name', 'Unnamed Key')
            logger.info(f"Testing API key: {key_name}")
            tested_any = True
            
            # Test it by sending 'Hello' message (same as Settings test)
            if test_api_key(key_data['key']):
                logger.info(f"✅ API health check PASSED - {key_name} is working")
                return True
            else:
                # Mark as inactive if test fails and save to JSON
                logger.warning(f"⚠️ API key '{key_name}' failed health check")
                key_data['active'] = False
                save_api_keys(keys)
                logger.info(f"💾 Updated {key_name} to inactive in JSON file")
    
    # No working key found
    if tested_any:
        raise Exception("All active API keys failed health check. Please test your API keys in Settings.")
    else:
        raise Exception("No active API keys available. Please test your API keys in Settings.")
