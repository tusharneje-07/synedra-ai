"""
Base Agent Class for Multi-Agent AI Council
============================================

This is the foundational class that all specialized agents inherit from.
It provides core functionality including:
- Markdown behavioral specification loading
- LLM integration (GROQ)
- Memory management
- Structured opinion generation
- Debate participation

Every agent MUST load its personality and rules from a .md file.

Author: AI Systems Engineer
Date: February 7, 2026
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

from groq import Groq
from langchain_groq import ChatGroq

from config.settings import get_settings
from memory.memory_manager import get_memory_manager
from graph.state_schema import (
    AgentProposal,
    AgentType,
    CouncilState,
    log_reasoning_step
)

logger = logging.getLogger(__name__)


class BaseLLMClient:
    """
    Wrapper for GROQ LLM client with retry logic and error handling.
    """
    
    def __init__(self):
        """Initialize GROQ client."""
        self.settings = get_settings()
        
        # Validate API key
        if not self.settings.validate_api_key():
            raise ValueError(
                "Invalid GROQ API key. Please set GROQ_API_KEY in .env file. "
                "Get your key from: https://console.groq.com/keys"
            )
        
        # Initialize GROQ client
        self.client = Groq(api_key=self.settings.groq_api_key)
        
        # LangChain wrapper for advanced features
        self.langchain_client = ChatGroq(
            groq_api_key=self.settings.groq_api_key,
            model_name=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.max_tokens
        )
        
        logger.info(f"LLM Client initialized with model: {self.settings.llm_model}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        max_retries: int = 3
    ) -> str:
        """
        Generate text using GROQ LLM with retry logic.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: Force JSON output
            max_retries: Maximum retry attempts
            
        Returns:
            Generated text
            
        Raises:
            Exception: If all retries fail
        """
        temp = temperature if temperature is not None else self.settings.llm_temperature
        tokens = max_tokens if max_tokens is not None else self.settings.max_tokens
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=tokens,
                    response_format={"type": "json_object"} if json_mode else {"type": "text"}
                )
                
                content = response.choices[0].message.content
                
                logger.debug(f"LLM generation successful (attempt {attempt + 1})")
                return content
                
            except Exception as e:
                last_error = e
                logger.warning(f"LLM generation attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
        
        raise Exception(f"LLM generation failed after {max_retries} attempts: {last_error}")
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON output from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            schema_description: Description of expected JSON schema
            
        Returns:
            Parsed JSON dictionary
        """
        # Enhance prompt for JSON output
        json_prompt = prompt
        if schema_description:
            json_prompt = f"{prompt}\n\nOutput format: {schema_description}"
        
        response = self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
            json_mode=True
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response: {response}")
            # Return a safe fallback
            return {"error": "JSON parsing failed", "raw_response": response}


class BaseAgent(ABC):
    """
    Base class for all council agents.
    
    This class provides core functionality that all specialized agents inherit.
    Each agent MUST load its behavior from a corresponding .md file.
    """
    
    def __init__(
        self,
        agent_name: str,
        agent_type: AgentType,
        behavior_file: str,
        voting_weight: float = 0.20
    ):
        """
        Initialize base agent.
        
        Args:
            agent_name: Human-readable agent name
            agent_type: Agent type from AgentType enum
            behavior_file: Name of markdown file (e.g., "TrendAgent.md")
            voting_weight: Initial voting weight (0-1)
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.voting_weight = voting_weight
        self.behavior_file = behavior_file
        
        # Initialize components
        self.settings = get_settings()
        self.memory = get_memory_manager()
        self.llm = BaseLLMClient()
        
        # Load behavioral specifications from markdown file
        self.behavior_spec = self._load_behavior_specification()
        
        # Build system prompt from markdown
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"Initialized {self.agent_name} ({self.agent_type})")
    
    # ========================================
    # BEHAVIORAL SPECIFICATION LOADING
    # ========================================
    
    def _load_behavior_specification(self) -> str:
        """
        Load agent behavior from markdown file.
        
        This is CRITICAL - the markdown file defines the agent's personality,
        objectives, constraints, and decision logic.
        
        Returns:
            Content of the markdown file
            
        Raises:
            FileNotFoundError: If markdown file doesn't exist
        """
        # Get path to behavior file
        behavior_path = self.settings.get_absolute_agent_definitions_path() / self.behavior_file
        
        if not behavior_path.exists():
            error_msg = (
                f"Behavior specification not found: {behavior_path}\n"
                f"Each agent MUST have a corresponding .md file in {self.settings.agent_definitions_path}"
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Load markdown content
        with open(behavior_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Loaded behavior spec for {self.agent_name} ({len(content)} chars)")
        return content
    
    def _build_system_prompt(self) -> str:
        """
        Build system prompt by injecting markdown behavior into template.
        
        This converts the markdown specification into an LLM system prompt
        that defines how the agent thinks and behaves.
        
        Returns:
            Formatted system prompt
        """
        system_prompt = f"""You are {self.agent_name}, an expert AI agent in a multi-agent marketing council.

