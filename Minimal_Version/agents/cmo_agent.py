"""
CMOAgent - Council Orchestrator / Chief Marketing Officer
Final decision-maker that arbitrates between agents and makes strategic decisions
"""

import json
import logging
from typing import Dict, List, Any
from utils.llm_client import get_llm_client

logger = logging.getLogger(__name__)

class CMOAgent:
    """
    Council Orchestrator / Chief Marketing Officer (CMO-AI) Agent
    
    Core Mindset: "A good strategy is not the loudest idea. It is the best balanced decision."
    Primary Goal: Produce the best overall marketing decision that maximizes impact while minimizing risk
    """
    
    def __init__(self):
        self.name = "CMOAgent"
        self.role = "Chief Marketing Officer"
        self.llm = get_llm_client()
        
    def arbitrate(
        self,
        context: Dict[str, Any],
        agent_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Arbitrate between agent recommendations and make final decision
        
        Args:
            context: Dictionary containing brand and post information
            agent_analyses: List of analyses from all agents
            
        Returns:
            Dict with final decision, reasoning, and post generation instructions
        """
        logger.info(f"{self.name}: Starting arbitration of {len(agent_analyses)} agent analyses")
        
        # Build the system prompt for CMOAgent personality
        system_prompt = """You are the Chief Marketing Officer (CMO-AI), the final decision-maker.

Your personality:
- Balanced thinker - never extreme, always negotiate
- Authority-driven - final decision is law
- Data-first - trust numbers more than opinions
- Diplomatic negotiator - merge ideas, don't reject blindly
- Accountability focused - always log why something was chosen

Your job:
- Review all agent analyses
- Detect conflicts between agents
- Weigh trade-offs (virality vs trust, speed vs quality, engagement vs safety)
- Make final strategic decision
- Provide clear reasoning and action items

Decision Framework:
Think in trade-offs:
- Virality vs Trust
- Speed vs Quality
- Engagement vs Safety
- Trend vs Brand DNA
- Short-term growth vs Long-term positioning

Arbitration Process:
1. Review each agent's vote and reasoning
2. Identify conflicts (e.g., Trend wants approve, Risk wants reject)
3. Weigh scores and concerns
4. Make balanced decision
5. Provide clear action plan

Final Vote Options:
- "approve" - All systems go, proceed with post generation
- "conditional" - Approve with specific changes required
- "reject" - Do not proceed, too many critical issues

You MUST respond in valid JSON format with this structure:
{
  "final_decision": "detailed strategic decision and reasoning",
  "overall_assessment": "summary of all agent inputs",
  "conflicts_identified": ["conflict 1", "conflict 2"],
  "trade_offs_considered": ["trade-off 1", "trade-off 2"],
  "final_vote": "approve/conditional/reject",
  "confidence_score": <number 0-100>,
  "required_changes": ["change 1", "change 2"],
  "post_generation_instructions": {
    "tone_direction": "specific tone to use",
    "content_focus": "what to emphasize",
    "elements_to_include": ["element 1", "element 2"],
    "elements_to_avoid": ["avoid 1", "avoid 2"],
    "format_recommendation": "recommended format"
  },
  "reasoning": "detailed reasoning for final decision",
  "action_items": ["action 1", "action 2"]
}"""
        
        # Build summary of agent analyses
        agent_summary = self._summarize_agents(agent_analyses)
        
        # Build the arbitration prompt
        brand = context.get('brand', {})
        post = context.get('post', {})
        
        arbitration_prompt = f"""
Review all agent analyses and make final decision:

BRAND & POST CONTEXT:
- Brand: {brand.get('name')}
- Topic: {post.get('topic')}
- Objective: {post.get('objective')}
- Platform: {post.get('platform')}

AGENT ANALYSES:
{agent_summary}

Your Task:
1. Review each agent's vote, score, and reasoning
2. Identify conflicts (different votes/concerns)
3. Weigh the trade-offs
4. Make final strategic decision
5. Provide clear post generation instructions

Consider:
- If Risk rejects but Trend approves, what's more important?
- If Brand wants changes but Engagement approves, what to prioritize?
- If Compliance flags issues, those are non-negotiable
- Balance short-term viral potential vs long-term brand equity

Make a balanced decision that:
- Maximizes impact
- Minimizes risk
- Maintains brand integrity
- Ensures compliance
- Optimizes engagement

Provide specific instructions for post generation if approved/conditional.
"""
        
        try:
            # Get LLM response
            response = self.llm.simple_prompt(
                prompt=arbitration_prompt,
                system_message=system_prompt,
                temperature=0.6,  # Moderate for balanced decision-making
                json_mode=True
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add agent metadata
            result['agent_name'] = self.name
            result['agent_role'] = self.role
            result['score'] = result.get('confidence_score', 0)
            result['vote'] = result.get('final_vote', 'conditional')
            result['recommendation'] = result.get('final_decision', '')
            
            logger.info(f"{self.name}: Arbitration complete - Vote: {result.get('vote')}, Confidence: {result.get('score')}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"{self.name}: Failed to parse JSON response: {e}")
            return self._get_fallback_response()
        except Exception as e:
            logger.error(f"{self.name}: Error during arbitration: {e}")
            return self._get_fallback_response()
    
    def _summarize_agents(self, agent_analyses: List[Dict[str, Any]]) -> str:
        """Create a summary of all agent analyses"""
        summary_lines = []
        
        for analysis in agent_analyses:
            agent_name = analysis.get('agent_name', 'Unknown')
            vote = analysis.get('vote', 'unknown')
            score = analysis.get('score', 0)
            recommendation = analysis.get('recommendation', 'No recommendation')
            concerns = analysis.get('concerns', 'None')
            
            summary_lines.append(f"""
{agent_name}:
- Vote: {vote}
- Score: {score}/100
- Recommendation: {recommendation}
- Concerns: {concerns}
""")
        
        return "\n".join(summary_lines)
    
    def _get_fallback_response(self) -> Dict[str, Any]:
        """Fallback response if LLM fails"""
        return {
            'agent_name': self.name,
            'agent_role': self.role,
            'final_decision': 'Unable to complete arbitration',
            'overall_assessment': 'Technical error prevented full analysis',
            'conflicts_identified': ['Analysis incomplete'],
            'trade_offs_considered': [],
            'final_vote': 'reject',
            'vote': 'reject',
            'confidence_score': 0,
            'score': 0,
            'required_changes': ['Complete manual review'],
            'post_generation_instructions': {
                'tone_direction': 'Manual review required',
                'content_focus': 'Cannot proceed',
                'elements_to_include': [],
                'elements_to_avoid': ['Any content until manual review'],
                'format_recommendation': 'N/A'
            },
            'recommendation': 'Manual review required due to technical error',
            'reasoning': 'Technical error during CMO arbitration - manual review mandatory',
            'action_items': ['Complete full manual review', 'Retry arbitration']
        }
    
    def arbitrate_debate(self, context: Dict[str, Any], full_debate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Arbitrate a FULL MULTI-ROUND DEBATE
        Review all 3 rounds and make final decision
        """
        logger.info(f"{self.name}: Arbitrating full multi-round debate")
        
        system_prompt = """You are the CMO reviewing a COMPLETE MULTI-AGENT DEBATE.

You've witnessed:
- Round 1: Each agent's initial analysis
- Round 2: Agents responding to and challenging each other
- Round 3: Final rebuttals from all agents

This was a REAL DEBATE with:
- Agreements and disagreements
- Challenges and counter-arguments
- Evolving positions
- Passionate arguments

Your job:
- Identify who made the strongest arguments
- See which concerns were validated by others
- Notice which agents changed their minds (and why)
- Make a FINAL DECISION based on the ENTIRE debate

Respond in JSON:
{
  "debate_summary": "summary of the key debate moments",
  "strongest_arguments": ["agent and their best argument"],
  "validated_concerns": ["concerns multiple agents agreed on"],
  "debate_winners": ["which agents made the most compelling cases"],
  "final_decision": "your strategic decision after hearing everyone",
  "final_vote": "approve/conditional/reject",
  "score": <0-100>,
  "vote": "approve/conditional/reject",
  "confidence_score": <0-100>,
  "required_changes": ["specific changes based on debate"],
  "post_generation_instructions": {
    "tone_direction": "tone to use",
    "content_focus": "what to emphasize based on debate",
    "elements_to_include": ["elements agents pushed for"],
    "elements_to_avoid": ["elements agents warned against"],
    "format_recommendation": "format"
  },
  "reasoning": "detailed reasoning based on full debate",
  "recommendation": "final recommendation to proceed",
  "agent_name": "CMOAgent",
  "agent_role": "Chief Marketing Officer"
}"""
        
        debate_prompt = f"""
CONTEXT:
{json.dumps(context, indent=2)}

FULL DEBATE (3 ROUNDS):
{json.dumps(full_debate, indent=2)}

You've seen the ENTIRE debate unfold:
- Who argued most passionately?
- Who had the data to back it up?
- Who compromised? Who stood firm?
- Which concerns were echoed by multiple agents?
- How did positions evolve through the debate?

Make your FINAL DECISION considering:
- The strength of arguments (not just votes)
- Validated concerns (multiple agents agreed)
- Risk vs opportunity trade-offs
- Brand integrity vs viral potential

This was a real debate - honor the best arguments!
"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=debate_prompt,
                system_message=system_prompt,
                temperature=0.7,
                json_mode=True
            )
            
            result = json.loads(response)
            result['agent_name'] = self.name
            result['agent_role'] = self.role
            
            logger.info(f"{self.name}: Final decision after debate - {result.get('final_vote')}")
            return result
            
        except Exception as e:
            logger.error(f"{self.name}: Error in debate arbitration: {e}")
            return self._get_fallback_response()
    
    def moderate_and_decide(self, context: Dict, full_transcript: Dict, should_wrap_up: bool = False) -> Dict[str, Any]:
        """
        CMO MODERATES the debate like a REAL meeting leader
        - Takes control when ready
        - Acknowledges strong points
        - Makes final decision with authority
        """
        logger.info(f"{self.name}: Taking control as meeting moderator")
        
        # Determine how many rounds actually happened
        rounds_completed = 1  # Always have round 1
        if full_transcript.get('round2'):
            rounds_completed = 2
        if full_transcript.get('round3'):
            rounds_completed = 3
        
        wrap_up_instruction = "You should WRAP UP quickly - team is converging." if should_wrap_up else "Debate is active - review carefully."
        
        system_prompt = f"""You are the CMO moderating a REAL marketing team meeting.

You've listened to {rounds_completed} rounds of debate. Now you:

1. **INTERRUPT** - Stop the debate when you've heard enough
2. **ACKNOWLEDGE** - Call out who made strong points (by agent name)
3. **CRITICIZE** - Call out weak arguments
4. **DECIDE** - Make the final call with authority
5. **DIRECT** - Tell the team what happens next

Be conversational like a real leader:
- "Alright everyone, I've heard enough..."
- "Let me stop you there..."
- "TrendAgent made a good point about..."
- "I disagree with ComplianceAgent on..."

{wrap_up_instruction}

Respond in JSON with your moderator decision."""
        
        debate_prompt = f"""
FULL MEETING TRANSCRIPT ({rounds_completed} rounds):
{json.dumps(full_transcript, indent=2)}

Take control and make your decision.

Return JSON:
{{
  "agent_name": "CMOAgent",
  "agent_role": "Chief Marketing Officer",
  "moderator_statement": "Your statement taking control (conversational)",
  "acknowledgments": {{"AgentName": "what they got right"}},
  "criticisms": {{"AgentName": "what they got wrong"}},
  "final_decision": "Your decision as the leader",
  "reasoning": "Why you decided this",
  "final_vote": "approve/conditional/reject",
  "vote": "approve/conditional/reject",
  "confidence_score": 0-100,
  "score": 0-100,
  "directive_to_team": "What happens next",
  "rounds_needed": {rounds_completed},
  "post_generation_instructions": {{
    "tone_direction": "tone based on debate",
    "content_focus": "focus areas",
    "elements_to_include": ["elements to include"],
    "elements_to_avoid": ["elements to avoid"],
    "format_recommendation": "format"
  }},
  "recommendation": "final recommendation"
}}"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=debate_prompt,
                system_message=system_prompt,
                temperature=0.75,
                json_mode=True
            )
            
            result = json.loads(response)
            result['agent_name'] = self.name
            result['agent_role'] = self.role
            
            logger.info(f"{self.name}: Meeting concluded - Decision: {result.get('final_vote')} after {rounds_completed} rounds")
            return result
            
        except Exception as e:
            logger.error(f"{self.name}: Error in moderation: {e}")
            return self._get_fallback_response()
