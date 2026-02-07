"""
Graph Package
=============

Contains LangGraph workflow implementations:
- CouncilGraph: Main workflow orchestrator
- DebateManager: Multi-round debate orchestration
- ConflictResolver: Conflict detection and analysis
- State schemas and utilities
"""

from .council_graph import CouncilGraph
from .debate_manager import DebateManager
from .conflict_resolver import ConflictResolver
from .state_schema import (
    CouncilState,
    AgentProposal,
    TrendAgentProposal,
    EngagementAgentProposal,
    BrandAgentProposal,
    RiskAgentProposal,
    ComplianceAgentProposal,
    ArbitratorAgentProposal,
    Conflict,
    DebateRound,
    ContentPiece,
    MultiPlatformContent,
    DecisionStatus,
    AgentType,
    ConflictSeverity,
    Platform,
    create_initial_state,
    add_proposal_to_state,
    log_reasoning_step,
    calculate_consensus_score
)

__all__ = [
    'CouncilGraph',
    'DebateManager',
    'ConflictResolver',
    'CouncilState',
    'AgentProposal',
    'TrendAgentProposal',
    'EngagementAgentProposal',
    'BrandAgentProposal',
    'RiskAgentProposal',
    'ComplianceAgentProposal',
    'ArbitratorAgentProposal',
    'Conflict',
    'DebateRound',
    'ContentPiece',
    'MultiPlatformContent',
    'DecisionStatus',
    'AgentType',
    'ConflictSeverity',
    'Platform',
    'create_initial_state',
    'add_proposal_to_state',
    'log_reasoning_step',
    'calculate_consensus_score'
]

