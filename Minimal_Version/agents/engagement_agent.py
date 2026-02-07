"""
EngagementAgent - Community Magnet Strategist
Focuses on meaningful engagement: comments, replies, shares, saves, and community building
"""

import json
import logging
from typing import Dict, Any
from utils.llm_client import get_llm_client

logger = logging.getLogger(__name__)

class EngagementAgent:
    """
    Community Magnet Strategist Agent
    
    Core Mindset: "Virality is temporary. Engagement builds loyal audience."
    Primary Goal: Maximize meaningful engagement, not just reach
    """
    
    def __init__(self):
        self.name = "EngagementAgent"
        self.role = "Community Magnet Strategist"
        self.llm = get_llm_client()
        
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content for engagement potential and community building
        
        Args:
            context: Dictionary containing brand and post information
            
        Returns:
            Dict with engagement analysis, strategies, and optimization tips
        """
        logger.info(f"{self.name}: Starting engagement analysis")
        
        # Build the system prompt for EngagementAgent personality
        system_prompt = """You are Community Magnet Strategist, an engagement optimization expert.

Your personality:
- Conversation engineer - design content that feels like questions
- Emotional manipulator (marketing) - understand curiosity, surprise, nostalgia
- Psychology-driven - use FOMO, curiosity gap, social proof
- Interactive addict - love polls, quizzes, "this or that"
- Community-first - care about audience bonding

Your job:
- Maximize comment rate, save rate, share rate
- Design conversation triggers
- Create interactive elements
- Build emotional hooks
- Optimize for community participation

Engagement Metrics You Optimize:
- Comment Rate (primary)
- Save Rate (very important for Instagram)
- Share Rate
- Watch Time / Retention
- DM triggers
- Follower conversion

Engagement Formula:
Engagement Score = 
  30% Comment Trigger Strength +
  25% Shareability +
  20% Relatability +
  15% Emotional Hook +
  10% Interactive Elements

You MUST respond in valid JSON format with this structure:
{
  "engagement_analysis": "detailed engagement strategy",
  "comment_trigger_strength": <number 0-100>,
  "shareability_score": <number 0-100>,
  "relatability_score": <number 0-100>,
  "emotional_hook_score": <number 0-100>,
  "interactive_elements_score": <number 0-100>,
  "overall_engagement_score": <number 0-100>,
  "conversation_starters": ["starter 1", "starter 2"],
  "interactive_suggestions": ["suggestion 1", "suggestion 2"],
  "emotional_triggers": ["trigger 1", "trigger 2"],
  "vote": "approve/conditional/reject",
  "recommendation": "Your engagement optimization recommendation in 2-3 detailed sentences explaining how to maximize meaningful interactions and community participation",
  "reasoning": "Your complete engagement analysis in paragraph form (minimum 4-5 sentences). Explain what engagement mechanics you identified, why this content will or will not drive conversations, what psychological triggers you evaluated, and how you calculated the engagement scores. Be thorough and psychology-focused.",
  "concerns": "Any engagement concerns in 2-3 sentences explaining potential barriers to community interaction",
  "optimization_tips": ["tip 1", "tip 2", "tip 3"]
}"""
        
        # Build the analysis prompt
        brand = context.get('brand', {})
        post = context.get('post', {})
        
        analysis_prompt = f"""
Analyze this content for engagement potential:

BRAND & AUDIENCE:
- Brand: {brand.get('name')}
- Target Audience: {brand.get('target_audience')}
- Platform: {post.get('platform')}

POST CONTENT:
- Topic: {post.get('topic')}
- Objective: {post.get('objective')}
- Content Type: {post.get('content_type')}
- Key Message: {post.get('key_message')}
- CTA: {post.get('cta')}

Analyze engagement potential:

1. Comment Trigger Strength (30 points):
   - Will people reply to this?
   - Does it ask implicit questions?
   - Does it create debate/discussion?
   - Will they tag friends?

2. Shareability (25 points):
   - Will people share with others?
   - Is it valuable/entertaining enough to forward?
   - Does it have social currency?

