from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename
from chat import FAQChatbot  

app = Flask(__name__, static_folder="static", template_folder="templates")

app.secret_key = os.getenv('keys')  # Required for flash messages

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json', 'txt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize chatbot with default FAQ data
default_faq_data = [
    {
        'question': 'Hello',
        'answer': 'Hi, what can I assist you with?'
    },
    {
        'question': 'Hi',
        'answer': 'Hello! How may I help you today?'
    },
    {
        'question': '1',
        'answer': 'You can upload a JSON file with FAQ data to help me better answer your questions. The file should contain a list of question-answer pairs.'
    },
    {
        'question': 'help',
        'answer': 'You can upload a JSON file with FAQ data to help me better answer your questions. The file should contain a list of question-answer pairs.'
    },
    {
        'question': 'How do I use this?',
        'answer': 'To get started, you can upload a JSON file containing your FAQ data. The file should include questions and their corresponding answers.'
    }
]
    
chatbot = FAQChatbot(default_faq_data)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_faq_data(data):
    """Validate the structure of uploaded FAQ data"""
    if not isinstance(data, list):
        return False, "FAQ data must be a list"
    
    for item in data:
        if not isinstance(item, dict):
            return False, "Each FAQ item must be a dictionary"
        
        if 'question' not in item or 'answer' not in item:
            return False, "Each FAQ item must contain 'question' and 'answer' keys"
        
        if not isinstance(item['question'], str) or not isinstance(item['answer'], str):
            return False, "Question and answer must be strings"
        
        if not item['question'].strip() or not item['answer'].strip():
            return False, "Question and answer cannot be empty"
    
    return True, "Data is valid"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a JSON or TXT file')
        return redirect(url_for('index'))
    
    if file:
        try:
            # Read and parse the file content
            content = file.read().decode('utf-8')
            faq_data = json.loads(content)
            
            # Validate FAQ data structure
            is_valid, message = validate_faq_data(faq_data)
            if not is_valid:
                flash(f'Invalid FAQ data format: {message}')
                return redirect(url_for('index'))
            
            # Update chatbot with new FAQ data
            global chatbot
            chatbot = FAQChatbot(faq_data)
            
            flash('FAQ data successfully uploaded and updated')
            return redirect(url_for('index'))
            
        except json.JSONDecodeError:
            flash('Invalid JSON format')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Invalid request'}), 400
        
        user_message = data['message']
        response = chatbot.generate_response(user_message)
        
        return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)