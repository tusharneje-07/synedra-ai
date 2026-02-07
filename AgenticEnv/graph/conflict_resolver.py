"""
Conflict Resolver - Agent Disagreement Detection & Resolution
==============================================================

Detects and categorizes conflicts between agent proposals:
- Vote conflicts (approve vs reject)
- Priority conflicts (high vs low)
- Reasoning conflicts (contradictory arguments)
- Strategic conflicts (long-term vs short-term)

Provides resolution strategies for arbitrator.

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from graph.state_schema import (
    CouncilState,
    AgentProposal,
    Conflict,
    AgentType
)

logger = logging.getLogger(__name__)


class ConflictResolver:
    """
    Detects and analyzes conflicts between agent proposals.
    
    Conflict Types:
    - VOTE: Direct vote opposition (approve vs reject)
    - PRIORITY: Different urgency assessments
    - REASONING: Contradictory logic
    - STRATEGIC: Short-term wins vs long-term brand
    - RISK_REWARD: Safety vs opportunity
    """
    
    CONFLICT_SEVERITIES = {
        'CRITICAL': 1.0,   # Direct vote opposition
        'HIGH': 0.75,      # Major reasoning conflicts
        'MEDIUM': 0.5,     # Priority misalignment
        'LOW': 0.25        # Minor disagreements
    }
    
    def __init__(self):
        """Initialize Conflict Resolver."""
        logger.info("ConflictResolver initialized")
    
    def detect_conflicts(
        self,
        proposals: List[AgentProposal]
    ) -> List[Conflict]:
        """
        Detect all conflicts between proposals.
        
        Args:
            proposals: List of agent proposals to analyze
            
        Returns:
            List of detected conflicts
        """
        if len(proposals) < 2:
            logger.info("Not enough proposals to detect conflicts")
            return []
        
        conflicts = []
        
        # Check all pairs of proposals
        for i, proposal_a in enumerate(proposals):
            for proposal_b in proposals[i+1:]:
                pair_conflicts = self._detect_pairwise_conflicts(
                    proposal_a,
                    proposal_b
                )
                conflicts.extend(pair_conflicts)
        
        logger.info(f"Detected {len(conflicts)} conflicts across {len(proposals)} proposals")
        
        return conflicts
    
    def _detect_pairwise_conflicts(
        self,
        proposal_a: AgentProposal,
        proposal_b: AgentProposal
    ) -> List[Conflict]:
        """
        Detect conflicts between two proposals.
        
        Args:
            proposal_a: First proposal
            proposal_b: Second proposal
            
        Returns:
            List of conflicts found
        """
        conflicts = []
        
        agent_a = proposal_a.get('agent_type', 'unknown')
        agent_b = proposal_b.get('agent_type', 'unknown')
        
        # Vote conflict
        vote_conflict = self._check_vote_conflict(proposal_a, proposal_b)
        if vote_conflict:
            conflicts.append({
                'conflict_type': 'VOTE',
                'severity': 'CRITICAL',
                'agents_involved': [agent_a, agent_b],
                'description': vote_conflict,
                'resolution_suggestion': self._suggest_vote_resolution(proposal_a, proposal_b),
                'metadata': {
                    'vote_a': proposal_a.get('vote'),
                    'vote_b': proposal_b.get('vote')
                }
            })
        
        # Priority conflict
        priority_conflict = self._check_priority_conflict(proposal_a, proposal_b)
        if priority_conflict:
            conflicts.append({
                'conflict_type': 'PRIORITY',
                'severity': 'MEDIUM',
                'agents_involved': [agent_a, agent_b],
                'description': priority_conflict,
                'resolution_suggestion': self._suggest_priority_resolution(proposal_a, proposal_b),
                'metadata': {
                    'priority_a': proposal_a.get('priority'),
                    'priority_b': proposal_b.get('priority')
                }
            })
        
        # Strategic conflict (trend vs brand, risk vs engagement)
        strategic_conflict = self._check_strategic_conflict(proposal_a, proposal_b)
        if strategic_conflict:
            conflicts.append({
                'conflict_type': 'STRATEGIC',
                'severity': 'HIGH',
                'agents_involved': [agent_a, agent_b],
                'description': strategic_conflict,
                'resolution_suggestion': self._suggest_strategic_resolution(agent_a, agent_b),
                'metadata': {
                    'agent_a_focus': self._get_agent_focus(agent_a),
                    'agent_b_focus': self._get_agent_focus(agent_b)
                }
            })
        
        # Confidence gap conflict
        confidence_conflict = self._check_confidence_gap(proposal_a, proposal_b)
        if confidence_conflict:
            conflicts.append({
                'conflict_type': 'CONFIDENCE',
                'severity': 'LOW',
                'agents_involved': [agent_a, agent_b],
                'description': confidence_conflict,
                'resolution_suggestion': "Weight decision toward higher confidence agent",
                'metadata': {
                    'confidence_a': proposal_a.get('confidence', 0),
                    'confidence_b': proposal_b.get('confidence', 0)
                }
            })
        
        return conflicts
    
    def _check_vote_conflict(
        self,
        proposal_a: AgentProposal,
        proposal_b: AgentProposal
    ) -> Optional[str]:
        """Check for direct vote opposition."""
        vote_a = proposal_a.get('vote', 'abstain')
        vote_b = proposal_b.get('vote', 'abstain')
        
        # Direct opposition
        if (vote_a == 'approve' and vote_b == 'reject') or \
           (vote_a == 'reject' and vote_b == 'approve'):
            return f"{proposal_a.get('agent_type')} votes {vote_a}, {proposal_b.get('agent_type')} votes {vote_b}"
        
        return None
    
    def _check_priority_conflict(
        self,
        proposal_a: AgentProposal,
        proposal_b: AgentProposal
    ) -> Optional[str]:
        """Check for priority misalignment."""
        priority_a = proposal_a.get('priority', 'medium')
        priority_b = proposal_b.get('priority', 'medium')
        
        priority_levels = {'low': 0, 'medium': 1, 'high': 2}
        
        level_a = priority_levels.get(priority_a, 1)
        level_b = priority_levels.get(priority_b, 1)
        
        # Significant priority difference
        if abs(level_a - level_b) >= 2:
            return f"{proposal_a.get('agent_type')} rates as {priority_a}, {proposal_b.get('agent_type')} rates as {priority_b}"
        
        return None
    
    def _check_strategic_conflict(
        self,
        proposal_a: AgentProposal,
        proposal_b: AgentProposal
    ) -> Optional[str]:
        """Check for strategic approach conflicts."""
        agent_a = proposal_a.get('agent_type', '')
        agent_b = proposal_b.get('agent_type', '')
        
        # Known strategic conflicts
        conflict_pairs = [
            ('trend', 'brand'),      # Viral vs consistency
            ('trend', 'risk'),       # Opportunity vs safety
            ('engagement', 'trend'), # Depth vs reach
            ('risk', 'engagement'),  # Safety vs interaction
        ]
        
        for type_x, type_y in conflict_pairs:
            if (agent_a == type_x and agent_b == type_y) or \
               (agent_a == type_y and agent_b == type_x):
                return f"Strategic tension between {agent_a} focus and {agent_b} focus"
        
        return None
    
    def _check_confidence_gap(
        self,
        proposal_a: AgentProposal,
        proposal_b: AgentProposal
    ) -> Optional[str]:
        """Check for significant confidence difference."""
        conf_a = proposal_a.get('confidence', 0.5)
        conf_b = proposal_b.get('confidence', 0.5)
        
        # Significant confidence gap
        if abs(conf_a - conf_b) >= 0.4:
            higher = proposal_a if conf_a > conf_b else proposal_b
            lower = proposal_b if conf_a > conf_b else proposal_a
            
            return (f"{higher.get('agent_type')} has {higher.get('confidence'):.2f} confidence, "
                   f"{lower.get('agent_type')} has {lower.get('confidence'):.2f}")
        
        return None
    
    def _suggest_vote_resolution(
        self,
        proposal_a: AgentProposal,
        proposal_b: AgentProposal
    ) -> str:
        """Suggest resolution for vote conflicts."""
        # Weight by confidence
        conf_a = proposal_a.get('confidence', 0.5)
        conf_b = proposal_b.get('confidence', 0.5)
        
        if conf_a > conf_b + 0.2:
            return f"Favor {proposal_a.get('agent_type')} (higher confidence: {conf_a:.2f})"
        elif conf_b > conf_a + 0.2:
            return f"Favor {proposal_b.get('agent_type')} (higher confidence: {conf_b:.2f})"
        else:
            return "Arbitrator must weigh agent expertise and strategic priorities"
    
    def _suggest_priority_resolution(
        self,
        proposal_a: AgentProposal,
        proposal_b: AgentProposal
    ) -> str:
        """Suggest resolution for priority conflicts."""
        return "Evaluate based on current business objectives and resource constraints"
    
    def _suggest_strategic_resolution(self, agent_a: str, agent_b: str) -> str:
        """Suggest resolution for strategic conflicts."""
        strategies = {
            ('trend', 'brand'): "Balance viral potential with brand consistency - test with small audience first",
            ('trend', 'risk'): "Assess risk tolerance vs opportunity cost - may require brand leadership input",
            ('engagement', 'trend'): "Consider platform algorithm - some platforms reward depth over reach",
            ('risk', 'engagement'): "Prioritize safety but explore compliant engagement tactics"
        }
        
        for (type_x, type_y), suggestion in strategies.items():
            if (agent_a == type_x and agent_b == type_y) or \
               (agent_a == type_y and agent_b == type_x):
                return suggestion
        
        return "Evaluate strategic trade-offs based on campaign goals"
    
    def _get_agent_focus(self, agent_type: str) -> str:
        """Get strategic focus of agent type."""
        focuses = {
            'trend': 'viral_reach',
            'engagement': 'community_depth',
            'brand': 'consistency',
            'risk': 'safety',
            'compliance': 'legal',
            'arbitrator': 'strategic_balance'
        }
        return focuses.get(agent_type, 'unknown')
    
    def categorize_conflicts(
        self,
        conflicts: List[Conflict]
    ) -> Dict[str, List[Conflict]]:
        """
        Categorize conflicts by type.
        
        Args:
            conflicts: List of detected conflicts
            
        Returns:
            Dict mapping conflict type to conflicts
        """
        categorized = defaultdict(list)
        
        for conflict in conflicts:
            conflict_type = conflict.get('conflict_type', 'UNKNOWN')
            categorized[conflict_type].append(conflict)
        
        return dict(categorized)
    
    def get_highest_severity_conflicts(
        self,
        conflicts: List[Conflict],
        top_n: int = 3
    ) -> List[Conflict]:
        """
        Get most severe conflicts.
        
        Args:
            conflicts: List of conflicts
            top_n: Number of top conflicts to return
            
        Returns:
            Top N most severe conflicts
        """
        sorted_conflicts = sorted(
            conflicts,
            key=lambda c: self.CONFLICT_SEVERITIES.get(c.get('severity', 'LOW'), 0),
            reverse=True
        )
        
        return sorted_conflicts[:top_n]
    
    def build_conflict_summary(
        self,
        conflicts: List[Conflict]
    ) -> Dict[str, Any]:
        """
        Build comprehensive conflict summary.
        
        Args:
            conflicts: List of conflicts
            
        Returns:
            Summary dict with statistics and recommendations
        """
        if not conflicts:
            return {
                'total_conflicts': 0,
                'requires_arbitration': False,
                'summary': 'No conflicts detected'
            }
        
        by_type = self.categorize_conflicts(conflicts)
        by_severity = defaultdict(int)
        
        for conflict in conflicts:
            severity = conflict.get('severity', 'LOW')
            by_severity[severity] += 1
        
        critical_count = by_severity.get('CRITICAL', 0)
        
        return {
            'total_conflicts': len(conflicts),
            'by_type': {k: len(v) for k, v in by_type.items()},
            'by_severity': dict(by_severity),
            'critical_conflicts': critical_count,
            'requires_arbitration': critical_count > 0 or len(conflicts) > 3,
            'top_conflicts': self.get_highest_severity_conflicts(conflicts),
            'resolution_complexity': self._assess_complexity(conflicts)
        }
    
    def _assess_complexity(self, conflicts: List[Conflict]) -> str:
        """Assess resolution complexity."""
        critical = sum(1 for c in conflicts if c.get('severity') == 'CRITICAL')
        total = len(conflicts)
        
        if critical >= 2:
            return 'HIGH'
        elif total >= 4:
            return 'MEDIUM'
        else:
            return 'LOW'
