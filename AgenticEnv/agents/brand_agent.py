"""
Brand Agent - BrandGuardian Architect
=====================================

This agent enforces brand consistency through measurable frameworks.
It loads its complete behavioral specification from BrandAgent.md.

Role: Maintain 85%+ brand consistency while allowing 15% experimental variance
Mindset: "Every post is a brand deposit or withdrawal. We optimize for compound trust."

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import Dict, List, Optional, Any

from agents.base_agent import BaseAgent
from graph.state_schema import (
    CouncilState,
    BrandAgentProposal,
    AgentProposal,
    AgentType,
    Platform
)

logger = logging.getLogger(__name__)


class BrandAgent(BaseAgent):
    """
    Brand Agent - Guardian of brand voice and consistency.
    
    Personality Traits (from BrandAgent.md):
    - Measurable scoring (no subjective "feels off-brand")
    - Self-learning brand DNA
    - Auto-rewrite capability
    - Platform-aware voice adaptation
    - Evidence-based debate system
    - Time-decay fatigue detection
    
    Focus Areas:
    - Tone alignment scoring (0-100)
    - Brand consistency measurement
    - Fatigue risk detection
    - Platform adaptation
    - Voice issue identification
    - Auto-rewrite suggestions
    """
    
    def __init__(self, voting_weight: float = 0.25):
        """
        Initialize Brand Agent.
        
        Args:
            voting_weight: Initial voting weight (higher for brand protection)
        """
        super().__init__(
            agent_name="BrandGuardian Architect",
            agent_type=AgentType.BRAND,
            behavior_file="BrandAgent.md",
            voting_weight=voting_weight
        )
        
        logger.info("BrandAgent initialized and ready to guard brand voice")
    
    def analyze(
        self,
        state: CouncilState,
        context: Optional[Dict[str, Any]] = None
    ) -> BrandAgentProposal:
        """
        Analyze brand alignment and generate voice consistency proposal.
        
        Args:
            state: Current council state
            context: Additional context
            
        Returns:
            BrandAgentProposal with brand consistency assessment
        """
        topic = self.extract_topic_from_state(state)
        platform = state.get('platform', Platform.INSTAGRAM)
        
        # Load memory context
        memory_context = self._load_memory_context(
            current_situation=f"Brand analysis for: {topic}",
            include_patterns=True
        )
        
        # Build analysis prompt
        analysis_prompt = f"""
SITUATION: {topic}

TARGET PLATFORM: {platform}

TASK:
Analyze this content for BRAND CONSISTENCY and VOICE ALIGNMENT.

Apply your measurable scoring framework:

1. TONE ALIGNMENT SCORE (0-100):
   - Vocabulary match (30pts): Word choice vs brand lexicon
   - Sentence structure (20pts): Simple/complex ratio
   - Emotional valence (25pts): Positive/neutral/authoritative
   - Punctuation style (15pts): Exclamation marks, questions
   - Brand archetype (10pts): Hero/Sage/Rebel consistency

2. BRAND CONSISTENCY SCORE (0-100):
   - Overall alignment with brand DNA

3. FATIGUE RISK (0-1):
   - Has this topic/angle been overused recently?
   - Time-decay detection

4. PLATFORM ADAPTATION:
   - Does tone need adjustment for this platform?
   - Different platforms = different voice nuances

5. VOICE ISSUES:
   - List any specific problems (too casual, too corporate, etc.)

6. REWRITE SUGGESTIONS:
   - If score < 75, provide rewrite recommendations

SCORING THRESHOLDS:
- 90-100: Perfect (approve immediately)
- 75-89: Acceptable (minor tweaks optional)
- 60-74: Needs work (trigger rewrite)
- <60: Rejected (hard block)

Remember: "Every post is a brand deposit or withdrawal. Optimize for compound trust, not viral spikes."

