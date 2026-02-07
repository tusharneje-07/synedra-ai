"""
Compliance Agent - Policy Enforcement Guardian
==============================================

This agent ensures all content meets platform guidelines and legal requirements.
It loads its complete behavioral specification from ComplianceAgent.md.

Role: Verify 100% compliance with platform policies and legal standards
Mindset: "Compliance isn't optional. It's the foundation of sustainable operation."

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import Dict, List, Optional, Any

from agents.base_agent import BaseAgent
from graph.state_schema import (
    CouncilState,
    ComplianceAgentProposal,
    AgentProposal,
    AgentType,
    Platform
)

logger = logging.getLogger(__name__)


class ComplianceAgent(BaseAgent):
    """
    Compliance Agent - Ensures platform and legal compliance.
    
    Personality Traits (from ComplianceAgent.md):
    - Detail-oriented scanner
    - Rule book expert
    - Zero-tolerance enforcer
    - Protective guardian
    
    Focus Areas:
    - Platform guidelines compliance
    - Legal requirements (FTC, GDPR, CCPA)
    - Required disclosures
    - Copyright/trademark compliance
    - Regulatory standards
    """
    
    def __init__(self, voting_weight: float = 0.15):
        """
        Initialize Compliance Agent.
        
        Args:
            voting_weight: Initial voting weight in council
        """
        super().__init__(
            agent_name="Policy Compliance Guardian",
            agent_type=AgentType.COMPLIANCE,
            behavior_file="ComplianceAgent.md",
            voting_weight=voting_weight
        )
        
        logger.info("ComplianceAgent initialized and ready to enforce compliance")
    
    def analyze(
        self,
        state: CouncilState,
        context: Optional[Dict[str, Any]] = None
    ) -> ComplianceAgentProposal:
        """
        Analyze compliance and generate policy enforcement proposal.
        
        Args:
            state: Current council state
            context: Additional context
            
        Returns:
            ComplianceAgentProposal with compliance assessment
        """
        topic = self.extract_topic_from_state(state)
        platform = state.get('platform', Platform.INSTAGRAM)
        
        # Load memory context
        memory_context = self._load_memory_context(
            current_situation=f"Compliance check for: {topic}",
            include_patterns=True
        )
        
        # Build analysis prompt
        analysis_prompt = f"""
SITUATION: {topic}

TARGET PLATFORM: {platform}

TASK:
Conduct COMPREHENSIVE COMPLIANCE CHECK for platform policies and legal requirements.

Your mindset: "Compliance isn't optional. It's the foundation of sustainable operation."

CHECK FOR:

1. PLATFORM GUIDELINES COMPLIANCE:
   - {platform} Community Guidelines
   - Content policies
   - Prohibited content categories
   - Age restrictions

2. LEGAL REQUIREMENTS:
   - FTC disclosure rules (ads, sponsorships)
   - GDPR/CCPA privacy compliance
   - Copyright law
   - Trademark law
   - Health claims regulations
   - Financial advice disclaimers

3. REQUIRED DISCLOSURES:
   - #ad, #sponsored tags needed?
   - Affiliate link disclaimers?
   - Material connection disclosures?
   - Medical/health disclaimers?
   - Financial advice warnings?

4. REGULATORY CONCERNS:
   - Industry-specific regulations
   - Advertising standards
   - Data privacy issues

COMPLIANCE SCORING (0-100):
- 100: Perfect compliance
- 90-99: Minor additions needed
- 75-89: Requires modifications
- <75: Violation - REJECT

VOTE RULES:
- Score 90+: APPROVE
- Score 75-89: CONDITIONAL (with required changes)
- Score <75: REJECT
- Any legal violation: HARD REJECT

