# api_blueprint_flask.py - REST API Blueprint (Flask-SocketIO version)
from flask import Blueprint, request, jsonify
from datetime import datetime

def create_api_blueprint(data_store, socketio):
    """Create REST API blueprint for Flask-SocketIO"""
    
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    
    # Remove all CORS handling here - let Flask-CORS at app level handle it
    # This prevents duplicate headers
    
    @api_bp.route('/health', methods=['GET'])
    def health_check():
        print("🔍 DEBUG: /api/health route hit!")  # Debug log
        response = jsonify({
            'status': 'healthy',
            'server': 'Flask-SocketIO + eventlet + single CORS',
            'connected_users': len(data_store.users),
            'active_rooms': len(data_store.rooms),
            'total_messages': len(data_store.messages),
            'timestamp': datetime.now().isoformat()
        })
        print(f"🔍 DEBUG: Response headers from route: {dict(response.headers)}")  # Debug log
        return response
    
    @api_bp.route('/door', methods=['GET'])
    def door_op():
        print("🔍 DEBUG: /api/door route hit!")  # Debug log
        response = jsonify({
            'command': request.data.decode('utf-8') if request.data else 'missing data',
            'status': 'door operational',
            'timestamp': datetime.now().isoformat()
        })
        print(f"🔍 DEBUG: Response headers from route: {dict(response.headers)}")  # Debug log
        return response
    
    @api_bp.route('/messages', methods=['GET'])
    def get_messages():
        limit = request.args.get('limit', 50, type=int)
        room = request.args.get('room')
        
        messages = data_store.get_messages(room=room, limit=limit)
        
        return jsonify({
            'messages': messages,
            'total': len(messages),
            'limit': limit,
            'room_filter': room
        })
    
    @api_bp.route('/messages', methods=['POST'])
    def create_message():
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({'error': 'Message content required'}), 400
        
        # Add message to store
        message = data_store.add_message(
            message_text=data['message'],
            username=data.get('username', 'Anonymous'),
            room=data.get('room', 'general')
        )
        
        # Broadcast via Socket.IO if room exists
        room_name = message['room']
        if data_store.get_room_info(room_name):
            socketio.emit('new_message', message, room=room_name)
        
        return jsonify(message), 201
    
    @api_bp.route('/users', methods=['GET'])
    def get_users():
        return jsonify({
            'users': list(data_store.users.values()),
            'count': len(data_store.users)
        })
    
    @api_bp.route('/rooms', methods=['GET'])
    def get_rooms():
        return jsonify({
            'rooms': data_store.get_all_rooms_info(),
            'count': len(data_store.rooms)
        })
    
    @api_bp.route('/rooms/<room_name>', methods=['GET'])
    def get_room_details(room_name):
        room_info = data_store.get_room_info(room_name)
        if not room_info:
            return jsonify({'error': 'Room not found'}), 404
        
        # Get recent messages for this room
        room_messages = data_store.get_messages(room=room_name, limit=20)
        
        return jsonify({
            'room': room_name,
            'user_count': len(room_info['users']),
            'recent_messages': room_messages,
            'created_at': room_info['created_at']
        })
    
    return api_bp