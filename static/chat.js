document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');

    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                });

                const data = await response.json();
                addMessage(data.response);
            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, I encountered an error. Please try again.');
            }
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Speech Recognition
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        micButton.addEventListener('click', () => {
            recognition.start();
            micButton.textContent = '🎤 Listening...';
            micButton.disabled = true;
        });

        recognition.addEventListener('result', (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            micButton.textContent = '🎤';
            micButton.disabled = false;
            sendMessage(); // Automatically send message after speech
        });

        recognition.addEventListener('end', () => {
            micButton.textContent = '🎤';
            micButton.disabled = false;
        });

        recognition.addEventListener('error', (event) => {
            console.error('Speech recognition error:', event.error);
            micButton.textContent = '🎤';
            micButton.disabled = false;
            addMessage('Speech recognition failed. Please try again.');
        });
    } else {
        micButton.style.display = 'none';
        console.warn('Speech Recognition not supported in this browser.');
    }
}); 