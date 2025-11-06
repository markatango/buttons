# server.py - Main Server File
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from datetime import datetime

# Import blueprints
from api_blueprint_flask import create_api_blueprint
from socketio_blueprint_flask import SocketIOBlueprint

# Shared data store (use database in production)
from data_store import DataStore

def create_app():
    """Create and configure the Flask app with Flask-SocketIO"""
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # ONLY use Flask-CORS at app level - remove duplicate CORS handling
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Remove the manual after_request handler to avoid duplicate headers
    # Flask-CORS will handle this automatically
    
    # Add global OPTIONS handler for preflight requests (keep this for debugging)
    @app.before_request
    def handle_preflight():
        print(f"🔍 DEBUG: before_request called for {request.method} {request.path} from origin: {request.headers.get('Origin', 'no-origin')}")  # Debug log
        if request.method == "OPTIONS":
            print("🔍 DEBUG: Handling OPTIONS preflight request")  # Debug log
            print(f"🔍 DEBUG: Request headers: {dict(request.headers)}")  # Debug request headers
            # Let Flask-CORS handle OPTIONS - don't return custom response
            return None
    
    # Create Flask-SocketIO instance (much better integration than python-socketio)
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*",
        logger=True,
        engineio_logger=False
    )
    
    # Initialize shared data store
    data_store = DataStore()
    
    # Create and register REST API blueprint
    api_bp = create_api_blueprint(data_store, socketio)
    app.register_blueprint(api_bp)
    print(f"🔍 DEBUG: Registered API blueprint with routes: {[rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith('/api')]}")  # Debug log
    
    # Create and register Socket.IO blueprint
    socketio_bp = SocketIOBlueprint(data_store, socketio)
    socketio_bp.register()
    
    # Root endpoint with CORS
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'message': 'Combined REST API + Socket.IO Server with Flask-SocketIO (CORS FIXED!)',
            'endpoints': {
                'REST': [
                    'GET /api/health',
                    'GET /api/messages',
                    'POST /api/messages',
                    'GET /api/users',
                    'GET /api/rooms'
                ],
                'Socket.IO': [
                    'connect',
                    'join_room',
                    'send_message',
                    'get_room_info',
                    'disconnect'
                ]
            },
            'timestamp': datetime.now().isoformat()
        })
    
    return app, socketio

def main():
    """Start the server"""
    app, socketio = create_app()
    
    # Debug: Show all registered routes
    print("🔍 DEBUG: All registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.methods} {rule.rule} -> {rule.endpoint}")
    
    print("🚀 Starting Combined REST API + Socket.IO Server with Flask-SocketIO")
    print("📡 REST API available at: http://127.0.0.1:5000")
    print("🔌 Socket.IO available at: http://127.0.0.1:5000")
    print("📋 API Documentation at: http://127.0.0.1:5000/")
    print("✅ CORS: SINGLE-LAYER Flask-CORS only - no duplicate headers!")
    print("🔧 Using Flask-SocketIO with eventlet for proper request handling")
    print("\n" + "="*60)
    
    # Use Flask-SocketIO's run method with eventlet - bind to IPv4 explicitly
    socketio.run(
        app,
        host='127.0.0.1',  # Use IPv4 localhost instead of 'localhost'
        port=5000,
        debug=False,  # Enable debug to see what's happening
        use_reloader=False
    )

if __name__ == '__main__':
    main()  