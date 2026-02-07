"""
Engagement Agent - Community Magnet Strategist
==============================================

This agent specializes in building meaningful audience engagement.
It loads its complete behavioral specification from EngagementAgent.md.

Role: Maximize meaningful engagement, not just reach
Mindset: "Virality is temporary. Engagement builds loyal audience."

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import Dict, List, Optional, Any

from agents.base_agent import BaseAgent
from graph.state_schema import (
    CouncilState,
    EngagementAgentProposal,
    AgentProposal,
    AgentType,
    Platform
)

logger = logging.getLogger(__name__)


class EngagementAgent(BaseAgent):
    """
    Engagement Agent - Turns viewers into active participants.
    
    Personality Traits (from EngagementAgent.md):
    - Conversation engineer
    - Emotional manipulator (marketing context)
    - Psychology-driven
    - Interactive addict
    - Community-first
    
    Focus Areas:
    - Comment triggers
    - Save rate optimization
    - Share mechanics
    - Watch time / retention
    - DM triggers
    - Community sentiment
    """
    
    def __init__(self, voting_weight: float = 0.20):
        """
        Initialize Engagement Agent.
        
        Args:
            voting_weight: Initial voting weight in council
        """
        super().__init__(
            agent_name="Community Magnet Strategist",
            agent_type=AgentType.ENGAGEMENT,
            behavior_file="EngagementAgent.md",
            voting_weight=voting_weight
        )
        
        logger.info("EngagementAgent initialized and ready to build communities")
    
    def analyze(
        self,
        state: CouncilState,
        context: Optional[Dict[str, Any]] = None
    ) -> EngagementAgentProposal:
        """
        Analyze engagement potential and generate community-building proposal.
        
        Args:
            state: Current council state
            context: Additional context
            
        Returns:
            EngagementAgentProposal with interaction strategy
        """
        topic = self.extract_topic_from_state(state)
        platform = state.get('platform', Platform.INSTAGRAM)
        
        # Load memory context
        memory_context = self._load_memory_context(
            current_situation=f"Engagement analysis for: {topic}",
            include_patterns=True
        )
        
        # Build analysis prompt
        analysis_prompt = f"""
SITUATION: {topic}

TARGET PLATFORM: {platform}

TASK:
Analyze this for ENGAGEMENT POTENTIAL - not just views, but active participation.

Focus on:
1. Comment trigger strength (will people reply?)
2. Shareability score (will they tag friends?)
3. Relatability score (will they connect personally?)
4. Emotional hook (what emotion drives interaction?)
5. Interaction format (polls, questions, "this or that", etc.)
6. Community building potential

Use psychological triggers:
- FOMO, curiosity gap, social proof
- Micro-conflict, identity-based hooks
- "Real developers know this..." type framing

Remember: Your goal is MEANINGFUL ENGAGEMENT, not viral spikes.
Comments > Views. Saves > Likes. Community > Reach.

