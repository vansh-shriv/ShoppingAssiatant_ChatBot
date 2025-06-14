document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');
    const viewCartButton = document.getElementById('view-cart-button');

    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.innerHTML = message; // Use innerHTML to allow for buttons
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

    async function addToCart(productId) {
        try {
            const response = await fetch('/api/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product_id: productId }),
            });
            const data = await response.json();
            alert(data.message); // Simple alert for confirmation
        } catch (error) {
            console.error('Error adding to cart:', error);
            alert('Failed to add item to cart.');
        }
    }

    async function viewCart() {
        try {
            const response = await fetch('/api/view_cart');
            const data = await response.json();
            let cartContent = '<h3>Your Cart:</h3>';
            if (data.cart.length === 0) {
                cartContent += '<p>Your cart is empty.</p>';
            } else {
                cartContent += '<ul>';
                data.cart.forEach(item => {
                    cartContent += `<li>${item.name} - $${item.price.toFixed(2)}</li>`;
                });
                cartContent += `</ul><p>Total Items: ${data.total_items}</p>`;
                cartContent += `<p>Total Price: $${data.total_price.toFixed(2)}</p>`;
            }
            addMessage(cartContent, false); // Display cart content as a bot message
        } catch (error) {
            console.error('Error viewing cart:', error);
            addMessage('Sorry, I could not retrieve your cart. Please try again.');
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    viewCartButton.addEventListener('click', viewCart);

    // Event listener for dynamically created 'Add to Cart' buttons
    chatMessages.addEventListener('click', function(event) {
        if (event.target.classList.contains('add-to-cart-btn')) {
            const productId = parseInt(event.target.dataset.productId);
            addToCart(productId);
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