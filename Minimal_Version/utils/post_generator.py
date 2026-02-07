"""
Post Generator - Creates final post variations from debate results
Generates multiple post options with title, content, hashtags, and image prompts
"""

import json
import logging
import os
from typing import Dict, List, Any
from database import get_db
from utils.llm_client import get_llm_client

logger = logging.getLogger(__name__)

class PostGenerator:
    """Generates final post variations based on agent recommendations"""
    
    def __init__(self):
        """Initialize post generator"""
        self.db = get_db()
        self.llm = get_llm_client()
        self.num_variations = int(os.getenv('NUM_POST_VARIATIONS', '3'))
    
    def generate_posts(
        self,
        post_input_id: int,
        debate_results: Dict[str, Any],
        num_variations: int = None
    ) -> List[Dict[str, Any]]:
        """
        Generate post variations based on CMO decision
        
        Args:
            post_input_id: ID of the post input
            debate_results: Results from the debate process
            num_variations: Number of variations to generate (default from env)
            
        Returns:
            List of generated post variations
        """
        if num_variations is None:
            num_variations = self.num_variations
            
        logger.info(f"Generating {num_variations} post variations for post_input_id: {post_input_id}")
        
        # Check if debate was successful
        if not debate_results.get('success'):
            logger.error("Cannot generate posts - debate failed")
            return []
        
        # Get CMO decision
        cmo_decision = debate_results.get('cmo_decision', {})
        final_vote = cmo_decision.get('final_vote', 'reject')
        
        # Don't generate if rejected
        if final_vote == 'reject':
            logger.warning("CMO rejected - not generating posts")
            return []
        
        # Get context and instructions
        context = debate_results.get('context', {})
        post_instructions = cmo_decision.get('post_generation_instructions', {})
        
        # Generate variations
        generated_posts = []
        
        for i in range(1, num_variations + 1):
            try:
                logger.info(f"Generating variation {i}/{num_variations}")
                post = self._generate_single_post(context, cmo_decision, post_instructions, i)
                
                if post:
                    # Save to database
                    post_id = self.save_generated_post(
                        post_input_id=post_input_id,
                        variation_number=i,
                        post_title=post['title'],
                        post_content=post['content'],
                        hashtags=post['hashtags'],
                        image_prompt=post['image_prompt'],
                        final_score=cmo_decision.get('confidence_score', 0),
                        metadata=post.get('metadata', {})
                    )
                    
                    post['id'] = post_id
                    post['variation_number'] = i
                    generated_posts.append(post)
                    
            except Exception as e:
                logger.error(f"Error generating variation {i}: {e}")
                continue
        
        logger.info(f"Successfully generated {len(generated_posts)} post variations")
        return generated_posts
    
    def _generate_single_post(
        self,
        context: Dict[str, Any],
        cmo_decision: Dict[str, Any],
        instructions: Dict[str, Any],
        variation_number: int
    ) -> Dict[str, Any]:
        """
        Generate a single post variation
        
        Args:
            context: Brand and post context
            cmo_decision: CMO arbitration decision
            instructions: Specific post generation instructions
            variation_number: Which variation this is (1, 2, 3)
            
        Returns:
            Dict with title, content, hashtags, image_prompt
        """
        # Build generation prompt
        system_prompt = """You are a professional social media content creator.

Your job is to create engaging, on-brand social media posts that follow specific strategic guidelines.

You MUST respond in valid JSON format with this exact structure:
{
  "title": "catchy post title/headline",
  "content": "complete post content/description",
  "hashtags": "#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5",
  "image_prompt": "detailed prompt for AI image generation",
  "metadata": {
    "variation_style": "description of this variation's approach",
    "key_elements": ["element 1", "element 2"]
  }
}"""
        
        brand = context.get('brand', {})
        post = context.get('post', {})
        
        # Different styles for different variations
        variation_styles = {
            1: "Most strategic and balanced - follow CMO instructions precisely",
            2: "More creative and trend-focused - slightly more bold",
            3: "Engagement-optimized - maximum interaction potential"
        }
        
        variation_style = variation_styles.get(variation_number, variation_styles[1])
        
        generation_prompt = f"""
Create a social media post based on these strategic guidelines:

BRAND CONTEXT:
- Brand: {brand.get('name')}
- Tone: {brand.get('tone')}
- Target Audience: {brand.get('target_audience')}
- Platform: {post.get('platform')}

POST REQUIREMENTS:
- Topic: {post.get('topic')}
- Objective: {post.get('objective')}
- Content Type: {post.get('content_type')}
- Key Message: {post.get('key_message')}
- CTA: {post.get('cta')}

CMO STRATEGIC DIRECTION:
- Tone Direction: {instructions.get('tone_direction', 'balanced')}
- Content Focus: {instructions.get('content_focus', '')}
- Elements to Include: {', '.join(instructions.get('elements_to_include', []))}
- Elements to Avoid: {', '.join(instructions.get('elements_to_avoid', []))}
- Format: {instructions.get('format_recommendation', 'standard post')}

VARIATION STYLE #{variation_number}:
{variation_style}

Create a complete social media post with:
1. TITLE: Catchy, attention-grabbing headline (50-80 characters)
2. CONTENT: Full post content (200-300 words for {post.get('platform')})
   - Start with a hook
   - Include the key message naturally
   - Add value/information
   - End with clear CTA
3. HASHTAGS: 5-8 relevant, trending hashtags (space-separated with #)
4. IMAGE_PROMPT: Detailed AI image generation prompt (describe the scene, mood, style, colors)

Make it engaging, authentic, and aligned with the brand voice!
"""
        
        try:
            # Get LLM response
            response = self.llm.simple_prompt(
                prompt=generation_prompt,
                system_message=system_prompt,
                temperature=0.7 + (variation_number * 0.05),  # Slightly more creative for later variations
                json_mode=True
            )
            
            # Parse JSON response
            post_data = json.loads(response)
            
            logger.info(f"Generated post variation {variation_number}")
            return post_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse post generation JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating post: {e}")
            return None
    
    def save_generated_post(
        self,
        post_input_id: int,
        variation_number: int,
        post_title: str,
        post_content: str,
        hashtags: str,
        image_prompt: str,
        final_score: float = None,
        metadata: Dict[str, Any] = None
    ) -> int:
        """Save a generated post to database"""
        post_data = {
            'post_input_id': post_input_id,
            'variation_number': variation_number,
            'post_title': post_title,
            'post_content': post_content,
            'hashtags': hashtags,
            'image_prompt': image_prompt,
            'final_score': final_score,
            'metadata': metadata or {}
        }
        
        return self.db.create_generated_post(post_data)
