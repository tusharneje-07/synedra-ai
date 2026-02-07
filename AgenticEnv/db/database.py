"""
Database Manager for Multi-Agent AI Council
============================================

This module handles all database operations for the autonomous multi-agent system.
It creates and manages SQLite tables for agent memory, council decisions, and engagement metrics.

Schema:
-------
1. agent_memory: Stores individual agent memories and decisions
2. council_decisions: Stores final council decisions with reasoning traces
3. engagement_metrics: Stores post-performance metrics for learning

Author: AI Systems Engineer
Date: February 7, 2026
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages SQLite database operations for the AI Council system.
    
    Features:
    - Automatic table creation
    - Connection pooling
    - Transaction management
    - Error handling and logging
    """
    
    def __init__(self, db_path: str = "db/council.db"):
        """
        Initialize database manager and create tables if they don't exist.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure database directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        logger.info(f"Database initialized at: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Create a new database connection.
        
        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _initialize_database(self):
        """Create all required tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Table 1: Agent Memory
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    context TEXT,
                    decision TEXT,
                    outcome TEXT,
                    reasoning TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 2: Council Decisions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS council_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT UNIQUE NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    final_decision TEXT NOT NULL,
                    reasoning_trace TEXT NOT NULL,
                    weights_snapshot TEXT,
                    debate_rounds INTEGER,
                    consensus_score REAL,
                    agent_proposals TEXT,
                    conflicts_detected TEXT,
                    resolution_method TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 3: Engagement Metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS engagement_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT UNIQUE NOT NULL,
                    cycle_id TEXT,
                    platform TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    saves INTEGER DEFAULT 0,
                    views INTEGER DEFAULT 0,
                    sentiment_score REAL,
                    engagement_rate REAL,
                    virality_score REAL,
                    content_snippet TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cycle_id) REFERENCES council_decisions(cycle_id)
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_memory_name 
                ON agent_memory(agent_name, timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_council_cycle 
                ON council_decisions(cycle_id, timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_engagement_platform 
                ON engagement_metrics(platform, timestamp DESC)
            """)
            
            conn.commit()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    # ========================================
    # AGENT MEMORY OPERATIONS
    # ========================================
    
    def store_agent_memory(
        self,
        agent_name: str,
        context: str,
        decision: str,
        outcome: Optional[str] = None,
        reasoning: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Store an agent's memory/decision in the database.
        
        Args:
            agent_name: Name of the agent
            context: Context in which decision was made
            decision: The decision made by the agent
            outcome: Result/outcome of the decision
            reasoning: Agent's reasoning process
            metadata: Additional metadata as dictionary
            
        Returns:
            ID of the inserted record
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO agent_memory 
                (agent_name, context, decision, outcome, reasoning, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                agent_name,
                context,
                decision,
                outcome,
                reasoning,
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
            record_id = cursor.lastrowid
            logger.debug(f"Stored memory for {agent_name}, ID: {record_id}")
            return record_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error storing agent memory: {e}")
            raise
        finally:
            conn.close()
    
    def get_agent_memory(
        self,
        agent_name: str,
        limit: int = 10,
        context_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent memories for a specific agent.
        
        Args:
            agent_name: Name of the agent
            limit: Maximum number of records to retrieve
            context_filter: Optional context keyword filter
            
        Returns:
            List of memory records as dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if context_filter:
                cursor.execute("""
                    SELECT * FROM agent_memory
                    WHERE agent_name = ? AND context LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (agent_name, f"%{context_filter}%", limit))
            else:
                cursor.execute("""
                    SELECT * FROM agent_memory
                    WHERE agent_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (agent_name, limit))
            
            rows = cursor.fetchall()
            memories = []
            
            for row in rows:
                memory = dict(row)
                # Parse JSON metadata
                if memory.get('metadata'):
                    memory['metadata'] = json.loads(memory['metadata'])
                memories.append(memory)
            
            logger.debug(f"Retrieved {len(memories)} memories for {agent_name}")
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving agent memory: {e}")
            return []
        finally:
            conn.close()
    
    # ========================================
    # COUNCIL DECISION OPERATIONS
    # ========================================
    
    def store_council_decision(
        self,
        cycle_id: str,
        final_decision: Dict,
        reasoning_trace: List[Dict],
        weights_snapshot: Dict,
        debate_rounds: int,
        consensus_score: float,
        agent_proposals: List[Dict],
        conflicts_detected: Optional[List[str]] = None,
        resolution_method: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Store a complete council decision with all debate information.
        
        Args:
            cycle_id: Unique identifier for this decision cycle
            final_decision: Final decision output
            reasoning_trace: Full reasoning trace from all agents
            weights_snapshot: Agent voting weights at decision time
            debate_rounds: Number of debate rounds conducted
            consensus_score: Final consensus score (0-1)
            agent_proposals: All agent proposals
            conflicts_detected: List of detected conflicts
            resolution_method: How conflicts were resolved
            metadata: Additional metadata
            
        Returns:
            ID of the inserted record
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO council_decisions
                (cycle_id, final_decision, reasoning_trace, weights_snapshot,
                 debate_rounds, consensus_score, agent_proposals, 
                 conflicts_detected, resolution_method, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cycle_id,
                json.dumps(final_decision),
                json.dumps(reasoning_trace),
                json.dumps(weights_snapshot),
                debate_rounds,
                consensus_score,
                json.dumps(agent_proposals),
                json.dumps(conflicts_detected) if conflicts_detected else None,
                resolution_method,
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
            record_id = cursor.lastrowid
            logger.info(f"Stored council decision, Cycle ID: {cycle_id}")
            return record_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error storing council decision: {e}")
            raise
        finally:
            conn.close()
    
    def get_council_decision(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific council decision by cycle ID.
        
        Args:
            cycle_id: Unique cycle identifier
            
        Returns:
            Decision record as dictionary, or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM council_decisions
                WHERE cycle_id = ?
            """, (cycle_id,))
            
            row = cursor.fetchone()
            if row:
                decision = dict(row)
                # Parse JSON fields
                for field in ['final_decision', 'reasoning_trace', 'weights_snapshot',
                             'agent_proposals', 'conflicts_detected', 'metadata']:
                    if decision.get(field):
                        decision[field] = json.loads(decision[field])
                return decision
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving council decision: {e}")
            return None
        finally:
            conn.close()
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent council decisions.
        
        Args:
            limit: Maximum number of decisions to retrieve
            
        Returns:
            List of decision records
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM council_decisions
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            decisions = []
            
            for row in rows:
                decision = dict(row)
                # Parse JSON fields
                for field in ['final_decision', 'reasoning_trace', 'weights_snapshot',
                             'agent_proposals', 'conflicts_detected', 'metadata']:
                    if decision.get(field):
                        decision[field] = json.loads(decision[field])
                decisions.append(decision)
            
            return decisions
            
        except Exception as e:
            logger.error(f"Error retrieving recent decisions: {e}")
            return []
        finally:
            conn.close()
    
    # ========================================
    # ENGAGEMENT METRICS OPERATIONS
    # ========================================
    
    def store_engagement_metrics(
        self,
        post_id: str,
        platform: str,
        cycle_id: Optional[str] = None,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        saves: int = 0,
        views: int = 0,
        sentiment_score: Optional[float] = None,
        engagement_rate: Optional[float] = None,
        virality_score: Optional[float] = None,
        content_snippet: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Store engagement metrics for a post.
        
        Args:
            post_id: Unique post identifier
            platform: Social media platform
            cycle_id: Associated decision cycle ID
            likes, comments, shares, saves, views: Engagement metrics
            sentiment_score: Overall sentiment score
            engagement_rate: Calculated engagement rate
            virality_score: Calculated virality score
            content_snippet: Preview of content
            metadata: Additional metadata
            
        Returns:
            ID of the inserted record
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO engagement_metrics
                (post_id, platform, cycle_id, likes, comments, shares, saves,
                 views, sentiment_score, engagement_rate, virality_score,
                 content_snippet, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id,
                platform,
                cycle_id,
                likes,
                comments,
                shares,
                saves,
                views,
                sentiment_score,
                engagement_rate,
                virality_score,
                content_snippet,
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
            record_id = cursor.lastrowid
            logger.debug(f"Stored engagement metrics for post: {post_id}")
            return record_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error storing engagement metrics: {e}")
            raise
        finally:
            conn.close()
    
    def get_platform_metrics(
        self,
        platform: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve engagement metrics for a specific platform.
        
        Args:
            platform: Social media platform
            limit: Maximum number of records
            
        Returns:
            List of engagement metric records
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM engagement_metrics
                WHERE platform = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (platform, limit))
            
            rows = cursor.fetchall()
            metrics = []
            
            for row in rows:
                metric = dict(row)
                if metric.get('metadata'):
                    metric['metadata'] = json.loads(metric['metadata'])
                metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error retrieving platform metrics: {e}")
            return []
        finally:
            conn.close()
    
    def get_performance_analytics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get aggregated performance analytics for the past N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with analytics data
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    platform,
                    COUNT(*) as total_posts,
                    AVG(likes) as avg_likes,
                    AVG(comments) as avg_comments,
                    AVG(shares) as avg_shares,
                    AVG(engagement_rate) as avg_engagement_rate,
                    AVG(sentiment_score) as avg_sentiment,
                    SUM(views) as total_views
                FROM engagement_metrics
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY platform
            """, (days,))
            
            rows = cursor.fetchall()
            
            analytics = {
                "period_days": days,
                "platforms": []
            }
            
            for row in rows:
                analytics["platforms"].append(dict(row))
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error calculating performance analytics: {e}")
            return {"period_days": days, "platforms": []}
        finally:
            conn.close()
    
    # ========================================
    # UTILITY OPERATIONS
    # ========================================
    
    def cleanup_old_records(self, days_to_keep: int = 90):
        """
        Clean up old records to prevent database bloat.
        
        Args:
            days_to_keep: Number of days of data to retain
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Clean old agent memories
            cursor.execute("""
                DELETE FROM agent_memory
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            """, (days_to_keep,))
            
            # Clean old engagement metrics (keep decisions longer)
            cursor.execute("""
                DELETE FROM engagement_metrics
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            """, (days_to_keep,))
            
            conn.commit()
            logger.info(f"Cleaned up records older than {days_to_keep} days")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error cleaning up old records: {e}")
        finally:
            conn.close()
    
    def get_database_stats(self) -> Dict[str, int]:
        """
        Get statistics about the database.
        
        Returns:
            Dictionary with table row counts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            for table in ['agent_memory', 'council_decisions', 'engagement_metrics']:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = cursor.fetchone()['count']
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
        finally:
            conn.close()


# Singleton instance
_db_instance: Optional[DatabaseManager] = None


def get_database(db_path: str = "db/council.db") -> DatabaseManager:
    """
    Get or create database manager singleton instance.
    
    Args:
        db_path: Path to database file
        
    Returns:
        DatabaseManager instance
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseManager(db_path)
    
    return _db_instance
