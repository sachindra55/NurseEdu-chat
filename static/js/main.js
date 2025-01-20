document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'message loading';
    loadingIndicator.textContent = 'NurseEdu is thinking...';

    // Initialize markdown-it
    const md = window.markdownit({
        html: true,
        linkify: true,
        typographer: true
    });

    function appendMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        if (isUser) {
            messageDiv.textContent = content;
        } else {
            // Convert markdown to HTML
            const htmlContent = md.render(content);
            messageDiv.innerHTML = htmlContent;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Clear input
        userInput.value = '';

        // Add user message
        appendMessage(message, true);

        // Show loading indicator
        chatMessages.appendChild(loadingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Remove loading indicator
            loadingIndicator.remove();

            if (data.success) {
                appendMessage(data.response, false);
            } else {
                appendMessage('Error: ' + (data.error || 'Something went wrong'), false);
            }
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.remove();
            appendMessage('Error: Failed to get response from server', false);
        }
    });

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
    });
});
