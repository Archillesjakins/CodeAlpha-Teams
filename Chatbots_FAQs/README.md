# Artficial Integelence Using Machine learning Models

A chatbot that can answer frequently asked
questions (FAQs) about a particular topic or product.
Using natural language processing (NLP) techniques and
pre-built libraries **NLTK** to understand and
generate responses.

![Screenshot](https://github.com/user-attachments/assets/47660fe1-9eaa-4311-b4fd-e992c647d75b)

This project implements an intelligent FAQ chatbot using Python and NLTK. The chatbot processes user input, matches it with pre-existing FAQ data, and provides relevant answers based on similarity calculations. If no match is found, it provides a fallback response.

## Features

- **Text Preprocessing:** Removes stopwords, punctuation, and applies lemmatization for better matching.
- **Jaccard Similarity:** Matches user input with FAQs using enhanced similarity measures.
- **Customizable Responses:** Includes fallback responses for unmatched queries.
- **Error Handling:** Validates FAQ data and provides meaningful error messages.

## Requirements

- Python 3.6+
- Libraries:
  - nltk
  - numpy

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Archillesjakins/Chatbots_FAQs.git
   cd app
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Download necessary NLTK resources:
   The script downloads required NLTK data automatically. Ensure you have an active internet connection.

## Usage

### Initialization

1. import your FAQ data as a list of dictionaries, each with each ids `question` and `answer` keys:

   ```python
   faq_data = [
       {"question": "What is your return policy?", "answer": "You can return items within 30 days of purchase."},
       {"question": "How can I track my order?", "answer": "You can track your order using the tracking link sent to your email."},
   ]
   ```

### Interaction

To interact with the chatbot, use the import your information data on json format:

```python
user_input = "How do I track my order?"
response = chatbot.generate_response(user_input)
print(response)
```

## Contributing

Feel free to fork this repository and contribute to its development! Submit a pull request with any features or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
