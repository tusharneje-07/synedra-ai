"""
Pipeline Package
================

Contains pipeline components for autonomous execution:
- TrendMonitor: Detect viral opportunities
- ContentGenerator: Create platform-specific content
- Scheduler: Autonomous execution cycles
- SentimentAnalyzer: Performance feedback loop
"""

from pipeline.trend_monitor import TrendMonitor
from pipeline.content_generator import ContentGenerator
from pipeline.scheduler import AutonomousScheduler
from pipeline.sentiment_analyzer import SentimentAnalyzer

__all__ = [
    'TrendMonitor',
    'ContentGenerator',
    'AutonomousScheduler',
    'SentimentAnalyzer'
]
