"""
RiskAgent - Reputation Shield Officer
Prevents brand damage before it happens by assessing controversy and backlash risks
"""

import json
import logging
from typing import Dict, Any
from utils.llm_client import get_llm_client

logger = logging.getLogger(__name__)

class RiskAgent:
    """
    Reputation Shield Officer (RSO) Agent
    
    Core Mindset: "One bad post can destroy months of brand trust."
    Primary Goal: Prevent brand damage before it happens
    """
    
    def __init__(self):
        self.name = "RiskAgent"
        self.role = "Reputation Shield Officer"
        self.llm = get_llm_client()
        
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content for reputation risks and potential backlash
        
        Args:
            context: Dictionary containing brand and post information
            
        Returns:
            Dict with risk analysis, scores, and safety recommendations
        """
        logger.info(f"{self.name}: Starting risk analysis")
        
        # Build the system prompt for RiskAgent personality
        system_prompt = """You are Reputation Shield Officer, a brand safety and risk expert.

Your personality:
- Cold, analytical, serious
- Worst-case thinker - imagine worst scenarios
- Paranoid investigator - search for hidden meanings
- Policy lawyer type - think in rules and guidelines
- Pattern memory expert - remember past backlashes

Your job:
- Detect sensitive topics (politics, religion, gender, war, discrimination)
- Assess controversy probability
- Identify potential backlash triggers
- Check for misinformation risks
- Evaluate toxicity and offensive content
- Predict platform ban probability

Risk Categories to Check:
1. Sensitive topics
2. Controversial statements
3. Cultural insensitivity
4. Misinformation potential
5. Offensive language
6. Brand reputation damage

Risk Score System:
- 0-25: Low risk (safe to publish)
- 26-50: Moderate risk (needs review)
- 51-75: High risk (significant changes needed)
- 76-100: Critical risk (reject immediately)

You MUST respond in valid JSON format with this structure:
{
  "risk_analysis": "detailed risk assessment",
  "controversy_probability": <number 0-100>,
  "backlash_risk": <number 0-100>,
  "platform_ban_probability": <number 0-100>,
  "toxicity_score": <number 0-100>,
  "sensitive_topics_detected": ["topic 1", "topic 2"],
  "potential_triggers": ["trigger 1", "trigger 2"],
  "worst_case_scenarios": ["scenario 1", "scenario 2"],
  "overall_risk_score": <number 0-100>,
  "vote": "approve/conditional/reject",
  "recommendation": "Your risk management recommendation in 2-3 detailed sentences explaining what should be done to protect brand reputation and why it matters",
  "reasoning": "Your complete risk analysis in paragraph form (minimum 4-5 sentences). Explain what risks you identified, why they matter for brand safety, what past incidents or patterns informed your analysis, and how you calculated the risk scores. Be thorough and analytical.",
  "concerns": "Specific reputation or safety concerns in 2-3 sentences explaining potential negative outcomes",
  "mitigation_strategies": ["strategy 1", "strategy 2"]
}"""
        
        # Build the analysis prompt
        brand = context.get('brand', {})
        post = context.get('post', {})
        
        analysis_prompt = f"""
Analyze this content for reputation risks:

BRAND CONTEXT:
- Brand: {brand.get('name')}
- Target Audience: {brand.get('target_audience')}
- Market Segment: {brand.get('market_segment')}
- Competitors: {brand.get('competitors')}

POST CONTENT:
- Topic: {post.get('topic')}
- Objective: {post.get('objective')}
- Platform: {post.get('platform')}
- Content Type: {post.get('content_type')}
- Key Message: {post.get('key_message')}
- CTA: {post.get('cta')}

Assess risks for:

1. Sensitive Topics:
   - Politics, religion, gender/identity
   - War, conflict, social justice
   - Discrimination, stereotypes
   
2. Controversy Potential:
   - Could this be misinterpreted?
   - Does it touch controversial subjects?
   - Could it offend any groups?

3. Brand Safety:
   - Platform ban risk
   - Negative sentiment spike potential
   - PR crisis probability
   - Trust erosion risk

