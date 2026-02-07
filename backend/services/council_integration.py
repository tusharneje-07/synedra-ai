"""
Council Integration Service
===========================

Integrates FastAPI backend with existing CouncilGraph.
Bridges the AI council system with WebSocket streaming.
"""

import sys
import os
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

# Add AgenticEnv to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'AgenticEnv'))

from services.websocket_manager import manager
from services.agent_status import agent_status_service
from services.council_broadcaster import broadcaster

logger = logging.getLogger(__name__)


class CouncilIntegrationService:
    """
    Integrates existing CouncilGraph with FastAPI backend.
    
    Responsibilities:
    - Import and wrap CouncilGraph
    - Emit events to WebSocket clients
    - Update agent status in real-time
    - Handle brand configuration injection
    """
    
    def __init__(self):
        self.council_graph = None
        self.is_initialized = False
        self.current_session_id: Optional[str] = None
    
    def initialize(self):
        """
        Initialize CouncilGraph integration.
        
        Lazy loads the council system to avoid import errors.
        """
        if self.is_initialized:
            return True
        
        try:
            # Import council components
            from graph.council_graph import CouncilGraph
            
            # Create CouncilGraph instance
            self.council_graph = CouncilGraph()
            
            self.is_initialized = True
            logger.info("✓ CouncilGraph integration initialized")
            return True
        
        except ImportError as e:
            logger.error(f"Failed to import CouncilGraph: {e}")
            logger.warning("CouncilGraph not available - using mock mode")
            return False
        
        except Exception as e:
            logger.error(f"Failed to initialize CouncilGraph: {e}")
            return False
    
    async def run_council_session(
        self,
        prompt: str,
        brand_config: Optional[Dict[str, Any]] = None,
        trigger_agents: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Run a council session with WebSocket streaming.
        
        Args:
            prompt: Topic/question for the council
            brand_config: Brand configuration to inject
            trigger_agents: Specific agents to trigger (or all if None)
        
        Returns:
            Session result with decision and metadata
        """
        # Initialize if not already done
        if not self.is_initialized:
            self.initialize()
        
        # Generate session ID
        session_id = f"session_{datetime.utcnow().timestamp()}"
        self.current_session_id = session_id
        
        # Determine participating agents
        agents = trigger_agents or ["trend", "engagement", "brand", "risk", "compliance"]
        
        # Start session
        agent_status_service.start_council_session(session_id, prompt, agents)
        await broadcaster.broadcast_council_start(session_id, prompt, agents)
        
        try:
            # Inject brand config if provided
            enhanced_prompt = self._enhance_prompt_with_brand_config(prompt, brand_config)
            
            # Update agent statuses to thinking
            for agent_id in agents:
                agent_status_service.update_agent_status(
                    agent_id,
                    "thinking",
                    progress=0,
                    current_task=f"Analyzing: {prompt[:100]}"
                )
                await broadcaster.broadcast_agent_status(
                    agent_id,
                    agent_status_service.AGENTS[agent_id]["name"],
                    "thinking",
                    progress=0
                )
            
            # Run council (mock implementation if CouncilGraph not available)
            if self.council_graph and self.is_initialized:
                result = await self._run_real_council(enhanced_prompt, agents)
            else:
                result = await self._run_mock_council(enhanced_prompt, agents)
            
            # Broadcast decision
            await broadcaster.broadcast_decision(
                decision=result.get("decision", "No decision reached"),
                confidence=result.get("confidence", 0.8),
                consensus_level=result.get("consensus_level", "majority")
            )
            
            # End session
            agent_status_service.end_council_session()
            await broadcaster.broadcast_council_end(
                session_id,
                result.get("decision", "Session completed")
            )
            
            return {
                "session_id": session_id,
                "success": True,
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Council session error: {e}")
            
            # Broadcast error
            await broadcaster.broadcast_system_message(
                "error",
                f"Council session failed: {str(e)}"
            )
            
            # Clean up
            agent_status_service.end_council_session()
            
            return {
                "session_id": session_id,
                "success": False,
                "error": str(e)
            }
        
        finally:
            self.current_session_id = None
    
    def _enhance_prompt_with_brand_config(
        self,
        prompt: str,
        brand_config: Optional[Dict[str, Any]]
    ) -> str:
        """Inject brand configuration into prompt."""
        if not brand_config:
            return prompt
        
        context = "\n\n**Brand Context:**\n"
        
        if brand_config.get("brand_name"):
            context += f"Brand: {brand_config['brand_name']}\n"
        
        if brand_config.get("brand_tone"):
            context += f"Tone: {brand_config['brand_tone']}\n"
        
        if brand_config.get("target_audience"):
            context += f"Target Audience: {brand_config['target_audience']}\n"
        
        if brand_config.get("brand_keywords"):
            context += f"Keywords: {', '.join(brand_config['brand_keywords'])}\n"
        
        return context + "\n**Task:** " + prompt
    
    async def _run_real_council(
        self,
        prompt: str,
        agents: list[str]
    ) -> Dict[str, Any]:
        """
        Run actual CouncilGraph with event streaming.
        
        This wraps the existing council system and emits events
        during execution.
        """
        logger.info("Running CouncilGraph...")
        
        # Execute council (this will be enhanced in actual integration)
        # For now, using basic execution
        result = self.council_graph.run(prompt)
        
        # Extract decision
        return {
            "decision": result.get("final_decision", "No decision"),
            "confidence": 0.85,
            "consensus_level": "majority",
            "agent_outputs": result
        }
    
    async def _run_mock_council(
        self,
        prompt: str,
        agents: list[str]
    ) -> Dict[str, Any]:
        """
        Mock council execution for testing when CouncilGraph unavailable.
        
        Simulates agent thinking and debate with realistic delays.
        """
        logger.info("Running mock council session...")
        
        # Simulate agent analysis
        for i, agent_id in enumerate(agents):
            agent_name = agent_status_service.AGENTS[agent_id]["name"]
            
            # Thinking phase
            await asyncio.sleep(0.5)
            
            agent_status_service.update_agent_status(
                agent_id, "thinking", progress=30
            )
            await broadcaster.broadcast_agent_thinking(
                agent_id,
                agent_name,
                f"Analyzing from {agent_status_service.AGENTS[agent_id]['role']} perspective...",
                step="analysis"
            )
            
            await asyncio.sleep(0.8)
            
            # Progress update
            agent_status_service.update_agent_status(
                agent_id, "thinking", progress=60
            )
            
            # Analysis complete
            analysis = f"Based on {agent_status_service.AGENTS[agent_id]['role']}, I recommend focusing on {['data-driven insights', 'user engagement', 'brand consistency', 'risk mitigation', 'compliance requirements'][i % 5]}."
            
            await broadcaster.broadcast_agent_thinking(
                agent_id,
                agent_name,
                analysis,
                step="completed"
            )
            
            agent_status_service.update_agent_status(
                agent_id, "completed", progress=100
            )
        
        # Debate phase
        await asyncio.sleep(0.5)
        await broadcaster.broadcast_system_message(
            "info",
            "Council entering debate phase..."
        )
        
        # Simulate debate
        for i in range(min(3, len(agents))):
            agent_id = agents[i]
            agent_name = agent_status_service.AGENTS[agent_id]["name"]
            
            agent_status_service.update_agent_status(agent_id, "debating")
            await broadcaster.broadcast_agent_status(agent_id, agent_name, "debating")
            
            await asyncio.sleep(0.6)
            
            await broadcaster.broadcast_debate(
                agent_id,
                agent_name,
                f"From the {agent_status_service.AGENTS[agent_id]['role']} perspective, we should prioritize...",
                debate_round=1
            )
            
            await asyncio.sleep(0.4)
            agent_status_service.update_agent_status(agent_id, "idle")
        
        # Final decision
        return {
            "decision": f"Proceed with strategy addressing: {prompt}. Implementation should balance innovation with risk management.",
            "confidence": 0.82,
            "consensus_level": "majority",
            "votes": {
                "approve": agents[:3],
                "approve_with_conditions": agents[3:4] if len(agents) > 3 else [],
                "abstain": agents[4:] if len(agents) > 4 else []
            }
        }


# Global service instance
council_integration = CouncilIntegrationService()
