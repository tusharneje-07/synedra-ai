"""
Risk Agent - Reputation Shield Officer
======================================

This agent specializes in preventing brand damage before it happens.
It loads its complete behavioral specification from RiskAgent.md.

Role: Ensure every content piece is safe, non-offensive, and compliant
Mindset: "One bad post can destroy months of brand trust."

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import Dict, List, Optional, Any

from agents.base_agent import BaseAgent
from graph.state_schema import (
    CouncilState,
    RiskAgentProposal,
    AgentProposal,
    AgentType,
    Platform
)

logger = logging.getLogger(__name__)


class RiskAgent(BaseAgent):
    """
    Risk Agent - Prevents brand damage and reputation crises.
    
    Personality Traits (from RiskAgent.md):
    - Cold, analytical, serious
    - Worst-case thinker
    - Paranoid investigator
    - Policy lawyer type
    - Pattern memory expert
    
    Focus Areas:
    - Controversy probability scoring
    - Brand backlash risk assessment
    - Platform ban probability
    - Toxicity detection
    - Misinformation risk
    - Sensitive topic identification
    """
    
    def __init__(self, voting_weight: float = 0.20):
        """
        Initialize Risk Agent.
        
        Args:
            voting_weight: Initial voting weight in council
        """
        super().__init__(
            agent_name="Reputation Shield Officer",
            agent_type=AgentType.RISK,
            behavior_file="RiskAgent.md",
            voting_weight=voting_weight
        )
        
        logger.info("RiskAgent initialized and ready to prevent brand damage")
    
    def analyze(
        self,
        state: CouncilState,
        context: Optional[Dict[str, Any]] = None
    ) -> RiskAgentProposal:
        """
        Analyze risk and generate safety assessment proposal.
        
        Args:
            state: Current council state
            context: Additional context
            
        Returns:
            RiskAgentProposal with comprehensive risk assessment
        """
        topic = self.extract_topic_from_state(state)
        platform = state.get('platform', Platform.INSTAGRAM)
        
        # Load memory context (especially past failures/controversies)
        memory_context = self._load_memory_context(
            current_situation=f"Risk analysis for: {topic}",
            include_patterns=True
        )
        
        # Build analysis prompt
        analysis_prompt = f"""
SITUATION: {topic}

TARGET PLATFORM: {platform}

TASK:
Conduct COMPREHENSIVE RISK ASSESSMENT. You are the safety shield.

Your mindset: "One bad post destroys months of trust."

Analyze for:

1. CONTROVERSY PROBABILITY (0-1):
   - Could this be misinterpreted?
   - Hidden offensive meanings?
   - Cultural sensitivity issues?

2. BRAND BACKLASH RISK (0-1):
   - Potential negative reactions
   - Community pushback likelihood
   - Historical similar failures

3. PLATFORM BAN PROBABILITY (0-1):
   - Violates platform guidelines?
   - Shadowban risk?
   - Content policy issues?

4. TOXICITY SCORE (0-1):
   - Hate speech potential
   - Discrimination concerns
   - Offensive language

5. SENSITIVE TOPICS DETECTED:
   - Politics, religion, gender/identity
   - War/conflict, social justice
   - Any trigger topics?

6. MITIGATION STRATEGIES:
   - How to reduce risks
   - Alternative approaches
   - Safety modifications

7. RED FLAGS:
   - List any immediate blockers

Remember: Think WORST-CASE scenario. Be paranoid. Better to block now than apologize later.

DECISION RULES:
- If ANY score > 0.7: REJECT
- If 2+ scores > 0.5: CONDITIONAL (with heavy mitigation)
- If all scores < 0.3: APPROVE
- Otherwise: CONDITIONAL

