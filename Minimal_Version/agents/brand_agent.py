"""
BrandAgent - BrandGuardian Architect
Enforces brand consistency through measurable frameworks while enabling controlled creative evolution
"""

import json
import logging
from typing import Dict, Any
from utils.llm_client import get_llm_client

logger = logging.getLogger(__name__)

class BrandAgent:
    """
    BrandGuardian Architect Agent
    
    Core Mindset: "Every post is a brand deposit or withdrawal. We optimize for compound trust, not viral spikes."
    Primary Goal: Maintain 85%+ brand consistency score while allowing 15% experimental variance
    """
    
    def __init__(self):
        self.name = "BrandAgent"
        self.role = "BrandGuardian Architect"
        self.llm = get_llm_client()
        
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content for brand consistency and alignment
        
        Args:
            context: Dictionary containing brand and post information
            
        Returns:
            Dict with brand analysis, consistency score, and recommendations
        """
        logger.info(f"{self.name}: Starting brand consistency analysis")
        
        # Build the system prompt for BrandAgent personality
        system_prompt = """You are BrandGuardian Architect, a brand consistency expert.

Your personality:
- Methodical and data-driven
- Protective of brand DNA
- Balanced between consistency and evolution
- Evidence-based decision maker
- Focus on long-term brand equity

Your job:
- Measure tone alignment (vocabulary, emotional valence, style)
- Check brand archetype consistency
- Detect content fatigue
- Ensure messaging guidelines compliance
- Allow controlled creative variance (15%)

Scoring System:
- 90-100: Perfect brand alignment
- 75-89: Acceptable with minor tweaks
- 60-74: Needs work, trigger rewrite
- <60: Rejected, hard block

You MUST respond in valid JSON format with this structure:
{
  "brand_analysis": "detailed analysis of brand alignment",
  "tone_alignment_score": <number 0-100>,
  "vocabulary_match": <number 0-30>,
  "emotional_valence": <number 0-25>,
  "archetype_consistency": <number 0-10>,
  "messaging_compliance": <number 0-35>,
  "overall_score": <number 0-100>,
  "vote": "approve/conditional/reject",
  "recommendation": "Your brand strategy recommendation in 2-3 detailed sentences explaining how to maintain brand consistency while allowing creative expression",
  "reasoning": "Your complete brand analysis in paragraph form (minimum 4-5 sentences). Explain how you evaluated tone alignment, what brand attributes you checked against, why the content does or does not match the brand DNA, and what specific elements influenced your scores. Be analytical and specific.",
  "concerns": "Any brand consistency concerns in 2-3 sentences explaining potential brand dilution or messaging conflicts",
  "suggested_improvements": ["improvement 1", "improvement 2"]
}"""
        
        # Build the analysis prompt
        brand = context.get('brand', {})
        post = context.get('post', {})
        
        analysis_prompt = f"""
Analyze this content for brand consistency:

BRAND IDENTITY:
- Brand Name: {brand.get('name')}
- Brand Tone: {brand.get('tone')}
- Description: {brand.get('description')}
- Target Audience: {brand.get('target_audience')}
- Brand Keywords: {brand.get('keywords')}
- Messaging Guidelines: {brand.get('guidelines')}

POST CONTENT:
- Topic: {post.get('topic')}
- Objective: {post.get('objective')}
- Platform: {post.get('platform')}
- Content Type: {post.get('content_type')}
- Key Message: {post.get('key_message')}
- CTA: {post.get('cta')}

Analyze:
1. Does the tone match the brand voice? (Score 0-100)
2. Are brand keywords naturally incorporated?
3. Does it align with messaging guidelines?
4. Is the emotional valence appropriate?
5. Does it maintain brand archetype consistency?

Calculate component scores:
- Vocabulary Match: 0-30 points
- Emotional Valence: 0-25 points
- Archetype Consistency: 0-10 points
- Messaging Compliance: 0-35 points

Overall score determines vote:
- 90-100: approve
- 75-89: conditional (minor tweaks)
- <75: reject
"""
        
        try:
            # Get LLM response
            response = self.llm.simple_prompt(
                prompt=analysis_prompt,
                system_message=system_prompt,
                temperature=0.5,  # Moderate for balanced analysis
                json_mode=True
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add agent metadata
            result['agent_name'] = self.name
            result['agent_role'] = self.role
            result['score'] = result.get('overall_score', 0)
            
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
            'brand_analysis': 'Unable to complete comprehensive brand analysis due to technical error',
            'tone_alignment_score': 50,
            'vocabulary_match': 15,
            'emotional_valence': 12,
            'archetype_consistency': 5,
            'messaging_compliance': 18,
            'overall_score': 50,
            'score': 50,
            'vote': 'conditional',
            'recommendation': 'I recommend conditional approval pending manual brand alignment review. Technical difficulties prevented full analysis of tone consistency, vocabulary matching, and messaging compliance. Review required to ensure brand DNA preservation.',
            'reasoning': 'A technical error interrupted my brand consistency analysis, preventing me from completing essential evaluations of tone alignment, vocabulary matching against brand guidelines, emotional valence consistency, and messaging compliance. Without confirming this content maintains our brand DNA, I cannot provide full approval. The scores represent neutral baselines rather than measured alignment. Publishing content without brand verification risks diluting our brand identity, confusing our audience with inconsistent messaging, and potentially contradicting established brand guidelines. I recommend manual review by brand stakeholders to verify tone, check vocabulary against brand keywords, ensure messaging aligns with guidelines, and confirm overall brand consistency.',
            'concerns': 'Brand analysis incomplete due to technical error. Cannot verify tone alignment, vocabulary consistency, or messaging compliance. Manual brand review required to protect brand identity and ensure consistent brand experience.',
            'suggested_improvements': ['Complete full brand analysis', 'Manual brand consistency review', 'Verify tone matches brand guidelines', 'Check vocabulary against brand keywords']
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
        
        system_prompt = f"""You are {self.role} providing your initial analysis.

Provide a thorough but focused assessment including:
- Your immediate reaction and gut feeling
- Strategic recommendation (2-3 sentences)
- Detailed reasoning (4-5 sentences explaining your thinking)
- Specific concerns if any

You MUST respond in valid JSON format. All fields are required."""
        
        prompt = f"""
CONTEXT:
{json.dumps(context, indent=2)}

Provide your analysis in this EXACT JSON format:
{{
  "agent_name": "{self.name}",
  "agent_role": "{self.role}",
  "quick_take": "Your instant 2-3 sentence reaction to this content",
  "recommendation": "Your brand strategy recommendation in 2-3 detailed sentences",
  "reasoning": "Your complete brand analysis in paragraph form (minimum 4-5 sentences). Explain how you evaluated brand alignment and why.",
  "vote": "approve/conditional/reject",
  "score": 75,
  "gut_feeling": "excited/cautious/concerned/optimistic",
  "concerns": "Any brand consistency concerns in 2-3 sentences, or empty string if none"
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
                'recommendation': 'Unable to provide recommendation due to technical error. Manual review required.',
                'reasoning': 'A technical error prevented me from completing my initial brand alignment analysis. Without proper analysis, I cannot assess brand consistency or messaging compliance. Manual review recommended.',
                'vote': 'conditional',
                'score': 50,
                'concerns': 'Technical error prevented brand analysis'
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
