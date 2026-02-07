"""
SQLite Database Management for Minimal Version
Handles all database operations for brand configs, posts, debates, and generated content
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class Database:
    def __init__(self, db_path: str = "database/minimal_version.db"):
        """Initialize database connection and create tables if they don't exist"""
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Create all necessary tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Brands table - stores brand configuration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_name TEXT NOT NULL UNIQUE,
                brand_tone TEXT NOT NULL,
                brand_description TEXT NOT NULL,
                product_list TEXT NOT NULL,
                target_audience TEXT NOT NULL,
                brand_keywords TEXT NOT NULL,
                messaging_guidelines TEXT NOT NULL,
                social_platforms TEXT NOT NULL,
                posting_frequency TEXT NOT NULL,
                competitors TEXT NOT NULL,
                market_segment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Post inputs table - stores user input for post creation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_id INTEGER NOT NULL,
                post_topic TEXT NOT NULL,
                post_objective TEXT NOT NULL,
                target_platform TEXT NOT NULL,
                content_type TEXT NOT NULL,
                key_message TEXT NOT NULL,
                call_to_action TEXT,
                special_requirements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (brand_id) REFERENCES brands (id)
            )
        ''')
        
        # Debates table - stores agent debate logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_input_id INTEGER NOT NULL,
                agent_name TEXT NOT NULL,
                agent_role TEXT NOT NULL,
                analysis TEXT NOT NULL,
                score INTEGER,
                recommendation TEXT NOT NULL,
                vote TEXT NOT NULL,
                reasoning TEXT NOT NULL,
                concerns TEXT,
                debate_round INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_input_id) REFERENCES post_inputs (id)
            )
        ''')
        
        # Generated posts table - stores final generated posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_input_id INTEGER NOT NULL,
                variation_number INTEGER NOT NULL,
                post_title TEXT NOT NULL,
                post_content TEXT NOT NULL,
                hashtags TEXT NOT NULL,
                image_prompt TEXT NOT NULL,
                final_score REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_input_id) REFERENCES post_inputs (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ===== BRAND OPERATIONS =====
    
    def create_brand(self, brand_data: Dict[str, str]) -> int:
        """Create a new brand configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO brands (
                brand_name, brand_tone, brand_description, product_list,
                target_audience, brand_keywords, messaging_guidelines,
                social_platforms, posting_frequency, competitors, market_segment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            brand_data['brand_name'],
            brand_data['brand_tone'],
            brand_data['brand_description'],
            brand_data['product_list'],
            brand_data['target_audience'],
            brand_data['brand_keywords'],
            brand_data['messaging_guidelines'],
            brand_data['social_platforms'],
            brand_data['posting_frequency'],
            brand_data['competitors'],
            brand_data['market_segment']
        ))
        
        brand_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return brand_id
    
    def get_brand(self, brand_id: int) -> Optional[Dict]:
        """Get brand by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM brands WHERE id = ?', (brand_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_brand_by_name(self, brand_name: str) -> Optional[Dict]:
        """Get brand by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM brands WHERE brand_name = ?', (brand_name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_brands(self) -> List[Dict]:
        """Get all brands"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM brands ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_brand(self, brand_id: int, brand_data: Dict[str, str]) -> bool:
        """Update brand configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE brands SET
                brand_tone = ?, brand_description = ?, product_list = ?,
                target_audience = ?, brand_keywords = ?, messaging_guidelines = ?,
                social_platforms = ?, posting_frequency = ?, competitors = ?,
                market_segment = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            brand_data['brand_tone'],
            brand_data['brand_description'],
            brand_data['product_list'],
            brand_data['target_audience'],
            brand_data['brand_keywords'],
            brand_data['messaging_guidelines'],
            brand_data['social_platforms'],
            brand_data['posting_frequency'],
            brand_data['competitors'],
            brand_data['market_segment'],
            brand_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # ===== POST INPUT OPERATIONS =====
    
    def create_post_input(self, post_data: Dict[str, Any]) -> int:
        """Create a new post input"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO post_inputs (
                brand_id, post_topic, post_objective, target_platform,
                content_type, key_message, call_to_action, special_requirements
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post_data['brand_id'],
            post_data['post_topic'],
            post_data['post_objective'],
            post_data['target_platform'],
            post_data['content_type'],
            post_data['key_message'],
            post_data.get('call_to_action', ''),
            post_data.get('special_requirements', '')
        ))
        
        post_input_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return post_input_id
    
    def get_post_input(self, post_input_id: int) -> Optional[Dict]:
        """Get post input by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM post_inputs WHERE id = ?', (post_input_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_posts_by_brand(self, brand_id: int) -> List[Dict]:
        """Get all post inputs for a brand"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM post_inputs WHERE brand_id = ? ORDER BY created_at DESC', (brand_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ===== DEBATE OPERATIONS =====
    
    def create_debate_entry(self, debate_data: Dict[str, Any]) -> int:
        """Create a new debate entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO debates (
                post_input_id, agent_name, agent_role, analysis, score,
                recommendation, vote, reasoning, concerns, debate_round
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            debate_data['post_input_id'],
            debate_data['agent_name'],
            debate_data['agent_role'],
            debate_data['analysis'],
            debate_data.get('score'),
            debate_data['recommendation'],
            debate_data['vote'],
            debate_data['reasoning'],
            debate_data.get('concerns', ''),
            debate_data.get('debate_round', 1)
        ))
        
        debate_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return debate_id
    
    def get_debates_for_post(self, post_input_id: int) -> List[Dict]:
        """Get all debate entries for a post input"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM debates 
            WHERE post_input_id = ? 
            ORDER BY debate_round ASC, created_at ASC
        ''', (post_input_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ===== GENERATED POST OPERATIONS =====
    
    def create_generated_post(self, post_data: Dict[str, Any]) -> int:
        """Create a new generated post"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO generated_posts (
                post_input_id, variation_number, post_title, post_content,
                hashtags, image_prompt, final_score, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post_data['post_input_id'],
            post_data['variation_number'],
            post_data['post_title'],
            post_data['post_content'],
            post_data['hashtags'],
            post_data['image_prompt'],
            post_data.get('final_score'),
            json.dumps(post_data.get('metadata', {}))
        ))
        
        generated_post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return generated_post_id
    
    def get_generated_posts(self, post_input_id: int) -> List[Dict]:
        """Get all generated posts for a post input"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM generated_posts 
            WHERE post_input_id = ? 
            ORDER BY variation_number ASC
        ''', (post_input_id,))
        rows = cursor.fetchall()
        conn.close()
        
        posts = []
        for row in rows:
            post = dict(row)
            post['metadata'] = json.loads(post['metadata']) if post['metadata'] else {}
            posts.append(post)
        
        return posts
    
    def delete_post_and_related(self, post_input_id: int) -> bool:
        """Delete a post input and all related data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete in order: generated_posts, debates, post_inputs
        cursor.execute('DELETE FROM generated_posts WHERE post_input_id = ?', (post_input_id,))
        cursor.execute('DELETE FROM debates WHERE post_input_id = ?', (post_input_id,))
        cursor.execute('DELETE FROM post_inputs WHERE id = ?', (post_input_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success


# Singleton instance
_db_instance = None

def get_db() -> Database:
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
