"""
Agents Package
==============

Contains all agent implementations for the AI Council:
- BaseAgent: Foundation class with LLM client and markdown loading
- TrendAgent: Viral opportunity hunter
- EngagementAgent: Community building specialist
- BrandAgent: Voice consistency guardian
- RiskAgent: Safety and damage prevention
- ComplianceAgent: Policy and legal enforcement
- ArbitratorAgent: CMO final decision maker
- AgentFactory: Factory for creating and managing agents
"""

from .base_agent import BaseAgent, BaseLLMClient, AgentFactory
from .trend_agent import TrendAgent
from .engagement_agent import EngagementAgent
from .brand_agent import BrandAgent
from .risk_agent import RiskAgent
from .compliance_agent import ComplianceAgent
from .arbitrator_agent import ArbitratorAgent

__all__ = [
    'BaseAgent',
    'BaseLLMClient',
    'AgentFactory',
    'TrendAgent',
    'EngagementAgent',
    'BrandAgent',
    'RiskAgent',
    'ComplianceAgent',
    'ArbitratorAgent'
]

