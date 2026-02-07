"""
Arbitrator Agent - CMO Decision Maker
=======================================

This agent makes final decisions by evaluating all specialist proposals and resolving conflicts.
It loads its complete behavioral specification from CMOAgent.md.

Role: Final decision maker with holistic view of business objectives
Mindset: "Balance creativity with results. Decide with data and gut feel."

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import Dict, List, Optional, Any

from agents.base_agent import BaseAgent
from graph.state_schema import (
    CouncilState,
    ArbitratorAgentProposal,
    AgentProposal,
    AgentType,
    Platform,
    calculate_consensus_score
)

logger = logging.getLogger(__name__)


class ArbitratorAgent(BaseAgent):
    """
    Arbitrator Agent - CMO who makes final decisions.
    
    Personality Traits (from CMOAgent.md):
    - Strategic visionary
    - Data-driven decision maker
    - Conflict resolver
    - Results-oriented leader
    - Holistic thinker
    
    Decision Framework:
    - Evaluates all specialist proposals
    - Weights agent votes by expertise
    - Resolves conflicts and deadlocks
    - Balances short-term wins vs long-term brand
    - Makes final strategic call
    """
    
    def __init__(self, voting_weight: float = 0.25):
        """
        Initialize Arbitrator Agent (CMO).
        
        Args:
            voting_weight: Initial voting weight (highest in council)
        """
        super().__init__(
            agent_name="CMO Chief Marketing Officer",
            agent_type=AgentType.ARBITRATOR,
            behavior_file="CMOAgent.md",
            voting_weight=voting_weight
        )
        
        logger.info("ArbitratorAgent (CMO) initialized and ready to make final decisions")
    
    def analyze(
        self,
        state: CouncilState,
        context: Optional[Dict[str, Any]] = None
    ) -> ArbitratorAgentProposal:
        """
        Analyze all proposals and make final strategic decision.
        
        Args:
            state: Current council state with all specialist proposals
            context: Additional context
            
        Returns:
            ArbitratorAgentProposal with final decision
        """
        topic = self.extract_topic_from_state(state)
        platform = state.get('platform', Platform.INSTAGRAM)
        
        # Extract all agent proposals from state
        all_proposals = self._extract_all_proposals(state)
        
        # Load memory context
        memory_context = self._load_memory_context(
            current_situation=f"Final decision for: {topic}",
            include_patterns=True
        )
        
        # Build comprehensive analysis prompt
        analysis_prompt = f"""
SITUATION: {topic}

TARGET PLATFORM: {platform}

SPECIALIST PROPOSALS:
{self._format_specialist_proposals(all_proposals)}

TASK:
As CMO, make FINAL STRATEGIC DECISION by evaluating all specialist inputs.

Your mindset: "Balance creativity with results. Decide with data and gut feel."

DECISION FRAMEWORK:

1. EVALUATE CONSENSUS:
   - Where do specialists agree?
   - What are the conflicts?
   - Calculate weighted consensus score

2. ASSESS STRATEGIC FIT:
   - Alignment with brand goals
   - Balance short-term wins vs long-term equity
   - Risk vs reward ratio
   - Resource requirements

3. RESOLVE CONFLICTS:
   - TrendAgent wants virality
   - EngagementAgent wants depth
   - BrandAgent guards consistency
   - RiskAgent prevents damage
   - ComplianceAgent enforces rules
   
   Your job: Find optimal balance

4. MAKE FINAL CALL:
   - approve: Execute as proposed
   - approve_with_modifications: Conditional approval
   - reject: Not aligned with strategy
   - revise_and_resubmit: Needs rework

SCORING:
- consensus_score: 0-100 (how aligned are specialists?)
- strategic_alignment: 0-100 (fits brand goals?)
- risk_adjusted_value: 0-100 (reward vs risk?)
- final_confidence: 0-1 (your certainty)