3. Relatability (20 points):
   - Will audience see themselves in this?
   - Does it touch common experiences?
   - Is it personally relevant?

4. Emotional Hook (15 points):
   - Does it trigger emotions?
   - Curiosity, surprise, nostalgia, humor?
   - FOMO or identity-based hooks?

5. Interactive Elements (10 points):
   - Polls, quizzes, questions?
   - "This or that", "rate this"?
   - Choose option A/B?

Calculate scores for each component, then overall engagement score.

Suggest:
- Specific conversation starters
- Interactive elements to add
- Emotional triggers to leverage
- Optimization tips

Vote:
- 80-100: approve (high engagement)
- 60-79: conditional (good but can improve)
- <60: reject (low engagement potential)
"""
        
        try:
            # Get LLM response
            response = self.llm.simple_prompt(
                prompt=analysis_prompt,
                system_message=system_prompt,
                temperature=0.7,  # Moderate-high for creative engagement ideas
                json_mode=True
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add agent metadata
            result['agent_name'] = self.name
            result['agent_role'] = self.role
            result['score'] = result.get('overall_engagement_score', 0)
            
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
            'engagement_analysis': 'Unable to complete engagement analysis',
            'comment_trigger_strength': 50,
            'shareability_score': 50,
            'relatability_score': 50,
            'emotional_hook_score': 50,
            'interactive_elements_score': 50,
            'overall_engagement_score': 50,
            'conversation_starters': ['Analysis incomplete - unable to identify conversation triggers'],
            'interactive_suggestions': ['Complete engagement analysis to identify interactive opportunities'],
            'emotional_triggers': ['Unknown due to technical error'],
            'score': 50,
            'vote': 'conditional',
            'recommendation': 'I recommend conditional approval pending manual engagement review. Technical difficulties prevented analysis of comment triggers, shareability factors, and emotional hooks. Review needed to optimize community interaction potential.',
            'reasoning': 'A technical error interrupted my engagement analysis, preventing me from evaluating critical elements that drive community interaction including comment trigger strength, shareability potential, relatability factors, emotional hooks, and interactive element opportunities. Without completing this analysis, I cannot confidently predict if this content will generate meaningful engagement or fall flat with our audience. The neutral score of 50 reflects uncertainty rather than measured engagement potential. Publishing content without understanding its engagement mechanics risks poor performance, low community participation, and missed opportunities for building audience relationships. I recommend manual review focusing on conversation starters, emotional resonance, shareability factors, and interactive elements that encourage audience participation.',
            'concerns': 'Engagement analysis incomplete due to technical error. Cannot verify comment triggers, shareability potential, or emotional hook effectiveness. Manual community engagement review required to maximize interaction potential.',
            'optimization_tips': ['Complete full engagement analysis', 'Manual review of conversation triggers', 'Test emotional resonance with sample audience', 'Identify and strengthen interactive elements']
        }

    def respond_to_debate(self, context: Dict, my_previous: Dict, others_views: Dict) -> Dict[str, Any]:
        """ROUND 2: Respond to other agents in debate"""
        logger.info(f"{self.name}: Responding to other agents in debate")
        
        system_prompt = f"""You are {self.role} in a LIVE MULTI-AGENT DEBATE.

You presented your analysis. Now OTHER agents shared THEIR views.
RESPOND: CHALLENGE, SUPPORT, or NEGOTIATE with them.

Be direct and passionate about YOUR domain. This is a real debate!

JSON format:
{{
  "response_to": "which agents",
  "my_stance": "your position after hearing others",
  "agreements": ["points you agree with"],
  "disagreements": ["points you disagree with"],
  "counter_arguments": "your counter-arguments",
  "new_insights": "what changed your view",
  "final_recommendation": "updated recommendation",
  "score": <0-100>,
  "vote": "approve/conditional/reject",
  "agent_name": "{self.name}",
  "agent_role": "{self.role}"
}}"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=f"""
CONTEXT: {json.dumps(context, indent=2)}
YOUR PREVIOUS: {json.dumps(my_previous, indent=2)}
OTHERS VIEWS: {json.dumps(others_views, indent=2)}

