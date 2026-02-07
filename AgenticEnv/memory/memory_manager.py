"""
Memory Manager for Multi-Agent AI Council
==========================================

This module manages contextual memory for all agents in the council.
It provides intelligent memory storage, retrieval, and relevance scoring
to enable agents to learn from past decisions and maintain context.

Features:
---------
- Per-agent memory isolation
- Relevance-based memory retrieval
- Automatic memory pruning
- Context summarization
- Pattern recognition from historical data

Author: AI Systems Engineer
Date: February 7, 2026
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import logging

from db.database import get_database
from config.settings import get_settings

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages contextual memory for AI agents.
    
    This class provides intelligent memory storage and retrieval,
    allowing agents to learn from past decisions and maintain
    context across multiple execution cycles.
    """
    
    def __init__(self):
        """Initialize memory manager with database connection."""
        self.db = get_database()
        self.settings = get_settings()
        self._memory_cache: Dict[str, List[Dict]] = defaultdict(list)
        self._cache_timestamp: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)  # Cache validity period
        
        logger.info("MemoryManager initialized")
    
    # ========================================
    # MEMORY STORAGE
    # ========================================
    
    def store_memory(
        self,
        agent_name: str,
        context: str,
        decision: Dict[str, Any],
        reasoning: str,
        outcome: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.5
    ) -> int:
        """
        Store a memory for an agent.
        
        Args:
            agent_name: Name of the agent
            context: The context/situation
            decision: The decision made (as dict)
            reasoning: Agent's reasoning process
            outcome: Result of the decision (if known)
            tags: Optional tags for categorization
            importance: Importance score (0-1)
            
        Returns:
            Memory record ID
        """
        metadata = {
            "tags": tags or [],
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        }
        
        record_id = self.db.store_agent_memory(
            agent_name=agent_name,
            context=context,
            decision=json.dumps(decision),
            outcome=outcome,
            reasoning=reasoning,
            metadata=metadata
        )
        
        # Invalidate cache for this agent
        if agent_name in self._memory_cache:
            del self._memory_cache[agent_name]
            del self._cache_timestamp[agent_name]
        
        logger.debug(f"Stored memory for {agent_name}, ID: {record_id}")
        return record_id
    
    def store_council_memory(
        self,
        cycle_id: str,
        final_decision: Dict[str, Any],
        agent_proposals: List[Dict[str, Any]],
        reasoning_trace: List[Dict[str, Any]],
        weights: Dict[str, float],
        debate_rounds: int,
        consensus_score: float,
        conflicts: Optional[List[str]] = None,
        resolution_method: Optional[str] = None
    ) -> int:
        """
        Store a complete council decision cycle.
        
        Args:
            cycle_id: Unique cycle identifier
            final_decision: The final decision output
            agent_proposals: All individual agent proposals
            reasoning_trace: Complete debate transcript
            weights: Agent voting weights used
            debate_rounds: Number of rounds conducted
            consensus_score: Final consensus level
            conflicts: Detected conflicts
            resolution_method: How conflicts were resolved
            
        Returns:
            Decision record ID
        """
        record_id = self.db.store_council_decision(
            cycle_id=cycle_id,
            final_decision=final_decision,
            reasoning_trace=reasoning_trace,
            weights_snapshot=weights,
            debate_rounds=debate_rounds,
            consensus_score=consensus_score,
            agent_proposals=agent_proposals,
            conflicts_detected=conflicts,
            resolution_method=resolution_method
        )
        
        logger.info(f"Stored council decision, Cycle: {cycle_id}")
        return record_id
    
    # ========================================
    # MEMORY RETRIEVAL
    # ========================================
    
    def get_agent_context(
        self,
        agent_name: str,
        current_context: Optional[str] = None,
        limit: int = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for an agent.
        
        Args:
            agent_name: Name of the agent
            current_context: Current context for relevance filtering
            limit: Maximum memories to retrieve
            use_cache: Whether to use cached results
            
        Returns:
            List of relevant memory records
        """
        if limit is None:
            limit = self.settings.memory_context_size
        
        # Check cache first
        if use_cache and agent_name in self._memory_cache:
            cache_age = datetime.now() - self._cache_timestamp.get(agent_name, datetime.min)
            if cache_age < self._cache_ttl:
                logger.debug(f"Using cached memories for {agent_name}")
                return self._memory_cache[agent_name][:limit]
        
        # Retrieve from database
        memories = self.db.get_agent_memory(
            agent_name=agent_name,
            limit=limit * 2,  # Get more for filtering
            context_filter=current_context
        )
        
        # Score and rank by relevance
        if current_context:
            scored_memories = self._score_memory_relevance(
                memories,
                current_context
            )
            memories = [m for m, _ in scored_memories[:limit]]
        else:
            memories = memories[:limit]
        
        # Update cache
        self._memory_cache[agent_name] = memories
        self._cache_timestamp[agent_name] = datetime.now()
        
        logger.debug(f"Retrieved {len(memories)} memories for {agent_name}")
        return memories
    
    def get_recent_council_decisions(
        self,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent council decisions.
        
        Args:
            limit: Number of decisions to retrieve
            
        Returns:
            List of decision records
        """
        decisions = self.db.get_recent_decisions(limit=limit)
        logger.debug(f"Retrieved {len(decisions)} recent council decisions")
        return decisions
    
    def get_decision_by_cycle(
        self,
        cycle_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific council decision.
        
        Args:
            cycle_id: Unique cycle identifier
            
        Returns:
            Decision record or None
        """
        decision = self.db.get_council_decision(cycle_id)
        if decision:
            logger.debug(f"Retrieved decision for cycle: {cycle_id}")
        return decision
    
    # ========================================
    # MEMORY ANALYSIS
    # ========================================
    
    def _score_memory_relevance(
        self,
        memories: List[Dict[str, Any]],
        current_context: str
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Score memories by relevance to current context.
        
        Args:
            memories: List of memory records
            current_context: Current context string
            
        Returns:
            List of (memory, score) tuples sorted by relevance
        """
        scored = []
        context_lower = current_context.lower()
        context_words = set(context_lower.split())
        
        for memory in memories:
            score = 0.0
            
            # Context similarity
            memory_context = memory.get('context', '').lower()
            memory_words = set(memory_context.split())
            
            # Word overlap score
            if memory_words:
                overlap = len(context_words & memory_words)
                score += (overlap / len(context_words)) * 0.4
            
            # Recency score (more recent = higher score)
            try:
                timestamp = datetime.fromisoformat(memory.get('timestamp', datetime.min.isoformat()))
                days_old = (datetime.now() - timestamp).days
                recency_score = max(0, 1 - (days_old / 30))  # Decay over 30 days
                score += recency_score * 0.3
            except:
                pass
            
            # Importance score
            metadata = memory.get('metadata', {})
            if isinstance(metadata, dict):
                importance = metadata.get('importance', 0.5)
                score += importance * 0.3
            
            scored.append((memory, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def analyze_agent_patterns(
        self,
        agent_name: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze patterns in an agent's decision history.
        
        Args:
            agent_name: Name of the agent
            days: Number of days to analyze
            
        Returns:
            Dictionary with pattern analysis
        """
        memories = self.db.get_agent_memory(agent_name=agent_name, limit=100)
        
        if not memories:
            return {
                "agent": agent_name,
                "total_decisions": 0,
                "patterns": {}
            }
        
        # Extract patterns
        decision_types = defaultdict(int)
        outcomes = defaultdict(int)
        contexts = defaultdict(int)
        
        for memory in memories:
            # Count decision types
            try:
                decision = json.loads(memory.get('decision', '{}'))
                decision_type = decision.get('type', 'unknown')
                decision_types[decision_type] += 1
            except:
                pass
            
            # Count outcomes
            outcome = memory.get('outcome', 'unknown')
            if outcome and outcome != 'unknown':
                outcomes[outcome] += 1
            
            # Count context types
            context = memory.get('context', '')[:50]  # First 50 chars
            if context:
                contexts[context] += 1
        
        return {
            "agent": agent_name,
            "total_decisions": len(memories),
            "decision_types": dict(decision_types),
            "outcomes": dict(outcomes),
            "common_contexts": dict(sorted(
                contexts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
        }
    
    def get_success_rate(
        self,
        agent_name: str,
        success_criteria: str = "positive"
    ) -> float:
        """
        Calculate success rate for an agent's decisions.
        
        Args:
            agent_name: Name of the agent
            success_criteria: What counts as success (in outcome field)
            
        Returns:
            Success rate (0-1)
        """
        memories = self.db.get_agent_memory(agent_name=agent_name, limit=50)
        
        if not memories:
            return 0.5  # Neutral starting point
        
        total = 0
        successful = 0
        
        for memory in memories:
            outcome = memory.get('outcome', '')
            if outcome and outcome != 'unknown':
                total += 1
                if success_criteria.lower() in outcome.lower():
                    successful += 1
        
        if total == 0:
            return 0.5
        
        return successful / total
    
    # ========================================
    # CONTEXT BUILDING
    # ========================================
    
    def build_agent_context_prompt(
        self,
        agent_name: str,
        current_situation: str,
        include_patterns: bool = True
    ) -> str:
        """
        Build a context prompt for an agent from its memory.
        
        Args:
            agent_name: Name of the agent
            current_situation: Current situation description
            include_patterns: Whether to include pattern analysis
            
        Returns:
            Formatted context string for LLM prompt
        """
        memories = self.get_agent_context(
            agent_name=agent_name,
            current_context=current_situation,
            limit=5
        )
        
        context_parts = [
            f"=== MEMORY CONTEXT FOR {agent_name.upper()} ===\n"
        ]
        
        if memories:
            context_parts.append("Recent relevant decisions:\n")
            for i, memory in enumerate(memories, 1):
                context_parts.append(f"\n{i}. Context: {memory.get('context', 'N/A')}")
                context_parts.append(f"   Decision: {memory.get('decision', 'N/A')}")
                if memory.get('outcome'):
                    context_parts.append(f"   Outcome: {memory['outcome']}")
                context_parts.append("")
        else:
            context_parts.append("No relevant past decisions found.\n")
        
        if include_patterns:
            patterns = self.analyze_agent_patterns(agent_name)
            if patterns['total_decisions'] > 0:
                context_parts.append("\nPattern Analysis:")
                context_parts.append(f"- Total decisions made: {patterns['total_decisions']}")
                if patterns['decision_types']:
                    context_parts.append(f"- Common decision types: {list(patterns['decision_types'].keys())}")
        
        context_parts.append("\n=== END MEMORY CONTEXT ===\n")
        
        return "\n".join(context_parts)
    
    def build_council_context_prompt(
        self,
        current_topic: str,
        limit: int = 3
    ) -> str:
        """
        Build context prompt from recent council decisions.
        
        Args:
            current_topic: Current topic/situation
            limit: Number of past decisions to include
            
        Returns:
            Formatted context string
        """
        decisions = self.get_recent_council_decisions(limit=limit)
        
        context_parts = [
            "=== RECENT COUNCIL DECISIONS ===\n"
        ]
        
        if decisions:
            for i, decision in enumerate(decisions, 1):
                context_parts.append(f"\n{i}. Cycle: {decision.get('cycle_id', 'N/A')}")
                context_parts.append(f"   Consensus: {decision.get('consensus_score', 0):.2%}")
                context_parts.append(f"   Rounds: {decision.get('debate_rounds', 0)}")
                
                final = decision.get('final_decision', {})
                if isinstance(final, dict):
                    context_parts.append(f"   Decision: {final.get('summary', 'N/A')[:100]}")
                
                conflicts = decision.get('conflicts_detected', [])
                if conflicts:
                    context_parts.append(f"   Conflicts: {len(conflicts)}")
                context_parts.append("")
        else:
            context_parts.append("No recent council decisions found.\n")
        
        context_parts.append("=== END COUNCIL CONTEXT ===\n")
        
        return "\n".join(context_parts)
    
    # ========================================
    # MEMORY MANAGEMENT
    # ========================================
    
    def prune_old_memories(
        self,
        days_to_keep: int = 90
    ):
        """
        Remove old memories to prevent database bloat.
        
        Args:
            days_to_keep: Number of days to retain
        """
        self.db.cleanup_old_records(days_to_keep=days_to_keep)
        
        # Clear cache
        self._memory_cache.clear()
        self._cache_timestamp.clear()
        
        logger.info(f"Pruned memories older than {days_to_keep} days")
    
    def clear_agent_cache(self, agent_name: Optional[str] = None):
        """
        Clear memory cache for an agent or all agents.
        
        Args:
            agent_name: Specific agent to clear, or None for all
        """
        if agent_name:
            if agent_name in self._memory_cache:
                del self._memory_cache[agent_name]
                del self._cache_timestamp[agent_name]
                logger.debug(f"Cleared cache for {agent_name}")
        else:
            self._memory_cache.clear()
            self._cache_timestamp.clear()
            logger.debug("Cleared all memory caches")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored memories.
        
        Returns:
            Dictionary with memory statistics
        """
        db_stats = self.db.get_database_stats()
        
        return {
            "total_agent_memories": db_stats.get('agent_memory', 0),
            "total_council_decisions": db_stats.get('council_decisions', 0),
            "total_engagement_records": db_stats.get('engagement_metrics', 0),
            "cache_size": len(self._memory_cache),
            "cached_agents": list(self._memory_cache.keys())
        }
    
    # ========================================
    # LEARNING & ADAPTATION
    # ========================================
    
    def calculate_agent_weight_adjustment(
        self,
        agent_name: str,
        recent_outcomes: List[str]
    ) -> float:
        """
        Calculate voting weight adjustment based on recent performance.
        
        Args:
            agent_name: Name of the agent
            recent_outcomes: List of recent outcomes
            
        Returns:
            Weight adjustment factor (0.8-1.2)
        """
        if not recent_outcomes:
            return 1.0
        
        # Count positive vs negative outcomes
        positive = sum(1 for o in recent_outcomes if 'positive' in o.lower() or 'success' in o.lower())
        negative = sum(1 for o in recent_outcomes if 'negative' in o.lower() or 'fail' in o.lower())
        
        if positive + negative == 0:
            return 1.0
        
        success_rate = positive / len(recent_outcomes)
        
        # Adjust weight based on success rate
        if success_rate >= 0.7:
            adjustment = 1.2  # Boost high performers
        elif success_rate >= 0.5:
            adjustment = 1.0  # Maintain average performers
        else:
            adjustment = 0.8  # Reduce weight for poor performers
        
        logger.debug(f"{agent_name} weight adjustment: {adjustment}x (success rate: {success_rate:.2%})")
        return adjustment
    
    def get_learning_insights(
        self,
        agent_name: str
    ) -> Dict[str, Any]:
        """
        Generate learning insights for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dictionary with insights
        """
        patterns = self.analyze_agent_patterns(agent_name)
        success_rate = self.get_success_rate(agent_name)
        
        insights = {
            "agent": agent_name,
            "success_rate": success_rate,
            "total_decisions": patterns['total_decisions'],
            "performance_level": "high" if success_rate >= 0.7 else "medium" if success_rate >= 0.5 else "low",
            "patterns": patterns,
            "recommendations": []
        }
        
        # Generate recommendations
        if success_rate < 0.5:
            insights['recommendations'].append("Review decision criteria and adjust strategy")
        
        if patterns['total_decisions'] < 10:
            insights['recommendations'].append("Insufficient data - continue gathering experience")
        
        return insights


# Singleton instance
_memory_manager_instance: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """
    Get or create memory manager singleton instance.
    
    Returns:
        MemoryManager instance
    """
    global _memory_manager_instance
    
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    
    return _memory_manager_instance
