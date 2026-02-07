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

# Import database
from database import get_db

# Import blueprints
from routes.settings import settings_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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
        
        # Validate required fields
        required_fields = [
            'brand_id', 'post_topic', 'post_objective', 'target_platform',
            'content_type', 'key_message'
        ]
        
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
        
        # Run debate process
        logger.info(f"Starting debate for post_input_id: {post_input_id}")
        orchestrator = DebateOrchestrator()
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
        
        return jsonify({
            'success': True,
            'post_input_id': post_input_id,
            'final_vote': final_vote,
            'cmo_decision': debate_results.get('cmo_decision'),
            'generated_posts_count': len(generated_posts),
            'message': f'Debate complete - {final_vote}. Generated {len(generated_posts)} post variations.'
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