Provide analysis in JSON format with:
- comment_trigger_strength: float (0-1)
- shareability_score: float (0-1)
- relatability_score: float (0-1)
- emotional_hook: string (what emotion to trigger)
- interaction_format: string (poll, question, quiz, etc.)
- community_building_score: float (0-1)
- recommendation: string
- confidence: float (0-1)
- reasoning: string
- concerns: array
- vote: string
"""
        
        schema_description = """
{
    "comment_trigger_strength": 0.0-1.0,
    "shareability_score": 0.0-1.0,
    "relatability_score": 0.0-1.0,
    "emotional_hook": "emotion name and strategy",
    "interaction_format": "format type",
    "community_building_score": 0.0-1.0,
    "recommendation": "detailed recommendation",
    "confidence": 0.0-1.0,
    "reasoning": "why this will drive engagement",
    "concerns": ["concern1"],
    "vote": "approve/reject/conditional"
}
"""
        
        opinion = self._generate_opinion(
            prompt=analysis_prompt,
            context=memory_context,
            schema_description=schema_description
        )
        
        # Build specialized EngagementAgentProposal
        proposal = EngagementAgentProposal(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            timestamp=self._get_timestamp(),
            
            # Core proposal fields
            recommendation=opinion.get('recommendation', 'No recommendation generated'),
            confidence=opinion.get('confidence', 0.5),
            priority=self._calculate_priority(opinion.get('confidence', 0.5)),
            reasoning=opinion.get('reasoning', 'No reasoning provided'),
            supporting_evidence=[
                f"Comment trigger: {opinion.get('comment_trigger_strength', 0):.0%}",
                f"Shareability: {opinion.get('shareability_score', 0):.0%}",
                f"Community building: {opinion.get('community_building_score', 0):.0%}"
            ],
            concerns=opinion.get('concerns', []),
            scores={
                'comment_trigger': opinion.get('comment_trigger_strength', 0.5),
                'shareability': opinion.get('shareability_score', 0.5),
                'relatability': opinion.get('relatability_score', 0.5),
                'community_building': opinion.get('community_building_score', 0.5)
            },
            conflicts_with=[],
            vote=opinion.get('vote', 'approve'),
            conditions=None,
            
            # Engagement-specific fields
            comment_trigger_strength=opinion.get('comment_trigger_strength', 0.5),
            shareability_score=opinion.get('shareability_score', 0.5),
            relatability_score=opinion.get('relatability_score', 0.5),
            emotional_hook=opinion.get('emotional_hook', 'curiosity'),
            interaction_format=opinion.get('interaction_format', 'question'),
            community_building_score=opinion.get('community_building_score', 0.5),
            
            metadata={
                'engagement_analysis_version': '1.0',
                'analysis_timestamp': self._get_timestamp()
            }
        )
        
        # Store in memory
        self._store_decision_memory(
            context=f"Engagement analysis: {topic}",
            decision={
                'comment_trigger_strength': proposal['comment_trigger_strength'],
                'interaction_format': proposal['interaction_format'],
                'vote': proposal['vote']
            },
            reasoning=proposal['reasoning'],
            importance=proposal['confidence']
        )
        
        logger.info(
            f"EngagementAgent analysis complete: "
            f"Comment trigger {proposal['comment_trigger_strength']:.0%}, "
            f"Format: {proposal['interaction_format']}, "
            f"Vote: {proposal['vote']}"
        )
        
        return proposal
    
    def debate(
        self,
        state: CouncilState,
        other_proposals: List[AgentProposal]
    ) -> Dict[str, Any]:
        """
        Participate in debate emphasizing community over virality.
        
        EngagementAgent typically:
        - Argues for sustainable community building
        - Counters Trend Agent's "quick win" mentality
        - Emphasizes long-term audience loyalty
        - Focuses on meaningful metrics (saves, comments) over vanity metrics (views)
        
        Args:
            state: Current council state
            other_proposals: Proposals from other agents
            
        Returns:
            Debate response with updated position
        """
        topic = self.extract_topic_from_state(state)
        
        # Identify trend agent's position for potential conflict
        trend_focus = None
        for proposal in other_proposals:
            if proposal.get('agent_type') == AgentType.TREND:
                trend_focus = proposal.get('recommendation', '')
                break
        
        debate_prompt = f"""
DEBATE SITUATION:
Topic: {topic}

OTHER AGENTS' POSITIONS:
{self._format_other_proposals(other_proposals)}

YOUR ROLE IN DEBATE:
You are EngagementAgent - focused on SUSTAINABLE community building, not viral spikes.

Your perspective:
"Virality is temporary. Engagement builds loyal audience."

TASK:
Respond to other agents' positions, especially if Trend Agent is pushing for quick virality.

Your arguments should emphasize:
- Comments > Views
- Saves > Likes  
- Community loyalty > One-time reach
- Long-term audience relationships
- Meaningful interaction formats

Provide:
1. Response to virality-focused proposals
2. Defense of community-building approach
3. Compromise position if needed
4. Final vote

Respond in JSON format.
"""
        
        schema = """
{
    "response_to_virality_focus": "counter-argument for sustainable engagement",
    "community_building_defense": "why long-term matters",
    "compromise_position": "any adjusted recommendation",
    "final_vote": "approve/reject/conditional",
    "key_metrics_emphasis": ["metric1", "metric2"]
}
"""
        
        debate_response = self._generate_opinion(
            prompt=debate_prompt,
            context="",
            schema_description=schema
        )
        
        logger.info(f"EngagementAgent debate response: {debate_response.get('final_vote', 'unknown')}")
        
        return {
            'agent_name': self.agent_name,
            'debate_response': debate_response,
            'emphasizes_community': True,
            'final_vote': debate_response.get('final_vote', 'conditional')
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
                f"- {p.get('agent_name', 'Unknown')} ({p.get('agent_type', 'unknown')}): "
                f"Vote={p.get('vote', 'unknown')}, "
                f"Confidence={p.get('confidence', 0):.0%}"
            )
        return "\n".join(formatted) if formatted else "No other proposals yet"
