"""
Trend Agent - Viral Opportunity Hunter
=======================================

This agent specializes in identifying and capitalizing on viral trends.
It loads its complete behavioral specification from TrendAgent.md.

Role: Maximize virality and engagement through trend exploitation
Mindset: "If people aren't talking about it, it's dead content"

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import Dict, List, Optional, Any

from agents.base_agent import BaseAgent
from graph.state_schema import (
    CouncilState,
    TrendAgentProposal,
    AgentProposal,
    AgentType,
    Platform
)

logger = logging.getLogger(__name__)


class TrendAgent(BaseAgent):
    """
    Trend Agent - Hunts viral opportunities and maximizes reach.
    
    Personality Traits (from TrendAgent.md):
    - Aggressive optimizer
    - Opportunistic
    - Fast decision maker
    - Pattern hunter
    - Slightly rebellious (argues with Brand Agent)
    
    Focus Areas:
    - Viral probability scoring
    - Trend lifespan estimation
    - Shareability analysis
    - Meme adaptability
    - Engagement potential
    """
    
    def __init__(self, voting_weight: float = 0.20):
        """
        Initialize Trend Agent.
        
        Args:
            voting_weight: Initial voting weight in council
        """
        super().__init__(
            agent_name="TrendPulse Strategist",
            agent_type=AgentType.TREND,
            behavior_file="TrendAgent.md",
            voting_weight=voting_weight
        )
        
        logger.info("TrendAgent initialized and ready to hunt viral opportunities")
    
    def analyze(
        self,
        state: CouncilState,
        context: Optional[Dict[str, Any]] = None
    ) -> TrendAgentProposal:
        """
        Analyze trends and generate viral opportunity proposal.
        
        Args:
            state: Current council state
            context: Additional context (trend data, metrics, etc.)
            
        Returns:
            TrendAgentProposal with viral opportunity assessment
        """
        topic = self.extract_topic_from_state(state)
        platform = state.get('platform', Platform.INSTAGRAM)
        
        # Load memory context
        memory_context = self._load_memory_context(
            current_situation=f"Trend analysis for: {topic}",
            include_patterns=True
        )
        
        # Build analysis prompt
        analysis_prompt = f"""
SITUATION: {topic}

TARGET PLATFORM: {platform}

TASK:
Analyze this topic for viral potential and recommend a trend-based strategy.
Consider:
1. Current trending topics that align with this
2. Viral probability (0-1 score)
3. Estimated trend lifespan
4. Best content angle for maximum shareability
5. Hook line that will grab attention
6. Engagement potential score

Remember your role: You prioritize VIRALITY and REACH above all else.
You are aggressive and opportunistic - if there's a trend to exploit, recommend it.

