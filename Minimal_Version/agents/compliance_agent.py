"""
ComplianceAgent - Policy Compliance Guardian
Ensures all content meets platform guidelines, legal requirements, and regulatory standards
"""

import json
import logging
from typing import Dict, Any
from utils.llm_client import get_llm_client

logger = logging.getLogger(__name__)

class ComplianceAgent:
    """
    Policy Compliance Guardian Agent
    
    Core Mindset: "Compliance isn't optional. It's the foundation of sustainable operation."
    Primary Goal: Verify 100% compliance with platform, legal, and regulatory requirements
    """
    
    def __init__(self):
        self.name = "ComplianceAgent"
        self.role = "Policy Compliance Guardian"
        self.llm = get_llm_client()
        
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content for compliance with platform and legal requirements
        
        Args:
            context: Dictionary containing brand and post information
            
        Returns:
            Dict with compliance analysis, score, and required disclosures
        """
        logger.info(f"{self.name}: Starting compliance analysis")
        
        # Build the system prompt for ComplianceAgent personality
        system_prompt = """You are Policy Compliance Guardian, a legal and compliance expert.

Your personality:
- Detail-oriented scanner
- Rule book expert (platform policies, FTC guidelines, legal requirements)
- Zero-tolerance enforcer
- Protective guardian preventing lawsuits, fines, account suspension

Your job:
- Check platform-specific content policies
- Verify legal advertising requirements
- Ensure proper disclosures (FTC, sponsorships, affiliates)
- Identify copyright/trademark risks
- Flag prohibited content categories

Compliance Score:
- 100: Perfect compliance
- 90-99: Minor disclosure additions needed
- 75-89: Requires compliance modifications
- <75: Compliance violation - REJECT

Vote Rules:
- Score 90+: approve
- Score 75-89: conditional (with required changes)
- Score <75: reject
- Any legal violation: HARD REJECT

You MUST respond in valid JSON format with this structure:
{
  "compliance_analysis": "detailed compliance review",
  "platform_guidelines_met": true/false,
  "legal_requirements_met": true/false,
  "required_disclosures": ["disclosure 1", "disclosure 2"],
  "regulatory_concerns": ["concern 1", "concern 2"],
  "copyright_risks": ["risk 1", "risk 2"],
  "prohibited_content_flags": ["flag 1", "flag 2"],
  "compliance_score": <number 0-100>,
  "vote": "approve/conditional/reject",
  "recommendation": "Your compliance recommendation in 2-3 detailed sentences explaining what actions are needed and why they matter for legal and platform compliance",
  "reasoning": "Your complete compliance analysis in paragraph form (minimum 4-5 sentences). Explain which regulations you reviewed, what compliance issues you identified or ruled out, why your assessment is correct, and what legal or platform risks you considered. Be specific and thorough.",
  "concerns": "Any compliance concerns in 2-3 sentences explaining specific legal or policy risks",
  "required_changes": ["change 1", "change 2"]
}"""
        
        # Build the analysis prompt
        brand = context.get('brand', {})
        post = context.get('post', {})
        
        analysis_prompt = f"""
Analyze this content for compliance:

PLATFORM & BRAND:
- Platform: {post.get('platform')}
- Brand: {brand.get('name')}
- Market Segment: {brand.get('market_segment')}

POST CONTENT:
- Topic: {post.get('topic')}
- Objective: {post.get('objective')}
- Content Type: {post.get('content_type')}
- Key Message: {post.get('key_message')}
- CTA: {post.get('cta')}
- Special Requirements: {post.get('requirements')}

Check compliance for:

1. Platform Guidelines ({post.get('platform')}):
   - Community guidelines
   - Content policies
   - Advertising policies
   - Prohibited content

2. Legal Requirements:
   - FTC disclosure rules (ads, sponsorships, affiliate links)
   - Copyright/trademark law
   - Health claims regulations
   - Financial advice disclaimers
   - Data privacy (GDPR, CCPA)

3. Required Disclosures:
   - #ad, #sponsored, #partner tags
   - Affiliate disclaimers
   - Material connections
   - Medical/health disclaimers

Identify:
- Any missing disclosures
- Potential legal violations
- Copyright/trademark risks
- Platform policy violations

Score 0-100:
- 100: Perfect compliance
- 90-99: Minor additions needed
- 75-89: Modifications required
- <75: Violation - reject
"""
        
        try:
            # Get LLM response
            response = self.llm.simple_prompt(
                prompt=analysis_prompt,
                system_message=system_prompt,
                temperature=0.3,  # Low for strict compliance
                json_mode=True
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add agent metadata
            result['agent_name'] = self.name
            result['agent_role'] = self.role
            result['score'] = result.get('compliance_score', 0)
            
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
            'compliance_analysis': 'Unable to complete compliance analysis due to technical error',
            'platform_guidelines_met': False,
            'legal_requirements_met': False,
            'required_disclosures': ['Manual compliance review required - technical error occurred'],
            'regulatory_concerns': ['Analysis incomplete - cannot verify compliance'],
            'copyright_risks': [],
            'prohibited_content_flags': [],
            'compliance_score': 50,
            'score': 50,
            'vote': 'reject',
            'recommendation': 'I must reject this content due to incomplete compliance analysis. Technical difficulties prevented me from verifying platform guidelines, legal requirements, and required disclosures. Manual legal review is mandatory before proceeding.',
            'reasoning': 'A technical error interrupted my compliance analysis, preventing me from completing essential checks for platform policies, FTC disclosure requirements, copyright risks, and regulatory compliance. Without confirming that this content meets all legal and platform standards, I cannot approve it for publication. The compliance score of 50 reflects uncertainty, not measured compliance. Publishing without full compliance verification exposes the brand to potential legal liability, platform penalties, or account suspension. I strongly recommend conducting a thorough manual compliance review covering all platform-specific guidelines, advertising disclosure requirements, and relevant legal regulations.',
            'concerns': 'Compliance analysis incomplete due to technical error. Cannot verify platform policy compliance, legal requirements, or disclosure obligations. Manual legal review is mandatory to prevent potential violations.',
            'required_changes': ['Complete full compliance analysis', 'Manual legal and policy review', 'Verify all required disclosures']
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
        
        system_prompt = f"""You are {self.role} providing your initial compliance analysis.

Provide a thorough but focused assessment including:
- Your immediate reaction and gut feeling
- Compliance recommendation (2-3 sentences)
- Detailed reasoning (4-5 sentences explaining your analysis)
- Specific concerns if any

You MUST respond in valid JSON format. All fields are required."""
        
        prompt = f"""
CONTEXT:
{json.dumps(context, indent=2)}

Provide your compliance analysis in this EXACT JSON format:
{{
  "agent_name": "{self.name}",
  "agent_role": "{self.role}",
  "quick_take": "Your instant 2-3 sentence compliance reaction",
  "recommendation": "Your compliance recommendation in 2-3 detailed sentences",
  "reasoning": "Your complete compliance analysis in paragraph form (minimum 4-5 sentences). Explain what you checked and why.",
  "vote": "approve/conditional/reject",
  "score": 90,
  "gut_feeling": "excited/cautious/concerned/optimistic",
  "concerns": "Any compliance concerns in 2-3 sentences, or empty string if none"
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
                'recommendation': 'Unable to provide compliance recommendation due to technical error. Manual legal review required.',
                'reasoning': 'A technical error prevented me from completing my initial compliance analysis. Without proper verification of platform guidelines and legal requirements, I cannot approve this content. Manual compliance review is mandatory.',
                'vote': 'reject',
                'score': 50,
                'concerns': 'Technical error prevented compliance verification'
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
