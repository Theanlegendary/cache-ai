"""
Cache AI REST API
Flask API server for Cache AI functionality
Access at: http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
from datetime import datetime
import os

# Import our services
from src.cache_service import CacheService
from src.cache_ai_rating import CacheAIRatingEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize services
cache_service = CacheService(use_file_storage=True)
rating_engine = CacheAIRatingEngine()

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Cache AI API',
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================================================
# SESSION ENDPOINTS
# ============================================================================

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new session"""
    try:
        data = request.get_json()
        
        session_data = {
            'user_id': data.get('user_id'),
            'repository': data.get('repository'),
            'branch': data.get('branch', 'main'),
            'ai_provider': data.get('ai_provider', 'cache_ai'),
            'metadata': data.get('metadata', {})
        }
        
        session_id = cache_service.store_session(session_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Session created',
            'session_id': session_id
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    try:
        session = cache_service.get_session(session_id)
        
        if not session:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        
        return jsonify({
            'status': 'success',
            'session': session
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all sessions"""
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 10))
        
        sessions = cache_service.get_sessions(user_id, limit)
        
        return jsonify({
            'status': 'success',
            'sessions': sessions,
            'count': len(sessions)
        }), 200
    
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# INTERACTION ENDPOINTS
# ============================================================================

@app.route('/api/interactions', methods=['POST'])
def log_interaction():
    """Log an AI interaction"""
    try:
        data = request.get_json()
        
        interaction_data = {
            'session_id': data.get('session_id'),
            'type': data.get('type'),
            'user_input': data.get('input'),
            'ai_response': data.get('response'),
            'ai_provider': data.get('ai_provider', 'cache_ai'),
            'tokens_used': data.get('tokens', 0),
            'response_time_ms': data.get('time', 0),
            'metadata': data.get('metadata', {})
        }
        
        interaction_id = cache_service.log_interaction(interaction_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Interaction logged',
            'interaction_id': interaction_id
        }), 201
    
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Error logging interaction: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/sessions/<session_id>/interactions', methods=['GET'])
def get_interactions(session_id):
    """Get interactions from a session"""
    try:
        interactions = cache_service.get_interactions(session_id)
        
        return jsonify({
            'status': 'success',
            'interactions': interactions,
            'count': len(interactions)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting interactions: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# CACHE ENDPOINTS
# ============================================================================

@app.route('/api/cache', methods=['POST'])
def cache_pattern():
    """Cache a code pattern"""
    try:
        data = request.get_json()
        
        pattern = data.get('pattern')
        response = data.get('response')
        ttl = data.get('ttl', 2592000)  # 30 days default
        
        if not pattern or not response:
            return jsonify({'status': 'error', 'message': 'pattern and response required'}), 400
        
        cache_id = cache_service.cache_pattern(pattern, response, ttl)
        
        return jsonify({
            'status': 'success',
            'message': 'Pattern cached',
            'cache_id': cache_id
        }), 201
    
    except Exception as e:
        logger.error(f"Error caching pattern: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/cache/<pattern>', methods=['GET'])
def get_cache(pattern):
    """Get cached response for a pattern"""
    try:
        cache_entry = cache_service.get_cache(pattern)
        
        if not cache_entry:
            return jsonify({'status': 'error', 'message': 'Cache not found'}), 404
        
        return jsonify({
            'status': 'success',
            'cache': cache_entry
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting cache: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get cache statistics"""
    try:
        stats = cache_service.get_statistics()
        
        return jsonify({
            'status': 'success',
            'statistics': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# RATING ENDPOINTS
# ============================================================================

@app.route('/api/rate', methods=['GET'])
def get_rating():
    """Get Cache AI rating (0-10)"""
    try:
        report = rating_engine.generate_full_report()
        
        return jsonify({
            'status': 'success',
            'rating': report['cache_ai_rating']['ratings']['overall'],
            'report': report
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting rating: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/compare/<provider>', methods=['GET'])
def compare_provider(provider):
    """Compare Cache AI vs specific provider"""
    try:
        comparison = rating_engine.get_cache_ai_vs_specific(provider)
        
        if 'error' in comparison:
            return jsonify({'status': 'error', 'message': comparison['error']}), 404
        
        return jsonify({
            'status': 'success',
            'comparison': comparison
        }), 200
    
    except Exception as e:
        logger.error(f"Error comparing providers: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/compare', methods=['GET'])
def compare_all():
    """Compare all providers"""
    try:
        comparison = rating_engine.compare_cache_ai_vs_all()
        
        return jsonify({
            'status': 'success',
            'comparison': comparison
        }), 200
    
    except Exception as e:
        logger.error(f"Error comparing all: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def dashboard():
    """Main dashboard"""
    try:
        stats = cache_service.get_statistics()
        rating = rating_engine.get_cache_ai_rating()
        
        return render_template('dashboard.html', stats=stats, rating=rating)
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/dashboard', methods=['GET'])
def dashboard_page():
    """Dashboard page"""
    return dashboard()

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 handler"""
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 handler"""
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Cache AI API Server Starting...")
    print("="*60)
    print("\n📊 API Available at: http://localhost:5000")
    print("🌐 Dashboard at:     http://localhost:5000/dashboard")
    print("\n📚 API Endpoints:")
    print("   POST   /api/sessions                - Create session")
    print("   GET    /api/sessions                - List sessions")
    print("   GET    /api/sessions/<id>           - Get session")
    print("   POST   /api/interactions            - Log interaction")
    print("   GET    /api/sessions/<id>/interactions - Get interactions")
    print("   POST   /api/cache                   - Cache pattern")
    print("   GET    /api/cache/<pattern>         - Get cache")
    print("   GET    /api/stats                   - Get statistics")
    print("   GET    /api/rate                    - Get rating (0-10)")
    print("   GET    /api/compare/<provider>      - Compare with provider")
    print("   GET    /api/compare                 - Compare all providers")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
