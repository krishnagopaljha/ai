document.addEventListener('DOMContentLoaded', function() {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const stopBtn = document.getElementById('stop-btn');
    const clearBtn = document.getElementById('clear-btn');
    
    let currentController = null;
    let currentAiMessageElement = null;
    
    function addMessage(text, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
        messageDiv.textContent = text;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        if (!isUser) {
            currentAiMessageElement = messageDiv;
        }
        
        return messageDiv;
    }
    
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, true);
        
        // Clear input
        userInput.value = '';
        
        // Disable send button and enable stop button
        sendBtn.disabled = true;
        stopBtn.disabled = false;
        
        // Create AI message element
        currentAiMessageElement = addMessage('', false);
        
        // Create an AbortController for this request
        currentController = new AbortController();
        const signal = currentController.signal;
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: message
                }),
                signal: signal
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiResponse = '';
            
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    break;
                }
                
                // Append the new token to the response
                aiResponse += decoder.decode(value, { stream: true });
                currentAiMessageElement.textContent = aiResponse;
                
                // Scroll to bottom
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
            
        } catch (error) {
            if (error.name === 'AbortError') {
                currentAiMessageElement.textContent += " [Stopped]";
            } else {
                console.error('Error:', error);
                currentAiMessageElement.textContent += ` [Error: ${error.message}]`;
            }
        } finally {
            resetUI();
        }
    }
    
    function stopGeneration() {
        if (currentController) {
            currentController.abort();
        }
        resetUI();
    }
    
    function resetUI() {
        sendBtn.disabled = false;
        stopBtn.disabled = true;
        currentController = null;
        currentAiMessageElement = null;
    }
    
    function clearChat() {
        chatHistory.innerHTML = '';
    }
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    stopBtn.addEventListener('click', stopGeneration);
    clearBtn.addEventListener('click', clearChat);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
