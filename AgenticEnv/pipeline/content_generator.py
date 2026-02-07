"""
Content Generator - Platform-Specific Content Creation
======================================================

Generates content optimized for each platform based on council decisions.

Features:
- Platform-specific formatting
- Character limit enforcement
- Hashtag optimization
- Media recommendations
- Multi-platform content variants

Author: AI Systems Engineer
Date: February 7, 2026
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from graph import Platform, CouncilState
from config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class ContentPiece:
    """Represents generated content for a platform."""
    platform: Platform
    content_type: str  # text, image, video
    primary_text: str
    caption: Optional[str]
    hashtags: List[str]
    call_to_action: Optional[str]
    media_suggestions: List[str]
    character_count: int
    estimated_engagement: float
    metadata: Dict[str, Any]
    created_at: str


@dataclass
class MultiPlatformContent:
    """Content optimized for multiple platforms."""
    topic: str
    platforms: List[Platform]
    variants: Dict[Platform, ContentPiece]
    council_decision: Dict[str, Any]
    created_at: str


class ContentGenerator:
    """
    Generates platform-optimized content based on council decisions.
    
    Platform Limits:
    - Instagram: 2200 chars, 30 hashtags
    - Twitter: 280 chars, 2 hashtags optimal
    - LinkedIn: 3000 chars, 3 hashtags optimal
    - YouTube: 5000 char description
    """
    
    PLATFORM_LIMITS = {
        Platform.INSTAGRAM: {'max_chars': 2200, 'optimal_hashtags': 30},
        Platform.TWITTER: {'max_chars': 280, 'optimal_hashtags': 2},
        Platform.LINKEDIN: {'max_chars': 3000, 'optimal_hashtags': 3},
        Platform.YOUTUBE: {'max_chars': 5000, 'optimal_hashtags': 5}
    }
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize Content Generator.
        
        Args:
            settings: Application settings
        """
        self.settings = settings or Settings()
        logger.info("ContentGenerator initialized")
    
    def generate_from_council_decision(
        self,
        council_state: CouncilState,
        platforms: List[Platform] = None
    ) -> MultiPlatformContent:
        """
        Generate content based on council decision.
        
        Args:
            council_state: Final council state with decision
            platforms: Platforms to generate for
            
        Returns:
            Multi-platform content package
        """
        logger.info(f"Generating content for topic: {council_state.get('topic')}")
        
        platforms = platforms or [council_state.get('platform', Platform.INSTAGRAM)]
        
        variants = {}
        for platform in platforms:
            content = self.generate_platform_content(
                council_state=council_state,
                platform=platform
            )
            variants[platform] = content
        
        return MultiPlatformContent(
            topic=council_state.get('topic', ''),
            platforms=platforms,
            variants=variants,
            council_decision=council_state.get('final_decision', {}),
            created_at=datetime.now().isoformat()
        )
    
    def generate_platform_content(
        self,
        council_state: CouncilState,
        platform: Platform
    ) -> ContentPiece:
        """
        Generate content for specific platform.
        
        Args:
            council_state: Council decision state
            platform: Target platform
            
        Returns:
            Platform-optimized content
        """
        final_decision = council_state.get('final_decision', {})
        topic = council_state.get('topic', '')
        
        # Extract council recommendations
        recommendation = final_decision.get('recommendation', topic)
        approved_elements = final_decision.get('approved_elements', [])
        modifications = final_decision.get('modifications_required', [])
        
        # Get platform limits
        limits = self.PLATFORM_LIMITS.get(platform, {'max_chars': 1000, 'optimal_hashtags': 5})
        
        # Generate primary text
        primary_text = self._generate_primary_text(
            recommendation=recommendation,
            platform=platform,
            max_chars=limits['max_chars'],
            approved_elements=approved_elements
        )
        
        # Generate hashtags
        hashtags = self._generate_hashtags(
            topic=topic,
            platform=platform,
            optimal_count=limits['optimal_hashtags']
        )
        
        # Generate CTA
        cta = self._generate_cta(platform=platform)
        
        # Media suggestions
        media = self._suggest_media(
            topic=topic,
            platform=platform
        )
        
        # Calculate character count
        full_text = f"{primary_text}\n\n{' '.join(hashtags)}"
        if cta:
            full_text += f"\n\n{cta}"
        
        char_count = len(full_text)
        
        return ContentPiece(
            platform=platform,
            content_type='text',
            primary_text=primary_text,
            caption=None,
            hashtags=hashtags,
            call_to_action=cta,
            media_suggestions=media,
            character_count=char_count,
            estimated_engagement=self._estimate_engagement(platform, primary_text, hashtags),
            metadata={
                'modifications_applied': modifications,
                'within_limits': char_count <= limits['max_chars']
            },
            created_at=datetime.now().isoformat()
        )
    
    def _generate_primary_text(
        self,
        recommendation: str,
        platform: Platform,
        max_chars: int,
        approved_elements: List[str]
    ) -> str:
        """Generate primary content text."""
        # In production, this would use LLM to craft compelling copy
        # For now, format the recommendation
        
        text = recommendation
        
        # Add platform-specific formatting
        if platform == Platform.TWITTER:
            # Twitter: Concise, punchy
            if len(text) > max_chars - 100:  # Leave room for hashtags
                text = text[:max_chars - 100] + "..."
        
        elif platform == Platform.LINKEDIN:
            # LinkedIn: Professional, detailed
            if approved_elements:
                text += "\n\nKey highlights:\n"
                text += "\n".join(f"• {elem}" for elem in approved_elements[:3])
        
        elif platform == Platform.INSTAGRAM:
            # Instagram: Engaging, visual-focused
            text = "✨ " + text
        
        return text
    
    def _generate_hashtags(
        self,
        topic: str,
        platform: Platform,
        optimal_count: int
    ) -> List[str]:
        """Generate relevant hashtags."""
        # In production, would analyze trending hashtags and relevance
        
        # Extract keywords from topic
        words = topic.lower().split()
        
        # Generate basic hashtags
        hashtags = []
        
        # Topic-based hashtags
        for word in words:
            if len(word) > 3 and word.isalpha():
                hashtags.append(f"#{word.capitalize()}")
        
        # Platform-specific hashtags
        if platform == Platform.INSTAGRAM:
            hashtags.extend(['#Instagood', '#Marketing'])
        elif platform == Platform.TWITTER:
            hashtags.extend(['#Tech', '#Innovation'])
        elif platform == Platform.LINKEDIN:
            hashtags.extend(['#Business', '#Leadership'])
        
        # Limit to optimal count
        return hashtags[:optimal_count]
    
    def _generate_cta(self, platform: Platform) -> Optional[str]:
        """Generate call-to-action."""
        ctas = {
            Platform.INSTAGRAM: "Link in bio! 👆",
            Platform.TWITTER: "Learn more ⬇️",
            Platform.LINKEDIN: "Share your thoughts in the comments.",
            Platform.YOUTUBE: "Subscribe for more content!"
        }
        
        return ctas.get(platform)
    
    def _suggest_media(
        self,
        topic: str,
        platform: Platform
    ) -> List[str]:
        """Suggest media types for content."""
        suggestions = []
        
        if platform == Platform.INSTAGRAM:
            suggestions = ['Carousel post', 'Reel', 'Story']
        elif platform == Platform.TWITTER:
            suggestions = ['Image', 'GIF', 'Poll']
        elif platform == Platform.LINKEDIN:
            suggestions = ['Infographic', 'Document post', 'Video']
        elif platform == Platform.YOUTUBE:
            suggestions = ['Tutorial video', 'Shorts', 'Interview']
        
        return suggestions
    
    def _estimate_engagement(
        self,
        platform: Platform,
        text: str,
        hashtags: List[str]
    ) -> float:
        """Estimate engagement potential (0-1)."""
        score = 0.5  # Base score
        
        # Text length optimization
        char_count = len(text)
        optimal_lengths = {
            Platform.INSTAGRAM: (150, 300),
            Platform.TWITTER: (100, 200),
            Platform.LINKEDIN: (200, 500)
        }
        
        optimal = optimal_lengths.get(platform, (100, 300))
        if optimal[0] <= char_count <= optimal[1]:
            score += 0.2
        
        # Hashtag optimization
        if len(hashtags) > 0:
            score += 0.1
        
        # Emoji usage (simple check)
        if any(ord(c) > 127 for c in text):
            score += 0.1
        
        # Question marks (engagement trigger)
        if '?' in text:
            score += 0.1
        
        return min(score, 1.0)
    
    def format_for_platform(
        self,
        content: ContentPiece,
        include_metadata: bool = False
    ) -> str:
        """
        Format content piece as ready-to-post text.
        
        Args:
            content: Content piece
            include_metadata: Include metadata in output
            
        Returns:
            Formatted text
        """
        parts = [content.primary_text]
        
        if content.hashtags:
            parts.append("")  # Blank line
            parts.append(" ".join(content.hashtags))
        
        if content.call_to_action:
            parts.append("")
            parts.append(content.call_to_action)
        
        formatted = "\n".join(parts)
        
        if include_metadata:
            meta = [
                "\n" + "="*50,
                f"Platform: {content.platform.value}",
                f"Character count: {content.character_count}",
                f"Estimated engagement: {content.estimated_engagement:.2f}",
                f"Media suggestions: {', '.join(content.media_suggestions)}"
            ]
            formatted += "\n" + "\n".join(meta)
        
        return formatted
    
    def export_multi_platform(
        self,
        multi_content: MultiPlatformContent,
        format: str = 'text'
    ) -> Dict[str, str]:
        """
        Export multi-platform content in specified format.
        
        Args:
            multi_content: Multi-platform content
            format: Export format (text, json, markdown)
            
        Returns:
            Dict mapping platform to formatted content
        """
        exports = {}
        
        for platform, content in multi_content.variants.items():
            if format == 'text':
                exports[platform.value] = self.format_for_platform(content, include_metadata=True)
            elif format == 'json':
                import json
                exports[platform.value] = json.dumps(content.__dict__, indent=2, default=str)
            elif format == 'markdown':
                exports[platform.value] = self._format_markdown(content)
        
        return exports
    
    def _format_markdown(self, content: ContentPiece) -> str:
        """Format content as markdown."""
        lines = [
            f"# {content.platform.value.title()} Post",
            "",
            "## Content",
            content.primary_text,
            "",
            "## Hashtags",
            " ".join(content.hashtags),
            "",
            "## CTA",
            content.call_to_action or "None",
            "",
            "## Media Suggestions",
            ", ".join(content.media_suggestions),
            "",
            f"**Character Count:** {content.character_count}",
            f"**Estimated Engagement:** {content.estimated_engagement:.2f}",
        ]
        
        return "\n".join(lines)
