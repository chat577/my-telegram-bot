import os
import logging
import random
import aiohttp
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

class EnglishAPI:
    def __init__(self):
        self.session = None
    
    async def get_verb_info(self, verb):
        """Получает информацию о глаголе из различных источников"""
        try:
            # Попробуем Free Dictionary API
            async with aiohttp.ClientSession() as session:
                url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{verb}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_dictionary_response(verb, data)
        except Exception as e:
            logger.error(f"Dictionary API error: {e}")
        
        # Если API не сработал, используем локальную базу
        return self._get_local_verb_info(verb)
    
    def _parse_dictionary_response(self, verb, data):
        """Парсит ответ от Dictionary API"""
        if not data:
            return None
        
        word_data = data[0]
        result = {
            'word': verb,
            'phonetic': '',
            'meanings': [],
            'source': 'Dictionary API'
        }
        
        # Получаем транскрипцию
        if 'phonetic' in word_data:
            result['phonetic'] = word_data['phonetic']
        elif 'phonetics' in word_data and word_data['phonetics']:
            for phonetics in word_data['phonetics']:
                if 'text' in phonetics:
                    result['phonetic'] = phonetics['text']
                    break
        
        # Получаем значения и переводы
        for meaning in word_data.get('meanings', []):
            part_of_speech = meaning.get('partOfSpeech', '')
            for definition in meaning.get('definitions', []):
                def_text = definition.get('definition', '')
                example = definition.get('example', '')
                
                # Простой перевод на русский (можно улучшить)
                translation = self._simple_translate(def_text)
                
                result['meanings'].append({
                    'partOfSpeech': part_of_speech,
                    'definition': def_text,
                    'translation': translation,
                    'example': example
                })
        
        return result
    
    def _simple_translate(self, text):
        """Простой перевод через локальную базу"""
        common_words = {
            'be': 'быть',
            'have': 'иметь',
            'do': 'делать',
            'say': 'говорить',
            'get': 'получать',
            'make': 'делать',
            'go': 'идти',
            'know': 'знать',
            'take': 'брать',
            'see': 'видеть',
            'come': 'приходить',
            'think': 'думать',
            'look': 'смотреть',
            'want': 'хотеть',
            'give': 'давать',
            'use': 'использовать',
            'find': 'находить',
            'tell': 'рассказывать',
            'ask': 'спрашивать',
            'work': 'работать',
            'seem': 'казаться',
            'feel': 'чувствовать',
            'try': 'пытаться',
            'leave': 'покидать',
            'call': 'звонить'
        }
        
        # Ищем совпадения в тексте
        for word, translation in common_words.items():
            if word in text.lower():
                return translation
        return "перевод"
    
    def _get_local_verb_info(self, verb):
        """Локальная база глаголов с транскрипцией"""
        verbs_db = {
            'be': {'phonetic': '/biː/', 'translation': 'быть', 'past': 'was/were', 'participle': 'been'},
            'have': {'phonetic': '/hæv/', 'translation': 'иметь', 'past': 'had', 'participle': 'had'},
            'do': {'phonetic': '/duː/', 'translation': 'делать', 'past': 'did', 'participle': 'done'},
            'say': {'phonetic': '/seɪ/', 'translation': 'говорить', 'past': 'said', 'participle': 'said'},
            'get': {'phonetic': '/ɡet/', 'translation': 'получать', 'past': 'got', 'participle': 'got/gotten'},
            'make': {'phonetic': '/meɪk/', 'translation': 'делать', 'past': 'made', 'participle': 'made'},
            'go': {'phonetic': '/ɡoʊ/', 'translation': 'идти', 'past': 'went', 'participle': 'gone'},
            'know': {'phonetic': '/noʊ/', 'translation': 'знать', 'past': 'knew', 'participle': 'known'},
            'take': {'phonetic': '/teɪk/', 'translation': 'брать', 'past': 'took', 'participle': 'taken'},
            'see': {'phonetic': '/siː/', 'translation': 'видеть', 'past': 'saw', 'participle': 'seen'},
            'come': {'phonetic': '/kʌm/', 'translation': 'приходить', 'past': 'came', 'participle': 'come'},
            'think': {'phonetic': '/θɪŋk/', 'translation': 'думать', 'past': 'thought', 'participle': 'thought'},
            'look': {'phonetic': '/lʊk/', 'translation': 'смотреть', 'past': 'looked', 'participle': 'looked'},
            'want': {'phonetic': '/wɒnt/', 'translation': 'хотеть', 'past': 'wanted', 'participle': 'wanted'},
            'give': {'phonetic': '/ɡɪv/', 'translation': 'давать', 'past': 'gave', 'participle': 'given'},
            'use': {'phonetic': '/juːz/', 'translation': 'использовать', 'past': 'used', 'participle': 'used'},
            'find': {'phonetic': '/faɪnd/', 'translation': 'находить', 'past': 'found', 'participle': 'found'},
            'tell': {'phonetic': '/tel/', 'translation': 'рассказывать', 'past': 'told', 'participle': 'told'},
            'ask': {'phonetic': '/æsk/', 'translation': 'спрашивать', 'past': 'asked', 'participle': 'asked'},
            'work': {'phonetic': '/wɜːrk/', 'translation': 'работать', 'past': 'worked', 'participle': 'worked'},
        }
        
        if verb in verbs_db:
            return {
                'word': verb,
                'phonetic': verbs_db[verb]['phonetic'],
                'meanings': [{
                    'partOfSpeech': 'verb',
                    'definition': f'to {verb}',
                    'translation': verbs_db[verb]['translation'],
                    'example': f'I {verb} every day'
                }],
                'past': verbs_db[verb]['past'],
                'participle': verbs_db[verb]['participle'],
                'source': 'Local Database'
            }
        
        return None

