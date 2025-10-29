from flask import Flask, render_template, request, jsonify, session
from chatbot import chatbot
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-123')

@app.before_request
def before_request():
    """Инициализация сессии для каждого пользователя"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['conversation_start'] = datetime.now().isoformat()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint для общения с ботом"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Пустое сообщение'}), 400
        
        # Получение ответа от бота
        bot_response = chatbot.generate_response(user_message)
        quick_replies = chatbot.get_quick_replies()
        
        return jsonify({
            'response': bot_response,
            'quick_replies': quick_replies,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Получить историю диалога"""
    try:
        history = chatbot.get_conversation_history()
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Очистить историю диалога"""
    try:
        chatbot.conversation_history.clear()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check для Railway"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
