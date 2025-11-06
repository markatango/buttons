# data_store.py - Shared Data Store
from datetime import datetime
import time

class DataStore:
    """Shared data store for messages, users, and rooms"""
    
    def __init__(self):
        self.messages = []
        self.users = {}
        self.rooms = {}
    
    def add_message(self, message_text, username, room='general', sid=None):
        """Add a new message to the store"""
        message = {
            'id': len(self.messages) + 1,
            'message': message_text,
            'username': username,
            'room': room,
            'sid': sid,
            'timestamp': time.time(),
            'created_at': datetime.now().isoformat()
        }
        self.messages.append(message)
        return message
    
    def get_messages(self, room=None, limit=50):
        """Get messages, optionally filtered by room"""
        filtered_messages = self.messages
        if room:
            filtered_messages = [msg for msg in self.messages if msg.get('room') == room]
        return filtered_messages[-limit:]
    
    def add_user(self, sid, username=None):
        """Add or update a user"""
        self.users[sid] = {
            'sid': sid,
            'connected_at': datetime.now().isoformat(),
            'username': username,
            'current_room': None
        }
        return self.users[sid]
    
    def remove_user(self, sid):
        """Remove a user"""
        if sid in self.users:
            del self.users[sid]
    
    def update_user_room(self, sid, room_name, username=None):
        """Update user's current room"""
        if sid in self.users:
            self.users[sid]['current_room'] = room_name
            if username:
                self.users[sid]['username'] = username
    
    def add_user_to_room(self, sid, room_name):
        """Add user to a room"""
        if room_name not in self.rooms:
            self.rooms[room_name] = {
                'users': set(),
                'created_at': datetime.now().isoformat()
            }
        self.rooms[room_name]['users'].add(sid)
    
    def remove_user_from_room(self, sid, room_name):
        """Remove user from a room"""
        if room_name in self.rooms:
            self.rooms[room_name]['users'].discard(sid)
            # Remove empty rooms
            if not self.rooms[room_name]['users']:
                del self.rooms[room_name]
    
    def get_room_info(self, room_name):
        """Get room information"""
        return self.rooms.get(room_name)
    
    def get_all_rooms_info(self):
        """Get information about all rooms"""
        room_info = {}
        for room_name, room_data in self.rooms.items():
            room_info[room_name] = {
                'name': room_name,
                'user_count': len(room_data['users']),
                'created_at': room_data['created_at']
            }
        return room_info