Provide decision in JSON format:
- final_decision: string (approve/approve_with_modifications/reject/revise_and_resubmit)
- consensus_score: float (0-100)
- strategic_alignment_score: float (0-100)
- risk_adjusted_value_score: float (0-100)
- conflicts_resolved: array (how you resolved each conflict)
- modifications_required: array (if conditional approval)
- rationale: string (explain your decision)
- confidence: float (0-1)
- key_considerations: array
- approved_elements: array
- rejected_elements: array
"""
        
        schema_description = """
{
    "final_decision": "approve/approve_with_modifications/reject/revise_and_resubmit",
    "consensus_score": 0-100,
    "strategic_alignment_score": 0-100,
    "risk_adjusted_value_score": 0-100,
    "conflicts_resolved": [{"conflict": "X vs Y", "resolution": "chosen approach"}],
    "modifications_required": ["modification1"],
    "rationale": "comprehensive explanation of decision",
    "confidence": 0.0-1.0,
    "key_considerations": ["consideration1"],
    "approved_elements": ["element1"],
    "rejected_elements": ["element1"]
}
"""
        
        opinion = self._generate_opinion(
            prompt=analysis_prompt,
            context=memory_context,
            schema_description=schema_description
        )
        
        # Build specialized ArbitratorAgentProposal
        proposal = ArbitratorAgentProposal(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            timestamp=self._get_timestamp(),
            
            # Core proposal fields
            recommendation=opinion.get('rationale', 'No rationale provided'),
            confidence=opinion.get('confidence', 0.7),
            priority=self._determine_priority(opinion.get('final_decision', 'revise_and_resubmit')),
            reasoning=opinion.get('rationale', 'No reasoning provided'),
            supporting_evidence=self._extract_supporting_evidence(all_proposals),
            concerns=[],
            scores={
                'consensus': opinion.get('consensus_score', 50) / 100,
                'strategic_alignment': opinion.get('strategic_alignment_score', 50) / 100,
                'risk_adjusted_value': opinion.get('risk_adjusted_value_score', 50) / 100
            },
            conflicts_with=[],
            vote=self._map_decision_to_vote(opinion.get('final_decision', 'conditional')),
            conditions=opinion.get('modifications_required', []),
            
            # Arbitrator-specific fields
            final_decision=opinion.get('final_decision', 'revise_and_resubmit'),
            consensus_score=opinion.get('consensus_score', 50.0),
            strategic_alignment_score=opinion.get('strategic_alignment_score', 50.0),
            risk_adjusted_value_score=opinion.get('risk_adjusted_value_score', 50.0),
            conflicts_resolved=opinion.get('conflicts_resolved', []),
            agent_votes_summary=self._summarize_agent_votes(all_proposals),
            weighted_vote_totals=self._calculate_weighted_votes(all_proposals),
            overruled_agents=self._identify_overruled_agents(
                opinion.get('final_decision', 'reject'),
                all_proposals
            ),
            modifications_required=opinion.get('modifications_required', []),
            
            metadata={
                'arbitration_version': '1.0',
                'decision_timestamp': self._get_timestamp(),
                'specialists_consulted': len(all_proposals),
                'decision_factors': opinion.get('key_considerations', [])
            }
        )
        
        # Store in memory with high importance
        self._store_decision_memory(
            context=f"Final decision: {topic}",
            decision={
                'final_decision': proposal['final_decision'],
                'consensus': proposal['consensus_score'],
                'confidence': proposal['confidence']
            },
            reasoning=proposal['reasoning'],
            importance=0.95
        )
        
        logger.info(
            f"ArbitratorAgent final decision: {proposal['final_decision']}, "
            f"Consensus: {proposal['consensus_score']:.0f}/100, "
            f"Confidence: {proposal['confidence']:.2f}"
        )
        
        return proposal
    
    def debate(
        self,
        state: CouncilState,
        other_proposals: List[AgentProposal]
    ) -> Dict[str, Any]:
        """
        CMO doesn't typically debate - makes final decision after hearing all inputs.
        
        However, can provide clarifying questions or request additional analysis.
        
        Args:
            state: Current council state
            other_proposals: Proposals from specialist agents
            
        Returns:
            Clarifying questions or decision rationale
        """
        topic = self.extract_topic_from_state(state)
        
        # CMO evaluates if enough information exists to decide
        debate_prompt = f"""
SITUATION:
Topic: {topic}

SPECIALIST PROPOSALS RECEIVED:
{self._format_other_proposals(other_proposals)}

YOUR ROLE:
As CMO, evaluate if you have enough information to make a final decision.

OPTIONS:
1. Make decision now (if consensus is clear)
2. Request additional analysis (if gaps exist)
3. Ask clarifying questions (if conflicts unresolved)

