class Chatbot {
    constructor() {
        this.isOpen = false;
        this.isLoading = false;
        this.initializeChatbot();
    }

    initializeChatbot() {
        this.attachEventListeners();
    }

    attachEventListeners() {
        const toggleBtn = document.getElementById('chatbotToggle');
        const closeBtn = document.getElementById('chatbotClose');
        const sendBtn = document.getElementById('chatbotSend');
        const input = document.getElementById('chatbotInput');
        const quickQuestions = document.querySelectorAll('.quick-question');

        // Toggle modal
        toggleBtn.addEventListener('click', () => this.toggleModal());

        // Close modal
        closeBtn.addEventListener('click', () => this.toggleModal());

        // Send message
        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Quick questions
        quickQuestions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.target.getAttribute('data-question');
                input.value = question;
                this.sendMessage();
            });
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            const modal = document.getElementById('chatbotModal');
            if (this.isOpen && !modal.contains(e.target) && !toggleBtn.contains(e.target)) {
                this.toggleModal();
            }
        });
    }

    toggleModal() {
        this.isOpen = !this.isOpen;
        const modal = document.getElementById('chatbotModal');

        if (this.isOpen) {
            modal.classList.add('active');
            document.getElementById('chatbotInput').focus();
        } else {
            modal.classList.remove('active');
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbotInput');
        const message = input.value.trim();

        if (!message || this.isLoading) return;

        this.addMessage(message, 'user');
        input.value = '';
        this.showLoading();

        try {
            const response = await this.callChatbotAPI(message);
            this.addMessage(response, 'bot');
        } catch (error) {
            console.error('Chatbot API error:', error);
            this.addMessage("Sorry, I'm having trouble connecting right now. Please try again later.", 'bot');
        } finally {
            this.hideLoading();
        }
    }

    async callChatbotAPI(message) {
        const csrfToken = this.getCSRFToken();

        const response = await fetch('/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.response;
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    showLoading() {
        this.isLoading = true;
        const sendBtn = document.getElementById('chatbotSend');
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        sendBtn.disabled = true;
    }

    hideLoading() {
        this.isLoading = false;
        const sendBtn = document.getElementById('chatbotSend');
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        sendBtn.disabled = false;
    }

    addMessage(text, sender) {
        const messagesContainer = document.getElementById('chatbotMessages');
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'bot' ? 'robot' : 'user'}"></i>
            </div>
            <div class="message-content">
                <p>${this.escapeHtml(text)}</p>
                <span class="message-time">${time}</span>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    new Chatbot();
});