# socketio_blueprint_flask.py - Socket.IO Events Blueprint (Flask-SocketIO version)
from flask_socketio import emit, join_room, leave_room
from flask import request

class SocketIOBlueprint:
    """Blueprint for Flask-SocketIO event handlers"""
    
    def __init__(self, data_store, socketio):
        self.data_store = data_store
        self.socketio = socketio
        self.name = "flask_socketio_events"
    
    def register(self):
        """Register all Flask-SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def on_connect():
            sid = request.sid
            print(f'Flask-SocketIO client {sid} connected')
            self.data_store.add_user(sid)
            emit('welcome', {
                'message': 'Connected to Flask-SocketIO server',
                'sid': sid
            })
        
        @self.socketio.on('disconnect')
        def on_disconnect():
            sid = request.sid
            print(f'Flask-SocketIO client {sid} disconnected')
            
            # Remove from room if in one
            user = self.data_store.users.get(sid)
            if user and user['current_room']:
                self._leave_room_helper(sid, user['current_room'])
            
            # Remove user
            self.data_store.remove_user(sid)
        
        @self.socketio.on('join_room')
        def on_join_room(data):
            sid = request.sid
            room_name = data.get('room', 'general')
            username = data.get('username', f'User_{sid[:8]}')
            
            # Leave current room if in one
            user = self.data_store.users.get(sid)
            if user and user['current_room']:
                self._leave_room_helper(sid, user['current_room'])
            
            # Join new room
            join_room(room_name)
            
            # Update data store
            self.data_store.update_user_room(sid, room_name, username)
            self.data_store.add_user_to_room(sid, room_name)
            
            # Get room info
            room_info = self.data_store.get_room_info(room_name)
            
            # Notify room
            emit('user_joined', {
                'username': username,
                'message': f'{username} joined {room_name}',
                'room': room_name,
                'user_count': len(room_info['users'])
            }, room=room_name)
            
            return {
                'success': True,
                'room': room_name,
                'username': username,
                'user_count': len(room_info['users'])
            }
        
        @self.socketio.on('send_message')
        def on_send_message(data):
            sid = request.sid
            message_text = data.get('message')
            if not message_text:
                return {'error': 'Message required'}
            
            user = self.data_store.users.get(sid)
            if not user or not user['current_room']:
                return {'error': 'Must join a room first'}
            
            # Add message to store
            message = self.data_store.add_message(
                message_text=message_text,
                username=user['username'],
                room=user['current_room'],
                sid=sid
            )
            
            # Broadcast to room
            emit('new_message', message, room=user['current_room'])
            
            return {'success': True, 'message_id': message['id']}
        
        @self.socketio.on('get_room_info')
        def on_get_room_info(data):
            sid = request.sid
            user = self.data_store.users.get(sid)
            if not user or not user['current_room']:
                return {'error': 'Not in any room'}
            
            room_name = user['current_room']
            room_data = self.data_store.get_room_info(room_name)
            
            if not room_data:
                return {'error': 'Room not found'}
            
            # Get recent messages for this room
            room_messages = self.data_store.get_messages(room=room_name, limit=10)
            
            return {
                'room': room_name,
                'user_count': len(room_data['users']),
                'recent_messages': room_messages,
                'created_at': room_data['created_at']
            }
        
        @self.socketio.on('leave_room')
        def on_leave_room(data):
            sid = request.sid
            user = self.data_store.users.get(sid)
            if not user or not user['current_room']:
                return {'error': 'Not in any room'}
            
            room_name = user['current_room']
            self._leave_room_helper(sid, room_name)
            
            return {'success': True, 'left_room': room_name}
        
        print(f"Registered {self.name} blueprint with Flask-SocketIO handlers")
    
    def _leave_room_helper(self, sid, room_name):
        """Helper function to handle leaving a room"""
        room_info = self.data_store.get_room_info(room_name)
        if room_info:
            # Remove from data store
            self.data_store.remove_user_from_room(sid, room_name)
            
            # Update user
            self.data_store.update_user_room(sid, None)
            
            # Notify remaining users if room still exists
            updated_room_info = self.data_store.get_room_info(room_name)
            if updated_room_info:
                user = self.data_store.users.get(sid)
                username = user['username'] if user else f'User_{sid[:8]}'
                emit('user_left', {
                    'username': username,
                    'message': f'{username} left {room_name}',
                    'room': room_name,
                    'user_count': len(updated_room_info['users'])
                }, room=room_name)
        
        # Leave Flask-SocketIO room
        leave_room(room_name)