Provide analysis in JSON format:
- controversy_probability: float (0-1)
- backlash_risk: float (0-1)
- platform_ban_risk: float (0-1)
- toxicity_score: float (0-1)
- sensitive_topics: array
- mitigation_strategies: array
- red_flags: array
- recommendation: string
- confidence: float (0-1)
- reasoning: string
- concerns: array
- vote: string
"""
        
        schema_description = """
{
    "controversy_probability": 0.0-1.0,
    "backlash_risk": 0.0-1.0,
    "platform_ban_risk": 0.0-1.0,
    "toxicity_score": 0.0-1.0,
    "sensitive_topics": ["topic1", "topic2"],
    "mitigation_strategies": ["strategy1", "strategy2"],
    "red_flags": ["flag1"],
    "recommendation": "detailed risk assessment",
    "confidence": 0.0-1.0,
    "reasoning": "worst-case analysis",
    "concerns": ["concern1"],
    "vote": "approve/reject/conditional"
}
"""
        
        opinion = self._generate_opinion(
            prompt=analysis_prompt,
            context=memory_context,
            schema_description=schema_description
        )
        
        # Build specialized RiskAgentProposal
        proposal = RiskAgentProposal(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            timestamp=self._get_timestamp(),
            
            # Core proposal fields
            recommendation=opinion.get('recommendation', 'No recommendation generated'),
            confidence=opinion.get('confidence', 0.5),
            priority=self._calculate_priority_from_risk(
                max(
                    opinion.get('controversy_probability', 0),
                    opinion.get('backlash_risk', 0),
                    opinion.get('toxicity_score', 0)
                )
            ),
            reasoning=opinion.get('reasoning', 'No reasoning provided'),
            supporting_evidence=[
                f"Controversy risk: {opinion.get('controversy_probability', 0):.0%}",
                f"Backlash risk: {opinion.get('backlash_risk', 0):.0%}",
                f"Toxicity: {opinion.get('toxicity_score', 0):.0%}"
            ],
            concerns=opinion.get('concerns', []),
            scores={
                'controversy': opinion.get('controversy_probability', 0.0),
                'backlash': opinion.get('backlash_risk', 0.0),
                'platform_ban': opinion.get('platform_ban_risk', 0.0),
                'toxicity': opinion.get('toxicity_score', 0.0)
            },
            conflicts_with=[],
            vote=opinion.get('vote', 'conditional'),
            conditions=opinion.get('mitigation_strategies', []),
            
            # Risk-specific fields
            controversy_probability=opinion.get('controversy_probability', 0.0),
            backlash_risk=opinion.get('backlash_risk', 0.0),
            platform_ban_risk=opinion.get('platform_ban_risk', 0.0),
            toxicity_score=opinion.get('toxicity_score', 0.0),
            mitigation_strategies=opinion.get('mitigation_strategies', []),
            red_flags=opinion.get('red_flags', []),
            
            metadata={
                'risk_analysis_version': '1.0',
                'analysis_timestamp': self._get_timestamp(),
                'sensitive_topics_detected': opinion.get('sensitive_topics', [])
            }
        )
        
        # Store in memory (especially rejections for pattern learning)
        self._store_decision_memory(
            context=f"Risk analysis: {topic}",
            decision={
                'max_risk_score': max(
                    proposal['controversy_probability'],
                    proposal['backlash_risk'],
                    proposal['toxicity_score']
                ),
                'vote': proposal['vote'],
                'red_flags_count': len(proposal['red_flags'])
            },
            reasoning=proposal['reasoning'],
            importance=0.9 if proposal['vote'] == 'reject' else 0.5  # High importance for rejections
        )
        
        logger.info(
            f"RiskAgent analysis complete: "
            f"Max risk {max(proposal['controversy_probability'], proposal['backlash_risk'], proposal['toxicity_score']):.0%}, "
            f"Vote: {proposal['vote']}, "
            f"Red flags: {len(proposal['red_flags'])}"
        )
        
        return proposal
    
    def debate(
        self,
        state: CouncilState,
        other_proposals: List[AgentProposal]
    ) -> Dict[str, Any]:
        """
        Participate in debate by emphasizing safety and worst-case scenarios.
        
        RiskAgent typically:
        - Uses fear-based arguments ("What if...")
        - References past failures
        - Demands mitigation before approval
        - Often conflicts with Trend Agent
        - Firm on high-risk content (no compromise)
        
        Args:
            state: Current council state
            other_proposals: Proposals from other agents
            
        Returns:
            Debate response with safety-focused arguments
        """
        topic = self.extract_topic_from_state(state)
        
        debate_prompt = f"""
DEBATE SITUATION:
Topic: {topic}

OTHER AGENTS' POSITIONS:
{self._format_other_proposals(other_proposals)}

YOUR ROLE IN DEBATE:
You are RiskAgent - cold, analytical, paranoid about brand damage.

Your mindset: "One bad post destroys months of trust."

TASK:
Defend your risk assessment against agents pushing for approval.

Your debate style:
- "It can be interpreted as mocking a community. Risk: high."
- "What if [worst case scenario]?"
- "Remember when [past failure]?"
- "We need mitigation X, Y, Z before approval"

If risk is HIGH (any score > 0.7):
- DO NOT COMPROMISE
- Hard block

If risk is MEDIUM (scores 0.4-0.7):
- Demand specific mitigations
- Conditional approval only

If risk is LOW (all scores < 0.3):
- Approve but note monitoring

Provide:
1. Worst-case scenario argument
2. Required mitigations (if any)
3. Non-negotiable safety boundaries
4. Final vote

Respond in JSON format.
"""
        
        schema = """
{
    "worst_case_scenario": "detailed fear-based argument",
    "required_mitigations": ["mitigation1", "mitigation2"],
    "safety_boundaries": ["non-negotiable1"],
    "past_failure_references": "similar issues we've seen",
    "final_vote": "approve/reject/conditional",
    "compromise_possible": true/false
}
"""
        
        debate_response = self._generate_opinion(
            prompt=debate_prompt,
            context="",
            schema_description=schema
        )
        
        logger.info(f"RiskAgent debate response: {debate_response.get('final_vote', 'unknown')}")
        
        return {
            'agent_name': self.agent_name,
            'debate_response': debate_response,
            'emphasizes_safety': True,
            'uses_fear_arguments': True,
            'final_vote': debate_response.get('final_vote', 'reject')
        }
    
    def _calculate_priority_from_risk(self, max_risk: float) -> str:
        """Calculate priority from risk level (inverse - higher risk = higher priority)."""
        if max_risk > 0.7:
            return "high"  # Critical risk
        elif max_risk > 0.4:
            return "medium"  # Moderate risk
        else:
            return "low"  # Low risk
    
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
