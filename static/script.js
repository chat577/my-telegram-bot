class ChatBotUI {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.quickRepliesContainer = document.getElementById('quickReplies');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        this.initEventListeners();
        this.showWelcomeMessage();
    }
    
    initEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Автофокус на поле ввода
        this.chatInput.focus();
    }
    
    showWelcomeMessage() {
        const welcomeMessage = "Привет! Я ваш AI-помощник. Чем могу помочь?";
        this.addMessage(welcomeMessage, 'bot');
        this.updateQuickReplies([
            "Привет! 👋",
            "Что ты умеешь?",
            "Помощь",
            "Расскажи о себе"
        ]);
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        // Очищаем поле ввода
        this.chatInput.value = '';
        
        // Добавляем сообщение пользователя
        this.addMessage(message, 'user');
        
        // Показываем индикатор набора
        this.showTypingIndicator();
        
        try {
            const response = await this.sendToBot(message);
            this.hideTypingIndicator();
            this.addMessage(response.response, 'bot');
            this.updateQuickReplies(response.quick_replies);
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Извините, произошла ошибка. Попробуйте еще раз.', 'bot');
            console.error('Error:', error);
        }
    }
    
    async sendToBot(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        return await response.json();
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = text;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.getCurrentTime();
        
        bubbleDiv.appendChild(timeDiv);
        messageDiv.appendChild(bubbleDiv);
        this.messagesContainer.appendChild(messageDiv);
        
        // Прокрутка вниз
        this.scrollToBottom();
    }
    
    updateQuickReplies(replies) {
        this.quickRepliesContainer.innerHTML = '';
        
        replies.forEach(reply => {
            const button = document.createElement('button');
            button.className = 'quick-reply-btn';
            button.textContent = reply;
            button.addEventListener('click', () => {
                this.chatInput.value = reply;
                this.sendMessage();
            });
            this.quickRepliesContainer.appendChild(button);
        });
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
    
    getCurrentTime() {
        return new Date().toLocaleTimeString('ru-RU', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
}

// Инициализация чата когда DOM загружен
document.addEventListener('DOMContentLoaded', () => {
    new ChatBotUI();
});
