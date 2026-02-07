"""
Settings Routes - API endpoints for managing settings
"""

from flask import Blueprint, jsonify, request
from database import get_db
import json

settings_bp = Blueprint('settings', __name__)

# ===== AGENT CONFIGURATION =====

@settings_bp.route('/agents', methods=['GET'])
def get_agents():
    """Get all agent configurations"""
    agents = [
        {'name': 'TrendAgent', 'role': 'TrendPulse Strategist', 'temperature': 0.95, 'enabled': True},
        {'name': 'BrandAgent', 'role': 'BrandGuardian Architect', 'temperature': 0.95, 'enabled': True},
        {'name': 'ComplianceAgent', 'role': 'Policy Compliance Guardian', 'temperature': 0.95, 'enabled': True},
        {'name': 'RiskAgent', 'role': 'Reputation Shield Officer', 'temperature': 0.95, 'enabled': True},
        {'name': 'EngagementAgent', 'role': 'Community Magnet Strategist', 'temperature': 0.95, 'enabled': True},
        {'name': 'CMOAgent', 'role': 'Chief Marketing Officer', 'temperature': 0.75, 'enabled': True}
    ]
    
    return jsonify({
        'success': True,
        'agents': agents
    })

@settings_bp.route('/agents/<agent_name>', methods=['GET'])
def get_agent(agent_name):
    """Get specific agent configuration"""
    agents = {
        'TrendAgent': {'name': 'TrendAgent', 'role': 'TrendPulse Strategist', 'temperature': 0.95, 'enabled': True},
        'BrandAgent': {'name': 'BrandAgent', 'role': 'BrandGuardian Architect', 'temperature': 0.95, 'enabled': True},
        'ComplianceAgent': {'name': 'ComplianceAgent', 'role': 'Policy Compliance Guardian', 'temperature': 0.95, 'enabled': True},
        'RiskAgent': {'name': 'RiskAgent', 'role': 'Reputation Shield Officer', 'temperature': 0.95, 'enabled': True},
        'EngagementAgent': {'name': 'EngagementAgent', 'role': 'Community Magnet Strategist', 'temperature': 0.95, 'enabled': True},
        'CMOAgent': {'name': 'CMOAgent', 'role': 'Chief Marketing Officer', 'temperature': 0.75, 'enabled': True}
    }
    
    if agent_name in agents:
        return jsonify({
            'success': True,
            'agent': agents[agent_name]
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Agent not found'
        }), 404

@settings_bp.route('/agents/<agent_name>', methods=['PUT'])
def update_agent(agent_name):
    """Update agent configuration"""
    data = request.json
    
    # In a real implementation, you would save this to a config file or database
    # For now, we'll just return success
    
    return jsonify({
        'success': True,
        'message': f'Agent {agent_name} updated successfully'
    })

# ===== API KEY POOL =====

@settings_bp.route('/api-keys', methods=['GET'])
def get_api_keys():
    """Get all API keys in the pool"""
    db = get_db()
    cursor = db.cursor()
    
    # Create api_keys table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT NOT NULL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('SELECT id, api_key, active FROM api_keys ORDER BY id')
    rows = cursor.fetchall()
    
    keys = []
    for row in rows:
        keys.append({
            'id': row[0],
            'key': row[1],
            'active': bool(row[2])
        })
    
    return jsonify({
        'success': True,
        'keys': keys
    })

@settings_bp.route('/api-keys', methods=['POST'])
def add_api_key():
    """Add a new API key to the pool"""
    data = request.json
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'API key is required'
        }), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT NOT NULL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if key already exists
    cursor.execute('SELECT id FROM api_keys WHERE api_key = ?', (api_key,))
    if cursor.fetchone():
        return jsonify({
            'success': False,
            'error': 'API key already exists'
        }), 400
    
    cursor.execute('INSERT INTO api_keys (api_key, active) VALUES (?, 1)', (api_key,))
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'API key added successfully'
    })

@settings_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
def remove_api_key(key_id):
    """Remove an API key from the pool"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('DELETE FROM api_keys WHERE id = ?', (key_id,))
    db.commit()
    
    if cursor.rowcount > 0:
        return jsonify({
            'success': True,
            'message': 'API key removed successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'API key not found'
        }), 404

# ===== MODEL SELECTION =====

@settings_bp.route('/model', methods=['GET'])
def get_model():
    """Get current model selection"""
    db = get_db()
    cursor = db.cursor()
    
    # Create settings table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('current_model',))
    row = cursor.fetchone()
    
    model = row[0] if row else 'llama-3.3-70b-versatile'
    
    return jsonify({
        'success': True,
        'model': model
    })

@settings_bp.route('/model', methods=['PUT'])
def update_model():
    """Update model selection"""
    data = request.json
    model = data.get('model')
    
    if not model:
        return jsonify({
            'success': False,
            'error': 'Model is required'
        }), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value, updated_at)
        VALUES ('current_model', ?, CURRENT_TIMESTAMP)
    ''', (model,))
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Model updated successfully',
        'model': model
    })
