"""
State Schema for LangGraph Multi-Agent Council
===============================================

This module defines the state schemas and type definitions for the
LangGraph-based multi-agent council system.

All state transitions, agent communications, and decision workflows
are managed through these typed state objects.

Author: AI Systems Engineer
Date: February 7, 2026
"""

from typing import TypedDict, List, Dict, Optional, Any, Literal
from datetime import datetime
from enum import Enum


# ========================================
# ENUMS FOR STATE MANAGEMENT
# ========================================

class DecisionStatus(str, Enum):
    """Status of a decision in the council workflow."""
    PENDING = "pending"
    IN_DEBATE = "in_debate"
    CONSENSUS_REACHED = "consensus_reached"
    ARBITRATION_NEEDED = "arbitration_needed"
    FINALIZED = "finalized"
    REJECTED = "rejected"


class AgentType(str, Enum):
    """Types of agents in the council."""
    TREND = "trend"
    ENGAGEMENT = "engagement"
    BRAND = "brand"
    RISK = "risk"
    COMPLIANCE = "compliance"
    ARBITRATOR = "arbitrator"


class ConflictSeverity(str, Enum):
    """Severity level of conflicts between agents."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Platform(str, Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"


# ========================================
# AGENT PROPOSAL SCHEMAS
# ========================================

class AgentProposal(TypedDict, total=False):
    """
    Schema for an individual agent's proposal.
    
    Each agent submits this structure during the council debate.
    """
    agent_name: str
    agent_type: AgentType
    timestamp: str
    
    # Core proposal
    recommendation: str
    confidence: float  # 0-1
    priority: str  # high, medium, low
    
    # Detailed opinion
    reasoning: str
    supporting_evidence: List[str]
    concerns: List[str]
    
    # Scores/Metrics
    scores: Dict[str, float]  # e.g., {"virality": 0.85, "risk": 0.2}
    
    # Conflicts
    conflicts_with: List[str]  # List of agent names
    
    # Voting
    vote: Literal["approve", "reject", "abstain", "conditional"]
    conditions: Optional[List[str]]  # If vote is conditional
    
    # Metadata
    metadata: Optional[Dict[str, Any]]


class TrendAgentProposal(AgentProposal):
    """Extended proposal schema for Trend Agent."""
    trend_topic: str
    viral_probability: float
    trend_lifespan: str
    platform_recommendation: Platform
    content_angle: str
    hook_line: str
    engagement_potential: float


class EngagementAgentProposal(AgentProposal):
    """Extended proposal schema for Engagement Agent."""
    comment_trigger_strength: float
    shareability_score: float
    relatability_score: float
    emotional_hook: str
    interaction_format: str
    community_building_score: float


class BrandAgentProposal(AgentProposal):
    """Extended proposal schema for Brand Agent."""
    tone_alignment_score: float
    brand_consistency_score: float
    fatigue_risk: float
    rewrite_suggestions: Optional[str]
    voice_issues: List[str]
    platform_adaptation_needed: bool


class RiskAgentProposal(AgentProposal):
    """Extended proposal schema for Risk Agent."""
    controversy_probability: float
    backlash_risk: float
    platform_ban_risk: float
    toxicity_score: float
    mitigation_strategies: List[str]
    red_flags: List[str]


class ComplianceAgentProposal(AgentProposal):
    """Extended proposal schema for Compliance Agent."""
    policy_compliance_score: float
    legal_risk_level: str
    platform_guidelines_met: bool
    required_disclosures: List[str]
    regulatory_concerns: List[str]


class ArbitratorAgentProposal(AgentProposal):
    """
    Extended proposal schema for Arbitrator Agent (CMO).
    
    The Arbitrator makes final decisions after evaluating all specialist proposals.
    """
    final_decision: str  # approve, approve_with_modifications, reject, revise_and_resubmit
    consensus_score: float  # 0-100 score of specialist agreement
    strategic_alignment_score: float  # 0-100 how well it fits strategy
    risk_adjusted_value_score: float  # 0-100 reward vs risk ratio
    conflicts_resolved: List[Dict[str, str]]  # How conflicts were resolved
    agent_votes_summary: Dict[str, str]  # Map of agent_type -> vote
    weighted_vote_totals: Dict[str, float]  # Weighted vote tallies
    overruled_agents: List[str]  # Agents whose votes were overruled
    modifications_required: List[str]  # Required changes if conditional


# ========================================
# CONFLICT DETECTION SCHEMAS
# ========================================

class Conflict(TypedDict):
    """Schema for a detected conflict between agents."""
    conflict_id: str
    agents_involved: List[str]
    severity: ConflictSeverity
    description: str
    conflict_type: str  # e.g., "value_mismatch", "priority_clash"
    
    # Agent positions
    agent_positions: Dict[str, str]
    
    # Resolution
    resolution_needed: bool
    resolution_method: Optional[str]
    resolved: bool


# ========================================
# DEBATE ROUND SCHEMAS
# ========================================

class DebateRound(TypedDict):
    """Schema for a single debate round."""
    round_number: int
    timestamp: str
    
    # Inputs
    topic: str
    agent_proposals: List[AgentProposal]
    
    # Analysis
    conflicts_detected: List[Conflict]
    consensus_score: float
    
    # Outcomes
    agreements: List[str]
    disagreements: List[str]
    
    # Next steps
    requires_negotiation: bool
    arbitration_needed: bool


# ========================================
# CONTENT GENERATION SCHEMAS
# ========================================

class ContentPiece(TypedDict):
    """Schema for generated content."""
    content_id: str
    platform: Platform
    format_type: str  # text, image, video, carousel, etc.
    
    # Content
    text: Optional[str]
    caption: Optional[str]
    hashtags: List[str]
    media_descriptions: List[str]
    
    # Metadata
    target_audience: str
    posting_time: Optional[str]
    campaign_tag: Optional[str]
    
    # Approval
    approved_by: List[str]
    final_approval: bool


class MultiPlatformContent(TypedDict):
    """Schema for content adapted to multiple platforms."""
    base_message: str
    variants: Dict[Platform, ContentPiece]
    unified_theme: str
    cross_platform_strategy: str


# ========================================
# MAIN COUNCIL STATE
# ========================================

class CouncilState(TypedDict, total=False):
    """
    Main state object for the LangGraph council workflow.
    
    This state is passed through all nodes in the graph and
    accumulates information throughout the decision process.
    """
    
    # ========================================
    # SESSION METADATA
    # ========================================
    cycle_id: str
    session_start: str
    session_end: Optional[str]
    status: DecisionStatus
    
    # ========================================
    # INPUT CONTEXT
    # ========================================
    trigger_event: str  # What triggered this cycle
    topic: str
    platform: Optional[Platform]
    urgency: str  # low, medium, high
    
    # External context
    trend_data: Optional[Dict[str, Any]]
    current_metrics: Optional[Dict[str, Any]]
    brand_guidelines: Optional[Dict[str, Any]]
    
    # ========================================
    # AGENT PROPOSALS
    # ========================================
    trend_proposal: Optional[TrendAgentProposal]
    engagement_proposal: Optional[EngagementAgentProposal]
    brand_proposal: Optional[BrandAgentProposal]
    risk_proposal: Optional[RiskAgentProposal]
    compliance_proposal: Optional[ComplianceAgentProposal]
    
    all_proposals: List[AgentProposal]
    
    # ========================================
    # DEBATE PROCESS
    # ========================================
    debate_rounds: List[DebateRound]
    current_round: int
    max_rounds: int
    
    conflicts_detected: List[Conflict]
    conflicts_resolved: List[Conflict]
    
    # ========================================
    # VOTING & CONSENSUS
    # ========================================
    agent_votes: Dict[str, str]  # agent_name -> vote
    agent_weights: Dict[str, float]  # agent_name -> weight
    
    consensus_score: float
    consensus_threshold: float
    consensus_reached: bool
    
    # ========================================
    # ARBITRATION
    # ========================================
    arbitration_needed: bool
    arbitrator_reasoning: Optional[str]
    arbitrator_override: bool
    
    # ========================================
    # FINAL DECISION
    # ========================================
    final_decision: Optional[Dict[str, Any]]
    decision_summary: Optional[str]
    action_items: List[str]
    
    # Content output
    generated_content: Optional[MultiPlatformContent]
    
    # ========================================
    # REASONING TRACE
    # ========================================
    reasoning_trace: List[Dict[str, Any]]
    decision_log: List[str]
    
    # ========================================
    # METADATA
    # ========================================
    processing_time: Optional[float]
    tokens_used: Optional[int]
    errors: List[str]
    warnings: List[str]


# ========================================
# GRAPH NODE OUTPUTS
# ========================================

class NodeOutput(TypedDict):
    """Generic output from a graph node."""
    node_name: str
    success: bool
    data: Dict[str, Any]
    errors: List[str]
    next_node: Optional[str]


class AgentNodeOutput(NodeOutput):
    """Output from an agent node."""
    proposal: AgentProposal
    confidence: float
    processing_time: float


class ArbitratorNodeOutput(NodeOutput):
    """Output from arbitrator node."""
    final_decision: Dict[str, Any]
    reasoning: str
    conflicts_resolved: int
    override_used: bool


# ========================================
# HELPER SCHEMAS
# ========================================

class AgentMemoryContext(TypedDict):
    """Context loaded from agent's memory."""
    agent_name: str
    relevant_memories: List[Dict[str, Any]]
    pattern_insights: Dict[str, Any]
    success_rate: float


