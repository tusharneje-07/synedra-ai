"""
Configuration Manager for Multi-Agent AI Council
=================================================

This module manages all configuration settings for the autonomous multi-agent system.
It loads environment variables, validates settings, and provides typed configuration objects.

Author: AI Systems Engineer
Date: February 7, 2026
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic for validation and type safety.
    """
    
    # ========================================
    # GROQ API Configuration
    # ========================================
    groq_api_key: str = Field(
        default="",
        description="GROQ API key for LLM access"
    )
    
    llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="GROQ LLM model to use"
    )
    
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Temperature for LLM responses (0-1)"
    )
    
    max_tokens: int = Field(
        default=4096,
        gt=0,
        description="Maximum tokens per LLM response"
    )
    
    # ========================================
    # Database Configuration
    # ========================================
    database_path: str = Field(
        default="db/council.db",
        description="Path to SQLite database file"
    )
    
    # ========================================
    # Agent Configuration
    # ========================================
    agent_definitions_path: str = Field(
        default="../Base Planning",
        description="Path to agent definition markdown files"
    )
    
    # ========================================
    # Debate System Configuration
    # ========================================
    max_debate_rounds: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of debate rounds before arbitration"
    )
    
    consensus_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum consensus score to accept decision (0-1)"
    )
    
    # ========================================
    # Memory Configuration
    # ========================================
    memory_context_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of past decisions to keep in active memory"
    )
    
    # ========================================
    # Pipeline Configuration
    # ========================================
    trend_monitor_interval: int = Field(
        default=60,
        ge=1,
        description="Trend monitoring interval in minutes"
    )
    
    autonomous_mode: bool = Field(
        default=False,
        description="Enable fully autonomous operation"
    )
    
    # ========================================
    # Logging Configuration
    # ========================================
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    log_file: str = Field(
        default="logs/council.log",
        description="Path to log file"
    )
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    def get_absolute_database_path(self) -> Path:
        """
        Get absolute path to database file.
        
        Returns:
            Absolute Path object
        """
        base_path = Path(__file__).parent.parent
        return base_path / self.database_path
    
    def get_absolute_agent_definitions_path(self) -> Path:
        """
        Get absolute path to agent definitions directory.
        
        Returns:
            Absolute Path object
        """
        base_path = Path(__file__).parent.parent
        return base_path / self.agent_definitions_path
    
    def get_absolute_log_path(self) -> Path:
        """
        Get absolute path to log file.
        
        Returns:
            Absolute Path object
        """
        base_path = Path(__file__).parent.parent
        return base_path / self.log_file
    
    def validate_api_key(self) -> bool:
        """
        Validate that API key is set and not a placeholder.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.groq_api_key:
            return False
        if self.groq_api_key == "your_groq_api_key_here":
            return False
        if len(self.groq_api_key) < 20:
            return False
        return True
    
    def get_agent_definition_file(self, agent_type: str) -> Optional[Path]:
        """
        Get path to specific agent definition file.
        
        Args:
            agent_type: Type of agent (trend, engagement, brand, risk, compliance, arbitrator)
            
        Returns:
            Path to markdown file, or None if not found
        """
        agent_file_map = {
            "trend": "TrendAgent.md",
            "engagement": "EngagementAgent.md",
            "brand": "BrandAgent.md",
            "risk": "RiskAgent.md",
            "compliance": "ComplianceAgent.md",
            "arbitrator": "CMOAgent.md"
        }
        
        if agent_type not in agent_file_map:
            return None
        
        file_path = self.get_absolute_agent_definitions_path() / agent_file_map[agent_type]
        
        if file_path.exists():
            return file_path
        return None


class AgentWeights:
    """
    Default voting weights for each agent in the council.
    
    These weights can be dynamically adjusted based on performance.
    """
    
    TREND_AGENT: float = 0.20
    ENGAGEMENT_AGENT: float = 0.20
    BRAND_AGENT: float = 0.25
    RISK_AGENT: float = 0.20
    COMPLIANCE_AGENT: float = 0.15
    
    @classmethod
    def get_all_weights(cls) -> dict:
        """Get all agent weights as dictionary."""
        return {
            "trend": cls.TREND_AGENT,
            "engagement": cls.ENGAGEMENT_AGENT,
            "brand": cls.BRAND_AGENT,
            "risk": cls.RISK_AGENT,
            "compliance": cls.COMPLIANCE_AGENT
        }
    
    @classmethod
    def validate_weights(cls, weights: dict) -> bool:
        """
        Validate that weights sum to approximately 1.0.
        
        Args:
            weights: Dictionary of agent weights
            
        Returns:
            True if valid, False otherwise
        """
        total = sum(weights.values())
        return abs(total - 1.0) < 0.01


class PlatformConfig:
    """
    Configuration for different social media platforms.
    """
    
    INSTAGRAM = {
        "max_caption_length": 2200,
        "max_hashtags": 30,
        "optimal_hashtags": 10,
        "max_video_duration": 90,  # seconds for Reels
        "supported_formats": ["image", "video", "carousel"]
    }
    
    TWITTER = {
        "max_text_length": 280,
        "max_hashtags": 10,
        "optimal_hashtags": 2,
        "max_video_duration": 140,
        "supported_formats": ["text", "image", "video"]
    }
    
    LINKEDIN = {
        "max_text_length": 3000,
        "max_hashtags": 10,
        "optimal_hashtags": 3,
        "max_video_duration": 600,
        "supported_formats": ["text", "image", "video", "article"]
    }
    
    YOUTUBE = {
        "max_title_length": 100,
        "max_description_length": 5000,
        "max_tags": 500,
        "optimal_tags": 15,
        "supported_formats": ["video", "short"]
    }
    
    @classmethod
    def get_platform_config(cls, platform: str) -> dict:
        """
        Get configuration for specific platform.
        
        Args:
            platform: Platform name (case-insensitive)
            
        Returns:
            Platform configuration dictionary
        """
        platform_upper = platform.upper()
        return getattr(cls, platform_upper, {})


def setup_logging(settings: Settings):
    """
    Configure logging for the application.
    
    Args:
        settings: Settings object with logging configuration
    """
    # Create logs directory if it doesn't exist
    log_path = settings.get_absolute_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info("Logging configured successfully")


# Singleton instance
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create settings singleton instance.
    
    Returns:
        Settings object
    """
    global _settings_instance
    
    if _settings_instance is None:
        _settings_instance = Settings()
    
    return _settings_instance


