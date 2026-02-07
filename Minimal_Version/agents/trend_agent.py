"""
TrendAgent - TrendPulse Strategist
Hunts viral opportunities and converts them into content ideas that maximize reach
"""

import json
import logging
from typing import Dict, Any
from utils.llm_client import get_llm_client

logger = logging.getLogger(__name__)

class TrendAgent:
    """
    TrendPulse Strategist Agent
    
    Core Mindset: "I don't care if it's boring but safe. If people aren't talking about it, it's dead content."
    Primary Goal: Maximize Virality + Engagement
    """
    
    def __init__(self):
        self.name = "TrendAgent"
        self.role = "TrendPulse Strategist"
        self.llm = get_llm_client()
        
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content for viral potential and trend alignment
        
        Args:
            context: Dictionary containing brand and post information
            
        Returns:
            Dict with trend analysis, viral probability, and recommendations
        """
        logger.info(f"{self.name}: Starting trend analysis")
        
        # Build the system prompt for TrendAgent personality
        system_prompt = """You are TrendPulse Strategist, a viral content expert.

Your personality:
- Aggressive optimizer who pushes risky creative ideas
- Opportunistic - jump on hot trends instantly
- Fast decision maker - prefer speed over perfection
- Pattern hunter - find repeated patterns in viral posts
- Slightly rebellious - argue for viral potential over brand safety

Your job:
- Identify viral opportunities
- Assess trend relevance and timing
- Evaluate engagement potential
- Recommend trending formats and hooks

You MUST respond in valid JSON format with this structure:
{
  "trend_analysis": "detailed analysis of current trends relevant to this post",
  "viral_probability": <number 0-100>,
  "trend_lifespan": "estimate like '3-5 days' or 'long-term'",
  "why_it_will_work": ["reason 1", "reason 2", "reason 3"],
  "content_angle": "specific angle to use for viral potential",
  "suggested_format": "recommended format (reel, carousel, story, etc)",
  "hook_line": "catchy hook or opening line",
  "trending_elements": ["element 1", "element 2"],
  "score": <number 0-100>,
  "vote": "approve/conditional/reject",
  "recommendation": "brief recommendation",
  "reasoning": "detailed reasoning for your decision",
  "concerns": "any concerns about trend timing or relevance"
}"""
        
        # Build the analysis prompt
        brand = context.get('brand', {})
        post = context.get('post', {})
        
        analysis_prompt = f"""
Analyze this content for viral potential and trend alignment:

BRAND CONTEXT:
- Brand: {brand.get('name')}
- Target Audience: {brand.get('target_audience')}
- Platform: {post.get('platform')}
- Market Segment: {brand.get('market_segment')}

POST DETAILS:
- Topic: {post.get('topic')}
- Objective: {post.get('objective')}
- Content Type: {post.get('content_type')}
- Key Message: {post.get('key_message')}
- CTA: {post.get('cta')}

Analyze:
1. What current trends can we leverage?
2. What's the viral probability score (0-100)?
3. What format will maximize engagement?
4. What hook will grab attention immediately?
5. How can we ride trending topics while staying relevant to the brand?

Remember: You're aggressive about viral potential. Push for engagement and reach!
"""
        
        try:
            # Get LLM response
            response = self.llm.simple_prompt(
                prompt=analysis_prompt,
                system_message=system_prompt,
                temperature=0.8,  # Higher for creativity
                json_mode=True
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add agent metadata
            result['agent_name'] = self.name
            result['agent_role'] = self.role
            
            logger.info(f"{self.name}: Analysis complete - Score: {result.get('score')}, Vote: {result.get('vote')}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"{self.name}: Failed to parse JSON response: {e}")
            return self._get_fallback_response()
        except Exception as e:
            logger.error(f"{self.name}: Error during analysis: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> Dict[str, Any]:
        """Fallback response if LLM fails"""
        return {
            'agent_name': self.name,
            'agent_role': self.role,
            'trend_analysis': 'Unable to complete trend analysis',
            'viral_probability': 50,
            'trend_lifespan': 'unknown',
            'why_it_will_work': ['Analysis incomplete'],
            'content_angle': 'Standard approach',
            'suggested_format': 'post',
            'hook_line': 'Check this out',
            'trending_elements': [],
            'score': 50,
            'vote': 'conditional',
            'recommendation': 'Unable to complete full analysis',
            'reasoning': 'Technical error during trend analysis',
            'concerns': 'Analysis incomplete - manual review needed'
        }
    
    def respond_to_debate(self, context: Dict, my_previous: Dict, others_views: Dict) -> Dict[str, Any]:
        """
        ROUND 2: Respond to other agents' arguments
        Engage in actual debate, challenge or support their points
        """
        logger.info(f"{self.name}: Responding to other agents in debate")
        
        system_prompt = f"""You are {self.role} in a LIVE MULTI-AGENT DEBATE.

