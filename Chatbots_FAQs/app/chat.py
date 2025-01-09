import nltk
import re
import random
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class FAQChatbot:
    def __init__(self, faq_data):
        """
        Initialize the chatbot with FAQ data.
        
        :param faq_data: List of dictionaries with 'question' and 'answer' keys
        """
        # Validate and normalize input data
        self.faq_data = self._validate_and_normalize_data(faq_data)
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Preprocess questions for faster matching
        self.processed_faqs = self.preprocess_faq_data()
    
    def _validate_and_normalize_data(self, data):
        """
        Validate and normalize the input FAQ data.
        
        :param data: Input FAQ data
        :return: Normalized FAQ data
        """
        if not isinstance(data, list):
            raise ValueError("FAQ data must be a list of dictionaries")
        
        normalized_data = []
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("Each FAQ item must be a dictionary")
            
            if 'question' not in item or 'answer' not in item:
                raise ValueError("Each FAQ item must contain 'question' and 'answer' keys")
            
            if not isinstance(item['question'], str) or not isinstance(item['answer'], str):
                raise ValueError("Question and answer must be strings")
            
            if not item['question'].strip() or not item['answer'].strip():
                raise ValueError("Question and answer cannot be empty")
            
            normalized_data.append({
                'question': item['question'].strip(),
                'answer': item['answer'].strip()
            })
        
        return normalized_data
    
    def preprocess_text(self, text):
        """
        Preprocess input text for comparison.
        
        :param text: Input text string
        :return: Processed list of lemmatized words
        """
        try:
            # Convert to lowercase and string type if needed
            text = str(text).lower()
            
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
        except Exception as e:
            raise ValueError(f"Error preprocessing text: {str(e)}")
    
    def preprocess_faq_data(self):
        """
        Preprocess all FAQ questions for faster matching.
        
        :return: List of preprocessed FAQ entries
        """
        processed_faqs = []
        for faq in self.faq_data:
            try:
                # Assign the processed tokens to a variable
                processed_question = self.preprocess_text(faq['question'])
                processed_faqs.append({
                    'original_question': faq['question'],
                    'processed_question': processed_question,  
                    'answer': faq['answer']
                })
            except Exception as e:
                print(f"Warning: Skipping invalid FAQ entry: {str(e)}")
                continue
        
        if not processed_faqs:
            raise ValueError("No valid FAQ entries were processed")
        
        return processed_faqs
    
    def calculate_similarity(self, input_tokens, faq_tokens):
        """
        Calculate similarity between input and FAQ question using Jaccard similarity.
        
        :param input_tokens: Preprocessed input tokens
        :param faq_tokens: Preprocessed FAQ question tokens
        :return: Similarity score
        """
        try:
            input_set = set(input_tokens)
            faq_set = set(faq_tokens)
            
            # Jaccard similarity
            intersection = len(input_set.intersection(faq_set))
            union = len(input_set.union(faq_set))
            
            # Enhanced similarity calculation
            if union == 0:
                return 0
            
            # Base Jaccard similarity
            jaccard = intersection / union
            
            # Check for partial matches
            partial_matches = sum(
                max(len(set(w1).intersection(w2))/max(len(w1), len(w2))
                    for w2 in faq_set)
                for w1 in input_set
            ) / len(input_set) if input_set else 0
            
            # Combine both metrics
            return (jaccard * 0.6 + partial_matches * 0.4)
        except Exception as e:
            print(f"Warning: Error calculating similarity: {str(e)}")
            return 0
    
    def find_best_match(self, input_text, similarity_threshold=0.3):
        """
        Find the best matching FAQ for the input text.
        
        :param input_text: User input string
        :param similarity_threshold: Minimum similarity to consider a match
        :return: Best matching FAQ or None
        """
        try:
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
        except Exception as e:
            print(f"Warning: Error finding best match: {str(e)}")
            return None
    
    def generate_response(self, input_text):
        """
        Generate a response to the input text.
        
        :param input_text: User input string
        :return: Chatbot response
        """
        try:
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
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

