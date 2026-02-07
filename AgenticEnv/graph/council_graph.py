"""
Council Graph - LangGraph Workflow for AI Council
==================================================

Main LangGraph workflow implementing the autonomous council:
1. Analysis Phase: All specialists analyze the topic
2. Conflict Detection: Identify disagreements
3. Debate Phase: Multi-round discussion (if needed)
4. Arbitration: CMO makes final decision
5. Decision Output: Final recommendation

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import Dict, Any, List, Literal
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from graph.state_schema import (
    CouncilState,
    AgentType,
    Platform,
    create_initial_state,
    calculate_consensus_score
)
from graph.debate_manager import DebateManager
from graph.conflict_resolver import ConflictResolver
from agents import AgentFactory

logger = logging.getLogger(__name__)


class CouncilGraph:
    """
    LangGraph workflow for autonomous AI council.
    
    Workflow Steps:
    1. initialize → Create council state
    2. analysis → All agents analyze topic
    3. detect_conflicts → Find disagreements
    4. should_debate → Decide if debate needed
    5. debate → Multi-round discussion (conditional)
    6. arbitration → CMO final decision
    7. finalize → Package results
    """
    
    def __init__(
        self,
        max_debate_rounds: int = 3,
        convergence_threshold: float = 0.85,
        auto_create_agents: bool = True
    ):
        """
        Initialize Council Graph.
        
        Args:
            max_debate_rounds: Maximum debate rounds
            convergence_threshold: Consensus needed to skip debate
            auto_create_agents: Automatically create agent council
        """
        self.max_debate_rounds = max_debate_rounds
        self.convergence_threshold = convergence_threshold
        
        # Create managers
        self.debate_manager = DebateManager(
            max_rounds=max_debate_rounds,
            convergence_threshold=convergence_threshold
        )
        self.conflict_resolver = ConflictResolver()
        
        # Create agents
        self.agents = None
        if auto_create_agents:
            self.agents = AgentFactory.create_full_council()
            logger.info(f"Council created with {len(self.agents)} agents")
        
        # Build graph
        self.graph = self._build_graph()
        
        logger.info("CouncilGraph initialized and ready")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(CouncilState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("analysis", self._analysis_node)
        workflow.add_node("detect_conflicts", self._detect_conflicts_node)
        workflow.add_node("debate", self._debate_node)
        workflow.add_node("arbitration", self._arbitration_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Add edges
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "analysis")
        workflow.add_edge("analysis", "detect_conflicts")
        
        # Conditional edge: debate or skip to arbitration
        workflow.add_conditional_edges(
            "detect_conflicts",
            self._should_debate,
            {
                "debate": "debate",
                "arbitration": "arbitration"
            }
        )
        
        workflow.add_edge("debate", "arbitration")
        workflow.add_edge("arbitration", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _initialize_node(self, state: CouncilState) -> CouncilState:
        """Initialize council state."""
        logger.info(f"Initializing council for topic: {state.get('topic', 'unknown')}")
        
        state['council_start_time'] = datetime.now().isoformat()
        state['workflow_stage'] = 'initialized'
        
        # Ensure agents exist
        if self.agents is None:
            self.agents = AgentFactory.create_full_council()
        
        return state
    
    def _analysis_node(self, state: CouncilState) -> CouncilState:
        """All specialist agents analyze the topic."""
        logger.info("Starting analysis phase")
        
        state['workflow_stage'] = 'analysis'
        proposals = []
        
        # Get all specialist agents (exclude arbitrator for now)
        specialist_agents = {
            agent_type: agent
            for agent_type, agent in self.agents.items()
            if agent_type != AgentType.ARBITRATOR
        }
        
        # Each specialist analyzes
        for agent_type, agent in specialist_agents.items():
            try:
                logger.info(f"  {agent_type.value} analyzing...")
                
                proposal = agent.analyze(state=state)
                proposals.append(proposal)
                
                logger.info(
                    f"  {agent_type.value} vote: {proposal.get('vote')}, "
                    f"confidence: {proposal.get('confidence', 0):.2f}"
                )
                
            except Exception as e:
                logger.error(f"Error in {agent_type} analysis: {e}")
                # Continue with other agents
        
        state['current_proposals'] = proposals
        state['initial_consensus_score'] = calculate_consensus_score(proposals)
        
        logger.info(f"Analysis complete: {len(proposals)} proposals, consensus={state['initial_consensus_score']:.2f}")
        
        return state
    
    def _detect_conflicts_node(self, state: CouncilState) -> CouncilState:
        """Detect conflicts between proposals."""
        logger.info("Detecting conflicts")
        
        state['workflow_stage'] = 'conflict_detection'
        
        proposals = state.get('current_proposals', [])
        conflicts = self.conflict_resolver.detect_conflicts(proposals)
        
        state['conflicts_detected'] = conflicts
        state['conflict_summary'] = self.conflict_resolver.build_conflict_summary(conflicts)
        
        logger.info(
            f"Conflicts detected: {len(conflicts)} total, "
            f"{state['conflict_summary'].get('critical_conflicts', 0)} critical"
        )
        
        return state
    
    def _should_debate(self, state: CouncilState) -> Literal["debate", "arbitration"]:
        """
        Decide if debate is needed.
        
        Debate if:
        - Low consensus (< threshold)
        - Critical conflicts exist
        - Arbitrator configuration requires it
        """
        consensus = state.get('initial_consensus_score', 0)
        conflict_summary = state.get('conflict_summary', {})
        critical_conflicts = conflict_summary.get('critical_conflicts', 0)
        
        # Skip debate if high consensus and no critical conflicts
        if consensus >= self.convergence_threshold and critical_conflicts == 0:
            logger.info(f"Skipping debate: high consensus ({consensus:.2f})")
            return "arbitration"
        
        logger.info(
            f"Debate required: consensus={consensus:.2f}, "
            f"critical_conflicts={critical_conflicts}"
        )
        return "debate"
    
    def _debate_node(self, state: CouncilState) -> CouncilState:
        """Execute multi-round debate."""
        logger.info("Starting debate phase")
        
        state['workflow_stage'] = 'debate'
        
        # Orchestrate debate
        state = self.debate_manager.orchestrate_debate(
            state=state,
            agents=self.agents
        )
        
        # Get debate summary
        debate_summary = self.debate_manager.get_debate_summary(state)
        state['debate_summary'] = debate_summary
        
        logger.info(
            f"Debate complete: {debate_summary.get('total_rounds')} rounds, "
            f"final consensus={debate_summary.get('final_consensus', 0):.2f}"
        )
        
        return state
    
    def _arbitration_node(self, state: CouncilState) -> CouncilState:
        """CMO makes final decision."""
        logger.info("Starting arbitration")
        
        state['workflow_stage'] = 'arbitration'
        
        # Get arbitrator
        arbitrator = self.agents.get(AgentType.ARBITRATOR)
        
        if not arbitrator:
            logger.error("Arbitrator not found!")
            state['final_decision'] = {
                'decision': 'ERROR',
                'error': 'Arbitrator agent not available'
            }
            return state
        
        try:
            # Arbitrator analyzes all proposals and makes decision
            final_proposal = arbitrator.analyze(state=state)
            
            state['final_decision'] = final_proposal
            state['arbitrator_decision'] = final_proposal.get('final_decision', 'unknown')
            
            logger.info(
                f"Arbitration complete: {final_proposal.get('final_decision')}, "
                f"confidence={final_proposal.get('confidence', 0):.2f}"
            )
            
        except Exception as e:
            logger.error(f"Error in arbitration: {e}")
            state['final_decision'] = {
                'decision': 'ERROR',
                'error': str(e)
            }
        
        return state
    
    def _finalize_node(self, state: CouncilState) -> CouncilState:
        """Finalize and package results."""
        logger.info("Finalizing council decision")
        
        state['workflow_stage'] = 'completed'
        state['council_end_time'] = datetime.now().isoformat()
        
        # Calculate total time
        start = state.get('council_start_time')
        end = state.get('council_end_time')
        
        if start and end:
            try:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                duration = (end_dt - start_dt).total_seconds()
                state['total_duration_seconds'] = duration
            except:
                pass
        
        # Build execution summary
        state['execution_summary'] = {
            'topic': state.get('topic'),
            'platform': state.get('platform'),
            'initial_consensus': state.get('initial_consensus_score', 0),
            'final_consensus': state.get('final_consensus_score', 0),
            'conflicts_detected': len(state.get('conflicts_detected', [])),
            'debate_rounds': state.get('total_debate_rounds', 0),
            'final_decision': state.get('arbitrator_decision', 'unknown'),
            'total_duration': state.get('total_duration_seconds', 0)
        }
        
        logger.info(
            f"Council decision finalized: {state['execution_summary']['final_decision']}"
        )
        
        return state
    
    def run(
        self,
        topic: str,
        platform: Platform = Platform.INSTAGRAM,
        context: Dict[str, Any] = None,
        trigger_event: str = "manual_request"
    ) -> CouncilState:
        """
        Run complete council workflow.
        
        Args:
            topic: Topic or content to analyze
            platform: Target social media platform
            context: Additional context
            trigger_event: What triggered this analysis
            
        Returns:
            Final council state with decision
        """
        logger.info(f"Running council for topic: {topic}")
        
        # Generate cycle ID
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create initial state
        initial_state = create_initial_state(
            cycle_id=cycle_id,
            topic=topic,
            trigger_event=trigger_event,
            platform=platform,
            urgency=context.get('urgency', 'medium') if context else 'medium',
            max_rounds=self.max_debate_rounds,
            consensus_threshold=self.convergence_threshold
        )
        
        # Add extra context if provided
        if context:
            initial_state['context'] = context
        
        # Run graph
        try:
            final_state = self.graph.invoke(initial_state)
            logger.info("Council workflow completed successfully")
            return final_state
            
        except Exception as e:
            logger.error(f"Council workflow failed: {e}")
            raise
    
    async def arun(
        self,
        topic: str,
        platform: Platform = Platform.INSTAGRAM,
        context: Dict[str, Any] = None,
        trigger_event: str = "manual_request"
    ) -> CouncilState:
        """
        Run complete council workflow asynchronously.
        
        Args:
            topic: Topic or content to analyze
            platform: Target social media platform
            context: Additional context
            trigger_event: What triggered this analysis
            
        Returns:
            Final council state with decision
        """
        logger.info(f"Running council (async) for topic: {topic}")
        
        # Generate cycle ID
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create initial state
        initial_state = create_initial_state(
            cycle_id=cycle_id,
            topic=topic,
            trigger_event=trigger_event,
            platform=platform,
            urgency=context.get('urgency', 'medium') if context else 'medium',
            max_rounds=self.max_debate_rounds,
            consensus_threshold=self.convergence_threshold
        )
        
        # Add extra context if provided
        if context:
            initial_state['context'] = context
        
        # Run graph asynchronously
        try:
            final_state = await self.graph.ainvoke(initial_state)
            logger.info("Council workflow completed successfully (async)")
            return final_state
            
        except Exception as e:
            logger.error(f"Council workflow failed (async): {e}")
            raise
    
    def visualize(self, output_path: str = "council_graph.png"):
        """
        Visualize the graph structure.
        
        Args:
            output_path: Path to save visualization
        """
        try:
            from IPython.display import Image, display
            
            graph_image = self.graph.get_graph().draw_mermaid_png()
            
            with open(output_path, 'wb') as f:
                f.write(graph_image)
            
            logger.info(f"Graph visualization saved to {output_path}")
            
        except Exception as e:
            logger.warning(f"Could not visualize graph: {e}")
