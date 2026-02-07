"""
Groq LLM Client - Simple wrapper for Groq API calls
Handles all LLM interactions without LangChain
CRITICAL: Uses api_manager to ensure healthy API before each call
"""

import os
from typing import Dict, List, Optional, Any
import logging
from groq import Groq

logger = logging.getLogger(__name__)

class LLMClient:
    """Simple Groq LLM client for agent interactions"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Groq client"""
        # Import here to avoid circular imports
        from utils.api_manager import get_active_api_key, get_current_key_name
        
        # Get working API key from pool
        if not api_key:
            try:
                self.api_key = get_active_api_key()
                key_name = get_current_key_name(self.api_key)
                logger.info(f"🔑 Initialized with API key: {key_name}")
            except Exception as e:
                # Fallback to env variable
                self.api_key = os.getenv('GROQ_API_KEY')
                if not self.api_key:
                    raise ValueError(f"No working API keys available: {str(e)}")
                logger.info("🔑 Using API key from environment variable")
        else:
            self.api_key = api_key
            logger.info("🔑 Using provided API key")
            
        self.model = model or os.getenv('LLM_MODEL', 'llama-3.3-70b-versatile')
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '4096'))
        
        # Initialize Groq client
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info(f"LLM Client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            raise
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        _retry_count: int = 0
    ) -> str:
        """
        Send a chat completion request to Groq
        Automatically rotates API keys on rate limit errors (429)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: Force JSON output format
            _retry_count: Internal retry counter
            
        Returns:
            str: The assistant's response
        """
        try:
            # Prepare parameters
            params = {
                'model': self.model,
                'messages': messages,
                'temperature': temperature or self.temperature,
                'max_tokens': max_tokens or self.max_tokens,
            }
            
            # Add JSON mode if requested
            if json_mode:
                params['response_format'] = {"type": "json_object"}
            
            # Make API call
            response = self.client.chat.completions.create(**params)
            
            # Extract and return content
            content = response.choices[0].message.content
            return content
            
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a rate limit error (429)
            if "429" in error_str or "rate_limit" in error_str.lower():
                logger.warning(f"⚠️ Rate limit hit! Error: {error_str}")
                
                # Prevent infinite retry loop
                if _retry_count >= 3:
                    logger.error("❌ All API keys exhausted after 3 retries")
                    raise Exception("All API keys have hit rate limits. Please wait or add more keys.")
                
                try:
                    # Import here to avoid circular imports
                    from utils.api_manager import get_next_api_key, get_current_key_name
                    
                    # Try to get next API key
                    logger.info(f"🔄 Attempting to switch to next API key (retry {_retry_count + 1}/3)...")
                    new_key = get_next_api_key(self.api_key)
                    
                    # Update client with new key
                    self.api_key = new_key
                    self.client = Groq(api_key=new_key)
                    new_key_name = get_current_key_name(new_key)
                    logger.info(f"✅ Successfully switched to: {new_key_name}")
                    
                    # Retry the request with new key
                    return self.chat(
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        json_mode=json_mode,
                        _retry_count=_retry_count + 1
                    )
                    
                except Exception as rotation_error:
                    logger.error(f"❌ Failed to rotate API key: {rotation_error}")
                    raise Exception(f"Rate limit reached and no backup API keys available: {rotation_error}")
            
            # Not a rate limit error, or other error - just log and raise
            logger.error(f"Error in LLM chat completion: {e}")
            logger.error(f"Model: {self.model}, Messages count: {len(messages)}, JSON mode: {json_mode}")
            logger.error(f"Full error details: {str(e)}", exc_info=True)
            raise
    
    def simple_prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> str:
        """
        Simple prompt wrapper for single-turn conversations
        
        Args:
            prompt: The user prompt
            system_message: Optional system message to set context
            temperature: Override default temperature
            json_mode: Force JSON output format
            
        Returns:
            str: The assistant's response
        """
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({
                'role': 'system',
                'content': system_message
            })
        
        # Add user prompt
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        return self.chat(
            messages=messages,
            temperature=temperature,
            json_mode=json_mode
        )
    
    def analyze_with_context(
        self,
        analysis_prompt: str,
        context: Dict[str, Any],
        system_role: str,
        json_mode: bool = True
    ) -> str:
        """
        Analyze with structured context (for agents)
        
        Args:
            analysis_prompt: The specific analysis task
            context: Context data (brand info, post details, etc.)
            system_role: The system role/persona for the agent
            json_mode: Force JSON output (default True for agents)
            
        Returns:
            str: The analysis response
        """
        # Build context string
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        
        # Build full prompt
        full_prompt = f"""
Context:
{context_str}

Task:
{analysis_prompt}
"""
        
        return self.simple_prompt(
            prompt=full_prompt,
            system_message=system_role,
            json_mode=json_mode
        )


# Singleton instance
_llm_client = None

def get_llm_client() -> LLMClient:
    """Get singleton LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
