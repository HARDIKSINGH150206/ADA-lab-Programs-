document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');

    // API Configuration
    const API_BASE_URL = 'http://localhost:8000'; // Default FastAPI URL

    // Format time to 10:30 AM
    function getCurrentTime() {
        return new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function showTypingIndicator() {
        typingIndicator.style.display = 'flex';
        chatContainer.appendChild(typingIndicator); // Move to bottom
        scrollToBottom();
    }

    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }

    function appendUserMessage(text) {
        const time = getCurrentTime();
        const html = `
            <div class="message-row user-row">
                <div class="message-content user-message">
                    <p>${text}</p>
                    <span class="timestamp">You • ${time}</span>
                </div>
                <div class="avatar user-avatar">
                    <i class="fa-solid fa-user"></i>
                </div>
            </div>
        `;
        // Insert before typing indicator
        typingIndicator.insertAdjacentHTML('beforebegin', html);
        scrollToBottom();
    }

    function appendBotMessage(text) {
        const time = getCurrentTime();
        const html = `
            <div class="message-row bot-row">
                <div class="avatar bot-avatar">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="message-content bot-message">
                    <p>${text}</p>
                    <span class="timestamp">AI Assistant • ${time}</span>
                </div>
            </div>
        `;
        typingIndicator.insertAdjacentHTML('beforebegin', html);
        scrollToBottom();
    }

    async function sendMessageToBackend(message) {
        // Here we would typically hit the actual chat endpoint
        // e.g., /api/v1/chat or /api/v1/demo/chat
        // Since we don't have the exact endpoint, we'll try a generic fetch or mock it
        
        try {
            // Attempting to reach the health endpoint just to test connection
            const response = await fetch(`${API_BASE_URL}/health`);
            if (response.ok) {
                // If backend is alive, simulate a response processing time
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve("I understand. Based on my analysis of Indian Labor Laws, you should prepare your documents. How else can I assist you?");
                    }, 1500);
                });
            } else {
                throw new Error("Backend not healthy");
            }
        } catch (error) {
            console.error("Error communicating with backend:", error);
            // Fallback mock response if backend is not running or unreachable
            return new Promise(resolve => {
                setTimeout(() => {
                    resolve("I'm currently unable to connect to the legal database. Please check your network connection.");
                }, 1000);
            });
        }
    }

    async function handleSend() {
        const text = chatInput.value.trim();
        if (!text) return;

        chatInput.value = '';
        appendUserMessage(text);
        
        showTypingIndicator();
        
        const botResponse = await sendMessageToBackend(text);
        
        hideTypingIndicator();
        appendBotMessage(botResponse);
    }

    // Event Listeners
    sendBtn.addEventListener('click', handleSend);
    
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });

    // Handle existing action buttons
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const actionText = e.target.innerText.trim();
            appendUserMessage(`I want to: ${actionText}`);
            
            showTypingIndicator();
            setTimeout(() => {
                hideTypingIndicator();
                appendBotMessage(`Great. Initiating the process for: ${actionText}. Please follow the instructions on screen.`);
            }, 1000);
        });
    });

    // Make sure typing indicator is at the bottom initially
    chatContainer.appendChild(typingIndicator);
    scrollToBottom();
});