4. Content Issues:
   - Misinformation potential
   - Offensive language
   - Cultural insensitivity
   - Inappropriate humor

Score each risk area 0-100, then calculate overall risk:
- Overall Risk Score = average of all risk scores

Vote based on risk:
- 0-25: approve (low risk)
- 26-50: conditional (moderate - needs safeguards)
- 51+: reject (high/critical risk)

Think like a paranoid auditor. Imagine worst-case scenarios!
"""
        
        try:
            # Get LLM response
            response = self.llm.simple_prompt(
                prompt=analysis_prompt,
                system_message=system_prompt,
                temperature=0.4,  # Low-moderate for careful analysis
                json_mode=True
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add agent metadata
            result['agent_name'] = self.name
            result['agent_role'] = self.role
            result['score'] = 100 - result.get('overall_risk_score', 50)  # Invert score (lower risk = higher score)
            
            logger.info(f"{self.name}: Analysis complete - Risk: {result.get('overall_risk_score')}, Vote: {result.get('vote')}")
            
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
            'risk_analysis': 'Unable to complete comprehensive risk analysis due to technical error',
            'controversy_probability': 50,
            'backlash_risk': 50,
            'platform_ban_probability': 20,
            'toxicity_score': 30,
            'sensitive_topics_detected': ['Unknown - analysis incomplete due to technical error'],
            'potential_triggers': ['Analysis incomplete - cannot identify all risk factors'],
            'worst_case_scenarios': ['Unable to assess worst-case outcomes without complete risk analysis'],
            'overall_risk_score': 50,
            'score': 50,
            'vote': 'reject',
            'recommendation': 'I must reject this content due to incomplete risk assessment. Technical difficulties prevented comprehensive analysis of brand safety risks. Manual reputation risk review is required before publication.',
            'reasoning': 'A technical error interrupted my risk analysis, preventing me from completing critical safety checks for sensitive topics, controversy potential, toxicity, and brand reputation damage. Without confirming this content is safe from backlash, platform violations, or PR crises, I cannot approve it. The risk scores reflect uncertainty rather than measured safety levels. Publishing content with unverified safety risks could result in brand damage, negative sentiment spikes, platform penalties, or public backlash. I strongly recommend conducting a thorough manual risk assessment covering sensitive topics, cultural sensitivity, potential misinterpretation, and worst-case reputation scenarios before proceeding.',
            'concerns': 'Risk analysis incomplete due to technical error. Cannot verify brand safety, identify sensitive topics, or assess backlash potential. Manual reputation review mandatory to protect brand integrity.',
            'mitigation_strategies': ['Complete full risk analysis', 'Manual brand safety review', 'Verify no sensitive or controversial elements', 'Test content with focus group before publishing']
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
        
        system_prompt = f"""You are {self.role} providing your initial risk analysis.

Provide a thorough but focused assessment including:
- Your immediate reaction and gut feeling
- Risk recommendation (2-3 sentences)
- Detailed reasoning (4-5 sentences explaining your safety analysis)
- Specific concerns if any

You MUST respond in valid JSON format. All fields are required."""
        
        prompt = f"""
CONTEXT:
{json.dumps(context, indent=2)}

Provide your risk analysis in this EXACT JSON format:
{{
  "agent_name": "{self.name}",
  "agent_role": "{self.role}",
  "quick_take": "Your instant 2-3 sentence risk assessment",
  "recommendation": "Your risk management recommendation in 2-3 detailed sentences",
  "reasoning": "Your complete risk analysis in paragraph form (minimum 4-5 sentences). Explain what risks you identified and why.",
  "vote": "approve/conditional/reject",
  "score": 80,
  "gut_feeling": "excited/cautious/concerned/optimistic",
  "concerns": "Any safety concerns in 2-3 sentences, or empty string if none"
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
                'recommendation': 'Unable to provide risk recommendation due to technical error. Manual safety review required.',
                'reasoning': 'A technical error prevented me from completing my initial risk analysis. Without proper assessment of brand safety risks and potential backlash, I cannot approve this content. Manual reputation review is mandatory.',
                'vote': 'reject',
                'score': 50,
                'concerns': 'Technical error prevented risk assessment'
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
