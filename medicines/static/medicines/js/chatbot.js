class Chatbot {
    constructor() {
        this.isOpen = false;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.toggleBtn = document.getElementById('chatbotToggle');
        this.modal = document.getElementById('chatbotModal');
        this.closeBtn = document.getElementById('chatbotClose');
        this.messagesContainer = document.getElementById('chatbotMessages');
        this.input = document.getElementById('chatbotInput');
        this.sendBtn = document.getElementById('chatbotSend');
        this.quickQuestions = document.querySelectorAll('.quick-question');
    }

    attachEventListeners() {
        this.toggleBtn.addEventListener('click', () => this.toggleModal());
        this.closeBtn.addEventListener('click', () => this.closeModal());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        this.quickQuestions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.target.getAttribute('data-question');
                this.input.value = question;
                this.sendMessage();
            });
        });

        // Close modal when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.modal.contains(e.target) && !this.toggleBtn.contains(e.target)) {
                this.closeModal();
            }
        });
    }

    toggleModal() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.modal.classList.add('active');
            this.input.focus();
        } else {
            this.modal.classList.remove('active');
        }
    }

    openModal() {
        this.isOpen = true;
        this.modal.classList.add('active');
        this.input.focus();
    }

    closeModal() {
        this.isOpen = false;
        this.modal.classList.remove('active');
    }

    sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        this.input.value = '';

        // Simulate bot response (you'll replace this with actual API call)
        setTimeout(() => {
            this.addMessage("I understand you're asking: '" + message + "'. This feature is coming soon!", 'bot');
        }, 1000);
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'bot' ? 'robot' : 'user'}"></i>
            </div>
            <div class="message-content">
                <p>${text}</p>
                <span class="message-time">${time}</span>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    new Chatbot();
}); s