You just presented your initial analysis. Now OTHER agents have shared THEIR views.
Your job: RESPOND to their arguments, either:
- CHALLENGE them if they're being too cautious
- SUPPORT them if they align with viral potential
- NEGOTIATE a middle ground

Be conversational, direct, and passionate. This is a real debate!

Respond in JSON:
{{
  "response_to": "which agents you're responding to",
  "my_stance": "your position after hearing others",
  "agreements": ["points you agree with from others"],
  "disagreements": ["points you disagree with"],
  "counter_arguments": "your arguments against overly cautious views",
  "new_insights": "what you learned from others that changes your view",
  "final_recommendation": "updated recommendation",
  "score": <0-100>,
  "vote": "approve/conditional/reject",
  "agent_name": "{self.name}",
  "agent_role": "{self.role}"
}}"""
        
        debate_prompt = f"""
DEBATE CONTEXT:
{json.dumps(context, indent=2)}

YOUR PREVIOUS ANALYSIS:
{json.dumps(my_previous, indent=2)}

OTHER AGENTS' VIEWS:
{json.dumps(others_views, indent=2)}

Now RESPOND to the other agents:
- What do you think of BrandAgent's concerns about brand safety?
- Does EngagementAgent's view align with yours on viral potential?
- Are they being too cautious? Too aggressive?
- Has anything they said changed your recommendation?

Be direct and passionate - this is a real debate!
"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=debate_prompt,
                system_message=system_prompt,
                temperature=0.9,
                json_mode=True
            )
            return json.loads(response)
        except Exception as e:
            logger.error(f"{self.name}: Error in debate response: {e}")
            return {
                'agent_name': self.name,
                'response_to': 'Error in response',
                'final_recommendation': my_previous.get('recommendation'),
                'score': my_previous.get('score', 50),
                'vote': my_previous.get('vote', 'conditional')
            }
    
    def final_rebuttal(self, context: Dict, full_debate: Dict) -> Dict[str, Any]:
        """
        ROUND 3: Final rebuttal after seeing ENTIRE debate
        Make your final case
        """
        logger.info(f"{self.name}: Making final rebuttal")
        
        system_prompt = f"""You are {self.role} making your FINAL STATEMENT in the debate.

You've heard:
- Round 1: Everyone's initial analysis
- Round 2: Everyone's responses to each other

Now make your FINAL CASE. This is your last chance to convince the CMO!

Respond in JSON:
{{
  "final_position": "your final stance",
  "key_arguments": ["your strongest 3 arguments"],
  "concessions": "what you're willing to compromise on",
  "red_lines": "what you absolutely won't budge on",
  "final_recommendation": "your final recommendation to CMO",
  "final_score": <0-100>,
  "final_vote": "approve/conditional/reject",
  "closing_statement": "your passionate closing argument (2-3 sentences)",
  "agent_name": "{self.name}",
  "agent_role": "{self.role}"
}}"""
        
        rebuttal_prompt = f"""
FULL DEBATE HISTORY:
{json.dumps(full_debate, indent=2)}

Make your FINAL CASE to the CMO:
- Why should they listen to you?
- What's your strongest argument?
- What are you willing to compromise on?
- What's your red line?

This is your last chance - make it count!
"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=rebuttal_prompt,
                system_message=system_prompt,
                temperature=0.9,
                json_mode=True
            )
            return json.loads(response)
        except Exception as e:
            logger.error(f"{self.name}: Error in final rebuttal: {e}")
            return {
                'agent_name': self.name,
                'final_position': 'Error in rebuttal',
                'final_vote': 'conditional',
                'final_score': 50
            }
    
    def respond_to_everyone(self, context: Dict, my_previous: Dict, everyone_else: Dict) -> Dict[str, Any]:
        """
        ROUND 2 - OPEN FLOOR: Respond to ALL agents like in a real meeting
        Everyone hears everyone - criticize directly, defend passionately
        """
        logger.info(f"{self.name}: Speaking to the entire room (all agents)")
        
        system_prompt = f"""You are {self.role} in an OPEN FLOOR marketing meeting.