Provide analysis in JSON format with:
- tone_alignment_score: float (0-100)
- brand_consistency_score: float (0-100)
- fatigue_risk: float (0-1)
- voice_issues: array of strings
- rewrite_suggestions: string (or null if not needed)
- platform_adaptation_needed: boolean
- recommendation: string
- confidence: float (0-1)
- reasoning: string
- concerns: array
- vote: string (approve if >75, conditional if 60-74, reject if <60)
"""
        
        schema_description = """
{
    "tone_alignment_score": 0-100,
    "brand_consistency_score": 0-100,
    "fatigue_risk": 0.0-1.0,
    "voice_issues": ["issue1", "issue2"],
    "rewrite_suggestions": "suggestions or null",
    "platform_adaptation_needed": true/false,
    "recommendation": "detailed recommendation",
    "confidence": 0.0-1.0,
    "reasoning": "scoring breakdown and analysis",
    "concerns": ["concern1"],
    "vote": "approve/reject/conditional"
}
"""
        
        opinion = self._generate_opinion(
            prompt=analysis_prompt,
            context=memory_context,
            schema_description=schema_description
        )
        
        # Build specialized BrandAgentProposal
        proposal = BrandAgentProposal(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            timestamp=self._get_timestamp(),
            
            # Core proposal fields
            recommendation=opinion.get('recommendation', 'No recommendation generated'),
            confidence=opinion.get('confidence', 0.5),
            priority=self._calculate_priority_from_scores(
                opinion.get('tone_alignment_score', 75),
                opinion.get('brand_consistency_score', 75)
            ),
            reasoning=opinion.get('reasoning', 'No reasoning provided'),
            supporting_evidence=[
                f"Tone alignment: {opinion.get('tone_alignment_score', 0)}/100",
                f"Brand consistency: {opinion.get('brand_consistency_score', 0)}/100",
                f"Fatigue risk: {opinion.get('fatigue_risk', 0):.0%}"
            ],
            concerns=opinion.get('concerns', []),
            scores={
                'tone_alignment': opinion.get('tone_alignment_score', 75) / 100,
                'brand_consistency': opinion.get('brand_consistency_score', 75) / 100,
                'fatigue_risk': opinion.get('fatigue_risk', 0.0)
            },
            conflicts_with=[],
            vote=opinion.get('vote', 'conditional'),
            conditions=None,
            
            # Brand-specific fields
            tone_alignment_score=opinion.get('tone_alignment_score', 75.0),
            brand_consistency_score=opinion.get('brand_consistency_score', 75.0),
            fatigue_risk=opinion.get('fatigue_risk', 0.0),
            rewrite_suggestions=opinion.get('rewrite_suggestions', None),
            voice_issues=opinion.get('voice_issues', []),
            platform_adaptation_needed=opinion.get('platform_adaptation_needed', False),
            
            metadata={
                'brand_analysis_version': '1.0',
                'analysis_timestamp': self._get_timestamp(),
                'scoring_framework': 'measurable_brand_framework_v1'
            }
        )
        
        # Store in memory
        self._store_decision_memory(
            context=f"Brand analysis: {topic}",
            decision={
                'tone_score': proposal['tone_alignment_score'],
                'consistency_score': proposal['brand_consistency_score'],
                'vote': proposal['vote']
            },
            reasoning=proposal['reasoning'],
            importance=proposal['confidence']
        )
        
        logger.info(
            f"BrandAgent analysis complete: "
            f"Tone {proposal['tone_alignment_score']:.0f}/100, "
            f"Consistency {proposal['brand_consistency_score']:.0f}/100, "
            f"Vote: {proposal['vote']}"
        )
        
        return proposal
    
    def debate(
        self,
        state: CouncilState,
        other_proposals: List[AgentProposal]
    ) -> Dict[str, Any]:
        """
        Participate in debate defending brand consistency.
        
        BrandAgent typically:
        - Argues with Trend Agent about "brand dilution"
        - Uses measurable scores to back arguments
        - Offers rewrite suggestions as compromise
        - Emphasizes long-term brand equity
        - Firm on hard boundaries (<60 score = block)
        
        Args:
            state: Current council state
            other_proposals: Proposals from other agents
            
        Returns:
            Debate response with updated position
        """
        topic = self.extract_topic_from_state(state)
        
        # Check if Trend Agent is pushing risky content
        trend_pushing_hard = False
        for proposal in other_proposals:
            if proposal.get('agent_type') == AgentType.TREND:
                if proposal.get('vote') == 'approve' and proposal.get('confidence', 0) > 0.8:
                    trend_pushing_hard = True
                    break
        
        debate_prompt = f"""
DEBATE SITUATION:
Topic: {topic}

OTHER AGENTS' POSITIONS:
{self._format_other_proposals(other_proposals)}

YOUR ROLE IN DEBATE:
You are BrandAgent - guardian of brand voice with MEASURABLE standards.

Your mindset: "Every post is a brand deposit or withdrawal. Optimize for compound trust."

TASK:
Respond to other agents, especially if trend/viral focus threatens brand consistency.

Your arguments should use:
- Specific scores (tone: X/100, consistency: Y/100)
- Evidence-based reasoning, not subjective feelings
- Rewrite suggestions as compromise (not outright rejection)
- Long-term brand equity arguments
- Platform-specific voice adaptation needs

If scores are:
- >90: Approve enthusiastically
- 75-89: Approve with minor suggestions
- 60-74: Conditional (require rewrites)
- <60: Hard block (brand damage risk)

Provide:
1. Score-based defense of your position
2. Rewrite alternatives if needed
3. Compromise options
4. Final vote

Respond in JSON format.
"""
        
        schema = """
{
    "score_based_defense": "using measurable scores",
    "rewrite_alternatives": "suggested improvements",
    "compromise_position": "middle ground if possible",
    "brand_equity_argument": "long-term impact",
    "final_vote": "approve/reject/conditional",
    "hard_boundaries": ["non-negotiable item1"]
}
"""
        
        debate_response = self._generate_opinion(
            prompt=debate_prompt,
            context="",
            schema_description=schema
        )
        
        logger.info(f"BrandAgent debate response: {debate_response.get('final_vote', 'unknown')}")
        
        return {
            'agent_name': self.agent_name,
            'debate_response': debate_response,
            'uses_measurable_scores': True,
            'offers_rewrites': debate_response.get('rewrite_alternatives') is not None,
            'final_vote': debate_response.get('final_vote', 'conditional')
        }
    
    def _calculate_priority_from_scores(self, tone_score: float, consistency_score: float) -> str:
        """Calculate priority from brand scores."""
        avg_score = (tone_score + consistency_score) / 2
        if avg_score >= 90:
            return "high"  # Approve immediately
        elif avg_score >= 75:
            return "medium"  # Acceptable
        else:
            return "low"  # Needs work or reject
    
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
                f"Confidence={p.get('confidence', 0):.0%}, "
                f"Key concern: {p.get('concerns', ['None'])[0] if p.get('concerns') else 'None'}"
            )
        return "\n".join(formatted) if formatted else "No other proposals yet"
