import numpy as np
import json
import random
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import re
from datetime import datetime

# Загрузка данных NLTK (для реального проекта нужно добавить загрузку)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class ChatBot:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_history = []
        self.vectorizer = TfidfVectorizer()
        self._train_vectorizer()
        
    def _load_knowledge_base(self):
        """База знаний бота"""
        return {
            "приветствия": [
                "Привет! Как я могу помочь вам сегодня?",
                "Здравствуйте! Рад вас видеть!",
                "Приветствую! Чем могу быть полезен?"
            ],
            "прощания": [
                "До свидания! Было приятно пообщаться!",
                "Пока! Возвращайтесь с новыми вопросами!",
                "Всего хорошего! Если что - я всегда здесь!"
            ],
            "возможности": [
                "Я могу: отвечать на вопросы, помогать с информацией, поддерживать беседу",
                "Мои возможности: обработка текста, ответы на вопросы, анализ запросов",
                "Я умею: общаться на разные темы, помогать с решениями, предоставлять информацию"
            ],
            "помощь": [
                "Просто напишите ваш вопрос, и я постараюсь помочь!",
                "Задайте любой вопрос - я сделаю всё возможное, чтобы ответить",
                "Я здесь чтобы помочь. Что вас интересует?"
            ],
            "ошибки": [
                "Извините, я не совсем понял вопрос. Можете переформулировать?",
                "Попробуйте задать вопрос по-другому",
                "Я еще учусь. Можете объяснить иначе?"
            ]
        }
    
    def _train_vectorizer(self):
        """Обучение векторизатора на базе знаний"""
        all_texts = []
        for category, responses in self.knowledge_base.items():
            all_texts.extend(responses)
            all_texts.append(category)
        
        if all_texts:
            self.vectorizer.fit(all_texts)
    
    def preprocess_text(self, text):
        """Предобработка текста"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def find_best_response(self, user_input):
        """Поиск лучшего ответа"""
        processed_input = self.preprocess_text(user_input)
        
        # Векторизация входного текста
        input_vec = self.vectorizer.transform([processed_input])
        
        best_similarity = 0
        best_category = None
        best_response = None
        
        # Поиск наиболее релевантной категории
        for category, responses in self.knowledge_base.items():
            category_vec = self.vectorizer.transform([category])
            similarity = cosine_similarity(input_vec, category_vec)[0][0]
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_category = category
        
        # Если найдена подходящая категория, выбираем случайный ответ
        if best_category and best_similarity > 0.3:
            best_response = random.choice(self.knowledge_base[best_category])
        else:
            best_response = random.choice(self.knowledge_base["ошибки"])
        
        return best_response
    
    def generate_response(self, user_input):
        """Генерация ответа с учетом контекста"""
        response = self.find_best_response(user_input)
        
        # Сохранение в историю
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'bot': response,
            'type': 'text'
        })
        
        # Ограничение истории (последние 50 сообщений)
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
        return response
    
    def get_quick_replies(self):
        """Быстрые ответы/кнопки"""
        return [
            "Привет! 👋",
            "Что ты умеешь?",
            "Помощь",
            "Спасибо!"
        ]
    
    def get_conversation_history(self):
        """Получить историю диалога"""
        return self.conversation_history

# Создание глобального экземпляра бота
chatbot = ChatBot()
