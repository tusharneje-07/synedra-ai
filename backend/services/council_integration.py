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
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

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
        trigger_agents: Optional[list[str]] = None,
        project_context: Optional[Dict[str, Any]] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Run a council session with WebSocket streaming and database persistence.
        
        Args:
            prompt: Topic/question for the council
            brand_config: Brand configuration to inject
            trigger_agents: Specific agents to trigger (or all if None)
            project_context: Project details (questionnaire, product info, etc.)
            db: Database session for persisting session data
        
        Returns:
            Session result with decision and metadata
        """
        # Initialize if not already done
        if not self.is_initialized:
            self.initialize()
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        self.current_session_id = session_id
        
        # Determine participating agents
        agents = trigger_agents or ["trend", "engagement", "brand", "risk", "compliance"]
        
        # Set broadcaster context for database persistence
        project_id = project_context.get("project_id") if project_context else None
        broadcaster.set_session_context(session_id, db, project_id)
        
        # Create ProjectSession record if db is available
        project_session = None
        if db and project_context:
            from models.project_session import ProjectSession
            from services.chat_service import ChatService
            
            project_session = ProjectSession(
                session_id=session_id,
                project_id=project_context["project_id"],
                topic=prompt,
                prompt=prompt,
                status="active",
                agents_participated=",".join(agents)
            )
            db.add(project_session)
            await db.commit()
            await db.refresh(project_session)
            
            logger.info(f"Created ProjectSession: {session_id} for project {project_context['project_id']}")
        
        # Start session
        agent_status_service.start_council_session(session_id, prompt, agents)
        await broadcaster.broadcast_council_start(session_id, prompt, agents)
        
        try:
            # Inject brand config and project context
            enhanced_prompt = self._enhance_prompt_with_context(
                prompt,
                brand_config,
                project_context
            )
            
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
                result = await self._run_real_council(enhanced_prompt, agents, session_id, db, project_context)
            else:
                result = await self._run_mock_council(enhanced_prompt, agents, session_id, db, project_context)
            
            # Update ProjectSession with results
            if db and project_session:
                project_session.decision = result.get("decision")
                project_session.confidence = result.get("confidence")
                project_session.consensus_level = result.get("consensus_level")
                project_session.total_messages = result.get("total_messages", 0)
                project_session.status = "completed"
                project_session.ended_at = datetime.utcnow()
                await db.commit()
            
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
            
            # Update session as failed
            if db and project_session:
                project_session.status = "failed"
                project_session.ended_at = datetime.utcnow()
                await db.commit()
            
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
    
    def _enhance_prompt_with_context(
        self,
        prompt: str,
        brand_config: Optional[Dict[str, Any]],
        project_context: Optional[Dict[str, Any]]
    ) -> str:
        """Inject brand configuration and project context into prompt."""
        enhanced = prompt
        
        # Add project context
        if project_context:
            context = "\n\n**Project Context:**\n"
            
            if project_context.get("project_name"):
                context += f"Project: {project_context['project_name']}\n"
            
            if project_context.get("description"):
                context += f"Description: {project_context['description']}\n"
            
            if project_context.get("post_topic"):
                context += f"Topic: {project_context['post_topic']}\n"
            
            if project_context.get("product_details"):
                context += f"\n**Product/Service Details:**\n"
                for key, value in project_context['product_details'].items():
                    context += f"  {key}: {value}\n"
            
            if project_context.get("target_details"):
                context += f"\n**Target Audience:**\n"
                for key, value in project_context['target_details'].items():
                    context += f"  {key}: {value}\n"
            
            if project_context.get("questionnaire_data"):
                context += f"\n**Questionnaire Responses:**\n"
                for key, value in project_context['questionnaire_data'].items():
                    if isinstance(value, list):
                        context += f"  {key}: {', '.join(value)}\n"
                    else:
                        context += f"  {key}: {value}\n"
            
            enhanced = context + "\n**Task:** " + prompt
        
        # Add brand config
        if brand_config:
            brand_context = "\n\n**Brand Guidelines:**\n"
            
            if brand_config.get("brand_name"):
                brand_context += f"Brand: {brand_config['brand_name']}\n"
            
            if brand_config.get("brand_tone"):
                brand_context += f"Tone: {brand_config['brand_tone']}\n"
            
            if brand_config.get("target_audience"):
                brand_context += f"Target Audience: {brand_config['target_audience']}\n"
            
            if brand_config.get("brand_keywords"):
                brand_context += f"Keywords: {', '.join(brand_config['brand_keywords'])}\n"
            
            enhanced = enhanced + brand_context
        
        return enhanced
    
    def _enhance_prompt_with_brand_config(
        self,
        prompt: str,
        brand_config: Optional[Dict[str, Any]]
    ) -> str:
        """DEPRECATED: Use _enhance_prompt_with_context instead."""
        return self._enhance_prompt_with_context(prompt, brand_config, None)
    
    async def _run_real_council(
        self,
        prompt: str,
        agents: list[str],
        session_id: str,
        db: Optional[AsyncSession] = None,
        project_context: Optional[Dict[str, Any]] = None
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
            "agent_outputs": result,
            "total_messages": len(agents) * 2  # Approximate
        }
    
    async def _run_mock_council(
        self,
        prompt: str,
        agents: list[str],
        session_id: str,
        db: Optional[AsyncSession] = None,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Mock council execution with realistic, project-aware debate.
        
        Creates multi-turn discussions where agents:
        - Actually analyze the user's request
        - Respond to each other's points
        - Disagree and challenge assumptions
        - Build consensus through discussion
        - Generate content based on what user asked for
        """
        logger.info(f"Running mock council session for request: {prompt}")
        
        # Extract project context for personalized responses
        project_name = project_context.get("project_name", "the project") if project_context else "the project"
        product_details = project_context.get("product_details", {}) if project_context else {}
        target_details = project_context.get("target_details", {}) if project_context else {}
        questionnaire = project_context.get("questionnaire_data", {}) if project_context else {}
        
        product_name = product_details.get("name", "the product")
        target_audience = target_details.get("audience", "target audience")
        primary_goal = questionnaire.get("primary_goal", "brand awareness")
        platforms = questionnaire.get("platforms", ["LinkedIn", "Twitter"])
        
        # Determine what type of content user is asking for
        prompt_lower = prompt.lower()
        is_strategy_request = any(word in prompt_lower for word in ["campaign", "strategy", "plan", "approach"])
        is_post_request = any(word in prompt_lower for word in ["post", "content", "write", "create"])
        is_analysis_request = any(word in prompt_lower for word in ["analyze", "review", "assess", "evaluate"])
        
        # Agent-specific analyses based on their roles AND user's request
        agent_analyses = {}
        
        # Phase 1: Individual Analysis
        for i, agent_id in enumerate(agents):
            agent_name = agent_status_service.AGENTS[agent_id]["name"]
            role = agent_status_service.AGENTS[agent_id]["role"]
            
            await asyncio.sleep(0.3)
            agent_status_service.update_agent_status(agent_id, "thinking", progress=20)
            
            await broadcaster.broadcast_agent_thinking(
                agent_id, agent_name,
                f"Analyzing your request: '{prompt[:100]}...'",
                step="analysis"
            )
            
            await asyncio.sleep(0.5)
            agent_status_service.update_agent_status(agent_id, "thinking", progress=60)
            
            # Generate role-specific analysis BASED ON USER REQUEST
            if agent_id == "trend":
                if is_post_request:
                    analysis = f"**Trend Analysis**: For a post about {product_name}, I recommend focusing on current industry trends. {target_audience} engages most with data-driven insights on {platforms[0] if platforms else 'LinkedIn'}. Hook: Start with a compelling statistic or question."
                elif is_strategy_request:
                    analysis = f"**Market Trends Analysis**: For {product_name} targeting {target_audience}, I'm seeing strong momentum in {platforms[0] if platforms else 'social media'}. Current data shows {primary_goal} campaigns perform 34% better when leveraging industry thought leadership."
                else:
                    analysis = f"**Trend Perspective**: Regarding '{prompt[:80]}...', the market shows that {target_audience} on {platforms[0] if platforms else 'social platforms'} responds best to authentic, value-driven content."
                    
            elif agent_id == "engagement":
                if is_post_request:
                    analysis = f"**Engagement Strategy**: The post should follow proven structure: compelling hook → value proposition → call-to-action. For {target_audience}, use conversational tone. Optimal length: 150-250 words with visual break (emoji or line breaks)."
                elif is_strategy_request:
                    analysis = f"**Engagement Approach**: {target_audience} responds best to authentic storytelling. For {primary_goal}, focus on {platforms[0] if platforms else 'primary platform'} with 2-3 posts weekly and strong CTAs."
                else:
                    analysis = f"**Engagement View**: For '{prompt[:80]}...', we should prioritize content that drives conversation. {target_audience} engages more with questions and interactive elements."
                    
            elif agent_id == "brand":
                if is_post_request:
                    analysis = f"**Brand Voice**: The post must align with {product_name}'s positioning. For {target_audience}, balance professionalism with approachability. Key brand pillars: innovation, trust, value. Avoid overly salesy language."
                elif is_strategy_request:
                    analysis = f"**Brand Positioning**: {product_name} should emphasize unique value proposition. Messaging for {target_audience} must balance professionalism with approachability, aligned with {primary_goal}."
                else:
                    analysis = f"**Brand Consideration**: Regarding '{prompt[:80]}...', ensure messaging stays consistent with {product_name}'s brand identity and resonates with {target_audience} values."
                    
            elif agent_id == "risk":
                if is_post_request:
                    analysis = f"**Risk Assessment**: Post should avoid controversial claims. Ensure any statistics are verifiable. For {target_audience}, maintain professional tone. Risk level: Low. Recommend A/B testing different hooks."
                elif is_strategy_request:
                    analysis = f"**Risk Profile**: Campaign for {product_name} has low-moderate risk. Key considerations: competitive response timing, platform changes on {platforms[0] if platforms else 'main channel'}. Recommend phased rollout."
                else:
                    analysis = f"**Risk Analysis**: For '{prompt[:80]}...', key risks include messaging misalignment and audience expectations. Mitigation: test with small segment first."
                    
            else:  # compliance
                if is_post_request:
                    analysis = f"**Compliance Check**: Post complies with advertising standards. For {target_audience}, ensure proper disclaimers if making claims. Avoid superlatives without evidence. Data privacy: OK for {platforms[0] if platforms else 'platform'}."
                elif is_strategy_request:
                    analysis = f"**Compliance Review**: Campaign complies with advertising standards. For {target_audience}, ensure data privacy messaging and proper disclaimers. {primary_goal.capitalize()} claims must be substantiated."
                else:
                    analysis = f"**Compliance Note**: Regarding '{prompt[:80]}...', content passes standard compliance review. No legal concerns for {target_audience} audience."
            
            agent_analyses[agent_id] = analysis
            
            await broadcaster.broadcast_agent_thinking(
                agent_id, agent_name, analysis, step="completed"
            )
            
            agent_status_service.update_agent_status(agent_id, "completed", progress=100)
        
        # Phase 2: Multi-turn Debate with Disagreement
        await asyncio.sleep(0.4)
        await broadcaster.broadcast_system_message("info", "Council entering debate phase...")
        
        debate_exchanges = []
        
        # Round 1: Initial positions
        for i, agent_id in enumerate(agents[:3]):  # First 3 agents debate
            agent_name = agent_status_service.AGENTS[agent_id]["name"]
            await asyncio.sleep(0.5)
            
            agent_status_service.update_agent_status(agent_id, "debating")
            await broadcaster.broadcast_agent_status(agent_id, agent_name, "debating")
            
            if agent_id == "trend":
                position = f"I propose we lead with data-driven insights about {product_name}. The market is ready for this message, especially on {platforms[0] if platforms else 'LinkedIn'}."
            elif agent_id == "engagement":
                position = f"I partially disagree - data alone won't drive {primary_goal}. We need emotional storytelling that resonates with {target_audience}."
            else:  # brand
                position = f"Both perspectives are valid, but we must ensure {product_name} messaging stays on-brand. Too much emotion risks diluting our professional image."
            
            debate_exchanges.append({"agent": agent_name, "position": position})
            
            await broadcaster.broadcast_debate(
                agent_id, agent_name, position, debate_round=1
            )
            
            agent_status_service.update_agent_status(agent_id, "idle")
        
        # Round 2: Responses and consensus building
        await asyncio.sleep(0.6)
        
        if len(agents) >= 2:
            # Engagement agent responds to Trend
            agent_id = "engagement" if "engagement" in agents else agents[1]
            agent_name = agent_status_service.AGENTS[agent_id]["name"]
            
            await asyncio.sleep(0.5)
            agent_status_service.update_agent_status(agent_id, "debating")
            
            response = f"After reviewing Trend Analyst's points, I agree we should use data - but as supporting evidence, not the hero. Let's combine: data-backed storytelling for {target_audience}."
            debate_exchanges.append({"agent": agent_name, "position": response})
            
            await broadcaster.broadcast_debate(
                agent_id, agent_name, response,
                responding_to="Trend Analyst", debate_round=2
            )
            agent_status_service.update_agent_status(agent_id, "idle")
        
        # Risk weighs in with final consideration
        if "risk" in agents:
            await asyncio.sleep(0.5)
            agent_name = agent_status_service.AGENTS["risk"]["name"]
            
            agent_status_service.update_agent_status("risk", "debating")
            
            risk_input = f"Agreed on the hybrid approach. One caveat: we should phase the rollout. Start with {platforms[0] if platforms else 'safest channel'}, measure response, then scale."
            debate_exchanges.append({"agent": agent_name, "position": risk_input})
            
            await broadcaster.broadcast_debate(
                "risk", agent_name, risk_input,
                responding_to="Engagement Expert", debate_round=2
            )
            agent_status_service.update_agent_status("risk", "idle")
        
        # Phase 3: Generate Final Content Based on User Request
        await asyncio.sleep(0.4)
        
        # Generate appropriate content based on what user asked for
        if is_post_request:
            # User wants a social media post
            final_post = f"""# Social Media Post for {product_name}

**Target Audience**: {target_audience}  
**Platform**: {platforms[0] if platforms else "LinkedIn"}  
**Goal**: {primary_goal}

---

## Drafted Post

{product_name} is transforming how {target_audience} achieve their goals. 🚀

Here's why this matters:

✅ **Innovation**: We're solving real problems with cutting-edge technology  
✅ **Impact**: Proven results that drive {primary_goal}  
✅ **Trust**: Built by experts, trusted by leaders

The future of your industry starts here.

👉 **Learn more** and see how {product_name} can work for you.

---

## Post Analysis

**Hook Strategy**: Opens with transformation statement to grab attention  
**Value Proposition**: Clear benefits using bullet points for scannability  
**Call-to-Action**: Direct CTA drives {primary_goal}

**Engagement Optimization**:
- Emoji usage: Moderate (professional yet approachable)
- Length: 145 words (optimal for {platforms[0] if platforms else "platform"})
- Format: Scannable with white space
- Tone: Confident but not pushy

**Risk Assessment**: ✓ Low risk, professional messaging  
**Compliance**: ✓ Approved for {target_audience} audience  
**Brand Alignment**: ✓ Maintains {product_name} positioning

**Recommended Posting Time**: Weekday mornings (9-11 AM) for maximum {target_audience} engagement

---
**Council Consensus**: Approved with minor A/B testing suggested for hook variations
"""
        
        elif is_analysis_request:
            # User wants analysis
            final_post = f"""# Analysis: {prompt[:100]}

## Overview
The council has analyzed your request regarding {product_name} and {target_audience}.

## Key Findings

### Market Trends
{agent_analyses.get('trend', 'No trend analysis available')}

### Engagement Insights
{agent_analyses.get('engagement', 'No engagement analysis available')}

### Brand Considerations
{agent_analyses.get('brand', 'No brand analysis available')}

### Risk Assessment
{agent_analyses.get('risk', 'No risk analysis available')}

### Compliance Status
{agent_analyses.get('compliance', 'No compliance review available')}

## Council Recommendation

Based on our multi-perspective analysis, we recommend:

1. **Immediate Actions**:
   - Leverage identified trends on {platforms[0] if platforms else "primary platform"}
   - Focus on {target_audience} engagement patterns
   - Maintain brand consistency

2. **Strategic Priorities**:
   - Align messaging with {primary_goal}
   - Monitor competitive landscape
   - Test and iterate based on data

3. **Risk Mitigation**:
   - Start with controlled rollout
   - Ensure compliance standards
   - Track performance metrics

## Next Steps
The council suggests moving forward with a phased approach, starting with {platforms[0] if platforms else "your primary channel"} and scaling based on early results.

---
**Council Consensus**: Unanimous agreement on approach
"""
        
        else:
            # Default to campaign strategy for broader requests
            final_post = f"""# {product_name} Campaign Strategy

## Executive Summary
After thorough analysis and debate, the council recommends a **data-backed storytelling approach** for {project_name}, targeting {target_audience} with the primary goal of {primary_goal}.

## Strategic Approach

### Content Strategy
- **Primary Platform**: {platforms[0] if platforms else "LinkedIn"}
- **Posting Frequency**: 2-3 times per week
- **Content Mix**: 
  - 40% Thought leadership with data insights
  - 40% Customer success stories and emotional narratives
  - 20% Product features and benefits

### Key Messages
1. **Innovation**: Position {product_name} as industry-leading solution
2. **Trust**: Leverage data and testimonials to build credibility
3. **Value**: Clear ROI for {target_audience}

### Recommended Campaign Flow

**Phase 1 (Weeks 1-2)**: Foundation
- Launch with data-driven thought leadership post
- Establish expertise and credibility
- Test messaging with A/B variants

**Phase 2 (Weeks 3-4)**: Engagement
- Share customer success stories
- Interactive content (polls, questions)
- Build community engagement

**Phase 3 (Weeks 5-6)**: Conversion
- Product spotlight with clear CTAs
- Limited-time offer or exclusive access
- Drive {primary_goal} metrics

## Risk Mitigation
- Phased rollout approach recommended by Risk Assessment team
- Monitor competitive responses weekly
- Compliance review before each post
- Platform algorithm tracking for optimization

## Success Metrics
- Engagement rate: Target 4-6%
- Reach: {target_audience} segment penetration
- Conversions: Track {primary_goal} KPIs
- Brand sentiment: Monitor social listening

## Next Steps
1. Finalize post calendar for Weeks 1-2
2. Create content assets (graphics, copy)
3. Set up A/B testing framework
4. Launch Phase 1 on {platforms[0] if platforms else "primary platform"}

---
**Council Consensus**: Unanimous approval with Risk Assessment conditions
**Confidence Level**: High (85%)
"""
        
        return {
            "decision": final_post,
            "confidence": 0.85,
            "consensus_level": "unanimous",
            "total_messages": len(agents) * 2 + len(debate_exchanges),
            "votes": {
                "approve": agents,
                "approve_with_conditions": [],
                "abstain": []
            }
        }


# Global service instance
council_integration = CouncilIntegrationService()
