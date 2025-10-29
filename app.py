from flask import Flask, render_template, request, jsonify
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

# Конфигурация DeepSeek API
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'your-deepseek-api-key-here')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class DeepSeekChatBot:
    def __init__(self):
        self.conversation_history = []
    
    def get_quick_replies(self):
        return [
            "Привет! 👋",
            "Расскажи о себе",
            "Что ты умеешь?",
            "Помоги с кодом",
            "Спасибо!"
        ]
    
    async def get_deepseek_response(self, user_message):
        """Получение ответа от DeepSeek API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }
            
            # Формируем промпт с историей
            messages = [
                {
                    "role": "system", 
                    "content": "Ты полезный AI-ассистент. Отвечай кратко и по делу. Будь дружелюбным."
                }
            ]
            
            # Добавляем историю (последние 6 сообщений)
            for msg in self.conversation_history[-6:]:
                messages.append({
                    "role": "user" if msg["type"] == "user" else "assistant",
                    "content": msg["content"]
                })
            
            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": user_message})
            
            payload = {
                "model": "deepseek-chat",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result['choices'][0]['message']['content']
                
                # Сохраняем в историю
                self.conversation_history.append({
                    "type": "user", 
                    "content": user_message,
                    "timestamp": datetime.now().isoformat()
                })
                self.conversation_history.append({
                    "type": "assistant", 
                    "content": bot_response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Ограничиваем историю
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return bot_response
            else:
                return f"Ошибка API: {response.status_code}"
                
        except Exception as e:
            return f"Произошла ошибка: {str(e)}"

# Создаем экземпляр бота
chatbot = DeepSeekChatBot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
async def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Пустое сообщение'}), 400
        
        # Получаем ответ от DeepSeek
        bot_response = await chatbot.get_deepseek_response(user_message)
        quick_replies = chatbot.get_quick_replies()
        
        return jsonify({
            'response': bot_response,
            'quick_replies': quick_replies,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Очистка истории диалога"""
    chatbot.conversation_history.clear()
    return jsonify({'success': True})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
