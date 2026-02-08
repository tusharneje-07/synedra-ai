"""
Debate Orchestrator - Manages the multi-agent debate process
Runs agents sequentially and collects their outputs
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
from database import get_db
from agents import (
    TrendAgent,
    BrandAgent,
    ComplianceAgent,
    RiskAgent,
    EngagementAgent,
    CMOAgent
)

logger = logging.getLogger(__name__)

class DebateOrchestrator:
    """Orchestrates the debate between multiple agents"""
    
    def __init__(self):
        """Initialize orchestrator with all agents"""
        self.db = get_db()
        
        # Initialize all agents
        self.trend_agent = TrendAgent()
        self.brand_agent = BrandAgent()
        self.compliance_agent = ComplianceAgent()
        self.risk_agent = RiskAgent()
        self.engagement_agent = EngagementAgent()
        self.cmo_agent = CMOAgent()
        self.live_updates_callback = None  # Will be set by caller
        
        logger.info("DebateOrchestrator initialized with 6 agents")
    
    def set_live_updates_callback(self, callback):
        """Set callback function to push live updates"""
        self.live_updates_callback = callback
    
    def _push_update(self, message_type, agent, content, metadata=None):
        """Push live update to frontend"""
        if self.live_updates_callback:
            update = {
                'type': message_type,
                'agent': agent,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            if metadata:
                update.update(metadata)
            self.live_updates_callback(update)
    
    def run_debate(
        self,
        post_input_id: int,
        brand_data: Dict[str, Any],
        post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a DYNAMIC multi-agent debate like a REAL heated team meeting
        - Agents jump in multiple times with rapid responses
        - Fast, instinct-driven reactions
        - Dynamic turn-based conversation (not fixed rounds)
        - CMO monitors live and stops when ready
        
        CRITICAL: Tests API health before starting
        
        Args:
            post_input_id: ID of the post input
            brand_data: Brand configuration data
            post_data: Post input data
            
        Returns:
            Dict with full conversation transcript and CMO decision
        """
        logger.info(f"=== STARTING DYNAMIC TEAM DEBATE for post_input_id: {post_input_id} ===")
        
        # CRITICAL: Check API health before starting
        from utils.api_manager import ensure_api_health, get_active_api_key, get_current_key_name
        try:
            ensure_api_health()
            # Get and log the API key being used
            current_key = get_active_api_key()
            current_key_name = get_current_key_name(current_key)
            logger.info(f"🔑 Debate will use API key: {current_key_name}")
        except Exception as e:
            logger.error(f"❌ API Health Check Failed: {str(e)}")
            return {
                'success': False,
                'error': f'API Health Check Failed: {str(e)}',
                'post_input_id': post_input_id,
                'message': 'Please ensure at least one working API key is configured in Settings.'
            }
        
        # Build context for all agents (including intervention if present)
        human_intervention = post_data.get('human_intervention')
        tagged_agents = post_data.get('tagged_agents', [])
        context = self._build_context(brand_data, post_data, human_intervention, tagged_agents)
        
        # Track conversation for frontend display
        conversation_messages = []
        conversation_messages.append({
            'type': 'system',
            'agent': 'SYSTEM',
            'message': f'Using API Key: {current_key_name}',
            'timestamp': 'start'
        })
        
        try:
            # PHASE 1: Quick initial reactions (everyone speaks once)
            logger.info("🎙️ PHASE 1: Initial quick reactions from all agents")
            conversation_messages.append({
                'type': 'phase',
                'agent': 'SYSTEM',
                'message': 'Phase 1: Initial Quick Reactions',
                'timestamp': 'phase1'
            })
            initial_reactions = self._get_initial_reactions(context, post_input_id, conversation_messages)
            
            # PHASE 2: DYNAMIC CONVERSATION - agents jump in with rapid responses
            logger.info("💬 PHASE 2: Open conversation - agents jumping in dynamically")
            conversation_messages.append({
                'type': 'phase',
                'agent': 'SYSTEM',
                'message': 'Phase 2: Dynamic Conversation',
                'timestamp': 'phase2'
            })
            conversation_log = self._run_dynamic_conversation(
                context, 
                initial_reactions, 
                post_input_id,
                conversation_messages,
                max_turns=20,  # Allow up to 20 back-and-forth exchanges
                min_turns=5    # Minimum 5 turns before allowing convergence to stop
            )
            
            # CMO INTERVENTION: Stops the debate and makes final call
            logger.info("👔 CMO: Stopping the debate and making final decision")
            conversation_messages.append({
                'type': 'phase',
                'agent': 'SYSTEM',
                'message': 'CMO Making Final Decision',
                'timestamp': 'cmo'
            })
            
            full_transcript = {
                'initial_reactions': initial_reactions,
                'conversation': conversation_log['turns'],
                'total_exchanges': conversation_log['turn_count'],
                'convergence_reached': conversation_log['converged']
            }
            
            cmo_decision = self.cmo_agent.moderate_and_decide(
                context, 
                full_transcript,
                should_wrap_up=conversation_log['converged']
            )
            self._save_agent_debate(post_input_id, cmo_decision)
            
            # Push CMO decision to frontend with full details
            cmo_statement = cmo_decision.get('moderator_statement', '') or cmo_decision.get('final_decision', '')
            cmo_reasoning = cmo_decision.get('reasoning', '')
            cmo_vote = cmo_decision.get('final_vote', 'unknown')
            
            cmo_full_message = f"📋 FINAL DECISION: {cmo_vote.upper()}\n\n"
            cmo_full_message += f"💭 {cmo_statement}\n\n"
            if cmo_reasoning:
                cmo_full_message += f"🔍 REASONING: {cmo_reasoning}"
            
            self._push_update('message', 'CMOAgent', cmo_full_message, {
                'vote': cmo_vote,
                'reasoning': cmo_reasoning,
                'argument': cmo_statement
            })
            
            logger.info(f"=== DEBATE CONCLUDED after {conversation_log['turn_count']} exchanges - Decision: {cmo_decision.get('final_vote')} ===")
            
            conversation_messages.append({
                'type': 'decision',
                'agent': 'CMOAgent',
                'message': f"Final Decision: {cmo_decision.get('final_vote')}",
                'timestamp': 'end'
            })
            
            return {
                'success': True,
                'post_input_id': post_input_id,
                'debate_transcript': full_transcript,
                'cmo_decision': cmo_decision,
                'final_vote': cmo_decision.get('final_vote'),
                'total_exchanges': conversation_log['turn_count'],
                'context': context,
                'api_key_name': current_key_name,
                'conversation_log': conversation_messages
            }
            
        except Exception as e:
            logger.error(f"Error during debate process: {e}")
            return {
                'success': False,
                'error': str(e),
                'post_input_id': post_input_id
            }
    
    def _get_initial_reactions(self, context: Dict, post_input_id: int, conversation_messages: list) -> Dict[str, Any]:
        """Phase 1: Quick initial gut reactions from all agents"""
        reactions = {}
        
        # Add intervention context to each agent if present
        intervention_context = context.get('human_intervention')
        if intervention_context:
            logger.info(f"Human intervention detected: {intervention_context.get('message')[:100]}...")
            conversation_messages.append({
                'type': 'intervention',
                'agent': 'HUMAN',
                'message': intervention_context.get('message'),
                'tagged_agents': intervention_context.get('tagged_agents', [])
            })
        
        logger.info("  📊 TrendAgent: Quick reaction...")
        self._push_update('thinking', 'TrendAgent', 'Analyzing current trends and market data...')
        conversation_messages.append({'type': 'thinking', 'agent': 'TrendAgent', 'message': 'Analyzing trends...'})
        # Add intervention prompt if applicable
        trend_context = self._add_intervention_to_context(context, 'TrendAgent')
        trend_reaction = self.trend_agent.quick_reaction(trend_context)
        reactions['TrendAgent'] = trend_reaction
        self._save_agent_debate(post_input_id, trend_reaction)
        score = trend_reaction.get('score', 'N/A')
        vote = trend_reaction.get('vote', 'unknown')
        reasoning = trend_reaction.get('reasoning', '')
        self._push_update('reaction', 'TrendAgent', f"Score: {score}/100 - Vote: {vote}", {'reasoning': reasoning, 'score': score, 'vote': vote})
        conversation_messages.append({'type': 'reaction', 'agent': 'TrendAgent', 'message': f"Score: {score}/100"})
        
        logger.info("  🎨 BrandAgent: Quick reaction...")
        self._push_update('thinking', 'BrandAgent', 'Checking brand alignment and voice consistency...')
        conversation_messages.append({'type': 'thinking', 'agent': 'BrandAgent', 'message': 'Checking brand alignment...'})
        brand_context = self._add_intervention_to_context(context, 'BrandAgent')
        brand_reaction = self.brand_agent.quick_reaction(brand_context)
        reactions['BrandAgent'] = brand_reaction
        self._save_agent_debate(post_input_id, brand_reaction)
        score = brand_reaction.get('score', 'N/A')
        vote = brand_reaction.get('vote', 'unknown')
        reasoning = brand_reaction.get('reasoning', '')
        self._push_update('reaction', 'BrandAgent', f"Score: {score}/100 - Vote: {vote}", {'reasoning': reasoning, 'score': score, 'vote': vote})
        conversation_messages.append({'type': 'reaction', 'agent': 'BrandAgent', 'message': f"Score: {score}/100"})
        
        logger.info("  ⚖️ ComplianceAgent: Quick reaction...")
        self._push_update('thinking', 'ComplianceAgent', 'Verifying compliance and regulatory requirements...')
        conversation_messages.append({'type': 'thinking', 'agent': 'ComplianceAgent', 'message': 'Verifying compliance...'})
        compliance_context = self._add_intervention_to_context(context, 'ComplianceAgent')
        compliance_reaction = self.compliance_agent.quick_reaction(compliance_context)
        reactions['ComplianceAgent'] = compliance_reaction
        self._save_agent_debate(post_input_id, compliance_reaction)
        score = compliance_reaction.get('score', 'N/A')
        vote = compliance_reaction.get('vote', 'unknown')
        reasoning = compliance_reaction.get('reasoning', '')
        self._push_update('reaction', 'ComplianceAgent', f"Score: {score}/100 - Vote: {vote}", {'reasoning': reasoning, 'score': score, 'vote': vote})
        conversation_messages.append({'type': 'reaction', 'agent': 'ComplianceAgent', 'message': f"Score: {score}/100"})
        
        logger.info("  🛡️ RiskAgent: Quick reaction...")
        self._push_update('thinking', 'RiskAgent', 'Assessing potential risks and vulnerabilities...')
        conversation_messages.append({'type': 'thinking', 'agent': 'RiskAgent', 'message': 'Assessing risks...'})
        risk_context = self._add_intervention_to_context(context, 'RiskAgent')
        risk_reaction = self.risk_agent.quick_reaction(risk_context)
        reactions['RiskAgent'] = risk_reaction
        self._save_agent_debate(post_input_id, risk_reaction)
        score = risk_reaction.get('score', 'N/A')
        vote = risk_reaction.get('vote', 'unknown')
        reasoning = risk_reaction.get('reasoning', '')
        self._push_update('reaction', 'RiskAgent', f"Score: {score}/100 - Vote: {vote}", {'reasoning': reasoning, 'score': score, 'vote': vote})
        conversation_messages.append({'type': 'reaction', 'agent': 'RiskAgent', 'message': f"Score: {score}/100"})
        
        logger.info("  💬 EngagementAgent: Quick reaction...")
        self._push_update('thinking', 'EngagementAgent', 'Evaluating engagement potential and virality...')
        conversation_messages.append({'type': 'thinking', 'agent': 'EngagementAgent', 'message': 'Evaluating engagement...'})
        engagement_context = self._add_intervention_to_context(context, 'EngagementAgent')
        engagement_reaction = self.engagement_agent.quick_reaction(engagement_context)
        reactions['EngagementAgent'] = engagement_reaction
        self._save_agent_debate(post_input_id, engagement_reaction)
        score = engagement_reaction.get('score', 'N/A')
        vote = engagement_reaction.get('vote', 'unknown')
        reasoning = engagement_reaction.get('reasoning', '')
        self._push_update('reaction', 'EngagementAgent', f"Score: {score}/100 - Vote: {vote}", {'reasoning': reasoning, 'score': score, 'vote': vote})
        conversation_messages.append({'type': 'reaction', 'agent': 'EngagementAgent', 'message': f"Score: {score}/100"})
        
        return reactions
    
    def _add_intervention_to_context(self, context: Dict, agent_name: str) -> Dict:
        """Add intervention prompt to context if present and relevant to agent"""
        if 'human_intervention' not in context:
            return context
        
        # Create a copy of context with intervention prompt
        new_context = context.copy()
        intervention_prompt = self._build_agent_prompt_with_intervention(context, agent_name)
        
        # Add intervention prompt to post requirements
        if intervention_prompt:
            current_requirements = new_context['post'].get('requirements', '')
            new_context['post']['requirements'] = current_requirements + '\n\n' + intervention_prompt
        
        return new_context
    
    def _run_dynamic_conversation(self, context: Dict, initial_reactions: Dict, post_input_id: int, conversation_messages: list, max_turns: int = 20, min_turns: int = 5) -> Dict[str, Any]:
        """
        Dynamic conversation where agents jump in with rapid responses
        Like a real heated meeting with back-and-forth
        
        Args:
            min_turns: Minimum number of turns before convergence can stop the debate
            max_turns: Maximum number of turns allowed
        """
        conversation_turns = []
        agent_list = ['TrendAgent', 'BrandAgent', 'ComplianceAgent', 'RiskAgent', 'EngagementAgent']
        agent_objects = {
            'TrendAgent': self.trend_agent,
            'BrandAgent': self.brand_agent,
            'ComplianceAgent': self.compliance_agent,
            'RiskAgent': self.risk_agent,
            'EngagementAgent': self.engagement_agent
        }
        
        # Track who spoke last to encourage different voices
        last_speaker = None
        
        for turn in range(max_turns):
            # Build conversation history
            conversation_history = {
                'initial': initial_reactions,
                'exchanges': conversation_turns
            }
            
            # Check convergence every 3 turns, but ONLY after minimum turns requirement
            if turn >= min_turns and turn % 3 == 0:
                convergence = self._check_conversation_convergence(initial_reactions, conversation_turns)
                logger.info(f"  📊 Turn {turn+1}: Convergence check - {convergence['consensus_level']:.0%} agreement")
                
                if convergence['consensus_level'] >= 0.75:
                    logger.info(f"  ✅ Strong consensus reached after {turn+1} turns - ending conversation")
                    return {
                        'turns': conversation_turns,
                        'turn_count': turn + 1,
                        'converged': True,
                        'final_convergence': convergence
                    }
            
            # Pick next speaker (prioritize those who disagree or haven't spoken recently)
            next_speaker = self._pick_next_speaker(agent_list, last_speaker, initial_reactions, conversation_turns)
            agent = agent_objects[next_speaker]
            
            logger.info(f"  💬 Turn {turn+1}/{max_turns}: {next_speaker} jumping in...")
            
            # Agent responds to the current conversation
            response = agent.jump_in_conversation(context, conversation_history)
            
            conversation_turn = {
                'turn': turn + 1,
                'speaker': next_speaker,
                'response': response
            }
            
            conversation_turns.append(conversation_turn)
            self._save_agent_debate(post_input_id, response)
            
            # Extract response fields - handle multiple possible field names
            vote = response.get('vote', 'unknown')
            passion = response.get('passion_level', 'calm')
            
            # Get argument/reasoning - check multiple possible field names
            argument = (
                response.get('argument') or 
                response.get('response') or 
                response.get('recommendation') or 
                response.get('reasoning') or
                'Analysis in progress...'
            )
            
            reasoning = (
                response.get('reasoning') or
                response.get('response') or
                response.get('explanation') or
                ''
            )
            
            # For jump_in_conversation, 'response' is the main content
            if 'response' in response and not response.get('argument'):
                argument = response['response']
                
            logger.info(f"    → Response extracted: {argument[:100]}...")
            
            # Push detailed update with actual argument
            self._push_update('message', next_speaker, argument, {
                'vote': vote,
                'passion': passion,
                'reasoning': reasoning,
                'argument': argument
            })
            
            conversation_messages.append({
                'type': 'message',
                'agent': next_speaker,
                'message': argument,
                'vote': vote,
                'passion': passion
            })
            
            last_speaker = next_speaker
            
            # Log the intensity
            logger.info(f"    → {passion.upper()} response, voting: {vote}")
        
        # Reached max turns without convergence
        final_convergence = self._check_conversation_convergence(initial_reactions, conversation_turns)
        logger.info(f"  ⏱️ Max turns reached ({max_turns}) - ending conversation")
        
        return {
            'turns': conversation_turns,
            'turn_count': max_turns,
            'converged': False,
            'final_convergence': final_convergence
        }
    
    def _pick_next_speaker(self, agent_list: list, last_speaker: str, initial_reactions: Dict, conversation_turns: list) -> str:
        """Pick the next agent to speak - prioritize those with strong opinions or who haven't spoken recently"""
        import random
        from collections import Counter
        
        # Count how many times each agent has spoken in conversation
        speaker_counts = Counter([turn['speaker'] for turn in conversation_turns])
        
        # Get the most recent votes
        latest_votes = {}
        for agent_name in agent_list:
            # Check latest vote in conversation turns
            for turn in reversed(conversation_turns):
                if turn['speaker'] == agent_name:
                    latest_votes[agent_name] = turn['response'].get('vote')
                    break
            # Fall back to initial reaction if not spoken yet
            if agent_name not in latest_votes:
                latest_votes[agent_name] = initial_reactions.get(agent_name, {}).get('vote', 'unknown')
        
        # Find agents who disagree with majority
        vote_distribution = Counter(latest_votes.values())
        majority_vote = vote_distribution.most_common(1)[0][0] if vote_distribution else 'approve'
        
        dissenters = [agent for agent in agent_list if latest_votes.get(agent) != majority_vote]
        least_spoken = [agent for agent in agent_list if speaker_counts[agent] < 2]
        
        # Priority: dissenters who haven't spoken much
        candidates = list(set(dissenters) & set(least_spoken)) if dissenters and least_spoken else \
                     dissenters if dissenters else \
                     least_spoken if least_spoken else \
                     [agent for agent in agent_list if agent != last_speaker]
        
        if not candidates:
            candidates = [agent for agent in agent_list if agent != last_speaker]
        
        return random.choice(candidates) if candidates else random.choice(agent_list)
    
    def _check_conversation_convergence(self, initial_reactions: Dict, conversation_turns: list) -> Dict[str, Any]:
        """Check if the conversation is converging towards agreement"""
        from collections import Counter
        
        # Get latest vote from each agent
        latest_votes = {}
        agent_list = ['TrendAgent', 'BrandAgent', 'ComplianceAgent', 'RiskAgent', 'EngagementAgent']
        
        for agent_name in agent_list:
            # Check conversation turns in reverse
            for turn in reversed(conversation_turns):
                if turn['speaker'] == agent_name:
                    latest_votes[agent_name] = turn['response'].get('vote', 'conditional')
                    break
            # Fall back to initial if not in conversation
            if agent_name not in latest_votes:
                latest_votes[agent_name] = initial_reactions.get(agent_name, {}).get('vote', 'conditional')
        
        # Calculate consensus
        vote_counts = Counter(latest_votes.values())
        total_agents = len(latest_votes)
        max_agreement = max(vote_counts.values()) if vote_counts else 0
        consensus_level = max_agreement / total_agents if total_agents > 0 else 0
        
        majority_vote = vote_counts.most_common(1)[0][0] if vote_counts else 'conditional'
        
        return {
            'consensus_level': consensus_level,
            'majority_vote': majority_vote,
            'vote_distribution': dict(vote_counts),
            'latest_votes': latest_votes
        }
    
    def _run_round_2_open_floor(self, context: Dict, round1: Dict, post_input_id: int) -> Dict[str, Any]:
        """
        Round 2: OPEN FLOOR - Everyone responds to EVERYONE
        Like a real meeting where everyone can hear everyone
        """
        responses = {}
        
        # Each agent sees ALL other agents' views
        all_others_views = round1.copy()
        
        logger.info("  📊 TrendAgent responding to the room...")
        all_others_views_for_trend = {k: v for k, v in round1.items() if k != 'trend'}
        trend_response = self.trend_agent.respond_to_everyone(
            context,
            my_previous=round1['trend'],
            everyone_else=all_others_views_for_trend
        )
        responses['trend'] = trend_response
        self._save_agent_debate(post_input_id, trend_response)
        
        logger.info("  🎨 BrandAgent responding to the room...")
        all_others_views_for_brand = {k: v for k, v in round1.items() if k != 'brand'}
        brand_response = self.brand_agent.respond_to_everyone(
            context,
            my_previous=round1['brand'],
            everyone_else=all_others_views_for_brand
        )
        responses['brand'] = brand_response
        self._save_agent_debate(post_input_id, brand_response)
        
        logger.info("  ⚖️ ComplianceAgent responding to the room...")
        all_others_views_for_compliance = {k: v for k, v in round1.items() if k != 'compliance'}
        compliance_response = self.compliance_agent.respond_to_everyone(
            context,
            my_previous=round1['compliance'],
            everyone_else=all_others_views_for_compliance
        )
        responses['compliance'] = compliance_response
        self._save_agent_debate(post_input_id, compliance_response)
        
        logger.info("  🛡️ RiskAgent responding to the room...")
        all_others_views_for_risk = {k: v for k, v in round1.items() if k != 'risk'}
        risk_response = self.risk_agent.respond_to_everyone(
            context,
            my_previous=round1['risk'],
            everyone_else=all_others_views_for_risk
        )
        responses['risk'] = risk_response
        self._save_agent_debate(post_input_id, risk_response)
        
        logger.info("  💬 EngagementAgent responding to the room...")
        all_others_views_for_engagement = {k: v for k, v in round1.items() if k != 'engagement'}
        engagement_response = self.engagement_agent.respond_to_everyone(
            context,
            my_previous=round1['engagement'],
            everyone_else=all_others_views_for_engagement
        )
        responses['engagement'] = engagement_response
        self._save_agent_debate(post_input_id, engagement_response)
        
        return responses
    
    def _run_round_3_final_clash(self, context: Dict, round1: Dict, round2: Dict, post_input_id: int) -> Dict[str, Any]:
        """
        Round 3: Final heated exchange - agents directly confront disagreements
        Only happens if debate hasn't converged
        """
        responses = {}
        
        full_conversation = {
            'round1': round1,
            'round2': round2
        }
        
        logger.info("  📊 TrendAgent making final stand...")
        trend_response = self.trend_agent.final_confrontation(context, full_conversation)
        responses['trend'] = trend_response
        self._save_agent_debate(post_input_id, trend_response)
        
        logger.info("  🎨 BrandAgent making final stand...")
        brand_response = self.brand_agent.final_confrontation(context, full_conversation)
        responses['brand'] = brand_response
        self._save_agent_debate(post_input_id, brand_response)
        
        logger.info("  ⚖️ ComplianceAgent making final stand...")
        compliance_response = self.compliance_agent.final_confrontation(context, full_conversation)
        responses['compliance'] = compliance_response
        self._save_agent_debate(post_input_id, compliance_response)
        
        logger.info("  🛡️ RiskAgent making final stand...")
        risk_response = self.risk_agent.final_confrontation(context, full_conversation)
        responses['risk'] = risk_response
        self._save_agent_debate(post_input_id, risk_response)
        
        logger.info("  💬 EngagementAgent making final stand...")
        engagement_response = self.engagement_agent.final_confrontation(context, full_conversation)
        responses['engagement'] = engagement_response
        self._save_agent_debate(post_input_id, engagement_response)
        
        return responses
    
    def _evaluate_debate_convergence(self, round1: Dict, round2: Dict) -> Dict[str, Any]:
        """
        Evaluate if the debate is converging (agreement forming) or diverging (more conflict)
        This helps CMO decide if they need to let debate continue or wrap it up
        """
        # Count votes in each round
        round1_votes = [a.get('vote') for a in round1.values()]
        round2_votes = [a.get('vote') for a in round2.values()]
        
        # Calculate consensus level
        from collections import Counter
        round1_consensus = max(Counter(round1_votes).values()) / len(round1_votes)
        round2_consensus = max(Counter(round2_votes).values()) / len(round2_votes)
        
        # Check if positions are changing (agents changing votes)
        positions_changed = sum(
            1 for agent_key in round1.keys()
            if round1[agent_key].get('vote') != round2[agent_key].get('vote')
        )
        
        # Converging if consensus is increasing and fewer position changes
        converging = round2_consensus >= round1_consensus and positions_changed <= 2
        
        return {
            'converging': converging,
            'consensus_level': round2_consensus,
            'positions_changed': positions_changed,
            'majority_vote': Counter(round2_votes).most_common(1)[0][0] if round2_votes else None,
            'vote_distribution': dict(Counter(round2_votes))
        }
    
    def _build_context(
        self,
        brand_data: Dict[str, Any],
        post_data: Dict[str, Any],
        human_intervention: str = None,
        tagged_agents: List[str] = None
    ) -> Dict[str, Any]:
        """Build comprehensive context for agents with optional human intervention"""
        context = {
            'brand': {
                'name': brand_data.get('brand_name'),
                'tone': brand_data.get('brand_tone'),
                'description': brand_data.get('brand_description'),
                'target_audience': brand_data.get('target_audience'),
                'keywords': brand_data.get('brand_keywords'),
                'guidelines': brand_data.get('messaging_guidelines'),
                'platforms': brand_data.get('social_platforms'),
                'competitors': brand_data.get('competitors'),
                'market_segment': brand_data.get('market_segment'),
            },
            'post': {
                'topic': post_data.get('post_topic'),
                'objective': post_data.get('post_objective'),
                'platform': post_data.get('target_platform'),
                'content_type': post_data.get('content_type'),
                'key_message': post_data.get('key_message'),
                'cta': post_data.get('call_to_action', ''),
                'requirements': post_data.get('special_requirements', ''),
            }
        }
        
        # Add human intervention if provided
        if human_intervention:
            context['human_intervention'] = {
                'message': human_intervention,
                'tagged_agents': tagged_agents or [],
                'priority': 'high'
            }
        
        return context
    
    def run_debate_with_intervention(
        self,
        post_input_id: int,
        post_input: Dict[str, Any],
        intervention_message: str,
        tagged_agents: List[str]
    ):
        """
        Run debate with human intervention incorporated
        This is a wrapper that adds intervention context to the regular debate
        """
        logger.info(f"Running debate with human intervention for post_input_id: {post_input_id}")
        logger.info(f"Intervention message: {intervention_message}")
        logger.info(f"Tagged agents: {tagged_agents}")
        
        try:
            # Get brand data
            brand_id = post_input.get('brand_id')
            if not brand_id:
                logger.error("No brand_id found in post_input")
                return
            
            brand_data = self.db.get_brand(brand_id)
            if not brand_data:
                logger.error(f"Brand not found for id: {brand_id}")
                return
            
            # Add intervention context to post data
            post_input['human_intervention'] = intervention_message
            post_input['tagged_agents'] = tagged_agents
            
            logger.info("Starting debate with intervention context...")
            # Run the regular debate which will now include intervention context
            result = self.run_debate(post_input_id, brand_data, post_input)
            logger.info(f"Debate completed with intervention. Success: {result.get('success', False)}")
            return result
        except Exception as e:
            logger.error(f"Error in run_debate_with_intervention: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_agent_prompt_with_intervention(
        self,
        base_context: Dict[str, Any],
        agent_name: str
    ) -> str:
        """Build agent prompt including human intervention if present"""
        intervention = base_context.get('human_intervention')
        
        if not intervention:
            return ""
        
        message = intervention.get('message', '')
        tagged_agents = intervention.get('tagged_agents', [])
        
        # Check if this agent is tagged
        is_tagged = agent_name in tagged_agents
        
        intervention_prompt = f"\n\n{'='*60}\n"
        intervention_prompt += "HUMAN INTERVENTION - CRITICAL UPDATE\n"
        intervention_prompt += f"{'='*60}\n\n"
        intervention_prompt += f"A human stakeholder has provided important feedback:\n\n"
        intervention_prompt += f'"{message}"\n\n'
        
        if is_tagged:
            intervention_prompt += f"IMPORTANT: YOU ({agent_name}) HAVE BEEN SPECIFICALLY TAGGED IN THIS INTERVENTION.\n"
            intervention_prompt += "You MUST address this feedback directly in your analysis.\n"
            intervention_prompt += "Consider how this changes your perspective and recommendations.\n\n"
        else:
            intervention_prompt += f"This feedback has been shared with all agents.\n"
            intervention_prompt += "Consider how it impacts your domain of expertise.\n\n"
        
        if tagged_agents:
            intervention_prompt += f"Agents tagged: {', '.join(tagged_agents)}\n\n"
        
        intervention_prompt += f"{'='*60}\n"
        
        return intervention_prompt
    
    def _save_agent_debate(self, post_input_id: int, analysis: Dict[str, Any]) -> int:
        """
        Save an agent's analysis to the database
        
        Args:
            post_input_id: ID of the post input
            analysis: Agent analysis dictionary
            
        Returns:
            int: Debate entry ID
        """
        # Extract common fields from analysis
        debate_data = {
            'post_input_id': post_input_id,
            'agent_name': analysis.get('agent_name', 'Unknown'),
            'agent_role': analysis.get('agent_role', 'Unknown'),
            'analysis': str(analysis),  # Store full JSON as string
            'score': analysis.get('score', 0),
            'recommendation': analysis.get('recommendation', ''),
            'vote': analysis.get('vote', 'unknown'),
            'reasoning': analysis.get('reasoning', ''),
            'concerns': analysis.get('concerns', ''),
            'debate_round': 1
        }
        
        return self.db.create_debate_entry(debate_data)
