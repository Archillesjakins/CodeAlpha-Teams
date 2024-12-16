document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const conversationId = userInput.getAttribute('data-conversation-id');

    // Function to add a message to the chat
    function addMessage(message, type) {
        const messageEl = document.createElement('div');
        messageEl.classList.add(`${type}-message`);
        messageEl.textContent = message;
        chatMessages.appendChild(messageEl);
        
        // Auto-scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to send a message
    function sendMessage() {
        const message = userInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        userInput.value = '';
        
        // Send message to backend
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application'
       }})
       }})