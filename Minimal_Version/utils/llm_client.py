"""
Groq LLM Client - Simple wrapper for Groq API calls
Handles all LLM interactions without LangChain
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
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.model = model or os.getenv('LLM_MODEL', 'llama-3.3-70b-versatile')
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '4096'))
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Initialize Groq client without proxies argument
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
        json_mode: bool = False
    ) -> str:
        """
        Send a chat completion request to Groq
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: Force JSON output format
            
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
            logger.error(f"Error in LLM chat completion: {e}")
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