CRITICAL BEHAVIORAL SPECIFICATION:
The following markdown document defines your COMPLETE personality, objectives, decision logic, and constraints.
You MUST adhere to these specifications in ALL your decisions and communications.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{self.behavior_spec}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPERATIONAL RULES:
1. You are part of a council with other specialized agents (Trend, Engagement, Brand, Risk, Compliance)
2. You will receive proposals and must provide structured opinions based on YOUR expertise
3. You may DISAGREE with other agents - conflict is expected and healthy
4. Your vote matters, but final decisions are made by the Arbitrator (CMO)
5. Always provide clear reasoning and evidence for your positions
6. Think step-by-step and consider multiple perspectives
7. Be honest about uncertainties and risks

OUTPUT FORMAT:
Always respond in valid JSON format with structured data.
Never output plain text - always use the requested JSON schema.

Remember: Your behavior file is your constitution. Follow it strictly."""

        return system_prompt
    
    # ========================================
    # MEMORY INTEGRATION
    # ========================================
    
    def _load_memory_context(
        self,
        current_situation: str,
        include_patterns: bool = True
    ) -> str:
        """
        Load relevant memories for current situation.
        
        Args:
            current_situation: Current situation/context
            include_patterns: Include pattern analysis
            
        Returns:
            Formatted memory context string
        """
        return self.memory.build_agent_context_prompt(
            agent_name=self.agent_name,
            current_situation=current_situation,
            include_patterns=include_patterns
        )
    
    def _store_decision_memory(
        self,
        context: str,
        decision: Dict[str, Any],
        reasoning: str,
        outcome: Optional[str] = None,
        importance: float = 0.5
    ):
        """
        Store a decision in agent's memory.
        
        Args:
            context: Decision context
            decision: The decision made
            reasoning: Reasoning behind decision
            outcome: Result (if known)
            importance: Importance score (0-1)
        """
        self.memory.store_memory(
            agent_name=self.agent_name,
            context=context,
            decision=decision,
            reasoning=reasoning,
            outcome=outcome,
            importance=importance
        )
    
    # ========================================
    # ABSTRACT METHODS (Must be implemented by subclasses)
    # ========================================
    
    @abstractmethod
    def analyze(
        self,
        state: CouncilState,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentProposal:
        """
        Analyze situation and generate proposal.
        
        This is the core method each agent must implement.
        It should analyze the current state and return a structured proposal.
        
        Args:
            state: Current council state
            context: Additional context (optional)
            
        Returns:
            Agent's structured proposal
        """
        pass
    
    @abstractmethod
    def debate(
        self,
        state: CouncilState,
        other_proposals: List[AgentProposal]
    ) -> Dict[str, Any]:
        """
        Participate in debate by responding to other proposals.
        
        Args:
            state: Current council state
            other_proposals: Proposals from other agents
            
        Returns:
            Debate response with updated position
        """
        pass
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _create_base_proposal(
        self,
        recommendation: str,
        confidence: float,
        reasoning: str,
        vote: str = "approve",
        concerns: Optional[List[str]] = None,
        conditions: Optional[List[str]] = None
    ) -> AgentProposal:
        """
        Create a base proposal structure.
        
        Args:
            recommendation: Agent's recommendation
            confidence: Confidence level (0-1)
            reasoning: Detailed reasoning
            vote: Vote (approve/reject/abstain/conditional)
            concerns: List of concerns
            conditions: Conditions if vote is conditional
            
        Returns:
            Base proposal structure
        """
        return AgentProposal(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            timestamp=datetime.now().isoformat(),
            recommendation=recommendation,
            confidence=confidence,
            priority="high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low",
            reasoning=reasoning,
            supporting_evidence=[],
            concerns=concerns or [],
            scores={},
            conflicts_with=[],
            vote=vote,
            conditions=conditions,
            metadata={}
        )
    
    def _generate_opinion(
        self,
        prompt: str,
        context: str,
        schema_description: str
    ) -> Dict[str, Any]:
        """
        Generate structured opinion using LLM.
        
        Args:
            prompt: Specific prompt for this decision
            context: Context and background
            schema_description: Description of expected JSON schema
            
        Returns:
            Structured opinion as dictionary
        """
        # Build full prompt with context
        full_prompt = f"""CONTEXT:
{context}

TASK:
{prompt}