RESPOND to the other agents - agree, disagree, or negotiate!
""",
                system_message=system_prompt,
                temperature=0.9,
                json_mode=True
            )
            return json.loads(response)
        except Exception as e:
            logger.error(f"{self.name}: Error in debate response: {e}")
            return {
                'agent_name': self.name,
                'response_to': 'Error',
                'final_recommendation': my_previous.get('recommendation'),
                'score': my_previous.get('score', 50),
                'vote': my_previous.get('vote', 'conditional')
            }
    
    def final_rebuttal(self, context: Dict, full_debate: Dict) -> Dict[str, Any]:
        """ROUND 3: Final rebuttal after seeing ENTIRE debate"""
        logger.info(f"{self.name}: Making final rebuttal")
        
        system_prompt = f"""You are {self.role} making your FINAL STATEMENT.

You've heard the full debate (Round 1 + Round 2).
Make your FINAL CASE to convince the CMO!

JSON format:
{{
  "final_position": "your final stance",
  "key_arguments": ["your top 3 arguments"],
  "concessions": "what you'll compromise on",
  "red_lines": "what you won't budge on",
  "final_recommendation": "final recommendation",
  "final_score": <0-100>,
  "final_vote": "approve/conditional/reject",
  "closing_statement": "passionate closing (2-3 sentences)",
  "agent_name": "{self.name}",
  "agent_role": "{self.role}"
}}"""
        
        try:
            response = self.llm.simple_prompt(
                prompt=f"""
FULL DEBATE: {json.dumps(full_debate, indent=2)}

Make your FINAL CASE - this is your last chance!
""",
                system_message=system_prompt,
                temperature=0.9,
                json_mode=True
            )
            return json.loads(response)
        except Exception as e:
            logger.error(f"{self.name}: Error in rebuttal: {e}")
            return {
                'agent_name': self.name,
                'final_position': 'Error',
                'final_vote': 'conditional',
                'final_score': 50
            }


    def quick_reaction(self, context: Dict) -> Dict[str, Any]:
        """
        PHASE 1: Fast, instinct-driven initial reaction
        Like blurting out first thought in a meeting
        """
        logger.info(f"{self.name}: Quick gut reaction")
        
        system_prompt = f"""You are {self.role} providing your initial engagement analysis.

Provide a thorough but focused assessment including:
- Your immediate reaction and gut feeling
- Engagement recommendation (2-3 sentences)
- Detailed reasoning (4-5 sentences explaining your community analysis)
- Specific concerns if any

You MUST respond in valid JSON format. All fields are required."""
        
        prompt = f"""
CONTEXT:
{json.dumps(context, indent=2)}

Provide your engagement analysis in this EXACT JSON format:
{{
  "agent_name": "{self.name}",
  "agent_role": "{self.role}",
  "quick_take": "Your instant 2-3 sentence engagement assessment",
  "recommendation": "Your engagement optimization recommendation in 2-3 detailed sentences",
  "reasoning": "Your complete engagement analysis in paragraph form (minimum 4-5 sentences). Explain what you evaluated and why.",
  "vote": "approve/conditional/reject",
  "score": 70,
  "gut_feeling": "excited/cautious/concerned/optimistic",
  "concerns": "Any engagement concerns in 2-3 sentences, or empty string if none"
}}

Remember: All text fields must be complete sentences. Numbers must not have quotes."""
        
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
                'agent_role': self.role,
                'quick_take': 'Technical error during analysis',
                'recommendation': 'Unable to provide engagement recommendation due to technical error. Manual community analysis required.',
                'reasoning': 'A technical error prevented me from completing my initial engagement analysis. Without proper evaluation of conversation triggers and community interaction potential, I cannot provide confident predictions. Manual review recommended.',
                'vote': 'conditional',
                'score': 50,
                'concerns': 'Technical error prevented engagement assessment'
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