class PerformanceMetrics(TypedDict):
    """Performance metrics for learning."""
    post_id: str
    platform: Platform
    engagement_rate: float
    virality_score: float
    sentiment_score: float
    outcome_label: str  # success, neutral, failure


class WeightAdjustment(TypedDict):
    """Agent weight adjustment record."""
    agent_name: str
    old_weight: float
    new_weight: float
    adjustment_factor: float
    reason: str
    timestamp: str


# ========================================
# UTILITY FUNCTIONS
# ========================================

def create_initial_state(
    cycle_id: str,
    topic: str,
    trigger_event: str,
    platform: Optional[Platform] = None,
    urgency: str = "medium",
    max_rounds: int = 3,
    consensus_threshold: float = 0.75
) -> CouncilState:
    """
    Create an initial state object for a council cycle.
    
    Args:
        cycle_id: Unique identifier for this cycle
        topic: Topic/situation to decide on
        trigger_event: What triggered this cycle
        platform: Target platform (if applicable)
        urgency: Urgency level
        max_rounds: Maximum debate rounds
        consensus_threshold: Threshold for consensus
        
    Returns:
        Initialized CouncilState object
    """
    return CouncilState(
        cycle_id=cycle_id,
        session_start=datetime.now().isoformat(),
        status=DecisionStatus.PENDING,
        
        trigger_event=trigger_event,
        topic=topic,
        platform=platform,
        urgency=urgency,
        
        all_proposals=[],
        debate_rounds=[],
        current_round=0,
        max_rounds=max_rounds,
        
        conflicts_detected=[],
        conflicts_resolved=[],
        
        agent_votes={},
        agent_weights={},
        consensus_score=0.0,
        consensus_threshold=consensus_threshold,
        consensus_reached=False,
        
        arbitration_needed=False,
        arbitrator_override=False,
        
        action_items=[],
        reasoning_trace=[],
        decision_log=[],
        
        errors=[],
        warnings=[]
    )


