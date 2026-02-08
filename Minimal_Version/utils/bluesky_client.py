"""
Bluesky Content Posting Client
"""

import os
import json
from typing import List, Optional
from datetime import datetime, timezone
import mimetypes
import requests
import logging

logger = logging.getLogger(__name__)


def create_client(handle: str, app_password: str):
    """Factory function to create and login a Bluesky client."""
    client = BlueskyClient()
    return client.login(handle, app_password)


class BlueskyClient:
    """Simple HTTP-based Bluesky client."""
    
    def __init__(self):
        self.api_base = "https://bsky.social/xrpc"
        self.session = None
        self.did = None
    
    def login(self, handle: str, app_password: str):
        """Authenticate and store session."""
        response = requests.post(
            f"{self.api_base}/com.atproto.server.createSession",
            json={"identifier": handle, "password": app_password}
        )
        response.raise_for_status()
        data = response.json()
        self.session = data["accessJwt"]
        self.did = data["did"]
        logger.info(f"Bluesky login successful for {handle}")
        return self
    
    def _headers(self):
        """Return authorization headers."""
        return {"Authorization": f"Bearer {self.session}"}
    
    def upload_image(self, image_path: str) -> dict:
        """Upload an image and return blob reference."""
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            mime_type = 'image/jpeg'
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        response = requests.post(
            f"{self.api_base}/com.atproto.repo.uploadBlob",
            headers={
                **self._headers(),
                "Content-Type": mime_type
            },
            data=image_data
        )
        response.raise_for_status()
        return response.json()["blob"]
    
    def post(self, text: str, image_paths: list = None) -> dict:
        """Create a post with optional images and return the response with uri."""
        # Ensure text is properly encoded
        if not text or not text.strip():
            raise ValueError("Post text cannot be empty")
        
        text = text.strip()
        
        # Bluesky has a 300 grapheme limit (using character count as approximation)
        MAX_LENGTH = 300
        if len(text) > MAX_LENGTH:
            text = text[:MAX_LENGTH - 3] + "..."
            logger.warning(f"Text truncated to {MAX_LENGTH} characters to meet Bluesky limit")
        
        record = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        # Upload images if provided
        if image_paths:
            images = []
            for img_path in image_paths[:4]:  # Bluesky supports max 4 images
                if os.path.isfile(img_path):
                    blob = self.upload_image(img_path)
                    images.append({
                        "alt": "",
                        "image": blob
                    })
            
            if images:
                record["embed"] = {
                    "$type": "app.bsky.embed.images",
                    "images": images
                }
        
        logger.info(f"Posting to Bluesky. Text length: {len(text)} chars")
        
        response = requests.post(
            f"{self.api_base}/com.atproto.repo.createRecord",
            headers={
                **self._headers(),
                "Content-Type": "application/json"
            },
            json={
                "repo": self.did,
                "collection": "app.bsky.feed.post",
                "record": record
            }
        )
        
        # Log the error response for debugging
        if response.status_code != 200:
            logger.error(f"Bluesky API error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            logger.error(f"Request record: {record}")
        
        response.raise_for_status()
        result = response.json()
        logger.info(f"Posted successfully. URI: {result.get('uri')}")
        return result
    
    def get_post_thread(self, uri: str) -> dict:
        """Fetch post thread data."""
        response = requests.get(
            f"{self.api_base}/app.bsky.feed.getPostThread",
            headers=self._headers(),
            params={"uri": uri}
        )
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self, uri: str) -> dict:
        """Fetch post metrics (likes, reposts, replies) and actual reply content."""
        data = self.get_post_thread(uri)
        post = data["thread"]["post"]
        
        # Extract replies from thread
        replies_data = []
        if "replies" in data["thread"]:
            for reply in data["thread"]["replies"]:
                if reply.get("post"):
                    reply_post = reply["post"]
                    replies_data.append({
                        "author": reply_post.get("author", {}).get("displayName") or reply_post.get("author", {}).get("handle", "Unknown"),
                        "handle": reply_post.get("author", {}).get("handle", ""),
                        "text": reply_post.get("record", {}).get("text", ""),
                        "created_at": reply_post.get("record", {}).get("createdAt", ""),
                        "like_count": reply_post.get("likeCount", 0),
                        "reply_count": reply_post.get("replyCount", 0)
                    })
        
        return {
            "likes": post.get("likeCount", 0),
            "reposts": post.get("repostCount", 0),
            "replies": post.get("replyCount", 0),
            "replies_data": replies_data,
            "uri": uri,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }


def create_client(handle: str, app_password: str) -> BlueskyClient:
    """Create and authenticate a Bluesky client."""
    client = BlueskyClient()
    client.login(handle, app_password)
    return client


def format_hashtags(hashtags: List[str]) -> str:
    """Format hashtags with # prefix."""
    clean = [tag.strip().lstrip("#") for tag in hashtags if tag and tag.strip()]
    return " ".join(f"#{tag}" for tag in clean)


def post_to_bluesky(
    handle: str,
    app_password: str,
    content: str,
    hashtags: List[str] = None,
    image_paths: List[str] = None
) -> dict:
    """
    Post content to Bluesky.
    
    Returns:
        dict with 'uri', 'cid', and other response data
    """
    client = create_client(handle, app_password)
    
    # Ensure content is a string and not empty
    if not content or not isinstance(content, str):
        raise ValueError("Content must be a non-empty string")
    
    content = content.strip()
    
    # Build post text
    post_text = content
    if hashtags:
        hashtag_text = format_hashtags(hashtags)
        if hashtag_text:
            # Add hashtags if there's room (Bluesky limit is 300 graphemes)
            combined = f"{content}\n\n{hashtag_text}".strip()
            if len(combined) <= 300:
                post_text = combined
            else:
                # Try to fit as much content as possible with truncated hashtags
                available_space = 300 - len(content) - 2  # -2 for "\n\n"
                if available_space > 10:  # Only add hashtags if we have reasonable space
                    truncated_tags = hashtag_text[:available_space]
                    post_text = f"{content}\n\n{truncated_tags}".strip()
                else:
                    # Not enough space, truncate content to fit some hashtags
                    content_limit = 300 - len(hashtag_text) - 5  # -5 for "...\n\n"
                    if content_limit > 50:  # Only if we can fit meaningful content
                        truncated_content = content[:content_limit] + "..."
                        post_text = f"{truncated_content}\n\n{hashtag_text}".strip()
                    else:
                        # Just truncate content without hashtags
                        post_text = content[:297] + "..."
                logger.warning("Content or hashtags truncated to meet 300 character limit")
    
    logger.info(f"Post text length: {len(post_text)}")
    
    # Filter valid image paths
    valid_images = None
    if image_paths:
        valid_images = [img for img in image_paths if img and os.path.isfile(img)]
        if valid_images:
            logger.info(f"Uploading {len(valid_images)} image(s)...")
    
    return client.post(text=post_text, image_paths=valid_images)