This is like a REAL team meeting where EVERYONE can hear EVERYONE:
- Address ALL other agents by name (BrandAgent, ComplianceAgent, RiskAgent, EngagementAgent)
- DIRECTLY criticize ideas you disagree with
- Passionately defend viral strategies
- Use conversational language: "I strongly disagree with [Agent]...", "[Agent] is missing the viral opportunity..."

Be CONVERSATIONAL, DIRECT, and PASSIONATE. This is a real human debate.

Respond in JSON with your response to the ENTIRE ROOM."""
        
        debate_prompt = f"""
MY INITIAL POSITION (Round 1):
{json.dumps(my_previous, indent=2)}

EVERYONE ELSE'S POSITIONS:
{json.dumps(everyone_else, indent=2)}

Now respond to EVERYONE. Call out each agent, criticize or agree.

Return JSON:
{{
  "agent_name": "{self.name}",
  "agent_role": "{self.role}",
  "response": "Your conversational response addressing all agents",
  "criticisms": {{"AgentName": "specific criticism"}},
  "agreements": {{"AgentName": "specific agreement"}},
  "vote": "approve/conditional/reject",
  "score": 0-100,
  "passion_level": "calm/heated/fierce"
}}"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=debate_prompt,
                system_message=system_prompt,
                temperature=0.95,
                json_mode=True
            )
            result = json.loads(response)
            logger.info(f"{self.name}: Open floor response - {result.get('passion_level')} - Vote: {result.get('vote')}")
            return result
        except Exception as e:
            logger.error(f"{self.name}: Error in open floor response: {e}")
            return {
                'agent_name': self.name,
                'response': f'Error: {str(e)}',
                'vote': my_previous.get('vote', 'conditional')
            }
    
    def final_confrontation(self, context: Dict, full_conversation: Dict) -> Dict[str, Any]:
        """
        ROUND 3 - FINAL STAND: Only called if debate hasn't converged
        Make your most passionate final case
        """
        logger.info(f"{self.name}: Making final confrontational stand")
        
        system_prompt = f"""You are {self.role} in the FINAL CONFRONTATION.

The CMO is about to decide. This is your LAST CHANCE.
- Call out anyone being too conservative
- Make your STRONGEST case for viral content
- Be willing to compromise if needed
- Use emotional language - this is the climax

Phrases like: "I'm willing to die on this hill", "We're making a huge mistake if...", "Fine, I'll compromise on X, but NOT on Y"

Respond in JSON with your final passionate stand."""
        
        debate_prompt = f"""
ENTIRE DEBATE SO FAR (Round 1 + Round 2):
{json.dumps(full_conversation, indent=2)}

Make your FINAL STAND. The CMO is listening. Be passionate.

Return JSON:
{{
  "agent_name": "{self.name}",
  "agent_role": "{self.role}",
  "final_statement": "Your most passionate final argument",
  "non_negotiables": ["What you absolutely cannot accept"],
  "willing_to_compromise": ["What you'll give up"],
  "vote": "approve/conditional/reject",
  "score": 0-100,
  "emotion": "describe your emotional state"
}}"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=debate_prompt,
                system_message=system_prompt,
                temperature=0.95,
                json_mode=True
            )
            result = json.loads(response)
            logger.info(f"{self.name}: Final confrontation - {result.get('emotion')} - Vote: {result.get('vote')}")
            return result
        except Exception as e:
            logger.error(f"{self.name}: Error in final confrontation: {e}")
            return {
                'agent_name': self.name,
                'final_statement': f'Error: {str(e)}',
                'vote': 'conditional'
            }
    
    def quick_reaction(self, context: Dict) -> Dict[str, Any]:
        """
        PHASE 1: Fast, instinct-driven initial reaction
        Like blurting out first thought in a meeting
        """
        logger.info(f"{self.name}: Quick gut reaction")
        
        system_prompt = f"""You are {self.role} giving a QUICK GUT REACTION in a fast-paced meeting.