Provide analysis in JSON format:
- compliance_score: float (0-100)
- platform_guidelines_met: boolean
- legal_requirements_met: boolean
- required_disclosures: array (what needs to be added)
- regulatory_concerns: array
- recommendation: string
- confidence: float (0-1)
- reasoning: string (cite specific policies/laws)
- concerns: array
- vote: string
"""
        
        schema_description = """
{
    "compliance_score": 0-100,
    "platform_guidelines_met": true/false,
    "legal_requirements_met": true/false,
    "required_disclosures": ["#ad", "disclaimer"],
    "regulatory_concerns": ["concern1"],
    "recommendation": "detailed compliance assessment",
    "confidence": 0.0-1.0,
    "reasoning": "cite specific policies and laws",
    "concerns": ["concern1"],
    "vote": "approve/reject/conditional"
}
"""
        
        opinion = self._generate_opinion(
            prompt=analysis_prompt,
            context=memory_context,
            schema_description=schema_description
        )
        
        # Build specialized ComplianceAgentProposal
        proposal = ComplianceAgentProposal(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            timestamp=self._get_timestamp(),
            
            # Core proposal fields
            recommendation=opinion.get('recommendation', 'No recommendation generated'),
            confidence=opinion.get('confidence', 0.5),
            priority=self._calculate_priority_from_compliance(
                opinion.get('compliance_score', 75)
            ),
            reasoning=opinion.get('reasoning', 'No reasoning provided'),
            supporting_evidence=[
                f"Compliance score: {opinion.get('compliance_score', 0)}/100",
                f"Platform guidelines: {'Met' if opinion.get('platform_guidelines_met') else 'Not met'}",
                f"Legal requirements: {'Met' if opinion.get('legal_requirements_met') else 'Not met'}"
            ],
            concerns=opinion.get('concerns', []),
            scores={
                'compliance': opinion.get('compliance_score', 75) / 100,
                'platform_compliance': 1.0 if opinion.get('platform_guidelines_met') else 0.0,
                'legal_compliance': 1.0 if opinion.get('legal_requirements_met') else 0.0
            },
            conflicts_with=[],
            vote=opinion.get('vote', 'conditional'),
            conditions=opinion.get('required_disclosures', []),
            
            # Compliance-specific fields
            policy_compliance_score=opinion.get('compliance_score', 75.0),
            legal_risk_level=self._determine_legal_risk(
                opinion.get('legal_requirements_met', False),
                opinion.get('compliance_score', 75)
            ),
            platform_guidelines_met=opinion.get('platform_guidelines_met', False),
            required_disclosures=opinion.get('required_disclosures', []),
            regulatory_concerns=opinion.get('regulatory_concerns', []),
            
            metadata={
                'compliance_analysis_version': '1.0',
                'analysis_timestamp': self._get_timestamp(),
                'platform_checked': platform.value if hasattr(platform, 'value') else str(platform)
            }
        )
        
        # Store in memory
        self._store_decision_memory(
            context=f"Compliance check: {topic}",
            decision={
                'compliance_score': proposal['policy_compliance_score'],
                'vote': proposal['vote'],
                'violations': len(proposal['regulatory_concerns'])
            },
            reasoning=proposal['reasoning'],
            importance=0.9 if proposal['vote'] == 'reject' else 0.6
        )
        
        logger.info(
            f"ComplianceAgent analysis complete: "
            f"Score {proposal['policy_compliance_score']:.0f}/100, "
            f"Vote: {proposal['vote']}, "
            f"Disclosures needed: {len(proposal['required_disclosures'])}"
        )
        
        return proposal
    
    def debate(
        self,
        state: CouncilState,
        other_proposals: List[AgentProposal]
    ) -> Dict[str, Any]:
        """
        Participate in debate using legal/policy citations.
        
        ComplianceAgent typically:
        - Uses factual, legal language
        - Cites specific policies and laws
        - No negotiation on legal violations
        - Helps with compliant alternatives
        - Firm but constructive
        
        Args:
            state: Current council state
            other_proposals: Proposals from other agents
            
        Returns:
            Debate response with policy-based arguments
        """
        topic = self.extract_topic_from_state(state)
        
        debate_prompt = f"""
DEBATE SITUATION:
Topic: {topic}

OTHER AGENTS' POSITIONS:
{self._format_other_proposals(other_proposals)}

YOUR ROLE IN DEBATE:
You are ComplianceAgent - detail-oriented, zero-tolerance on legal issues.

Your mindset: "Compliance isn't optional."

TASK:
Respond to other agents using FACTUAL, LEGAL language.

Your debate style:
- "This requires FTC disclosure under 16 CFR Part 255"
- "Platform policy 3.2 prohibits this content type"
- "GDPR Article 6 requires explicit consent"
- "We can make it compliant by adding [specific change]"

Rules:
- NO negotiation on legal violations
- Willing to help with compliant alternatives
- Cite specific policies, laws, regulations
- Offer constructive solutions when possible

Provide:
1. Legal/policy citations for your position
2. Required compliance modifications
3. Compliant alternative suggestions (if applicable)
4. Final vote

Respond in JSON format.
"""
        
        schema = """
{
    "legal_policy_citations": ["citation1", "citation2"],
    "required_modifications": ["change1", "change2"],
    "compliant_alternatives": "suggestions for compliance",
    "negotiation_possible": true/false,
    "final_vote": "approve/reject/conditional"
}
"""
        
        debate_response = self._generate_opinion(
            prompt=debate_prompt,
            context="",
            schema_description=schema
        )
        
        logger.info(f"ComplianceAgent debate response: {debate_response.get('final_vote', 'unknown')}")
        
        return {
            'agent_name': self.agent_name,
            'debate_response': debate_response,
            'uses_legal_citations': True,
            'offers_alternatives': debate_response.get('compliant_alternatives') is not None,
            'final_vote': debate_response.get('final_vote', 'conditional')
        }
    
    def _calculate_priority_from_compliance(self, compliance_score: float) -> str:
        """Calculate priority from compliance score."""
        if compliance_score >= 90:
            return "low"  # Compliant, low urgency
        elif compliance_score >= 75:
            return "medium"  # Needs work
        else:
            return "high"  # Violation, high urgency
    
    def _determine_legal_risk(self, legal_met: bool, score: float) -> str:
        """Determine legal risk level."""
        if not legal_met or score < 60:
            return "high"
        elif score < 80:
            return "medium"
        else:
            return "low"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _format_other_proposals(self, proposals: List[AgentProposal]) -> str:
        """Format other proposals for debate context."""
        formatted = []
        for p in proposals:
            formatted.append(
                f"- {p.get('agent_name', 'Unknown')} ({p.get('agent_type', 'unknown')}): "
                f"Vote={p.get('vote', 'unknown')}"
            )
        return "\n".join(formatted) if formatted else "No other proposals yet"
