"""
Flask Application for Minimal Version Multi-Agent Social Media Post Generator
Main entry point with all routes and API endpoints
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from typing import Dict, List, Any
from datetime import datetime

# Import database
from database import get_db

# Import blueprints
from routes.settings import settings_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# In-memory storage for live debate progress
# Format: {post_input_id: {'messages': [...], 'status': 'running/complete', 'last_update': timestamp}}
live_debate_updates = {}

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'minimal-version-secret-key-2026')
CORS(app)  # Enable CORS for frontend communication

# Register blueprints
app.register_blueprint(settings_bp, url_prefix='/api/settings')

# Initialize database
db = get_db()

# ========================================
# HTML ROUTES (Frontend Pages)
# ========================================

@app.route('/')
def index():
    """Home page - Brand configuration"""
    return render_template('index.html')

@app.route('/create-post')
def create_post():
    """Create post page - Post input form"""
    return render_template('create-post.html')

@app.route('/debate/<int:post_id>')
def debate(post_id):
    """Debate page - Show agent debates"""
    return render_template('debate.html', post_id=post_id)

@app.route('/results/<int:post_id>')
def results(post_id):
    """Results page - Display generated posts"""
    return render_template('results.html', post_id=post_id)

@app.route('/saved-posts')
def saved_posts():
    """Saved posts page - View all saved posts"""
    return render_template('saved-posts.html')

@app.route('/history')
def history():
    """History page - View all past generations"""
    return render_template('history.html')

@app.route('/settings')
def settings():
    """Settings page - Configuration management"""
    return render_template('settings.html')

# ========================================
# API ROUTES - Brand Management
# ========================================

@app.route('/api/brands', methods=['GET'])
def get_brands():
    """Get all brands"""
    try:
        brands = db.get_all_brands()
        return jsonify({
            'success': True,
            'brands': brands
        })
    except Exception as e:
        logger.error(f"Error fetching brands: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/brands/<int:brand_id>', methods=['GET'])
def get_brand(brand_id):
    """Get brand by ID"""
    try:
        brand = db.get_brand(brand_id)
        if brand:
            return jsonify({
                'success': True,
                'brand': brand
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
    except Exception as e:
        logger.error(f"Error fetching brand {brand_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/brands', methods=['POST'])
def create_brand():
    """Create a new brand configuration"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = [
            'brand_name', 'brand_tone', 'brand_description', 'product_list',
            'target_audience', 'brand_keywords', 'messaging_guidelines',
            'social_platforms', 'posting_frequency', 'competitors', 'market_segment'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create brand
        brand_id = db.create_brand(data)
        brand = db.get_brand(brand_id)
        
        return jsonify({
            'success': True,
            'message': 'Brand created successfully',
            'brand': brand
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating brand: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/brands/<int:brand_id>', methods=['PUT'])
def update_brand(brand_id):
    """Update brand configuration"""
    try:
        data = request.json
        
        # Check if brand exists
        existing_brand = db.get_brand(brand_id)
        if not existing_brand:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
        
        # Update brand
        success = db.update_brand(brand_id, data)
        
        if success:
            brand = db.get_brand(brand_id)
            return jsonify({
                'success': True,
                'message': 'Brand updated successfully',
                'brand': brand
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update brand'
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating brand {brand_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========================================
# API ROUTES - Post Input Management
# ========================================

@app.route('/api/post-inputs', methods=['POST'])
def create_post_input():
    """Create a new post input"""
    try:
        data = request.json
        
        # Validate required fields (simplified - only 3 fields needed)
        required_fields = ['brand_id', 'post_topic', 'target_platform']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Verify brand exists
        brand = db.get_brand(data['brand_id'])
        if not brand:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
        
        # Auto-populate missing fields that agents will determine
        # Agents will handle objective, content type, and key message based on topic
        if 'post_objective' not in data or not data['post_objective']:
            data['post_objective'] = 'Engagement'  # Default, agents will optimize
        
        if 'content_type' not in data or not data['content_type']:
            data['content_type'] = 'General'  # Agents will determine best type
        
        if 'key_message' not in data or not data['key_message']:
            data['key_message'] = data['post_topic']  # Use topic as base message
        
        # Optional fields - keep if provided
        if 'target_cta' not in data:
            data['target_cta'] = ''
        
        if 'trending_topics' not in data:
            data['trending_topics'] = ''
        
        # Create post input
        post_input_id = db.create_post_input(data)
        post_input = db.get_post_input(post_input_id)
        
        return jsonify({
            'success': True,
            'message': 'Post input created successfully',
            'post_input': post_input,
            'post_input_id': post_input_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating post input: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/post-inputs/<int:post_input_id>', methods=['GET'])
def get_post_input(post_input_id):
    """Get post input by ID"""
    try:
        post_input = db.get_post_input(post_input_id)
        if post_input:
            return jsonify({
                'success': True,
                'post_input': post_input
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Post input not found'
            }), 404
    except Exception as e:
        logger.error(f"Error fetching post input {post_input_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/brands/<int:brand_id>/posts', methods=['GET'])
def get_brand_posts(brand_id):
    """Get all posts for a brand"""
    try:
        posts = db.get_posts_by_brand(brand_id)
        return jsonify({
            'success': True,
            'posts': posts
        })
    except Exception as e:
        logger.error(f"Error fetching posts for brand {brand_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========================================
# API ROUTES - Debate Process
# ========================================

@app.route('/api/debates/<int:post_input_id>/live-progress', methods=['GET'])
def get_live_debate_progress(post_input_id):
    """
    Get live debate progress for real-time updates
    """
    try:
        if post_input_id not in live_debate_updates:
            return jsonify({
                'success': True,
                'messages': [],
                'status': 'not_started'
            })
        
        progress = live_debate_updates[post_input_id]
        return jsonify({
            'success': True,
            'messages': progress.get('messages', []),
            'status': progress.get('status', 'running'),
            'last_update': progress.get('last_update')
        })
        
    except Exception as e:
        logger.error(f"Error getting live debate progress: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debates/current-api-key', methods=['GET'])
def get_current_api_key():
    """
    Get the name of the currently active API key
    """
    try:
        from utils.api_manager import get_active_api_key, get_current_key_name
        
        api_key = get_active_api_key()
        if api_key:
            key_name = get_current_key_name(api_key)
            return jsonify({
                'success': True,
                'api_key_name': key_name
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No active API key available'
            }), 503
            
    except Exception as e:
        logger.error(f"Error getting current API key: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debates/start', methods=['POST'])
def start_debate():
    """
    Start the debate process for a post input and generate posts
    """
    try:
        from utils.debate_orchestrator import DebateOrchestrator
        from utils.post_generator import PostGenerator
        
        data = request.json
        post_input_id = data.get('post_input_id')
        
        if not post_input_id:
            return jsonify({
                'success': False,
                'error': 'post_input_id is required'
            }), 400
        
        # Verify post input exists
        post_input = db.get_post_input(post_input_id)
        if not post_input:
            return jsonify({
                'success': False,
                'error': 'Post input not found'
            }), 404
        
        # Get brand information
        brand = db.get_brand(post_input['brand_id'])
        if not brand:
            return jsonify({
                'success': False,
                'error': 'Brand not found'
            }), 404
        
        # Initialize live debate updates for this post
        if post_input_id not in live_debate_updates:
            live_debate_updates[post_input_id] = {
                'messages': [],
                'status': 'running'
            }
        
        # Define callback to push updates to frontend
        def push_live_update(update):
            live_debate_updates[post_input_id]['messages'].append(update)
        
        # Run debate process
        logger.info(f"Starting debate for post_input_id: {post_input_id}")
        orchestrator = DebateOrchestrator()
        
        # CRITICAL: Set the callback BEFORE running debate
        orchestrator.set_live_updates_callback(push_live_update)
        
        debate_results = orchestrator.run_debate(post_input_id, brand, post_input)
        
        if not debate_results.get('success'):
            error_msg = debate_results.get('error', '')
            # Check if it's a rate limit error
            if 'rate_limit_exceeded' in str(error_msg) or 'Rate limit reached' in str(error_msg):
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'error_type': 'rate_limit',
                    'details': 'Groq API rate limit reached. Please try again in 20-30 minutes or upgrade your plan.',
                    'message': 'API Rate Limit Exceeded - Please wait and try again later'
                }), 429
            return jsonify({
                'success': False,
                'error': 'Debate process failed',
                'details': debate_results.get('error')
            }), 500
        
        # Generate posts if approved or conditional
        final_vote = debate_results.get('final_vote')
        generated_posts = []
        
        if final_vote in ['approve', 'conditional']:
            logger.info("Generating posts based on CMO decision")
            generator = PostGenerator()
            generated_posts = generator.generate_posts(post_input_id, debate_results)
        
        # Log the response data for debugging
        api_key_name = debate_results.get('api_key_name', 'Unknown')
        conversation_log = debate_results.get('conversation_log', [])
        logger.info(f"📤 Returning to frontend - API Key: {api_key_name}, Conversation Messages: {len(conversation_log)}")
        
        # Mark debate as complete
        if post_input_id in live_debate_updates:
            live_debate_updates[post_input_id]['status'] = 'complete'
            live_debate_updates[post_input_id]['last_update'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'post_input_id': post_input_id,
            'final_vote': final_vote,
            'cmo_decision': debate_results.get('cmo_decision'),
            'generated_posts_count': len(generated_posts),
            'message': f'Debate complete - {final_vote}. Generated {len(generated_posts)} post variations.',
            'api_key_name': api_key_name,
            'conversation_log': conversation_log
        })
        
    except Exception as e:
        logger.error(f"Error starting debate: {e}", exc_info=True)
        error_str = str(e)
        # Check if it's a rate limit error
        if 'rate_limit_exceeded' in error_str or 'Rate limit reached' in error_str or '429' in error_str:
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'error_type': 'rate_limit',
                'details': error_str,
                'message': '[RATE LIMIT] Groq API Rate Limit Exceeded - Please wait 20-30 minutes and try again'
            }), 429
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debates/<int:post_input_id>', methods=['GET'])
def get_debates(post_input_id):
    """Get all debate entries for a post input"""
    try:
        debates = db.get_debates_for_post(post_input_id)
        return jsonify({
            'success': True,
            'debates': debates,
            'count': len(debates)
        })
    except Exception as e:
        logger.error(f"Error fetching debates for post {post_input_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========================================
# API ROUTES - Generated Posts
# ========================================

@app.route('/api/generated-posts/<int:post_input_id>', methods=['GET'])
def get_generated_posts(post_input_id):
    """Get all generated posts for a post input"""
    try:
        posts = db.get_generated_posts(post_input_id)
        return jsonify({
            'success': True,
            'posts': posts,
            'count': len(posts)
        })
    except Exception as e:
        logger.error(f"Error fetching generated posts for {post_input_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-post/<int:post_id>', methods=['POST'])
def save_post(post_id):
    """Save a post with all its context and debate data"""
    try:
        # Get custom name from request body if provided
        data = request.get_json() or {}
        custom_name = data.get('custom_name', None)
        
        # Mark post as saved in database with optional custom name
        result = db.save_post(post_id, custom_name)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Post saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Post not found or already saved'
            }), 404
    except Exception as e:
        logger.error(f"Error saving post {post_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/saved-posts', methods=['GET'])
def get_saved_posts():
    """Get all saved posts"""
    try:
        posts = db.get_saved_posts()
        return jsonify({
            'success': True,
            'posts': posts,
            'count': len(posts)
        })
    except Exception as e:
        logger.error(f"Error fetching saved posts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/saved-post/<int:post_id>', methods=['GET'])
def get_saved_post_detail(post_id):
    """Get detailed view of a saved post including all debate context"""
    try:
        post_detail = db.get_saved_post_detail(post_id)
        
        if post_detail:
            return jsonify({
                'success': True,
                'post': post_detail
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Saved post not found'
            }), 404
    except Exception as e:
        logger.error(f"Error fetching saved post detail {post_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get all post generation history"""
    try:
        history = db.get_post_history()
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/<int:post_input_id>', methods=['GET'])
def get_history_detail(post_input_id):
    """Get detailed history for a specific post input"""
    try:
        history_detail = db.get_history_detail(post_input_id)
        
        if history_detail:
            return jsonify({
                'success': True,
                'history': history_detail
            })
        else:
            return jsonify({
                'success': False,
                'message': 'History not found'
            }), 404
    except Exception as e:
        logger.error(f"Error fetching history detail {post_input_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/retry-debate/<int:post_input_id>', methods=['POST'])
def retry_debate(post_input_id):
    """Retry the debate for a post input"""
    try:
        # Get the original post input data
        post_input = db.get_post_input(post_input_id)
        
        if not post_input:
            return jsonify({
                'success': False,
                'message': 'Post input not found'
            }), 404
        
        # Clear previous debates and generated posts for this input
        db.clear_post_results(post_input_id)
        
        # Trigger new debate (async)
        from utils.debate_orchestrator import DebateOrchestrator
        debate_orchestrator = DebateOrchestrator()
        
        # Run debate asynchronously
        import threading
        thread = threading.Thread(
            target=debate_orchestrator.run_debate,
            args=(post_input_id, post_input)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Debate retry initiated',
            'post_input_id': post_input_id
        })
    except Exception as e:
        logger.error(f"Error retrying debate for {post_input_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========================================
# API ROUTES - Health Check
# ========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'Minimal Version API is running'
    })

# ========================================
# Error Handlers
# ========================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ========================================
# Main Entry Point
# ========================================

if __name__ == '__main__':
    # Create database tables if they don't exist
    db.init_database()
    
    # Get configuration from environment
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Run the application
    logger.info(f"Starting Minimal Version Flask App on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
