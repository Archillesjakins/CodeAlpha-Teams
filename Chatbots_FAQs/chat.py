import nltk
import re
import random
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt_tab', quiet=True)

class FAQChatbot:
    def __init__(self, faq_data):
        """
        Initialize the chatbot with FAQ data.
        
        :param faq_data: List of dictionaries with 'question' and 'answer' keys
        """
        self.faq_data = faq_data
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Preprocess questions for faster matching
        self.processed_faqs = self.preprocess_faq_data()
    
    def preprocess_text(self, text):
        """
        Preprocess input text for comparison.
        
        :param text: Input text string
        :return: Processed list of lemmatized words
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words
        ]
        
        return processed_tokens
    
    def preprocess_faq_data(self):
        """
        Preprocess all FAQ questions for faster matching.
        
        :return: List of preprocessed FAQ entries
        """
        processed_faqs = []
        for faq in self.faq_data:
            processed_question = self.preprocess_text(faq['question'])
            processed_faqs.append({
                'original_question': faq['question'],
                'processed_question': processed_question,
                'answer': faq['answer']
            })
        return processed_faqs
    
    def calculate_similarity(self, input_tokens, faq_tokens):
        """
        Calculate similarity between input and FAQ question using Jaccard similarity.
        
        :param input_tokens: Preprocessed input tokens
        :param faq_tokens: Preprocessed FAQ question tokens
        :return: Similarity score
        """
        input_set = set(input_tokens)
        faq_set = set(faq_tokens)
        
        # Jaccard similarity
        intersection = len(input_set.intersection(faq_set))
        union = len(input_set.union(faq_set))
        
        return intersection / union if union > 0 else 0
    
    def find_best_match(self, input_text, similarity_threshold=0.3):
        """
        Find the best matching FAQ for the input text.
        
        :param input_text: User input string
        :param similarity_threshold: Minimum similarity to consider a match
        :return: Best matching FAQ or None
        """
        # Preprocess input
        processed_input = self.preprocess_text(input_text)
        
        # Calculate similarities
        similarities = []
        for faq in self.processed_faqs:
            similarity = self.calculate_similarity(
                processed_input, 
                faq['processed_question']
            )
            similarities.append((similarity, faq))
        
        # Sort by similarity in descending order
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        # Return best match if above threshold
        if similarities and similarities[0][0] >= similarity_threshold:
            return similarities[0][1]
        
        return None
    
    def generate_response(self, input_text):
        """
        Generate a response to the input text.
        
        :param input_text: User input string
        :return: Chatbot response
        """
        # Try to find a matching FAQ
        match = self.find_best_match(input_text)
        
        if match:
            return match['answer']
        
        # Fallback responses if no match found
        fallback_responses = [
            "I'm sorry, I couldn't find a specific answer to your question.",
            "Could you please rephrase your question?",
            "I don't have enough information to answer that. Can you be more specific?",
            "I'm afraid I don't understand. Could you try asking differently?"
        ]
        
        return random.choice(fallback_responses)

# Load FAQ data from a JSON file
def load_faq_data(file_path='faqs.json'):
    """
    Load FAQ data from a JSON file.
    
    :param file_path: Path to the JSON file containing FAQ data
    :return: List of FAQ dictionaries
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default FAQs if file not found
        return [
            {
                'question': 'What are your business hours?',
                'answer': 'We are open Monday to Friday from 9 AM to 5 PM.'
            },
            {
                'question': 'How can I contact customer support?',
                'answer': 'You can reach our customer support at 1-800-SUPPORT or email support@company.com'
            }
        ]

# Create a global chatbot instance
faq_data = load_faq_data()
chatbot = FAQChatbot(faq_data)