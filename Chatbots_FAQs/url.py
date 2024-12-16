import redis
import json
import uuid
from datetime import datetime, timedelta

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0):
        """
        Initialize Redis connection.
        
        :param host: Redis server host
        :param port: Redis server port
        :param db: Redis database number
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    
    def create_conversation(self, user_id=None):
        """
        Create a new conversation ID and initialize conversation data.
        
        :param user_id: Optional user identifier
        :return: Conversation ID
        """
        # Generate a unique conversation ID if not provided
        conv_id = user_id or str(uuid.uuid4())
        
        # Initialize conversation metadata
        conv_data = {
            'id': conv_id,
            'created_at': datetime.now().isoformat(),
            'messages': []
        }
        
        # Store conversation in Redis with expiration
        key = f'conversation:{conv_id}'
        self.redis_client.setex(
            key, 
            timedelta(hours=24),  # Conversation expires after 24 hours
            value=json.dumps(conv_data)
        )
        
        return conv_id
    
    def add_message(self, conversation_id, role, message):
        """
        Add a message to a conversation.
        
        :param conversation_id: Conversation ID
        :param role: 'user' or 'bot'
        :param message: Message content
        """
        key = f'conversation:{conversation_id}'
        
        # Retrieve existing conversation
        conv_str = self.redis_client.get(key)
        if not conv_str:
            # Create new conversation if not exists
            conv_data = {
                'id': conversation_id,
                'created_at': datetime.now().isoformat(),
                'messages': []
            }
        else:
            conv_data = json.loads(conv_str)
        
        # Add new message
        conv_data['messages'].append({
            'role': role,
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update conversation in Redis
        self.redis_client.setex(
            key, 
            timedelta(hours=24), 
            value=json.dumps(conv_data)
        )
    
    def get_conversation(self, conversation_id):
        """
        Retrieve a conversation's full history.
        
        :param conversation_id: Conversation ID
        :return: Conversation data or None
        """
        key = f'conversation:{conversation_id}'
        conv_str = self.redis_client.get(key)
        
        return json.loads(conv_str) if conv_str else None
    
    def clear_conversation(self, conversation_id):
        """
        Clear a specific conversation.
        
        :param conversation_id: Conversation ID
        """
        key = f'conversation:{conversation_id}'
        self.redis_client.delete(key)

# Create a global Redis manager instance
redis_manager = RedisManager()