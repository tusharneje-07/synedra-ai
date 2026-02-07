"""
Debate Manager - Multi-Round Discussion Orchestration
======================================================

Manages debate rounds between specialist agents:
- Orchestrates argument exchange
- Tracks convergence
- Detects when consensus is reached or stalemate occurs
- Manages debate rounds and timing

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from graph.state_schema import (
    CouncilState,
    AgentProposal,
    DebateRound,
    AgentType,
    calculate_consensus_score
)

logger = logging.getLogger(__name__)


class DebateManager:
    """
    Orchestrates multi-round debates between agents.
    
    Features:
    - Round-by-round argument tracking
    - Convergence detection
    - Position change tracking
    - Stalemate detection
    """
    
    def __init__(
        self,
        max_rounds: int = 3,
        convergence_threshold: float = 0.85,
        min_position_change: float = 0.05
    ):
        """
        Initialize Debate Manager.
        
        Args:
            max_rounds: Maximum number of debate rounds
            convergence_threshold: Consensus score needed to stop early (0-1)
            min_position_change: Minimum vote change to continue debating
        """
        self.max_rounds = max_rounds
        self.convergence_threshold = convergence_threshold
        self.min_position_change = min_position_change
        
        logger.info(
            f"DebateManager initialized: max_rounds={max_rounds}, "
            f"convergence_threshold={convergence_threshold}"
        )
    
    def orchestrate_debate(
        self,
        state: CouncilState,
        agents: Dict[AgentType, Any]
    ) -> CouncilState:
        """
        Orchestrate complete debate process.
        
        Args:
            state: Current council state with initial proposals
            agents: Dict of agent instances
            
        Returns:
            Updated state with debate rounds and final positions
        """
        logger.info(f"Starting debate orchestration for: {state.get('topic', 'unknown')}")
        
        current_proposals = state.get('current_proposals', [])
        if not current_proposals:
            logger.warning("No initial proposals to debate")
            return state
        
        debate_rounds = []
        previous_votes = self._extract_votes(current_proposals)
        
        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"Debate round {round_num}/{self.max_rounds}")
            
            # Execute debate round
            round_data, updated_proposals = self._execute_debate_round(
                round_num=round_num,
                state=state,
                current_proposals=current_proposals,
                agents=agents
            )
            
            debate_rounds.append(round_data)
            
            # Check for convergence
            current_votes = self._extract_votes(updated_proposals)
            consensus_score = calculate_consensus_score(updated_proposals)
            
            logger.info(f"Round {round_num} consensus: {consensus_score:.2f}")
            
            # Update proposals for next round
            current_proposals = updated_proposals
            
            # Check stopping conditions
            should_stop, reason = self._should_stop_debate(
                round_num=round_num,
                consensus_score=consensus_score,
                previous_votes=previous_votes,
                current_votes=current_votes
            )
            
            if should_stop:
                logger.info(f"Debate stopped: {reason}")
                round_data['termination_reason'] = reason
                break
            
            previous_votes = current_votes
        
        # Update state with debate results
        state['debate_rounds'] = debate_rounds
        state['current_proposals'] = current_proposals
        state['final_consensus_score'] = calculate_consensus_score(current_proposals)
        state['total_debate_rounds'] = len(debate_rounds)
        
        logger.info(
            f"Debate complete: {len(debate_rounds)} rounds, "
            f"consensus={state['final_consensus_score']:.2f}"
        )
        
        return state
    
    def _execute_debate_round(
        self,
        round_num: int,
        state: CouncilState,
        current_proposals: List[AgentProposal],
        agents: Dict[AgentType, Any]
    ) -> Tuple[DebateRound, List[AgentProposal]]:
        """
        Execute a single debate round.
        
        Args:
            round_num: Current round number
            state: Council state
            current_proposals: Current agent proposals
            agents: Agent instances
            
        Returns:
            Tuple of (round_data, updated_proposals)
        """
        round_start = datetime.now().isoformat()
        arguments = []
        updated_proposals = []
        position_changes = []
        
        # Each agent debates with other proposals
        for agent_type, agent in agents.items():
            # Skip arbitrator in early rounds (observes only)
            if agent_type == AgentType.ARBITRATOR and round_num < self.max_rounds:
                continue
            
            # Get other proposals (exclude own)
            other_proposals = [
                p for p in current_proposals 
                if p.get('agent_type') != agent_type
            ]
            
            if not other_proposals:
                continue
            
            try:
                # Agent participates in debate
                debate_response = agent.debate(
                    state=state,
                    other_proposals=other_proposals
                )
                
                arguments.append({
                    'agent_type': agent_type.value,
                    'agent_name': agent.agent_name,
                    'round': round_num,
                    'response': debate_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Check if agent changed position
                original_proposal = next(
                    (p for p in current_proposals if p.get('agent_type') == agent_type),
                    None
                )
                
                new_vote = debate_response.get('final_vote') or debate_response.get('debate_response', {}).get('final_vote')
                
                if original_proposal and new_vote:
                    old_vote = original_proposal.get('vote')
                    if old_vote != new_vote:
                        position_changes.append({
                            'agent': agent_type.value,
                            'from': old_vote,
                            'to': new_vote,
                            'round': round_num
                        })
                        
                        # Update proposal with new vote
                        updated_proposal = original_proposal.copy()
                        updated_proposal['vote'] = new_vote
                        updated_proposal['debate_rounds_participated'] = round_num
                        updated_proposals.append(updated_proposal)
                        
                        logger.info(f"{agent_type.value} changed vote: {old_vote} → {new_vote}")
                    else:
                        updated_proposals.append(original_proposal)
                else:
                    if original_proposal:
                        updated_proposals.append(original_proposal)
                        
            except Exception as e:
                logger.error(f"Error in debate for {agent_type}: {e}")
                # Keep original proposal on error
                original = next(
                    (p for p in current_proposals if p.get('agent_type') == agent_type),
                    None
                )
                if original:
                    updated_proposals.append(original)
        
        # If no proposals were updated, use current proposals
        if not updated_proposals:
            updated_proposals = current_proposals
        
        round_data: DebateRound = {
            'round_number': round_num,
            'proposals': updated_proposals,
            'arguments': arguments,
            'consensus_score': calculate_consensus_score(updated_proposals),
            'position_changes': position_changes,
            'timestamp': round_start,
            'termination_reason': None
        }
        
        return round_data, updated_proposals
    
    def _should_stop_debate(
        self,
        round_num: int,
        consensus_score: float,
        previous_votes: Dict[str, str],
        current_votes: Dict[str, str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if debate should stop.
        
        Args:
            round_num: Current round number
            consensus_score: Current consensus score
            previous_votes: Votes from previous round
            current_votes: Votes from current round
            
        Returns:
            Tuple of (should_stop, reason)
        """
        # Reached max rounds
        if round_num >= self.max_rounds:
            return True, "Max rounds reached"
        
        # High consensus achieved
        if consensus_score >= self.convergence_threshold:
            return True, f"Consensus achieved ({consensus_score:.2f})"
        
        # Stalemate detection - no position changes
        position_changes = sum(
            1 for agent_type in current_votes
            if previous_votes.get(agent_type) != current_votes.get(agent_type)
        )
        
        if position_changes == 0:
            return True, "Stalemate - no position changes"
        
        # Continue debate
        return False, None
    
    def _extract_votes(self, proposals: List[AgentProposal]) -> Dict[str, str]:
        """
        Extract vote mapping from proposals.
        
        Args:
            proposals: List of agent proposals
            
        Returns:
            Dict mapping agent_type to vote
        """
        votes = {}
        for p in proposals:
            agent_type = p.get('agent_type', 'unknown')
            vote = p.get('vote', 'abstain')
            votes[agent_type] = vote
        
        return votes
    
    def get_debate_summary(self, state: CouncilState) -> Dict[str, Any]:
        """
        Generate summary of debate process.
        
        Args:
            state: Council state after debate
            
        Returns:
            Debate summary dict
        """
        debate_rounds = state.get('debate_rounds', [])
        
        if not debate_rounds:
            return {'status': 'no_debate_occurred'}
        
        total_position_changes = sum(
            len(round_data.get('position_changes', []))
            for round_data in debate_rounds
        )
        
        final_round = debate_rounds[-1]
        
        return {
            'total_rounds': len(debate_rounds),
            'final_consensus': state.get('final_consensus_score', 0),
            'total_position_changes': total_position_changes,
            'termination_reason': final_round.get('termination_reason', 'unknown'),
            'converged': state.get('final_consensus_score', 0) >= self.convergence_threshold,
            'consensus_by_round': [
                round_data.get('consensus_score', 0)
                for round_data in debate_rounds
            ]
        }