Respond with structured JSON following this schema:
{schema_description}"""
        
        # Generate with LLM
        response = self.llm.generate_json(
            prompt=full_prompt,
            system_prompt=self.system_prompt,
            schema_description=schema_description
        )
        
        return response
    
    def extract_topic_from_state(self, state: CouncilState) -> str:
        """
        Extract the main topic/situation from council state.
        
        Args:
            state: Council state
            
        Returns:
            Topic string
        """
        return state.get('topic', 'Unknown topic')
    
    def get_voting_weight(self) -> float:
        """
        Get current voting weight.
        
        Returns:
            Current weight (0-1)
        """
        return self.voting_weight
    
    def update_voting_weight(self, new_weight: float):
        """
        Update voting weight (used for dynamic adjustment).
        
        Args:
            new_weight: New weight value (0-1)
        """
        old_weight = self.voting_weight
        self.voting_weight = max(0.05, min(0.40, new_weight))  # Clamp to reasonable range
        
        logger.info(
            f"{self.agent_name} weight updated: {old_weight:.3f} -> {self.voting_weight:.3f}"
        )
    
    def detect_conflicts(
        self,
        my_proposal: AgentProposal,
        other_proposals: List[AgentProposal]
    ) -> List[str]:
        """
        Detect conflicts with other agents' proposals.
        
        Args:
            my_proposal: This agent's proposal
            other_proposals: Other agents' proposals
            
        Returns:
            List of agent names with conflicting positions
        """
        conflicts = []
        my_vote = my_proposal.get('vote', 'abstain')
        
        for other in other_proposals:
            other_vote = other.get('vote', 'abstain')
            other_name = other.get('agent_name', 'Unknown')
            
            # Conflict if votes are opposite
            if (my_vote == 'approve' and other_vote == 'reject') or \
               (my_vote == 'reject' and other_vote == 'approve'):
                conflicts.append(other_name)
        
        return conflicts
    
    def __repr__(self) -> str:
        """String representation of agent."""
        return f"<{self.agent_name} ({self.agent_type}) weight={self.voting_weight:.2f}>"


class AgentFactory:
    """
    Factory for creating specialized agents.
    
    Supports all agent types:
    - TREND: Viral opportunity hunter
    - ENGAGEMENT: Community building specialist
    - BRAND: Voice consistency guardian
    - RISK: Safety and damage prevention
    - COMPLIANCE: Policy and legal enforcement
    - ARBITRATOR: CMO final decision maker
    """
    
    @staticmethod
    def create_agent(
        agent_type: AgentType,
        voting_weight: Optional[float] = None
    ) -> BaseAgent:
        """
        Create an agent instance by type.
        
        Args:
            agent_type: Type of agent to create
            voting_weight: Optional custom voting weight (uses default if None)
            
        Returns:
            Specialized agent instance
            
        Raises:
            ValueError: If agent_type is invalid
        """
        # Import specialized agents
        from agents.trend_agent import TrendAgent
        from agents.engagement_agent import EngagementAgent
        from agents.brand_agent import BrandAgent
        from agents.risk_agent import RiskAgent
        from agents.compliance_agent import ComplianceAgent
        from agents.arbitrator_agent import ArbitratorAgent
        
        # Agent type to class mapping
        agent_classes = {
            AgentType.TREND: TrendAgent,
            AgentType.ENGAGEMENT: EngagementAgent,
            AgentType.BRAND: BrandAgent,
            AgentType.RISK: RiskAgent,
            AgentType.COMPLIANCE: ComplianceAgent,
            AgentType.ARBITRATOR: ArbitratorAgent
        }
        
        # Get agent class
        agent_class = agent_classes.get(agent_type)
        
        if agent_class is None:
            raise ValueError(
                f"Invalid agent type: {agent_type}. "
                f"Valid types: {list(agent_classes.keys())}"
            )
        
        # Create agent with optional custom weight
        if voting_weight is not None:
            return agent_class(voting_weight=voting_weight)
        else:
            return agent_class()
    
    @staticmethod
    def create_full_council(
        custom_weights: Optional[Dict[AgentType, float]] = None
    ) -> Dict[AgentType, BaseAgent]:
        """
        Create a complete agent council with all 6 specialist types.
        
        Args:
            custom_weights: Optional dict mapping agent types to custom voting weights
            
        Returns:
            Dict mapping agent types to agent instances
            
        Example:
            >>> council = AgentFactory.create_full_council()
            >>> trend_agent = council[AgentType.TREND]
            >>> arbitrator = council[AgentType.ARBITRATOR]
        """
        custom_weights = custom_weights or {}
        
        council = {}
        
        for agent_type in AgentType:
            weight = custom_weights.get(agent_type)
            council[agent_type] = AgentFactory.create_agent(
                agent_type=agent_type,
                voting_weight=weight
            )
        
        logger.info(
            f"Full council created with {len(council)} agents: "
            f"{[a.value for a in council.keys()]}"
        )
        
        return council
    
    @staticmethod
    def get_default_weights() -> Dict[AgentType, float]:
        """
        Get default voting weights for all agent types.
        
        Returns:
            Dict mapping agent types to default weights
            
        Note:
            Weights typically sum to 1.0:
            - ARBITRATOR: 0.25 (CMO has highest weight)
            - BRAND: 0.20 (brand consistency critical)
            - RISK: 0.15 (safety important)
            - COMPLIANCE: 0.15 (legal requirements)
            - ENGAGEMENT: 0.13 (community value)
            - TREND: 0.12 (viral potential)
        """
        return {
            AgentType.ARBITRATOR: 0.25,
            AgentType.BRAND: 0.20,
            AgentType.RISK: 0.15,
            AgentType.COMPLIANCE: 0.15,
            AgentType.ENGAGEMENT: 0.13,
            AgentType.TREND: 0.12
        }