# Создаем экземпляр API
english_api = EnglishAPI()

# --- КЛАВИАТУРЫ ---
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔤 Найти слово/глагол", callback_data="search_word")],
        [InlineKeyboardButton("📚 Популярные глаголы", callback_data="popular_verbs")],
        [InlineKeyboardButton("💬 Разговорные фразы", callback_data="common_phrases")],
        [InlineKeyboardButton("🎯 Случайное слово", callback_data="random_word")],
        [InlineKeyboardButton("📖 Грамматика", callback_data="grammar")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_verbs_keyboard():
    keyboard = [
        [InlineKeyboardButton("be", callback_data="verb_be"), InlineKeyboardButton("have", callback_data="verb_have")],
        [InlineKeyboardButton("do", callback_data="verb_do"), InlineKeyboardButton("go", callback_data="verb_go")],
        [InlineKeyboardButton("see", callback_data="verb_see"), InlineKeyboardButton("say", callback_data="verb_say")],
        [InlineKeyboardButton("get", callback_data="verb_get"), InlineKeyboardButton("make", callback_data="verb_make")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_phrases_keyboard():
    keyboard = [
        [InlineKeyboardButton("👋 Приветствия", callback_data="phrases_greetings")],
        [InlineKeyboardButton("🤝 Знакомство", callback_data="phrases_introduction")],
        [InlineKeyboardButton("☕ В кафе", callback_data="phrases_cafe")],
        [InlineKeyboardButton("❓ Вопросы", callback_data="phrases_questions")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_grammar_keyboard():
    keyboard = [
        [InlineKeyboardButton("📝 Present Simple", callback_data="grammar_present_simple")],
        [InlineKeyboardButton("⏳ Present Continuous", callback_data="grammar_present_continuous")],
        [InlineKeyboardButton("🕰️ Past Simple", callback_data="grammar_past_simple")],
        [InlineKeyboardButton("🔮 Future Simple", callback_data="grammar_future_simple")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- ОБРАБОТЧИКИ КОМАНД ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🇬🇧 *English Learning Bot* 🇺🇸

*Умный помощник для изучения английского!*

✨ *Возможности:*
• 🔤 Поиск слов с транскрипцией и переводом
• 📚 Популярные глаголы с формами
• 💬 Полезные разговорные фразы
• 📖 Объяснения грамматики
• 🎯 Интерактивные упражнения

*Выберите действие:*
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *Как использовать бота:*

*Основные команды:*
/start - Главное меню
/help - Эта справка  
/word <слово> - Найти слово
/verb <глагол> - Информация о глаголе
/random - Случайное слово

*Интерактивное меню:*
• Используйте кнопки для навигации
• Нажимайте на слова для подробной информации
• Практикуйтесь ежедневно!

💡 *Советы для изучения:*
1. Учите по 5-10 слов в день
2. Составляйте предложения
3. Повторяйте пройденное
4. Практикуйте произношение

*Удачи в изучении английского!* 🚀
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

# --- ОБРАБОТЧИКИ CALLBACK ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "back_to_main":
        await show_main_menu(query)
    
    elif callback_data == "search_word":
        await search_word_handler(query)
    
    elif callback_data == "popular_verbs":
        await popular_verbs_handler(query)
    
    elif callback_data == "common_phrases":
        await common_phrases_handler(query)
    
    elif callback_data == "random_word":
        await random_word_handler(query)
    
    elif callback_data == "grammar":
        await grammar_handler(query)
    
    elif callback_data == "help":
        await help_handler(query)
    
    elif callback_data.startswith("verb_"):
        await verb_detail_handler(query, callback_data.replace("verb_", ""))
    
    elif callback_data.startswith("phrases_"):
        await phrases_handler(query, callback_data.replace("phrases_", ""))
    
    elif callback_data.startswith("grammar_"):
        await grammar_detail_handler(query, callback_data.replace("grammar_", ""))

async def show_main_menu(query):
    text = "🏠 *Главное меню*\n\nВыберите раздел:"
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

async def search_word_handler(query):
    text = """
🔍 *Поиск слова или глагола*

Введите слово на английском, и я найду:
• 📝 Транскрипцию (произношение)
• 🇷🇺 Перевод на русский
• 📚 Примеры использования

*Используйте команды:*
`/word hello` - найти слово
`/verb go` - найти глагол

*Или выберите популярные глаголы:*
    """
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_verbs_keyboard()
    )

async def popular_verbs_handler(query):
    text = """
📚 *Популярные английские глаголы*

Выберите глагол для подробной информации:

*Топ-10 самых используемых глаголов:*
"""
    verbs = ["be", "have", "do", "say", "get", "make", "go", "know", "take", "see"]
    for i, verb in enumerate(verbs, 1):
        text += f"{i}. *{verb}* - базовый глагол\n"
    
    text += "\n💡 *Совет:* Эти глаголы покрывают 50% всей английской речи!"
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_verbs_keyboard()
    )

async def common_phrases_handler(query):
    text = """
💬 *Разговорные фразы*

Выберите категорию полезных фраз для повседневного общения:
"""
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_phrases_keyboard()
    )

async def random_word_handler(query):
    words = [
        {"word": "hello", "translation": "привет", "example": "Hello! How are you?"},
        {"word": "beautiful", "translation": "красивый", "example": "What a beautiful day!"},
        {"word": "important", "translation": "важный", "example": "This is very important."},
        {"word": "understand", "translation": "понимать", "example": "I understand you."},
        {"word": "different", "translation": "разный", "example": "We are different."},
    ]
    
    word = random.choice(words)
    
    text = f"""
🎯 *Случайное слово для изучения!*

📖 *Слово:* {word['word']}
🇷🇺 *Перевод:* {word['translation']}
💡 *Пример:* {word['example']}

*Практика:* Составьте своё предложение с этим словом!

🔄 *Обновить слово:* /random
    """
    
    keyboard = [
        [InlineKeyboardButton("🔄 Новое слово", callback_data="random_word")],
        [InlineKeyboardButton("🔍 Найти слово", callback_data="search_word")],
        [InlineKeyboardButton("◀️ В меню", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def grammar_handler(query):
    text = """
📖 *Грамматика английского языка*

Выберите время для изучения:

*Доступные разделы:*
• 📝 Present Simple - регулярные действия
• ⏳ Present Continuous - действия сейчас  
• 🕰️ Past Simple - завершенные действия
• 🔮 Future Simple - будущие действия

💡 *Каждое время включает:*
- Правила образования
- Примеры предложений
- Слова-маркеры
- Упражнения
    """
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_grammar_keyboard()
    )

async def help_handler(query):
    text = """
ℹ️ *Помощь по использованию бота*

*Основные функции:*
🔤 *Поиск слов* - транскрипция, перевод, примеры
📚 *Глаголы* - формы, использование, примеры
💬 *Фразы* - разговорные выражения по темам
📖 *Грамматика* - правила и упражнения

*Команды:*
/start - главное меню
/help - помощь
/word <слово> - найти слово
/verb <глагол> - найти глагол  
/random - случайное слово

💡 *Для лучшего результата:*
• Занимайтесь регулярно
• Составляйте свои предложения
• Повторяйте пройденное
• Практикуйте произношение

*Удачи в изучении!* 🌟
    """
    
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")]]
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def verb_detail_handler(query, verb):
    # Показываем загрузку
    await query.edit_message_text(
        text=f"🔍 Ищу информацию о глаголе *{verb}*...",
        parse_mode='Markdown'
    )
    
    # Получаем информацию о глаголе
    verb_info = await english_api.get_verb_info(verb)
    
    if verb_info:
        text = f"""
🔤 *Глагол: {verb_info['word']}*

📝 *Транскрипция:* {verb_info.get('phonetic', '/транскрипция/')}
🇷🇺 *Перевод:* {verb_info['meanings'][0]['translation'] if verb_info['meanings'] else 'перевод'}

"""
        
        # Добавляем формы для глаголов
        if 'past' in verb_info and 'participle' in verb_info:
            text += f"📊 *Формы:*\n"
            text += f"• Past Simple: {verb_info['past']}\n"
            text += f"• Past Participle: {verb_info['participle']}\n\n"
        
        # Добавляем примеры
        text += f"💡 *Примеры:*\n"
        text += f"• I {verb} every day\n"
        text += f"• She {verb}s to school\n"
        text += f"• They {verb_info.get('past', verb+'ed')} yesterday\n\n"
        
        text += f"📚 *Источник:* {verb_info.get('source', 'База данных')}\n\n"
        text += "🎯 *Практика:* Составьте 3 предложения с этим глаголом!"
    
    else:
        text = f"""
🔤 *Глагол: {verb}*

⚠️ *Информация временно недоступна*

*Базовые формы:*
• Infinitive: {verb}
• Past Simple: {verb}ed
• Past Participle: {verb}ed

💡 *Пример использования:*
I {verb} to learn English - Я {verb} учить английский

*Попробуйте другой глагол или используйте команду:* `/verb {verb}`
        """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Другой глагол", callback_data="popular_verbs")],
        [InlineKeyboardButton("🎯 Случайное слово", callback_data="random_word")],
        [InlineKeyboardButton("◀️ В меню", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def phrases_handler(query, category):
    phrases_db = {
        "greetings": [
            {"english": "Hello! / Hi!", "russian": "Привет!", "context": "Неформальное приветствие"},
            {"english": "Good morning!", "russian": "Доброе утро!", "context": "До 12:00"},
            {"english": "Good afternoon!", "russian": "Добрый день!", "context": "12:00-18:00"},
            {"english": "Good evening!", "russian": "Добрый вечер!", "context": "После 18:00"},
            {"english": "How are you?", "russian": "Как дела?", "context": "Стандартный вопрос"},
            {"english": "I'm fine, thanks!", "russian": "Хорошо, спасибо!", "context": "Позитивный ответ"},
        ],
        "introduction": [
            {"english": "What's your name?", "russian": "Как тебя зовут?", "context": "Спросить имя"},
            {"english": "My name is...", "russian": "Меня зовут...", "context": "Представиться"},
            {"english": "Where are you from?", "russian": "Откуда ты?", "context": "Спросить откуда"},
            {"english": "I'm from Russia", "russian": "Я из России", "context": "Ответить откуда"},
            {"english": "Nice to meet you!", "russian": "Приятно познакомиться!", "context": "После знакомства"},
        ],
        "cafe": [
            {"english": "Can I have a coffee?", "russian": "Можно мне кофе?", "context": "Заказ напитка"},
            {"english": "I would like tea", "russian": "Я бы хотел(а) чай", "context": "Вежливый заказ"},
            {"english": "How much is it?", "russian": "Сколько это стоит?", "context": "Узнать цену"},
            {"english": "The bill, please", "russian": "Счет, пожалуйста", "context": "Попросить счет"},
        ],
        "questions": [
            {"english": "What is this?", "russian": "Что это?", "context": "Спросить о предмете"},
            {"english": "Where is...?", "russian": "Где...?", "context": "Спросить о месте"},
            {"english": "When...?", "russian": "Когда...?", "context": "Спросить о времени"},
            {"english": "Why...?", "russian": "Почему...?", "context": "Спросить причину"},
            {"english": "How...?", "russian": "Как...?", "context": "Спросить способ"},
        ]
    }
    
    category_names = {
        "greetings": "👋 Приветствия",
        "introduction": "🤝 Знакомство", 
        "cafe": "☕ В кафе",
        "questions": "❓ Вопросы"
    }
    
    phrases = phrases_db.get(category, [])
    category_name = category_names.get(category, category)
    
    text = f"💬 *{category_name}*\n\n"
    
    for phrase in phrases:
        text += f"• *{phrase['english']}*\n"
        text += f"  🇷🇺 {phrase['russian']}\n"
        text += f"  _💡 {phrase['context']}_\n\n"
    
    text += "💡 *Совет:* Произносите фразы вслух для лучшего запоминания!"
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_phrases_keyboard()
    )

async def grammar_detail_handler(query, tense):
    grammar_db = {
        "present_simple": {
            "name": "Present Simple",
            "usage": "Регулярные действия, привычки, факты, расписания",
            "structure": "Subject + V1/V1+s (he/she/it)",
            "examples": [
                "I work every day - Я работаю каждый день",
                "He works in an office - Он работает в офисе",
                "We like music - Нам нравится музыка",
                "The sun rises in the east - Солнце встает на востоке"
            ],
            "signal_words": ["always", "usually", "often", "every day", "sometimes", "never"]
        },
        "present_continuous": {
            "name": "Present Continuous", 
            "usage": "Действия в момент речи, временные ситуации, планы на ближайшее будущее",
            "structure": "Subject + am/is/are + V-ing",
            "examples": [
                "I am reading now - Я сейчас читаю",
                "She is watching TV - Она смотрит телевизор", 
                "They are playing football - Они играют в футбол",
                "We are meeting tomorrow - Мы встречаемся завтра"
            ],
            "signal_words": ["now", "at the moment", "currently", "today", "right now"]
        },
        "past_simple": {
            "name": "Past Simple",
            "usage": "Завершенные действия в прошлом, последовательные события", 
            "structure": "Subject + V2 (правильные: V+ed)",
            "examples": [
                "I worked yesterday - Я работал вчера",
                "She went to school - Она ходила в школу",
                "We saw a movie - Мы смотрели фильм", 
                "He lived in London - Он жил в Лондоне"
            ],
            "signal_words": ["yesterday", "last week", "ago", "in 2020", "then"]
        },
        "future_simple": {
            "name": "Future Simple",
            "usage": "Спонтанные решения, предсказания, обещания, будущие факты",
            "structure": "Subject + will + V1", 
            "examples": [
                "I will help you - Я помогу тебе",
                "It will rain tomorrow - Завтра будет дождь",
                "We will travel next year - Мы будем путешествовать в следующем году",
                "She will be 25 next month - Ей будет 25 в следующем месяце"
            ],
            "signal_words": ["tomorrow", "next week", "soon", "in the future", "later"]
        }
    }
    
    tense_info = grammar_db.get(tence, {})
    
    if tense_info:
        text = f"""
📖 *{tense_info['name']}*

🎯 *Использование:* {tense_info['usage']}

🏗️ *Формула:* `{tense_info['structure']}`

📝 *Примеры:*
"""
        for example in tense_info['examples']:
            text += f"• {example}\n"
        
        text += f"\n🔍 *Слова-маркеры:* {', '.join(tense_info['signal_words'])}"
        
        text += f"""

💡 *Упражнение:* Составьте 2 предложения в {tense_info['name']}!
        """
    else:
        text = "Информация о данном времени временно недоступна."
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=get_grammar_keyboard()
    )

# --- КОМАНДЫ ДЛЯ ВВОДА ТЕКСТА ---
async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Введите слово после команды: `/word hello`",
            parse_mode='Markdown'
        )
        return
    
    word = context.args[0].lower()
    await search_and_send_word_info(update, word, "word")

async def verb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Введите глагол после команды: `/verb go`",
            parse_mode='Markdown'
        )
        return
    
    verb = context.args[0].lower()
    await search_and_send_word_info(update, verb, "verb")

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await random_word_handler(update)

async def search_and_send_word_info(update, word, word_type):
    # Показываем что ищем
    if update.message:
        message = await update.message.reply_text(f"🔍 Ищу информацию о {'глаголе' if word_type == 'verb' else 'слове'} *{word}*...", parse_mode='Markdown')
    else:
        message = await update.callback_query.message.reply_text(f"🔍 Ищу информацию о {'глаголе' if word_type == 'verb' else 'слове'} *{word}*...", parse_mode='Markdown')
    
    # Получаем информацию
    word_info = await english_api.get_verb_info(word)
    
    if word_info:
        text = f"""
🔍 *Результат поиска:*

📖 *{'Глагол' if word_type == 'verb' else 'Слово'}:* {word_info['word']}
📝 *Транскрипция:* {word_info.get('phonetic', '/транскрипция/')}
🇷🇺 *Перевод:* {word_info['meanings'][0]['translation'] if word_info['meanings'] else 'перевод'}
"""
        
        if word_type == 'verb' and 'past' in word_info:
            text += f"📊 *Формы глагола:*\n"
            text += f"• Past Simple: {word_info['past']}\n"
            text += f"• Past Participle: {word_info['participle']}\n\n"
        
        text += f"💡 *Пример:* I {word} every day.\n\n"
        text += f"📚 *Источник:* {word_info.get('source', 'База данных')}"
    
    else:
        text = f"""
🔍 *{'Глагол' if word_type == 'verb' else 'Слово'}:* {word}

⚠️ *Подробная информация не найдена*

*Базовая информация:*
• Используйте в предложениях
• Практикуйте произношение
• Составляйте свои примеры

💡 *Пример:* I like to {word} - Мне нравится {word}
        """
    
    # Обновляем сообщение или отправляем новое
    if update.message:
        await message.edit_text(text, parse_mode='Markdown', reply_markup=get_main_menu_keyboard())
    else:
        await message.edit_text(text, parse_mode='Markdown', reply_markup=get_main_menu_keyboard())

# --- ОСНОВНАЯ ФУНКЦИЯ ---
def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден! Установите в переменных окружения Railway.")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("word", word_command))
    application.add_handler(CommandHandler("verb", verb_command))
    application.add_handler(CommandHandler("random", random_command))
    
    # Обработчики callback
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Запуск
    if os.getenv('RAILWAY_ENVIRONMENT'):
        # На Railway используем вебхук
        PORT = int(os.getenv('PORT', 8443))
        WEBHOOK_URL = os.getenv('RAILWAY_STATIC_URL')
        
        if WEBHOOK_URL:
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=BOT_TOKEN,
                webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
            )
        else:
            # Если нет вебхука, используем поллинг
            logger.info("Запуск в режиме поллинга на Railway...")
            application.run_polling()
    else:
        # Локально используем поллинг
        logger.info("Запуск в режиме поллинга локально...")
        application.run_polling()

if __name__ == '__main__':
    main()
