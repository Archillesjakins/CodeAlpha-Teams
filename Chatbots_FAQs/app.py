from flask import Flask, render_template, request, jsonify
from chat import chatbot
from url import redis_manager
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    """
    Render the main chat interface.
    
    :return: Rendered HTML template
    """
    # Generate a unique conversation ID for the session
    conversation_id = str(uuid.uuid4())
    redis_manager.create_conversation(conversation_id)
    
    return render_template('index.html', conversation_id=conversation_id)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages.
    
    :return: JSON response with bot's reply
    """
    data = request.get_json()
    user_message = data.get('message', '')
    conversation_id = data.get('conversation_id')
    
    # Validate inputs
    if not user_message or not conversation_id:
        return jsonify({
            'error': 'Invalid input',
            'message': 'Message and conversation ID are required.'
        }), 400
    
    # Store user message in Redis
    redis_manager.add_message(conversation_id, 'user', user_message)
    
    # Generate bot response
    bot_response = chatbot.generate_response(user_message)
    
    # Store bot response in Redis
    redis_manager.add_message(conversation_id, 'bot', bot_response)
    
    return jsonify({
        'message': bot_response,
        'conversation_id': conversation_id
    })

@app.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Retrieve full conversation history.
    
    :param conversation_id: Unique conversation identifier
    :return: JSON response with conversation history
    """
    conversation = redis_manager.get_conversation(conversation_id)
    
    if not conversation:
        return jsonify({
            'error': 'Conversation not found',
            'message': 'No conversation exists with this ID.'
        }), 404
    
    return jsonify(conversation)

if __name__ == '__main__':
    app.run(debug=True, port=4002)