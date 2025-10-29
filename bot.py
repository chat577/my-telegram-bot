import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Импортируем данные через относительный импорт
try:
    from data import verbs, words, phrases, grammar
    print("✅ Данные успешно загружены из data/")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    # Создаем пустые структуры как fallback
    verbs = {}
    words = {}
    phrases = {}
    grammar = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

class EnglishBot:
    def __init__(self):
        self.verbs = verbs
        self.words = words
        self.phrases = phrases
        self.grammar = grammar
        print(f"📊 Загружено: {len(verbs)} глаголов, {len(words)} слов, {len(phrases)} категорий фраз")

    def get_random_word(self):
        """Возвращает случайное слово или глагол"""
        all_items = {**self.verbs, **self.words}
        if not all_items:
            return None, {"phonetic": "/test/", "translation": "тест", "examples": ["Test example"]}
        word = random.choice(list(all_items.keys()))
        return word, all_items[word]

    def search_word(self, word):
        """Ищет слово в базах данных"""
        word = word.lower()
        if word in self.verbs:
            return self.verbs[word], 'verb'
        elif word in self.words:
            return self.words[word], 'word'
        return None, None

# Создаем экземпляр бота
bot_data = EnglishBot()

# ... остальной код бота (клавиатуры, обработчики) остается таким же ...