Provide your analysis in JSON format with these fields:
- trend_topic: string (the specific trend to leverage)
- viral_probability: float (0-1)
- trend_lifespan: string (e.g., "3-5 days", "1-2 weeks")
- platform_recommendation: string (best platform for this trend)
- content_angle: string (unique angle to take)
- hook_line: string (attention-grabbing first line)
- engagement_potential: float (0-1)
- recommendation: string (your overall recommendation)
- confidence: float (0-1)
- reasoning: string (detailed explanation)
- concerns: array of strings (any risks you foresee)
- vote: string ("approve", "reject", "conditional")
"""
        
        # Generate opinion using LLM
        schema_description = """
{
    "trend_topic": "specific trend name",
    "viral_probability": 0.0-1.0,
    "trend_lifespan": "X-Y days/weeks",
    "platform_recommendation": "platform name",
    "content_angle": "unique angle description",
    "hook_line": "catchy first line",
    "engagement_potential": 0.0-1.0,
    "recommendation": "detailed recommendation",
    "confidence": 0.0-1.0,
    "reasoning": "why this will work",
    "concerns": ["concern1", "concern2"],
    "vote": "approve/reject/conditional"
}
"""
        
        opinion = self._generate_opinion(
            prompt=analysis_prompt,
            context=memory_context,
            schema_description=schema_description
        )
        
        # Build specialized TrendAgentProposal
        proposal = TrendAgentProposal(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            timestamp=self._get_timestamp(),
            
            # Core proposal fields
            recommendation=opinion.get('recommendation', 'No recommendation generated'),
            confidence=opinion.get('confidence', 0.5),
            priority=self._calculate_priority(opinion.get('confidence', 0.5)),
            reasoning=opinion.get('reasoning', 'No reasoning provided'),
            supporting_evidence=[
                f"Viral probability: {opinion.get('viral_probability', 0):.0%}",
                f"Engagement potential: {opinion.get('engagement_potential', 0):.0%}",
                f"Trend lifespan: {opinion.get('trend_lifespan', 'unknown')}"
            ],
            concerns=opinion.get('concerns', []),
            scores={
                'viral_probability': opinion.get('viral_probability', 0.5),
                'engagement_potential': opinion.get('engagement_potential', 0.5),
                'shareability': opinion.get('viral_probability', 0.5) * 0.9
            },
            conflicts_with=[],
            vote=opinion.get('vote', 'approve'),
            conditions=None,
            
            # Trend-specific fields
            trend_topic=opinion.get('trend_topic', topic),
            viral_probability=opinion.get('viral_probability', 0.5),
            trend_lifespan=opinion.get('trend_lifespan', 'unknown'),
            platform_recommendation=Platform(opinion.get('platform_recommendation', platform).lower()) if opinion.get('platform_recommendation') else platform,
            content_angle=opinion.get('content_angle', 'Standard approach'),
            hook_line=opinion.get('hook_line', 'Attention-grabbing content'),
            engagement_potential=opinion.get('engagement_potential', 0.5),
            
            metadata={
                'trend_analysis_version': '1.0',
                'analysis_timestamp': self._get_timestamp()
            }
        )
        
        # Store in memory
        self._store_decision_memory(
            context=f"Trend analysis: {topic}",
            decision={
                'trend_topic': proposal['trend_topic'],
                'viral_probability': proposal['viral_probability'],
                'vote': proposal['vote']
            },
            reasoning=proposal['reasoning'],
            importance=proposal['confidence']
        )
        
        logger.info(
            f"TrendAgent analysis complete: {proposal['trend_topic']} "
            f"(viral: {proposal['viral_probability']:.0%}, vote: {proposal['vote']})"
        )
        
        return proposal
    
    def debate(
        self,
        state: CouncilState,
        other_proposals: List[AgentProposal]
    ) -> Dict[str, Any]:
        """
        Participate in debate by defending viral opportunities.
        
        TrendAgent typically:
        - Pushes hard for trending content
        - Argues with Brand Agent about "playing it safe"
        - Emphasizes time sensitivity
        - Uses pressure language like "we're missing the wave"
        
        Args:
            state: Current council state
            other_proposals: Proposals from other agents
            
        Returns:
            Debate response with updated position
        """
        topic = self.extract_topic_from_state(state)
        
        # Identify conflicts
        my_vote = "approve"  # Trend agent usually approves viral content
        conflicts = []
        brand_concerns = []
        risk_concerns = []
        
        for proposal in other_proposals:
            agent_name = proposal.get('agent_name', '')
            vote = proposal.get('vote', 'abstain')
            
            if vote == 'reject' or vote == 'conditional':
                conflicts.append(agent_name)
                
                if 'Brand' in agent_name:
                    brand_concerns.extend(proposal.get('concerns', []))
                elif 'Risk' in agent_name:
                    risk_concerns.extend(proposal.get('concerns', []))
        
        # Build debate prompt
        debate_prompt = f"""
DEBATE SITUATION:
Topic: {topic}

OTHER AGENTS' POSITIONS:
{self._format_other_proposals(other_proposals)}

YOUR ROLE IN DEBATE:
You are TrendAgent - aggressive, opportunistic, focused on VIRALITY.

TASK:
Respond to other agents' concerns while defending your viral opportunity recommendation.

Use your characteristic debate style:
- "We are missing the wave"
- "If we post late, competitor will take it"
- "This is perfect for engagement"
- "Brand safety is fine, we can soften tone"

Provide:
1. Response to concerns (especially from Brand/Risk agents)
2. Counter-arguments emphasizing time sensitivity
3. Adjusted position if needed (or double-down)
4. Final vote (approve/reject/conditional)

Respond in JSON format.
"""
        
        schema = """
{
    "response_to_concerns": "your counter-arguments",
    "time_sensitivity_argument": "why we must act now",
    "adjusted_position": "any changes to your recommendation",
    "final_vote": "approve/reject/conditional",
    "pressure_points": ["argument1", "argument2"]
}
"""
        
        debate_response = self._generate_opinion(
            prompt=debate_prompt,
            context="",
            schema_description=schema
        )
        
        logger.info(f"TrendAgent debate response: {debate_response.get('final_vote', 'unknown')}")
        
        return {
            'agent_name': self.agent_name,
            'debate_response': debate_response,
            'conflicts_addressed': conflicts,
            'maintains_position': debate_response.get('final_vote', 'approve') == 'approve'
        }
    
    def _calculate_priority(self, confidence: float) -> str:
        """Calculate priority level from confidence."""
        if confidence > 0.8:
            return "high"
        elif confidence > 0.5:
            return "medium"
        else:
            return "low"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _format_other_proposals(self, proposals: List[AgentProposal]) -> str:
        """Format other proposals for debate context."""
        formatted = []
        for p in proposals:
            formatted.append(
                f"- {p.get('agent_name', 'Unknown')}: "
                f"Vote={p.get('vote', 'unknown')}, "
                f"Confidence={p.get('confidence', 0):.0%}"
            )
        return "\n".join(formatted) if formatted else "No other proposals yet"
