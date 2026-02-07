"""
Autonomous Scheduler - Automated Execution Cycles
==================================================

Manages autonomous execution cycles for the AI council:
- Scheduled trend monitoring
- Automatic council triggering
- Content generation pipelines
- Performance tracking

Features:
- Configurable execution intervals
- Priority-based scheduling
- Error handling and retry logic
- Execution history tracking

Author: AI Systems Engineer  
Date: February 7, 2026
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from graph import CouncilGraph, Platform
from pipeline.trend_monitor import TrendMonitor, TrendOpportunity
from pipeline.content_generator import ContentGenerator
from db.database import DatabaseManager

logger = logging.getLogger(__name__)


class ScheduleMode(str, Enum):
    """Execution modes."""
    CONTINUOUS = "continuous"  # Run continuously
    INTERVAL = "interval"      # Run at intervals
    TRIGGERED = "triggered"    # Run on external trigger
    MANUAL = "manual"          # Manual execution only


@dataclass
class ExecutionCycle:
    """Represents an execution cycle."""
    cycle_id: str
    mode: ScheduleMode
    started_at: str
    completed_at: Optional[str]
    status: str  # running, completed, failed
    trends_detected: int
    councils_triggered: int
    content_generated: int
    errors: List[str]
    duration_seconds: Optional[float]


class AutonomousScheduler:
    """
    Autonomous scheduler for AI council execution.
    
    Orchestrates:
    1. Trend monitoring
    2. Council analysis (when needed)
    3. Content generation
    4. Performance feedback
    """
    
    def __init__(
        self,
        council_graph: Optional[CouncilGraph] = None,
        trend_monitor: Optional[TrendMonitor] = None,
        content_generator: Optional[ContentGenerator] = None,
        db_manager: Optional[DatabaseManager] = None,
        mode: ScheduleMode = ScheduleMode.INTERVAL,
        interval_minutes: int = 30
    ):
        """
        Initialize Autonomous Scheduler.
        
        Args:
            council_graph: Council graph instance
            trend_monitor: Trend monitor instance
            content_generator: Content generator instance
            db_manager: Database manager
            mode: Execution mode
            interval_minutes: Interval for scheduled execution
        """
        self.council = council_graph or CouncilGraph(auto_create_agents=True)
        self.trend_monitor = trend_monitor or TrendMonitor()
        self.content_generator = content_generator or ContentGenerator()
        self.db = db_manager or DatabaseManager()
        
        self.mode = mode
        self.interval = timedelta(minutes=interval_minutes)
        
        self.is_running = False
        self.execution_history: List[ExecutionCycle] = []
        
        logger.info(
            f"AutonomousScheduler initialized: mode={mode.value}, "
            f"interval={interval_minutes}min"
        )
    
    async def start(
        self,
        brand_keywords: List[str] = None,
        industry_keywords: List[str] = None
    ):
        """
        Start autonomous execution.
        
        Args:
            brand_keywords: Keywords related to brand
            industry_keywords: Industry keywords for trend filtering
        """
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.is_running = True
        logger.info(f"Starting autonomous scheduler in {self.mode.value} mode")
        
        try:
            if self.mode == ScheduleMode.CONTINUOUS:
                await self._run_continuous(brand_keywords, industry_keywords)
            elif self.mode == ScheduleMode.INTERVAL:
                await self._run_interval(brand_keywords, industry_keywords)
            else:
                logger.info("Manual mode - awaiting manual triggers")
                
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            self.is_running = False
            raise
    
    async def _run_continuous(
        self,
        brand_keywords: List[str],
        industry_keywords: List[str]
    ):
        """Run continuously with minimal delays."""
        while self.is_running:
            await self.execute_cycle(brand_keywords, industry_keywords)
            await asyncio.sleep(60)  # 1 minute between cycles
    
    async def _run_interval(
        self,
        brand_keywords: List[str],
        industry_keywords: List[str]
    ):
        """Run at configured intervals."""
        while self.is_running:
            await self.execute_cycle(brand_keywords, industry_keywords)
            logger.info(f"Next cycle in {self.interval.total_seconds()/60:.0f} minutes")
            await asyncio.sleep(self.interval.total_seconds())
    
    async def execute_cycle(
        self,
        brand_keywords: List[str] = None,
        industry_keywords: List[str] = None
    ) -> ExecutionCycle:
        """
        Execute a single autonomous cycle.
        
        Args:
            brand_keywords: Brand keywords
            industry_keywords: Industry keywords
            
        Returns:
            Execution cycle results
        """
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting execution cycle: {cycle_id}")
        
        cycle = ExecutionCycle(
            cycle_id=cycle_id,
            mode=self.mode,
            started_at=start_time.isoformat(),
            completed_at=None,
            status='running',
            trends_detected=0,
            councils_triggered=0,
            content_generated=0,
            errors=[],
            duration_seconds=None
        )
        
        try:
            # Step 1: Scan trends
            logger.info("Step 1: Scanning trends...")
            trends = self.trend_monitor.scan_trends(
                brand_keywords=brand_keywords,
                industry_keywords=industry_keywords
            )
            cycle.trends_detected = len(trends)
            logger.info(f"Detected {len(trends)} trends")
            
            # Step 2: Trigger council for high-priority trends
            logger.info("Step 2: Evaluating trends for council analysis...")
            for trend in trends:
                if self.trend_monitor.should_trigger_council(trend):
                    logger.info(f"Triggering council for: {trend.topic}")
                    
                    try:
                        # Run council analysis
                        council_state = await self.council.arun(
                            topic=trend.topic,
                            platform=trend.platform,
                            context={
                                'trend_data': trend.__dict__,
                                'urgency': trend.urgency,
                                'virality_potential': trend.virality_potential
                            },
                            trigger_event='trend_detection'
                        )
                        
                        cycle.councils_triggered += 1
                        
                        # Step 3: Generate content if approved
                        final_decision = council_state.get('arbitrator_decision', 'reject')
                        
                        if final_decision in ['approve', 'approve_with_modifications']:
                            logger.info("Decision approved - generating content")
                            
                            content = self.content_generator.generate_from_council_decision(
                                council_state=council_state,
                                platforms=[trend.platform]
                            )
                            
                            cycle.content_generated += 1
                            
                            # Store in database
                            self._store_results(
                                cycle_id=cycle_id,
                                trend=trend,
                                council_state=council_state,
                                content=content
                            )
                            
                        else:
                            logger.info(f"Decision: {final_decision} - no content generated")
                            
                    except Exception as e:
                        error_msg = f"Error processing trend {trend.topic}: {str(e)}"
                        logger.error(error_msg)
                        cycle.errors.append(error_msg)
            
            # Step 4: Cleanup expired trends
            logger.info("Step 4: Cleaning up expired trends...")
            expired = self.trend_monitor.cleanup_expired_trends()
            logger.info(f"Cleaned up {expired} expired trends")
            
            # Mark cycle complete
            cycle.status = 'completed'
            
        except Exception as e:
            cycle.status = 'failed'
            error_msg = f"Cycle execution failed: {str(e)}"
            logger.error(error_msg)
            cycle.errors.append(error_msg)
        
        finally:
            end_time = datetime.now()
            cycle.completed_at = end_time.isoformat()
            cycle.duration_seconds = (end_time - start_time).total_seconds()
            
            self.execution_history.append(cycle)
            
            logger.info(
                f"Cycle {cycle_id} {cycle.status}: "
                f"{cycle.trends_detected} trends, "
                f"{cycle.councils_triggered} councils, "
                f"{cycle.content_generated} content pieces, "
                f"{len(cycle.errors)} errors"
            )
        
        return cycle
    
    def _store_results(
        self,
        cycle_id: str,
        trend: TrendOpportunity,
        council_state: Dict[str, Any],
        content: Any
    ):
        """Store execution results in database."""
        try:
            # Store council decision
            self.db.store_council_decision(
                cycle_id=cycle_id,
                final_decision=str(council_state.get('final_decision', {})),
                reasoning_trace=str(council_state.get('reasoning_trace', [])),
                weights_snapshot=str(council_state.get('agent_weights', {})),
                agent_proposals=str(council_state.get('all_proposals', []))
            )
            
            logger.debug(f"Stored results for cycle {cycle_id}")
            
        except Exception as e:
            logger.error(f"Error storing results: {e}")
    
    def stop(self):
        """Stop autonomous execution."""
        logger.info("Stopping autonomous scheduler")
        self.is_running = False
    
    def manual_trigger(
        self,
        topic: str,
        platform: Platform = Platform.INSTAGRAM,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Manually trigger council analysis.
        
        Args:
            topic: Topic to analyze
            platform: Target platform
            context: Additional context
            
        Returns:
            Council decision and generated content
        """
        logger.info(f"Manual trigger: {topic}")
        
        # Run council synchronously for manual triggers
        council_state = self.council.run(
            topic=topic,
            platform=platform,
            context=context,
            trigger_event='manual_trigger'
        )
        
        # Generate content if approved
        content = None
        final_decision = council_state.get('arbitrator_decision', 'reject')
        
        if final_decision in ['approve', 'approve_with_modifications']:
            content = self.content_generator.generate_from_council_decision(
                council_state=council_state,
                platforms=[platform]
            )
        
        return {
            'council_state': council_state,
            'content': content,
            'decision': final_decision
        }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {'total_cycles': 0, 'message': 'No cycles executed yet'}
        
        total_cycles = len(self.execution_history)
        completed = sum(1 for c in self.execution_history if c.status == 'completed')
        failed = sum(1 for c in self.execution_history if c.status == 'failed')
        
        total_trends = sum(c.trends_detected for c in self.execution_history)
        total_councils = sum(c.councils_triggered for c in self.execution_history)
        total_content = sum(c.content_generated for c in self.execution_history)
        
        avg_duration = sum(
            c.duration_seconds for c in self.execution_history 
            if c.duration_seconds
        ) / max(total_cycles, 1)
        
        return {
            'total_cycles': total_cycles,
            'completed': completed,
            'failed': failed,
            'success_rate': completed / total_cycles if total_cycles > 0 else 0,
            'total_trends_detected': total_trends,
            'total_councils_triggered': total_councils,
            'total_content_generated': total_content,
            'average_cycle_duration_seconds': avg_duration,
            'is_running': self.is_running,
            'mode': self.mode.value
        }
    
    def get_recent_cycles(self, count: int = 5) -> List[ExecutionCycle]:
        """Get most recent execution cycles."""
        return self.execution_history[-count:]
