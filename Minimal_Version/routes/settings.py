"""
Settings Routes - API endpoints for managing settings
"""

from flask import Blueprint, jsonify, request
import json
import logging

settings_bp = Blueprint('settings', __name__)
logger = logging.getLogger(__name__)

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

import os
from pathlib import Path

API_KEYS_FILE = Path('apiconfig/apis.json')

def load_api_keys():
    """Load API keys from JSON file"""
    if not API_KEYS_FILE.exists():
        API_KEYS_FILE.parent.mkdir(exist_ok=True)
        return []
    
    try:
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_api_keys(keys):
    """Save API keys to JSON file"""
    API_KEYS_FILE.parent.mkdir(exist_ok=True)
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

@settings_bp.route('/api-keys', methods=['GET'])
def get_api_keys():
    """Get all API keys in the pool"""
    keys = load_api_keys()
    
    return jsonify({
        'success': True,
        'keys': keys
    })

@settings_bp.route('/api-keys', methods=['POST'])
def add_api_key():
    """Add a new API key to the pool"""
    data = request.json
    api_key = data.get('api_key')
    key_name = data.get('name', 'Unnamed Key')
    
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'API key is required'
        }), 400
    
    keys = load_api_keys()
    
    # Check if key already exists
    if any(k['key'] == api_key for k in keys):
        return jsonify({
            'success': False,
            'error': 'API key already exists'
        }), 400
    
    # Generate new ID
    new_id = max([k['id'] for k in keys], default=0) + 1
    
    # Add new key
    new_key = {
        'id': new_id,
        'name': key_name,
        'key': api_key,
        'active': True
    }
    
    keys.append(new_key)
    save_api_keys(keys)
    
    return jsonify({
        'success': True,
        'message': 'API key added successfully',
        'key': new_key
    })

@settings_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
def remove_api_key(key_id):
    """Remove an API key from the pool"""
    keys = load_api_keys()
    
    # Filter out the key to remove
    updated_keys = [k for k in keys if k['id'] != key_id]
    
    if len(updated_keys) < len(keys):
        save_api_keys(updated_keys)
        return jsonify({
            'success': True,
            'message': 'API key removed successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'API key not found'
        }), 404

@settings_bp.route('/api-keys/test-all', methods=['POST'])
def test_all_api_keys():
    """Test all API keys and update their active status"""
    # Use the api_manager function which properly tests and updates status
    from utils.api_manager import test_all_keys_and_update_status
    
    logger.info("Testing all API keys from Settings...")
    result = test_all_keys_and_update_status()
    
    # Reload keys to get updated status
    updated_keys = load_api_keys()
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'active_count': result['active_count'],
            'total_count': result['total_count'],
            'results': result['results'],
            'keys': updated_keys
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('message', 'Failed to test API keys'),
            'keys': updated_keys
        })

# ===== MODEL SELECTION =====

MODEL_SETTINGS_FILE = Path('config/model_settings.json')

def load_model_settings():
    """Load model settings from JSON file"""
    if not MODEL_SETTINGS_FILE.exists():
        MODEL_SETTINGS_FILE.parent.mkdir(exist_ok=True)
        return {'current_model': 'llama-3.3-70b-versatile'}
    
    try:
        with open(MODEL_SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'current_model': 'llama-3.3-70b-versatile'}

def save_model_settings(settings):
    """Save model settings to JSON file"""
    MODEL_SETTINGS_FILE.parent.mkdir(exist_ok=True)
    with open(MODEL_SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

@settings_bp.route('/model', methods=['GET'])
def get_model():
    """Get current model selection"""
    settings = load_model_settings()
    
    return jsonify({
        'success': True,
        'model': settings.get('current_model', 'llama-3.3-70b-versatile')
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
    
    settings = load_model_settings()
    settings['current_model'] = model
    save_model_settings(settings)
    
    return jsonify({
        'success': True,
        'message': 'Model updated successfully',
        'model': model
    })