def validate_environment() -> tuple[bool, list[str]]:
    """
    Validate that all required environment variables and files are present.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    settings = get_settings()
    
    # Check API key
    if not settings.validate_api_key():
        errors.append("GROQ_API_KEY is not set or invalid. Please set it in .env file.")
    
    # Check agent definition files
    agent_types = ["trend", "engagement", "brand", "risk", "compliance", "arbitrator"]
    for agent_type in agent_types:
        file_path = settings.get_agent_definition_file(agent_type)
        if file_path is None or not file_path.exists():
            errors.append(f"Agent definition file not found for {agent_type}")
    
    # Check database directory
    db_path = settings.get_absolute_database_path()
    if not db_path.parent.exists():
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create database directory: {e}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


if __name__ == "__main__":
    # Test configuration loading
    print("Testing configuration...")
    
    settings = get_settings()
    print(f"\nLoaded settings:")
    print(f"  LLM Model: {settings.llm_model}")
    print(f"  Max Debate Rounds: {settings.max_debate_rounds}")
    print(f"  Consensus Threshold: {settings.consensus_threshold}")
    print(f"  Database Path: {settings.get_absolute_database_path()}")
    print(f"  Agent Definitions Path: {settings.get_absolute_agent_definitions_path()}")
    
    # Validate environment
    is_valid, errors = validate_environment()
    print(f"\nEnvironment validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
    
    # Test agent weights
    print(f"\nAgent Weights:")
    for agent, weight in AgentWeights.get_all_weights().items():
        print(f"  {agent}: {weight}")