def add_proposal_to_state(
    state: CouncilState,
    proposal: AgentProposal
) -> CouncilState:
    """
    Add an agent proposal to the state.
    
    Args:
        state: Current council state
        proposal: Agent proposal to add
        
    Returns:
        Updated state
    """
    if 'all_proposals' not in state:
        state['all_proposals'] = []
    
    state['all_proposals'].append(proposal)
    
    # Also set agent-specific proposal
    agent_type = proposal.get('agent_type')
    if agent_type == AgentType.TREND:
        state['trend_proposal'] = proposal
    elif agent_type == AgentType.ENGAGEMENT:
        state['engagement_proposal'] = proposal
    elif agent_type == AgentType.BRAND:
        state['brand_proposal'] = proposal
    elif agent_type == AgentType.RISK:
        state['risk_proposal'] = proposal
    elif agent_type == AgentType.COMPLIANCE:
        state['compliance_proposal'] = proposal
    
    return state


def log_reasoning_step(
    state: CouncilState,
    agent_name: str,
    step_type: str,
    content: str
) -> CouncilState:
    """
    Add a reasoning step to the trace.
    
    Args:
        state: Current council state
        agent_name: Name of the agent
        step_type: Type of reasoning step
        content: Content of the step
        
    Returns:
        Updated state
    """
    if 'reasoning_trace' not in state:
        state['reasoning_trace'] = []
    
    state['reasoning_trace'].append({
        'timestamp': datetime.now().isoformat(),
        'agent': agent_name,
        'type': step_type,
        'content': content
    })
    
    return state


def calculate_consensus_score(proposals: List[AgentProposal]) -> float:
    """
    Calculate consensus score from agent proposals.
    
    Args:
        proposals: List of agent proposals
        
    Returns:
        Consensus score (0-1)
    """
    if not proposals:
        return 0.0
    
    # Count votes
    votes = [p.get('vote', 'abstain') for p in proposals]
    approvals = votes.count('approve')
    total = len([v for v in votes if v != 'abstain'])
    
    if total == 0:
        return 0.0
    
    return approvals / total