Provide response in JSON format:
- ready_to_decide: true/false
- information_gaps: array (what's missing?)
- clarifying_questions: array (questions for specialists)
- preliminary_direction: string (if ready to decide)
"""
        
        schema = """
{
    "ready_to_decide": true/false,
    "information_gaps": ["gap1"],
    "clarifying_questions": ["question1"],
    "preliminary_direction": "approve/reject/conditional"
}
"""
        
        debate_response = self._generate_opinion(
            prompt=debate_prompt,
            context="",
            schema_description=schema
        )
        
        logger.info(
            f"ArbitratorAgent debate participation: "
            f"Ready={debate_response.get('ready_to_decide', False)}"
        )
        
        return {
            'agent_name': self.agent_name,
            'debate_response': debate_response,
            'is_final_arbiter': True,
            'clarifying_questions': debate_response.get('clarifying_questions', []),
            'ready_for_decision': debate_response.get('ready_to_decide', False)
        }
    
    def _extract_all_proposals(self, state: CouncilState) -> List[AgentProposal]:
        """Extract all agent proposals from council state."""
        proposals = []
        
        # Get proposals from different debate rounds
        for round_data in state.get('debate_rounds', []):
            proposals.extend(round_data.get('proposals', []))
        
        # Also check current_proposals
        proposals.extend(state.get('current_proposals', []))
        
        return proposals
    
    def _format_specialist_proposals(self, proposals: List[AgentProposal]) -> str:
        """Format specialist proposals for CMO review."""
        formatted = []
        
        for p in proposals:
            agent_type = p.get('agent_type', 'unknown')
            vote = p.get('vote', 'unknown')
            confidence = p.get('confidence', 0)
            recommendation = p.get('recommendation', 'N/A')
            
            formatted.append(
                f"\n{agent_type.upper()}:\n"
                f"  Vote: {vote}\n"
                f"  Confidence: {confidence:.2f}\n"
                f"  Recommendation: {recommendation[:200]}...\n"
                f"  Key Concerns: {', '.join(p.get('concerns', [])[:3])}"
            )
        
        return "\n".join(formatted) if formatted else "No specialist proposals available"
    
    def _extract_supporting_evidence(self, proposals: List[AgentProposal]) -> List[str]:
        """Extract supporting evidence from all proposals."""
        evidence = []
        
        for p in proposals:
            agent_name = p.get('agent_name', 'Unknown')
            vote = p.get('vote', 'unknown')
            evidence.append(f"{agent_name}: {vote}")
        
        return evidence
    
    def _summarize_agent_votes(self, proposals: List[AgentProposal]) -> Dict[str, str]:
        """Summarize how each agent voted."""
        summary = {}
        
        for p in proposals:
            agent_type = p.get('agent_type', 'unknown')
            vote = p.get('vote', 'unknown')
            summary[agent_type] = vote
        
        return summary
    
    def _calculate_weighted_votes(self, proposals: List[AgentProposal]) -> Dict[str, float]:
        """Calculate weighted vote totals."""
        votes = {'approve': 0.0, 'reject': 0.0, 'conditional': 0.0}
        
        for p in proposals:
            vote = p.get('vote', 'conditional')
            weight = p.get('voting_weight', 0.15)
            
            if vote in votes:
                votes[vote] += weight
        
        return votes
    
    def _identify_overruled_agents(
        self,
        final_decision: str,
        proposals: List[AgentProposal]
    ) -> List[str]:
        """Identify which agents were overruled by CMO decision."""
        overruled = []
        
        decision_map = {
            'approve': 'approve',
            'approve_with_modifications': 'conditional',
            'reject': 'reject',
            'revise_and_resubmit': 'reject'
        }
        
        expected_vote = decision_map.get(final_decision, 'conditional')
        
        for p in proposals:
            agent_type = p.get('agent_type', 'unknown')
            vote = p.get('vote', 'unknown')
            
            if vote != expected_vote and vote != 'conditional':
                overruled.append(agent_type)
        
        return overruled
    
    def _determine_priority(self, final_decision: str) -> str:
        """Determine priority based on final decision."""
        if final_decision == 'approve':
            return "high"  # Execute immediately
        elif final_decision == 'approve_with_modifications':
            return "medium"  # Needs tweaks first
        else:
            return "low"  # Don't execute
    
    def _map_decision_to_vote(self, final_decision: str) -> str:
        """Map CMO decision to standard vote format."""
        mapping = {
            'approve': 'approve',
            'approve_with_modifications': 'conditional',
            'reject': 'reject',
            'revise_and_resubmit': 'reject'
        }
        return mapping.get(final_decision, 'conditional')
    
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
                f"Confidence={p.get('confidence', 0):.2f}"
            )
        return "\n".join(formatted) if formatted else "No other proposals yet"