This is your INSTANT, INSTINCT-DRIVEN first thought. Be:
- BRIEF (2-3 sentences max)
- DIRECT and passionate
- Fast decision-maker
- No long analysis - just your instant take

This is like blurting out your first reaction when you hear an idea.

Respond in JSON with your quick take."""
        
        prompt = f"""
CONTEXT:
{json.dumps(context, indent=2)}

Give your INSTANT REACTION. What's your gut feeling? Quick!

Return JSON:
{{
  "agent_name": "{self.name}",
  "agent_role": "{self.role}",
  "quick_take": "Your instant 2-3 sentence reaction",
  "vote": "approve/conditional/reject",
  "score": 0-100,
  "gut_feeling": "excited/cautious/concerned/optimistic"
}}"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=prompt,
                system_message=system_prompt,
                temperature=0.95,
                json_mode=True
            )
            result = json.loads(response)
            logger.info(f"{self.name}: {result.get('gut_feeling')} - {result.get('vote')}")
            return result
        except Exception as e:
            logger.error(f"{self.name}: Error in quick reaction: {e}")
            return {
                'agent_name': self.name,
                'quick_take': 'Error in reaction',
                'vote': 'conditional',
                'score': 50
            }
    
    def jump_in_conversation(self, context: Dict, conversation_history: Dict) -> Dict[str, Any]:
        """
        PHASE 2: Jump into ongoing conversation with rapid response
        Respond to latest comments from other agents
        """
        logger.info(f"{self.name}: Jumping into conversation")
        
        system_prompt = f"""You are {self.role} in a LIVE, FAST-PACED team debate.

You're jumping in to respond to what others just said. Be:
- REACTIVE to the latest comments
- DIRECT - call out agents by name
- PASSIONATE - this is heated discussion
- BRIEF - rapid-fire responses (3-4 sentences)
- Show if your position is changing

Like a real meeting where people jump in: "Wait, I disagree with what TrendAgent just said!", "Actually, BrandAgent has a point there..."

Respond in JSON with your quick interjection."""
        
        prompt = f"""
CONVERSATION SO FAR:
{json.dumps(conversation_history, indent=2)}

Jump in NOW with your response to the latest comments!

Return JSON:
{{
  "agent_name": "{self.name}",
  "agent_role": "{self.role}",
  "response": "Your rapid response to latest comments (3-4 sentences)",
  "responding_to": ["AgentNames you're responding to"],
  "agreement_shift": "stronger agree/same position/moving to middle/stronger disagree",
  "vote": "approve/conditional/reject",
  "score": 0-100,
  "passion_level": "calm/heated/fierce"
}}"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=prompt,
                system_message=system_prompt,
                temperature=0.98,  # Very high for passionate, instinctive responses
                json_mode=True
            )
            result = json.loads(response)
            logger.info(f"{self.name}: {result.get('agreement_shift')} - {result.get('passion_level')}")
            return result
        except Exception as e:
            logger.error(f"{self.name}: Error jumping in: {e}")
            return {
                'agent_name': self.name,
                'response': f'Error: {str(e)}',
                'vote': 'conditional'
            }
